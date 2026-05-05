"""루틴 추천 — RPE 메타 룰 (5): A02, A05, A07, A10, A13.

세션 처방 단계에서 무게를 정할 때 쓰이는 RPE 관련 룰.
실시간 코칭에도 일부 같은 룰이 들어가지만, 여기선 추천 컨텍스트
(세션 시작 전 무게 처방) 용도로 다시 구현.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# A02 — RPE-1RM% 변환표 (간이판)
# ----------------------------------------------------------------------------
# rules/A02.yaml | csv 2행
# 출처: Tuchscherer / PowerliftingToWin
# URL : https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/  ★★★
# ============================================================================
A02 = Citation(
    rule_id="A02", name="RPE-1RM% 변환표",
    source="Tuchscherer",
    url="https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/",
    confidence="★★★",
)


# ============================================================================
# A07 — RTS Generalized 풀 매트릭스 (추천 컨텍스트)
# ----------------------------------------------------------------------------
# 동일 표를 routine 컨텍스트에서도 사용 — coaching_rules.rpe 의 a07 함수와
# 같은 데이터지만 의존성을 끊기 위해 여기서 재정의.
# ============================================================================
A07 = Citation(
    rule_id="A07", name="RTS RPE×렙 매트릭스",
    source="Tuchscherer / RTS",
    url="https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/",
    confidence="★★☆",
)

_RTS_TABLE: dict[int, dict[float, float]] = {
    1:  {10.0: 100.0, 9.5: 97.8, 9.0: 95.5, 8.5: 93.9, 8.0: 92.2, 7.5: 90.7, 7.0: 89.2, 6.5: 87.8},
    5:  {10.0:  86.3, 9.5: 85.0, 9.0: 83.7, 8.5: 82.2, 8.0: 81.1, 7.5: 79.7, 7.0: 78.6, 6.5: 77.4},
    8:  {10.0:  78.6, 9.5: 77.4, 9.0: 76.2, 8.5: 75.1, 8.0: 74.0, 7.5: 72.3, 7.0: 70.7, 6.5: 69.4},
    12: {10.0:  71.3, 9.5: 70.3, 9.0: 70.3, 8.5: 68.9, 8.0: 67.5, 7.5: 65.9, 7.0: 64.4, 6.5: 63.0},
}

def a07_session_pct(reps: int, target_rpe: float) -> float:
    """A07: 세션 처방용 — 가장 가까운 표 셀로 보간."""
    keys = sorted(_RTS_TABLE)
    if reps <= keys[0]:
        rep_key = keys[0]
    elif reps >= keys[-1]:
        rep_key = keys[-1]
    else:
        rep_key = min(keys, key=lambda k: abs(k - reps))
    rpe_snapped = max(6.5, min(10.0, round(target_rpe * 2) / 2))
    return _RTS_TABLE[rep_key][rpe_snapped]


# ============================================================================
# A05 — 자율조절 vs 고정 %
# ----------------------------------------------------------------------------
# rules/A05.yaml | csv 5행
# 출처: MASS Research
# URL : https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/  ★★★
# ============================================================================
A05 = Citation(
    rule_id="A05", name="자율조절 vs 고정 %",
    source="MASS Research",
    url="https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/",
    confidence="★★★",
)

def a05_pick_mode(goal: str) -> str:
    """A05: 근력 목표 → 자율조절 우선 / 근비대 → 볼륨 우선."""
    if goal == "스트렝스":
        return "자율조절"
    return "볼륨우선"


# ============================================================================
# A10 — 종목·근육군별 변환 보정
# ----------------------------------------------------------------------------
# rules/A10.yaml | csv 10행
# 출처: Helms RPE accuracy 시리즈 / Tuchscherer
# URL : https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/  ★★☆
# ============================================================================
A10 = Citation(
    rule_id="A10", name="종목·근육군별 변환 보정",
    source="Helms / Tuchscherer",
    url="https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/",
    confidence="★★☆",
)

# 종목별 보정계수 (룰 카드 한줄설명: 스쿼트 1.00 / 벤치 1.00 / 데드 1.01 / 단관절 0.95)
_A10_FACTORS = {
    "스쿼트": 1.00, "벤치프레스": 1.00, "데드리프트": 1.01,
    "사이드레터럴": 0.95, "이두컬": 0.95, "삼두익스텐션": 0.95,
}

def a10_apply_correction(table_pct: float, movement: str, reps: int) -> float:
    """A10: 표 결과 % × 종목 보정계수.

    8렙 초과·단관절 → -3~5%p 추가 하향 (룰 카드).
    """
    factor = _A10_FACTORS.get(movement, 1.0)
    corrected = table_pct * factor
    if reps > 8 or factor < 1.0:
        corrected -= 3.0   # 룰 카드 -3~5%p 중간값
    return round(corrected, 1)


# ============================================================================
# A13 — 세션 간 RPE drift 보정 (추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/A13.yaml | csv 13행
# 출처: Tuchscherer / Helms
# URL : https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively  ★★☆
# ============================================================================
A13 = Citation(
    rule_id="A13", name="세션 간 RPE drift 보정",
    source="Tuchscherer / Helms",
    url="https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively",
    confidence="★★☆",
)

def a13_session_drift(drift: float, current_kg: float) -> tuple[float, str]:
    """A13: drift +1↑ → -5%, drift -1↓ → +2.5~5%."""
    if drift >= 1.0:
        return round(current_kg * 0.95, 1), "회복부족_감산"
    if drift <= -1.0:
        return round(current_kg * 1.025, 1), "진보_가산"
    return current_kg, "유지"
