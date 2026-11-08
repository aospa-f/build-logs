from pathlib import Path
import re
import shutil

BASE = Path("/serverhive5/raizenftw/aospa/vendor/google/gms")

def remove_module_block(path: Path, module_name: str):
    lines = path.read_text().splitlines(keepends=True)
    name_idx = next(
        i for i, line in enumerate(lines) if f'name: "{module_name}"' in line
    )
    start = None
    for i in range(name_idx, -1, -1):
        if lines[i].startswith("android_app_import {"):
            start = i
            break
    if start is None:
        raise SystemExit(f"module block not found: {module_name}")
    depth = 0
    end = None
    for i in range(start, len(lines)):
        depth += lines[i].count("{") - lines[i].count("}")
        if depth == 0:
            end = i
            break
    if end is None:
        raise SystemExit(f"module block end not found: {module_name}")
    path.write_text("".join(lines[:start] + lines[end + 1:]))
    print(f"removed {module_name} block")

bp = BASE / "Android.bp"
for module in ("Chrome64", "Photos", "TrichromeLibrary64"):
    remove_module_block(bp, module)

# gms-vendor.mk package entries
p = BASE / "gms-vendor.mk"
t = p.read_text()
for line in ("    Chrome64 \\\n", "    Photos \\\n", "    TrichromeLibrary64 \\\n"):
    if line not in t:
        raise SystemExit(f"gms-vendor entry not found: {line!r}")
    t = t.replace(line, "", 1)
p.write_text(t)
print("removed gms-vendor package entries")

# config.mk overlay entry
p = BASE / "config.mk"
t = p.read_text()
line = "    GmsConfigOverlayPhotos \\\n"
if line not in t:
    raise SystemExit("GmsConfigOverlayPhotos entry not found")
p.write_text(t.replace(line, "", 1))
print("removed GmsConfigOverlayPhotos entry")

# proprietary-files.txt
p = BASE / "proprietary-files.txt"
t = p.read_text()
for line in (
    "product/app/Chrome64/Chrome64.apk;OVERRIDES=Browser,Browser2;PRESIGNED\n",
    "product/app/Photos/Photos.apk;OVERRIDES=Gallery2,SnapdragonGallery;PRESIGNED\n",
    "product/app/TrichromeLibrary64/TrichromeLibrary64.apk;PRESIGNED\n",
):
    if line not in t:
        raise SystemExit(f"proprietary-files entry not found: {line!r}")
    t = t.replace(line, "", 1)
p.write_text(t)
print("removed proprietary-files entries")

# extract-files.py split-file entries
p = BASE / "extract-files.py"
t = p.read_text()
for line in (
    "        'product/app/Photos/Photos.apk',\n",
    "        'product/app/TrichromeLibrary64/TrichromeLibrary64.apk',\n",
):
    if line not in t:
        raise SystemExit(f"extract-files entry not found: {line!r}")
    t = t.replace(line, "", 1)
p.write_text(t)
print("removed extract-files entries")

# vendorsetup.sh lines and .gitignore lines
for filename, needles in (
    ("vendorsetup.sh", ("Photos.apk", "TrichromeLibrary64.apk")),
    (".gitignore", ("Photos.apk", "TrichromeLibrary64.apk")),
):
    p = BASE / filename
    lines = p.read_text().splitlines(keepends=True)
    kept = [line for line in lines if not any(n in line for n in needles)]
    if len(kept) == len(lines):
        raise SystemExit(f"no matching lines in {filename}")
    p.write_text("".join(kept))
    print(f"removed {filename} lines")

# blobs and overlay
for path in (
    BASE / "proprietary/product/app/Chrome64",
    BASE / "proprietary/product/app/Photos",
    BASE / "proprietary/product/app/TrichromeLibrary64",
    BASE / "overlay/GmsConfigOverlayPhotos",
):
    if path.exists():
        shutil.rmtree(path)
        print("removed", path)
