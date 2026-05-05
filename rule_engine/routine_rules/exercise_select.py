"""루틴 추천 — 운동 선택 (10 룰): F05, J01-J05, J07, E14, E17, I03.

운동 종목 풀, 대체 운동, 비율, ROM/그립, 운동 순서.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# F05 — SFR (자극/피로 비율)
# ----------------------------------------------------------------------------
# rules/F05.yaml | csv 73행
# 출처: Israetel / RP
# URL : https://www.strongerbyscience.com/exercise-selection/  ★★☆
#
# 컴파운드 SFR 보통, 머신/아이솔 SFR 우수.
# ============================================================================
F05 = Citation(
    rule_id="F05", name="SFR (자극/피로 비율)",
    source="Israetel / RP",
    url="https://www.strongerbyscience.com/exercise-selection/",
    confidence="★★☆",
)

# 운동 ID → SFR 점수 (1=낮음, 5=높음). 대체 추천 시 가중치로 사용.
_F05_SFR = {
    "백스쿼트": 3, "프론트스쿼트": 3, "레그프레스": 5, "레그익스텐션": 5,
    "벤치프레스": 3, "덤벨프레스": 4, "푸시업": 5, "체스트프레스": 5,
    "데드리프트": 2, "RDL": 3, "힙쓰러스트": 5,
    "OHP": 3, "덤벨숄더프레스": 4, "사이드레터럴": 5,
    "풀업": 3, "랫풀다운": 5, "케이블로우": 5,
    "바벨로우": 3, "체스트서포트로우": 5,
}

def f05_sfr(movement: str) -> int:
    """F05: 운동의 SFR 점수 (1~5). 부상·피로 시 높은 값을 우선."""
    return _F05_SFR.get(movement, 3)


# ============================================================================
# J01 — 부상별 대체 운동 매트릭스
# ----------------------------------------------------------------------------
# rules/J01.yaml | csv 87행
# 출처: NASM / Israetel
# URL : https://www.strongerbyscience.com/exercise-selection/  ★★☆
# ============================================================================
J01 = Citation(
    rule_id="J01", name="부상별 대체 운동",
    source="NASM / Israetel",
    url="https://www.strongerbyscience.com/exercise-selection/",
    confidence="★★☆",
)

_J01_INJURY_TO_ALT = {
    "무릎":   {"백스쿼트": ["레그프레스", "벨트스쿼트", "스플릿스쿼트"]},
    "어깨":   {"벤치프레스": ["푸시업", "덤벨프레스", "랜드마인프레스"]},
    "허리":   {"데드리프트": ["힙쓰러스트", "RDL", "백 익스텐션"]},
    "손목":   {"백스쿼트": ["safety bar 스쿼트", "프론트스쿼트(크로스암)"]},
    "팔꿈치": {"벤치프레스": ["체스트프레스 머신", "덤벨플라이"]},
}

def j01_alternatives(injury_site: str, movement: str) -> list[str]:
    """J01: 부상 부위 + 회피할 운동 → 대체 운동 후보."""
    return _J01_INJURY_TO_ALT.get(injury_site, {}).get(movement, [])


# ============================================================================
# J02 — 장비별 대체 운동
# ----------------------------------------------------------------------------
# rules/J02.yaml | csv 88행
# 출처: Free Exercise DB / wger
# URL : https://github.com/yuhonas/free-exercise-db  ★★★
# ============================================================================
J02 = Citation(
    rule_id="J02", name="장비별 대체 운동",
    source="Free Exercise DB",
    url="https://github.com/yuhonas/free-exercise-db",
    confidence="★★★",
)

# 운동 → 장비 별 대체
_J02_EQUIPMENT_ALT = {
    "백스쿼트":   {"덤벨": "덤벨고블릿스쿼트", "맨몸": "에어스쿼트", "케틀벨": "케틀벨스쿼트"},
    "벤치프레스": {"덤벨": "덤벨벤치프레스",   "맨몸": "푸시업", "밴드": "밴드 체스트프레스"},
    "데드리프트": {"덤벨": "덤벨데드리프트",   "맨몸": "굿모닝(맨몸)", "케틀벨": "케틀벨스윙"},
    "OHP":        {"덤벨": "덤벨숄더프레스",   "맨몸": "파이크 푸시업", "밴드": "밴드 OHP"},
    "바벨로우":   {"덤벨": "덤벨로우",          "맨몸": "인버티드로우", "밴드": "밴드 시티드로우"},
}

def j02_filter_by_equipment(movement: str, available: list[str]) -> str:
    """J02: 사용자 장비 환경에 맞는 대체 운동.

    바벨이 있으면 원래 운동 그대로 반환.
    """
    if "바벨" in available:
        return movement
    fallback = _J02_EQUIPMENT_ALT.get(movement, {})
    for eq in ("덤벨", "케틀벨", "밴드", "맨몸"):
        if eq in available and eq in fallback:
            return fallback[eq]
    return movement


# ============================================================================
# J03 — 자유중량 vs 머신
# ----------------------------------------------------------------------------
# rules/J03.yaml | csv 89행
# 출처: Schwanbeck 2020 / Haugen 2023
# URL : https://pubmed.ncbi.nlm.nih.gov/32358310/  ★★★
# ============================================================================
J03 = Citation(
    rule_id="J03", name="자유중량 vs 머신",
    source="Schwanbeck 2020",
    url="https://pubmed.ncbi.nlm.nih.gov/32358310/",
    confidence="★★★",
)

def j03_freeweight_machine_ratio(level: str, goal: str, prefer_safety: bool = False) -> tuple[int, int]:
    """J03: (자유중량 %, 머신 %) — 합계 100.

    초보+안전 선호 → 머신 비중↑
    근력 목표 → 자유중량↑
    """
    if level == "초보" or prefer_safety:
        return (40, 60)
    if goal == "스트렝스":
        return (80, 20)
    return (60, 40)


# ============================================================================
# J04 — 편측 vs 양측 운동
# ----------------------------------------------------------------------------
# rules/J04.yaml | csv 90행
# 출처: McCurdy 2005 / NSCA
# URL : https://pubmed.ncbi.nlm.nih.gov/15705051/  ★★☆
# ============================================================================
J04 = Citation(
    rule_id="J04", name="편측 vs 양측",
    source="McCurdy 2005 / NSCA",
    url="https://pubmed.ncbi.nlm.nih.gov/15705051/",
    confidence="★★☆",
)

def j04_unilateral_ratio(asymmetry_pct: float | None) -> tuple[int, int]:
    """J04: (양측 %, 편측 %) 비율.

    좌우 불균형 ≥10%면 편측 비중 ↑
    """
    if asymmetry_pct is not None and asymmetry_pct >= 10.0:
        return (50, 50)
    return (75, 25)


# ============================================================================
# J05 — 컴파운드:아이솔 비율
# ----------------------------------------------------------------------------
# rules/J05.yaml | csv 91행
# 출처: Israetel / NSCA
# URL : https://www.strongerbyscience.com/exercise-selection/  ★★☆
# ============================================================================
J05 = Citation(
    rule_id="J05", name="컴파운드:아이솔 비율",
    source="Israetel / NSCA",
    url="https://www.strongerbyscience.com/exercise-selection/",
    confidence="★★☆",
)

def j05_compound_isolation_ratio(level: str) -> tuple[int, int]:
    """J05: (컴파운드 %, 아이솔 %) 비율 — 룰 카드 그대로."""
    return {"초보": (70, 30), "중급": (60, 40), "고급": (50, 50)}.get(level, (60, 40))


# ============================================================================
# J07 — 근육군 매핑 (primary/secondary)
# ----------------------------------------------------------------------------
# rules/J07.yaml | csv 93행
# 출처: wger / Free Exercise DB
# URL : https://wger.de/en/software/api  ★★★
# ============================================================================
J07 = Citation(
    rule_id="J07", name="근육군 매핑",
    source="wger / Free Exercise DB",
    url="https://wger.de/en/software/api",
    confidence="★★★",
)

# 운동 → {primary: [...], secondary: [...]}
_J07_MAP = {
    "백스쿼트":     {"primary": ["다리", "둔근"], "secondary": ["복근", "햄스트링"]},
    "프론트스쿼트": {"primary": ["다리"],         "secondary": ["둔근", "복근"]},
    "벤치프레스":   {"primary": ["가슴"],         "secondary": ["삼두", "어깨"]},
    "덤벨프레스":   {"primary": ["가슴"],         "secondary": ["삼두", "어깨"]},
    "데드리프트":   {"primary": ["햄스트링", "둔근", "등"], "secondary": ["전완", "복근"]},
    "RDL":          {"primary": ["햄스트링", "둔근"], "secondary": ["등", "전완"]},
    "OHP":          {"primary": ["어깨"],         "secondary": ["삼두", "복근"]},
    "풀업":         {"primary": ["등"],           "secondary": ["이두", "전완"]},
    "바벨로우":     {"primary": ["등"],           "secondary": ["이두", "전완"]},
    "사이드레터럴": {"primary": ["어깨"],         "secondary": []},
    "이두컬":       {"primary": ["이두"],         "secondary": ["전완"]},
    "삼두익스텐션": {"primary": ["삼두"],         "secondary": []},
}

def j07_volume_weights(movement: str) -> dict[str, float]:
    """J07: 운동의 근육군별 가중치 (primary=1.0, secondary=0.5)."""
    info = _J07_MAP.get(movement)
    if not info:
        return {}
    weights: dict[str, float] = {}
    for m in info["primary"]:
        weights[m] = 1.0
    for m in info["secondary"]:
        weights[m] = max(weights.get(m, 0), 0.5)
    return weights


# ============================================================================
# E14 — 가동범위 (ROM) 기준 (추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/E14.yaml | csv 64행
# 출처: Pedrosa 2022
# URL : https://pubmed.ncbi.nlm.nih.gov/33977835/  ★★★
# ============================================================================
E14 = Citation(
    rule_id="E14", name="ROM 기준",
    source="Pedrosa 2022",
    url="https://pubmed.ncbi.nlm.nih.gov/33977835/",
    confidence="★★★",
)

def e14_rom_default() -> str:
    """E14: 디폴트 처방 — 풀ROM 우선, 신장강조 부분반복은 옵션."""
    return "풀ROM 우선 (신장강조 부분반복은 옵션)"


# ============================================================================
# E17 — 그립 너비/유형 (추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/E17.yaml | csv 67행
# 출처: PowerliftingTechnique / SBS
# URL : https://startingstrength.com/article/grip-width-on-the-bench-press  ★★☆
# ============================================================================
E17 = Citation(
    rule_id="E17", name="그립 너비/유형",
    source="PowerliftingTechnique / SBS",
    url="https://startingstrength.com/article/grip-width-on-the-bench-press",
    confidence="★★☆",
)

def e17_grip_recommendations() -> dict:
    """E17: 운동별 권장 그립."""
    return {
        "벤치프레스": "어깨너비의 1.5배 (오버그립)",
        "데드리프트": "어깨너비, 고중량은 후크그립",
        "풀업_광배강조": "와이드 오버그립",
        "풀업_이두강조": "내로우/언더그립",
    }


# ============================================================================
# I03 — 운동 순서 (컴파운드 우선)
# ----------------------------------------------------------------------------
# rules/I03.yaml | csv 93행
# 출처: NSCA Essentials
# URL : https://www.strongerbyscience.com/exercise-order-video/  ★★★
# ============================================================================
I03 = Citation(
    rule_id="I03", name="운동 순서 (컴파운드 우선)",
    source="NSCA Essentials",
    url="https://www.strongerbyscience.com/exercise-order-video/",
    confidence="★★★",
)

# 운동 → 순서 가중치 (작을수록 앞)
_I03_ORDER = {
    "백스쿼트": 1, "데드리프트": 1, "벤치프레스": 1, "OHP": 1,
    "프론트스쿼트": 2, "RDL": 2, "덤벨프레스": 2, "바벨로우": 2,
    "풀업": 2, "힙쓰러스트": 3,
    "레그프레스": 4, "체스트프레스": 4, "랫풀다운": 4,
    "사이드레터럴": 5, "이두컬": 5, "삼두익스텐션": 5, "레그익스텐션": 5,
}

def i03_order_session(movements: list[str]) -> list[str]:
    """I03: 세션 운동 목록을 컴파운드→보조→아이솔 순서로 정렬."""
    return sorted(movements, key=lambda m: _I03_ORDER.get(m, 9))
