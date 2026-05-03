"""
Build a single master TSV from workout_knowledge_base.csv for paste into
the "마스터" tab in Google Sheets. All 14 columns preserved.

Companion derived tabs use QUERY() to filter by Y flags — no separate files needed.
"""
import csv, os, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(HERE)

SRC = 'workout_knowledge_base.csv'
OUT = 'output/sheet_마스터.tsv'
os.makedirs('output', exist_ok=True)

def safe(v: str) -> str:
    return (v or '').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

with open(SRC, encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    rows = list(reader)

header, data = rows[0], rows[1:]
data.sort(key=lambda r: r[0])

with open(OUT, 'w', encoding='utf-8', newline='') as f:
    f.write('\t'.join(safe(c) for c in header) + '\n')
    for r in data:
        f.write('\t'.join(safe(c) for c in r) + '\n')

print(f'Wrote {OUT}: {len(data)} rows + 1 header')
print(f'Columns ({len(header)}): {header}')
