#!/usr/bin/env python3
"""Check that b2b/data.js has the shape the dashboard expects.

Run it after every change to data.js (Claude runs it automatically):

    python3 scripts/check_data.py            # checks b2b/data.js
    python3 scripts/check_data.py path.js    # checks another file

Prints OK and exits 0, or lists each problem and exits 1.
"""
import re
import sys
from datetime import date
from pathlib import Path

REQUIRED = ['MQL_INBOUND', 'MQL_OUTBOUND', 'DAILY', 'DEALS', 'PEOPLE', 'MB',
            'RAG', 'TARGETS', 'MONTHS', 'MONTH_NOTES', 'P', 'EVENTS', 'ATTRIB_MQL',
            'ATTRIB_CUST', 'CAMPAIGNS', 'VERIFIED', 'CARDS']
DAILY_SERIES = ['mql', 'meet', 'sql', 'sqlex', 'pipe', 'dealn']
TARGET_KEYS = ['mqlPerMonth', 'meetPerMonth', 'sqlShareOfMQL', 'demoPerMonth', 'pipelinePerMonth']
PERIODS = ['weekly', 'monthly', 'quarterly', 'h1', 'h2', 'annual']
CARD_KEYS = {'mql', 'demos', 'meetings', 'events', 'social', 'paid', 'search', 'content'}


def iso(s):
    y, m, d = map(int, s.split('-'))
    return date(y, m, d)


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / 'b2b' / 'data.js')
    js = path.read_text(encoding='utf8')
    problems = []

    for name in REQUIRED:
        if not re.search(r'^const ' + name + r'\s*=', js, re.M):
            problems.append(f'missing block: const {name} = ...')

    # comments must be closed, or the whole file silently fails to load
    if js.count('/*') != js.count('*/'):
        problems.append('a /* comment */ is not closed')

    m = re.search(r"const DAILY\s*=\s*\{start:'(\d{4}-\d\d-\d\d)',\s*end:'(\d{4}-\d\d-\d\d)'(.*?)\};", js, re.S)
    if m:
        start, end, body = iso(m.group(1)), iso(m.group(2)), m.group(3)
        days = (end - start).days + 1
        if days <= 0:
            problems.append(f'DAILY end ({end}) is before start ({start})')
        for key in DAILY_SERIES:
            a = re.search(r'\b' + key + r':\[([^\]]*)\]', body)
            if not a:
                problems.append(f'DAILY.{key} is missing')
                continue
            vals = [v for v in a.group(1).split(',') if v.strip()]
            if len(vals) != days:
                problems.append(f'DAILY.{key} has {len(vals)} values but {start} → {end} is {days} days')
            if any(not re.fullmatch(r'\s*\d+(\.\d+)?\s*', v) for v in vals):
                problems.append(f'DAILY.{key} contains something that is not a number')
        # deal dates and "became SQL" dates can't be in the future
        # (PEOPLE may hold future meeting dates: those are booked meetings, which is fine)
        deals = re.search(r'const DEALS\s*=\s*\[(.*?)\];', js, re.S)
        mb = re.search(r'const MB\s*=\s*\[(.*?)\];', js, re.S)
        found = (re.findall(r'\[\s*"[^"]*",\s*"[^"]*",\s*[\d.]+,\s*"(\d{4}-\d\d-\d\d)"\s*\]', deals.group(1)) if deals else []) + \
                (re.findall(r'"d":\s*"(\d{4}-\d\d-\d\d)"', mb.group(1)) if mb else [])
        for ds in found:
            try:
                if iso(ds) > end:
                    problems.append(f'deal / SQL date {ds} is after DAILY.end ({end})')
                    break
            except ValueError:
                problems.append(f'not a real date: {ds}')
                break
    elif 'const DAILY' in js:
        problems.append("DAILY must start with {start:'YYYY-MM-DD', end:'YYYY-MM-DD', ...}")

    months = re.search(r'const MONTHS\s*=\s*\[([^\]]*)\]', js)
    if months:
        n = len([x for x in months.group(1).split(',') if x.strip()])
        for name in ['MQL_INBOUND', 'MQL_OUTBOUND']:
            a = re.search(r'const ' + name + r'\s*=\s*\[([^\]]*)\]', js)
            if a and len([x for x in a.group(1).split(',') if x.strip()]) != n:
                problems.append(f'{name} should have one value per month in MONTHS ({n})')
        notes = re.search(r'const MONTH_NOTES\s*=\s*\[(.*?)\];', js, re.S)
        if notes and len(re.findall(r"^\s*'", notes.group(1), re.M)) != n:
            problems.append(f'MONTH_NOTES should have one line per month in MONTHS ({n})')

    t = re.search(r'const TARGETS\s*=\s*\{([^}]*)\}', js)
    if t:
        for k in TARGET_KEYS:
            if not re.search(r'\b' + k + r'\s*:', t.group(1)):
                problems.append(f'TARGETS.{k} is missing')

    p = re.search(r'const P\s*=\s*\{(.*?)\n\};', js, re.S)
    if p:
        for k in PERIODS:
            if not re.search(r'^\s*' + k + r'\s*:', p.group(1), re.M):
                problems.append(f'P.{k} (channel figures for that period) is missing')

    c = re.search(r'const CARDS\s*=\s*\{(.*?)\n\};', js, re.S)
    if c:
        keys = set(re.findall(r'^\s*(\w+)\s*:\s*\{', c.group(1), re.M))
        for k in sorted(keys - CARD_KEYS):
            problems.append(f'CARDS.{k} is not a card the page knows (use: {", ".join(sorted(CARD_KEYS))})')

    if problems:
        print(f'✗ {path} has {len(problems)} problem(s):')
        for x in problems:
            print('  -', x)
        sys.exit(1)
    print(f'✓ {path.name} looks good')


if __name__ == '__main__':
    main()
