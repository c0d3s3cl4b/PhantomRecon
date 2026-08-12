# Contributing to PhantomRecon

Thanks for helping improve PhantomRecon.

## Development setup

```bash
git clone https://github.com/c0d3s3cl4b/PhantomRecon.git
cd PhantomRecon
python -m venv .venv
pip install -e ".[dev]"
```

Run the quality gates before submitting changes:

```bash
ruff check cli.py core modules tests
pytest
phantomrecon doctor
phantomrecon providers
```

## Contribution guidelines

- keep analysis logic separate from terminal presentation
- return machine-readable data through `ScanResult`
- use the shared HTTP/provider layer for external data sources
- keep network concurrency and retries bounded
- add or update tests for behavior changes
- document user-facing CLI changes
- do not commit generated files, bytecode, credentials, API keys, or personal data

## Security and reconnaissance features

Changes that add active reconnaissance must have a legitimate defensive or authorized-testing use case and should use conservative defaults, explicit user intent, bounded concurrency, and clear documentation.

Do not submit functionality intended for credential theft, persistence, stealthy unauthorized access, destructive actions, malware delivery, or evasion of security controls.

## Pull requests

Keep pull requests focused. Explain the problem, the implementation, how it was tested, and any security or compatibility considerations. CI should pass on the supported Python versions before merge.

## Reporting security issues

See `SECURITY.md` for vulnerability reporting guidance.
