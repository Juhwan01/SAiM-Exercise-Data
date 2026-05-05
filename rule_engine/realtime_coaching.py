"""실시간 코칭 진입 함수.

외부에서는 ``realtime_coaching(state)`` 만 호출하면 된다. 내부에서는
``coaching_rules/`` 폴더의 50개 룰을 정해진 순서로 돌리고, 결과를 한 묶음으로
반환한다.

순서:
    1. 안전 게이트 (Q01·L05·L06·L07·L08·K06·E15)
       — 차단 신호가 나오면 즉시 반환 (운동 중단)
    2. 다음 세트 무게 (A04 → A11 → A14, 또는 A12, 종료 트리거 A03)
    3. 휴식 시간 (C07)
    4. 폼·호흡·체크리스트 (E05~E17 발동)
    5. 디로드 권고 (G02·G04·G07)
    6. 보조 안내 (P05·K04·K08)

각 단계마다 어느 룰을 발동했는지 ``CoachingResult.발동_룰`` 에 누적해
사용자가 "왜?" 를 누르면 출처 URL 까지 보여줄 수 있게 한다.
"""

from __future__ import annotations

from rule_engine.coaching_rules import deload, form_cues, misc, progression, rpe, safety
from rule_engine.types import CoachingResult, CoachingState, RuleHit


# ---------------------------------------------------------------------------
# 진입 함수
# ---------------------------------------------------------------------------
def realtime_coaching(state: CoachingState) -> CoachingResult:
    """실시간 코칭 1회 호출 → 결과 묶음."""
    out = CoachingResult()

    # ── 1단계: 안전 게이트 ────────────────────────────────────
    if _run_safety_gates(state, out):
        return out  # 차단 발생 → 즉시 종료

    # ── 2단계: 다음 세트 무게 ────────────────────────────────
    _compute_next_weight(state, out)

    # ── 3단계: 휴식 ──────────────────────────────────────────
    _set_rest(state, out)

    # ── 4단계: 폼·호흡·체크리스트 ────────────────────────────
    _set_form_and_breath(state, out)

    # ── 5단계: 디로드 권고 ───────────────────────────────────
    _check_deload(state, out)

    # ── 6단계: 보조 안내 ────────────────────────────────────
    _aux_advice(state, out)

    return out


