#!/usr/bin/env python3
"""Rebuild the canon-list indexes embedded in index.html.

The app ticks films that appear on the 1001 Movies list (green) or in the
Sight & Sound 250 (red). Both lists live in index.html as normalised
title -> year indexes so matching happens at render time with no network
call and no per-film stored flags.

Run after editing either source list, or after adding an alias to EXTRA:

    python3 tools/build-canon-lists.py

It rewrites the two `const LIST_1001=` / `const LIST_SS=` lines in place and
prints what changed. Nothing else in index.html is touched.

Source files (same directory):
  1001-movies.txt        one film per line: "Title (Alt Title) (Year)"
  sight-and-sound-250.txt  "[=]Rank. Title (Year) - Director"
"""

import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, '..', 'index.html')

# Titles our sources spell differently from the Wikidata label the app stores.
# Add here when a film that should tick doesn't: 'our title' -> 'list title'.
EXTRA = {
    'ugetsu': 'Tales of Ugetsu',
}

# Must stay identical to listKey() in index.html.
ART = r'^(the|a|an|le|la|les|l|il|el|lo|los|las|un|une|una|der|die|das|ein|eine|o|os)\s+'
NUM = {'i': '1', 'ii': '2', 'iii': '3', 'iv': '4', 'v': '5',
       'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5'}


def key(s):
    t = unicodedata.normalize('NFKD', str(s or ''))
    t = ''.join(c for c in t if not unicodedata.combining(c))
    t = t.lower().replace('&', ' and ').replace("'", '')
    t = re.sub(r'[^a-z0-9]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(ART, '', t)
    return ' '.join(NUM.get(w, w) for w in t.split()).strip()


def parse_1001(path):
    """-> [{names: [main, alt...], year}]  (alt titles matter: 'Yi Yi' is
    listed as 'A One and a Two', and about a third of entries carry one)"""
    out = []
    for line in open(path, encoding='utf-8'):
        line = line.strip()
        m = re.search(r'\((\d{4})\)\s*$', line)
        if not m:
            continue
        head = line[:m.start()].strip()
        alts = re.findall(r'\(([^)]*)\)', head)
        main = re.sub(r'\s*\([^)]*\)', '', head).strip()
        out.append({'names': [main] + [a.strip() for a in alts if a.strip()],
                    'year': int(m.group(1))})
    return out


def parse_ss(path):
    """-> [{rank, title, year}]  (ties share a rank, so ranks repeat)"""
    out = []
    for line in open(path, encoding='utf-8'):
        m = re.match(r'^=?(\d+)\.\s+(.*?)\s+\((\d{4})\)\s*-\s*(.*)$', line.strip())
        if m:
            out.append({'rank': int(m.group(1)), 'title': m.group(2).strip(),
                        'year': int(m.group(3))})
    return out


def main():
    l1001 = parse_1001(os.path.join(HERE, '1001-movies.txt'))
    ss = parse_ss(os.path.join(HERE, 'sight-and-sound-250.txt'))
    if not l1001 or not ss:
        sys.exit('could not parse the source lists — check their format')

    i1 = {}
    for it in l1001:
        for n in it['names']:
            i1.setdefault(key(n), set()).add(it['year'])
    for alias, target in EXTRA.items():
        tk = key(target)
        if tk not in i1:
            sys.exit('EXTRA alias target not found in the 1001 list: %r' % target)
        i1.setdefault(key(alias), set()).update(i1[tk])

    i2 = {}
    for it in ss:
        i2.setdefault(key(it['title']), []).append([it['year'], it['rank']])

    o1 = {k: sorted(v) for k, v in sorted(i1.items()) if k}
    o2 = {k: v for k, v in sorted(i2.items()) if k}

    html = open(INDEX, encoding='utf-8').read()
    before = len(html)
    for name, obj in (('LIST_1001', o1), ('LIST_SS', o2)):
        line = 'const %s=%s;' % (name, json.dumps(obj, separators=(',', ':'), ensure_ascii=False))
        html, n = re.subn(r'const %s=.*?;\n' % name, lambda _m: line + '\n', html, count=1, flags=re.S)
        if n != 1:
            sys.exit('could not find the %s line in index.html' % name)
    open(INDEX, 'w', encoding='utf-8').write(html)

    print('1001: %d films -> %d keys (incl. alt titles and %d alias(es))'
          % (len(l1001), len(o1), len(EXTRA)))
    print('S&S : %d films -> %d keys' % (len(ss), len(o2)))
    print('index.html %d -> %d bytes' % (before, len(html)))


if __name__ == '__main__':
    main()
