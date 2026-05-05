"""룰 카드 ↔ 엔진 구현 일치 검증.

각 YAML 카드의 ID 가 엔진의 어느 모듈/함수에 등장하는지 grep 해서
실시간 코칭(50)·운동 추천(97) 라벨대로 구현됐는지 확인한다.
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
RULES = ROOT / "rules"
COACH = ROOT / "rule_engine" / "coaching_rules"
ROUTINE = ROOT / "rule_engine" / "routine_rules"


def main() -> None:
    coach_text = "\n".join(p.read_text(encoding="utf-8") for p in COACH.glob("*.py"))
    routine_text = "\n".join(p.read_text(encoding="utf-8") for p in ROUTINE.glob("*.py"))

    rt_expected: list[str] = []
    rec_expected: list[str] = []
    for path in sorted(RULES.glob("*.yaml")):
        d = yaml.safe_load(path.read_text(encoding="utf-8"))
        usage = d.get("쓰임새") or {}
        if usage.get("실시간_코칭"):
            rt_expected.append(d["ID"])
        if usage.get("운동_추천"):
            rec_expected.append(d["ID"])

    def has_id(text: str, rid: str) -> bool:
        # rule_id="A11" 또는 # rules/A11.yaml 같은 토큰
        return bool(re.search(rf"\b{rid}\b", text))

    rt_missing = [r for r in rt_expected if not has_id(coach_text, r)]
    rt_extra: list[str] = []  # (간단 검증 — 추가만 검사)

    rec_missing = [r for r in rec_expected if not has_id(routine_text, r)]

    print(f"실시간 코칭 라벨 룰: {len(rt_expected)}")
    print(f"  coaching_rules/ 에서 발견: {len(rt_expected) - len(rt_missing)}")
    print(f"  누락: {rt_missing or '없음'}")
    print()
    print(f"운동 추천 라벨 룰: {len(rec_expected)}")
    print(f"  routine_rules/ 에서 발견: {len(rec_expected) - len(rec_missing)}")
    print(f"  누락: {rec_missing or '없음'}")
    print()
    if not rt_missing and not rec_missing:
        print("✅ 라벨된 모든 룰이 해당 엔진에 구현됨")
    else:
        print("⚠ 누락된 룰 있음 — 위 ID 카드를 해당 폴더에 추가 필요")


if __name__ == "__main__":
    main()
