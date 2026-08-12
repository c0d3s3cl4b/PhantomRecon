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

from core.banner import AUTHOR

VERSION = "2.0.0a1"
console = Console()

MODULES = {
    "phone": "modules.phone_lookup",
    "ip": "modules.ip_lookup",
    "email": "modules.email_osint",
    "username": "modules.username_search",
    "whois": "modules.whois_lookup",
    "subdomain": "modules.subdomain_finder",
    "ports": "modules.port_scanner",
    "exif": "modules.exif_extractor",
}

DEPENDENCIES = {
    "rich": "Rich terminal UI",
    "requests": "HTTP client",
    "phonenumbers": "Phone OSINT",
    "whois": "WHOIS lookup",
    "dns": "DNS resolution",
    "PIL": "Image metadata",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phantomrecon",
        description="PhantomRecon V2 - modular OSINT and authorized reconnaissance framework",
    )
    parser.add_argument("--version", action="version", version=f"PhantomRecon {VERSION}")

    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("menu", help="Open the classic interactive PhantomRecon menu")
    subparsers.add_parser("doctor", help="Check runtime and dependency health")

    module_parser = subparsers.add_parser(
        "module",
        help="Run one of the existing interactive modules",
    )
    module_parser.add_argument("name", choices=sorted(MODULES))

    ip_parser = subparsers.add_parser("ip", help="Look up an IP address or domain")
    ip_parser.add_argument("target", help="IP address or domain name")
    ip_parser.add_argument("--json", action="store_true", dest="as_json", help="Emit JSON")
    ip_parser.add_argument("--output", type=Path, help="Write structured JSON to a file")
    ip_parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")

    return parser


def run_doctor() -> int:
    table = Table(title="PhantomRecon V2 Doctor")
    table.add_column("Component")
    table.add_column("Status")
    table.add_column("Details")

    py_ok = sys.version_info >= (3, 10)
    table.add_row(
        "Python",
        "OK" if py_ok else "FAIL",
        f"{platform.python_version()} (requires >= 3.10)",
    )

    healthy = py_ok
    for module_name, purpose in DEPENDENCIES.items():
        try:
            importlib.import_module(module_name)
            status = "OK"
        except ImportError:
            status = "MISSING"
            healthy = False
        table.add_row(module_name, status, purpose)

    console.print(table)
    return 0 if healthy else 1


def run_interactive_module(name: str) -> int:
    module = importlib.import_module(MODULES[name])
    module.run()
    return 0


def _write_json(payload: dict[str, object], output: Path | None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)


def run_ip(target: str, *, as_json: bool, output: Path | None, timeout: float) -> int:
    from modules.ip_lookup import lookup_ip

    result = lookup_ip(target, timeout=timeout)
    payload = result.to_dict()

    if as_json or output is not None:
        _write_json(payload, output)
        if output is not None and not as_json:
            console.print(f"[green]Saved:[/green] {output}")
    elif result.status == "success":
        table = Table(title=f"IP Lookup: {target}")
        table.add_column("Field", style="cyan")
        table.add_column("Value")
        for key, value in result.data.items():
            table.add_row(key.replace("_", " ").title(), str(value))
        console.print(table)
    else:
        console.print(f"[red]Error:[/red] {result.errors[0] if result.errors else 'lookup failed'}")

    return 0 if result.status == "success" else 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "menu"):
        from phantomrecon import main as interactive_main

        interactive_main()
        return 0

    if args.command == "doctor":
        return run_doctor()

    if args.command == "module":
        return run_interactive_module(args.name)

    if args.command == "ip":
        return run_ip(
            args.target,
            as_json=args.as_json,
            output=args.output,
            timeout=args.timeout,
        )

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
