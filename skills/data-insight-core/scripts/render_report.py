#!/usr/bin/env python3
"""Render a markdown data insight report from JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_payload(path: str | None) -> dict:
    if path:
        return json.loads(Path(path).read_text())
    return json.load(sys.stdin)


def render_section(title: str, items: list[str]) -> list[str]:
    if not items:
        return []
    lines = [f"## {title}"]
    lines.extend(f"- {item}" for item in items)
    lines.append("")
    return lines


def render_report(payload: dict) -> str:
    title = payload.get("title", "Data Insight Report")
    lines = [f"# {title}"]

    meta_parts = []
    for label, key in (
        ("Period", "period"),
        ("Audience", "audience"),
        ("Confidence", "confidence"),
        ("Ticket", "ticket"),
    ):
        value = payload.get(key)
        if value:
            meta_parts.append(f"**{label}:** {value}")
    if meta_parts:
        lines.append(" | ".join(meta_parts))
    lines.append("")

    lines.extend(render_section("Key Highlights", payload.get("highlights", [])))

    metric_definition = payload.get("metric_definition", [])
    lines.extend(render_section("Metric Definition", metric_definition))

    evidence = payload.get("evidence", [])
    lines.extend(render_section("Evidence", evidence))

    findings = payload.get("findings", [])
    lines.extend(render_section("Findings", findings))

    assumptions = payload.get("assumptions", [])
    lines.extend(render_section("Assumptions", assumptions))

    next_checks = payload.get("next_checks", [])
    lines.extend(render_section("Next Checks", next_checks))

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Render a markdown insight report from a JSON payload."
    )
    parser.add_argument(
        "path",
        nargs="?",
        help="Path to the JSON payload. Reads stdin when omitted.",
    )
    args = parser.parse_args()

    payload = load_payload(args.path)
    sys.stdout.write(render_report(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
