"""
Regenerate goal1/2/3 CSVs from master based on Y-flag columns.

Master columns 5/6/7 ("운동 추천", "실시간 코칭", "지식베이스") are filter flags.
- goal1 = rows where 운동 추천 == Y
- goal2 = rows where 실시간 코칭 == Y
- goal3 = rows where 지식베이스 == Y

Master is the only source of truth; goal files are derived.
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "workout_knowledge_base.csv"

GOALS = [
    ("운동 추천",   ROOT / "goal1_session_recommendation.csv"),
    ("실시간 코칭", ROOT / "goal2_realtime_coaching.csv"),
    ("지식베이스",  ROOT / "goal3_knowledge_base.csv"),
]


def id_sort_key(row_id):
    prefix = row_id[0]
    try:
        num = int(row_id[1:])
    except ValueError:
        num = 0
    return (prefix, num)


def main():
    with MASTER.open(encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    header, *data = rows
    print(f"master: {len(data)} rows")

    for col_name, out_path in GOALS:
        try:
            col_idx = header.index(col_name)
        except ValueError:
            sys.exit(f"missing column in master header: {col_name!r}")

        filtered = [r for r in data if r[col_idx] == "Y"]
        filtered.sort(key=lambda r: id_sort_key(r[0]))

        with out_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            w.writerow(header)
            w.writerows(filtered)

        print(f"  {out_path.name:42s} {len(filtered):3d} rows  ({col_name} = Y)")


if __name__ == "__main__":
    main()
