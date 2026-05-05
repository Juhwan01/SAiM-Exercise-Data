"""실시간 코칭 — 안전 게이트 (7개): Q01, L05, L06, L07, L08, K06, K08.

이 모듈의 함수는 다른 룰보다 **먼저** 실행된다. 차단 신호가 나오면 진입 함수
`realtime_coaching` 은 즉시 결과에 `차단됨=True` 를 박고 반환한다.

만성질환 4종(L05-L08)은 모두 한국·국제 가이드라인의 적색기(즉시 의뢰) 트리거를
포함한다. 출처는 ACSM/ADA/대한고혈압학회/OARSI/ACR 등 공식 가이드라인이다.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# Q01 — 급성 부상 처치 (PEACE & LOVE)
# ----------------------------------------------------------------------------
# rules/Q01.yaml | csv 96행
# 출처: Dubois 2019 BJSM
# URL : https://bjsm.bmj.com/content/54/2/72  ★★★
#
# 급성기(0~3일): Protect · Elevate · Avoid anti-inflam · Compress · Educate
# 후속        : Load · Optimism · Vascular · Exercise
# RICE 는 구식 (Dubois 2019 가 권고 변경).
# ============================================================================
Q01 = Citation(
    rule_id="Q01", name="급성 부상 처치 (PEACE & LOVE)",
    source="Dubois 2019 BJSM",
    url="https://bjsm.bmj.com/content/54/2/72",
    confidence="★★★",
)

def q01_acute_injury_protocol(hours_since_injury: float) -> dict:
    """Q01: 부상 후 경과 시간에 따른 단계별 가이드.

    Returns:
        {"단계": "PEACE" or "LOVE", "행동": [...], "차단": bool}
    """
    # 급성기 = 발생 후 3일(72h) 이내
    if hours_since_injury < 72:
        return {
            "단계": "PEACE (급성기 0~3일)",
            "행동": [
                "P  Protect — 통증 유발 동작 회피",
                "E  Elevate — 부위 거상",
                "A  Avoid anti-inflam — 초기 NSAIDs 자제",
                "C  Compress — 압박",
                "E  Educate — 자연 회복 흐름 설명",
            ],
            "차단": True,    # 운동 중단 권고
        }
    return {
        "단계": "LOVE (3일 후)",
        "행동": [
            "L  Load — 점진적 부하",
            "O  Optimism — 회복 신뢰",
            "V  Vascular — 가벼운 유산소",
            "E  Exercise — 점진 재개",
        ],
        "차단": False,
    }


# ============================================================================
# L05 — 제2형 당뇨 운동 처방
# ----------------------------------------------------------------------------
# rules/L05.yaml | csv 119행
# 출처: ACSM Guidelines 11th ed (2022) + ADA Standards of Care 2024 + 대한당뇨병학회 2023
# URL : https://www.acsm.org/education-resources/books/guidelines-exercise-testing-prescription/  ★★★
#
# 룰 카드 한줄설명에 적색기 트리거가 명시돼 있다:
#   증식성 망막증 → 고강도/Valsalva/점프/머리숙임 금지·안과 의뢰
#   자율신경병증·심한 신경병증·족부궤양 → 체중부하 운동 제한·내분비내과 의뢰
#   공복혈당>250 mg/dL + 케톤 양성 → 운동 보류
#   저혈당 빈발 또는 무자각성 저혈당 → 내분비내과 상담
# ============================================================================
L05 = Citation(
    rule_id="L05", name="제2형 당뇨 운동 처방",
    source="ACSM 2022 + ADA 2024 + 대한당뇨병학회 2023",
    url="https://www.acsm.org/education-resources/books/guidelines-exercise-testing-prescription/",
    confidence="★★★",
)

def l05_diabetes_gate(
    has_diabetes: bool,
    medications: list[str] | None = None,
    complications: list[str] | None = None,   # ["증식성_망막증", "자율신경병증", "신경병증_심", "족부궤양"]
    fasting_glucose_mgdl: float | None = None,
    ketone_positive: bool = False,
    pre_exercise_glucose_mgdl: float | None = None,
) -> dict:
    """L05: 당뇨 사용자에 대한 안전 게이트.

    Returns:
        {"차단": bool, "이유": str|None, "의뢰": str|None, "주의": [...]}
    """
    out: dict = {"차단": False, "이유": None, "의뢰": None, "주의": []}
    if not has_diabetes:
        return out
    medications = medications or []
    complications = complications or []

    # 적색기: 공복혈당>250 + 케톤 양성 → 운동 보류
    if fasting_glucose_mgdl is not None and fasting_glucose_mgdl > 250 and ketone_positive:
        out.update(차단=True, 이유="공복혈당>250 + 케톤(+) — 운동 보류",
                   의뢰="내분비내과 즉시 상담")
        return out

    # 적색기: 증식성 망막증 → 고강도/Valsalva/점프/머리숙임 금지
    if "증식성_망막증" in complications:
        out["주의"].append("고강도·Valsalva·점프·머리숙임 동작 금지")
        out["의뢰"] = "안과 의뢰"

    # 적색기: 자율신경/심한 신경병증/족부궤양 → 체중부하 제한
    if any(c in complications for c in ("자율신경병증", "신경병증_심", "족부궤양")):
        out["주의"].append("체중부하 운동 제한 (좌식 운동 우선)")
        out["의뢰"] = (out["의뢰"] + " + 내분비내과") if out["의뢰"] else "내분비내과"

    # 인슐린/SU 복용자 + 운동 전 혈당<100 → 탄수 15g 보충
    on_insulin_or_su = any(m in medications for m in ("인슐린", "글리메피리드", "글리피지드", "SU"))
    if on_insulin_or_su and pre_exercise_glucose_mgdl is not None and pre_exercise_glucose_mgdl < 100:
        out["주의"].append("운동 전 혈당<100 — 탄수 15g(바나나 1/2개) 보충")

    return out


# ============================================================================
# L06 — 고혈압 운동 처방
# ----------------------------------------------------------------------------
# rules/L06.yaml | csv 120행
# 출처: ACSM 2022 + ACSM Pronouncement 2023 + 대한고혈압학회 2022
# URL : https://www.koreanhypertension.org/reference/guide?mode=read&idno=10081  ★★★
#
# 적색기:
#   안정시 BP ≥ 180/110 → 운동 보류
#   가슴통증·심한두통·시야흐림·호흡곤란·실신감 → 즉시 중단·119
#   미조절 고혈압(>160/100 지속)·표적장기 손상 의심 → 심장내과
# Valsalva(호흡 참기) 절대 회피.
# ============================================================================
L06 = Citation(
    rule_id="L06", name="고혈압 운동 처방",
    source="ACSM 2022 + 대한고혈압학회 2022",
    url="https://www.koreanhypertension.org/reference/guide?mode=read&idno=10081",
    confidence="★★★",
)

def l06_hypertension_gate(
    has_hypertension: bool,
    resting_sbp: float | None = None,
    resting_dbp: float | None = None,
    medications: list[str] | None = None,
    acute_symptoms: list[str] | None = None,   # ["가슴통증","심한두통","시야흐림","호흡곤란","실신감"]
) -> dict:
    out: dict = {"차단": False, "이유": None, "의뢰": None, "주의": [], "RPE_상한": None}
    if not has_hypertension:
        return out
    medications = medications or []
    acute_symptoms = acute_symptoms or []

    # 적색기 1: 급성 증상 → 즉시 중단·119
    if acute_symptoms:
        out.update(차단=True, 이유=f"급성 심혈관 증상: {', '.join(acute_symptoms)}",
                   의뢰="119 또는 응급실")
        return out

    # 적색기 2: 안정시 BP ≥ 180/110 → 운동 보류
    if resting_sbp is not None and resting_sbp >= 180:
        out.update(차단=True, 이유=f"안정시 SBP {resting_sbp} ≥ 180", 의뢰="내과 진료")
        return out
    if resting_dbp is not None and resting_dbp >= 110:
        out.update(차단=True, 이유=f"안정시 DBP {resting_dbp} ≥ 110", 의뢰="내과 진료")
        return out

    # 미조절 고혈압
    if (resting_sbp is not None and resting_sbp > 160) or (resting_dbp is not None and resting_dbp > 100):
        out["의뢰"] = "심장내과 상담 (미조절 고혈압)"

    # 항상 적용: Valsalva 회피, 저항운동 RPE 상한 6
    out["주의"].append("Valsalva(호흡 참기) 절대 회피 — 들 때 호기, 내릴 때 흡기")
    out["RPE_상한"] = 6.0

    # 약물별 추가 주의
    if "베타차단제" in medications or "β-차단제" in medications:
        out["주의"].append("베타차단제: 심박수 둔화 → HR 대신 RPE로 강도 관리")
    if "이뇨제" in medications:
        out["주의"].append("이뇨제: 탈수·전해질 주의")
    if "α-차단제" in medications or "알파차단제" in medications:
        out["주의"].append("알파차단제: 운동 후 기립성 저혈압 — 쿨다운 5분 필수")

    return out


# ============================================================================
# L07 — 이상지질혈증·대사증후군 운동 처방
# ----------------------------------------------------------------------------
# rules/L07.yaml | csv 121행
# 출처: ACSM 2022 + 한국지질·동맥경화학회 2022
# URL : https://www.lipid.or.kr/uploaded/board/guideline/_50e8f3527d0798a82a29b8ef6c363cce2.pdf  ★★★
#
# 적색기: 가족성 고콜레스테롤(LDL>190)·기왕 심혈관질환·당뇨+50세 이상·운동 중
#         가슴통증/턱·왼팔 방사통/심한 호흡곤란 → 운동부하검사
# ============================================================================
L07 = Citation(
    rule_id="L07", name="이상지질혈증·대사증후군 운동 처방",
    source="ACSM 2022 + 한국지질학회 2022",
    url="https://www.lipid.or.kr/uploaded/board/guideline/_50e8f3527d0798a82a29b8ef6c363cce2.pdf",
    confidence="★★★",
)

def l07_dyslipidemia_gate(
    has_dyslipidemia: bool,
    ldl: float | None = None,
    has_cvd_history: bool = False,
    has_diabetes_and_age50plus: bool = False,
    acute_symptoms: list[str] | None = None,
) -> dict:
    out: dict = {"차단": False, "이유": None, "의뢰": None, "주의": []}
    if not has_dyslipidemia:
        return out
    acute_symptoms = acute_symptoms or []

    # 적색기 1: 운동 중 가슴통증/방사통/호흡곤란 → 즉시 중단
    if acute_symptoms:
        out.update(차단=True, 이유=f"심혈관 의심 증상: {', '.join(acute_symptoms)}",
                   의뢰="응급실")
        return out

    # 적색기 2: 가족성 고콜레스테롤(LDL>190) — 운동 시작 전 부하검사
    if ldl is not None and ldl > 190:
        out["의뢰"] = "심혈관내과 운동부하검사 (가족성 고콜레스테롤 의심)"
    elif has_cvd_history:
        out["의뢰"] = "심혈관내과 운동부하검사 (심혈관질환 이력)"
    elif has_diabetes_and_age50plus:
        out["의뢰"] = "심혈관내과 운동부하검사 (당뇨+50세 이상)"

    # 일반 권고
    out["주의"].append("주당 200~300분 유산소 (체중감량/지질개선 최적)")
    out["주의"].append("주당 칼로리 소비 1,000~2,000 kcal 권고")
    return out


# ============================================================================
# L08 — 골관절염(무릎·고관절) 운동 처방
# ----------------------------------------------------------------------------
# rules/L08.yaml | csv 122행
# 출처: OARSI 2019 (Bannuru) + ACR 2019 (Kolasinski) + ACSM 2022
# URL : https://www.oarsijournal.com/article/S1063-4584(19)31116-1/fulltext  ★★★
#
# 통증 NRS≤4 유지가 핵심. NRS>5 → 즉시 강도/ROM 감량.
# 회피: 깊은 스쿼트(>90°)·점프/착지·중량 런지·갑작스런 방향전환.
# 적색기: 야간통·관절잠김·갑작스런 무력감·관절 발적·발열 → 정형외과.
# ============================================================================
L08 = Citation(
    rule_id="L08", name="골관절염(무릎·고관절) 운동 처방",
    source="OARSI 2019 + ACR 2019",
    url="https://www.oarsijournal.com/article/S1063-4584(19)31116-1/fulltext",
    confidence="★★★",
)

_L08_RED_FLAGS = ("야간통", "관절잠김", "갑작스런_무력감", "관절_발적", "발열", "외상성_부종")
_L08_AVOID_MOVEMENTS = ("깊은_스쿼트", "점프", "착지", "중량_런지", "갑작스런_방향전환")

def l08_oa_gate(
    has_knee_oa: bool = False,
    has_hip_oa: bool = False,
    pain_nrs: int | None = None,
    red_flags: list[str] | None = None,
    movement: str | None = None,
) -> dict:
    out: dict = {"차단": False, "이유": None, "의뢰": None, "주의": [], "ROM_제한": None, "RPE_상한": None}
    if not (has_knee_oa or has_hip_oa):
        return out
    red_flags = red_flags or []

    # 적색기: 즉시 정형외과
    matched = [f for f in red_flags if f in _L08_RED_FLAGS]
    if matched:
        out.update(차단=True, 이유=f"적색기 신호: {', '.join(matched)}",
                   의뢰="정형외과 즉시 평가")
        return out

    # 통증 NRS>5 → 강도/ROM 감량 (차단까진 아님, 룰 카드)
    if pain_nrs is not None and pain_nrs > 5:
        out["주의"].append(f"통증 NRS {pain_nrs}>5 — 즉시 강도/ROM 감량")
        out["RPE_상한"] = 5.0

    # 회피 동작 검사
    if movement and any(m in movement.replace(" ", "") for m in _L08_AVOID_MOVEMENTS):
        out["주의"].append(f"{movement}은 OA 회피 동작 — 부분 ROM 또는 머신 대체")

    if has_knee_oa:
        out["ROM_제한"] = "무릎 굴곡 ≤ 90°"
    out["주의"].append("저항 RPE 5~7 / 통증 NRS≤4 유지 / 수중운동·태극권 권고")
    if not out["RPE_상한"]:
        out["RPE_상한"] = 7.0
    return out


# ============================================================================
# K06 — 수면 부족 → 부상 위험
# ----------------------------------------------------------------------------
# rules/K06.yaml | csv 80행
# 출처: Milewski 2014
# URL : https://pubmed.ncbi.nlm.nih.gov/25028798/  ★★★
#
# <8h 수면 시 부상 위험 1.7배. 3일 연속 6h 미만 → 디로드 권고.
# ============================================================================
K06 = Citation(
    rule_id="K06", name="수면 부족 → 부상 위험",
    source="Milewski 2014",
    url="https://pubmed.ncbi.nlm.nih.gov/25028798/",
    confidence="★★★",
)

def k06_sleep_check(last_3_days_h: list[float]) -> dict:
    """K06: 최근 3일 수면 평균/패턴 → 위험 신호.

    Returns:
        {"위험": bool, "메모": str, "권고": str|None}
    """
    if not last_3_days_h or len(last_3_days_h) < 1:
        return {"위험": False, "메모": "데이터 없음", "권고": None}
    under_6h_days = sum(1 for h in last_3_days_h[-3:] if h < 6.0)
    if under_6h_days >= 3:
        return {
            "위험": True,
            "메모": "3일 연속 수면 6h 미만",
            "권고": "이번 세션 디로드 또는 휴식 권장",
        }
    if min(last_3_days_h[-3:]) < 5.0:
        return {
            "위험": True,
            "메모": f"최저 수면 {min(last_3_days_h[-3:])}h",
            "권고": "강도 RPE 1단계 하향 권장",
        }
    return {"위험": False, "메모": "수면 양호", "권고": None}


# ============================================================================
# K08 — 근육통 (DOMS) 관리
# ----------------------------------------------------------------------------
# rules/K08.yaml | csv 82행
# 출처: Dupuy 2018
# URL : https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full  ★★☆
#
# 24~72h 피크. 7일+ 지속 시 부상 의심.
# ============================================================================
K08 = Citation(
    rule_id="K08", name="근육통 (DOMS) 관리",
    source="Dupuy 2018",
    url="https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full",
    confidence="★★☆",
)

def k08_doms_classify(hours_since_onset: float | None, intensity_0_10: int | None = None) -> dict:
    """K08: DOMS 시점·강도 → 정상/이상 분류."""
    if hours_since_onset is None:
        return {"분류": "정보없음", "권고": None}
    # 7일+ 지속 → 부상 의심
    if hours_since_onset >= 24 * 7:
        return {"분류": "부상_의심", "권고": "통증 7일+ 지속 — 의료 평가"}
    # 24~72h 정상 피크
    if 24 <= hours_since_onset <= 72:
        return {"분류": "DOMS_피크", "권고": "가벼운 운동·능동회복(K07) 권장"}
    return {"분류": "DOMS_회복중", "권고": None}
