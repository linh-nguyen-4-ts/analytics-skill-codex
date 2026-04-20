#!/usr/bin/env python3
"""PostgreSQL adapter for setup, schema discovery, previews, profiling, and queries."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
from decimal import Decimal
from pathlib import Path
from typing import Any

try:
    import psycopg
    from psycopg.rows import dict_row
except ImportError:
    print(
        "Missing dependency. Install with: pip3 install 'psycopg[binary]'",
        file=os.sys.stderr,
    )
    raise SystemExit(1)


SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"


def load_env() -> dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    data: dict[str, str] = {}
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, _, value = line.partition("=")
        data[key.strip()] = value.strip()
    return data


def get_config() -> dict[str, str]:
    env = load_env()
    return {
        "database_url": env.get("DATABASE_URL", ""),
        "host": env.get("PGHOST", ""),
        "port": env.get("PGPORT", ""),
        "database": env.get("PGDATABASE", ""),
        "user": env.get("PGUSER", ""),
        "password": env.get("PGPASSWORD", ""),
        "sslmode": env.get("PGSSLMODE", ""),
        "default_schema": env.get("PGSCHEMA", "public"),
    }


def quote_identifier(name: str) -> str:
    escaped = name.replace('"', '""')
    return f'"{escaped}"'


def get_connection() -> tuple["psycopg.Connection[Any]", dict[str, str]]:
    config = get_config()
    if config["database_url"]:
        conn = psycopg.connect(config["database_url"], row_factory=dict_row)
    else:
        if not config["database"]:
            raise SystemExit(
                "Missing PostgreSQL config. Set DATABASE_URL or PGDATABASE and related PG* values."
            )
        kwargs: dict[str, Any] = {
            "dbname": config["database"],
            "row_factory": dict_row,
        }
        if config["host"]:
            kwargs["host"] = config["host"]
        if config["port"]:
            kwargs["port"] = int(config["port"])
        if config["user"]:
            kwargs["user"] = config["user"]
        if config["password"]:
            kwargs["password"] = config["password"]
        if config["sslmode"]:
            kwargs["sslmode"] = config["sslmode"]
        conn = psycopg.connect(**kwargs)

    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SET default_transaction_read_only = on")
        if config["default_schema"]:
            schema = quote_identifier(config["default_schema"])
            cur.execute(f"SET search_path TO {schema}, public")
    return conn, config


def normalize_table_name(name: str, default_schema: str) -> tuple[str, str]:
    parts = name.split(".")
    if len(parts) == 1:
        return default_schema or "public", parts[0]
    if len(parts) == 2:
        return parts[0], parts[1]
    raise SystemExit("Table name must be table or schema.table.")


def table_sql(schema: str, table: str) -> str:
    return f"{quote_identifier(schema)}.{quote_identifier(table)}"


def serialize_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat") and not isinstance(value, str):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def serialize_row(row: dict[str, Any]) -> dict[str, Any]:
    return {key: serialize_value(value) for key, value in row.items()}


def fetch_all(cur: "psycopg.Cursor[Any]") -> list[dict[str, Any]]:
    rows = cur.fetchall()
    return [serialize_row(dict(row)) for row in rows]


def ask(prompt: str, key: str, existing: dict[str, str], default: str = "") -> str:
    current = existing.get(key, default)
    suffix = f" [{current}]" if current else ""
    value = input(f"{prompt}{suffix}: ").strip()
    return value or current


def cmd_setup(_: argparse.Namespace) -> int:
    existing = load_env()
    database_url = ask("DATABASE_URL (optional)", "DATABASE_URL", existing)
    host = ask("PGHOST", "PGHOST", existing)
    port = ask("PGPORT", "PGPORT", existing, "5432")
    database = ask("PGDATABASE", "PGDATABASE", existing)
    user = ask("PGUSER", "PGUSER", existing)
    password = ask("PGPASSWORD", "PGPASSWORD", existing)
    sslmode = ask("PGSSLMODE", "PGSSLMODE", existing, "prefer")
    default_schema = ask("PGSCHEMA", "PGSCHEMA", existing, "public")

    ENV_PATH.write_text(
        "\n".join(
            [
                "# PostgreSQL adapter configuration",
                f"DATABASE_URL={database_url}",
                f"PGHOST={host}",
                f"PGPORT={port}",
                f"PGDATABASE={database}",
                f"PGUSER={user}",
                f"PGPASSWORD={password}",
                f"PGSSLMODE={sslmode}",
                f"PGSCHEMA={default_schema}",
                "",
            ]
        )
    )
    print(f"Saved {ENV_PATH}")
    return 0


def cmd_test(_: argparse.Namespace) -> int:
    conn, config = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT current_database() AS database_name, current_user AS user_name, current_schema() AS schema_name, NOW() AS connected_at"
            )
            row = serialize_row(dict(cur.fetchone()))
            print(json.dumps(row, ensure_ascii=False, indent=2))
    finally:
        conn.close()
    if config["database_url"]:
        print("Connected via DATABASE_URL")
    return 0


def cmd_schemas(_: argparse.Namespace) -> int:
    conn, _config = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('information_schema')
                  AND schema_name NOT LIKE 'pg_%'
                ORDER BY schema_name
                """
            )
            for row in fetch_all(cur):
                print(row["schema_name"])
    finally:
        conn.close()
    return 0