# ---------------------------------------------------------------------------
# 1. 안전 게이트
# ---------------------------------------------------------------------------
def _run_safety_gates(s: CoachingState, out: CoachingResult) -> bool:
    """차단 신호가 나면 True 반환. out 에는 차단 이유와 발동 룰을 기록한다."""

    # Q01 — 급성 부상 입력 시 (PEACE & LOVE)
    if s.통증_시작_h is not None:
        q = safety.q01_acute_injury_protocol(s.통증_시작_h)
        out.add(RuleHit(safety.Q01, summary=f"부상 단계: {q['단계']}", output=q))
        if q["차단"]:
            out.차단됨 = True
            out.차단_이유 = q["단계"]
            out.제안 = q["행동"]
            return True

    # E15 — 통증 패턴 분류 (관절통/예리한/국소 → 부상 의심)
    if s.통증부위 or s.통증패턴 or s.통증강도_0_10 is not None:
        is_joint = (s.통증부위 or "") in ("무릎", "어깨", "팔꿈치", "손목", "허리", "고관절")
        e = form_cues.e15_pain_classify(s.통증패턴, s.통증강도_0_10, is_joint=is_joint)
        out.add(RuleHit(form_cues.E15, summary=e["권고"] or "", output=e))
        if e["분류"] == "부상_의심":
            out.차단됨 = True
            out.차단_이유 = "부상 의심 신호 — Q01 PEACE 단계로 전환"
            return True

    # L05 — 당뇨
    if "당뇨" in s.질환:
        complications = [c for c in s.질환 if c in ("증식성_망막증", "자율신경병증", "신경병증_심", "족부궤양")]
        gate = safety.l05_diabetes_gate(
            has_diabetes=True,
            complications=complications,
            fasting_glucose_mgdl=None,
            ketone_positive=False,
        )
        if gate["차단"] or gate["주의"]:
            out.add(RuleHit(safety.L05, summary=gate["이유"] or "당뇨 가드 적용", output=gate))
            out.경고.extend(gate["주의"])
            if gate["의뢰"]:
                out.의뢰_권고 = gate["의뢰"]
            if gate["차단"]:
                out.차단됨 = True
                out.차단_이유 = gate["이유"]
                return True

    # L06 — 고혈압
    if "고혈압" in s.질환:
        gate = safety.l06_hypertension_gate(has_hypertension=True)
        if gate["차단"] or gate["주의"]:
            out.add(RuleHit(safety.L06, summary="고혈압 가드 — Valsalva 회피 / RPE 상한 6", output=gate))
            out.경고.extend(gate["주의"])
            if gate["RPE_상한"] is not None and s.목표RPE > gate["RPE_상한"]:
                out.경고.append(f"목표 RPE {s.목표RPE} → {gate['RPE_상한']} 으로 하향 권고")

    # L07 — 이상지질혈증
    if "이상지질혈증" in s.질환:
        gate = safety.l07_dyslipidemia_gate(has_dyslipidemia=True)
        if gate["주의"]:
            out.add(RuleHit(safety.L07, summary="이상지질혈증 가드", output=gate))
            out.경고.extend(gate["주의"])

    # L08 — 골관절염
    has_knee = "골관절염_무릎" in s.질환
    has_hip = "골관절염_고관절" in s.질환
    if has_knee or has_hip:
        gate = safety.l08_oa_gate(
            has_knee_oa=has_knee, has_hip_oa=has_hip,
            pain_nrs=s.통증강도_0_10, movement=s.운동명,
        )
        if gate["차단"] or gate["주의"]:
            out.add(RuleHit(safety.L08, summary="OA 가드", output=gate))
            out.경고.extend(gate["주의"])
            if gate["차단"]:
                out.차단됨 = True
                out.차단_이유 = gate["이유"]
                if gate["의뢰"]:
                    out.의뢰_권고 = gate["의뢰"]
                return True

    # K06 — 수면 위험
    if s.최근_3일_수면_h:
        k = safety.k06_sleep_check(s.최근_3일_수면_h)
        if k["위험"]:
            out.add(RuleHit(safety.K06, summary=k["메모"], output=k))
            if k["권고"]:
                out.제안.append(k["권고"])

    # K08 — DOMS 7일+
    if s.근육통_시작_h is not None:
        d = safety.k08_doms_classify(s.근육통_시작_h)
        out.add(RuleHit(safety.K08, summary=d.get("권고") or "", output=d))
        if d["분류"] == "부상_의심":
            out.차단됨 = True
            out.차단_이유 = "근육통 7일+ 지속 — 부상 의심"
            out.의뢰_권고 = "의료 평가"
            return True

    return False


