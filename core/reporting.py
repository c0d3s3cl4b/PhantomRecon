"""Unified report generation for PhantomRecon scan results."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Iterable

from core.result import ScanResult


def report_payload(results: Iterable[ScanResult]) -> dict[str, object]:
    items = [result.to_dict() for result in results]
    return {
        "schema": "phantomrecon.report.v1",
        "result_count": len(items),
        "results": items,
    }


def write_json_report(results: Iterable[ScanResult], output: Path) -> Path:
    payload = report_payload(results)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return output


def _render_value(value: object) -> str:
    if isinstance(value, (dict, list, tuple)):
        return html.escape(json.dumps(value, indent=2, ensure_ascii=False))
    return html.escape(str(value))


def write_html_report(results: Iterable[ScanResult], output: Path) -> Path:
    payload = report_payload(results)
    cards = []
    for item in payload["results"]:
        rows = "".join(
            f"<tr><th>{html.escape(str(key))}</th><td><pre>{_render_value(value)}</pre></td></tr>"
            for key, value in item.items()
        )
        cards.append(f"<section><h2>{html.escape(str(item['module']))}</h2><table>{rows}</table></section>")

    document = f"""<!doctype html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\">
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
<title>PhantomRecon Report</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 1100px; margin: 2rem auto; padding: 0 1rem; }}
section {{ border: 1px solid #ddd; border-radius: 10px; padding: 1rem; margin: 1rem 0; }}
table {{ width: 100%; border-collapse: collapse; }}
th, td {{ text-align: left; vertical-align: top; border-bottom: 1px solid #eee; padding: .55rem; }}
th {{ width: 190px; }}
pre {{ white-space: pre-wrap; word-break: break-word; margin: 0; }}
</style>
</head>
<body>
<h1>PhantomRecon Report</h1>
<p>Results: {payload['result_count']}</p>
{''.join(cards)}
</body>
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output
