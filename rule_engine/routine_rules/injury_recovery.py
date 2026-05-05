"""루틴 추천 — 부상 복귀 프로토콜 (5 룰): Q02, Q03, Q04, Q05, Q06.

부상 후 단계적 운동 복귀 처방. 적색기는 즉시 의료기관 의뢰.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# Q02 — 부상 복귀 단계
# ----------------------------------------------------------------------------
# rules/Q02.yaml | csv 97행
# 출처: BJSM Return-to-Sport
# URL : https://bjsm.bmj.com/content/50/14/853  ★★★
# ============================================================================
Q02 = Citation(
    rule_id="Q02", name="부상 복귀 단계",
    source="BJSM Return-to-Sport",
    url="https://bjsm.bmj.com/content/50/14/853",
    confidence="★★★",
)

def q02_return_phase(current_phase: int, pain_score: int) -> dict:
    """Q02: 단계별 진행 권고.

    1: 통증 0/10 휴식 → 2: ROM 회복 → 3: 무통 저강도 → 4: 점진 부하 → 5: 복귀
    각 단계 다음으로 진행하려면 통증 0 확인.
    """
    if pain_score > 0:
        return {"권고": f"{current_phase}단계 유지", "메모": f"통증 {pain_score}/10 — 0 도달까지 진행 X"}
    if current_phase < 5:
        return {"권고": f"{current_phase + 1}단계 진행", "메모": "무통 확인됨"}
    return {"권고": "Q03 복귀 기준 평가", "메모": "5단계 완료"}


# ============================================================================
# Q03 — 운동 복귀 기준
# ----------------------------------------------------------------------------
# rules/Q03.yaml | csv 98행
# 출처: Ardern 2016
# URL : https://bjsm.bmj.com/content/50/14/853  ★★★
# ============================================================================
Q03 = Citation(
    rule_id="Q03", name="운동 복귀 기준",
    source="Ardern 2016",
    url="https://bjsm.bmj.com/content/50/14/853",
    confidence="★★★",
)

def q03_can_return(
    rom_normal: bool,
    bilateral_strength_diff_pct: float,
    can_compound_painfree: bool,
    weeks_painfree: int,
) -> dict:
    """Q03: 4가지 충족 시 복귀 허용."""
    checklist = {
        "ROM_정상": rom_normal,
        "양측_근력차_<10%": bilateral_strength_diff_pct < 10.0,
        "무통_컴파운드_가능": can_compound_painfree,
        "2주_무통_유지": weeks_painfree >= 2,
    }
    return {"체크리스트": checklist, "복귀_가능": all(checklist.values())}


# ============================================================================
# Q04 — 요추 통증 단계별 프로토콜
# ----------------------------------------------------------------------------
# rules/Q04.yaml | csv 99행
# 출처: NICE NG59 + Foster 2018 Lancet
# URL : https://www.nice.org.uk/guidance/ng59  ★★★
# ============================================================================
Q04 = Citation(
    rule_id="Q04", name="요추 통증 프로토콜",
    source="NICE NG59 + Foster 2018",
    url="https://www.nice.org.uk/guidance/ng59",
    confidence="★★★",
)

_Q04_RED_FLAGS = (
    "다리_양측_저림", "안장마비", "괄약근_이상", "배뇨이상",
    "발열", "암_병력_동반_통증", "외상_후_통증",
)

def q04_low_back_protocol(
    days_since_onset: float,
    pain_nprs: int,
    red_flags: list[str] | None = None,
) -> dict:
    """Q04: 요추 통증 단계 + 권고.

    적색기 신호가 있으면 즉시 의료기관.
    """
    red_flags = red_flags or []
    matched = [f for f in red_flags if f in _Q04_RED_FLAGS]
    if matched:
        return {
            "단계": "적색기",
            "차단": True,
            "의뢰": "응급실 또는 신경외과",
            "이유": f"적색기: {', '.join(matched)}",
        }
    if days_since_onset < 3:
        return {
            "단계": "급성 0~3일",
            "허용": ["일상활동 유지", "골반 틸트", "McKenzie 신전 5×10"],
            "회피": ["데드리프트", "스쿼트", "침상안정"],
            "재시작_pct_1RM": 0,
        }
    if days_since_onset < 14:
        return {
            "단계": "아급성 3~14일",
            "허용": ["스트레칭", "근력", "유산소", "운동조절"],
            "메모": "도수치료는 운동의 보조로만",
            "재시작_pct_1RM": 0,
        }
    return {
        "단계": "복귀 14일~",
        "허용": ["글루트·코어 활성화 후 힙힌지", "데드/스쿼트는 1RM 30%부터"],
        "주_증가율_pct": 10.0,
        "재시작_pct_1RM": 30.0,
    }


# ============================================================================
# Q05 — 어깨 임핀지/RCRSP 프로토콜
# ----------------------------------------------------------------------------
# rules/Q05.yaml | csv 100행
# 출처: Lewis 2016 / Cools 2015
# URL : https://pubmed.ncbi.nlm.nih.gov/27083390/  ★★★
# ============================================================================
Q05 = Citation(
    rule_id="Q05", name="어깨 RCRSP 프로토콜",
    source="Lewis 2016 / Cools 2015",
    url="https://pubmed.ncbi.nlm.nih.gov/27083390/",
    confidence="★★★",
)

_Q05_RED_FLAGS = (
    "외상_후_거상_불가", "진행성_위약", "야간통_종괴_동반", "발열", "상지_신경학적_결손",
)

def q05_shoulder_protocol(
    days_since_onset: float,
    pain_nprs: int,
    red_flags: list[str] | None = None,
) -> dict:
    red_flags = red_flags or []
    matched = [f for f in red_flags if f in _Q05_RED_FLAGS]
    if matched:
        return {"단계": "적색기", "차단": True,
                "의뢰": "정형외과", "이유": f"{', '.join(matched)}"}
    if days_since_onset < 7:
        return {
            "단계": "급성 0~7일",
            "회피": ["오버헤드", "behind-the-neck", "딥 호리젠탈 어덕션"],
            "허용": ["진자운동", "견갑 후퇴/하강 활성"],
            "재시작_pct_1RM": 0,
        }
    if days_since_onset < 42:
        return {
            "단계": "아급성 1~6주",
            "처방": ["밴드 외회전 3×15", "서라투스 펀치", "로우", "후방관절낭 스트레칭"],
            "통증_NPRS_상한": 4,
        }
    return {
        "단계": "복귀 6주~",
        "허용": ["벤치/OHP/풀업 1RM 30%부터"],
        "주_증가율_pct": 10.0,
        "오버헤드_조건": "통증 0/10 + 외회전 좌우차 <10%",
        "재시작_pct_1RM": 30.0,
    }


# ============================================================================
# Q06 — 무릎 PFPS(슬개대퇴 통증) 프로토콜
# ----------------------------------------------------------------------------
# rules/Q06.yaml | csv 101행
# 출처: Powers 2017 BJSM + Crossley 2016 + Barton 2015
# URL : https://pubmed.ncbi.nlm.nih.gov/29109118/  ★★★
# ============================================================================
Q06 = Citation(
    rule_id="Q06", name="무릎 PFPS 프로토콜",
    source="Powers 2017 / Crossley 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/29109118/",
    confidence="★★★",
)

_Q06_RED_FLAGS = ("외상_후_부종", "관절잠김", "이탈감", "체중부하_불가", "발적", "발열")

def q06_pfps_protocol(
    days_since_onset: float,
    pain_nprs: int,
    red_flags: list[str] | None = None,
) -> dict:
    red_flags = red_flags or []
    matched = [f for f in red_flags if f in _Q06_RED_FLAGS]
    if matched:
        return {"단계": "적색기", "차단": True,
                "의뢰": "정형외과", "이유": f"{', '.join(matched)}"}
    if days_since_onset < 14:
        return {
            "단계": "급성 0~2주",
            "회피": ["딥 스쿼트", "런지", "계단 내려오기", "오픈체인 레그익스텐션 90→0°"],
            "허용": ["활동 수정", "교육"],
            "재시작_pct_1RM": 0,
        }
    if days_since_onset < 42:
        return {
            "단계": "아급성 2~6주",
            "처방": [
                "고관절: 클램쉘 3×15", "사이드 라잉 힙 어브덕션 3×15",
                "대퇴사두: 미니 스쿼트 0~45° 3×10", "레그프레스 짧은 ROM 1RM 30%",
            ],
            "통증_NPRS_상한": 3,
            "재시작_pct_1RM": 30.0,
        }
    return {
        "단계": "복귀 6주~",
        "허용": ["스쿼트/런지 통증 한도 내 점진"],
        "주_증가율_pct": 10.0,
        "풀스쿼트_조건": "통증 0/10 + 편측 근력차 <10%",
        "재시작_pct_1RM": 30.0,
    }
