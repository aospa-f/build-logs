from pathlib import Path

# --- device/oneplus/giulia/Android.bp ---
p = Path("/serverhive5/raizenftw/aospa/device/oneplus/giulia/Android.bp")
t = p.read_text()
old = "soong_namespace {\n}"
new = "soong_namespace {\n    imports: [\n        \"vendor/sony/dolby\",\n    ],\n}"
assert t.count(old) == 1, t.count(old)
t = t.replace(old, new, 1)
idx = t.find("// Ronard's 568080-byte")
assert idx != -1
t = t[:idx].rstrip() + "\n"
p.write_text(t)
print("patched giulia Android.bp")

# --- device/oneplus/giulia/device.mk ---
p = Path("/serverhive5/raizenftw/aospa/device/oneplus/giulia/device.mk")
t = p.read_text()
old = """# Dolby
PRODUCT_PACKAGES += \\
    android.hardware.media.c2@1.0.ronard \\
    android.hardware.media.c2@1.0_symlink

# Dolby Vision
"""
new = """# Dolby Vision
"""
assert t.count(old) == 1, t.count(old)
p.write_text(t.replace(old, new, 1))
print("patched giulia device.mk")

# --- vendor/sony/dolby/Android.bp: remove the prebuilt C2 service block ---
p = Path("/serverhive5/raizenftw/aospa/vendor/sony/dolby/Android.bp")
lines = p.read_text().splitlines(keepends=True)
name_idx = next(
    i for i, line in enumerate(lines)
    if 'name: "vendor.dolby.media.c2@1.0-service"' in line
)
start = None
for i in range(name_idx, -1, -1):
    if lines[i].startswith("cc_prebuilt_binary {"):
        start = i
        break
assert start is not None
depth = 0
end = None
for i in range(start, len(lines)):
    depth += lines[i].count("{") - lines[i].count("}")
    if depth == 0:
        end = i
        break
assert end is not None
comment = [
    "// vendor.dolby.media.c2@1.0-service is built from AOSPA source in\n",
    "// device/oneplus/giulia/dolby; it links the stock libcodec2_store_dolby.\n",
]
p.write_text("".join(lines[:start] + comment + lines[end + 1:]))
print("removed prebuilt Dolby C2 service")

# --- vendor/sony/dolby/proprietary-files.txt ---
p = Path("/serverhive5/raizenftw/aospa/vendor/sony/dolby/proprietary-files.txt")
t = p.read_text()
line = "vendor/bin/hw/vendor.dolby.media.c2@1.0-service\n"
assert t.count(line) == 1, t.count(line)
p.write_text(t.replace(line, "", 1))
print("removed stock service from proprietary-files.txt")

# --- delete stock service binary and CFI-free HIDL prebuilt ---
for f in [
    "/serverhive5/raizenftw/aospa/vendor/sony/dolby/proprietary/vendor/bin/hw/vendor.dolby.media.c2@1.0-service",
    "/serverhive5/raizenftw/aospa/device/oneplus/giulia/prebuilt/vendor/lib64/android.hardware.media.c2@1.0.so",
    "/serverhive5/raizenftw/aospa/device/oneplus/giulia/prebuilt/README.md",
]:
    q = Path(f)
    assert q.exists(), f
    q.unlink()
    print("deleted", f)
