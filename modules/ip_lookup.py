"""PhantomRecon IP lookup module."""

from __future__ import annotations

import socket

import requests

import core.builtin_providers  # noqa: F401
from core.banner import (
    console,
    get_input,
    print_error,
    print_info,
    print_success,
    show_module_banner,
)
from core.providers import registry
from core.result import ScanResult
from core.utils import (
    ask_save_report,
    display_results_table,
    pause,
    resolve_domain,
    validate_domain,
    validate_ip,
)

IP_API_FIELDS = (
    "status,message,continent,country,countryCode,region,regionName,city,zip,"
    "lat,lon,timezone,isp,org,as,asname,reverse,mobile,proxy,hosting,query"
)


def normalize_target(target: str) -> tuple[str, str | None]:
    target = target.strip().lower()
    if validate_ip(target):
        return target, None
    if not validate_domain(target):
        raise ValueError("Invalid IP address or domain")
    resolved = resolve_domain(target)
    if not resolved:
        raise ValueError(f"Could not resolve domain: {target}")
    return resolved, target


def lookup_ip(target: str, timeout: float = 10.0) -> ScanResult:
    try:
        ip, original_domain = normalize_target(target)
    except ValueError as exc:
        return ScanResult.failure("ip_lookup", target, str(exc))

    provider = registry.get("ip-api")
    try:
        payload = provider.handler(ip, fields=IP_API_FIELDS, timeout=timeout)
    except (requests.RequestException, ValueError) as exc:
        return ScanResult.failure("ip_lookup", target, f"IP service request failed: {exc}")

    if not isinstance(payload, dict) or payload.get("status") != "success":
        if isinstance(payload, dict):
            message = payload.get("message", "IP lookup failed")
        else:
            message = "IP lookup failed"
        return ScanResult.failure("ip_lookup", target, message)

    try:
        reverse_dns = socket.gethostbyaddr(ip)[0]
    except (socket.herror, socket.gaierror, OSError):
        reverse_dns = payload.get("reverse") or None

    data = {
        "ip": payload.get("query") or ip,
        "continent": payload.get("continent"),
        "country": payload.get("country"),
        "country_code": payload.get("countryCode"),
        "region": payload.get("regionName"),
        "region_code": payload.get("region"),
        "city": payload.get("city"),
        "zip_code": payload.get("zip"),
        "latitude": payload.get("lat"),
        "longitude": payload.get("lon"),
        "timezone": payload.get("timezone"),
        "isp": payload.get("isp"),
        "organization": payload.get("org"),
        "as": payload.get("as"),
        "as_name": payload.get("asname"),
        "reverse_dns": reverse_dns,
        "mobile": bool(payload.get("mobile")),
        "proxy": bool(payload.get("proxy")),
        "hosting": bool(payload.get("hosting")),
        "provider": provider.name,
    }
    if original_domain:
        data["original_domain"] = original_domain
    return ScanResult(module="ip_lookup", target=target, data=data)


def _display_data(result: ScanResult) -> dict[str, object]:
    data = result.data
    country = data.get("country") or "N/A"
    if data.get("country_code"):
        country = f"{country} ({data['country_code']})"
    region = data.get("region") or "N/A"
    if data.get("region_code"):
        region = f"{region} ({data['region_code']})"
    values: dict[str, object] = {
        "IP Address": data.get("ip") or "N/A",
        "Continent": data.get("continent") or "N/A",
        "Country": country,
        "Region": region,
        "City": data.get("city") or "N/A",
        "Zip Code": data.get("zip_code") or "N/A",
        "Coordinates": f"{data.get('latitude')}, {data.get('longitude')}",
        "Time Zone": data.get("timezone") or "N/A",
        "ISP": data.get("isp") or "N/A",
        "Organization": data.get("organization") or "N/A",
        "AS": data.get("as") or "N/A",
        "AS Name": data.get("as_name") or "N/A",
        "Reverse DNS": data.get("reverse_dns") or "N/A",
        "Mobile": "✅ Yes" if data.get("mobile") else "❌ No",
        "Proxy/VPN": "✅ Yes" if data.get("proxy") else "❌ No",
        "Hosting": "✅ Yes" if data.get("hosting") else "❌ No",
    }
    if data.get("original_domain"):
        values["Original Domain"] = data["original_domain"]
    return values


def run() -> None:
    show_module_banner("IP Address Lookup", "🌐")
    print_info("Enter IP address or domain name (e.g., 8.8.8.8 or example.com)")
    target = get_input("IP/Domain")
    if not target:
        print_error("No target entered.")
        pause()
        return
    print_info("Querying IP information...")
    result = lookup_ip(target)
    if result.status != "success":
        print_error(result.errors[0] if result.errors else "IP lookup failed")
        pause()
        return
    results = _display_data(result)
    print_success("IP information gathering complete!")
    display_results_table("🌐 IP Lookup Results", results)
    lat = result.data.get("latitude")
    lon = result.data.get("longitude")
    if lat is not None and lon is not None:
        map_url = f"https://www.google.com/maps?q={lat},{lon}"
        console.print(f"  [cyan]🗺  Map:[/cyan] [link={map_url}]{map_url}[/link]")
    ask_save_report(results, "ip_lookup", target)
    pause()
