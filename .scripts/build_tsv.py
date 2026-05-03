"""
Build 3 TSVs for paste into Google Sheets template.
Target columns: A (빈칸) | B (내용) | C (출처) | D (자료 위치)
Paste anchor: user clicks A3 (or A<next-empty-row>) and pastes.

Uses .scripts/rewrites.json for plain-language rewrites of 분류/항목/핵심/적용시점.
"""
import csv, json, os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).resolve().parents[1])

with open('.scripts/rewrites.json', encoding='utf-8') as _f:
    REWRITES = json.load(_f)

OUT_DIR = 'output'
os.makedirs(OUT_DIR, exist_ok=True)

TABS = {
    '운동 루틴 세션':   'goal1_session_recommendation.csv',
    '실시간 코칭':      'goal2_realtime_coaching.csv',
    '운동 지식베이스':   'goal3_knowledge_base.csv',
}

def load(p):
    with open(p, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

def build_content(r: dict) -> str:
    """Plain-language rewrite (조합 1).

    Format: [분류_평이 / 항목_평이] — 핵심_평이 (적용: 적용_평이)
    Falls back to original CSV fields if a row's ID is missing from rewrites.json.
    """
    rid = r['ID']
    rw = REWRITES.get(rid, {})

    cat = rw.get('분류_평이') or r['분류']
    item = rw.get('항목_평이') or r['항목']
    body = rw.get('핵심_평이') or r.get('핵심 룰 (한 줄)', '').strip()
    timing = rw.get('적용_평이') or r.get('적용 시점', '').strip()

    head = f"[{cat} / {item}]"
    line = f"{head} — {body}" if body else head
    if timing:
        line += f" (적용: {timing})"

    return line.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

def safe_cell(v: str) -> str:
    """Sanitize a cell for TSV paste (no tabs, no newlines)."""
    return (v or '').replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')

def write_tsv(tab_name: str, rows: list[dict]):
    # Sort by ID to keep deterministic order
    rows = sorted(rows, key=lambda r: r['ID'])
    out_path = os.path.join(OUT_DIR, f"sheet_{tab_name}.tsv")
    with open(out_path, 'w', encoding='utf-8', newline='') as f:
        for r in rows:
            cells = [
                '',                              # A: blank
                safe_cell(build_content(r)),     # B: 내용
                safe_cell(r.get('출처', '')),     # C: 출처
                safe_cell(r.get('URL', '')),     # D: 자료 위치
            ]
            f.write('\t'.join(cells) + '\n')
    return out_path, len(rows)

print('Building TSVs...\n')
results = []
for tab, src in TABS.items():
    rows = load(src)
    path, n = write_tsv(tab, rows)
    results.append((tab, src, path, n))
    print(f'  {tab}: {src} ({n} rows) -> {path}')

# Preview: 1st row of each
print('\n=== PREVIEW (first row, each tab) ===')
for tab, src, path, n in results:
    rows = sorted(load(src), key=lambda r: r['ID'])
    r = rows[0]
    content = build_content(r)
    print(f'\n[{tab}]')
    print(f'  A (빈) | B (내용) | C (출처) | D (자료위치)')
    print(f'  내용: {content}')
    print(f'  출처: {r.get("출처","")}')
    print(f'  URL : {r.get("URL","")}')