def cmd_tables(args: argparse.Namespace) -> int:
    conn, _config = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_type, table_name
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_type, table_name
                """,
                (args.schema,),
            )
            for row in fetch_all(cur):
                print(f"{row['table_type']}\t{row['table_name']}")
    finally:
        conn.close()
    return 0


def cmd_describe(args: argparse.Namespace) -> int:
    conn, config = get_connection()
    try:
        schema, table = normalize_table_name(args.table, config["default_schema"])
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                  column_name,
                  data_type,
                  is_nullable,
                  column_default,
                  character_maximum_length,
                  numeric_precision,
                  datetime_precision
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
                """,
                (schema, table),
            )
            for row in fetch_all(cur):
                print(json.dumps(row, ensure_ascii=False))
    finally:
        conn.close()
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    conn, config = get_connection()
    try:
        schema, table = normalize_table_name(args.table, config["default_schema"])
        with conn.cursor() as cur:
            cur.execute(
                f"SELECT * FROM {table_sql(schema, table)} LIMIT {args.limit}"
            )
            for row in fetch_all(cur):
                print(json.dumps(row, ensure_ascii=False))
    finally:
        conn.close()
    return 0


def cmd_profile(args: argparse.Namespace) -> int:
    conn, config = get_connection()
    try:
        schema, table = normalize_table_name(args.table, config["default_schema"])
        qualified = table_sql(schema, table)
        with conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) AS row_count FROM {qualified}")
            row_count = cur.fetchone()["row_count"]

            cur.execute(
                """
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position
                """,
                (schema, table),
            )
            columns = fetch_all(cur)

            payload: dict[str, Any] = {
                "schema": schema,
                "table": table,
                "row_count": row_count,
                "columns": [],
            }

            for column in columns:
                name = column["column_name"]
                identifier = quote_identifier(name)
                cur.execute(
                    f"SELECT COUNT(*) AS null_count FROM {qualified} WHERE {identifier} IS NULL"
                )
                null_count = cur.fetchone()["null_count"]
                cur.execute(
                    f"SELECT COUNT(DISTINCT {identifier}) AS distinct_count FROM {qualified}"
                )
                distinct_count = cur.fetchone()["distinct_count"]
                cur.execute(
                    (
                        f"SELECT DISTINCT {identifier} AS value "
                        f"FROM {qualified} WHERE {identifier} IS NOT NULL "
                        f"LIMIT {args.sample_values}"
                    )
                )
                sample_values = [row["value"] for row in fetch_all(cur)]
                payload["columns"].append(
                    {
                        "column_name": name,
                        "data_type": column["data_type"],
                        "null_count": null_count,
                        "null_rate": (null_count / row_count) if row_count else 0,
                        "distinct_count": distinct_count,
                        "sample_values": sample_values,
                    }
                )

            print(json.dumps(payload, ensure_ascii=False, indent=2))
    finally:
        conn.close()
    return 0


def load_sql(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text()
    if args.sql:
        return args.sql
    raise SystemExit("Provide SQL directly or with --file.")


def strip_trailing_semicolon(sql: str) -> str:
    return sql.strip().rstrip(";")


def cmd_query(args: argparse.Namespace) -> int:
    conn, _config = get_connection()
    try:
        sql = strip_trailing_semicolon(load_sql(args))
        wrapped_sql = f"SELECT * FROM ({sql}) AS subquery LIMIT {args.max_rows}"

        with conn.cursor() as cur:
            cur.execute(wrapped_sql)
            rows = fetch_all(cur)

        if args.csv:
            if not rows:
                return 0
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
            print(output.getvalue(), end="")
            return 0

        for row in rows:
            print(json.dumps(row, ensure_ascii=False))
    finally:
        conn.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup").set_defaults(func=cmd_setup)
    subparsers.add_parser("test").set_defaults(func=cmd_test)
    subparsers.add_parser("schemas").set_defaults(func=cmd_schemas)

    tables = subparsers.add_parser("tables")
    tables.add_argument("schema")
    tables.set_defaults(func=cmd_tables)

    describe = subparsers.add_parser("describe")
    describe.add_argument("table")
    describe.set_defaults(func=cmd_describe)

    preview = subparsers.add_parser("preview")
    preview.add_argument("table")
    preview.add_argument("--limit", type=int, default=5)
    preview.set_defaults(func=cmd_preview)

    profile = subparsers.add_parser("profile")
    profile.add_argument("table")
    profile.add_argument("--sample-values", type=int, default=5)
    profile.set_defaults(func=cmd_profile)

    query = subparsers.add_parser("query")
    query.add_argument("sql", nargs="?")
    query.add_argument("--file")
    query.add_argument("--csv", action="store_true")
    query.add_argument("--max-rows", type=int, default=500)
    query.set_defaults(func=cmd_query)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
