import json

from core.reporting import report_payload, write_html_report, write_json_report
from core.result import ScanResult


def test_report_payload_wraps_results():
    payload = report_payload([ScanResult(module="ip_lookup", target="8.8.8.8", data={"ok": True})])
    assert payload["schema"] == "phantomrecon.report.v1"
    assert payload["result_count"] == 1


def test_write_json_report(tmp_path):
    path = tmp_path / "report.json"
    write_json_report([ScanResult(module="demo", target="target")], path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["results"][0]["module"] == "demo"


def test_write_html_report_escapes_values(tmp_path):
    path = tmp_path / "report.html"
    write_html_report(
        [ScanResult(module="demo", target="<script>", data={"value": "<b>x</b>"})],
        path,
    )
    content = path.read_text(encoding="utf-8")
    assert "&lt;script&gt;" in content
    assert "&lt;b&gt;x&lt;/b&gt;" in content
    assert "<script>" not in content
