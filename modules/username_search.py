"""Username OSINT across public profile URLs."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from rich import box
from rich.align import Align
from rich.table import Table

from core.banner import (
    console,
    get_input,
    print_error,
    print_info,
    show_module_banner,
)
from core.result import ScanResult
from core.utils import ask_save_report, pause

PLATFORMS = [
    ("GitHub", "https://github.com/{}"),
    ("Twitter/X", "https://x.com/{}"),
    ("Instagram", "https://www.instagram.com/{}/"),
    ("Reddit", "https://www.reddit.com/user/{}/"),
    ("TikTok", "https://www.tiktok.com/@{}"),
    ("YouTube", "https://www.youtube.com/@{}"),
    ("Pinterest", "https://www.pinterest.com/{}/"),
    ("Twitch", "https://www.twitch.tv/{}"),
    ("Steam", "https://steamcommunity.com/id/{}"),
    ("Medium", "https://medium.com/@{}"),
    ("GitLab", "https://gitlab.com/{}"),
    ("Bitbucket", "https://bitbucket.org/{}/"),
    ("Dev.to", "https://dev.to/{}"),
    ("HackerOne", "https://hackerone.com/{}"),
    ("Keybase", "https://keybase.io/{}"),
    ("Gravatar", "https://en.gravatar.com/{}"),
    ("Patreon", "https://www.patreon.com/{}"),
    ("Spotify", "https://open.spotify.com/user/{}"),
    ("SoundCloud", "https://soundcloud.com/{}"),
    ("Flickr", "https://www.flickr.com/people/{}/"),
    ("Telegram", "https://t.me/{}"),
    ("Docker Hub", "https://hub.docker.com/u/{}"),
    ("npm", "https://www.npmjs.com/~{}"),
    ("PyPI", "https://pypi.org/user/{}/"),
    ("Replit", "https://replit.com/@{}"),
]

HEADERS = {
    "User-Agent": "PhantomRecon/2.0 (+authorized OSINT)",
    "Accept": "text/html,*/*",
}


def check_platform(
    platform: str,
    url: str,
    timeout: float = 8.0,
) -> dict[str, object]:
    """Check whether a public profile URL appears to exist."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=False,
        )
        return {
            "platform": platform,
            "url": url,
            "found": response.status_code == 200,
            "status_code": response.status_code,
            "error": None,
        }
    except requests.RequestException as exc:
        return {
            "platform": platform,
            "url": url,
            "found": False,
            "status_code": None,
            "error": str(exc),
        }


def search_username(
    username: str,
    *,
    timeout: float = 8.0,
    workers: int = 10,
) -> ScanResult:
    """Search public profile URLs for a username."""
    username = username.strip()
    if len(username) < 2 or any(char.isspace() for char in username):
        return ScanResult.failure("username_search", username, "Invalid username")

    workers = max(1, min(workers, 20))
    results: list[dict[str, object]] = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                check_platform,
                name,
                template.format(username),
                timeout,
            )
            for name, template in PLATFORMS
        ]
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda item: str(item["platform"]))
    found = [item for item in results if item["found"]]
    errors = [item for item in results if item["error"]]

    return ScanResult(
        module="username_search",
        target=username,
        data={
            "username": username,
            "platforms_scanned": len(results),
            "profiles_found": len(found),
            "request_errors": len(errors),
            "profiles": found,
            "checks": results,
        },
    )


def run() -> None:
    """Run the classic interactive username search interface."""
    show_module_banner("Username Search", "👤")
    print_info("Enter the username you want to search for")
    target = get_input("Username")
    if not target:
        print_error("No username entered.")
        pause()
        return

    print_info(f"Searching {len(PLATFORMS)} public profile URLs...")
    result = search_username(target)
    if result.status != "success":
        print_error(result.errors[0])
        pause()
        return

    profiles = result.data["profiles"]
    if profiles:
        table = Table(
            title=f"[bold green]Profiles Found ({len(profiles)})[/bold green]",
            box=box.ROUNDED,
            border_style="green",
        )
        table.add_column("Platform")
        table.add_column("URL")
        table.add_column("Status")
        for profile in profiles:
            table.add_row(
                str(profile["platform"]),
                str(profile["url"]),
                str(profile["status_code"]),
            )
        console.print(Align.center(table))
    else:
        print_error("No profiles positively identified.")

    report = {
        "Username": target,
        "Platforms Scanned": result.data["platforms_scanned"],
        "Profiles Found": result.data["profiles_found"],
    }
    for profile in profiles:
        report[str(profile["platform"])] = profile["url"]

    ask_save_report(report, "username_search", target)
    pause()
