"""
PhantomRecon - WHOIS Lookup Module
Queries WHOIS data for domain names.
"""

import whois

from core.banner import show_module_banner, print_success, print_error, print_info, get_input, console
from core.utils import validate_domain, display_results_table, ask_save_report, pause


def run():
    """Run the WHOIS lookup module."""
    show_module_banner("WHOIS Lookup", "🔍")

    print_info("Enter the domain name for WHOIS lookup (e.g., example.com)")
    target = get_input("Domain")

    if not target:
        print_error("No domain entered.")
        pause()
        return

    # Clean up domain
    target = target.replace("http://", "").replace("https://", "").split("/")[0]

    if not validate_domain(target):
        print_error("Invalid domain name!")
        pause()
        return

    try:
        print_info(f"Querying WHOIS for {target}...")

        w = whois.whois(target)

        if not w.domain_name:
            print_error("WHOIS information not found.")
            pause()
            return

        # Process domain names
        domain_name = w.domain_name
        if isinstance(domain_name, list):
            domain_name = domain_name[0]

        # Process name servers
        name_servers = w.name_servers
        if isinstance(name_servers, list):
            name_servers = ", ".join(name_servers[:5])

        # Process dates
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]

        expiration_date = w.expiration_date
        if isinstance(expiration_date, list):
            expiration_date = expiration_date[0]

        updated_date = w.updated_date
        if isinstance(updated_date, list):
            updated_date = updated_date[0]

        # Process emails
        emails = w.emails
        if isinstance(emails, list):
            emails = ", ".join(emails)

        results = {
            "Domain": domain_name,
            "Registrar": w.registrar or "N/A",
            "WHOIS Server": w.whois_server or "N/A",
            "Creation Date": str(creation_date) if creation_date else "N/A",
            "Last Update": str(updated_date) if updated_date else "N/A",
            "Expiration Date": str(expiration_date) if expiration_date else "N/A",
            "Name Servers": name_servers or "N/A",
            "Status": ", ".join(w.status[:3]) if isinstance(w.status, list) else (w.status or "N/A"),
            "Organization": w.org or "N/A",
            "Country": w.country or "N/A",
            "State": w.state or "N/A",
            "City": w.city or "N/A",
            "Address": w.address or "N/A",
            "Email": emails or "N/A",
            "DNSSEC": w.dnssec or "N/A",
        }

        print_success("WHOIS lookup complete!")
        display_results_table("🔍 WHOIS Lookup Results", results)

        ask_save_report(results, "whois_lookup", target)

    except Exception as e:
        print_error(f"WHOIS lookup failed: {e}")

    pause()
