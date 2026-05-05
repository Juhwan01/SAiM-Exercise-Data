"""루틴 추천 — 워밍업·스트레칭 (11 룰): I05, I06, I07, I08, P01, P02, P03, P04, P05, E02, E09.

세션 시작 시퀀스. 일반 워밍업 → 모빌리티 → 종목별 워크업.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# I05 — 일반 워밍업 (전신 체온 상승)
# ----------------------------------------------------------------------------
# rules/I05.yaml | csv 95행
# 출처: NSCA, Introduction to Dynamic Warm-Up
# URL : https://www.nsca.com/education/articles/kinetic-select/introduction-to-dynamic-warm-up/  ★★★
# ============================================================================
I05 = Citation(
    rule_id="I05", name="일반 워밍업",
    source="NSCA Dynamic Warm-Up",
    url="https://www.nsca.com/education/articles/kinetic-select/introduction-to-dynamic-warm-up/",
    confidence="★★★",
)

def i05_general_warmup(available_minutes: int) -> str:
    """I05: 본 운동 전 5~10분 저강도 유산소."""
    minutes = max(5, min(10, available_minutes // 6))
    return f"{minutes}분 저강도 유산소(조깅·자전거) — 땀 살짝 날 정도"


# ============================================================================
# I06 — 특이적 워밍업 (컴파운드 워크업)
# ----------------------------------------------------------------------------
# rules/I06.yaml | csv 96행
# 출처: Mark Rippetoe, Starting Strength
# URL : https://startingstrength.com/training/warmup  ★★☆
# ============================================================================
I06 = Citation(
    rule_id="I06", name="컴파운드 워크업",
    source="Rippetoe SS",
    url="https://startingstrength.com/training/warmup",
    confidence="★★☆",
)

def i06_compound_warmup(workset_kg: float, bar_kg: float = 20.0) -> list[dict]:
    """I06: 빈 봉 ×5×2세트 → 40%×5 → 60%×3 → 80%×2 → 본 세트."""
    if workset_kg <= bar_kg:
        return [{"무게": bar_kg, "렙": 5, "세트": 2}]
    return [
        {"무게": bar_kg,                       "렙": 5, "세트": 2},
        {"무게": round(workset_kg * 0.4, 1),  "렙": 5, "세트": 1},
        {"무게": round(workset_kg * 0.6, 1),  "렙": 3, "세트": 1},
        {"무게": round(workset_kg * 0.8, 1),  "렙": 2, "세트": 1},
    ]


# ============================================================================
# I07 — 특이적 워밍업 (아이솔/머신)
# ----------------------------------------------------------------------------
# rules/I07.yaml | csv 97행
# 출처: Greg Nuckols, Stronger by Science
# URL : https://www.strongerbyscience.com/warm-up/  ★★☆
# ============================================================================
I07 = Citation(
    rule_id="I07", name="아이솔/머신 워밍업",
    source="Nuckols (SBS)",
    url="https://www.strongerbyscience.com/warm-up/",
    confidence="★★☆",
)

def i07_isolation_warmup(workset_kg: float) -> list[dict]:
    """I07: 50%×8, 80%×3 (1~2 워크업 세트면 충분)."""
    return [
        {"무게": round(workset_kg * 0.5, 1), "렙": 8, "세트": 1},
        {"무게": round(workset_kg * 0.8, 1), "렙": 3, "세트": 1},
    ]


# ============================================================================
# I08 — 시간 부족 시 무거운 워크업 우선
# ----------------------------------------------------------------------------
# rules/I08.yaml | csv 98행
# 출처: Greg Nuckols, Stronger by Science
# URL : https://www.strongerbyscience.com/heavier-warm-ups/  ★★☆
# ============================================================================
I08 = Citation(
    rule_id="I08", name="시간 부족 시 무거운 워크업",
    source="Nuckols (SBS)",
    url="https://www.strongerbyscience.com/heavier-warm-ups/",
    confidence="★★☆",
)

def i08_time_compressed_warmup(workset_kg: float) -> list[dict]:
    """I08: 시간 부족하면 80%×3~5 1세트만 → 본 세트."""
    return [{"무게": round(workset_kg * 0.8, 1), "렙": 4, "세트": 1}]


# ============================================================================
# P01 — 운동 전 정/동적 스트레칭
# ----------------------------------------------------------------------------
# rules/P01.yaml | csv 102행
# 출처: Behm 2016 메타분석
# URL : https://pubmed.ncbi.nlm.nih.gov/26642915/  ★★★
# ============================================================================
P01 = Citation(
    rule_id="P01", name="운동 전 스트레칭",
    source="Behm 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/26642915/",
    confidence="★★★",
)

def p01_warmup_stretch_policy() -> dict:
    return {
        "운동_전_정적": "회피 (60s+ 정적 스트레칭은 근력↓)",
        "운동_전_동적": "권장",
        "정적_타이밍": "운동 후 또는 별도 세션",
    }


# ============================================================================
# P02 — PNF 스트레칭
# ----------------------------------------------------------------------------
# rules/P02.yaml | csv 103행
# 출처: Hindle 2012
# URL : https://pubmed.ncbi.nlm.nih.gov/23487249/  ★★☆
# ============================================================================
P02 = Citation(
    rule_id="P02", name="PNF 스트레칭",
    source="Hindle 2012",
    url="https://pubmed.ncbi.nlm.nih.gov/23487249/",
    confidence="★★☆",
)

def p02_pnf_for(target_area: str) -> dict:
    return {
        "기법": "Contract-relax-contract",
        "용도": "정적/동적보다 ROM 향상 우월",
        "필요": "파트너 (또는 밴드 사용 셀프 PNF)",
        "부위": target_area,
    }


# ============================================================================
# P03 — 자가근막이완 (SMR/폼롤러)
# ----------------------------------------------------------------------------
# rules/P03.yaml | csv 104행
# 출처: Wiewelhove 2019
# URL : https://www.frontiersin.org/articles/10.3389/fphys.2019.00376/full  ★★★
# ============================================================================
P03 = Citation(
    rule_id="P03", name="자가근막이완 (SMR)",
    source="Wiewelhove 2019",
    url="https://www.frontiersin.org/articles/10.3389/fphys.2019.00376/full",
    confidence="★★★",
)

def p03_smr_dose() -> dict:
    return {"부위당_초": (30, 60), "타이밍": ["세션 전", "세션 후"]}


# ============================================================================
# P04 — 관절 모빌리티 워크
# ----------------------------------------------------------------------------
# rules/P04.yaml | csv 105행
# 출처: Page 2012
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/  ★★☆
# ============================================================================
P04 = Citation(
    rule_id="P04", name="관절 모빌리티",
    source="Page 2012",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/",
    confidence="★★☆",
)

def p04_default_mobility() -> list[str]:
    """P04: 컴파운드 폼 에러 주원인 — 고관절·발목·흉추 모빌리티 5~10분."""
    return ["고관절 모빌리티 3분", "발목 모빌리티 2분", "흉추 모빌리티 3분"]


# ============================================================================
# P05 — 정적 스트레칭 회피 (워밍업)
# ----------------------------------------------------------------------------
# rules/P05.yaml | csv 106행
# 출처: Simic et al. 2013
# URL : https://pubmed.ncbi.nlm.nih.gov/22316148/  ★★★
# ============================================================================
P05 = Citation(
    rule_id="P05", name="정적 스트레칭 회피",
    source="Simic 2013 meta",
    url="https://pubmed.ncbi.nlm.nih.gov/22316148/",
    confidence="★★★",
)

def p05_warmup_static_warning() -> str:
    return "워밍업 정적 스트레칭 ≥45초 회피 — 최대 근력 평균 -5.4% 감소"


# ============================================================================
# E02 — Load-Velocity Profile (추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/E02.yaml | csv 52행
# 출처: Vitruve
# URL : https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/  ★★☆
# ============================================================================
E02 = Citation(
    rule_id="E02", name="Load-Velocity Profile",
    source="Vitruve",
    url="https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/",
    confidence="★★☆",
)

def e02_session_start_calibration() -> dict:
    """E02: 세션 시작 시 워밍업 속도로 그날 1RM 추정 → 무게 자동 보정."""
    return {
        "절차": "워밍업 세트 무게/속도 측정 → 선형회귀 → 그날 1RM 추정",
        "사용": "감지된 1RM 변동에 맞춰 본 세트 무게 ±5% 자동 보정",
    }


# ============================================================================
# E09 — RAMP 워밍업 프로토콜
# ----------------------------------------------------------------------------
# rules/E09.yaml | csv 59행
# 출처: Ian Jeffreys 2007
# URL : https://humankinetics.me/2019/03/04/what-is-the-ramp-warm-up/  ★★★
# ============================================================================
E09 = Citation(
    rule_id="E09", name="RAMP 워밍업",
    source="Ian Jeffreys 2007",
    url="https://humankinetics.me/2019/03/04/what-is-the-ramp-warm-up/",
    confidence="★★★",
)

def e09_ramp_sequence(workset_kg: float, bar_kg: float = 20.0) -> dict:
    """E09: R(심박↑)-A(타깃 활성)-M(가동성)-P(종목 점증세트)."""
    return {
        "R_심박": "5분 저강도 유산소",
        "A_활성": "타깃 근육 점증 활성 (밴드·체중 운동 2~3종)",
        "M_모빌리티": "운동별 관절 모빌리티 3~5분",
        "P_점증세트": [
            {"무게": round(workset_kg * 0.5, 1), "렙": 5, "세트": 1},
            {"무게": round(workset_kg * 0.7, 1), "렙": 3, "세트": 1},
            {"무게": round(workset_kg * 0.85, 1), "렙": 2, "세트": 1},
        ],
        "주의": "정적 스트레칭 회피 (P05 가드)",
    }
