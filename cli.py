"""Command-line entry point for PhantomRecon V2."""
from __future__ import annotations
import argparse, importlib, json, platform, sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from core.result import ScanResult
VERSION = "2.0.0a1"; console = Console()
MODULES = {"phone":"modules.phone_lookup","ip":"modules.ip_lookup","email":"modules.email_osint","username":"modules.username_search","whois":"modules.whois_lookup","subdomain":"modules.subdomain_finder","ports":"modules.port_scanner","exif":"modules.exif_extractor"}
DEPENDENCIES = {"rich":"Rich terminal UI","requests":"HTTP client","phonenumbers":"Phone OSINT","whois":"WHOIS lookup","dns":"DNS resolution","PIL":"Image metadata"}
def _add_output_options(parser):
    parser.add_argument("--json",action="store_true",dest="as_json",help="Emit JSON"); parser.add_argument("--output",type=Path,help="Write structured JSON to a file")
def build_parser():
    parser=argparse.ArgumentParser(prog="phantomrecon",description="PhantomRecon V2 - modular OSINT and authorized reconnaissance framework"); parser.add_argument("--version",action="version",version=f"PhantomRecon {VERSION}"); sub=parser.add_subparsers(dest="command")
    sub.add_parser("menu"); sub.add_parser("doctor"); mod=sub.add_parser("module"); mod.add_argument("name",choices=sorted(MODULES))
    ip=sub.add_parser("ip"); ip.add_argument("target"); ip.add_argument("--timeout",type=float,default=10.0); _add_output_options(ip)
    wh=sub.add_parser("whois"); wh.add_argument("target"); _add_output_options(wh)
    ph=sub.add_parser("phone"); ph.add_argument("target"); _add_output_options(ph)
    em=sub.add_parser("email"); em.add_argument("target"); em.add_argument("--timeout",type=float,default=10.0); em.add_argument("--no-reputation",action="store_true"); _add_output_options(em)
    us=sub.add_parser("username",help="Search public profile URLs"); us.add_argument("target"); us.add_argument("--timeout",type=float,default=8.0); us.add_argument("--workers",type=int,default=10); _add_output_options(us)
    sd=sub.add_parser("subdomain",help="Discover subdomains from certificate transparency"); sd.add_argument("target"); sd.add_argument("--active-dns",action="store_true",help="Also check a small DNS wordlist; use only on domains you are authorized to assess"); sd.add_argument("--timeout",type=float,default=15.0); sd.add_argument("--workers",type=int,default=10); _add_output_options(sd)
    return parser
def run_doctor():
    table=Table(title="PhantomRecon V2 Doctor"); table.add_column("Component"); table.add_column("Status"); table.add_column("Details"); ok=sys.version_info>=(3,10); table.add_row("Python","OK" if ok else "FAIL",f"{platform.python_version()} (requires >= 3.10)")
    for name,purpose in DEPENDENCIES.items():
        try: importlib.import_module(name); status="OK"
        except ImportError: status="MISSING"; ok=False
        table.add_row(name,status,purpose)
    console.print(table); return 0 if ok else 1
def _write_json(payload,output):
    text=json.dumps(payload,indent=2,ensure_ascii=False)
    if output: output.parent.mkdir(parents=True,exist_ok=True); output.write_text(text+"\n",encoding="utf-8")
    else: print(text)
def _render_result(result:ScanResult,*,as_json,output):
    if as_json or output: _write_json(result.to_dict(),output)
    elif result.status=="success": console.print_json(data=result.to_dict())
    else: console.print(f"[red]Error:[/red] {result.errors[0] if result.errors else 'operation failed'}")
    return 0 if result.status=="success" else 1
def main():
    parser=build_parser(); args=parser.parse_args()
    if args.command in (None,"menu"):
        from phantomrecon import main as interactive_main; interactive_main(); return 0
    if args.command=="doctor": return run_doctor()
    if args.command=="module": importlib.import_module(MODULES[args.name]).run(); return 0
    if args.command=="ip":
        from modules.ip_lookup import lookup_ip; result=lookup_ip(args.target,timeout=args.timeout)
    elif args.command=="whois":
        from modules.whois_lookup import lookup_whois; result=lookup_whois(args.target)
    elif args.command=="phone":
        from modules.phone_lookup import lookup_phone; result=lookup_phone(args.target)
    elif args.command=="email":
        from modules.email_osint import analyze_email; result=analyze_email(args.target,reputation=not args.no_reputation,timeout=args.timeout)
    elif args.command=="username":
        from modules.username_search import search_username; result=search_username(args.target,timeout=args.timeout,workers=args.workers)
    elif args.command=="subdomain":
        from modules.subdomain_finder import find_subdomains; result=find_subdomains(args.target,active_dns=args.active_dns,timeout=args.timeout,workers=args.workers)
    else: parser.print_help(); return 2
    return _render_result(result,as_json=args.as_json,output=args.output)
if __name__=="__main__": raise SystemExit(main())
