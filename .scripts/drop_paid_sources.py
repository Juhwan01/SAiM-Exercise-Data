"""
Drop rows whose source is a paid book product page (Helms pyramid book).
Targets: H01, H02, J06, M02
Affected files: master CSV + goal1 + goal3 (goal2 unaffected).
"""
import csv, os, shutil, sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')
os.chdir(r'C:\users\jungj\desktop\workout-knowledge')

DROP_IDS = {'H01', 'H02', 'J06', 'M02'}
FILES = [
    'workout_knowledge_base.csv',
    'goal1_session_recommendation.csv',
    'goal3_knowledge_base.csv',
]

stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = f'.scripts/backup/{stamp}_drop_paid'
os.makedirs(backup_dir, exist_ok=True)

print(f'Backup -> {backup_dir}\n')

for fp in FILES:
    shutil.copy2(fp, os.path.join(backup_dir, os.path.basename(fp)))
    with open(fp, encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        rows = list(reader)
    header, body = rows[0], rows[1:]
    kept = [r for r in body if r and r[0] not in DROP_IDS]
    dropped = [r[0] for r in body if r and r[0] in DROP_IDS]
    with open(fp, 'w', encoding='utf-8', newline='') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(kept)
    print(f'{fp}')
    print(f'  before: {len(body)} data rows')
    print(f'  dropped: {dropped}')
    print(f'  after : {len(kept)} data rows\n')

print('Done.')
