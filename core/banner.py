"""
PhantomRecon - Banner & UI Components
Cyberpunk-themed terminal UI using Rich library
"""

import random

from rich import box
from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()

VERSION = "2.0.0a1"
AUTHOR = "c0d3s3cl4b"

BANNER_ART = r"""
    ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
    ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
    ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
    ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
    ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
    ██████╗ ███████╗ ██████╗ ██████╗ ███╗   ██╗
    ██╔══██╗██╔════╝██╔════╝██╔═══██╗████╗  ██║
    ██████╔╝█████╗  ██║     ██║   ██║██╔██╗ ██║
    ██╔══██╗██╔══╝  ██║     ██║   ██║██║╚██╗██║
    ██║  ██║███████╗╚██████╗╚██████╔╝██║ ╚████║
    ╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝
"""

TAGLINES = [
    ">> Shadows don't leave fingerprints <<",
    ">> Eyes everywhere, traces nowhere <<",
    ">> The ghost in the machine <<",
    ">> Information is power <<",
    ">> Reconnaissance is the key <<",
]


def show_banner():
    """Display the main PhantomRecon banner."""
    console.clear()

    tagline = random.choice(TAGLINES)

    banner_text = Text(BANNER_ART, style="bold cyan")
    console.print(banner_text, justify="center")

    info_text = Text()
    info_text.append("  ⚡ ", style="yellow")
    info_text.append("Mobile Pentest & OSINT Framework", style="bold white")
    info_text.append(f"  │  v{VERSION}", style="dim cyan")
    info_text.append(f"  │  @{AUTHOR}", style="dim magenta")
    console.print(Align.center(info_text))

    console.print(Align.center(Text(f"\n  {tagline}\n", style="dim green italic")))

    console.print(
        Align.center(
            Text(
                "━" * 60,
                style="dim cyan",
            )
        )
    )
    console.print()


def show_menu():
    """Display the main menu with all available modules."""
    table = Table(
        title="[bold cyan]⚙  MODULES[/bold cyan]",
        box=box.DOUBLE_EDGE,
        border_style="cyan",
        title_style="bold cyan",
        show_header=True,
        header_style="bold magenta",
        padding=(0, 2),
    )

    table.add_column("#", style="bold yellow", justify="center", width=4)
    table.add_column("Module", style="bold white", width=28)
    table.add_column("Description", style="dim white", width=40)

    modules = [
        ("01", "📱  Phone Lookup", "Phone number OSINT analysis"),
        ("02", "🌐  IP Lookup", "IP address info gathering & geolocation"),
        ("03", "📧  Email OSINT", "Email address research & validation"),
        ("04", "👤  Username Search", "Social media username scanner"),
        ("05", "🔍  WHOIS Lookup", "Domain WHOIS info lookup"),
        ("06", "🌍  Subdomain Finder", "Subdomain discovery & enumeration"),
        ("07", "🔓  Port Scanner", "TCP port scanning & service detection"),
        ("08", "📸  EXIF Extractor", "EXIF metadata extraction from images"),
        ("00", "🚪  Exit", "Exit the program"),
    ]

    for num, name, desc in modules:
        if num == "00":
            table.add_row(
                f"[red]{num}[/red]",
                f"[red]{name}[/red]",
                f"[dim red]{desc}[/dim red]",
            )
        else:
            table.add_row(num, name, desc)

    console.print(Align.center(table))
    console.print()


def show_module_banner(module_name: str, icon: str = "⚡"):
    """Display a module-specific header."""
    console.print()
    panel = Panel(
        f"[bold white]{module_name}[/bold white]",
        title=f"[cyan]{icon} PhantomRecon[/cyan]",
        border_style="cyan",
        padding=(1, 4),
    )
    console.print(Align.center(panel))
    console.print()


def print_success(message: str):
    """Print a success message."""
    console.print(f"  [green]✔[/green]  {message}")


def print_error(message: str):
    """Print an error message."""
    console.print(f"  [red]✘[/red]  {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"  [cyan]ℹ[/cyan]  {message}")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"  [yellow]⚠[/yellow]  {message}")


def get_input(prompt: str = "Target") -> str:
    """Get user input with styled prompt."""
    try:
        return console.input(
            f"\n  [bold cyan]┌──([/bold cyan][bold yellow]PhantomRecon[/bold yellow][bold cyan])─[{prompt}]\n"
            "  └──▶ [/bold cyan]"
        ).strip()
    except (EOFError, KeyboardInterrupt):
        return ""
