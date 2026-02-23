"""
PhantomRecon - Port Scanner Module
Multi-threaded TCP port scanner with service detection.
"""

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.table import Table
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

from core.banner import show_module_banner, print_success, print_error, print_info, print_warning, get_input, console
from core.utils import validate_ip, validate_domain, resolve_domain, ask_save_report, pause


# Common ports and their services
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 111: "RPCBind", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 465: "SMTPS", 587: "SMTP-Submission",
    993: "IMAPS", 995: "POP3S", 1433: "MSSQL", 1521: "Oracle", 1723: "PPTP",
    2049: "NFS", 3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    5985: "WinRM", 6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt",
    8888: "HTTP-Alt", 9090: "WebSM", 9200: "Elasticsearch", 27017: "MongoDB",
}

TOP_100_PORTS = [
    20, 21, 22, 23, 25, 53, 67, 68, 69, 80, 110, 111, 119, 123, 135, 137,
    138, 139, 143, 161, 162, 179, 194, 389, 443, 445, 465, 514, 515, 520,
    521, 543, 544, 548, 554, 587, 631, 636, 873, 902, 993, 995, 1080, 1194,
    1433, 1434, 1521, 1701, 1723, 1812, 1813, 2049, 2082, 2083, 2181, 2222,
    3128, 3306, 3389, 4443, 5060, 5222, 5432, 5900, 5938, 6379, 6660, 6661,
    6662, 6663, 6665, 6667, 6697, 8000, 8008, 8080, 8081, 8443, 8888, 9000,
    9090, 9091, 9200, 9300, 9418, 9999, 10000, 11211, 27017, 27018, 28017,
    50000, 50070, 50075, 50090, 60010, 60030,
]


def scan_port(ip: str, port: int, timeout: float = 1.0) -> dict | None:
    """Scan a single port on the target IP."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))

        if result == 0:
            # Try banner grabbing
            banner = ""
            try:
                sock.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                banner = banner.split("\n")[0][:60]
            except (socket.timeout, ConnectionResetError, OSError):
                pass

            sock.close()
            service = COMMON_PORTS.get(port, "Unknown")
            return {
                "port": port,
                "status": "OPEN",
                "service": service,
                "banner": banner,
            }
        sock.close()
    except (socket.timeout, ConnectionRefusedError, OSError):
        pass
    return None


def run():
    """Run the port scanner module."""
    show_module_banner("Port Scanner", "🔓")

    print_info("Enter target IP address or domain")
    target = get_input("Target")

    if not target:
        print_error("No target entered.")
        pause()
        return

    ip = target
    if not validate_ip(target):
        if validate_domain(target):
            print_info(f"Resolving domain: {target}")
            resolved = resolve_domain(target)
            if resolved:
                ip = resolved
                print_success(f"Resolved: {target} → {ip}")
            else:
                print_error(f"Could not resolve domain: {target}")
                pause()
                return
        else:
            print_error("Invalid IP address or domain!")
            pause()
            return

    # Scan type selection
    console.print()
    console.print("  [bold cyan]Scan Type:[/bold cyan]")
    console.print("  [yellow]1[/yellow] ─ Quick Scan (Top 100 ports)")
    console.print("  [yellow]2[/yellow] ─ Custom port range")
    console.print()

    try:
        scan_choice = console.input("  [bold cyan]Choice ▶[/bold cyan] ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    ports_to_scan = []

    if scan_choice == "2":
        try:
            port_input = console.input("  [bold cyan]Port range (e.g., 1-1000) ▶[/bold cyan] ").strip()
            if "-" in port_input:
                start, end = port_input.split("-")
                start, end = int(start.strip()), int(end.strip())
                if 1 <= start <= end <= 65535:
                    ports_to_scan = list(range(start, end + 1))
                else:
                    print_error("Invalid port range! (1-65535)")
                    pause()
                    return
            else:
                ports_to_scan = [int(p.strip()) for p in port_input.split(",")]
        except ValueError:
            print_error("Invalid port format!")
            pause()
            return
    else:
        ports_to_scan = TOP_100_PORTS

    print_info(f"Target: {ip} | Ports to scan: {len(ports_to_scan)}")
    console.print()

    open_ports = []

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="green"),
        TextColumn("[bold]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning ports...", total=len(ports_to_scan))

        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {}
            for port in ports_to_scan:
                future = executor.submit(scan_port, ip, port)
                futures[future] = port

            for future in as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
                progress.advance(task)

    # Display results
    console.print()

    if open_ports:
        table = Table(
            title=f"[bold green]🔓 Open Ports ({len(open_ports)})[/bold green]",
            box=box.ROUNDED,
            border_style="green",
            padding=(0, 1),
        )
        table.add_column("Port", style="bold yellow", justify="center", width=8)
        table.add_column("Status", style="bold green", justify="center", width=8)
        table.add_column("Service", style="bold white", width=20)
        table.add_column("Banner", style="dim cyan", width=40)

        for port_info in sorted(open_ports, key=lambda x: x["port"]):
            table.add_row(
                str(port_info["port"]),
                port_info["status"],
                port_info["service"],
                port_info["banner"] or "-",
            )

        console.print(Align.center(table))
    else:
        print_warning("No open ports found.")

    console.print()
    console.print(f"  [cyan]📊 Result:[/cyan] {len(ports_to_scan)} ports scanned, [bold green]{len(open_ports)}[/bold green] open ports found")

    report_data = {
        "Target": ip,
        "Original Target": target,
        "Ports Scanned": str(len(ports_to_scan)),
        "Open Ports": str(len(open_ports)),
    }
    for p in sorted(open_ports, key=lambda x: x["port"]):
        report_data[f"Port {p['port']}"] = f"{p['service']} - {p['banner'] or 'No banner'}"

    ask_save_report(report_data, "port_scanner", target)

    pause()
