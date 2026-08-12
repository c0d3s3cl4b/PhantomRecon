"""Username OSINT across public profile URLs with conservative verification."""

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

# These sites have sufficiently stable 200/404 profile semantics for a high-confidence
# status-only check. Other platforms frequently return a generic HTTP 200 page for missing
# users, bot challenges, or login walls, so a 200 is reported as an unverified candidate.
RELIABLE_STATUS_PLATFORMS = {
    "Bitbucket",
    "Dev.to",
    "Docker Hub",
    "GitHub",
    "HackerOne",
    "Keybase",
    "PyPI",
}

HEADERS = {
    "User-Agent": "PhantomRecon/2.2.1 (+authorized OSINT)",
    "Accept": "text/html,*/*",
}


def classify_response(platform: str, status_code: int) -> tuple[str, str]:
    """Return a conservative verification state and confidence for an HTTP response."""
    if status_code in {404, 410}:
        return "not_found", "high"
    if status_code == 200 and platform in RELIABLE_STATUS_PLATFORMS:
        return "confirmed", "high"
    if status_code == 200:
        return "candidate", "low"
    return "unknown", "low"


def check_platform(
    platform: str,
    url: str,
    timeout: float = 8.0,
) -> dict[str, object]:
    """Check a public profile URL without treating every HTTP 200 as confirmed."""
    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            allow_redirects=False,
        )
        state, confidence = classify_response(platform, response.status_code)
        return {
            "platform": platform,
            "url": url,
            "found": state == "confirmed",
            "state": state,
            "confidence": confidence,
            "status_code": response.status_code,
            "error": None,
        }
    except requests.RequestException as exc:
        return {
            "platform": platform,
            "url": url,
            "found": False,
            "state": "error",
            "confidence": "low",
            "status_code": None,
            "error": str(exc),
        }


def _state(item: dict[str, object]) -> str:
    value = item.get("state")
    if isinstance(value, str):
        return value
    return "confirmed" if item.get("found") else "not_found"


def search_username(
    username: str,
    *,
    timeout: float = 8.0,
    workers: int = 10,
) -> ScanResult:
    """Search public profile URLs for a username with conservative confidence labels."""
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
    confirmed = [item for item in results if _state(item) == "confirmed"]
    candidates = [item for item in results if _state(item) == "candidate"]
    unknown = [item for item in results if _state(item) == "unknown"]
    errors = [item for item in results if item.get("error")]

    return ScanResult(
        module="username_search",
        target=username,
        data={
            "username": username,
            "platforms_scanned": len(results),
            "profiles_found": len(confirmed),
            "candidate_profiles": len(candidates),
            "unknown_checks": len(unknown),
            "request_errors": len(errors),
            "profiles": confirmed,
            "candidates": candidates,
            "checks": results,
            "verification_note": (
                "Only high-confidence status semantics are counted as confirmed. "
                "Candidate profiles require manual verification."
            ),
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
    candidates = result.data["candidates"]
    if profiles:
        table = Table(
            title=f"[bold green]Confirmed Profiles ({len(profiles)})[/bold green]",
            box=box.ROUNDED,
            border_style="green",
        )
        table.add_column("Platform")
        table.add_column("URL")
        table.add_column("Confidence")
        for profile in profiles:
            table.add_row(
                str(profile["platform"]),
                str(profile["url"]),
                str(profile.get("confidence", "high")),
            )
        console.print(Align.center(table))
    else:
        print_error("No high-confidence profiles identified.")

    if candidates:
        print_info(
            f"{len(candidates)} additional HTTP 200 result(s) require manual verification."
        )

    report = {
        "Username": target,
        "Platforms Scanned": result.data["platforms_scanned"],
        "Confirmed Profiles": result.data["profiles_found"],
        "Candidates": result.data["candidate_profiles"],
    }
    for profile in profiles:
        report[str(profile["platform"])] = profile["url"]

    ask_save_report(report, "username_search", target)
    pause()
