"""
PhantomRecon - Utility Functions
Common helpers used across all modules
"""

import os
import re
import json
import socket
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich import box

console = Console()


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def validate_ip(ip: str) -> bool:
    """Validate an IPv4 address."""
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    parts = ip.split(".")
    return all(0 <= int(part) <= 255 for part in parts)


def validate_email(email: str) -> bool:
    """Validate an email address format."""
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """Validate a phone number format (must start with +)."""
    pattern = r"^\+\d{7,15}$"
    return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))


def validate_domain(domain: str) -> bool:
    """Validate a domain name."""
    pattern = r"^([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


def resolve_domain(domain: str) -> str | None:
    """Resolve a domain to its IP address."""
    try:
        return socket.gethostbyname(domain)
    except socket.gaierror:
        return None


def save_report(data: dict, module_name: str, target: str) -> str:
    """Save scan results to a JSON report file."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_target = re.sub(r"[^\w\-.]", "_", target)
    filename = f"{module_name}_{safe_target}_{timestamp}.json"
    filepath = os.path.join(reports_dir, filename)

    report = {
        "tool": "PhantomRecon",
        "module": module_name,
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "results": data,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)

    return filepath


def display_results_table(title: str, data: dict, key_style: str = "cyan", value_style: str = "white"):
    """Display results in a formatted Rich table."""
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        box=box.ROUNDED,
        border_style="dim cyan",
        padding=(0, 2),
        show_header=False,
    )

    table.add_column("Key", style=f"bold {key_style}", width=25)
    table.add_column("Value", style=value_style, width=50)

    for key, value in data.items():
        if value is None or value == "":
            value = "[dim]N/A[/dim]"
        elif isinstance(value, (list, tuple)):
            value = ", ".join(str(v) for v in value)
        else:
            value = str(value)
        table.add_row(str(key), value)

    console.print()
    console.print(Align.center(table))
    console.print()


def ask_save_report(data: dict, module_name: str, target: str):
    """Ask user if they want to save the report."""
    try:
        choice = console.input("\n  [bold cyan]┌──([/bold cyan][bold yellow]Save Report?[/bold yellow][bold cyan])\n  └──▶ [y/N]: [/bold cyan]").strip().lower()
        if choice == "y":
            filepath = save_report(data, module_name, target)
            console.print(f"  [green]✔[/green]  Report saved: [cyan]{filepath}[/cyan]")
        else:
            console.print(f"  [dim]Report not saved.[/dim]")
    except (EOFError, KeyboardInterrupt):
        pass


def pause():
    """Pause and wait for user input."""
    try:
        console.input("\n  [dim cyan]Press Enter to continue...[/dim cyan]")
    except (EOFError, KeyboardInterrupt):
        pass
