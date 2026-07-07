#!/usr/bin/env python3
"""Update 3 dashboard HTML files with W9 data using regex (UTF-16 safe)."""
import re

W9_BLOCK = """\
    { id: 'w9', label: '29.06\u201305.07', short: '29.06\u201305.07',
      impressions: 98963, clicks: 1200, spend: 33075, leads: 35, target: 10,
      ctr: 1.21, cpc: 28, cpa: 945, cpl: 3308, convLead: 2.92, convTarget: 28.57,
      seo: 88, seoLeads: 8, seoTarget: 4,
      otherLeads: 16, otherTarget: 1,
      accounts: {
        'e-20010227': { imp: 53253, clicks: 425, spend: 28105, leads: 11, target: 5 },
        'e-17228851': { imp: 45340, clicks: 757, spend: 4971, leads: 0, target: 0 },
        'dune-group': { imp: 0, clicks: 0, spend: 0, leads: 0, target: 0 },
        'porg-3uieikjn': { imp: 370, clicks: 18, spend: 0, leads: 0, target: 0 }
      }
    }"""

W8_DROPDOWN = '''<option value="w7">15.06\u201321.06</option>'''
W8_W9_DROPDOWN = '''<option value="w7">15.06\u201321.06</option>
                <option value="w8">22.06\u201330.06</option>
                <option value="w9">29.06\u201305.07</option>'''

W8_MONTHS = "weeks: ['w5', 'w6', 'w7', 'w8'],"
W9_MONTHS = "weeks: ['w5', 'w6', 'w7', 'w8', 'w9'],"


def read_file(path):
    with open(path, 'rb') as f:
        raw = f.read()
    if raw[:2] == b'\xff\xfe':
        return raw[2:].decode('utf-16-le')
    return raw.decode('utf-8-sig')


def write_file(path, content):
    with open(path, 'wb') as f:
        f.write(b'\xff\xfe' + content.encode('utf-16-le'))


def update_file(path, full_w8_w9=False):
    """Update a single dashboard. If full_w8_w9=False, only update files that already have W8."""
    content = read_file(path)
    original_len = len(content)
    changes = []

    has_w8 = "id: 'w8'" in content

    # 1. Insert W9 data block after W8 closing (only if W8 exists)
    if has_w8 and "id: 'w9'" not in content:
        w8_close_pattern = r"(        'porg-3uieikjn': \{ imp: 440, clicks: 20, spend: 0, leads: 0, target: 0 \}\r?\n      \}\r?\n    \})"
        match = re.search(w8_close_pattern, content)
        if match:
            end = match.end(1)
            insertion = ",\r\n" + W9_BLOCK
            content = content[:end] + insertion + content[end:]
            changes.append('Added W9 data block')
        else:
            print(f"  WARNING: W8 close pattern not found in {path} despite W8 id present")
    elif "id: 'w9'" in content:
        changes.append('W9 data block already present')
    # else: W8 not in file, skipping data block entirely (older dashboard)

    # 2. Update dropdown options (ALWAYS - add or skip if already)
    if 'value="w9"' not in content:
        if W8_DROPDOWN in content:
            content = content.replace(W8_DROPDOWN, W8_W9_DROPDOWN, 1)
            changes.append('Added w8+w9 dropdown options')
        else:
            print(f"  WARNING: w7 dropdown option not found in {path}")
    else:
        changes.append('w9 dropdown already present')

    # 3. Update months array ONLY if W8 is in the months
    if 'w5\', \'w6\', \'w7\', \'w8\'' in content and "w9']" not in content:
        if W8_MONTHS in content:
            content = content.replace(W8_MONTHS, W9_MONTHS, 1)
            changes.append('Updated m2.weeks to include w9')
        else:
            print(f"  WARNING: w8 months pattern not found in {path}")
    elif "w9']" in content:
        changes.append('w9 months already present')

    write_file(path, content)
    print(f"{path}: {original_len} -> {len(content)} chars")
    for c in changes:
        print(f"  + {c}")


if __name__ == '__main__':
    for p in ['index.html', 'index2.html', 'index_ghpages.html']:
        try:
            update_file(p)
        except FileNotFoundError:
            print(f"  SKIP: {p} not found")
