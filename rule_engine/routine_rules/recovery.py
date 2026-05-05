"""루틴 추천 — 회복/디로드/수면 (12 룰): K05, K06, K07, G01, G03, G04, G05, G06, G08, G09, G10, G11.

메조사이클 디로드 처방, 수면 권장, 능동 회복.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# K05 — 수면-근비대 관계
# ----------------------------------------------------------------------------
# rules/K05.yaml | csv 79행
# 출처: Knowles 2018 / Mah 2011
# URL : https://pubmed.ncbi.nlm.nih.gov/29422383/  ★★★
# ============================================================================
K05 = Citation(
    rule_id="K05", name="수면-근비대 관계",
    source="Knowles 2018 / Mah 2011",
    url="https://pubmed.ncbi.nlm.nih.gov/29422383/",
    confidence="★★★",
)

def k05_sleep_target(age: int) -> tuple[float, float]:
    """K05: 권장 수면 시간 범위(시간)."""
    return (7.0, 9.0)


# ============================================================================
# K06 — 수면 부족 → 부상 위험 (추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/K06.yaml | csv 80행
# 출처: Milewski 2014
# URL : https://pubmed.ncbi.nlm.nih.gov/25028798/  ★★★
# ============================================================================
K06 = Citation(
    rule_id="K06", name="수면 부족 위험",
    source="Milewski 2014",
    url="https://pubmed.ncbi.nlm.nih.gov/25028798/",
    confidence="★★★",
)

def k06_warning_threshold() -> dict:
    """K06: 알림 임계값 — 8h 미만이면 부상 위험 1.7배."""
    return {"위험_시작_h": 8.0, "위험배수": 1.7, "메모": "<8h 시 부상 위험 1.7배"}


# ============================================================================
# K07 — 능동 회복 (active recovery)
# ----------------------------------------------------------------------------
# rules/K07.yaml | csv 81행
# 출처: Dupuy 2018 / Frontiers
# URL : https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full  ★★★
# ============================================================================
K07 = Citation(
    rule_id="K07", name="능동 회복",
    source="Dupuy 2018",
    url="https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full",
    confidence="★★★",
)

def k07_active_recovery() -> dict:
    """K07: 저강도 유산소 10~30분 (20~40% VO2max)."""
    return {
        "강도_pct_VO2max": (20, 40),
        "분": (10, 30),
        "예시": ["가벼운 자전거", "걷기", "수영"],
    }


# ============================================================================
# G01 — 디로드 정의·주기
# ----------------------------------------------------------------------------
# rules/G01.yaml | csv 75행
# 출처: Bell et al / Frontiers
# URL : https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2022.1073223/full  ★★★
# ============================================================================
G01 = Citation(
    rule_id="G01", name="디로드 정의·주기",
    source="Bell / Frontiers",
    url="https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2022.1073223/full",
    confidence="★★★",
)

def g01_deload_cycle() -> dict:
    """G01: 디로드 = 5~7일, 평균 4~6주마다."""
    return {"디로드_일": (5, 7), "주기_주": (4, 6)}


# ============================================================================
# G03 — 디로드 처방 방법
# ----------------------------------------------------------------------------
# rules/G03.yaml | csv 77행
# 출처: Bell 2024 / RP
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/  ★★★
# ============================================================================
G03 = Citation(
    rule_id="G03", name="디로드 처방 방법",
    source="Bell 2024 / RP",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/",
    confidence="★★★",
)

def g03_deload_basic_prescription(prev_volume: int, prev_intensity_pct: float) -> dict:
    """G03: 볼륨 -50%, 강도 -10~20%, 빈도 유지."""
    return {
        "볼륨_세트": int(round(prev_volume * 0.5)),
        "강도_pct": round(prev_intensity_pct * 0.85, 1),  # -15% 중간값
        "빈도": "유지",
    }


# ============================================================================
# G04 — 주간 부하 +10% 룰
# ----------------------------------------------------------------------------
# rules/G04.yaml | csv 78행
# 출처: Gabbett ACWR
# URL : https://gymaware.com/progressive-overload-the-ultimate-guide/  ★★★
# ============================================================================
G04 = Citation(
    rule_id="G04", name="주간 부하 +10% 룰",
    source="Gabbett",
    url="https://gymaware.com/progressive-overload-the-ultimate-guide/",
    confidence="★★★",
)

def g04_weekly_cap_pct() -> float:
    """G04: 주간 총 부하 증가 상한(%)."""
    return 10.0


# ============================================================================
# G05 — 디로드 주 볼륨/강도 정량 처방
# ----------------------------------------------------------------------------
# rules/G05.yaml | csv 79행
# 출처: Helms 3DMJ + RP
# URL : https://www.3dmusclejourney.com/blog/how-do-we-deload-part-1  ★★★
# ============================================================================
G05 = Citation(
    rule_id="G05", name="디로드 정량 처방",
    source="Helms 3DMJ",
    url="https://www.3dmusclejourney.com/blog/how-do-we-deload-part-1",
    confidence="★★★",
)

def g05_deload_quantitative(
    prev_sets_per_muscle: dict[str, int],
    prev_avg_weight: dict[str, float],
) -> dict:
    """G05: 세트 수 ½, 무게 90~100% 유지, 빈도 유지, 5~7일."""
    return {
        "세트_per_근육": {m: max(1, s // 2) for m, s in prev_sets_per_muscle.items()},
        "무게_per_운동": {m: round(w * 0.95, 1) for m, w in prev_avg_weight.items()},
        "기간_일": 7,
    }


# ============================================================================
# G06 — 고피로 시 강도까지 동시 감축
# ----------------------------------------------------------------------------
# rules/G06.yaml | csv 80행
# 출처: Israetel / RP
# URL : https://renaissanceperiodization.com/dr-mike-israetel-compilation/  ★★☆
# ============================================================================
G06 = Citation(
    rule_id="G06", name="고피로 동시 감축",
    source="Israetel / RP",
    url="https://renaissanceperiodization.com/dr-mike-israetel-compilation/",
    confidence="★★☆",
)

def g06_high_fatigue_deload(
    rpe_avg_recent: float, sleep_avg_h: float, joint_pain: bool,
) -> dict:
    """G06: 일반 vs 고피로 디로드 분기.

    고피로 신호: RPE 평균 >9 + 수면 <6h + 관절통 있음
    """
    is_high_fatigue = rpe_avg_recent > 9 and sleep_avg_h < 6 and joint_pain
    if is_high_fatigue:
        return {"모드": "고피로", "세트_배수": 0.5, "무게_배수": 0.5}
    return {"모드": "일반", "세트_배수": 0.5, "무게_배수": 0.95}


# ============================================================================
# G08 — MRV 도달 시 강제 디로드
# ----------------------------------------------------------------------------
# rules/G08.yaml | csv 82행
# 출처: Israetel — Volume Landmarks
# URL : https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/  ★★☆
# ============================================================================
G08 = Citation(
    rule_id="G08", name="MRV 도달 강제 디로드",
    source="Israetel",
    url="https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/",
    confidence="★★☆",
)

def g08_force_deload(weekly_sets: int, mrv: int, rpe_drift: float, week_num: int) -> bool:
    """G08: MRV 도달 + RPE +1 이상 상승 OR 6주차 초과 → 강제 디로드."""
    if weekly_sets >= mrv and rpe_drift >= 1.0:
        return True
    if week_num > 6:
        return True
    return False


# ============================================================================
# G09 — 활성 디로드 vs 완전 휴식 선택
# ----------------------------------------------------------------------------
# rules/G09.yaml | csv 83행
# 출처: Coleman et al. 2024 PeerJ
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC10809978/  ★★★
# ============================================================================
G09 = Citation(
    rule_id="G09", name="활성 디로드 vs 완전 휴식",
    source="Coleman 2024",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10809978/",
    confidence="★★★",
)

def g09_choose_deload_type(
    has_injury: bool, burnout_1_5: int | None, sleep_avg_h: float | None,
) -> str:
    """G09: 활성(권장) vs 패시브 1주 선택.

    부상·번아웃·수면<5h 지속 시에만 패시브.
    """
    if has_injury:
        return "패시브_1주"
    if burnout_1_5 is not None and burnout_1_5 <= 1:
        return "패시브_1주"
    if sleep_avg_h is not None and sleep_avg_h < 5:
        return "패시브_1주"
    return "활성"


# ============================================================================
# G10 — 한국 사용자 디로드 주기 기본값
# ----------------------------------------------------------------------------
# rules/G10.yaml | csv 84행
# 출처: RP 메조 가이드
# URL : https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/  ★★☆
# ============================================================================
G10 = Citation(
    rule_id="G10", name="한국 사용자 디로드 주기",
    source="RP 메조 가이드",
    url="https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/",
    confidence="★★☆",
)

def g10_korean_deload_cycle(level: str) -> dict:
    """G10: 한국 직장인 변수(회식·출장) 고려 → 6주 상한."""
    if level in ("초보", "절대초보"):
        return {"방식": "신호기반_자동", "기본_주기_주": None}
    return {"방식": "강제", "기본_주기_주": 6}   # 4~6주 중 상한


# ============================================================================
# G11 — 미달 누적 디로드 트리거
# ----------------------------------------------------------------------------
# rules/G11.yaml | csv 85행
# 출처: Israetel et al., Scientific Principles of Hypertrophy Training
# URL : https://rpstrength.com/blogs/articles/in-defense-of-set-increases-within-the-hypertrophy-mesocycle  ★★☆
# ============================================================================
G11 = Citation(
    rule_id="G11", name="미달 누적 디로드 트리거",
    source="Israetel — Hypertrophy Training",
    url="https://rpstrength.com/blogs/articles/in-defense-of-set-increases-within-the-hypertrophy-mesocycle",
    confidence="★★☆",
)

def g11_should_deload_from_stalls(stalled_lifts_count: int, avg_rpe: float) -> bool:
    """G11: 다관절 메인리프트 ≥2개 stall + 평균 RPE 9~10 → 디로드."""
    return stalled_lifts_count >= 2 and avg_rpe >= 9.0
