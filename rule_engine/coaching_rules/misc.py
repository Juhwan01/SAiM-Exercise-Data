"""실시간 코칭 — 기타 (7개): C07, P04, P05, K04, B04, I02, D04.

휴식 타이머·모빌리티·수분·볼륨 한계·템포 등 보조 룰 모음.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# C07 — 휴식 시간
# ----------------------------------------------------------------------------
# rules/C07.yaml | csv 26행
# 출처: Schoenfeld 2016 / de Salles
# URL : https://pubmed.ncbi.nlm.nih.gov/26605807/  ★★★
#
# 근력/파워 3~5분, 컴파운드 근비대 2~3분, 아이솔레이션 1~2분.
# ============================================================================
C07 = Citation(
    rule_id="C07", name="휴식 시간",
    source="Schoenfeld 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/26605807/",
    confidence="★★★",
)

def c07_rest_seconds(movement_type: str, goal: str) -> int:
    """C07: 운동 종류 + 목표 → 권장 휴식 초.

    movement_type: "compound" or "isolation"
    goal: "스트렝스"/"근육량 증가"/"벌크업"/"다이어트"/"건강증진"
    """
    if goal == "스트렝스":
        return 240    # 4분 (3~5분 중간값)
    if movement_type == "compound":
        return 150    # 2.5분 (컴파운드 근비대 2~3분)
    return 90         # 1.5분 (아이솔레이션 1~2분)


# ============================================================================
# P04 — 관절 모빌리티 워크
# ----------------------------------------------------------------------------
# rules/P04.yaml | csv 105행
# 출처: Page 2012
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/  ★★☆
#
# 고관절·발목·흉추 모빌리티 부족 = 컴파운드 폼 에러 주원인. 5~10분 동적 모빌리티.
# ============================================================================
P04 = Citation(
    rule_id="P04", name="관절 모빌리티 워크",
    source="Page 2012",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/",
    confidence="★★☆",
)

# 폼 에러 → 책임 관절(들) 매핑
_P04_ERROR_TO_JOINT = {
    "스쿼트_깊이부족": ["발목", "고관절"],
    "스쿼트_무릎내회전": ["고관절"],
    "스쿼트_골반윙크": ["고관절", "흉추"],
    "벤치_광배활성부족": ["흉추"],
    "데드_등말림": ["고관절", "흉추"],
    "OHP_바경로": ["흉추"],
}

def p04_mobility_prescription(form_error: str | None) -> dict:
    """P04: 폼 에러 입력 → 모빌리티 5~10분 처방."""
    if not form_error or form_error not in _P04_ERROR_TO_JOINT:
        return {"부위": [], "분": 0, "메모": "처방 없음"}
    joints = _P04_ERROR_TO_JOINT[form_error]
    return {
        "부위": joints,
        "분": 8,            # 5~10분 중간
        "메모": f"{', '.join(joints)} 동적 모빌리티 8분 (세션 전)",
    }


# ============================================================================
# P05 — 정적 스트레칭 회피 (워밍업 시)
# ----------------------------------------------------------------------------
# rules/P05.yaml | csv 106행
# 출처: Simic et al. 2013, Scand J Med Sci Sports
# URL : https://pubmed.ncbi.nlm.nih.gov/22316148/  ★★★
#
# 워밍업에서 ≥45~60초 정적 스트레칭은 최대 근력 평균 -5.4% 감소 → 동적으로 대체.
# ============================================================================
P05 = Citation(
    rule_id="P05", name="정적 스트레칭 회피 (워밍업 시)",
    source="Simic 2013 meta",
    url="https://pubmed.ncbi.nlm.nih.gov/22316148/",
    confidence="★★★",
)

def p05_warmup_check(stretch_seconds: int, kind: str = "static") -> dict:
    """P05: 사용자가 워밍업에 정적 스트레칭을 길게 넣으면 대체 권고."""
    if kind == "static" and stretch_seconds >= 45:
        return {
            "경고": True,
            "메모": "워밍업 정적 스트레칭 ≥45초 — 근력 평균 -5.4%",
            "대체": "레그스윙·아키바이크·동적 모빌리티로 교체",
        }
    return {"경고": False, "메모": None, "대체": None}


# ============================================================================
# K04 — 수분 가이드
# ----------------------------------------------------------------------------
# rules/K04.yaml | csv 78행
# 출처: ACSM Position Stand
# URL : https://www.acsm.org/docs/default-source/files-for-resource-library/exercise-fluid-replacement.pdf  ★★★
#
# 기본 30~35ml/kg + 운동 시간당 +500~1000ml. 2% 탈수에서 수행 저하.
# ============================================================================
K04 = Citation(
    rule_id="K04", name="수분 가이드",
    source="ACSM Position Stand",
    url="https://www.acsm.org/docs/default-source/files-for-resource-library/exercise-fluid-replacement.pdf",
    confidence="★★★",
)

def k04_hydration_target_ml(body_weight_kg: float, session_minutes: int) -> int:
    """K04: 일일 + 운동 시간 가산 = 권장 수분 ml.

    공식:
        기본 = 32.5ml/kg (30~35 중간)
        세션 추가 = (시간당 750ml) × (분 / 60)
    """
    base = body_weight_kg * 32.5
    session = (session_minutes / 60.0) * 750.0
    return int(round(base + session))


# ============================================================================
# B04 — MRV (회복 가능 최대 볼륨)
# ----------------------------------------------------------------------------
# rules/B04.yaml | csv 18행
# 출처: Israetel
# URL : https://propanefitness.com/maximum-recoverable-volume/  ★★★
#
# 근육군당 주 18~25+ 세트. 초과 시 오버트레이닝 신호.
# ============================================================================
B04 = Citation(
    rule_id="B04", name="MRV (회복 가능 최대 볼륨)",
    source="Israetel",
    url="https://propanefitness.com/maximum-recoverable-volume/",
    confidence="★★★",
)

# 근육군별 MRV 상한(세트/주, 보수적 디폴트=18)
_B04_MRV = {
    "가슴": 22, "등": 25, "어깨": 22, "이두": 26, "삼두": 24,
    "다리": 20, "둔근": 20, "햄스트링": 20, "복근": 25,
    "전완": 25, "기타": 18,
}

def b04_mrv_check(weekly_sets_by_muscle: dict[str, int]) -> dict:
    """B04: 근육군별 누적 세트 → MRV 초과 여부."""
    over: list[str] = []
    for muscle, sets in weekly_sets_by_muscle.items():
        cap = _B04_MRV.get(muscle, 18)
        if sets >= cap:
            over.append(f"{muscle}({sets}/{cap})")
    return {
        "초과_근육군": over,
        "권고_디로드": len(over) > 0,
    }


# ============================================================================
# I02 — Tempo Notation (메트로놈)
# ----------------------------------------------------------------------------
# rules/I02.yaml | csv 92행
# 출처: NSCA / SBS
# URL : https://www.strongerbyscience.com/tempo-for-muscle/  ★☆☆
#
# 4-숫자 표기(예: 3-1-1-0): 이심성-바닥-구심성-탑.
# ============================================================================
I02 = Citation(
    rule_id="I02", name="Tempo Notation",
    source="NSCA / SBS",
    url="https://www.strongerbyscience.com/tempo-for-muscle/",
    confidence="★☆☆",
)

def i02_parse_tempo(notation: str) -> tuple[int, int, int, int]:
    """I02: '3-1-1-0' 같은 표기 → (이심성, 바닥, 구심성, 탑) 초.

    공백/하이픈 모두 허용. 잘못된 입력은 디폴트 (2,0,1,0) 반환.
    """
    parts = notation.replace(" ", "").split("-")
    if len(parts) != 4:
        return (2, 0, 1, 0)
    try:
        a, b, c, d = (int(x) for x in parts)
        return (a, b, c, d)
    except ValueError:
        return (2, 0, 1, 0)


# ============================================================================
# D04 — Flexible DUP
# ----------------------------------------------------------------------------
# rules/D04.yaml | csv 32행
# 출처: McNamara & Stearne 2010
# URL : https://pubmed.ncbi.nlm.nih.gov/20042923/  ★★★
#
# 고정 순서 대신 사용자가 그날 컨디션 선택. 전통 DUP 와 동등 효과.
# ============================================================================
D04 = Citation(
    rule_id="D04", name="Flexible DUP",
    source="McNamara & Stearne 2010",
    url="https://pubmed.ncbi.nlm.nih.gov/20042923/",
    confidence="★★★",
)

def d04_recommend_session_type(condition: str) -> str:
    """D04: 사용자 입력 컨디션 → 오늘 세션 타입.

    condition: "좋음" | "보통" | "피곤"
    Returns: "근력" | "비대" | "회복"
    """
    if condition == "좋음":
        return "근력"
    if condition == "보통":
        return "비대"
    return "회복"
