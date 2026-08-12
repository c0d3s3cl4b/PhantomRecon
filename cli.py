"""Command-line entry point for PhantomRecon."""

from __future__ import annotations

import argparse
import importlib
import json
import platform
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from core.result import ScanResult

VERSION = "2.2.0a1"
console = Console()

MODULES = {
    "email": "modules.email_osint",
    "exif": "modules.exif_extractor",
    "ip": "modules.ip_lookup",
    "phone": "modules.phone_lookup",
    "ports": "modules.port_scanner",
    "subdomain": "modules.subdomain_finder",
    "username": "modules.username_search",
    "whois": "modules.whois_lookup",
}

DEPENDENCIES = {
    "PIL": "Image metadata",
    "dns": "DNS resolution",
    "phonenumbers": "Phone OSINT",
    "requests": "HTTP client",
    "rich": "Rich terminal UI",
    "whois": "WHOIS lookup",
}


def _add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output", type=Path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phantomrecon",
        description="PhantomRecon 2.2 - OSINT and authorized reconnaissance framework",
    )
    parser.add_argument("--version", action="version", version=f"PhantomRecon {VERSION}")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("menu", help="Open the classic interactive menu")
    subparsers.add_parser("doctor", help="Check runtime, config, and dependencies")
    subparsers.add_parser("providers", help="List registered external data providers")
    config_parser = subparsers.add_parser("config", help="Show effective runtime configuration")
    config_parser.add_argument("--json", action="store_true", dest="as_json")

    plugins_parser = subparsers.add_parser("plugins", help="Discover installed plugins")
    plugins_parser.add_argument("--load", action="store_true", help="Attempt to import plugins")
    plugins_parser.add_argument("--json", action="store_true", dest="as_json")

    report_parser = subparsers.add_parser("report", help="Convert saved results into a report")
    report_parser.add_argument("input", type=Path, help="ScanResult JSON or PhantomRecon report JSON")
    report_parser.add_argument("--format", choices=("json", "html"), default="html")
    report_parser.add_argument("--output", type=Path)

    module_parser = subparsers.add_parser("module")
    module_parser.add_argument("name", choices=sorted(MODULES))

    ip_parser = subparsers.add_parser("ip")
    ip_parser.add_argument("target")
    ip_parser.add_argument("--timeout", type=float, default=10.0)
    _add_output_options(ip_parser)

    whois_parser = subparsers.add_parser("whois")
    whois_parser.add_argument("target")
    _add_output_options(whois_parser)

    phone_parser = subparsers.add_parser("phone")
    phone_parser.add_argument("target")
    _add_output_options(phone_parser)

    email_parser = subparsers.add_parser("email")
    email_parser.add_argument("target")
    email_parser.add_argument("--timeout", type=float, default=10.0)
    email_parser.add_argument("--no-reputation", action="store_true")
    _add_output_options(email_parser)

    username_parser = subparsers.add_parser("username")
    username_parser.add_argument("target")
    username_parser.add_argument("--timeout", type=float, default=8.0)
    username_parser.add_argument("--workers", type=int, default=10)
    _add_output_options(username_parser)

    subdomain_parser = subparsers.add_parser("subdomain")
    subdomain_parser.add_argument("target")
    subdomain_parser.add_argument("--active-dns", action="store_true")
    subdomain_parser.add_argument("--timeout", type=float, default=15.0)
    subdomain_parser.add_argument("--workers", type=int, default=10)
    _add_output_options(subdomain_parser)

    ports_parser = subparsers.add_parser("ports")
    ports_parser.add_argument("target")
    ports_parser.add_argument("--ports", dest="port_spec")
    ports_parser.add_argument("--timeout", type=float, default=0.75)
    ports_parser.add_argument("--workers", type=int, default=32)
    _add_output_options(ports_parser)

    exif_parser = subparsers.add_parser("exif")
    exif_parser.add_argument("target")
    _add_output_options(exif_parser)
    return parser


def run_doctor() -> int:
    from core.config import settings

    table = Table(title="PhantomRecon Doctor")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")
    healthy = sys.version_info >= (3, 10)
    table.add_row(
        "Python",
        "OK" if healthy else "FAIL",
        f"{platform.python_version()} (requires >= 3.10)",
    )
    for module_name, purpose in DEPENDENCIES.items():
        try:
            importlib.import_module(module_name)
            status = "OK"
        except ImportError:
            status = "MISSING"
            healthy = False
        table.add_row(module_name, status, purpose)
    table.add_row("HTTP timeout", "OK", f"{settings.http_timeout}s")
    table.add_row("HTTP retries", "OK", str(settings.http_retries))
    table.add_row("Max workers", "OK", str(settings.max_workers))
    table.add_row("Report directory", "OK", str(settings.report_directory))
    console.print(table)
    return 0 if healthy else 1


def run_providers() -> int:
    import core.builtin_providers  # noqa: F401
    from core.providers import registry

    table = Table(title="PhantomRecon Providers")
    table.add_column("Name")
    table.add_column("Capability")
    for provider in registry.list():
        table.add_row(provider.name, provider.capability)
    console.print(table)
    return 0


