#!/usr/bin/env python3
"""
rename_kyles.py
  Kyle  → Kyle K  (JS key: KyleK,  display: Kyle K)
  Kyle2 → Kyle P  (JS key: KyleP,  display: Kyle P)

Strategy: replace Kyle2/KyleP first, then standalone Kyle/KyleK.
"""
import pathlib, re

HTML = pathlib.Path(__file__).parent / 'kdp_report.html'
src = HTML.read_text(encoding='utf-8')

# ── PASS 1: Kyle2 → KyleP / "Kyle P" ────────────────────────────────────────
# Do this first so "Kyle" replacements don't clobber "Kyle2" occurrences.
p1 = [
    # JS object keys in h2hData and MANAGERS (quoted string keys)
    ("'Kyle2':",           "'KyleP':"),
    ("'Kyle2'}",           "'KyleP'}"),        # winner:'Kyle2'}
    ("winner:'Kyle2'",     "winner:'KyleP'"),
    # HTML option values (match the JS key)
    ('value="Kyle2"',      'value="KyleP"'),
    # MANAGERS label
    ("label: 'Kyle2'",     "label: 'Kyle P'"),
    # Display text in HTML elements
    (">Kyle2<",            ">Kyle P<"),
    # Dropdown display text
    ("Kyle2 (Since",       "Kyle P (Since"),
    # Strong tags in tables
    ("<strong>Kyle2</strong>", "<strong>Kyle P</strong>"),
    # Table cells
    ('"rh">Kyle2</td>',    '"rh">Kyle P</td>'),
    # Any remaining bare Kyle2 in attribute/text contexts
    ("Kyle2",              "Kyle P"),           # catch-all — must be last in pass 1
]

out = src
for old, new in p1:
    out = out.replace(old, new)

# ── PASS 2: Kyle → KyleK / "Kyle K" ─────────────────────────────────────────
# At this point "Kyle2" is gone, replaced by "Kyle P" or "KyleP".
p2 = [
    # JS object keys in h2hData and MANAGERS
    ("'Kyle':",            "'KyleK':"),
    ("'Kyle'}",            "'KyleK'}"),
    ("winner:'Kyle'",      "winner:'KyleK'"),
    # HTML option values
    ('value="Kyle"',       'value="KyleK"'),
    # MANAGERS label
    ("label: 'Kyle'",      "label: 'Kyle K'"),
    # PF/PA chart teams array entry (display name, not key)
    ("'Kyle'",             "'Kyle K'"),
    # Display text in HTML elements
    (">Kyle<",             ">Kyle K<"),
    # Dropdown display text
    ("Kyle (Since",        "Kyle K (Since"),
    # Strong tags
    ("<strong>Kyle</strong>", "<strong>Kyle K</strong>"),
    # Table cells (mgr cells etc.)
    ('"rh">Kyle</td>',     '"rh">Kyle K</td>'),
    # Veteran card name
    ('vet-nm">Kyle<',      'vet-nm">Kyle K<'),
    # Narrative prose
    (" Kyle ",             " Kyle K "),
    (" Kyle.",             " Kyle K."),
    (" Kyle,",             " Kyle K,"),
    (">Kyle ",             ">Kyle K "),
]

for old, new in p2:
    out = out.replace(old, new)

# ── Verification ─────────────────────────────────────────────────────────────
# Check for stray bare 'Kyle' not followed by K or P
stray = [(m.start(), out[max(0,m.start()-30):m.start()+40])
         for m in re.finditer(r"\bKyle\b", out)
         if not re.match(r"Kyle [KP]", out[m.start():])]
if stray:
    print(f"WARNING — {len(stray)} stray 'Kyle' occurrences found:")
    for pos, ctx in stray[:10]:
        print(f"  pos {pos}: ...{ctx!r}...")
else:
    print("✓ No stray bare 'Kyle' remaining")

kk = out.count('Kyle K')
kp = out.count('Kyle P')
kyk = out.count('KyleK')
kyp = out.count('KyleP')
print(f"  'Kyle K' occurrences  : {kk}")
print(f"  'Kyle P' occurrences  : {kp}")
print(f"  'KyleK'  (key) occurrences: {kyk}")
print(f"  'KyleP'  (key) occurrences: {kyp}")

HTML.write_text(out, encoding='utf-8')
print("Done — kdp_report.html saved.")
