"""
PhantomRecon - Username Search Module
Searches for a username across 25+ social media platforms.
"""

import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.table import Table
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import box

from core.banner import show_module_banner, print_success, print_error, print_info, get_input, console
from core.utils import ask_save_report, pause


# Platform definitions: (name, url_template, error_type, error_indicator)
# error_type: "status" = check HTTP status, "text" = check for text in response
PLATFORMS = [
    ("GitHub", "https://github.com/{}", "status", None),
    ("Twitter/X", "https://x.com/{}", "status", None),
    ("Instagram", "https://www.instagram.com/{}/", "status", None),
    ("Reddit", "https://www.reddit.com/user/{}/", "status", None),
    ("TikTok", "https://www.tiktok.com/@{}", "status", None),
    ("YouTube", "https://www.youtube.com/@{}", "status", None),
    ("Pinterest", "https://www.pinterest.com/{}/", "status", None),
    ("Twitch", "https://www.twitch.tv/{}", "status", None),
    ("Steam", "https://steamcommunity.com/id/{}", "status", None),
    ("Medium", "https://medium.com/@{}", "status", None),
    ("GitLab", "https://gitlab.com/{}", "status", None),
    ("Bitbucket", "https://bitbucket.org/{}/", "status", None),
    ("Dev.to", "https://dev.to/{}", "status", None),
    ("HackerOne", "https://hackerone.com/{}", "status", None),
    ("Keybase", "https://keybase.io/{}", "status", None),
    ("Gravatar", "https://en.gravatar.com/{}", "status", None),
    ("Patreon", "https://www.patreon.com/{}", "status", None),
    ("Spotify", "https://open.spotify.com/user/{}", "status", None),
    ("SoundCloud", "https://soundcloud.com/{}", "status", None),
    ("Flickr", "https://www.flickr.com/people/{}/", "status", None),
    ("Telegram", "https://t.me/{}", "status", None),
    ("Docker Hub", "https://hub.docker.com/u/{}", "status", None),
    ("npm", "https://www.npmjs.com/~{}", "status", None),
    ("PyPI", "https://pypi.org/user/{}/", "status", None),
    ("Replit", "https://replit.com/@{}", "status", None),
]


def check_platform(platform_name: str, url: str) -> dict:
    """Check if a username exists on a given platform."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(url, headers=headers, timeout=8, allow_redirects=False)

        # Most platforms return 200 for existing users and 404 for non-existing
        found = response.status_code == 200

        return {
            "platform": platform_name,
            "url": url,
            "found": found,
            "status_code": response.status_code,
        }
    except requests.RequestException:
        return {
            "platform": platform_name,
            "url": url,
            "found": False,
            "status_code": "Error",
        }


def run():
    """Run the username search module."""
    show_module_banner("Username Search", "👤")

    print_info("Enter the username you want to search for")
    target = get_input("Username")

    if not target:
        print_error("No username entered.")
        pause()
        return

    if len(target) < 2:
        print_error("Username too short!")
        pause()
        return

    print_info(f"Searching for [bold]{target}[/bold] across {len(PLATFORMS)} platforms...")
    console.print()

    found_profiles = []
    not_found = []

    with Progress(
        SpinnerColumn(style="cyan"),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=40, complete_style="green"),
        TextColumn("[bold]{task.completed}/{task.total}"),
        console=console,
    ) as progress:
        task = progress.add_task("Scanning platforms...", total=len(PLATFORMS))

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {}
            for name, url_template, error_type, error_indicator in PLATFORMS:
                url = url_template.format(target)
                future = executor.submit(check_platform, name, url)
                futures[future] = name

            for future in as_completed(futures):
                result = future.result()
                if result["found"]:
                    found_profiles.append(result)
                else:
                    not_found.append(result)
                progress.advance(task)

    # Display results
    console.print()

    if found_profiles:
        table = Table(
            title=f"[bold green]✅ Profiles Found ({len(found_profiles)})[/bold green]",
            box=box.ROUNDED,
            border_style="green",
            padding=(0, 1),
        )
        table.add_column("#", style="bold yellow", justify="center", width=4)
        table.add_column("Platform", style="bold white", width=15)
        table.add_column("URL", style="cyan", width=50)
        table.add_column("Status", style="green", justify="center", width=8)

        for i, profile in enumerate(sorted(found_profiles, key=lambda x: x["platform"]), 1):
            table.add_row(
                str(i),
                profile["platform"],
                profile["url"],
                str(profile["status_code"]),
            )

        console.print(Align.center(table))
    else:
        print_error("No profiles found on any platform.")

    console.print()

    summary = {
        "Username": target,
        "Platforms Scanned": str(len(PLATFORMS)),
        "Profiles Found": str(len(found_profiles)),
        "Not Found": str(len(not_found)),
    }

    # Add found URLs to report
    report_data = {**summary}
    for profile in found_profiles:
        report_data[f"📌 {profile['platform']}"] = profile["url"]

    ask_save_report(report_data, "username_search", target)

    pause()
