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
    "phone": "modules.phone_lookup", "ip": "modules.ip_lookup", "email": "modules.email_osint",
    "username": "modules.username_search", "whois": "modules.whois_lookup",
    "subdomain": "modules.subdomain_finder", "ports": "modules.port_scanner", "exif": "modules.exif_extractor",
}
DEPENDENCIES = {"rich": "Rich terminal UI", "requests": "HTTP client", "phonenumbers": "Phone OSINT", "whois": "WHOIS lookup", "dns": "DNS resolution", "PIL": "Image metadata"}


def _add_output_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON")
    parser.add_argument("--output", type=Path, help="Write structured JSON to a file")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="phantomrecon", description="PhantomRecon V2 - modular OSINT and authorized reconnaissance framework")
    parser.add_argument("--version", action="version", version=f"PhantomRecon {VERSION}")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("menu")
    sub.add_parser("doctor")
    module = sub.add_parser("module")
    module.add_argument("name", choices=sorted(MODULES))

    ip = sub.add_parser("ip", help="Look up an IP address or domain")
    ip.add_argument("target"); ip.add_argument("--timeout", type=float, default=10.0); _add_output_options(ip)
    whois = sub.add_parser("whois", help="Query domain WHOIS data")
    whois.add_argument("target"); _add_output_options(whois)
    phone = sub.add_parser("phone", help="Analyze a phone number")
    phone.add_argument("target"); _add_output_options(phone)
    email = sub.add_parser("email", help="Analyze an email address")
    email.add_argument("target"); email.add_argument("--timeout", type=float, default=10.0); email.add_argument("--no-reputation", action="store_true"); _add_output_options(email)
    username = sub.add_parser("username", help="Search public profile URLs")
    username.add_argument("target"); username.add_argument("--timeout", type=float, default=8.0); username.add_argument("--workers", type=int, default=10); _add_output_options(username)
    subdomain = sub.add_parser("subdomain", help="Discover subdomains from certificate transparency")
    subdomain.add_argument("target")
    subdomain.add_argument("--active-dns", action="store_true", help="Also check a small DNS wordlist; use only on domains you are authorized to assess")
    subdomain.add_argument("--timeout", type=float, default=15.0)
    subdomain.add_argument("--workers", type=int, default=10)
    _add_output_options(subdomain)
    return parser


def run_doctor() -> int:
    table = Table(title="PhantomRecon V2 Doctor")
    table.add_column("Component"); table.add_column("Status"); table.add_column("Details")
    healthy = sys.version_info >= (3, 10)
    table.add_row("Python", "OK" if healthy else "FAIL", f"{platform.python_version()} (requires >= 3.10)")
    for name, purpose in DEPENDENCIES.items():
        try:
            importlib.import_module(name); status = "OK"
        except ImportError:
            status = "MISSING"; healthy = False
        table.add_row(name, status, purpose)
    console.print(table)
    return 0 if healthy else 1


def _write_json(payload: dict[str, object], output: Path | None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True); output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def _render_result(result: ScanResult, *, as_json: bool, output: Path | None) -> int:
    if as_json or output:
        _write_json(result.to_dict(), output)
    elif result.status == "success":
        console.print_json(data=result.to_dict())
    else:
        console.print(f"[red]Error:[/red] {result.errors[0] if result.errors else 'operation failed'}")
    return 0 if result.status == "success" else 1


def main() -> int:
    parser = build_parser(); args = parser.parse_args()
    if args.command in (None, "menu"):
        from phantomrecon import main as interactive_main
        interactive_main(); return 0
    if args.command == "doctor":
        return run_doctor()
    if args.command == "module":
        importlib.import_module(MODULES[args.name]).run(); return 0
    if args.command == "ip":
        from modules.ip_lookup import lookup_ip
        result = lookup_ip(args.target, timeout=args.timeout)
    elif args.command == "whois":
        from modules.whois_lookup import lookup_whois
        result = lookup_whois(args.target)
    elif args.command == "phone":
        from modules.phone_lookup import lookup_phone
        result = lookup_phone(args.target)
    elif args.command == "email":
        from modules.email_osint import analyze_email
        result = analyze_email(args.target, reputation=not args.no_reputation, timeout=args.timeout)
    elif args.command == "username":
        from modules.username_search import search_username
        result = search_username(args.target, timeout=args.timeout, workers=args.workers)
    elif args.command == "subdomain":
        from modules.subdomain_finder import find_subdomains
        result = find_subdomains(args.target, active_dns=args.active_dns, timeout=args.timeout, workers=args.workers)
    else:
        parser.print_help(); return 2
    return _render_result(result, as_json=args.as_json, output=args.output)


if __name__ == "__main__":
    raise SystemExit(main())
