"""Passive-first subdomain discovery with optional DNS wordlist checks."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import dns.resolver
import requests
from rich import box
from rich.align import Align
from rich.table import Table

import core.builtin_providers  # noqa: F401
from core.banner import (
    console,
    get_input,
    print_error,
    print_info,
    show_module_banner,
)
from core.providers import registry
from core.result import ScanResult
from core.utils import ask_save_report, pause, validate_domain

SUBDOMAIN_WORDLIST = [
    "www", "mail", "api", "dev", "staging", "test", "app", "blog", "shop",
    "portal", "cdn", "static", "assets", "auth", "sso", "docs", "status",
]

DNS_ERRORS = (
    dns.resolver.NXDOMAIN,
    dns.resolver.NoAnswer,
    dns.resolver.NoNameservers,
    dns.resolver.Timeout,
)


def normalize_domain(domain: str) -> str:
    domain = (
        domain.strip()
        .lower()
        .replace("http://", "")
        .replace("https://", "")
        .split("/")[0]
    )
    if not validate_domain(domain):
        raise ValueError("Invalid domain name")
    return domain


def crt_sh_lookup(domain: str, timeout: float = 15.0) -> set[str]:
    provider = registry.get("crt.sh")
    found: set[str] = set()
    try:
        data = provider.handler(domain, timeout=timeout)
    except (requests.RequestException, ValueError):
        return found
    if not isinstance(data, list):
        return found
    for entry in data:
        if not isinstance(entry, dict):
            continue
        for name in entry.get("name_value", "").split("\n"):
            name = name.strip().lower()
            if name.endswith(f".{domain}") and "*" not in name:
                found.add(name)
    return found


def resolve_subdomain(hostname: str) -> list[str]:
    try:
        return sorted({str(answer) for answer in dns.resolver.resolve(hostname, "A")})
    except DNS_ERRORS:
        return []


def find_subdomains(
    domain: str,
    *,
    active_dns: bool = False,
    timeout: float = 15.0,
    workers: int = 10,
) -> ScanResult:
    try:
        domain = normalize_domain(domain)
    except ValueError as exc:
        return ScanResult.failure("subdomain_finder", domain, str(exc))

    records: dict[str, dict[str, object]] = {
        name: {"hostname": name, "sources": ["crt.sh"], "addresses": []}
        for name in crt_sh_lookup(domain, timeout)
    }

    if active_dns:
        workers = max(1, min(workers, 20))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(resolve_subdomain, f"{word}.{domain}"): f"{word}.{domain}"
                for word in SUBDOMAIN_WORDLIST
            }
            for future in as_completed(futures):
                hostname = futures[future]
                addresses = future.result()
                if not addresses:
                    continue
                record = records.setdefault(
                    hostname,
                    {"hostname": hostname, "sources": [], "addresses": []},
                )
                sources = record["sources"]
                if "dns" not in sources:
                    sources.append("dns")
                record["addresses"] = addresses

    subdomains = sorted(records.values(), key=lambda item: str(item["hostname"]))
    return ScanResult(
        module="subdomain_finder",
        target=domain,
        data={
            "domain": domain,
            "mode": "passive+dns" if active_dns else "passive",
            "provider": "crt.sh",
            "total": len(subdomains),
            "subdomains": subdomains,
        },
    )


def run() -> None:
    show_module_banner("Subdomain Finder", "🌍")
    print_info("Enter the target domain name (passive crt.sh mode)")
    target = get_input("Domain")
    if not target:
        print_error("No domain entered.")
        pause()
        return
    result = find_subdomains(target)
    if result.status != "success":
        print_error(result.errors[0])
        pause()
        return
    entries = result.data["subdomains"]
    if entries:
        table = Table(
            title=f"[bold green]Subdomains Found ({len(entries)})[/bold green]",
            box=box.ROUNDED,
            border_style="green",
        )
        table.add_column("Subdomain")
        table.add_column("Source")
        for entry in entries:
            table.add_row(str(entry["hostname"]), ", ".join(entry["sources"]))
        console.print(Align.center(table))
    else:
        print_error("No subdomains found in certificate transparency data.")
    report = {"Target Domain": result.target, "Total Subdomains": result.data["total"]}
    for entry in entries:
        report[str(entry["hostname"])] = ", ".join(entry["sources"])
    ask_save_report(report, "subdomain_finder", result.target)
    pause()
