"""
PhantomRecon - IP Lookup Module
Gathers geolocation, ISP, and network information for IP addresses.
"""

import requests
import socket

from core.banner import show_module_banner, print_success, print_error, print_info, get_input, console
from core.utils import validate_ip, validate_domain, resolve_domain, display_results_table, ask_save_report, pause


def run():
    """Run the IP lookup module."""
    show_module_banner("IP Address Lookup", "🌐")

    print_info("Enter IP address or domain name (e.g., 8.8.8.8 or example.com)")
    target = get_input("IP/Domain")

    if not target:
        print_error("No target entered.")
        pause()
        return

    ip = target

    # If domain is entered, resolve to IP
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
            print_error("Invalid IP address or domain.")
            pause()
            return

    try:
        # Query ip-api.com
        print_info("Querying IP information...")
        response = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,continent,country,countryCode,"
            f"region,regionName,city,zip,lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query",
            timeout=10,
        )
        data = response.json()

        if data.get("status") != "success":
            print_error(f"Query failed: {data.get('message', 'Unknown error')}")
            pause()
            return

        # Reverse DNS
        try:
            reverse_dns = socket.gethostbyaddr(ip)[0]
        except (socket.herror, socket.gaierror, OSError):
            reverse_dns = data.get("reverse", "N/A")

        results = {
            "IP Address": data.get("query"),
            "Continent": data.get("continent"),
            "Country": f"{data.get('country')} ({data.get('countryCode')})",
            "Region": f"{data.get('regionName')} ({data.get('region')})",
            "City": data.get("city"),
            "Zip Code": data.get("zip"),
            "Coordinates": f"{data.get('lat')}, {data.get('lon')}",
            "Time Zone": data.get("timezone"),
            "ISP": data.get("isp"),
            "Organization": data.get("org"),
            "AS": data.get("as"),
            "AS Name": data.get("asname"),
            "Reverse DNS": reverse_dns,
            "Mobile": "✅ Yes" if data.get("mobile") else "❌ No",
            "Proxy/VPN": "✅ Yes" if data.get("proxy") else "❌ No",
            "Hosting": "✅ Yes" if data.get("hosting") else "❌ No",
        }

        if target != ip:
            results["Original Domain"] = target

        print_success("IP information gathering complete!")
        display_results_table("🌐 IP Lookup Results", results)

        # Show map link
        lat, lon = data.get("lat"), data.get("lon")
        if lat and lon:
            map_url = f"https://www.google.com/maps?q={lat},{lon}"
            console.print(f"  [cyan]🗺  Map:[/cyan] [link={map_url}]{map_url}[/link]")

        ask_save_report(results, "ip_lookup", target)

    except requests.RequestException as e:
        print_error(f"Bağlantı hatası: {e}")
    except Exception as e:
        print_error(f"Hata oluştu: {e}")

    pause()
