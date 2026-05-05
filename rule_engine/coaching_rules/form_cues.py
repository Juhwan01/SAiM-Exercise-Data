"""실시간 코칭 — 폼·큐·호흡·VBT 룰 (16개): E01~E17 (E09 제외).

E01-E04: VBT (속도 기반 훈련) - 센서/카메라 데이터 기반
E05    : 외적 vs 내적 큐 (메타 룰)
E06-E12: 종목별 폼 큐 (스쿼트/벤치/데드/OHP/풀업/바벨로우)
E13    : Valsalva 호흡
E14    : 가동범위(ROM) 기준
E15    : 부상 신호 vs 근육통 분기
E16    : 컴파운드 셋업 5단계 체크리스트
E17    : 그립 너비/유형

E09(RAMP 워밍업)은 운동_추천 전용 → routine_rules 폴더로.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# E01 — VBT (속도 기반 훈련)
# ----------------------------------------------------------------------------
# rules/E01.yaml | csv 51행
# 출처: NSCA SCJ 2021
# URL : https://journals.lww.com/nsca-scj/fulltext/2021/04000/velocity_based_training__from_theory_to.4.aspx  ★★☆
# ============================================================================
E01 = Citation(
    rule_id="E01", name="VBT (속도 기반 훈련)",
    source="NSCA SCJ 2021",
    url="https://journals.lww.com/nsca-scj/fulltext/2021/04000/velocity_based_training__from_theory_to.4.aspx",
    confidence="★★☆",
)

def e01_vbt_alert(rep_velocities_ms: list[float], threshold_drop_pct: float = 0.20) -> dict:
    """E01: 렙별 바벨 속도 리스트를 받아 피로 신호 반환.

    Returns:
        {"피로_감지": bool, "감소율": float, "메모": str}
    """
    if not rep_velocities_ms or len(rep_velocities_ms) < 2:
        return {"피로_감지": False, "감소율": 0.0, "메모": "데이터 부족"}
    first = rep_velocities_ms[0]
    last = rep_velocities_ms[-1]
    if first <= 0:
        return {"피로_감지": False, "감소율": 0.0, "메모": "측정 오류"}
    drop = (first - last) / first
    return {
        "피로_감지": drop >= threshold_drop_pct,
        "감소율": round(drop, 3),
        "메모": f"첫렙 {first:.2f}m/s → 마지막렙 {last:.2f}m/s",
    }


# ============================================================================
# E02 — Load-Velocity Profile
# ----------------------------------------------------------------------------
# rules/E02.yaml | csv 52행
# 출처: Vitruve
# URL : https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/  ★★☆
#
# 워밍업 무게/속도 → 그날의 1RM 추정 → 무게 자동 보정
# 선형 회귀: 무게=a×속도+b. 1RM = 속도 0(MVT, minimum velocity threshold) 시 무게.
# 일반 MVT 기준: 스쿼트 0.30 m/s, 벤치 0.15 m/s, 데드 0.13 m/s.
# ============================================================================
E02 = Citation(
    rule_id="E02", name="Load-Velocity Profile",
    source="Vitruve",
    url="https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/",
    confidence="★★☆",
)

_E02_MVT = {"스쿼트": 0.30, "벤치프레스": 0.15, "데드리프트": 0.13}

def e02_estimate_one_rm(samples: list[tuple[float, float]], movement: str = "스쿼트") -> float:
    """E02: [(무게, 속도)] 샘플 → 그날의 추정 1RM(kg).

    선형 회귀 후 속도=MVT 시점의 무게 = 1RM.
    """
    if len(samples) < 2:
        return 0.0
    n = len(samples)
    sum_v = sum(v for _, v in samples)
    sum_w = sum(w for w, _ in samples)
    sum_vv = sum(v * v for _, v in samples)
    sum_vw = sum(v * w for w, v in samples)
    denom = n * sum_vv - sum_v * sum_v
    if denom == 0:
        return 0.0
    a = (n * sum_vw - sum_v * sum_w) / denom   # 기울기
    b = (sum_w - a * sum_v) / n                # 절편
    mvt = _E02_MVT.get(movement, 0.20)
    return round(a * mvt + b, 1)


# ============================================================================
# E03 — Velocity Loss 임계
# ----------------------------------------------------------------------------
# rules/E03.yaml | csv 53행
# 출처: Pareja-Blanco / Sports Med 2022
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC9807551/  ★★★
#
# 첫 렙 대비 감소율로 세트 종료. 목표별 임계:
#   파워 10~20% / 근력 20~25% / 근비대 25~40% / 35%+ 지속 비권장
# ============================================================================
E03 = Citation(
    rule_id="E03", name="Velocity Loss 임계",
    source="Pareja-Blanco 2022",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC9807551/",
    confidence="★★★",
)

_E03_THRESHOLD = {
    "파워": 0.15, "근력": 0.225, "근비대": 0.325, "건강증진": 0.20,
}

def e03_should_stop_by_velocity(rep_velocities_ms: list[float], goal: str = "근력") -> bool:
    """E03: 속도 감소율이 목표별 임계를 넘으면 True (세트 종료 권고)."""
    if not rep_velocities_ms or len(rep_velocities_ms) < 2:
        return False
    first, last = rep_velocities_ms[0], rep_velocities_ms[-1]
    if first <= 0:
        return False
    drop = (first - last) / first
    return drop >= _E03_THRESHOLD.get(goal, 0.225)


# ============================================================================
# E04 — 실시간 피드백 효과 (세트 후 시각 피드백)
# ----------------------------------------------------------------------------
# rules/E04.yaml | csv 54행
# 출처: Weakley 2023 (Sports Med meta)
# URL : https://pubmed.ncbi.nlm.nih.gov/37410360/  ★★☆
# ============================================================================
E04 = Citation(
    rule_id="E04", name="실시간 피드백 효과",
    source="Weakley 2023",
    url="https://pubmed.ncbi.nlm.nih.gov/37410360/",
    confidence="★★☆",
)

def e04_post_set_feedback(rep_velocities_ms: list[float]) -> dict:
    """E04: 세트 후 보여줄 시각 피드백 데이터(평균/피크/감소율)."""
    if not rep_velocities_ms:
        return {"평균": 0.0, "피크": 0.0, "감소율_pct": 0.0}
    avg = sum(rep_velocities_ms) / len(rep_velocities_ms)
    peak = max(rep_velocities_ms)
    drop = (rep_velocities_ms[0] - rep_velocities_ms[-1]) / rep_velocities_ms[0] * 100
    return {
        "평균": round(avg, 3),
        "피크": round(peak, 3),
        "감소율_pct": round(drop, 1),
    }


# ============================================================================
# E05 — External vs Internal 큐
# ----------------------------------------------------------------------------
# rules/E05.yaml | csv 55행
# 출처: Wulf
# URL : https://www.thestrengthathlete.com/blog/external-cues  ★★★
#
# 외적 큐 ("천장으로 밀어") > 내적 큐 ("가슴 사용"). 학습·수행 모두 외적 우월.
# E06~E12 의 큐는 모두 외적 큐 우선으로 구성됐다 (이 룰의 메타 가이드).
# ============================================================================
E05 = Citation(
    rule_id="E05", name="External vs Internal 큐",
    source="Wulf",
    url="https://www.thestrengthathlete.com/blog/external-cues",
    confidence="★★★",
)

def e05_prefer_external() -> bool:
    """E05: 큐 선택 시 외적 큐 우선 사용 여부. 항상 True (이 룰의 결론)."""
    return True


# ============================================================================
# E06 — 스쿼트 폼 에러·큐
# ----------------------------------------------------------------------------
# rules/E06.yaml | csv 56행
# 출처: Power Rack Strength / TPS
# URL : https://www.powerrackstrength.com/3-common-squat-mistakes/  ★★☆
# ============================================================================
E06 = Citation(
    rule_id="E06", name="스쿼트 폼 에러·큐",
    source="Power Rack Strength / TPS",
    url="https://www.powerrackstrength.com/3-common-squat-mistakes/",
    confidence="★★☆",
)

# 키 = 폼 에러, 값 = 외적 큐 텍스트
_E06_ERROR_TO_CUE = {
    "무릎_내회전": "무릎으로 벽을 밀어내듯",
    "깊이_부족": "엉덩이를 의자 뒤로 더 보내",
    "중심_이동": "발 한가운데로 무게를 눌러",
    "골반_윙크": "갈비뼈를 골반 위에 얹는다는 느낌으로",
}

def e06_squat_cue(error: str | None = None) -> list[str]:
    """E06: 폼 에러가 감지되면 매칭 큐, 없으면 기본 셋업 큐 셋."""
    if error and error in _E06_ERROR_TO_CUE:
        return [_E06_ERROR_TO_CUE[error]]
    # 기본(에러 없음) 큐
    return ["발 한가운데를 발로 누르며 일어선다", "가슴을 천장으로 보낸다는 느낌"]


# ============================================================================
# E07 — 벤치프레스 폼 큐
# ----------------------------------------------------------------------------
# rules/E07.yaml | csv 57행
# 출처: PowerliftingTechnique / Starting Strength
# URL : https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology  ★★★
# ============================================================================
E07 = Citation(
    rule_id="E07", name="벤치프레스 폼 큐",
    source="Starting Strength",
    url="https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology",
    confidence="★★★",
)

def e07_bench_cue() -> list[str]:
    """E07: 벤치프레스 셋업 체크리스트 + 외적 큐 (룰 카드 한줄설명 그대로)."""
    return [
        "발을 바닥에 단단히 고정",
        "광배를 활성화 (어깨를 후퇴·하강)",
        "바 패스: 가슴 하부 → 어깨 위 직선",
        "팔꿈치는 몸통과 45~75°",
        "바를 천장으로 밀어내듯",   # 외적 큐
    ]


# ============================================================================
# E08 — 데드리프트 폼 큐
# ----------------------------------------------------------------------------
# rules/E08.yaml | csv 58행
# 출처: PowerliftingTechnique / Men's Journal
# URL : https://powerliftingtechnique.com/deadlift-cues/  ★★★
# ============================================================================
E08 = Citation(
    rule_id="E08", name="데드리프트 폼 큐",
    source="PowerliftingTechnique",
    url="https://powerliftingtechnique.com/deadlift-cues/",
    confidence="★★★",
)

def e08_deadlift_cue() -> list[str]:
    return [
        "바는 발 한가운데(미드풋) 위",
        "광배 잠금 (겨드랑이에 오렌지 끼우듯)",
        "척추 중립 (등 평평하게)",
        "다리로 바닥을 밀어내듯",         # 외적 큐
        "Valsalva 호흡 셋팅 (E13 참조)",
    ]


# ============================================================================
# E10 — 오버헤드프레스 폼 큐
# ----------------------------------------------------------------------------
# rules/E10.yaml | csv 60행
# 출처: Starting Strength / Stronger By Science
# URL : https://startingstrength.com/article/the-press  ★★★
# ============================================================================
E10 = Citation(
    rule_id="E10", name="오버헤드프레스 폼 큐",
    source="Starting Strength",
    url="https://startingstrength.com/article/the-press",
    confidence="★★★",
)

def e10_ohp_cue() -> list[str]:
    return [
        "발 어깨너비, 코어/둔근 단단히 잠그기",
        "바 경로: 코끝 → 머리 위 직선",
        "락아웃 시 머리 통과 (어깨가 귀 옆으로)",
        "천장을 밀어내듯",   # 외적 큐
    ]


# ============================================================================
# E11 — 풀업/친업 폼 큐
# ----------------------------------------------------------------------------
# rules/E11.yaml | csv 61행
# 출처: Stronger By Science
# URL : https://startingstrength.com/article/chins-and-pullups  ★★★
# ============================================================================
E11 = Citation(
    rule_id="E11", name="풀업/친업 폼 큐",
    source="Stronger By Science",
    url="https://startingstrength.com/article/chins-and-pullups",
    confidence="★★★",
)

def e11_pullup_cue() -> list[str]:
    return [
        "어깨 후퇴/하강 시작 (디드 컵 주머니 동작)",
        "가슴을 바에 닿는다는 느낌",   # 외적 큐
        "턱이 바 위로",
        "발 교차/킵핑 금지 (스트릭트 풀업)",
    ]


# ============================================================================
# E12 — 바벨 로우 폼 큐
# ----------------------------------------------------------------------------
# rules/E12.yaml | csv 62행
# 출처: Strength Log
# URL : https://www.strengthlog.com/barbell-row/  ★★☆
# ============================================================================
E12 = Citation(
    rule_id="E12", name="바벨 로우 폼 큐",
    source="Strength Log",
    url="https://www.strengthlog.com/barbell-row/",
    confidence="★★☆",
)

def e12_barbell_row_cue() -> list[str]:
    return [
        "힙힌지 45° (상체 기울기)",
        "척추 중립",
        "바를 배꼽 하단으로 당긴다",   # 외적 큐
        "팔꿈치는 옆구리 방향으로",
        "당김 끝에 견갑 후퇴",
    ]


# ============================================================================
# E13 — Valsalva 호흡
# ----------------------------------------------------------------------------
# rules/E13.yaml | csv 63행
# 출처: NSCA Essentials / Hackett 2013
# URL : https://pubmed.ncbi.nlm.nih.gov/23222073/  ★★★
#
# 고중량(>80% 1RM) 시 들숨 → 호흡정지로 복강내압 형성 → 하강 → 상승 후 배출.
# 고혈압자 주의 (L06 가드와 충돌 — L06 가 우선).
# ============================================================================
E13 = Citation(
    rule_id="E13", name="Valsalva 호흡",
    source="NSCA / Hackett 2013",
    url="https://pubmed.ncbi.nlm.nih.gov/23222073/",
    confidence="★★★",
)

def e13_breathing_guide(weight_kg: float, one_rm_kg: float, has_hypertension: bool = False) -> str:
    """E13: 무게 비율과 고혈압 여부에 따라 호흡 가이드 텍스트.

    >80% 1RM AND 고혈압 없음 → Valsalva 권장
    >80% 1RM AND 고혈압 있음 → 들 때 숨 내쉬기 (L06 가드)
    그 외(80% 미만) → 일반 호흡 (들 때 호기, 내릴 때 흡기)
    """
    if one_rm_kg <= 0:
        return "들어올릴 때 숨 내쉬기, 내릴 때 들이마시기"
    pct = weight_kg / one_rm_kg
    if pct > 0.80 and not has_hypertension:
        return "들숨 후 호흡정지(Valsalva) → 하강 → 상승 후 배출"
    if pct > 0.80 and has_hypertension:
        return "고혈압 가드: Valsalva 금지. 들 때 강하게 '후' 내쉬기"
    return "들어올릴 때 숨 내쉬기, 내릴 때 들이마시기"


# ============================================================================
# E14 — 가동범위 (ROM) 기준
# ----------------------------------------------------------------------------
# rules/E14.yaml | csv 64행
# 출처: Pedrosa 2022 (Eur J Sport Sci)
# URL : https://pubmed.ncbi.nlm.nih.gov/33977835/  ★★★
# ============================================================================
E14 = Citation(
    rule_id="E14", name="가동범위 (ROM) 기준",
    source="Pedrosa 2022",
    url="https://pubmed.ncbi.nlm.nih.gov/33977835/",
    confidence="★★★",
)

def e14_rom_cue(movement: str, depth_ratio: float | None) -> list[str]:
    """E14: 측정된 ROM 비율(0~1, 1=풀ROM)을 보고 큐 반환.

    depth_ratio 가 None 이면 빈 리스트 (측정 데이터 없음 = 알림 안 함).
    """
    if depth_ratio is None:
        return []
    if depth_ratio < 0.85:
        if movement == "스쿼트":
            return ["엉덩이를 더 내린다 (대퇴 평행 이상)"]
        if movement == "벤치프레스":
            return ["바를 가슴까지 (멈추지 말고 터치)"]
        return ["풀ROM 으로 한 번 더 — 부분 반복 우선 X"]
    return []


# ============================================================================
# E15 — 부상 신호 vs 근육통(DOMS) 분기
# ----------------------------------------------------------------------------
# rules/E15.yaml | csv 65행
# 출처: Cheung 2003 (DOMS 리뷰)
# URL : https://pubmed.ncbi.nlm.nih.gov/12617692/  ★★☆
#
# 관절통·날카로운·국소 = 부상 신호 → 운동 중단
# 양측 대칭 둔통 24~72h = DOMS 정상 → 가벼운 운동 가능
# ============================================================================
E15 = Citation(
    rule_id="E15", name="부상 신호 vs 근육통",
    source="Cheung 2003",
    url="https://pubmed.ncbi.nlm.nih.gov/12617692/",
    confidence="★★☆",
)

def e15_pain_classify(
    pain_pattern: str | None,           # "예리한"/"둔한"/"국소"/"양측대칭"
    pain_intensity_0_10: int | None,
    is_joint: bool = False,
) -> dict:
    """E15: 통증 분류 → {분류, 권고}."""
    if pain_pattern is None and pain_intensity_0_10 is None:
        return {"분류": "정보없음", "권고": "통증 입력 후 재판정"}
    # 부상 의심 신호
    if is_joint or pain_pattern in ("예리한", "국소"):
        return {"분류": "부상_의심", "권고": "운동 중단, 통증 부위 평가 (Q01 발동)"}
    # DOMS 정상 신호
    if pain_pattern == "양측대칭":
        return {"분류": "DOMS_정상", "권고": "가벼운 운동·능동회복 가능"}
    return {"분류": "불확실", "권고": "통증 강도가 5 이상이면 중단 권장"}


# ============================================================================
# E16 — 컴파운드 셋업 5단계 체크리스트
# ----------------------------------------------------------------------------
# rules/E16.yaml | csv 66행
# 출처: NSCA / Starting Strength
# URL : https://startingstrength.com/article/the_squat  ★★★
# ============================================================================
E16 = Citation(
    rule_id="E16", name="컴파운드 셋업 체크리스트",
    source="NSCA / Starting Strength",
    url="https://startingstrength.com/article/the_squat",
    confidence="★★★",
)

def e16_setup_checklist() -> list[str]:
    """E16: 모든 컴파운드 첫 세트 직전 5단계 (룰 카드 한줄설명 그대로)."""
    return [
        "①발 위치",
        "②그립 너비",
        "③척추 중립",
        "④광배/코어 잠금",
        "⑤호흡 셋팅",
    ]


# ============================================================================
# E17 — 그립 너비/유형
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

def e17_grip_guide(movement: str, target_muscle: str | None = None) -> str:
    """E17: 운동 + 목표 근육에 따른 그립 권장."""
    if movement == "벤치프레스":
        return "어깨너비의 1.5배 (오버그립)"
    if movement == "데드리프트":
        return "어깨너비, 고중량은 후크그립"
    if movement == "풀업":
        if target_muscle == "이두":
            return "내로우/언더그립"
        return "와이드 오버그립 (광배 강조)"
    return "기본 어깨너비 오버그립"
