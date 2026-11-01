#!/usr/bin/env python3
import os
import re
import sys

aosp_root = sys.argv[1] if len(sys.argv) > 1 else '/serverhive5/raizenftw/aospa'
qcom_root = os.path.join(aosp_root, 'vendor/qcom/common')
hw_qcom_root = os.path.join(aosp_root, 'hardware/qcom')

product_namespaces = set([
    'device/oneplus/giulia',
    'device/oneplus/sm8650-common',
    'hardware/oplus',
    'vendor/oneplus/sm8650-common',
    'vendor/oneplus/giulia',
    'vendor/google/gms',
    'vendor/qcom/common/vendor/adreno/u',
    'vendor/qcom/common/system/alarm',
    'vendor/qcom/common/vendor/alarm',
    'vendor/qcom/common/system/audio',
    'vendor/qcom/common/system/av',
    'vendor/qcom/common/system/bt',
    'vendor/qcom/common/system/display',
    'vendor/qcom/common/vendor/display',
    'vendor/qcom/common/system/gps',
    'vendor/qcom/common/system/perf',
    'vendor/qcom/common/vendor/perf',
    'vendor/qcom/common/system/telephony',
    'vendor/qcom/common/system/wfd',
    'vendor/qcom/common/vendor/wlan',
])

def get_namespace_for_dir(d):
    curr = d
    while curr and curr != aosp_root:
        bp = os.path.join(curr, 'Android.bp')
        if os.path.exists(bp):
            with open(bp) as f:
                if 'soong_namespace' in f.read():
                    return os.path.relpath(curr, aosp_root)
        curr = os.path.dirname(curr)
    return '.'

def get_modules_from_text(text):
    return set(re.findall(r'name:\s*"([^"]+)"', text))

# Collect active modules from vendor/qcom/common
active_qcom_modules = set()
for root, _, files in os.walk(qcom_root):
    for f in files:
        if f.endswith('.bp'):
            ns = get_namespace_for_dir(root)
            if ns in product_namespaces:
                with open(os.path.join(root, f)) as fin:
                    active_qcom_modules.update(get_modules_from_text(fin.read()))

# Also collect modules defined in hardware/qcom (GPS, Display, WLAN, etc.)
if os.path.exists(hw_qcom_root):
    for root, _, files in os.walk(hw_qcom_root):
        for f in files:
            full_f = os.path.join(root, f)
            if f.endswith('.bp'):
                with open(full_f) as fin:
                    active_qcom_modules.update(get_modules_from_text(fin.read()))
            elif f.endswith('.mk'):
                try:
                    with open(full_f) as fin:
                        for line in fin:
                            m = re.match(r'^\s*LOCAL_MODULE\s*:?=\s*([^\s]+)', line)
                            if m:
                                active_qcom_modules.add(m.group(1))
                except Exception:
                    pass

print(f"Collected {len(active_qcom_modules)} active modules from vendor/qcom/common and hardware/qcom.")