# ---------------------------------------------------------------------------
# 2. 다음 세트 무게
# ---------------------------------------------------------------------------
def _compute_next_weight(s: CoachingState, out: CoachingResult) -> None:
    """A11/A12/A14 + A03 종료 트리거. 입력 RPE 가 없으면 스킵."""
    if s.입력RPE is None:
        return  # 직전 세트 RPE 입력 없음 → 무게 보정 X

    # A04: RIR 과소예측 보정 (입력 RIR 을 내부값으로 변환)
    reported_rir = rpe.a08_precise_rir(s.입력RPE)
    if reported_rir is not None:
        corrected_rir = rpe.a04_corrected_rir(reported_rir, level=s.사용자레벨)
        # 보정된 RIR → 내부 RPE
        adjusted_input_rpe = 10.0 - corrected_rir
        out.add(RuleHit(rpe.A04, summary=f"RIR 보정: {reported_rir}→{corrected_rir}", output=corrected_rir))
    else:
        adjusted_input_rpe = s.입력RPE

    # A11: Helms 단순 식 (디폴트 사용)
    next_kg = rpe.a11_helms_set_to_set(s.목표RPE, adjusted_input_rpe, s.현재무게_kg)
    out.add(RuleHit(rpe.A11, summary=f"{s.현재무게_kg}kg → {next_kg}kg (목표 {s.목표RPE} vs 입력 {s.입력RPE})", output=next_kg))

    # A12: 컴파운드인 경우 RTS 룰로 한 번 더 검증 — 두 결과 평균
    if s.운동종류 == "compound":
        rts_kg, stop_flag = rpe.a12_rts_set_to_set(
            s.목표RPE, adjusted_input_rpe, s.현재무게_kg,
            movement_type=s.운동종류, reps=s.목표렙,
        )
        out.add(RuleHit(rpe.A12, summary=f"RTS 보정 → {rts_kg}kg, 종료={stop_flag}", output=(rts_kg, stop_flag)))
        # Helms·RTS 평균
        next_kg = round((next_kg + rts_kg) / 2, 1)
        if stop_flag:
            out.세트_종료_권고 = True

    # A14: 고강도 영역 추가 보정
    if s.최대무게_추정_kg > 0:
        corrected = rpe.a14_intensity_correction(next_kg, s.최대무게_추정_kg, s.목표렙)
        if corrected != next_kg:
            out.add(RuleHit(rpe.A14, summary=f"고강도 보정 {next_kg}→{corrected}", output=corrected))
            next_kg = corrected

    out.다음_무게_kg = next_kg

    # A03: 톱셋 대비 누적 피로 8% 이상이면 종료 권고
    if s.톱셋_무게_kg and s.톱셋_RPE is not None and s.실제렙 is not None:
        # 톱셋 e1RM = 톱셋무게 × (1 + 톱셋RIR/30)  (Epley 변형)
        top_rir = rpe.a08_precise_rir(s.톱셋_RPE) or 0.0
        top_e1rm = s.톱셋_무게_kg * (1 + top_rir / 30)
        cur_rir = rpe.a08_precise_rir(s.입력RPE) or 0.0
        cur_e1rm = s.현재무게_kg * (1 + cur_rir / 30)
        if rpe.a03_should_stop(top_e1rm, cur_e1rm):
            out.세트_종료_권고 = True
            out.add(RuleHit(rpe.A03, summary="누적 피로 임계 — 세트 종료 권고", output=True))


# ---------------------------------------------------------------------------
# 3. 휴식
# ---------------------------------------------------------------------------
def _set_rest(s: CoachingState, out: CoachingResult) -> None:
    # 목표 추정: 1RM 대비 무게가 75% 이상이면 "스트렝스" 모드, 아니면 사용자 레벨 기반
    goal = "스트렝스" if (s.최대무게_추정_kg > 0 and s.현재무게_kg / s.최대무게_추정_kg >= 0.85) else "근육량 증가"
    out.휴식_초 = misc.c07_rest_seconds(s.운동종류, goal)
    out.add(RuleHit(misc.C07, summary=f"휴식 {out.휴식_초}초 ({goal})", output=out.휴식_초))


