#!/usr/bin/env python3
"""BigQuery adapter for setup, schema discovery, previews, and query execution."""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    from google.cloud import bigquery
except ImportError:
    print(
        "Missing dependency. Install with: pip3 install google-cloud-bigquery",
        file=sys.stderr,
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
        "billing_project": env.get("GCP_BILLING_PROJECT", ""),
        "data_project": env.get("GCP_DATA_PROJECT", ""),
        "credentials_path": env.get("GOOGLE_APPLICATION_CREDENTIALS", ""),
    }


def get_client() -> tuple["bigquery.Client", dict[str, str]]:
    config = get_config()
    billing_project = config["billing_project"] or config["data_project"]
    if not billing_project:
        raise SystemExit(
            "Missing GCP_BILLING_PROJECT or GCP_DATA_PROJECT. Run setup first."
        )

    credentials = None
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"],
            stderr=subprocess.DEVNULL,
        ).decode().strip()
        if token:
            from google.oauth2.credentials import Credentials

            credentials = Credentials(token=token)
    except (subprocess.CalledProcessError, FileNotFoundError):
        credentials = None

    if not credentials and config["credentials_path"]:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["credentials_path"]

    kwargs: dict[str, object] = {"project": billing_project}
    if credentials is not None:
        kwargs["credentials"] = credentials
    return bigquery.Client(**kwargs), config


def normalize_table_name(name: str, data_project: str) -> str:
    parts = name.split(".")
    if len(parts) == 2:
        if not data_project:
            raise SystemExit(
                "Table must be project.dataset.table when GCP_DATA_PROJECT is unset."
            )
        return f"{data_project}.{parts[0]}.{parts[1]}"
    if len(parts) == 3:
        return name
    raise SystemExit("Table name must be dataset.table or project.dataset.table.")


def serialize_row(row: dict) -> dict:
    output = {}
    for key, value in row.items():
        if hasattr(value, "isoformat"):
            output[key] = value.isoformat()
        elif isinstance(value, bytes):
            output[key] = value.decode("utf-8", errors="replace")
        else:
            output[key] = value
    return output


def cmd_setup(_: argparse.Namespace) -> int:
    existing = load_env()

    def ask(prompt: str, key: str, default: str = "") -> str:
        current = existing.get(key, default)
        suffix = f" [{current}]" if current else ""
        entered = input(f"{prompt}{suffix}: ").strip()
        return entered or current

    billing = ask("Billing project", "GCP_BILLING_PROJECT")
    data = ask("Data project", "GCP_DATA_PROJECT")
    credentials = ask(
        "Credentials path (leave empty to use gcloud or ADC)",
        "GOOGLE_APPLICATION_CREDENTIALS",
    )

    ENV_PATH.write_text(
        "\n".join(
            [
                "# BigQuery adapter configuration",
                f"GCP_BILLING_PROJECT={billing}",
                f"GCP_DATA_PROJECT={data}",
                f"GOOGLE_APPLICATION_CREDENTIALS={credentials}",
                "",
            ]
        )
    )
    print(f"Saved {ENV_PATH}")
    return 0


def cmd_test(_: argparse.Namespace) -> int:
    client, config = get_client()
    print(f"Billing project: {config['billing_project'] or config['data_project']}")
    print(f"Data project: {config['data_project'] or '(same as billing)'}")
    try:
        rows = list(client.query("SELECT 1 AS ok").result())
    except Exception as exc:
        print(f"Connection failed: {exc}", file=sys.stderr)
        print(
            "Try gcloud auth application-default login and set the quota project.",
            file=sys.stderr,
        )
        return 1
    print(f"Query OK: {dict(rows[0])}")
    return 0


def cmd_datasets(_: argparse.Namespace) -> int:
    client, config = get_client()
    data_project = config["data_project"] or config["billing_project"]
    for dataset in client.list_datasets(project=data_project):
        print(dataset.dataset_id)
    return 0


def cmd_tables(args: argparse.Namespace) -> int:
    client, config = get_client()
    data_project = config["data_project"] or config["billing_project"]
    dataset_ref = f"{data_project}.{args.dataset}"
    for table in client.list_tables(dataset_ref):
        print(f"{table.table_type}\t{table.table_id}")
    return 0


def cmd_schema(args: argparse.Namespace) -> int:
    client, config = get_client()
    table_name = normalize_table_name(args.table, config["data_project"])
    table = client.get_table(table_name)
    for field in table.schema:
        print(f"{field.name}\t{field.field_type}\t{field.mode}")
    return 0


def cmd_preview(args: argparse.Namespace) -> int:
    client, config = get_client()
    table_name = normalize_table_name(args.table, config["data_project"])
    sql = f"SELECT * FROM `{table_name}` LIMIT {args.limit}"
    rows = client.query(sql).result()
    for row in rows:
        print(json.dumps(serialize_row(dict(row)), ensure_ascii=False))
    return 0


def load_sql(args: argparse.Namespace) -> str:
    if args.file:
        return Path(args.file).read_text()
    if args.sql:
        return args.sql
    raise SystemExit("Provide SQL directly or with --file.")


def cmd_query(args: argparse.Namespace) -> int:
    client, _config = get_client()
    sql = load_sql(args)
    try:
        result = client.query(sql).result()
    except Exception as exc:
        print(f"Query failed: {exc}", file=sys.stderr)
        return 1

    rows = []
    for index, row in enumerate(result):
        if index >= args.max_rows:
            break
        rows.append(serialize_row(dict(row)))

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
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("setup").set_defaults(func=cmd_setup)
    subparsers.add_parser("test").set_defaults(func=cmd_test)
    subparsers.add_parser("datasets").set_defaults(func=cmd_datasets)

    tables = subparsers.add_parser("tables")
    tables.add_argument("dataset")
    tables.set_defaults(func=cmd_tables)

    schema = subparsers.add_parser("schema")
    schema.add_argument("table")
    schema.set_defaults(func=cmd_schema)

    preview = subparsers.add_parser("preview")
    preview.add_argument("table")
    preview.add_argument("--limit", type=int, default=5)
    preview.set_defaults(func=cmd_preview)

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