def deduplicate_vendor_tree(bp_path, mk_path, tree_name):
    print(f"\n--- Deduplicating {tree_name} ---")
    if not os.path.exists(bp_path):
        print(f"File {bp_path} does not exist, skipping.")
        return

    with open(bp_path, 'r') as f:
        bp_content = f.read()

    common_mods = get_modules_from_text(bp_content)
    duplicates = sorted(common_mods.intersection(active_qcom_modules))
    print(f"Found {len(duplicates)} duplicate modules between {tree_name} and active vendor/qcom/common.")

    symlink_mods = set()
    for mod in duplicates:
        for m in re.finditer(r'install_symlink\s*\{[^}]*name:\s*"([^"]+)"[^}]*(?:symlink_target|installed_location):\s*"[^"]*/' + re.escape(mod) + r'(?:\.so)?"', bp_content):
            symlink_mods.add(m.group(1))
    print(f"Found {len(symlink_mods)} associated symlink modules.")

    all_to_remove = set(duplicates).union(symlink_mods)
    protected = {
        "vendor.qti.hardware.limits@1.0",
        "vendor.qti.hardware.limits@1.1",
        "vendor.qti.hardware.fm@1.0",
        "vendor.qti.hardware.data.iwlandata-V1-ndk",
        "vendor.qti.hardware.data.dynamicddsaidlservice-V1-ndk",
        "vendor.qti.data.factoryservice-V1-ndk",
        "vendor.qti.ims.rcssipaidlservice-V1-ndk",
    }
    all_to_remove -= protected
    if tree_name == "giulia":
        all_to_remove.add("vendor.display.color@1.4")
        all_to_remove.add("vendor.display.color@1.5")

    # Detect prebuilt modules whose source files do not exist on disk
    base_dir = os.path.dirname(bp_path)
    missing_src_count = 0
    for m in re.finditer(r'([a-zA-Z0-9_]+)\s*\{', bp_content):
        mod_type = m.group(1)
        if mod_type == 'soong_namespace':
            continue
        start = m.end()
        count = 1
        idx = start
        while idx < len(bp_content) and count > 0:
            if bp_content[idx] == '{': count += 1
            elif bp_content[idx] == '}': count -= 1
            idx += 1
        block = bp_content[start:idx-1]
        name_m = re.search(r'name:\s*"([^"]+)"', block)
        if not name_m: continue
        mod_name = name_m.group(1)
        srcs_m = re.findall(r'(?:srcs|src|apk):\s*(?:\[\s*)?"([^"]+)"', block)
        for src in srcs_m:
            full_p = os.path.join(base_dir, src)
            if not os.path.exists(full_p):
                all_to_remove.add(mod_name)
                missing_src_count += 1
                break

    if missing_src_count > 0:
        print(f"Found {missing_src_count} modules with missing source files on disk.")

    if not all_to_remove:
        print("Nothing to remove.")
        return

    lines = bp_content.splitlines(keepends=True)
    out_lines = []
    i = 0
    removed_count = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^([a-zA-Z0-9_]+)\s*\{', line.strip())
        if m and m.group(1) != "soong_namespace":
            block_lines = [line]
            brace_count = line.count('{') - line.count('}')
            j = i + 1
            while j < len(lines) and brace_count > 0:
                block_lines.append(lines[j])
                brace_count += lines[j].count('{') - lines[j].count('}')
                j += 1
            block_text = "".join(block_lines)
            name_match = re.search(r'name:\s*"([^"]+)"', block_text)
            if name_match and name_match.group(1) in all_to_remove:
                removed_count += 1
                i = j
                if i < len(lines) and lines[i].strip() == "":
                    i += 1
                continue
            else:
                out_lines.extend(block_lines)
                i = j
                continue
        else:
            out_lines.append(line)
            i += 1
    print(f"Removed {removed_count} module blocks from {bp_path}")

    # Update soong_namespace to import active QCOM namespaces
    new_bp_text = "".join(out_lines)
    if tree_name == 'sm8650-common':
        ns_block = """soong_namespace {
    imports: [
        "device/oneplus/sm8650-common",
        "hardware/oplus",
        "vendor/qcom/common/vendor/adreno/u",
        "vendor/qcom/common/system/alarm",
        "vendor/qcom/common/vendor/alarm",
        "vendor/qcom/common/system/audio",
        "vendor/qcom/common/system/av",
        "vendor/qcom/common/system/bt",
        "vendor/qcom/common/system/display",
        "vendor/qcom/common/vendor/display",
        "vendor/qcom/common/system/gps",
        "vendor/qcom/common/system/perf",
        "vendor/qcom/common/vendor/perf",
        "vendor/qcom/common/system/telephony",
        "vendor/qcom/common/system/wfd",
        "vendor/qcom/common/vendor/wlan",
    ],
}"""
        new_bp_text = re.sub(r'soong_namespace\s*\{[^}]*\}', ns_block, new_bp_text, count=1)
    elif tree_name == 'giulia':
        ns_block = """soong_namespace {
    imports: [
        "device/oneplus/giulia",
        "hardware/oplus",
        "vendor/oneplus/sm8650-common",
        "vendor/qcom/common/vendor/adreno/u",
        "vendor/qcom/common/system/alarm",
        "vendor/qcom/common/vendor/alarm",
        "vendor/qcom/common/system/audio",
        "vendor/qcom/common/system/av",
        "vendor/qcom/common/system/bt",
        "vendor/qcom/common/system/display",
        "vendor/qcom/common/vendor/display",
        "vendor/qcom/common/system/gps",
        "vendor/qcom/common/system/perf",
        "vendor/qcom/common/vendor/perf",
        "vendor/qcom/common/system/telephony",
        "vendor/qcom/common/system/wfd",
        "vendor/qcom/common/vendor/wlan",
    ],
}"""
    if tree_name == 'sm8650-common':
        new_bp_text = new_bp_text.replace(
            '"CneApp.libvndfwk_detect_jni.qti_vendor_symlink"',
            '"CneApp.libvndfwk_detect_jni.qti_symlink"'
        )

    # Remove any shared_libs references to removed modules
    for mod in all_to_remove:
        new_bp_text = re.sub(r'^\s*"' + re.escape(mod) + r'",?\s*\n', '', new_bp_text, flags=re.MULTILINE)

    with open(bp_path, 'w') as f:
        f.write(new_bp_text)

    if os.path.exists(mk_path):
        with open(mk_path, 'r') as f:
            mk_lines = f.readlines()

        new_mk_lines = []
        removed_mk_count = 0
        for line in mk_lines:
            stripped = line.strip().rstrip('\\').strip()
            if stripped in all_to_remove:
                removed_mk_count += 1
                continue
            if ':' in stripped and not stripped.startswith('#'):
                src = stripped.split(':')[0].strip()
                if src.startswith('vendor/'):
                    full_p = os.path.join(aosp_root, src)
                    if not os.path.exists(full_p):
                        print(f"Pruning missing copy file from {tree_name}: {src}")
                        removed_mk_count += 1
                        continue
            new_mk_lines.append(line)

        print(f"Removed {removed_mk_count} entries from {mk_path}")
        with open(mk_path, 'w') as f:
            f.writelines(new_mk_lines)

# Reset sm8650-common to HEAD before deduplicating
os.system(f"git -C {aosp_root}/vendor/oneplus/sm8650-common checkout Android.bp sm8650-common-vendor.mk")

deduplicate_vendor_tree(
    os.path.join(aosp_root, 'vendor/oneplus/sm8650-common/Android.bp'),
    os.path.join(aosp_root, 'vendor/oneplus/sm8650-common/sm8650-common-vendor.mk'),
    'sm8650-common'
)

deduplicate_vendor_tree(
    os.path.join(aosp_root, 'vendor/oneplus/giulia/Android.bp'),
    os.path.join(aosp_root, 'vendor/oneplus/giulia/giulia-vendor.mk'),
    'giulia'
)

print("\nDeduplication completed cleanly and accurately!")
