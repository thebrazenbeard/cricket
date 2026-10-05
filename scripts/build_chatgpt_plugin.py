from __future__ import annotations

from pathlib import Path
import shutil
import struct
import tarfile
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "integrations" / "chatgpt"
DIST = ROOT / "dist"
OUTPUT = DIST / "cricket-chatgpt-plugin.tar.gz"
PUBLIC_OUTPUT = DIST / "cricket-conscience-public.zip"
ICON = SOURCE / "assets" / "cricket-256.png"

def _validate_icon(path: Path) -> None:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise RuntimeError("Cricket plugin icon must be a PNG")
    if len(data) < 24:
        raise RuntimeError("Cricket plugin icon is truncated")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (256, 256):
        raise RuntimeError(f"Cricket plugin icon must be 256x256, got {width}x{height}")

def _stage(tmp: str) -> Path:
    if not ICON.is_file():
        raise RuntimeError("ChatGPT plugin projection is missing assets/cricket-256.png")
    _validate_icon(ICON)
    stage = Path(tmp) / "plugin"
    shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns("README.md", "CUSTOM_INSTRUCTIONS.md"))
    _validate_icon(stage / "assets" / "cricket-256.png")
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
