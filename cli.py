"""Command-line entry point for PhantomRecon V2."""

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

VERSION = "2.0.0a1"
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
        description="PhantomRecon V2 - OSINT and authorized reconnaissance framework",
    )
    parser.add_argument("--version", action="version", version=f"PhantomRecon {VERSION}")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("menu", help="Open the classic interactive menu")
    subparsers.add_parser("doctor", help="Check runtime, config, and dependencies")
    subparsers.add_parser("providers", help="List registered external data providers")

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

    table = Table(title="PhantomRecon V2 Doctor")
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

        return analyze_email(
            args.target,
            reputation=not args.no_reputation,
            timeout=args.timeout,
        )
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
        return scan_ports(
            args.target,
            ports,
            timeout=args.timeout,
            workers=args.workers,
        )
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
