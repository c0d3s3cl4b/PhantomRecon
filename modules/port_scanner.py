"""Bounded TCP port scanner for explicitly authorized targets."""
from __future__ import annotations
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.banner import console, get_input, print_error, print_info, show_module_banner
from core.result import ScanResult
from core.utils import ask_save_report, pause, resolve_domain, validate_domain, validate_ip
COMMON_PORTS={21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",587:"SMTP-Submission",993:"IMAPS",995:"POP3S",3306:"MySQL",3389:"RDP",5432:"PostgreSQL",6379:"Redis",8080:"HTTP-Alt",8443:"HTTPS-Alt",9200:"Elasticsearch",27017:"MongoDB"}
TOP_PORTS=sorted(COMMON_PORTS)
def parse_ports(spec:str|None)->list[int]:
    if not spec:return TOP_PORTS.copy()
    ports:set[int]=set()
    for part in spec.split(","):
        part=part.strip()
        if "-" in part:
            start,end=(int(x) for x in part.split("-",1));
            if start>end:raise ValueError("Invalid port range")
            ports.update(range(start,end+1))
        else:ports.add(int(part))
    if not ports or min(ports)<1 or max(ports)>65535:raise ValueError("Ports must be between 1 and 65535")
    if len(ports)>1024:raise ValueError("A single scan is limited to 1024 ports")
    return sorted(ports)
def normalize_target(target:str)->tuple[str,str]:
    target=target.strip().lower()
    if validate_ip(target):return target,target
    if validate_domain(target):
        resolved=resolve_domain(target)
        if resolved:return resolved,target
    raise ValueError("Invalid or unresolvable target")
def scan_port(ip:str,port:int,timeout:float=.75)->dict[str,object]|None:
    try:
        with socket.create_connection((ip,port),timeout=timeout):
            return {"port":port,"state":"open","service":COMMON_PORTS.get(port,"unknown")}
    except (socket.timeout,ConnectionRefusedError,OSError):return None
def scan_ports(target:str,ports:list[int]|None=None,*,timeout:float=.75,workers:int=32)->ScanResult:
    try:ip,original=normalize_target(target)
    except ValueError as exc:return ScanResult.failure("port_scanner",target,str(exc))
    ports=ports or TOP_PORTS.copy()
    if len(ports)>1024:return ScanResult.failure("port_scanner",target,"A single scan is limited to 1024 ports")
    workers=max(1,min(workers,64)); opened=[]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures=[executor.submit(scan_port,ip,p,timeout) for p in ports]
        for future in as_completed(futures):
            item=future.result()
            if item:opened.append(item)
    opened.sort(key=lambda item:int(item["port"]))
    return ScanResult(module="port_scanner",target=original,data={"resolved_ip":ip,"ports_scanned":len(ports),"open_count":len(opened),"open_ports":opened,"timeout":timeout,"workers":workers})
def run()->None:
    show_module_banner("Port Scanner","🔓"); print_info("Use only on systems you own or are explicitly authorized to assess."); target=get_input("Target")
    if not target:print_error("No target entered.");pause();return
    spec=get_input("Ports (blank = common ports, e.g. 22,80,443)")
    try:ports=parse_ports(spec)
    except ValueError as exc:print_error(str(exc));pause();return
    result=scan_ports(target,ports)
    if result.status!="success":print_error(result.errors[0]);pause();return
    console.print(f"[green]Open ports:[/green] {result.data['open_count']} / {result.data['ports_scanned']}")
    for item in result.data["open_ports"]:console.print(f"  {item['port']}/tcp  {item['service']}")
    report={"Target":result.target,"Resolved IP":result.data["resolved_ip"],"Ports Scanned":result.data["ports_scanned"],"Open Ports":result.data["open_count"]}
    for item in result.data["open_ports"]:report[f"Port {item['port']}"]=item["service"]
    ask_save_report(report,"port_scanner",result.target);pause()
