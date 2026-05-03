"""
Merge .omc/research/ staging CSVs into master workout_knowledge_base.csv.
Inserts new rows in ID-sorted positions to preserve master's alphabetical layout.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "workout_knowledge_base.csv"
STAGING_FILES = [
    ROOT / ".omc/research/k12_korean_protein.csv",
    ROOT / ".omc/research/r01-r10_behavior_coaching.csv",
    ROOT / ".omc/research/q04-q06_rehab.csv",
    ROOT / ".omc/research/l05_chronic_disease.csv",
]
EXPECTED_HEADER = [
    "ID", "분류", "항목", "적용 시점",
    "운동 추천", "실시간 코칭", "지식베이스",
    "핵심 룰 (한 줄)",
    "입력값", "출력값/동작", "활용 예시",
    "출처", "URL", "신뢰도",
]


def read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)
    if not rows:
        sys.exit(f"empty: {path}")
    header, *data = rows
    if header != EXPECTED_HEADER:
        sys.exit(f"header mismatch in {path}\n  got:  {header}\n  want: {EXPECTED_HEADER}")
    bad = [(i + 2, len(r)) for i, r in enumerate(data) if len(r) != 14]
    if bad:
        sys.exit(f"column-count errors in {path}: {bad}")
    return header, data


def id_sort_key(row_id: str):
    prefix = row_id[0]
    try:
        num = int(row_id[1:])
    except ValueError:
        num = 0
    return (prefix, num)


def main():
    header, master = read_csv(MASTER)
    print(f"master: {len(master)} rows")

    staging_rows = []
    for sp in STAGING_FILES:
        _, rows = read_csv(sp)
        print(f"  + {sp.name}: {len(rows)} rows -> IDs {[r[0] for r in rows]}")
        staging_rows.extend(rows)

    # ID uniqueness check
    master_ids = {r[0] for r in master}
    new_ids = [r[0] for r in staging_rows]
    if len(new_ids) != len(set(new_ids)):
        dupes = [i for i in new_ids if new_ids.count(i) > 1]
        sys.exit(f"duplicate IDs within staging: {sorted(set(dupes))}")
    collisions = [i for i in new_ids if i in master_ids]
    if collisions:
        sys.exit(f"ID collisions with master: {collisions}")

    merged = sorted(master + staging_rows, key=lambda r: id_sort_key(r[0]))

    out_path = MASTER
    with out_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(merged)

    print(f"\nwrote {out_path}: {len(merged)} rows ({len(master)} + {len(staging_rows)})")
    print(f"new IDs inserted: {sorted(new_ids, key=id_sort_key)}")


if __name__ == "__main__":
    main()
