from __future__ import annotations

from pathlib import Path
import binascii
import shutil
import struct
import tarfile
import tempfile
import zipfile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "integrations" / "chatgpt"
DIST = ROOT / "dist"
OUTPUT = DIST / "cricket-chatgpt-plugin.tar.gz"
PUBLIC_OUTPUT = DIST / "cricket-conscience-public.zip"

def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)

def _write_icon(path: Path) -> None:
    width = height = 256
    rows = []
    for y in range(height):
        row = bytearray([0])
        for x in range(width):
            # Dark field with a high-contrast C-shaped "conscience" mark and two antenna ticks.
            bg = (27, 67, 50, 255)
            dx, dy = x - 128, y - 128
            r2 = dx * dx + dy * dy
            ring = 52 * 52 <= r2 <= 83 * 83 and not (x > 137 and 82 < y < 174)
            antenna = (84 <= x <= 94 and 44 <= y <= 71 and abs((x - 89) - (y - 57) // 3) <= 3) or (162 <= x <= 172 and 44 <= y <= 71 and abs((x - 167) + (y - 57) // 3) <= 3)
            if ring or antenna:
                rgba = (245, 240, 220, 255)
            else:
                rgba = bg
            row.extend(rgba)
        rows.append(bytes(row))
    raw = b"".join(rows)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
    png += _chunk(b"IDAT", zlib.compress(raw, 9))
    png += _chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(png)

def _stage(tmp: str) -> Path:
    stage = Path(tmp) / "plugin"
    shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns("README.md", "CUSTOM_INSTRUCTIONS.md"))
    _write_icon(stage / "assets" / "cricket-256.png")
    return stage

def build() -> Path:
    if not (SOURCE / "plugin.json").is_file():
        raise RuntimeError("ChatGPT plugin projection is missing plugin.json")
    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stage = _stage(tmp)
        with tarfile.open(OUTPUT, "w:gz") as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.add(path, arcname=path.relative_to(stage))
    return OUTPUT

def build_public_zip() -> Path:
    if not (SOURCE / "plugin.json").is_file():
        raise RuntimeError("ChatGPT plugin projection is missing plugin.json")
    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stage = _stage(tmp)
        with zipfile.ZipFile(PUBLIC_OUTPUT, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.write(path, arcname=path.relative_to(stage))
    return PUBLIC_OUTPUT

if __name__ == "__main__":
    print(build())
    print(build_public_zip())
