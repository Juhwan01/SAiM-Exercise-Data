"""
Merge staging_new_rows.csv (35 rows) into master workout_knowledge_base.csv.

Steps:
  1. Load master + staging.
  2. Drop F01~F04 (paid/external exercise DBs no longer needed; we have 449-row internal pool).
  3. Resolve C11 collision: staging C11~C14 -> C12~C15 (master already owns C11=세션 길이 가이드).
  4. ID-sort + write back.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "workout_knowledge_base.csv"
STAGING = ROOT / "staging_new_rows.csv"

EXPECTED_HEADER = [
    "ID", "분류", "항목", "적용 시점",
    "운동 추천", "실시간 코칭", "지식베이스",
    "핵심 룰 (한 줄)",
    "입력값", "출력값/동작", "활용 예시",
    "출처", "URL", "신뢰도",
]

DROP_IDS = {"F01", "F02", "F03", "F04"}

# C11 in master is "세션 길이 가이드"; staging C-series shifts +1 to land after it.
STAGING_RENAME = {"C11": "C12", "C12": "C13", "C13": "C14", "C14": "C15"}


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    if not rows:
        sys.exit(f"empty: {path}")
    header, *data = rows
    if header != EXPECTED_HEADER:
        sys.exit(f"header mismatch in {path}\n  got:  {header}\n  want: {EXPECTED_HEADER}")
    bad = [(i + 2, len(r)) for i, r in enumerate(data) if len(r) != 14]
    if bad:
        sys.exit(f"column-count errors in {path}: {bad}")
    return header, data


def id_sort_key(row_id):
    prefix = row_id[0]
    try:
        num = int(row_id[1:])
    except ValueError:
        num = 0
    return (prefix, num)


def main():
    header, master = read_csv(MASTER)
    _, staging = read_csv(STAGING)
    print(f"master: {len(master)} rows  |  staging: {len(staging)} rows")

    # Drop F01~F04
    dropped = [r for r in master if r[0] in DROP_IDS]
    master = [r for r in master if r[0] not in DROP_IDS]
    print(f"dropped from master: {[r[0] for r in dropped]} ({len(dropped)} rows)")

    # Rename C11~C14 in staging
    renamed = []
    for r in staging:
        if r[0] in STAGING_RENAME:
            old = r[0]
            r[0] = STAGING_RENAME[old]
            renamed.append((old, r[0]))
    print(f"staging renamed: {renamed}")

    # Collision check
    master_ids = {r[0] for r in master}
    staging_ids = [r[0] for r in staging]
    if len(staging_ids) != len(set(staging_ids)):
        dupes = [i for i in staging_ids if staging_ids.count(i) > 1]
        sys.exit(f"duplicate IDs within staging: {sorted(set(dupes))}")
    collisions = [i for i in staging_ids if i in master_ids]
    if collisions:
        sys.exit(f"unresolved collisions: {collisions}")

    merged = sorted(master + staging, key=lambda r: id_sort_key(r[0]))

    with MASTER.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(header)
        w.writerows(merged)

    print(f"\nwrote {MASTER}: {len(merged)} rows")
    print(f"  master before: {len(master) + len(dropped)}  (- {len(dropped)} dropped)")
    print(f"  staging:       {len(staging)} rows added")
    print(f"  total:         {len(merged)}")


if __name__ == "__main__":
    main()
