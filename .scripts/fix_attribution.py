"""
Update 출처 (source attribution) to match new URLs for A01, E15, P04.
Also regenerate TSVs.
"""
import csv, os, sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

ATTR = {
    'A01': 'Zourdos 2016 (Tuchscherer RPE 검증)',
    'E15': 'Cheung 2003 (DOMS 리뷰)',
    'P04': 'Page 2012 (스트레칭·모빌리티 리뷰)',
}

CSVS = [
    'workout_knowledge_base.csv',
    'goal1_session_recommendation.csv',
    'goal2_realtime_coaching.csv',
    'goal3_knowledge_base.csv',
]

def patch(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    n = 0
    for r in rows:
        rid = r.get('ID')
        if rid in ATTR and r.get('출처') != ATTR[rid]:
            r['출처'] = ATTR[rid]
            n += 1
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return n

for c in CSVS:
    if os.path.exists(c):
        n = patch(c)
        print(f'{c}: {n} 출처 updates')

# Rebuild TSVs
print('\nRebuilding TSVs...')
r = subprocess.run([sys.executable, '.scripts/build_tsv.py'], capture_output=True, text=True, encoding='utf-8')
print(r.stdout[-1200:] if r.stdout else '')
if r.returncode != 0:
    print('STDERR:', r.stderr)
