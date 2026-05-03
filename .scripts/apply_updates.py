"""
Apply URL updates to all 4 CSVs (master + 3 goal files).
Then re-run build_tsv to regenerate output TSVs.
"""
import csv, os, sys, shutil, subprocess
sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

UPDATES = {
    'D05': 'https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter',
    'E11': 'https://startingstrength.com/article/chins-and-pullups',
    'L03': 'https://pubmed.ncbi.nlm.nih.gov/19620931/',
    'O02': 'https://www.strongerbyscience.com/concurrent-training/',
    'A01': 'https://pubmed.ncbi.nlm.nih.gov/26049792/',
    'C11': 'https://pubmed.ncbi.nlm.nih.gov/29490526/',
    'E07': 'https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology',
    'E15': 'https://pubmed.ncbi.nlm.nih.gov/12617692/',
    'E16': 'https://startingstrength.com/article/the_squat',
    'E17': 'https://startingstrength.com/article/grip-width-on-the-bench-press',
    'F05': 'https://www.strongerbyscience.com/exercise-selection/',
    'H01': 'https://muscleandstrengthpyramids.com/training/',
    'H02': 'https://muscleandstrengthpyramids.com/training/',
    'I01': 'https://startingstrength.com/get-started/programs',
    'I02': 'https://www.strongerbyscience.com/tempo-for-muscle/',
    'I03': 'https://www.strongerbyscience.com/exercise-order-video/',
    'I04': 'https://www.scienceforsport.com/acutechronic-workload-ratio/',
    'J01': 'https://www.strongerbyscience.com/exercise-selection/',
    'J04': 'https://pubmed.ncbi.nlm.nih.gov/15903374/',
    'J05': 'https://www.strongerbyscience.com/exercise-selection/',
    'J06': 'https://muscleandstrengthpyramids.com/training/',
    'M02': 'https://muscleandstrengthpyramids.com/training/',
    'P04': 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/',
}

CSVS = [
    'workout_knowledge_base.csv',
    'goal1_session_recommendation.csv',
    'goal2_realtime_coaching.csv',
    'goal3_knowledge_base.csv',
]

# backup originals once
os.makedirs('.scripts/backup', exist_ok=True)
for c in CSVS:
    bk = os.path.join('.scripts/backup', c)
    if not os.path.exists(bk):
        shutil.copy2(c, bk)
        print(f'backup: {c} -> {bk}')

def update_csv(path):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)
    changed = 0
    for r in rows:
        rid = r.get('ID')
        if rid in UPDATES and r.get('URL') != UPDATES[rid]:
            r['URL'] = UPDATES[rid]
            changed += 1
    with open(path, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    return changed, len(rows)

total = 0
for c in CSVS:
    if not os.path.exists(c):
        print(f'(skip missing) {c}')
        continue
    n, total_rows = update_csv(c)
    total += n
    print(f'{c}: {n} URL updates / {total_rows} rows')

print(f'\nTotal URL updates across files: {total}')

# regenerate TSVs
print('\n--- Rebuilding TSVs ---')
r = subprocess.run([sys.executable, '.scripts/build_tsv.py'], capture_output=True, text=True, encoding='utf-8')
print(r.stdout[-1500:] if r.stdout else '')
if r.returncode != 0:
    print('STDERR:', r.stderr)
