# Security Policy

## Supported version

The latest stable release of PhantomRecon receives security fixes.

| Version | Supported |
| --- | --- |
| 2.1.x | Yes |
| < 2.1 | No |

## Reporting a vulnerability

Please do not publish exploit details for a suspected vulnerability before the maintainer has had a reasonable opportunity to investigate it.

For security-sensitive reports, contact the maintainer through the GitHub profile associated with this repository and clearly mark the message as a PhantomRecon security report. Include:

- affected version or commit
- affected component
- reproduction steps
- expected and observed behavior
- impact assessment
- suggested mitigation, if known

Do not include unrelated secrets, credentials, personal data, or data obtained from systems you were not authorized to assess.

## Scope

Useful reports include vulnerabilities in PhantomRecon itself, such as unsafe file handling, unintended command execution, dependency or packaging issues, credential leakage, or flaws that violate documented safety boundaries.

Reports about third-party services queried by PhantomRecon should normally be reported to those service operators unless PhantomRecon is handling the service response unsafely.

## Responsible use

PhantomRecon is intended for defensive security research, authorized penetration testing, OSINT using public information, education, and lab environments. Active reconnaissance features should only be used against systems or domains the user owns or is explicitly authorized to assess.
