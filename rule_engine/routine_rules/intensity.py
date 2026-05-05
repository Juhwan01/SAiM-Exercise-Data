"""루틴 추천 — 세트/렙/강도 처방 (15 룰): C01~C15.

목표·렙수·1RM·실패 처리·추정 1RM 공식 모음.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# C01 — NSCA RM-1RM% 표
# ----------------------------------------------------------------------------
# rules/C01.yaml | csv 20행
# 출처: NSCA Essentials 4판
# URL : https://www.nsca.com/contentassets/61d813865e264c6e852cadfe247eae52/nsca_training_load_chart.pdf  ★★★
# ============================================================================
C01 = Citation(
    rule_id="C01", name="NSCA RM-1RM% 표",
    source="NSCA Essentials 4판",
    url="https://www.nsca.com/contentassets/61d813865e264c6e852cadfe247eae52/nsca_training_load_chart.pdf",
    confidence="★★★",
)

# 룰 카드 한줄설명: 5RM=87%, 8RM=80%, 10RM=75%, 12RM=67%
_C01_RM_PCT = {
    1: 100.0, 2: 95.0, 3: 93.0, 4: 90.0, 5: 87.0,
    6: 85.0,  7: 83.0, 8: 80.0, 9: 77.0, 10: 75.0,
    11: 70.0, 12: 67.0, 15: 60.0, 20: 50.0,
}

def c01_pct_for_reps(reps: int) -> float:
    """C01: RM 횟수 → %1RM (NSCA 표 보간)."""
    if reps in _C01_RM_PCT:
        return _C01_RM_PCT[reps]
    keys = sorted(_C01_RM_PCT)
    if reps <= keys[0]:
        return _C01_RM_PCT[keys[0]]
    if reps >= keys[-1]:
        return _C01_RM_PCT[keys[-1]]
    # 선형 보간
    for i, k in enumerate(keys[:-1]):
        if k <= reps <= keys[i + 1]:
            lo, hi = k, keys[i + 1]
            t = (reps - lo) / (hi - lo)
            return _C01_RM_PCT[lo] * (1 - t) + _C01_RM_PCT[hi] * t
    return 75.0


def c01_recommend_weight(reps: int, one_rm_kg: float) -> float:
    """C01: 목표 렙수 + 1RM → 추천 무게(kg)."""
    return round(one_rm_kg * c01_pct_for_reps(reps) / 100.0, 1)


# ============================================================================
# C02 — Repetition Continuum
# ----------------------------------------------------------------------------
# rules/C02.yaml | csv 21행
# 출처: Schoenfeld 2021 / NSCA
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/  ★★★
#
# 근력 ≥85%/1~6렙, 근비대 67~85%/6~12렙 (단 6~30렙 폭넓게 가능),
# 근지구력 ≤67%/12+렙
# ============================================================================
C02 = Citation(
    rule_id="C02", name="Repetition Continuum",
    source="Schoenfeld 2021 / NSCA",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/",
    confidence="★★★",
)

def c02_continuum(goal: str) -> dict:
    """C02: 목표 → 렙범위 + %1RM 범위."""
    if goal == "스트렝스":
        return {"렙범위": (1, 6), "pct": (85.0, 100.0)}
    if goal in ("벌크업", "근육량 증가"):
        return {"렙범위": (6, 12), "pct": (67.0, 85.0)}
    if goal == "다이어트":
        return {"렙범위": (8, 15), "pct": (60.0, 80.0)}
    # 근지구력/건강
    return {"렙범위": (12, 20), "pct": (50.0, 67.0)}


# ============================================================================
# C03 — NSCA 단계별 처방
# ----------------------------------------------------------------------------
# rules/C03.yaml | csv 22행
# 출처: NSCA / Bompa
# URL : https://www.nsca.com/...  ★★★
#
# 근비대기: 50~75%, 8~20렙, 3~6세트 / 근력기: 80~95%, 2~6렙, 2~6세트
# ============================================================================
C03 = Citation(
    rule_id="C03", name="NSCA 단계별 처방",
    source="NSCA / Bompa",
    url="https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/",
    confidence="★★★",
)

def c03_phase_prescription(phase: str) -> dict:
    """C03: 훈련 단계 → 세트/렙/강도."""
    if phase == "근력기":
        return {"세트": (2, 6), "렙": (2, 6), "pct": (80.0, 95.0)}
    if phase == "근비대기":
        return {"세트": (3, 6), "렙": (8, 20), "pct": (50.0, 75.0)}
    return {"세트": (3, 4), "렙": (10, 15), "pct": (60.0, 75.0)}   # 일반


# ============================================================================
# C04 — ACSM 일반인 가이드라인
# ----------------------------------------------------------------------------
# rules/C04.yaml | csv 23행
# 출처: ACSM 2026 Position Stand
# URL : https://acsm.org/resistance-training-guidelines-update-2026/  ★★★
# ============================================================================
C04 = Citation(
    rule_id="C04", name="ACSM 일반인 가이드라인",
    source="ACSM 2026",
    url="https://acsm.org/resistance-training-guidelines-update-2026/",
    confidence="★★★",
)

def c04_general_population_default() -> dict:
    """C04: 건강 성인 디폴트 처방.

    주 2~3회, 근육군당 1~4세트, 8~20렙, 40~70% 1RM.
    강화 시 60~80%, 8~12렙, 2~3분 휴식.
    """
    return {
        "주_빈도": (2, 3),
        "근육군당_세트": (1, 4),
        "렙": (8, 20),
        "pct": (40.0, 70.0),
        "강화시_pct": (60.0, 80.0),
        "강화시_렙": (8, 12),
        "강화시_휴식_초": (120, 180),
    }


# ============================================================================
# C05 — 실패 vs RIR
# ----------------------------------------------------------------------------
# rules/C05.yaml | csv 24행
# 출처: Refalo / Pelland 2024
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC10161210/  ★★★
#
# 컴파운드 RIR 2~3 / 아이솔레이션 RIR 0~2 디폴트.
# ============================================================================
C05 = Citation(
    rule_id="C05", name="실패 vs RIR",
    source="Refalo / Pelland 2024",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC10161210/",
    confidence="★★★",
)

def c05_default_rir(movement_type: str) -> int:
    """C05: 운동 종류별 권장 디폴트 RIR.

    'compound' → 2 (2~3 중간)
    'isolation' → 1 (0~2 중간)
    """
    return 2 if movement_type == "compound" else 1


# ============================================================================
# C06 — 훈련 빈도
# ----------------------------------------------------------------------------
# rules/C06.yaml | csv 25행
# 출처: Schoenfeld 2016/2018
# URL : https://pubmed.ncbi.nlm.nih.gov/27102172/  ★★★
#
# 볼륨 동일 시 빈도는 비대에 무의미. 단 주 2회 이상 분할이 유리.
# ============================================================================
C06 = Citation(
    rule_id="C06", name="훈련 빈도",
    source="Schoenfeld 2016/2018",
    url="https://pubmed.ncbi.nlm.nih.gov/27102172/",
    confidence="★★★",
)

def c06_min_frequency_per_muscle() -> int:
    """C06: 근육군당 최소 주 빈도(룰 카드 권장 = 2)."""
    return 2


# ============================================================================
# C07 — 휴식 시간 (운동 추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/C07.yaml | csv 26행
# 출처: Schoenfeld 2016
# URL : https://pubmed.ncbi.nlm.nih.gov/26605807/  ★★★
# ============================================================================
C07 = Citation(
    rule_id="C07", name="휴식 시간",
    source="Schoenfeld 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/26605807/",
    confidence="★★★",
)

def c07_rest_table(goal: str) -> dict[str, int]:
    """C07: 운동 종류별 권장 휴식 초 묶음."""
    if goal == "스트렝스":
        return {"compound": 240, "isolation": 180}
    return {"compound": 150, "isolation": 90}


# ============================================================================
# C08 — Double Progression (운동 추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/C08.yaml | csv 27행
# 출처: Legion / Bret Contreras
# URL : https://legionathletics.com/double-progression/  ★★★
# ============================================================================
C08 = Citation(
    rule_id="C08", name="Double Progression",
    source="Legion / Bret Contreras",
    url="https://legionathletics.com/double-progression/",
    confidence="★★★",
)

def c08_default_rep_range(goal: str) -> tuple[int, int]:
    """C08: 목표별 디폴트 렙 레인지 (Double Progression 운영용)."""
    if goal == "스트렝스":
        return (3, 6)
    if goal in ("벌크업", "근육량 증가"):
        return (8, 12)
    return (10, 15)


# ============================================================================
# C09 / C10 — 1RM 추정 공식
# ----------------------------------------------------------------------------
# rules/C09.yaml | csv 28행 / rules/C10.yaml | csv 29행
# 출처: Epley 1985 / Brzycki 1993
# URL : https://en.wikipedia.org/wiki/One-repetition_maximum  ★★★
# ============================================================================
C09 = Citation(rule_id="C09", name="Epley 1RM 공식", source="Epley 1985",
               url="https://en.wikipedia.org/wiki/One-repetition_maximum", confidence="★★★")
C10 = Citation(rule_id="C10", name="Brzycki 1RM 공식", source="Brzycki 1993",
               url="https://en.wikipedia.org/wiki/One-repetition_maximum", confidence="★★★")

def c09_epley_1rm(weight_kg: float, reps: int) -> float:
    """C09: 1RM = 무게 × (1 + 렙수/30). 6~10렙에서 정확."""
    return round(weight_kg * (1 + reps / 30.0), 1)


def c10_brzycki_1rm(weight_kg: float, reps: int) -> float:
    """C10: 1RM = 무게 × 36 / (37 - 렙수). 1~6렙에서 더 정확."""
    if reps >= 37:
        return weight_kg
    return round(weight_kg * 36.0 / (37 - reps), 1)


def c09_c10_smart_estimate(weight_kg: float, reps: int) -> float:
    """C09/C10 자동 분기: 저렙 Brzycki, 중렙 이상 Epley."""
    if reps <= 6:
        return c10_brzycki_1rm(weight_kg, reps)
    return c09_epley_1rm(weight_kg, reps)


# ============================================================================
# C11 — 세션 길이 가이드
# ----------------------------------------------------------------------------
# rules/C11.yaml | csv 30행
# 출처: NSCA Essentials
# URL : https://www.nsca.com/...  ★★☆
#
# 효율 세션 45~75분.
# ============================================================================
C11 = Citation(
    rule_id="C11", name="세션 길이 가이드",
    source="NSCA Essentials",
    url="https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/",
    confidence="★★☆",
)

def c11_exercises_per_session(available_minutes: int, goal: str) -> int:
    """C11: 가용 시간 → 운동 가짓수.

    경험적 매핑: 30~40분 4개, 45~60분 5~6개, 60~75분 7~8개.
    """
    if available_minutes < 40:
        return 4
    if available_minutes < 60:
        return 5
    if available_minutes < 75:
        return 7
    return 8


# ============================================================================
# C12 — 마지막 세트만 미달 (Top-set drop-off)
# ----------------------------------------------------------------------------
# rules/C12.yaml | csv 31행
# 출처: Rippetoe & Kilgore, Practical Programming 3rd ed.
# URL : https://startingstrength.com/article/training  ★★☆
# ============================================================================
C12 = Citation(rule_id="C12", name="Top-set drop-off",
               source="Rippetoe & Kilgore", url="https://startingstrength.com/article/training",
               confidence="★★☆")

def c12_handle_last_set_miss(set_results: list[int], target_reps: int) -> dict:
    """C12: [세트별 실제렙] + 목표렙 → 다음 세션 권고."""
    if not set_results:
        return {"권고": "유지", "메모": "데이터 없음"}
    misses = [i for i, r in enumerate(set_results) if r < target_reps]
    # 마지막 세트만 미달 + 미달폭 1~2렙
    if len(misses) == 1 and misses[0] == len(set_results) - 1 and (target_reps - set_results[-1]) <= 2:
        return {"권고": "무게유지_재시도", "메모": "정상 피로 — 다음 세션 동일 무게"}
    return {"권고": "재평가", "메모": "C13/C14 검사로 이동"}


# ============================================================================
# C13 — Stall 1회차 (모든 세트 미달)
# ----------------------------------------------------------------------------
# rules/C13.yaml | csv 32행
# 출처: Stronger By Science
# URL : https://www.strongerbyscience.com/reps-sets/  ★★☆
# ============================================================================
C13 = Citation(rule_id="C13", name="Stall 1회차",
               source="Greg Nuckols (SBS)", url="https://www.strongerbyscience.com/reps-sets/",
               confidence="★★☆")

def c13_handle_full_stall_first_time(consecutive_stall_weeks: int) -> dict:
    """C13: 1회차 stall → 무게 유지 1주. 그래도 미달이면 C14."""
    if consecutive_stall_weeks == 1:
        return {"권고": "1주_무게유지", "추가_체크": ["수면", "영양", "스트레스"]}
    return {"권고": "C14_적용", "메모": "Reset 필요"}


# ============================================================================
# C14 — 2주(3세션) 연속 미달 → Reset (-10%)
# ----------------------------------------------------------------------------
# rules/C14.yaml | csv 33행
# 출처: Rippetoe Reset 절차
# URL : https://startingstrength.com/article/the_first_three_questions  ★★★
# ============================================================================
C14 = Citation(rule_id="C14", name="Reset (-10%)",
               source="Rippetoe", url="https://startingstrength.com/article/the_first_three_questions",
               confidence="★★★")

def c14_reset(current_kg: float) -> float:
    """C14: 작업 무게 -10%."""
    return round(current_kg * 0.90, 1)


# ============================================================================
# C15 — Double Progression 미달 처리 보강
# ----------------------------------------------------------------------------
# rules/C15.yaml | csv 34행
# 출처: Helms M&S Pyramid Training 2nd ed.
# URL : https://muscleandstrengthpyramids.com/  ★★☆
# ============================================================================
C15 = Citation(rule_id="C15", name="Double Progression 미달 보강",
               source="Helms", url="https://muscleandstrengthpyramids.com/",
               confidence="★★☆")

def c15_handle_dp_miss(
    current_kg: float, last_session_reps: list[int],
    rep_range: tuple[int, int], lower_miss_count: int = 0,
) -> dict:
    """C15: 렙 레인지 하한 2세션 연속 미달 → -5~10%."""
    lower, upper = rep_range
    if lower_miss_count >= 2:
        new_kg = round(current_kg * 0.925, 1)   # 중간값 -7.5%
        return {"권고": "감량_재축적", "다음_무게": new_kg}
    if all(r >= upper for r in last_session_reps):
        return {"권고": "무게_+2.5%", "다음_무게": round(current_kg * 1.025, 1)}
    return {"권고": "유지_렙_누적", "다음_무게": current_kg}
