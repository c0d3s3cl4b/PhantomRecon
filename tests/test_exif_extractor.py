from pathlib import Path

from PIL import Image

from modules.exif_extractor import convert_gps_to_decimal, extract_exif


def test_convert_gps_to_decimal():
    assert convert_gps_to_decimal((41, 0, 0), "N") == 41.0
    assert convert_gps_to_decimal((29, 0, 0), "W") == -29.0


def test_extract_exif_reads_basic_image_metadata(tmp_path: Path):
    image_path = tmp_path / "sample.jpg"
    Image.new("RGB", (32, 16)).save(image_path)

    result = extract_exif(str(image_path))

    assert result.status == "success"
    assert result.data["file"] == "sample.jpg"
    assert result.data["width"] == 32
    assert result.data["height"] == 16
    assert result.data["format"] == "JPEG"


def test_extract_exif_reports_missing_file(tmp_path: Path):
    result = extract_exif(str(tmp_path / "missing.jpg"))
    assert result.status == "error"
    assert "File not found" in result.errors[0]
