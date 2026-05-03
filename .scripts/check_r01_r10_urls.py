"""Validate R01-R10 CSV: column count, ID order, schema parity with master."""
import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

MASTER = '/home/pc1/workout-knowledge/workout_knowledge_base.csv'
NEW = '/home/pc1/workout-knowledge/.omc/research/r01-r10_behavior_coaching.csv'

with open(MASTER, encoding='utf-8-sig', newline='') as f:
    master_header = next(csv.reader(f))

with open(NEW, encoding='utf-8-sig', newline='') as f:
    rdr = csv.reader(f)
    new_header = next(rdr)
    rows = list(rdr)

print(f'Master cols ({len(master_header)}):', master_header)
print(f'New cols    ({len(new_header)}):', new_header)
print(f'Schema match: {master_header == new_header}')
print(f'Row count: {len(rows)}')
print()
for i, r in enumerate(rows, 1):
    print(f'Row {i:2}: cols={len(r):2} ID={r[0] if r else "?"!s:5} 분류={r[1] if len(r)>1 else "?":8} 항목={r[2] if len(r)>2 else "?"}')
    if len(r) != len(master_header):
        print(f'  !! COLUMN COUNT MISMATCH: {len(r)} vs {len(master_header)}')
        print(f'     row contents: {r}')

ids = [r[0] for r in rows]
expected = [f'R{i:02d}' for i in range(1,11)]
print()
print(f'IDs OK: {ids == expected}  got: {ids}')

# Check all 분류 = 행동 코칭
all_cat_ok = all(r[1] == '행동 코칭' for r in rows)
print(f'분류 all 행동 코칭: {all_cat_ok}')

# Check 지식베이스 = Y for all
all_kb_y = all(r[6] == 'Y' for r in rows)
print(f'지식베이스 all Y: {all_kb_y}')

# Check 실시간 코칭 = - for all
all_realtime_dash = all(r[5] == '-' for r in rows)
print(f'실시간 코칭 all -: {all_realtime_dash}')

# Print 신뢰도 distribution
from collections import Counter
print(f'신뢰도 dist: {Counter(r[13] for r in rows)}')
