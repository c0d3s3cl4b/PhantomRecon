#!/usr/bin/env python3
"""
PhantomRecon - Mobile Pentest & OSINT Framework
A comprehensive reconnaissance and information gathering toolkit.

Author: @c0d3s3cl4b
Version: 2.0.0a1
"""

import os
import sys

# Add project root to path for legacy direct execution compatibility.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.banner import console, print_error, show_banner, show_menu


def main():
    """Main entry point for the classic interactive PhantomRecon menu."""
    while True:
        try:
            show_banner()
            show_menu()

            choice = console.input(
                "  [bold cyan]┌──([/bold cyan][bold yellow]PhantomRecon[/bold yellow][bold cyan])─[Module]\n"
                "  └──▶ [/bold cyan]"
            ).strip()

            if choice == "01" or choice == "1":
                from modules import phone_lookup

                phone_lookup.run()

            elif choice == "02" or choice == "2":
                from modules import ip_lookup

                ip_lookup.run()

            elif choice == "03" or choice == "3":
                from modules import email_osint

                email_osint.run()

            elif choice == "04" or choice == "4":
                from modules import username_search

                username_search.run()

            elif choice == "05" or choice == "5":
                from modules import whois_lookup

                whois_lookup.run()

            elif choice == "06" or choice == "6":
                from modules import subdomain_finder

                subdomain_finder.run()

            elif choice == "07" or choice == "7":
                from modules import port_scanner

                port_scanner.run()

            elif choice == "08" or choice == "8":
                from modules import exif_extractor

                exif_extractor.run()

            elif choice == "00" or choice == "0" or choice.lower() == "exit":
                console.print(
                    "\n  [bold cyan]👻 PhantomRecon shutting down... See you in the shadows![/bold cyan]\n"
                )
                return

            else:
                print_error("Invalid selection! Please enter 01-08 or 00.")
                from core.utils import pause

                pause()

        except KeyboardInterrupt:
            console.print(
                "\n\n  [bold cyan]👻 PhantomRecon shutting down... See you in the shadows![/bold cyan]\n"
            )
            return
        except Exception as exc:
            print_error(f"Unexpected error: {exc}")
            from core.utils import pause

            pause()


if __name__ == "__main__":
    main()
