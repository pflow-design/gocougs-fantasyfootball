#!/usr/bin/env python3
"""
fix_report.py
  1. Rename manager "Ryan" → "Rudee" throughout kdp_report.html
     (careful not to touch "Ryan C" / "RyanC")
  2. Add missing managers (Larson, Kyle2, Bradley) to the H2H dropdowns
     and MANAGERS JS object.
"""
import pathlib, re

HTML = pathlib.Path(__file__).parent / 'kdp_report.html'
src = HTML.read_text(encoding='utf-8')

# ── 1.  RENAME "Ryan" → "Rudee" ──────────────────────────────────────────────
# Strategy: replace the exact JS string 'Ryan' and display-text "Ryan"
# making sure we never touch 'RyanC' or "Ryan C".

replacements = [
    # JS object keys / winner strings in h2hData and MANAGERS
    ("'Ryan':",        "'Rudee':"),
    ("'Ryan'}",        "'Rudee'}"),     # winner:'Ryan'}
    ("winner:'Ryan'",  "winner:'Rudee'"),
    # Option value attributes
    ('value="Ryan"',   'value="Rudee"'),
    # MANAGERS label
    ("label: 'Ryan',",     "label: 'Rudee',"),
    # var teams array entry
    ("'Ryan',",        "'Rudee',"),
    ("'Ryan']",        "'Rudee']"),     # in case it's the last element
    # Inner h2hData references where Ryan appears as an inner key
    ("'Ryan': {w1",    "'Rudee': {w1"),
    # Display text in HTML (span, td, div) – use careful patterns
    (">Ryan<",         ">Rudee<"),
    (">Ryan\n",        ">Rudee\n"),
    # Narrative text
    ("Ryan's KDP debut",        "Rudee's KDP debut"),
    ("Ryan (Since '19)",         "Rudee (Since '19)"),
    ("Ryan (Since '11)",         "Rudee (Since '11)"),
    # Table/record cells  e.g.  <td class="rh">Ryan</td>
    ("<td class=\"rh\">Ryan</td>",      '<td class="rh">Rudee</td>'),
    ("<td class=\"rh\">Ryan vs.",       '<td class="rh">Rudee vs.'),
    # Veterans section
    ('"vet-nm">Ryan<',          '"vet-nm">Rudee<'),
    # Standings table strong tag
    ("><strong>Ryan</strong><",  "><strong>Rudee</strong><"),
]

out = src
for (old, new) in replacements:
    out = out.replace(old, new)

# Safety check: 'Ryan' (without C) should now only appear in Ryan C contexts
remaining = [(m.start(), out[max(0,m.start()-20):m.start()+25])
             for m in re.finditer(r"\bRyan\b", out)
             if 'Ryan C' not in out[max(0,m.start()-5):m.start()+10]]
if remaining:
    print("WARNING — stray 'Ryan' occurrences (not 'Ryan C'):")
    for pos, ctx in remaining:
        print(f"  pos {pos}: ...{ctx!r}...")
else:
    print("✓ All 'Ryan' (non-Ryan-C) references renamed to 'Rudee'")


# ── 2.  ADD MISSING MANAGERS TO DROPDOWNS & MANAGERS OBJECT ──────────────────
# Missing: Larson (Since '09), Kyle2 (Since '12), Bradley (Since '09, 2 seasons only)

new_options = """\
          <option value="Larson">Larson (Since '09)</option>
          <option value="Kyle2">Kyle2 (Since '12)</option>
          <option value="Bradley">Bradley (Since '09)</option>"""

# Insert after the last existing option in each select
# Both selects end with the Jeremy option — insert after it
jeremy_option = "          <option value=\"Jeremy\">Jeremy Trevino (Since '20)</option>"
out = out.replace(
    jeremy_option + "\n        </select>",
    jeremy_option + "\n" + new_options + "\n        </select>",
    2   # replace both occurrences (mgr1 and mgr2)
)

# Add to MANAGERS JS object (insert after Jeremy entry)
jeremy_mgr = "  'Jeremy':   { label: 'Jeremy Trevino', since: \"'20\" }"
new_mgrs = """\n  'Larson':   { label: 'Larson',         since: \"'09\" },
  'Kyle2':    { label: 'Kyle2',          since: \"'12\" },
  'Bradley':  { label: 'Bradley',        since: \"'09\" }"""

out = out.replace(
    jeremy_mgr + "\n};",
    jeremy_mgr + "," + new_mgrs + "\n};"
)

print("✓ Added Larson, Kyle2, Bradley to dropdowns and MANAGERS object")

# ── 3.  Write out ────────────────────────────────────────────────────────────
HTML.write_text(out, encoding='utf-8')
print("Done — kdp_report.html saved.")
