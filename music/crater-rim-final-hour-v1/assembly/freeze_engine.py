"""Freeze byte-exact Colony v3 and its small runtime dependency closure locally."""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import shutil
import sys

H = Path(__file__).resolve().parent
R = H.parents[2]
SOURCE = R / "creative/brand/intro-v3/tool-source-snapshot"
APP = Path("C:/dev/SpeedySlideShow")
DEST = H / "engine"


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    evidence = json.loads((R / "creative/brand/intro-v3/implementation-verification.json").read_text(encoding="utf-8"))
    expected = {Path(item["path"]).relative_to(APP).as_posix(): item["sha256"] for item in evidence["files"]}
    snapshot_files = ["colony/intro.py", "colony/render.py", "colony/assets/fonts/BarlowCondensed-Regular.ttf",
                      "colony/assets/fonts/BarlowCondensed-SemiBold.ttf", "colony/assets/fonts/OFL.txt"]
    installed_files = ["colony/sfx.py", "app/__init__.py", "app/exporter.py", "app/trims.py", "app/utils.py"]
    rows = []
    for relative in snapshot_files + installed_files:
        source = (SOURCE if relative in snapshot_files else APP) / relative
        actual = digest(source)
        if relative in snapshot_files:
            assert actual == expected[relative], source
        target = DEST / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert digest(target) == actual, "Refusing to overwrite changed frozen engine"
        else:
            shutil.copy2(source, target)
        rows.append({"path": "engine/" + relative, "source": str(source), "bytes": target.stat().st_size,
                     "sha256": actual, "source_kind": "verified_intro_v3" if relative in snapshot_files else "installed_runtime_dependency"})
    # The original colony directory is a namespace package. An empty local marker
    # prevents another installed Colony package from taking precedence on another PC.
    marker = DEST / "colony/__init__.py"
    marker_bytes = b'"""Frozen Colony package namespace for this production job."""\n'
    if marker.exists():
        assert marker.read_bytes() == marker_bytes
    else:
        marker.write_bytes(marker_bytes)
    rows.append({"path": marker.relative_to(H).as_posix(), "source_kind": "local_package_marker",
                 "bytes": len(marker_bytes), "sha256": digest(marker)})
    packages = {name: importlib.metadata.version(name) for name in ("numpy", "Pillow")}
    try:
        packages["imageio-ffmpeg"] = importlib.metadata.version("imageio-ffmpeg")
    except importlib.metadata.PackageNotFoundError:
        pass  # Colony's original exporter falls back to FFmpeg on PATH.
    manifest = {"purpose": "Portable byte-exact actual Colony v3 engine and runtime closure",
                "intro_version": 3, "python": sys.version, "packages": packages,
                "ffmpeg_discovery": "FFmpeg and FFprobe on PATH; optional imageio-ffmpeg is not required",
                "installed_application_modified": False, "files": rows}
    (H / "engine-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (H / "requirements.txt").write_text("\n".join(f"{name}=={version}" for name, version in packages.items()) + "\n", encoding="utf-8")
    print(json.dumps({"status": "frozen", "files": len(rows), "packages": packages}), flush=True)


if __name__ == "__main__":
    main()
