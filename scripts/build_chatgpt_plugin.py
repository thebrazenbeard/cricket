from __future__ import annotations

from pathlib import Path
import shutil
import tarfile
import tempfile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "integrations" / "chatgpt"
DIST = ROOT / "dist"
OUTPUT = DIST / "cricket-chatgpt-plugin.tar.gz"


def build() -> Path:
    if not (SOURCE / "plugin.json").is_file():
        raise RuntimeError("ChatGPT plugin projection is missing plugin.json")

    DIST.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        stage = Path(tmp) / "plugin"
        shutil.copytree(
            SOURCE,
            stage,
            ignore=shutil.ignore_patterns("README.md", "CUSTOM_INSTRUCTIONS.md"),
        )
        with tarfile.open(OUTPUT, "w:gz") as archive:
            for path in sorted(stage.rglob("*")):
                if path.is_file():
                    archive.add(path, arcname=path.relative_to(stage))
    return OUTPUT


if __name__ == "__main__":
    print(build())
