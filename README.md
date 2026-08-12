# 👻 PhantomRecon V2

**PhantomRecon** is a modular OSINT and authorized reconnaissance framework written in Python. V2 keeps the classic interactive Rich interface while adding structured engines, an installable CLI, JSON output, tests, CI, and a shared provider layer.

> Use PhantomRecon only on systems, accounts, domains, files, and infrastructure you own or are explicitly authorized to assess.

## Highlights

- 8 modular reconnaissance and OSINT engines
- installable `phantomrecon` command
- machine-readable `ScanResult` output
- JSON export with `--json` and `--output`
- classic interactive cyberpunk/Rich menu remains available
- bounded concurrency and timeout controls
- passive-first subdomain discovery
- bounded TCP connect scanning for authorized targets
- centralized HTTP retry/backoff policy
- pluggable external data provider registry
- environment-aware runtime settings
- unit tests and GitHub Actions across Python 3.10, 3.11, and 3.12

## Modules

| Command | Purpose |
| --- | --- |
| `phone` | phone-number metadata and validation |
| `ip` | public IP/domain network information |
| `email` | email format, MX, provider and optional reputation data |
| `username` | public profile URL checks across multiple platforms |
| `whois` | normalized domain WHOIS information |
| `subdomain` | passive certificate-transparency discovery with optional DNS checks |
| `ports` | bounded TCP connect scan for authorized targets |
| `exif` | local image metadata and GPS extraction |

## Requirements

- Python 3.10+
- pip

## Installation

```bash
git clone https://github.com/c0d3s3cl4b/PhantomRecon.git
cd PhantomRecon
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

Verify the environment:

```bash
phantomrecon doctor
phantomrecon providers
phantomrecon --version
```

## Runtime Configuration

PhantomRecon V2.1 reads optional environment variables for shared network behavior:

```bash
PHANTOMRECON_HTTP_TIMEOUT=10
PHANTOMRECON_HTTP_RETRIES=2
PHANTOMRECON_HTTP_BACKOFF=0.4
PHANTOMRECON_USER_AGENT="PhantomRecon/2.x"
PHANTOMRECON_MAX_WORKERS=32
```

`phantomrecon doctor` reports the active timeout, retry count, and worker limit.

## Provider Layer

External data sources are registered through a shared provider registry. Current built-ins are:

| Provider | Capability |
| --- | --- |
| `ip-api` | IP metadata |
| `emailrep` | optional email reputation |
| `crt.sh` | passive certificate-transparency discovery |

List active providers with:

```bash
phantomrecon providers
```

IP Lookup, Email OSINT reputation, and passive Subdomain Discovery use the same shared HTTP session with bounded retry/backoff behavior.

## Classic Interactive Mode

```bash
phantomrecon
# or
phantomrecon menu
```

Existing modules can also be opened through the compatibility command:

```bash
phantomrecon module ip
phantomrecon module email
phantomrecon module ports
```

## Direct CLI Examples

### IP Lookup

```bash
phantomrecon ip 8.8.8.8
phantomrecon ip example.com --json
phantomrecon ip 8.8.8.8 --output reports/ip.json
```

### WHOIS

```bash
phantomrecon whois example.com --json
```

### Phone OSINT

```bash
phantomrecon phone +14155552671 --json
```

### Email OSINT

```bash
phantomrecon email user@example.com --json
phantomrecon email user@example.com --no-reputation --json
```

### Username Search

```bash
phantomrecon username c0d3s3cl4b --json
```

### Subdomain Discovery

Passive certificate-transparency mode is the default:

```bash
phantomrecon subdomain example.com --json
```

Optional bounded DNS checks must be explicitly enabled and should only be used on authorized domains:

```bash
phantomrecon subdomain example.com --active-dns --json
```

### Port Scanner

The scanner uses TCP connect checks only. It does not send HTTP payloads to arbitrary services. A single invocation is limited to 1024 ports and worker concurrency is bounded.

```bash
phantomrecon ports 192.168.1.10
phantomrecon ports 192.168.1.10 --ports 22,80,443 --json
phantomrecon ports example.com --ports 1-100 --timeout 0.5 --workers 20
```

### EXIF Extractor

```bash
phantomrecon exif photo.jpg
phantomrecon exif photo.jpg --json
phantomrecon exif photo.jpg --output reports/photo.json
```

## Structured Output

V2 engines return a common result model:

```json
{
  "module": "ip_lookup",
  "target": "8.8.8.8",
  "data": {},
  "status": "success",
  "errors": [],
  "timestamp": "2026-08-12T12:00:00+00:00"
}
```

This makes PhantomRecon easier to integrate with scripts, reports, CI workflows, and defensive automation.

## Development

Run the test suite:

```bash
pytest
```

Run Ruff on the V2.1 surface:

```bash
ruff check cli.py core modules tests
```

GitHub Actions validates the project on Python 3.10, 3.11, and 3.12 and runs both `phantomrecon doctor` and `phantomrecon providers` as smoke tests.

## Data Sources

External services may rate-limit, change behavior, or become unavailable. PhantomRecon centralizes retries for eligible GET/HEAD requests and treats optional provider failures separately from local validation where possible.

## Legal and Ethical Use

PhantomRecon is intended for defensive security research, authorized penetration testing, public-information OSINT, education, lab environments, and analysis of files or infrastructure you are permitted to inspect.

Do not use the tool for unauthorized scanning, intrusion, harassment, credential theft, or access to systems without permission.

## License

MIT License. See `LICENSE`.

## Author

[@c0d3s3cl4b](https://github.com/c0d3s3cl4b)
