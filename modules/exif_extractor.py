"""
PhantomRecon - EXIF Extractor Module
Extracts metadata from images including GPS coordinates.
"""

import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from core.banner import show_module_banner, print_success, print_error, print_info, print_warning, get_input, console
from core.utils import display_results_table, ask_save_report, pause


def get_exif_data(image_path: str) -> dict:
    """Extract EXIF data from an image file."""
    exif_data = {}
    try:
        image = Image.open(image_path)
        info = image._getexif()

        if info:
            for tag_id, value in info.items():
                tag = TAGS.get(tag_id, tag_id)

                if tag == "GPSInfo":
                    gps_data = {}
                    for gps_tag_id, gps_value in value.items():
                        gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                        gps_data[gps_tag] = gps_value
                    exif_data[tag] = gps_data
                else:
                    # Handle bytes
                    if isinstance(value, bytes):
                        try:
                            value = value.decode("utf-8", errors="ignore")
                        except (UnicodeDecodeError, AttributeError):
                            value = str(value)
                    exif_data[tag] = value

        # Add basic image info
        exif_data["_ImageSize"] = f"{image.width}x{image.height}"
        exif_data["_ImageFormat"] = image.format or "Unknown"
        exif_data["_ImageMode"] = image.mode

    except Exception as e:
        exif_data["Error"] = str(e)

    return exif_data


def convert_gps_to_decimal(gps_coords, gps_ref) -> float:
    """Convert GPS coordinates from DMS to decimal degrees."""
    try:
        degrees = float(gps_coords[0])
        minutes = float(gps_coords[1])
        seconds = float(gps_coords[2])

        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)

        if gps_ref in ["S", "W"]:
            decimal = -decimal

        return round(decimal, 6)
    except (IndexError, TypeError, ValueError):
        return 0.0


def run():
    """Run the EXIF extractor module."""
    show_module_banner("EXIF Extractor", "📸")

    print_info("Enter the image file path (e.g., C:\\photo.jpg)")
    target = get_input("Image Path")

    if not target:
        print_error("No file path entered.")
        pause()
        return

    # Clean quotes
    target = target.strip("\"'")

    if not os.path.isfile(target):
        print_error(f"File not found: {target}")
        pause()
        return

    # Check file extension
    valid_extensions = [".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".gif", ".webp"]
    file_ext = os.path.splitext(target)[1].lower()
    if file_ext not in valid_extensions:
        print_warning(f"Supported formats: {', '.join(valid_extensions)}")
        print_error("Unsupported file format!")
        pause()
        return

    try:
        print_info("Extracting EXIF metadata...")

        exif_data = get_exif_data(target)

        if not exif_data or "Error" in exif_data:
            print_error(f"Failed to read EXIF: {exif_data.get('Error', 'Unknown error')}")
            pause()
            return

        # Format results
        results = {
            "File": os.path.basename(target),
            "File Size": f"{os.path.getsize(target) / 1024:.1f} KB",
            "Dimensions": exif_data.get("_ImageSize", "N/A"),
            "Format": exif_data.get("_ImageFormat", "N/A"),
            "Color Mode": exif_data.get("_ImageMode", "N/A"),
        }

        # Camera info
        if "Make" in exif_data:
            results["Camera Make"] = str(exif_data["Make"]).strip()
        if "Model" in exif_data:
            results["Camera Model"] = str(exif_data["Model"]).strip()
        if "Software" in exif_data:
            results["Software"] = str(exif_data["Software"])
        if "DateTime" in exif_data:
            results["Date Taken"] = str(exif_data["DateTime"])
        if "DateTimeOriginal" in exif_data:
            results["Original Date"] = str(exif_data["DateTimeOriginal"])

        # Camera settings
        if "FocalLength" in exif_data:
            fl = exif_data["FocalLength"]
            results["Focal Length"] = f"{float(fl):.1f}mm" if fl else "N/A"
        if "ExposureTime" in exif_data:
            et = exif_data["ExposureTime"]
            results["Exposure Time"] = f"1/{int(1/float(et))}s" if et and float(et) > 0 else str(et)
        if "FNumber" in exif_data:
            fn = exif_data["FNumber"]
            results["Aperture"] = f"f/{float(fn):.1f}" if fn else "N/A"
        if "ISOSpeedRatings" in exif_data:
            results["ISO"] = str(exif_data["ISOSpeedRatings"])

        # GPS info
        gps_info = exif_data.get("GPSInfo", {})
        if gps_info:
            lat = gps_info.get("GPSLatitude")
            lat_ref = gps_info.get("GPSLatitudeRef")
            lon = gps_info.get("GPSLongitude")
            lon_ref = gps_info.get("GPSLongitudeRef")

            if lat and lon:
                lat_decimal = convert_gps_to_decimal(lat, lat_ref)
                lon_decimal = convert_gps_to_decimal(lon, lon_ref)

                results["📍 GPS Latitude"] = f"{lat_decimal}° {lat_ref or ''}"
                results["📍 GPS Longitude"] = f"{lon_decimal}° {lon_ref or ''}"
                results["📍 Coordinates"] = f"{lat_decimal}, {lon_decimal}"

                map_url = f"https://www.google.com/maps?q={lat_decimal},{lon_decimal}"
                results["📍 Map Link"] = map_url

            if "GPSAltitude" in gps_info:
                results["📍 Altitude"] = f"{float(gps_info['GPSAltitude']):.1f}m"
        else:
            results["📍 GPS Data"] = "❌ Not found"

        print_success("EXIF metadata extraction complete!")
        display_results_table("📸 EXIF Metadata", results)

        # Show GPS map link separately
        if gps_info and "GPSLatitude" in gps_info:
            lat_decimal = convert_gps_to_decimal(gps_info["GPSLatitude"], gps_info.get("GPSLatitudeRef"))
            lon_decimal = convert_gps_to_decimal(gps_info["GPSLongitude"], gps_info.get("GPSLongitudeRef"))
            map_url = f"https://www.google.com/maps?q={lat_decimal},{lon_decimal}"
            console.print(f"\n  [cyan]🗺  Google Maps:[/cyan] [link={map_url}]{map_url}[/link]")

        ask_save_report(results, "exif_extractor", os.path.basename(target))

    except Exception as e:
        print_error(f"Hata oluştu: {e}")

    pause()
