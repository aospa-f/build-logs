from pathlib import Path
import difflib
import shutil

BASE = Path("/serverhive5/raizenftw/aospa/vendor/oneplus/giulia")
BACKUP = Path("/serverhive5/raizenftw/build-logs/backups/20261102-no-firmware")
PATCH = Path("/serverhive5/raizenftw/build-logs/patches/vendor_oneplus_giulia_no_firmware_ota.patch")

BACKUP.mkdir(parents=True, exist_ok=True)
PATCH.parent.mkdir(parents=True, exist_ok=True)

def backup(path):
    dst = BACKUP / path.name
    if not dst.exists():
        shutil.copy2(path, dst)
        print(f"backed up {path} -> {dst}")

def read(path):
    return path.read_text().splitlines(keepends=True)

def write(path, lines):
    path.write_text("".join(lines))

# --- BoardConfigVendor.mk: comment out the firmware AB_OTA_PARTITIONS block ---
bc = BASE / "BoardConfigVendor.mk"
backup(bc)
orig_bc = read(bc)
new_bc = []
i = 0
while i < len(orig_bc):
    line = orig_bc[i]
    if line.startswith("AB_OTA_PARTITIONS +="):
        new_bc.append(
            "# Firmware OTA packaging intentionally disabled: the phone already runs\n"
            "# OnePlus 13R India 16.0.10.600 firmware. Re-enable this block only when\n"
            "# building a firmware-inclusive ROM.\n"
        )
        while i < len(orig_bc):
            firmware_line = orig_bc[i]
            new_bc.append("# " + firmware_line if firmware_line.strip() else firmware_line)
            if "xbl_ramdump" in firmware_line:
                i += 1
                break
            i += 1
        continue
    new_bc.append(line)
    i += 1
write(bc, new_bc)

# --- Android.mk: comment out add-radio-file-sha1-checked firmware entries ---
am = BASE / "Android.mk"
backup(am)
orig_am = read(am)
new_am = []
for line in orig_am:
    if line.lstrip().startswith("$(call add-radio-file-sha1-checked,"):
        new_am.append("# " + line)
    else:
        new_am.append(line)
write(am, new_am)

# --- Generate a unified diff for the build-logs repo ---
diff = difflib.unified_diff(
    orig_bc,
    new_bc,
    fromfile="vendor/oneplus/giulia/BoardConfigVendor.mk",
    tofile="vendor/oneplus/giulia/BoardConfigVendor.mk",
)
diff2 = difflib.unified_diff(
    orig_am,
    new_am,
    fromfile="vendor/oneplus/giulia/Android.mk",
    tofile="vendor/oneplus/giulia/Android.mk",
)
PATCH.write_text("".join(diff) + "".join(diff2))
print(f"wrote patch {PATCH}")

print("BoardConfigVendor firmware lines left:", sum(
    1 for l in new_bc if l.startswith("AB_OTA_PARTITIONS") or (l.startswith("    ") and l.strip())
))
print("Android.mk active add-radio-file lines left:", sum(
    1 for l in new_am if l.lstrip().startswith("$(call add-radio-file-sha1-checked,")
))
