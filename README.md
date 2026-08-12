# 👻 PhantomRecon 2.2

**PhantomRecon** is a modular OSINT and authorized reconnaissance framework written in Python. The 2.2 development line adds third-party plugin discovery, unified reporting, richer runtime diagnostics, and automated GitHub releases while keeping the eight structured engines and classic Rich interface.

> Use PhantomRecon only on systems, accounts, domains, files, and infrastructure you own or are explicitly authorized to assess.

## Highlights

- 8 structured reconnaissance and OSINT engines
- installable `phantomrecon` CLI
- machine-readable `ScanResult` output
- JSON export and unified JSON/HTML reporting
- Python entry-point based third-party plugin discovery
- classic interactive cyberpunk/Rich menu
- bounded concurrency, timeouts, DNS checks, and TCP scans
- centralized HTTP retry/backoff policy
- pluggable external provider registry
- environment-aware runtime configuration
- CI on Python 3.10, 3.11, and 3.12
- tag-driven GitHub Release automation

## Install

Stable users should use the latest release. For 2.2 development:

```bash
git clone https://github.com/c0d3s3cl4b/PhantomRecon.git
cd PhantomRecon
git checkout feature/phantomrecon-2.2
pip install -e ".[dev]"
```

Verify the environment:

```bash
phantomrecon --version
phantomrecon doctor
phantomrecon config
phantomrecon providers
phantomrecon plugins
```

## Commands

| Command | Purpose |
| --- | --- |
| `ip` | public IP/domain metadata |
| `whois` | normalized WHOIS information |
| `phone` | phone metadata and validation |
| `email` | email format, MX, provider and optional reputation data |
| `username` | public profile URL checks |
| `subdomain` | passive CT discovery with optional authorized DNS checks |
| `ports` | bounded TCP connect scan for authorized targets |
| `exif` | local image metadata and GPS extraction |
| `providers` | list built-in external providers |
| `plugins` | discover installed third-party PhantomRecon plugins |
| `config` | display effective runtime settings |
| `report` | convert saved ScanResult JSON into JSON/HTML reports |

## Runtime Configuration

```bash
PHANTOMRECON_HTTP_TIMEOUT=10
PHANTOMRECON_HTTP_RETRIES=2
PHANTOMRECON_HTTP_BACKOFF=0.4
PHANTOMRECON_USER_AGENT="PhantomRecon/2.2"
PHANTOMRECON_MAX_WORKERS=32
PHANTOMRECON_REPORT_DIR=reports
```

Show effective values with:

```bash
phantomrecon config
phantomrecon config --json
```

## Provider Layer

Built-in providers currently include `ip-api`, `emailrep`, and `crt.sh`. IP lookup, optional email reputation, and passive subdomain discovery share the same bounded HTTP session and retry policy.

```bash
phantomrecon providers
```

## Plugin System

PhantomRecon 2.2 discovers third-party Python packages through the `phantomrecon.plugins` entry-point group. Discovery is metadata-only by default; plugin code is imported only when `--load` is explicitly supplied.

```bash
phantomrecon plugins
phantomrecon plugins --json
phantomrecon plugins --load
```

A plugin package can register an entry point in its own `pyproject.toml`:

```toml
[project.entry-points."phantomrecon.plugins"]
my-plugin = "my_plugin:plugin"
```

This keeps third-party extensions outside the PhantomRecon core package and isolates load failures during diagnostics.

## Direct CLI Examples

```bash
phantomrecon ip 8.8.8.8 --json
phantomrecon whois example.com --json
phantomrecon phone +14155552671 --json
phantomrecon email user@example.com --no-reputation --json
phantomrecon username c0d3s3cl4b --json
phantomrecon subdomain example.com --json
phantomrecon ports 192.168.1.10 --ports 22,80,443 --json
phantomrecon exif photo.jpg --json
```

Active DNS checks and TCP port scans should only be used against explicitly authorized targets.

## Reporting

Save a normal engine result first:

```bash
phantomrecon ip 8.8.8.8 --output reports/ip.json
```

Then create a standalone HTML or normalized JSON report:

```bash
phantomrecon report reports/ip.json --format html --output reports/ip.html
phantomrecon report reports/ip.json --format json --output reports/ip-report.json
```

HTML values are escaped before rendering. Unified report JSON uses the schema identifier `phantomrecon.report.v1` and can contain multiple structured results.

## Classic Interactive Mode

```bash
phantomrecon
phantomrecon menu
phantomrecon module ip
```

## Development

```bash
pytest
ruff check cli.py core modules tests
phantomrecon doctor
phantomrecon providers
phantomrecon plugins
phantomrecon config --json
```

GitHub Actions validates Python 3.10, 3.11, and 3.12. The release workflow builds wheel/sdist artifacts and automatically creates a GitHub Release when a version tag matching the package version is pushed.

## Legal and Ethical Use

PhantomRecon is intended for defensive security research, authorized penetration testing, public-information OSINT, education, lab environments, and analysis of files or infrastructure you are permitted to inspect.

Do not use the tool for unauthorized scanning, intrusion, harassment, credential theft, or access to systems without permission.

## Project Files

See `CHANGELOG.md`, `SECURITY.md`, and `CONTRIBUTING.md` for release history, vulnerability reporting, and contribution guidance.

## License

MIT License. See `LICENSE`.

## Author

[@c0d3s3cl4b](https://github.com/c0d3s3cl4b)
