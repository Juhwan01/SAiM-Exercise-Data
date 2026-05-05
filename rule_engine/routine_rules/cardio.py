"""루틴 추천 — 카디오 (3 룰): O01, O02, O03.

근력+유산소 간섭, HIIT vs LISS 선택, 카디오 타이밍.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# O01 — 근력+유산소 간섭효과
# ----------------------------------------------------------------------------
# rules/O01.yaml | csv 109행
# 출처: Wilson 2012 메타분석
# URL : https://pubmed.ncbi.nlm.nih.gov/22002517/  ★★★
# ============================================================================
O01 = Citation(
    rule_id="O01", name="근력+유산소 간섭",
    source="Wilson 2012 meta",
    url="https://pubmed.ncbi.nlm.nih.gov/22002517/",
    confidence="★★★",
)

def o01_interference_check(weekly_freq: int, minutes_per_session: int) -> dict:
    """O01: 카디오 빈도/시간 → 간섭 위험."""
    safe = weekly_freq < 3 or minutes_per_session <= 30
    return {
        "안전": safe,
        "메모": "주 3회 미만 또는 30분 이하 = 간섭 미미",
        "같은날_권고": "근력 먼저 또는 6h+ 분리",
    }


# ============================================================================
# O02 — HIIT vs LISS
# ----------------------------------------------------------------------------
# rules/O02.yaml | csv 110행
# 출처: Schoenfeld / Helms
# URL : https://www.strongerbyscience.com/concurrent-training/  ★★★
# ============================================================================
O02 = Citation(
    rule_id="O02", name="HIIT vs LISS",
    source="Schoenfeld / Helms",
    url="https://www.strongerbyscience.com/concurrent-training/",
    confidence="★★★",
)

def o02_pick_modality(strength_freq: int, available_minutes: int) -> str:
    """O02: 근력 사용자 = LISS 우선. 시간 부족 = HIIT."""
    if available_minutes < 20:
        return "HIIT 15분"
    if strength_freq >= 4:
        return "LISS 30분 (회복 부담↓)"
    return "혼합 (HIIT 1~2회 + LISS 1~2회)"


# ============================================================================
# O03 — 카디오 타이밍
# ----------------------------------------------------------------------------
# rules/O03.yaml | csv 111행
# 출처: Robineau 2016
# URL : https://pubmed.ncbi.nlm.nih.gov/25546450/  ★★☆
# ============================================================================
O03 = Citation(
    rule_id="O03", name="카디오 타이밍",
    source="Robineau 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/25546450/",
    confidence="★★☆",
)

def o03_cardio_placement(strength_focus: bool, leg_day: bool) -> str:
    """O03: 카디오 배치.

    근력 우선 → 근력 후 카디오 또는 별도 세션.
    다리 운동 후 러닝 X.
    """
    if leg_day:
        return "다리 운동 후 러닝 회피 — 다른 날로"
    if strength_focus:
        return "근력 후 카디오 또는 별도 세션. 다른 날 분리가 최선"
    return "별도 세션 권장 (카디오/근력 분리)"
