"""
PhantomRecon - Subdomain Finder Module
Discovers subdomains using crt.sh API and DNS brute-force.
"""

import requests
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.table import Table
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

from core.banner import show_module_banner, print_success, print_error, print_info, print_warning, get_input, console
from core.utils import validate_domain, ask_save_report, pause


# Common subdomain wordlist
SUBDOMAIN_WORDLIST = [
    "www", "mail", "ftp", "cpanel", "webmail", "smtp", "pop", "imap",
    "admin", "api", "dev", "staging", "test", "beta", "demo", "app",
    "blog", "shop", "store", "portal", "secure", "vpn", "remote",
    "cloud", "cdn", "static", "assets", "img", "images", "media",
    "ns1", "ns2", "ns3", "dns", "dns1", "dns2", "mx", "mx1", "mx2",
    "login", "auth", "sso", "accounts", "dashboard", "panel",
    "db", "database", "mysql", "postgres", "mongo", "redis", "cache",
    "git", "gitlab", "jenkins", "ci", "deploy", "docker", "k8s",
    "docs", "wiki", "help", "support", "status", "monitor", "grafana",
    "proxy", "gateway", "lb", "internal", "intranet", "corp",
    "m", "mobile", "ws", "wss", "socket", "stream", "live",
    "search", "elastic", "kibana", "log", "logs", "sentry",
    "backup", "bak", "old", "new", "staging2", "uat", "qa",
    "crm", "erp", "hr", "finance", "marketing", "sales",
    "s3", "storage", "files", "upload", "download", "share",
]


def crt_sh_lookup(domain: str) -> set:
    """Query crt.sh for subdomains via SSL certificate transparency logs."""
    subdomains = set()
    try:
        response = requests.get(
            f"https://crt.sh/?q=%.{domain}&output=json",
            timeout=15,
        )
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                name_value = entry.get("name_value", "")
                for name in name_value.split("\n"):
                    name = name.strip().lower()
                    if name and name.endswith(domain) and "*" not in name:
                        subdomains.add(name)
    except (requests.RequestException, ValueError):
        pass
    return subdomains


def dns_bruteforce_check(subdomain: str, domain: str) -> str | None:
    """Check if a subdomain exists via DNS resolution."""
    full_domain = f"{subdomain}.{domain}"
    try:
        answers = dns.resolver.resolve(full_domain, "A")
        if answers:
            ip = str(answers[0])
            return f"{full_domain}:{ip}"
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers,
            dns.resolver.Timeout, Exception):
        pass
    return None


def run():
    """Run the subdomain finder module."""
    show_module_banner("Subdomain Finder", "🌍")

    print_info("Enter the target domain name (e.g., example.com)")
    target = get_input("Domain")

    if not target:
        print_error("No domain entered.")
        pause()
        return

    target = target.replace("http://", "").replace("https://", "").split("/")[0].lower()

    if not validate_domain(target):
        print_error("Invalid domain name!")
        pause()
        return

    all_subdomains = {}

    # Phase 1: crt.sh passive enumeration
    print_info("[1/2] Querying crt.sh (SSL Certificate Transparency Logs)...")
    crt_results = crt_sh_lookup(target)

    if crt_results:
        print_success(f"Found {len(crt_results)} subdomains from crt.sh!")
        for sub in crt_results:
            all_subdomains[sub] = "crt.sh"
    else:
        print_warning("No results from crt.sh.")

    # Phase 2: DNS brute-force
    print_info(f"[2/2] Starting DNS brute-force scan ({len(SUBDOMAIN_WORDLIST)} words)...")
    console.print()

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="green"),
        TextColumn("[bold]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("DNS Brute-Force...", total=len(SUBDOMAIN_WORDLIST))

        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {}
            for word in SUBDOMAIN_WORDLIST:
                future = executor.submit(dns_bruteforce_check, word, target)
                futures[future] = word

            for future in as_completed(futures):
                result = future.result()
                if result:
                    full_domain, ip = result.split(":")
                    if full_domain not in all_subdomains:
                        all_subdomains[full_domain] = f"DNS ({ip})"
                progress.advance(task)

    # Display results
    console.print()

    if all_subdomains:
        table = Table(
            title=f"[bold green]🌍 Subdomains Found ({len(all_subdomains)})[/bold green]",
            box=box.ROUNDED,
            border_style="green",
            padding=(0, 1),
        )
        table.add_column("#", style="bold yellow", justify="center", width=4)
        table.add_column("Subdomain", style="bold cyan", width=40)
        table.add_column("Source", style="dim white", width=20)

        for i, (subdomain, source) in enumerate(sorted(all_subdomains.items()), 1):
            table.add_row(str(i), subdomain, source)

        console.print(Align.center(table))
    else:
        print_error("No subdomains found.")

    console.print()
    console.print(f"  [cyan]📊 Summary:[/cyan] Found [bold]{len(all_subdomains)}[/bold] unique subdomains")

    report_data = {
        "Target Domain": target,
        "Total Subdomains": str(len(all_subdomains)),
        "crt.sh": str(len(crt_results)),
        "DNS Brute-Force": str(len(all_subdomains) - len(crt_results)),
    }
    for sub, src in sorted(all_subdomains.items()):
        report_data[sub] = src

    ask_save_report(report_data, "subdomain_finder", target)

    pause()
