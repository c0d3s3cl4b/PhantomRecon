"""Command-line entry point for PhantomRecon V2."""
from __future__ import annotations
import argparse,importlib,json,platform,sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from core.result import ScanResult
VERSION="2.0.0a1";console=Console()
MODULES={"phone":"modules.phone_lookup","ip":"modules.ip_lookup","email":"modules.email_osint","username":"modules.username_search","whois":"modules.whois_lookup","subdomain":"modules.subdomain_finder","ports":"modules.port_scanner","exif":"modules.exif_extractor"}
DEPENDENCIES={"rich":"Rich terminal UI","requests":"HTTP client","phonenumbers":"Phone OSINT","whois":"WHOIS lookup","dns":"DNS resolution","PIL":"Image metadata"}
def _out(p):p.add_argument("--json",action="store_true",dest="as_json");p.add_argument("--output",type=Path)
def build_parser():
 p=argparse.ArgumentParser(prog="phantomrecon",description="PhantomRecon V2 - OSINT and authorized reconnaissance framework");p.add_argument("--version",action="version",version=f"PhantomRecon {VERSION}");s=p.add_subparsers(dest="command");s.add_parser("menu");s.add_parser("doctor");m=s.add_parser("module");m.add_argument("name",choices=sorted(MODULES))
 for name,help_text in [("whois","Query WHOIS"),("phone","Analyze phone")]:q=s.add_parser(name,help=help_text);q.add_argument("target");_out(q)
 q=s.add_parser("ip");q.add_argument("target");q.add_argument("--timeout",type=float,default=10.0);_out(q)
 q=s.add_parser("email");q.add_argument("target");q.add_argument("--timeout",type=float,default=10.0);q.add_argument("--no-reputation",action="store_true");_out(q)
 q=s.add_parser("username");q.add_argument("target");q.add_argument("--timeout",type=float,default=8.0);q.add_argument("--workers",type=int,default=10);_out(q)
 q=s.add_parser("subdomain");q.add_argument("target");q.add_argument("--active-dns",action="store_true");q.add_argument("--timeout",type=float,default=15.0);q.add_argument("--workers",type=int,default=10);_out(q)
 q=s.add_parser("ports",help="Bounded TCP scan for explicitly authorized targets");q.add_argument("target");q.add_argument("--ports",dest="port_spec",help="Comma/range list; max 1024 ports");q.add_argument("--timeout",type=float,default=.75);q.add_argument("--workers",type=int,default=32);_out(q)
 q=s.add_parser("exif",help="Extract metadata from a local image");q.add_argument("target");_out(q);return p
def run_doctor():
 t=Table(title="PhantomRecon V2 Doctor");t.add_column("Component");t.add_column("Status");t.add_column("Details");ok=sys.version_info>=(3,10);t.add_row("Python","OK" if ok else "FAIL",platform.python_version())
 for n,d in DEPENDENCIES.items():
  try:importlib.import_module(n);st="OK"
  except ImportError:st="MISSING";ok=False
  t.add_row(n,st,d)
 console.print(t);return 0 if ok else 1
def _render(r:ScanResult,a,o):
 text=json.dumps(r.to_dict(),indent=2,ensure_ascii=False)
 if o:o.parent.mkdir(parents=True,exist_ok=True);o.write_text(text+"\n",encoding="utf-8")
 if a or not o:print(text)
 return 0 if r.status=="success" else 1
def main():
 p=build_parser();a=p.parse_args()
 if a.command in (None,"menu"):
  from phantomrecon import main as im;im();return 0
 if a.command=="doctor":return run_doctor()
 if a.command=="module":importlib.import_module(MODULES[a.name]).run();return 0
 if a.command=="ip":
  from modules.ip_lookup import lookup_ip;r=lookup_ip(a.target,timeout=a.timeout)
 elif a.command=="whois":
  from modules.whois_lookup import lookup_whois;r=lookup_whois(a.target)
 elif a.command=="phone":
  from modules.phone_lookup import lookup_phone;r=lookup_phone(a.target)
 elif a.command=="email":
  from modules.email_osint import analyze_email;r=analyze_email(a.target,reputation=not a.no_reputation,timeout=a.timeout)
 elif a.command=="username":
  from modules.username_search import search_username;r=search_username(a.target,timeout=a.timeout,workers=a.workers)
 elif a.command=="subdomain":
  from modules.subdomain_finder import find_subdomains;r=find_subdomains(a.target,active_dns=a.active_dns,timeout=a.timeout,workers=a.workers)
 elif a.command=="ports":
  from modules.port_scanner import parse_ports,scan_ports
  try:ports=parse_ports(a.port_spec)
  except ValueError as e:console.print(f"[red]Error:[/red] {e}");return 2
  r=scan_ports(a.target,ports,timeout=a.timeout,workers=a.workers)
 elif a.command=="exif":
  from modules.exif_extractor import extract_exif;r=extract_exif(a.target)
 else:p.print_help();return 2
 return _render(r,a.as_json,a.output)
if __name__=="__main__":raise SystemExit(main())
