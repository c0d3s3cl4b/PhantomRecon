"""Unified report generation for PhantomRecon scan results."""

from __future__ import annotations

import html
import json
from collections.abc import Iterable
from pathlib import Path

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


def _escape(value: object) -> str:
    return html.escape(str(value))


def _render_scalar(value: object) -> str:
    if value is None:
        return '<span class="muted">—</span>'
    if isinstance(value, bool):
        label = "yes" if value else "no"
        return f'<span class="pill">{label}</span>'
    return _escape(value)


def _render_dict_table(data: dict[object, object]) -> str:
    rows = []
    for key, value in data.items():
        rows.append(
            "<tr>"
            f"<th>{_escape(key)}</th>"
            f"<td>{_render_value(value)}</td>"
            "</tr>"
        )
    return f'<div class="table-wrap"><table>{"".join(rows)}</table></div>'


def _render_list_table(items: list[object]) -> str:
    if not items:
        return '<span class="muted">No entries</span>'
    if all(isinstance(item, dict) for item in items):
        dict_items = [item for item in items if isinstance(item, dict)]
        columns: list[object] = []
        for item in dict_items:
            for key in item:
                if key not in columns:
                    columns.append(key)
        head = "".join(f"<th>{_escape(column)}</th>" for column in columns)
        body_rows = []
        for item in dict_items:
            cells = "".join(
                f"<td>{_render_scalar(item.get(column))}</td>" for column in columns
            )
            body_rows.append(f"<tr>{cells}</tr>")
        return (
            '<div class="table-wrap"><table class="list-table">'
            f"<thead><tr>{head}</tr></thead>"
            f"<tbody>{''.join(body_rows)}</tbody></table></div>"
        )
    return "<ul>" + "".join(f"<li>{_render_value(item)}</li>" for item in items) + "</ul>"


def _render_value(value: object) -> str:
    if isinstance(value, dict):
        return _render_dict_table(value)
    if isinstance(value, list):
        return _render_list_table(value)
    if isinstance(value, tuple):
        return _render_list_table(list(value))
    return _render_scalar(value)


def _status_badge(status: object) -> str:
    value = str(status or "unknown")
    css_class = "success" if value == "success" else "error"
    return f'<span class="status {css_class}">{_escape(value)}</span>'


def _render_result_card(item: dict[str, object]) -> str:
    module = _escape(item.get("module", "unknown"))
    target = _escape(item.get("target", "unknown"))
    timestamp = _escape(item.get("timestamp", ""))
    status = _status_badge(item.get("status"))
    data = item.get("data")
    errors = item.get("errors")

    data_html = _render_value(data if isinstance(data, dict) else {})
    errors_html = ""
    if isinstance(errors, list) and errors:
        errors_html = (
            '<div class="errors"><h3>Errors</h3>'
            f"{_render_list_table(errors)}"
            "</div>"
        )

    return (
        '<section class="result-card">'
        '<div class="result-head">'
        f"<div><h2>{module}</h2><div class=\"target\">{target}</div></div>"
        f"{status}"
        "</div>"
        '<div class="meta">'
        f"<span>Target: <strong>{target}</strong></span>"
        f"<span>Timestamp: <strong>{timestamp}</strong></span>"
        "</div>"
        '<div class="data-block"><h3>Data</h3>'
        f"{data_html}</div>{errors_html}</section>"
    )


def write_html_report(results: Iterable[ScanResult], output: Path) -> Path:
    payload = report_payload(results)
    raw_results = payload["results"]
    result_items = raw_results if isinstance(raw_results, list) else []
    cards = "".join(
        _render_result_card(item) for item in result_items if isinstance(item, dict)
    )
    result_count = int(payload["result_count"])
    success_count = sum(
        1
        for item in result_items
        if isinstance(item, dict) and item.get("status") == "success"
    )
    error_count = result_count - success_count

    document = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PhantomRecon Report</title>
<style>
:root {{ color-scheme: light dark; }}
* {{ box-sizing: border-box; }}
body {{
  font-family: Inter, ui-sans-serif, system-ui, sans-serif;
  margin: 0;
  background: #0b1020;
  color: #e5e7eb;
}}
main {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1rem 4rem; }}
.hero {{
  border: 1px solid #26324a;
  border-radius: 18px;
  padding: 1.5rem;
  background: #111827;
  margin-bottom: 1rem;
}}
.hero h1 {{ margin: 0 0 .35rem; font-size: 2rem; }}
.hero p {{ margin: 0; color: #9ca3af; }}
.summary {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: .75rem;
  margin: 1rem 0 1.5rem;
}}
.metric {{
  border: 1px solid #26324a;
  border-radius: 14px;
  background: #111827;
  padding: 1rem;
}}
.metric strong {{ display: block; font-size: 1.7rem; margin-top: .2rem; }}
.metric span {{ color: #9ca3af; font-size: .85rem; }}
.result-card {{
  border: 1px solid #26324a;
  border-radius: 18px;
  background: #111827;
  padding: 1.2rem;
  margin: 1rem 0;
}}
.result-head {{ display: flex; justify-content: space-between; gap: 1rem; }}
.result-head h2 {{ margin: 0; }}
.target {{ color: #93c5fd; margin-top: .25rem; }}
.status {{
  align-self: flex-start;
  border-radius: 999px;
  padding: .3rem .65rem;
  font-size: .8rem;
  font-weight: 700;
}}
.status.success {{ background: #064e3b; color: #a7f3d0; }}
.status.error {{ background: #7f1d1d; color: #fecaca; }}
.meta {{ display: flex; flex-wrap: wrap; gap: 1rem; color: #9ca3af; margin: 1rem 0; }}
.data-block h3, .errors h3 {{ margin-bottom: .6rem; }}
.table-wrap {{ overflow-x: auto; border: 1px solid #26324a; border-radius: 12px; }}
table {{ width: 100%; border-collapse: collapse; min-width: 520px; }}
th, td {{ text-align: left; vertical-align: top; padding: .65rem .75rem; }}
th {{ color: #cbd5e1; font-weight: 600; }}
tbody tr + tr, table > tbody > tr + tr {{ border-top: 1px solid #1f2937; }}
thead {{ background: #172033; }}
.list-table td {{ white-space: normal; word-break: break-word; }}
.pill {{
  display: inline-block;
  padding: .15rem .45rem;
  border-radius: 999px;
  background: #1f2937;
}}
.muted {{ color: #6b7280; }}
.errors {{ color: #fecaca; margin-top: 1rem; }}
ul {{ margin: .35rem 0; padding-left: 1.2rem; }}
@media (max-width: 640px) {{
  main {{ padding-top: 1rem; }}
  .result-head {{ flex-direction: column; }}
  .meta {{ flex-direction: column; gap: .35rem; }}
}}
</style>
</head>
<body>
<main>
  <header class="hero">
    <h1>PhantomRecon Report</h1>
    <p>Structured reconnaissance results</p>
  </header>
  <div class="summary">
    <div class="metric"><span>Total results</span><strong>{result_count}</strong></div>
    <div class="metric"><span>Successful</span><strong>{success_count}</strong></div>
    <div class="metric"><span>Errors</span><strong>{error_count}</strong></div>
  </div>
  {cards}
</main>
</body>
</html>
"""
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(document, encoding="utf-8")
    return output
