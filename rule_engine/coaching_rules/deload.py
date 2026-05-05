"""실시간 코칭 — 디로드 트리거 (3개): G02, G04, G07.

디로드(=훈련 자극을 의도적으로 줄이는 주)를 자동 권고하는 트리거들.
실시간 코칭에서는 "이번 세트는 정상 진행하지만, 이번 주말에 디로드 권고"
같은 사용자 알림으로 노출된다.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# G02 — 디로드 트리거 (자동 감지)
# ----------------------------------------------------------------------------
# rules/G02.yaml | csv 75행
# 출처: Israetel / Bell 2024
# URL : https://shura.shu.ac.uk/35313/3/Bell-APracticalApproach(AM).pdf  ★★★
#
# 같은 무게에 RPE +2 상승, 수면·식욕 악화, 관절통 누적, 동기 저하 → 디로드 신호.
# ============================================================================
G02 = Citation(
    rule_id="G02", name="디로드 트리거 (자동 감지)",
    source="Israetel / Bell 2024",
    url="https://shura.shu.ac.uk/35313/3/Bell-APracticalApproach(AM).pdf",
    confidence="★★★",
)

def g02_basic_deload_trigger(rpe_drift: float, joint_pain_nprs: int | None = None) -> bool:
    """G02: 기본 디로드 트리거.

    True 이면 사용자에게 '이번 주 디로드 권장' 푸시.
    조건(룰 카드 한줄설명):
        같은 무게×렙에서 RPE +2 점 상승  OR  관절통 누적(NPRS≥4)
    """
    if rpe_drift >= 2.0:
        return True
    if joint_pain_nprs is not None and joint_pain_nprs >= 4:
        return True
    return False


# ============================================================================
# G04 — 주간 부하 +10% 룰 (부상 예방)
# ----------------------------------------------------------------------------
# rules/G04.yaml | csv 77행
# 출처: Gabbett ACWR
# URL : https://gymaware.com/progressive-overload-the-ultimate-guide/  ★★★
#
# 주간 총 부하 증가는 10% 이내. 초과 시 부상 위험. ACWR 0.8~1.3 안전 구간.
# ============================================================================
G04 = Citation(
    rule_id="G04", name="주간 부하 +10% 룰",
    source="Gabbett ACWR",
    url="https://gymaware.com/progressive-overload-the-ultimate-guide/",
    confidence="★★★",
)

def g04_weekly_load_check(this_week_volume: float, last_week_volume: float) -> dict:
    """G04: 주간 볼륨 변화율 → 경고 신호.

    Returns:
        {"증가율": float, "초과": bool, "메모": str}
    """
    if last_week_volume <= 0:
        return {"증가율": 0.0, "초과": False, "메모": "비교 기준 없음"}
    growth = (this_week_volume - last_week_volume) / last_week_volume
    if growth > 0.10:
        return {
            "증가율": round(growth, 3),
            "초과": True,
            "메모": f"주간 볼륨 +{growth*100:.1f}% — 10% 상한 초과 (부상 위험)",
        }
    return {"증가율": round(growth, 3), "초과": False, "메모": "주간 부하 안전 구간"}


# ============================================================================
# G07 — 디로드 트리거 신호 (다지표 자동)
# ----------------------------------------------------------------------------
# rules/G07.yaml | csv 80행
# 출처: Bell et al. 2023 Delphi Consensus (Sports Medicine - Open)
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/  ★★★
#
# 5개 지표 중 ≥2개 충족 시 익주 디로드 자동 권고:
#   ①RPE drift +1.5 이상
#   ②수면 <6h 주 4일+
#   ③관절통 NPRS ≥4
#   ④동기 ≤2/5
#   ⑤최근 PR 후 14일 경과
# ============================================================================
G07 = Citation(
    rule_id="G07", name="디로드 트리거 신호 (다지표 자동)",
    source="Bell 2023 Delphi Consensus",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/",
    confidence="★★★",
)

def g07_multi_indicator_deload(
    rpe_drift: float = 0.0,
    weekly_sleep_under_6h_days: int = 0,
    joint_pain_nprs: int | None = None,
    motivation_1_5: int | None = None,
    days_since_last_pr: int | None = None,
) -> dict:
    """G07: 5개 지표 평가 → 만족 개수 + 권고.

    Returns:
        {"히트": [지표명...], "권고_디로드": bool}
    """
    hits: list[str] = []
    if rpe_drift >= 1.5:
        hits.append("RPE_drift_+1.5↑")
    if weekly_sleep_under_6h_days >= 4:
        hits.append("수면<6h_주4일↑")
    if joint_pain_nprs is not None and joint_pain_nprs >= 4:
        hits.append("관절통_NPRS≥4")
    if motivation_1_5 is not None and motivation_1_5 <= 2:
        hits.append("동기≤2/5")
    if days_since_last_pr is not None and days_since_last_pr >= 14:
        hits.append("PR후_14일↑")
    return {"히트": hits, "권고_디로드": len(hits) >= 2}
