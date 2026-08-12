"""Local image metadata extraction engine."""
from __future__ import annotations
from pathlib import Path
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from core.banner import get_input, print_error, print_info, show_module_banner
from core.result import ScanResult
from core.utils import ask_save_report, display_results_table, pause
SUPPORTED={".jpg",".jpeg",".png",".tiff",".tif",".bmp",".gif",".webp"}
def _json_value(value):
    if isinstance(value,bytes):return value.decode("utf-8",errors="replace")
    if isinstance(value,(str,int,float,bool)) or value is None:return value
    if isinstance(value,(list,tuple)):return [_json_value(v) for v in value]
    if isinstance(value,dict):return {str(k):_json_value(v) for k,v in value.items()}
    try:return float(value)
    except (TypeError,ValueError):return str(value)
def convert_gps_to_decimal(coords,ref)->float|None:
    try:
        d,m,s=(float(v) for v in coords); value=d+m/60+s/3600
        if str(ref).upper() in {"S","W"}:value=-value
        return round(value,6)
    except (TypeError,ValueError,IndexError):return None
def extract_exif(path:str)->ScanResult:
    file=Path(path.strip("\"'"))
    if not file.is_file():return ScanResult.failure("exif_extractor",str(file),"File not found")
    if file.suffix.lower() not in SUPPORTED:return ScanResult.failure("exif_extractor",str(file),"Unsupported image format")
    try:
        with Image.open(file) as image:
            raw=image.getexif(); metadata={}
            for tag_id,value in raw.items():
                tag=TAGS.get(tag_id,str(tag_id))
                if tag=="GPSInfo" and isinstance(value,dict):metadata[tag]={str(GPSTAGS.get(k,k)):_json_value(v) for k,v in value.items()}
                else:metadata[str(tag)]=_json_value(value)
            data={"file":file.name,"path":str(file),"size_bytes":file.stat().st_size,"width":image.width,"height":image.height,"format":image.format,"mode":image.mode,"metadata":metadata}
            gps=metadata.get("GPSInfo",{})
            lat=convert_gps_to_decimal(gps.get("GPSLatitude"),gps.get("GPSLatitudeRef")) if isinstance(gps,dict) else None
            lon=convert_gps_to_decimal(gps.get("GPSLongitude"),gps.get("GPSLongitudeRef")) if isinstance(gps,dict) else None
            if lat is not None and lon is not None:data["gps"]={"latitude":lat,"longitude":lon}
            return ScanResult(module="exif_extractor",target=str(file),data=data)
    except (OSError,ValueError) as exc:return ScanResult.failure("exif_extractor",str(file),f"Could not read image: {exc}")
def run()->None:
    show_module_banner("EXIF Extractor","📸");print_info("Enter a local image path");target=get_input("Image Path")
    if not target:print_error("No file path entered.");pause();return
    result=extract_exif(target)
    if result.status!="success":print_error(result.errors[0]);pause();return
    data=result.data; display={"File":data["file"],"File Size":f"{data['size_bytes']/1024:.1f} KB","Dimensions":f"{data['width']}x{data['height']}","Format":data["format"],"Color Mode":data["mode"],"EXIF Fields":len(data["metadata"]),"GPS":"Present" if "gps" in data else "Not found"}
    display_results_table("📸 EXIF Metadata",display);ask_save_report(display,"exif_extractor",data["file"]);pause()
