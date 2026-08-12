"""Local image metadata extraction engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS

from core.banner import get_input, print_error, print_info, show_module_banner
from core.result import ScanResult
from core.utils import ask_save_report, display_results_table, pause

SUPPORTED = {
    ".bmp",
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".tif",
    ".tiff",
    ".webp",
}


def _json_value(value: Any) -> Any:
    """Convert Pillow EXIF values into JSON-friendly values."""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    try:
        return float(value)
    except (TypeError, ValueError):
        return str(value)


def convert_gps_to_decimal(coords: Any, ref: Any) -> float | None:
    """Convert EXIF DMS coordinates to decimal degrees."""
    try:
        degrees, minutes, seconds = (float(value) for value in coords)
        decimal = degrees + minutes / 60 + seconds / 3600
        if str(ref).upper() in {"S", "W"}:
            decimal = -decimal
        return round(decimal, 6)
    except (TypeError, ValueError, IndexError):
        return None


def extract_exif(path: str) -> ScanResult:
    """Extract structured metadata from a local image file."""
    file_path = Path(path.strip("\"'"))
    if not file_path.is_file():
        return ScanResult.failure(
            "exif_extractor",
            str(file_path),
            "File not found",
        )
    if file_path.suffix.lower() not in SUPPORTED:
        return ScanResult.failure(
            "exif_extractor",
            str(file_path),
            "Unsupported image format",
        )

    try:
        with Image.open(file_path) as image:
            metadata: dict[str, Any] = {}
            for tag_id, value in image.getexif().items():
                tag = TAGS.get(tag_id, str(tag_id))
                if tag == "GPSInfo" and isinstance(value, dict):
                    metadata[tag] = {
                        str(GPSTAGS.get(key, key)): _json_value(item)
                        for key, item in value.items()
                    }
                else:
                    metadata[str(tag)] = _json_value(value)

            data: dict[str, Any] = {
                "file": file_path.name,
                "path": str(file_path),
                "size_bytes": file_path.stat().st_size,
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "metadata": metadata,
            }

            gps = metadata.get("GPSInfo", {})
            if isinstance(gps, dict):
                latitude = convert_gps_to_decimal(
                    gps.get("GPSLatitude"),
                    gps.get("GPSLatitudeRef"),
                )
                longitude = convert_gps_to_decimal(
                    gps.get("GPSLongitude"),
                    gps.get("GPSLongitudeRef"),
                )
                if latitude is not None and longitude is not None:
                    data["gps"] = {
                        "latitude": latitude,
                        "longitude": longitude,
                    }

            return ScanResult(
                module="exif_extractor",
                target=str(file_path),
                data=data,
            )
    except (OSError, ValueError) as exc:
        return ScanResult.failure(
            "exif_extractor",
            str(file_path),
            f"Could not read image: {exc}",
        )


def run() -> None:
    """Run the classic interactive EXIF interface."""
    show_module_banner("EXIF Extractor", "📸")
    print_info("Enter a local image path")
    target = get_input("Image Path")
    if not target:
        print_error("No file path entered.")
        pause()
        return

    result = extract_exif(target)
    if result.status != "success":
        print_error(result.errors[0])
        pause()
        return

    data = result.data
    display = {
        "File": data["file"],
        "File Size": f"{data['size_bytes'] / 1024:.1f} KB",
        "Dimensions": f"{data['width']}x{data['height']}",
        "Format": data["format"],
        "Color Mode": data["mode"],
        "EXIF Fields": len(data["metadata"]),
        "GPS": "Present" if "gps" in data else "Not found",
    }

    display_results_table("📸 EXIF Metadata", display)
    ask_save_report(display, "exif_extractor", data["file"])
    pause()
