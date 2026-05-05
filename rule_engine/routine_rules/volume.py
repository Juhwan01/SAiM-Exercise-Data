"""루틴 추천 — 주간 볼륨 기준 (5 룰): B01, B02, B03, B04, B05.

근육군별 볼륨 랜드마크. 메조사이클 처방의 기준값.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# B01 — MV (유지 볼륨)
# ----------------------------------------------------------------------------
# rules/B01.yaml | csv 15행
# 출처: Israetel / RP Strength
# URL : https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth  ★★★
#
# 근육군당 주 6세트 정도가 현재 근육량 유지 최소치.
# ============================================================================
B01 = Citation(
    rule_id="B01", name="MV (유지 볼륨)",
    source="Israetel / RP",
    url="https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth",
    confidence="★★★",
)

# 근육군별 MV (유지 볼륨, 세트/주). 룰 카드 기준 보수적 디폴트=6
_B01_MV = {
    "가슴": 8, "등": 8, "어깨": 8, "이두": 6, "삼두": 6,
    "다리": 6, "둔근": 6, "햄스트링": 6, "복근": 6,
    "기타": 6,
}

def b01_maintenance_volume(muscle: str) -> int:
    """B01: 근육군별 유지 볼륨(세트/주)."""
    return _B01_MV.get(muscle, 6)


# ============================================================================
# B02 — MEV (성장 시작 볼륨)
# ----------------------------------------------------------------------------
# rules/B02.yaml | csv 16행
# 출처: Israetel
# URL : https://drmikeisraetel.com/dr-mike-israetel-mv-mev-mav-mrv-explained/  ★★★
#
# 한줄설명: 가슴 8, 등 10, 다리 6~8세트/주 등 근육군별 다름.
# ============================================================================
B02 = Citation(
    rule_id="B02", name="MEV (성장 시작 볼륨)",
    source="Israetel",
    url="https://drmikeisraetel.com/dr-mike-israetel-mv-mev-mav-mrv-explained/",
    confidence="★★★",
)

# 룰 카드 한줄설명에 명시된 값 + 합리적 디폴트
_B02_MEV = {
    "가슴": 8, "등": 10, "어깨": 8, "이두": 8, "삼두": 6,
    "다리": 7, "둔근": 6, "햄스트링": 6, "복근": 0,
    "기타": 8,
}

def b02_starting_volume(muscle: str) -> int:
    """B02: 메조사이클 1주차 시작 볼륨(세트/주)."""
    return _B02_MEV.get(muscle, 8)


# ============================================================================
# B03 — MAV (최적 적응 볼륨)
# ----------------------------------------------------------------------------
# rules/B03.yaml | csv 17행
# 출처: Israetel / RP
# URL : https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth  ★★★
#
# MEV~MRV 사이의 "성장 존". 매주 +1~2세트 점진 증가.
# ============================================================================
B03 = Citation(
    rule_id="B03", name="MAV (최적 적응 볼륨)",
    source="Israetel / RP",
    url="https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth",
    confidence="★★★",
)

def b03_progress_weekly(current_volume: int, week_num: int) -> int:
    """B03: 다음 주 권장 볼륨 = 이번 주 + 1~2세트 (룰 카드 그대로).

    초기 주차는 +2, 4주차 이후는 +1 로 보수적.
    """
    increment = 2 if week_num <= 3 else 1
    return current_volume + increment


# ============================================================================
# B04 — MRV (회복 가능 최대 볼륨)
# ----------------------------------------------------------------------------
# rules/B04.yaml | csv 18행
# 출처: Israetel
# URL : https://propanefitness.com/maximum-recoverable-volume/  ★★★
# ============================================================================
B04 = Citation(
    rule_id="B04", name="MRV (회복 가능 최대 볼륨)",
    source="Israetel",
    url="https://propanefitness.com/maximum-recoverable-volume/",
    confidence="★★★",
)

# 근육군당 주 18~25+ 세트 (룰 카드)
_B04_MRV = {
    "가슴": 22, "등": 25, "어깨": 22, "이두": 26, "삼두": 24,
    "다리": 20, "둔근": 20, "햄스트링": 20, "복근": 25,
    "기타": 18,
}

def b04_max_volume(muscle: str) -> int:
    """B04: 근육군당 회복 가능 최대 볼륨."""
    return _B04_MRV.get(muscle, 18)


# ============================================================================
# B05 — Volume Dose-Response 메타
# ----------------------------------------------------------------------------
# rules/B05.yaml | csv 19행
# 출처: Schoenfeld / Krieger
# URL : https://www.strongerbyscience.com/volume/  ★★★
#
# 근비대 목표: 주당 12~20세트. 20+ 추가 효과 미미.
# ============================================================================
B05 = Citation(
    rule_id="B05", name="Volume Dose-Response 메타",
    source="Schoenfeld / Krieger",
    url="https://www.strongerbyscience.com/volume/",
    confidence="★★★",
)

def b05_recommended_volume_range(goal: str) -> tuple[int, int]:
    """B05: 목표별 주간 권장 볼륨 범위."""
    if goal in ("벌크업", "근육량 증가"):
        return (12, 20)
    if goal == "스트렝스":
        return (8, 16)
    if goal == "다이어트":
        return (10, 18)
    return (8, 12)   # 건강증진
