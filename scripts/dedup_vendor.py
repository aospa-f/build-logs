import re
import os
import sys

qcom_dir = '/serverhive5/raizenftw/aospa/vendor/qcom/common'

def get_modules(text):
    return set(re.findall(r'name:\s*"([^"]+)"', text))

qcom_mods = set()
for root, _, files in os.walk(qcom_dir):
    for f in files:
        if f.endswith('.bp'):
            with open(os.path.join(root, f)) as f_in:
                qcom_mods.update(get_modules(f_in.read()))

def deduplicate_vendor_tree(bp_path, mk_path, tree_name):
    print(f"\n--- Deduplicating {tree_name} ---")
    if not os.path.exists(bp_path):
        print(f"File {bp_path} does not exist, skipping.")
        return

    with open(bp_path, 'r') as f:
        bp_content = f.read()

    common_mods = get_modules(bp_content)
    duplicates = sorted(common_mods.intersection(qcom_mods))
    print(f"Found {len(duplicates)} duplicate modules between {tree_name} and vendor/qcom/common.")

    symlink_mods = set()
    for mod in duplicates:
        for m in re.findall(rf'name:\s*"([^"]*{re.escape(mod)}[^"]*)"', bp_content):
            if m != mod:
                symlink_mods.add(m)
    print(f"Found {len(symlink_mods)} associated symlink modules.")

    all_to_remove = set(duplicates).union(symlink_mods)
    if not all_to_remove:
        print("Nothing to remove.")
        return

    lines = bp_content.splitlines(keepends=True)
    out_lines = []
    i = 0
    removed_count = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r'^(cc_[a-zA-Z0-9_]+|android_[a-zA-Z0-9_]+|install_symlink)\s*\{', line.strip())
        if m:
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

    with open(bp_path, 'w') as f:
        f.write("".join(out_lines))

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
            new_mk_lines.append(line)

        print(f"Removed {removed_mk_count} entries from {mk_path}")
        with open(mk_path, 'w') as f:
            f.writelines(new_mk_lines)

deduplicate_vendor_tree(
    '/serverhive5/raizenftw/aospa/vendor/oneplus/sm8650-common/Android.bp',
    '/serverhive5/raizenftw/aospa/vendor/oneplus/sm8650-common/sm8650-common-vendor.mk',
    'sm8650-common'
)

deduplicate_vendor_tree(
    '/serverhive5/raizenftw/aospa/vendor/oneplus/giulia/Android.bp',
    '/serverhive5/raizenftw/aospa/vendor/oneplus/giulia/giulia-vendor.mk',
    'giulia'
)

print("\nAll deduplications completed successfully!")

