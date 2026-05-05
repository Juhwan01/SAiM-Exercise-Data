"""서비스별 룰 명단을 뽑는다 (실시간 코칭 / 운동 추천)."""
from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"


def main() -> None:
    realtime: list[dict] = []
    recommend: list[dict] = []
    both: list[dict] = []
    for path in sorted(RULES_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            r = yaml.safe_load(f)
        usage = r.get("쓰임새") or {}
        rt = usage.get("실시간_코칭", False)
        rc = usage.get("운동_추천", False)
        if rt:
            realtime.append(r)
        if rc:
            recommend.append(r)
        if rt and rc:
            both.append(r)

    print(f"실시간 코칭 룰: {len(realtime)}")
    print(f"운동 추천 룰: {len(recommend)}")
    print(f"양쪽 모두: {len(both)}")
    print(f"실시간 전용: {len(realtime) - len(both)}")
    print(f"추천 전용: {len(recommend) - len(both)}")
    print()

    print("=== 실시간 코칭 명단 ===")
    by_class = defaultdict(list)
    for r in realtime:
        by_class[r.get("분류", "기타")].append((r["ID"], r.get("이름", "")))
    for cls, lst in sorted(by_class.items()):
        print(f"\n[{cls}] ({len(lst)})")
        for rid, name in lst:
            print(f"  - {rid}: {name}")

    print("\n\n=== 운동 추천 명단 ===")
    by_class2 = defaultdict(list)
    for r in recommend:
        by_class2[r.get("분류", "기타")].append((r["ID"], r.get("이름", "")))
    for cls, lst in sorted(by_class2.items()):
        print(f"\n[{cls}] ({len(lst)})")
        for rid, name in lst:
            print(f"  - {rid}: {name}")


if __name__ == "__main__":
    main()
