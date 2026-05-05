"""루틴 추천 — 영양 (4 룰): K19, K20, K21, K22.

BMR/TDEE 계산. 온보딩 1회, 체중 변동 시 재계산.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# K19 — Mifflin-St Jeor BMR 공식 (1순위)
# ----------------------------------------------------------------------------
# rules/K19.yaml | csv 91행
# 출처: Mifflin & St Jeor 1990 (Am J Clin Nutr 51:241-7)
# URL : https://pubmed.ncbi.nlm.nih.gov/2305711/  ★★★
#
# 한줄설명 그대로:
#   남: BMR = 10×W(kg) + 6.25×H(cm) - 5×나이 + 5
#   여: 동일식 -161
# 비만·정상 모두 ±10% 오차로 가장 정확. 1순위 권장식.
# ============================================================================
K19 = Citation(
    rule_id="K19", name="Mifflin-St Jeor BMR (1순위)",
    source="Mifflin & St Jeor 1990",
    url="https://pubmed.ncbi.nlm.nih.gov/2305711/",
    confidence="★★★",
)

def k19_bmr_mifflin(sex: str, weight_kg: float, height_cm: float, age_y: int) -> int:
    """K19: BMR(kcal/일). 성별 'sex' 는 '남' / '여'."""
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age_y
    bmr = base + (5 if sex == "남" else -161)
    return int(round(bmr))


# ============================================================================
# K20 — Katch-McArdle BMR 공식 (체지방률 알 때)
# ----------------------------------------------------------------------------
# rules/K20.yaml | csv 92행
# 출처: Aragon et al. 2017 ISSN Position Stand
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/  ★★★
#
# BMR = 370 + (21.6 × LBM kg)
# LBM = 체중 × (1 - 체지방률)
# ============================================================================
K20 = Citation(
    rule_id="K20", name="Katch-McArdle BMR (체지방률 기반)",
    source="Aragon ISSN 2017",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/",
    confidence="★★★",
)

def k20_bmr_katch(weight_kg: float, body_fat_pct: float) -> int:
    """K20: 체지방률 알면 더 정확. body_fat_pct 는 0~100 (예: 18.5)."""
    lbm = weight_kg * (1 - body_fat_pct / 100.0)
    bmr = 370 + 21.6 * lbm
    return int(round(bmr))


# ============================================================================
# K21 — 활동계수(PAL) 표 → TDEE
# ----------------------------------------------------------------------------
# rules/K21.yaml | csv 93행
# 출처: FAO/WHO/UNU 2001 Human Energy Requirements
# URL : https://www.fao.org/4/y5686e/y5686e07.htm  ★★★
#
# TDEE = BMR × PAL
# 좌식 1.2 / 가벼움 1.375 / 보통 1.55 / 활발 1.725 / 매우 활발 1.9
# ============================================================================
K21 = Citation(
    rule_id="K21", name="활동계수(PAL) → TDEE",
    source="FAO/WHO/UNU 2001",
    url="https://www.fao.org/4/y5686e/y5686e07.htm",
    confidence="★★★",
)

PAL = {
    "좌식":      1.2,
    "가벼움":    1.375,
    "보통":      1.55,
    "활발":      1.725,
    "매우_활발": 1.9,
}

def k21_tdee(bmr_kcal: int, activity_category: str) -> int:
    """K21: TDEE = BMR × PAL."""
    pal = PAL.get(activity_category, 1.375)
    return int(round(bmr_kcal * pal))


# ============================================================================
# K22 — 활동 카테고리 한국 사용자 매핑
# ----------------------------------------------------------------------------
# rules/K22.yaml | csv 94행
# 출처: FAO/WHO/UNU 2001 PAL 범위
# URL : https://www.fao.org/4/y5686e/y5686e07.htm  ★★☆
#
# 한국 직장인 다수 = 좌식 + 주3회 헬스 → 보수적 1.375 권장
# ============================================================================
K22 = Citation(
    rule_id="K22", name="활동 카테고리 한국 매핑",
    source="FAO PAL + 자체 매핑",
    url="https://www.fao.org/4/y5686e/y5686e07.htm",
    confidence="★★☆",
)

def k22_classify_activity(job_type: str, exercise_freq: str) -> str:
    """K22: 직업 + 주당 운동 빈도 → 5단계 카테고리.

    Args:
        job_type: '사무직' / '서비스' / '육체노동'
        exercise_freq: '없음' / '주1~3회' / '주3~5회' / '주6~7회'
    """
    # 육체노동 + 격한 운동 → 매우 활발
    if job_type == "육체노동" and exercise_freq in ("주3~5회", "주6~7회"):
        return "매우_활발"
    # 격한 운동 단독
    if exercise_freq == "주6~7회":
        return "활발"
    # 보통 활동
    if exercise_freq == "주3~5회":
        return "보통"
    # 가벼운 활동 (한국 직장인 디폴트, 룰 카드: 보수적 1.375)
    if exercise_freq == "주1~3회":
        return "가벼움"
    # 사무직 + 운동 없음
    return "좌식"