def run_config(*, as_json: bool) -> int:
    from core.config import settings

    data = settings.to_dict()
    if as_json:
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return 0
    table = Table(title="PhantomRecon Configuration")
    table.add_column("Setting")
    table.add_column("Value")
    for key, value in data.items():
        table.add_row(key, str(value))
    console.print(table)
    return 0


def run_plugins(*, load: bool, as_json: bool) -> int:
    from core.plugins import discover_plugins

    plugins = discover_plugins(load=load)
    if as_json:
        print(json.dumps([plugin.to_dict() for plugin in plugins], indent=2, ensure_ascii=False))
        return 0
    table = Table(title="PhantomRecon Plugins")
    table.add_column("Name")
    table.add_column("Distribution")
    table.add_column("Version")
    table.add_column("Status")
    for plugin in plugins:
        status = "error" if plugin.error else ("loaded" if plugin.loaded else "discovered")
        table.add_row(
            plugin.name,
            plugin.distribution or "-",
            plugin.version or "-",
            status,
        )
    if not plugins:
        table.add_row("No third-party plugins installed", "-", "-", "-")
    console.print(table)
    return 1 if any(plugin.error for plugin in plugins) else 0


def _result_from_dict(item: dict[str, object]) -> ScanResult:
    return ScanResult(
        module=str(item.get("module", "unknown")),
        target=str(item.get("target", "unknown")),
        data=dict(item.get("data", {})) if isinstance(item.get("data"), dict) else {},
        status=str(item.get("status", "success")),
        errors=[str(value) for value in item.get("errors", [])]
        if isinstance(item.get("errors"), list)
        else [],
        timestamp=str(item.get("timestamp", "")),
    )


def _load_report_results(path: Path) -> list[ScanResult]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Input JSON must be an object")
    raw_results = payload.get("results")
    if isinstance(raw_results, list):
        return [_result_from_dict(item) for item in raw_results if isinstance(item, dict)]
    if "module" in payload:
        return [_result_from_dict(payload)]
    raise ValueError("Input is not a PhantomRecon ScanResult/report")


def run_report(input_path: Path, *, output_format: str, output: Path | None) -> int:
    from core.config import settings
    from core.reporting import write_html_report, write_json_report

    try:
        results = _load_report_results(input_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        console.print(f"[red]Report error:[/red] {exc}")
        return 2
    suffix = ".html" if output_format == "html" else ".json"
    destination = output or settings.report_directory / f"phantomrecon-report{suffix}"
    if output_format == "html":
        write_html_report(results, destination)
    else:
        write_json_report(results, destination)
    console.print(f"[green]Report saved:[/green] {destination}")
    return 0


def _render_result(result: ScanResult, *, as_json: bool, output: Path | None) -> int:
    text = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
        if not as_json:
            console.print(f"[green]Saved:[/green] {output}")
    if as_json or output is None:
        print(text)
    return 0 if result.status == "success" else 1


def _run_direct_command(args: argparse.Namespace) -> ScanResult | None:
    if args.command == "ip":
        from modules.ip_lookup import lookup_ip

        return lookup_ip(args.target, timeout=args.timeout)
    if args.command == "whois":
        from modules.whois_lookup import lookup_whois

        return lookup_whois(args.target)
    if args.command == "phone":
        from modules.phone_lookup import lookup_phone

        return lookup_phone(args.target)
    if args.command == "email":
        from modules.email_osint import analyze_email

        return analyze_email(args.target, reputation=not args.no_reputation, timeout=args.timeout)
    if args.command == "username":
        from modules.username_search import search_username

        return search_username(args.target, timeout=args.timeout, workers=args.workers)
    if args.command == "subdomain":
        from modules.subdomain_finder import find_subdomains

        return find_subdomains(
            args.target,
            active_dns=args.active_dns,
            timeout=args.timeout,
            workers=args.workers,
        )
    if args.command == "ports":
        from modules.port_scanner import parse_ports, scan_ports

        try:
            ports = parse_ports(args.port_spec)
        except ValueError as exc:
            return ScanResult.failure("port_scanner", args.target, str(exc))
        return scan_ports(args.target, ports, timeout=args.timeout, workers=args.workers)
    if args.command == "exif":
        from modules.exif_extractor import extract_exif

        return extract_exif(args.target)
    return None


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.command in (None, "menu"):
        from phantomrecon import main as interactive_main

        interactive_main()
        return 0
    if args.command == "doctor":
        return run_doctor()
    if args.command == "providers":
        return run_providers()
    if args.command == "config":
        return run_config(as_json=args.as_json)
    if args.command == "plugins":
        return run_plugins(load=args.load, as_json=args.as_json)
    if args.command == "report":
        return run_report(args.input, output_format=args.format, output=args.output)
    if args.command == "module":
        importlib.import_module(MODULES[args.name]).run()
        return 0

    result = _run_direct_command(args)
    if result is None:
        parser.print_help()
        return 2
    return _render_result(result, as_json=args.as_json, output=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