# ---------------------------------------------------------------------------
# 4. 폼·호흡·체크리스트
# ---------------------------------------------------------------------------
def _set_form_and_breath(s: CoachingState, out: CoachingResult) -> None:
    # E16: 첫 세트 직전이면 셋업 체크리스트
    if s.세트번호 == 1 and s.운동종류 == "compound":
        out.셋업_체크리스트 = form_cues.e16_setup_checklist()
        out.add(RuleHit(form_cues.E16, summary="컴파운드 셋업 5단계", output=out.셋업_체크리스트))

    # E06~E12: 운동별 폼 큐 (외적 큐 우선 — E05)
    movement_cues = {
        "스쿼트":           (form_cues.E06, form_cues.e06_squat_cue()),
        "벤치프레스":       (form_cues.E07, form_cues.e07_bench_cue()),
        "데드리프트":       (form_cues.E08, form_cues.e08_deadlift_cue()),
        "오버헤드프레스":   (form_cues.E10, form_cues.e10_ohp_cue()),
        "OHP":              (form_cues.E10, form_cues.e10_ohp_cue()),
        "풀업":             (form_cues.E11, form_cues.e11_pullup_cue()),
        "친업":             (form_cues.E11, form_cues.e11_pullup_cue()),
        "바벨로우":         (form_cues.E12, form_cues.e12_barbell_row_cue()),
    }
    if s.운동명 in movement_cues:
        cite, cues = movement_cues[s.운동명]
        out.폼_큐.extend(cues)
        out.add(RuleHit(cite, summary=f"{s.운동명} 폼 큐", output=cues))
        # E05 외적 큐 우선 메타 룰 — 한 번만 기록
        out.add(RuleHit(form_cues.E05, summary="외적 큐 우선 사용", output=True))

    # E13: 호흡 (고혈압 시 자동 가드)
    has_htn = "고혈압" in s.질환
    out.호흡_가이드 = form_cues.e13_breathing_guide(s.현재무게_kg, s.최대무게_추정_kg, has_hypertension=has_htn)
    out.add(RuleHit(form_cues.E13, summary=out.호흡_가이드, output=out.호흡_가이드))

    # E17: 그립 가이드
    if s.운동명 in ("벤치프레스", "데드리프트", "풀업", "친업"):
        out.그립_가이드 = form_cues.e17_grip_guide(s.운동명)
        out.add(RuleHit(form_cues.E17, summary=out.그립_가이드, output=out.그립_가이드))

    # E03: VBT 데이터 있으면 속도 손실 임계 검사
    if s.렙별_바벨속도_ms:
        if form_cues.e03_should_stop_by_velocity(s.렙별_바벨속도_ms, "근력"):
            out.세트_종료_권고 = True
            out.add(RuleHit(form_cues.E03, summary="속도 손실 임계 도달", output=True))


# ---------------------------------------------------------------------------
# 5. 디로드 권고
# ---------------------------------------------------------------------------
def _check_deload(s: CoachingState, out: CoachingResult) -> None:
    # G02: 기본 트리거
    if deload.g02_basic_deload_trigger(s.최근_RPE_drift, s.관절통_NPRS):
        out.제안.append("이번 주말 디로드 권장 (G02)")
        out.add(RuleHit(deload.G02, summary="기본 디로드 트리거 발동", output=True))

    # G04: 주간 부하 +10% 검사
    cur_volume = sum(s.이번주_볼륨_세트.values())
    last_volume = sum(s.지난주_볼륨_세트.values())
    if last_volume > 0:
        gv = deload.g04_weekly_load_check(cur_volume, last_volume)
        if gv["초과"]:
            out.경고.append(gv["메모"])
            out.add(RuleHit(deload.G04, summary=gv["메모"], output=gv))

    # G07: 다지표
    sleep_under_6h = sum(1 for h in (s.최근_3일_수면_h or []) if h < 6.0)
    g7 = deload.g07_multi_indicator_deload(
        rpe_drift=s.최근_RPE_drift,
        weekly_sleep_under_6h_days=sleep_under_6h,
        joint_pain_nprs=s.관절통_NPRS,
        motivation_1_5=s.동기_1_5,
        days_since_last_pr=s.최근_PR_경과일,
    )
    if g7["권고_디로드"]:
        out.제안.append(f"다지표 디로드 권고: {', '.join(g7['히트'])}")
        out.add(RuleHit(deload.G07, summary="다지표 디로드 충족", output=g7))

    # B04: MRV 초과 검사
    if s.이번주_볼륨_세트:
        b = misc.b04_mrv_check(s.이번주_볼륨_세트)
        if b["권고_디로드"]:
            out.제안.append(f"MRV 초과: {', '.join(b['초과_근육군'])}")
            out.add(RuleHit(misc.B04, summary="근육군별 MRV 초과", output=b))


# ---------------------------------------------------------------------------
# 6. 보조 안내
# ---------------------------------------------------------------------------
def _aux_advice(s: CoachingState, out: CoachingResult) -> None:
    # K04: 수분 가이드 (세션 시작 시점에 한 번)
    if s.세트번호 == 1 and s.체중_kg > 0:
        ml = misc.k04_hydration_target_ml(s.체중_kg, session_minutes=60)
        out.제안.append(f"오늘 수분 목표 {ml}ml")
        out.add(RuleHit(misc.K04, summary=f"수분 {ml}ml/일", output=ml))
