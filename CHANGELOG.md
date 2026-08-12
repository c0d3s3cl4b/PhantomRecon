# Changelog

All notable changes to PhantomRecon will be documented in this file.

## [2.2.0] - 2026-08-12

### Added
- Python entry-point based third-party plugin discovery through `phantomrecon.plugins`
- `phantomrecon plugins` diagnostics with metadata-only discovery by default
- `phantomrecon config` for effective runtime configuration
- unified JSON and HTML report generation through `phantomrecon report`
- configurable report directory with `PHANTOMRECON_REPORT_DIR`
- per-host HTTP request throttling with `PHANTOMRECON_HTTP_MIN_INTERVAL`
- provider readiness, metadata, descriptions, and JSON diagnostics
- automated tag-driven GitHub Release workflow with wheel and source distribution assets

### Changed
- improved provider diagnostics and terminal tables
- shared HTTP client now honors Retry-After and applies bounded per-host throttling
- package and CLI promoted to stable `2.2.0`

### Safety
- plugin discovery does not import third-party plugin code unless `--load` is explicitly requested
- active DNS checks and TCP scanning retain their existing bounded limits and authorization guidance

## [2.1.0] - 2026-08-12

### Added
- installable `phantomrecon` CLI with direct module commands
- structured `ScanResult` output and JSON/file export
- `doctor` runtime diagnostics and `providers` provider diagnostics
- centralized environment-aware runtime settings
- shared HTTP session with bounded retry/backoff behavior
- provider registry with built-in `ip-api`, `emailrep`, and `crt.sh` providers
- unit tests and GitHub Actions across Python 3.10, 3.11, and 3.12
- release documentation, contribution guidance, and security policy

### Changed
- refactored all eight engines to separate analysis logic from terminal presentation
- migrated IP lookup, email reputation, and passive subdomain discovery to the shared provider layer
- made subdomain discovery passive-first with explicit optional DNS checks
- replaced protocol-agnostic HTTP banner probing in the port scanner with bounded TCP connect checks
- normalized machine-readable output for automation and integrations

### Safety
- active DNS checks and TCP port scans remain bounded
- active reconnaissance is documented for systems and domains the user owns or is explicitly authorized to assess

### Supported engines
- IP Lookup
- WHOIS Lookup
- Phone OSINT
- Email OSINT
- Username Search
- Subdomain Finder
- Port Scanner
- EXIF Extractor
