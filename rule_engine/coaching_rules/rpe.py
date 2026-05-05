"""RPE 자율조절 룰 (12개): A01, A02, A03, A04, A06, A07, A08, A09, A11, A12, A13, A14.

이 모듈은 "사용자가 한 세트 끝나고 RPE를 입력하면 다음 무게를 얼마로 줄지"의
계산 로직을 모아둔다. 모든 함수는 `rules/{ID}.yaml` 한 장에서 1:1로 파생됐다.
주석에 어느 룰 카드인지, 어느 출처(논문/매뉴얼)에서 왔는지를 매번 적어둔다.

큰 흐름:
    A08(RIR↔RPE 정의) → A04(과소예측 보정) → A11/A12(다음 세트 무게)
                                            → A14(고강도 영역 가산 보정)
    별도: A01(정의), A02/A07(RPE→%1RM 표), A03(세션 종료 트리거),
          A06(대안 입력 UI), A09(보정 신뢰구간), A13(세션간 drift)
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# A01 — RPE 정의
# ----------------------------------------------------------------------------
# rules/A01.yaml | workout_knowledge_base.csv 1행
# 출처: Zourdos 2016 (Tuchscherer RPE 검증, J Strength Cond Res 30(1):267-275)
# URL : https://pubmed.ncbi.nlm.nih.gov/26049792/  ★★★
# ============================================================================
A01 = Citation(
    rule_id="A01", name="RPE 정의",
    source="Zourdos 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/26049792/",
    confidence="★★★",
)

def a01_rpe_to_rir(rpe: float) -> float:
    """A01: 사용자가 입력한 RPE(0~10)를 RIR(남은 가능 횟수)로 환산.

    Zourdos 2016 RIR-기반 RPE 스케일:
        RPE 10 = 0 RIR  (완전 실패)
        RPE 9  = 1 RIR  ("한 번 더 가능했음")
        RPE 8  = 2 RIR
        ...
    공식: RIR = 10 - RPE  (0.5 단위까지 가능)

    Returns:
        남은 가능 횟수 (0.0 ~ 10.0).
    """
    rir = 10.0 - rpe
    return max(0.0, rir)


# ============================================================================
# A02 — RPE-1RM% 변환표 (간이판)
# ----------------------------------------------------------------------------
# rules/A02.yaml | csv 2행
# 출처: Tuchscherer / PowerliftingToWin 정리
# URL : https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/  ★★★
#
# 동일 출처를 더 정밀하게 표로 가진 룰이 A07. A02 는 빠른 룩업/근사용.
# ============================================================================
A02 = Citation(
    rule_id="A02", name="RPE-1RM% 변환표",
    source="Tuchscherer / PowerliftingToWin",
    url="https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/",
    confidence="★★★",
)


# ============================================================================
# A07 — RTS Generalized RPE×렙 → %1RM 풀 매트릭스
# ----------------------------------------------------------------------------
# rules/A07.yaml | csv 7행
# 출처: Tuchscherer / RTS · PowerliftingToWin 정리
# URL : https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/  ★★☆
#
# 룰 카드 한줄설명에 박힌 표 그대로 옮겼다. 룰 카드에 없는 셀은 같은 행의
# 인접 셀로 선형보간한다(주석 표시).
# ============================================================================
A07 = Citation(
    rule_id="A07", name="RTS Generalized RPE×렙 → %1RM 풀 매트릭스",
    source="Tuchscherer / RTS",
    url="https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/",
    confidence="★★☆",
)

# 표 구조: _RTS_TABLE[렙수][RPE] = %1RM
# 룰 카드 한줄설명에 명시된 셀만 진실. 그 사이는 보간으로 채움.
# 1렙: RPE10=100, 9=95.5, 8=92.2
# 5렙: RPE10=86.3, 9=83.7, 8=81.1
# 8렙: RPE10=78.6, 9=76.2, 8=74.0
# 12렙: RPE10=71.3, 9=70.3, 8=67.5
# RPE 6.5~10 × 렙 1~12 전체 매트릭스.
_RTS_ANCHORS: dict[int, dict[float, float]] = {
    1:  {10.0: 100.0, 9.5: 97.8, 9.0: 95.5, 8.5: 93.9, 8.0: 92.2, 7.5: 90.7, 7.0: 89.2, 6.5: 87.8},
    2:  {10.0:  95.5, 9.5: 93.9, 9.0: 92.2, 8.5: 90.7, 8.0: 89.2, 7.5: 87.8, 7.0: 86.3, 6.5: 85.0},
    3:  {10.0:  92.2, 9.5: 90.7, 9.0: 89.2, 8.5: 87.8, 8.0: 86.3, 7.5: 85.0, 7.0: 83.7, 6.5: 82.2},
    4:  {10.0:  89.2, 9.5: 87.8, 9.0: 86.3, 8.5: 85.0, 8.0: 83.7, 7.5: 82.2, 7.0: 81.1, 6.5: 79.7},
    5:  {10.0:  86.3, 9.5: 85.0, 9.0: 83.7, 8.5: 82.2, 8.0: 81.1, 7.5: 79.7, 7.0: 78.6, 6.5: 77.4},
    6:  {10.0:  83.7, 9.5: 82.2, 9.0: 81.1, 8.5: 79.7, 8.0: 78.6, 7.5: 77.4, 7.0: 76.2, 6.5: 75.1},
    7:  {10.0:  81.1, 9.5: 79.7, 9.0: 78.6, 8.5: 77.4, 8.0: 76.2, 7.5: 75.1, 7.0: 74.0, 6.5: 72.3},
    8:  {10.0:  78.6, 9.5: 77.4, 9.0: 76.2, 8.5: 75.1, 8.0: 74.0, 7.5: 72.3, 7.0: 70.7, 6.5: 69.4},
    9:  {10.0:  76.2, 9.5: 75.1, 9.0: 74.0, 8.5: 72.3, 8.0: 70.7, 7.5: 69.4, 7.0: 68.0, 6.5: 66.7},
    10: {10.0:  74.0, 9.5: 72.3, 9.0: 70.7, 8.5: 69.4, 8.0: 68.0, 7.5: 66.7, 7.0: 65.3, 6.5: 64.0},
    11: {10.0:  72.3, 9.5: 70.7, 9.0: 69.4, 8.5: 68.0, 8.0: 66.7, 7.5: 65.3, 7.0: 64.0, 6.5: 62.6},
    12: {10.0:  71.3, 9.5: 70.3, 9.0: 70.3, 8.5: 68.9, 8.0: 67.5, 7.5: 65.9, 7.0: 64.4, 6.5: 63.0},
}

def a07_pct_1rm(reps: int, rpe: float) -> float:
    """A07: 목표 렙수와 RPE를 받아 1RM 대비 % 반환.

    표 밖 입력은 가장 가까운 모서리로 클램프. 0.5 단위가 아니면 가까운 0.5로 라운딩.
    예: 5렙 RPE 8.0 → 81.1 (룰 카드 한줄설명 매트릭스 그대로)
    """
    reps = max(1, min(12, int(reps)))
    rpe = max(6.5, min(10.0, round(rpe * 2) / 2))
    return _RTS_ANCHORS[reps][rpe]


def a02_target_weight_kg(reps: int, target_rpe: float, one_rm_kg: float) -> float:
    """A02: '오늘 N렙 RPE M 목표' → 추천 무게(kg).

    A07 표를 직접 참조하는 같은 출처의 단순 호출이다.
    추천_무게 = 1RM × A07(렙, RPE) / 100.
    """
    pct = a07_pct_1rm(reps, target_rpe)
    return round(one_rm_kg * pct / 100.0, 1)


# ============================================================================
# A08 — RIR ↔ RPE 매핑 정의 (정밀)
# ----------------------------------------------------------------------------
# rules/A08.yaml | csv 8행
# 출처: Zourdos 2016 (RIR-based RPE Scale)
# URL : https://pubmed.ncbi.nlm.nih.gov/26049792/  ★★★
#
# A01 이 사람이 보는 정의라면 A08 은 0.5 단위까지 정밀 매핑을 보장한다.
# RPE 6 이하는 "워밍업 영역"이라 RIR 환산을 의도적으로 하지 않는다.
# ============================================================================
A08 = Citation(
    rule_id="A08", name="RIR ↔ RPE 매핑 정의",
    source="Zourdos 2016",
    url="https://pubmed.ncbi.nlm.nih.gov/26049792/",
    confidence="★★★",
)

_A08_TABLE = {
    10.0: 0.0, 9.5: 0.5, 9.0: 1.0, 8.5: 1.5,
    8.0:  2.0, 7.5: 2.5, 7.0: 3.0, 6.5: 3.5,
}

def a08_precise_rir(rpe: float) -> float | None:
    """A08: 0.5 단위 RPE → RIR. 6 이하는 워밍업 영역으로 보고 None 반환."""
    if rpe < 6.5:
        return None  # 워밍업 영역 — Zourdos 검증 범위 밖
    snapped = round(rpe * 2) / 2
    return _A08_TABLE.get(snapped, 10.0 - snapped)


# ============================================================================
# A04 — RIR 예측 정확도 보정
# ----------------------------------------------------------------------------
# rules/A04.yaml | csv 4행
# 출처: MASS Research / Bastos 2024
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC11127506/  ★★☆
#
# 사용자는 RIR 을 평균 +1회 정도 과소예측한다. 특히 RIR≥3 입력일수록 더 부정확.
# 초보·노인은 +1 보정 강하게, 중·고급은 약하게.
# ============================================================================
A04 = Citation(
    rule_id="A04", name="RIR 예측 정확도 보정",
    source="MASS Research / Bastos 2024",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC11127506/",
    confidence="★★☆",
)

def a04_corrected_rir(reported_rir: float, level: str = "초보", age: int | None = None) -> float:
    """A04: 사용자 입력 RIR 에 보정계수를 더해 내부값으로 변환.

    근거 한 줄(Bastos 2024 메타): 평균 +1 과소예측, RIR≥3에서 정확도 크게 떨어짐.
    레벨·나이 가중:
        초보: +1.0   |   중급: +0.5   |   고급: +0.25
        65세 이상: +0.5 추가 가산
    상한은 5 (그 이상은 워밍업 영역으로 의미 없음).
    """
    base = {"초보": 1.0, "중급": 0.5, "고급": 0.25}.get(level, 0.75)
    if reported_rir >= 3:
        base += 0.5  # RIR≥3 구간 추가 보정 (룰 카드 한줄설명)
    if age is not None and age >= 65:
        base += 0.5
    return min(reported_rir + base, 5.0)


# ============================================================================
# A11 — 세트 간 무게 보정 (Helms 룰)
# ----------------------------------------------------------------------------
# rules/A11.yaml | csv 11행
# 출처: Helms (Muscle and Strength Pyramid) / Ripped Body
# URL : https://rippedbody.com/rpe/  ★★★
#
# 룰 카드 한줄설명: "목표 RPE 대비 0.5점 차이당 무게 ±2% (1점=±4%, 2점=±8%)"
# 동일 세션의 다음 세트에 즉시 적용.
# ============================================================================
A11 = Citation(
    rule_id="A11", name="세트 간 무게 보정 (Helms 룰)",
    source="Helms (M&S Pyramid) / Ripped Body",
    url="https://rippedbody.com/rpe/",
    confidence="★★★",
)

def a11_helms_set_to_set(target_rpe: float, reported_rpe: float, current_kg: float) -> float:
    """A11: 다음 세트 추천 무게(kg).

    공식: 다음무게 = 현재무게 × (1 + (목표RPE − 입력RPE) × 0.04)
        - 입력 RPE 가 1점 더 무겁다(목표8, 실제9) → -4%
        - 0.5점 차이는 ±2%
    예시(룰 카드): 5렙 RPE8 목표 + 입력 RPE9 → 100kg → 96kg
                  RPE7 입력 → 100kg → 104kg
    """
    delta = target_rpe - reported_rpe          # 양수면 가벼움 → 무게↑
    return round(current_kg * (1.0 + delta * 0.04), 1)


# ============================================================================
# A12 — 세트 간 무게 보정 (RTS 룰)
# ----------------------------------------------------------------------------
# rules/A12.yaml | csv 12행
# 출처: Tuchscherer Reactive Training Systems / Exodus Strength 분석
# URL : https://www.exodus-strength.com/forum/viewtopic.php?t=2967  ★★☆
#
# A11 이 단순 식이라면 A12 는 운동 종류·렙수에 따라 폭이 다르다:
#     컴파운드: 1 RPE 차당 4~5%
#     아이솔레이션 또는 8렙 초과: 2~3%
#     RPE +2 이상이면 즉시 -7~10% 또는 운동 종료
# ============================================================================
A12 = Citation(
    rule_id="A12", name="세트 간 무게 보정 (RTS 룰)",
    source="Tuchscherer RTS",
    url="https://www.exodus-strength.com/forum/viewtopic.php?t=2967",
    confidence="★★☆",
)

def a12_rts_set_to_set(
    target_rpe: float,
    reported_rpe: float,
    current_kg: float,
    movement_type: str = "compound",   # "compound" or "isolation"
    reps: int = 5,
) -> tuple[float, bool]:
    """A12: (다음 무게 kg, 종료 권고 여부) 반환.

    종료 권고 = True 인 경우 호출자(`realtime_coaching`)가
    `세트_종료_권고 = True` 로 결과에 반영한다.
    """
    delta = target_rpe - reported_rpe          # 음수면 무거움
    abs_delta = abs(delta)

    # 폭 결정 — 룰 카드 한줄설명 그대로
    if movement_type == "compound" and reps <= 8:
        per_rpe_pct = 0.045   # 4~5% → 중간값 4.5%
    else:
        per_rpe_pct = 0.025   # 아이솔/고렙 2~3% → 중간값 2.5%

    # +2 이상 무거움이면 즉시 -7~10% + 종료 권고
    if delta <= -2.0:
        return round(current_kg * (1 - 0.085), 1), True

    return round(current_kg * (1 + delta * per_rpe_pct), 1), False


# ============================================================================
# A14 — 강도 의존성 보정 (>85% 1RM)
# ----------------------------------------------------------------------------
# rules/A14.yaml | csv 14행
# 출처: Tuchscherer RPE 차트 (RM 간격: 1-2RM 4.5% → 9-10RM 2.3%)
# URL : https://www.exodus-strength.com/forum/viewtopic.php?t=2967  ★★☆
#
# 고강도 영역(<5렙, ≥85% 1RM)에선 RPE 1점 오차 = RM 변화 4.5% 로 큼.
# 보수적으로 -5%(컴파운드)/디폴트 +1단계 더 깎기.
# 저강도(>10렙)는 2~3%만.
# ============================================================================
A14 = Citation(
    rule_id="A14", name="강도 의존성 보정 (>85% 1RM)",
    source="Tuchscherer RPE 차트",
    url="https://www.exodus-strength.com/forum/viewtopic.php?t=2967",
    confidence="★★☆",
)

def a14_intensity_correction(weight_kg: float, one_rm_kg: float, reps: int) -> float:
    """A14: A11/A12 결과에 고강도 영역 추가 감산.

    적용 규칙:
        ≥85% 1RM 또는 ≤5렙: 결과를 추가로 -5% (컴파운드 가정)
        ≤70% 1RM 또는 >10렙: 추가 보정 없음(폭 자체가 작음)
        그 외: 변경 없음
    """
    if one_rm_kg <= 0:
        return weight_kg
    pct = weight_kg / one_rm_kg
    if pct >= 0.85 or reps <= 5:
        return round(weight_kg * 0.95, 1)
    return weight_kg


# ============================================================================
# A09 — RPE 변환표 정확도/검증 한계 (캘리브레이션)
# ----------------------------------------------------------------------------
# rules/A09.yaml | csv 9행
# 출처: Zourdos 2016 / Helms 2017 RPE accuracy
# URL : https://pubmed.ncbi.nlm.nih.gov/26049792/  ★★★
#
# 룰 카드: 셀별 %1RM 은 ±2~5%p 오차. 초보 ±5, 중급 ±3, 고급 ±2.
# 3세션 연속 '예상 RPE 8 → 실제 RPE 9.5' 식이면 표 자체를 -3%p 자동 캘리브레이션.
# ============================================================================
A09 = Citation(
    rule_id="A09", name="RPE 변환표 정확도/검증 한계",
    source="Zourdos 2016 / Helms 2017",
    url="https://pubmed.ncbi.nlm.nih.gov/26049792/",
    confidence="★★★",
)

def a09_confidence_band(level: str = "초보") -> float:
    """A09: 사용자 레벨별 RPE 표 신뢰구간(±%p)."""
    return {"초보": 5.0, "중급": 3.0, "고급": 2.0}.get(level, 4.0)


def a09_should_recalibrate(recent_actual_minus_target: list[float]) -> bool:
    """3세션 연속 평균 RPE 차이가 ±1.5 이상이면 표 캘리브레이션 권고."""
    if len(recent_actual_minus_target) < 3:
        return False
    last_three = recent_actual_minus_target[-3:]
    return abs(sum(last_three) / 3) >= 1.5


# ============================================================================
# A13 — 세션 간 RPE drift 보정
# ----------------------------------------------------------------------------
# rules/A13.yaml | csv 13행
# 출처: Tuchscherer "Deloading Effectively" / Helms 자율조절 원칙
# URL : https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively  ★★☆
#
# 같은 무게×렙에서 RPE 가 2주 이상 +1 점 drift → 회복 부족 → -5% 또는 디로드.
# RPE -1 점 drift → 적응 완료, +2.5~5% 진행.
# ============================================================================
A13 = Citation(
    rule_id="A13", name="세션 간 RPE drift 보정",
    source="Tuchscherer / Helms",
    url="https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively",
    confidence="★★☆",
)

def a13_session_drift_adjustment(drift: float, current_kg: float) -> tuple[float, str]:
    """A13: 누적 drift(평균 RPE 변화) → 다음 세션 무게 + 권고 라벨.

    권고:
        drift >= +1.0 → -5%  (라벨: "회복부족_감산")
        drift <= -1.0 → +2.5~5% (라벨: "진보_가산")
        그 외 → 유지
    """
    if drift >= 1.0:
        return round(current_kg * 0.95, 1), "회복부족_감산"
    if drift <= -1.0:
        return round(current_kg * 1.025, 1), "진보_가산"
    return current_kg, "유지"


# ============================================================================
# A03 — Fatigue Percent (피로 누적률)
# ----------------------------------------------------------------------------
# rules/A03.yaml | csv 3행
# 출처: Tuchscherer / All Things Gym
# URL : https://www.allthingsgym.com/mike-tuchscherer-auto-regulation-fundamentals-fatigue-percentages/  ★★★
#
# 톱셋(RPE9) 후 무게를 N% 줄여 같은 RPE 도달까지 백오프 세트 누적.
# 누적 피로(=현재세트 1RM 추정 / 톱셋 1RM 추정의 비율)가 임계 이하로 떨어지면 종료.
# ============================================================================
A03 = Citation(
    rule_id="A03", name="Fatigue Percent (피로 누적률)",
    source="Tuchscherer / All Things Gym",
    url="https://www.allthingsgym.com/mike-tuchscherer-auto-regulation-fundamentals-fatigue-percentages/",
    confidence="★★★",
)

def a03_should_stop(top_set_e1rm: float, current_set_e1rm: float, threshold: float = 0.92) -> bool:
    """A03: 누적 피로로 인해 세트 종료할지 판단.

    e1RM (estimated 1RM) 은 C09/C10 으로 계산된 추정값을 의미한다.
    threshold 0.92 = 톱셋 대비 8% 이상 떨어지면 종료(룰 카드 활용예시 기반).
    """
    if top_set_e1rm <= 0:
        return False
    return (current_set_e1rm / top_set_e1rm) < threshold


# ============================================================================
# A06 — OMNI-RES 스케일 (대안 입력 UI)
# ----------------------------------------------------------------------------
# rules/A06.yaml | csv 6행
# 출처: Robertson 2003
# URL : https://pubmed.ncbi.nlm.nih.gov/12569225/  ★★☆
#
# 0~10 시각형 RPE 스케일. Borg 와 r=0.94~0.97. 초보·노인·재활용 검증.
# 룰 카드 "하는_일": 대안 RPE 입력 UI 제공. 즉 사용자 레벨에 따라 입력 방식 토글.
# ============================================================================
A06 = Citation(
    rule_id="A06", name="OMNI-RES 스케일",
    source="Robertson 2003",
    url="https://pubmed.ncbi.nlm.nih.gov/12569225/",
    confidence="★★☆",
)

def a06_input_mode(level: str = "초보", age: int | None = None) -> str:
    """A06: 사용자 특성별 RPE 입력 UI 모드.

    Returns: "OMNI-RES" (시각 0~10) | "RIR" (남은 가능 횟수) | "RPE_정밀" (0.5 단위)
    """
    if level == "초보" or (age is not None and age >= 65):
        return "OMNI-RES"
    if level == "고급":
        return "RPE_정밀"
    return "RIR"
