import csv, os, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(Path(__file__).resolve().parents[1])

files = {
    '운동 루틴 세션': 'goal1_session_recommendation.csv',
    '실시간 코칭':    'goal2_realtime_coaching.csv',
    '운동 지식베이스': 'goal3_knowledge_base.csv',
}
master = 'workout_knowledge_base.csv'

def load(p):
    with open(p, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

datasets = {k: load(p) for k, p in files.items()}
m = load(master)

print('row counts:', {k: len(v) for k, v in datasets.items()})
print('master rows:', len(m))
print('columns:', list(datasets['운동 루틴 세션'][0].keys()))

master_ids = {r['ID'] for r in m}
print()
print('Validation — filtered goal files vs master Y-flagged rows:')
for k, rows, col in [
    ('운동 루틴 세션',   datasets['운동 루틴 세션'],   '운동 추천'),
    ('실시간 코칭',     datasets['실시간 코칭'],     '실시간 코칭'),
    ('운동 지식베이스',  datasets['운동 지식베이스'],  '지식베이스'),
]:
    expected = {r['ID'] for r in m if r[col] == 'Y'}
    actual = {r['ID'] for r in rows}
    print(f"  {k}: expected={len(expected)} actual={len(actual)} match={expected==actual}")
    if expected != actual:
        print(f"    only-in-expected: {sorted(expected-actual)[:5]}")
        print(f"    only-in-actual:   {sorted(actual-expected)[:5]}")

# Sample 1 row pretty
print()
print('Sample row (first row of 운동 루틴 세션):')
r = datasets['운동 루틴 세션'][0]
for k, v in r.items():
    print(f'  {k}: {v[:80]}{"..." if len(v)>80 else ""}')
