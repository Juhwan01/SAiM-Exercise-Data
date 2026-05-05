"""운동 루틴 추천 진입 함수.

외부에서는 ``recommend_routine(profile)`` 만 호출. 내부에서 ``routine_rules/``
폴더의 97 룰을 정해진 순서로 적용한다.

순서:
    1. 안전 게이트 (L02-L08)
       — 차단 신호가 나오면 의료 의뢰만 남기고 처방 정지
    2. 레벨 분류 (L04)
    3. 영양 (K19-K22) — BMR/TDEE/목표 칼로리
    4. 분할/프로그램 선택 (D05 → D06/D07/D08/D09/D10)
    5. 시작 무게 (D11·D12 + D14 클램프) + 증량 폭 (D15)
    6. 강도/볼륨 처방 (C01-C04, C07, B02-B05)
    7. 주기화 / 디로드 (D01-D04, G01/G10/G05)
    8. 운동 선택 (J02-J05, J07, F05, I03)
    9. 워밍업 / 스트레칭 (I05-I08, P01-P05, E09)
    10. 카디오 (O01-O03)
    11. 회복 / 수면 (K05-K07)
    12. 부상 이력별 가산 (Q04-Q06 + J01)
    13. 한국 사용자 행동 조정 (R10) + 교육 메시지 (N02·N04·M03)
"""

from __future__ import annotations

from rule_engine.routine_rules import (
    cardio, exercise_select, injury_recovery, intensity, knowledge,
    nutrition, periodization, populations, recovery, rpe_meta,
    volume, warmup_stretch,
)
from rule_engine.types import RoutineRecommendation, RuleHit, UserProfile


# ============================================================================
# 진입
# ============================================================================
def recommend_routine(profile: UserProfile) -> RoutineRecommendation:
    """루틴 추천 1회 → 결과 묶음."""
    out = RoutineRecommendation()

    # ── 1. 안전 게이트 ─────────────────────────────────────
    if _gate_population_safety(profile, out):
        return out

    # ── 2. 레벨 분류 ───────────────────────────────────────
    _classify_level(profile, out)

    # ── 3. 영양 ────────────────────────────────────────────
    _compute_nutrition(profile, out)

    # ── 4. 분할/프로그램 선택 ─────────────────────────────
    _pick_program(profile, out)

    # ── 5. 시작 무게 + 증량 ────────────────────────────────
    _set_start_weights(profile, out)

    # ── 6. 강도/볼륨 처방 ─────────────────────────────────
    _set_intensity_volume(profile, out)

    # ── 7. 주기화 / 디로드 ────────────────────────────────
    _set_periodization(profile, out)

    # ── 8. 운동 선택 ──────────────────────────────────────
    _set_exercise_selection(profile, out)

    # ── 9. 워밍업/스트레칭 ────────────────────────────────
    _set_warmup_stretch(profile, out)

    # ── 10. 카디오 ────────────────────────────────────────
    _set_cardio(profile, out)

    # ── 11. 회복/수면 ─────────────────────────────────────
    _set_recovery(profile, out)

    # ── 12. 부상 이력별 가산 ──────────────────────────────
    _apply_injury_history(profile, out)

    # ── 13. 한국 행동 + 교육 ─────────────────────────────
    _add_behavior_and_education(profile, out)

    return out


# ============================================================================
# 1. 안전 게이트
# ============================================================================
def _gate_population_safety(p: UserProfile, out: RoutineRecommendation) -> bool:
    """L02-L08 검사. 차단 신호가 나오면 True 반환."""
    blocked = False

    # L02: 노인 (50+)
    if p.나이 >= 50 or "고령(50+)" in p.질환:
        prescription = populations.l02_elderly_prescription(p.나이)
        if prescription:
            out.add(RuleHit(populations.L02, summary="노인 처방 적용", output=prescription))
            out.경고.append("점진과부하 보수적 진행 — 8주 적응기 필요")

    # L03: 청소년 (<18)
    if p.나이 < 18 or "청소년(<18)" in p.질환:
        y = populations.l03_youth_prescription(p.나이)
        if y:
            out.add(RuleHit(populations.L03, summary="청소년 처방 — 1RM 테스트 잠금", output=y))
            out.경고.extend(y["주의"])

    # L05: 당뇨
    if "당뇨" in p.질환:
        d = populations.l05_diabetes_prescription()
        out.add(RuleHit(populations.L05, summary="당뇨 처방", output=d))
        out.경고.extend(d["회피_조건"])

    # L06: 고혈압
    if "고혈압" in p.질환:
        h = populations.l06_hypertension_prescription()
        out.add(RuleHit(populations.L06, summary="고혈압 처방", output=h))
        out.경고.append("Valsalva 회피 / 저항 RPE6 상한")
        # 적색기: 안정시 BP ≥ 180/110
        if (p.bp_sbp is not None and p.bp_sbp >= 180) or (p.bp_dbp is not None and p.bp_dbp >= 110):
            blocked = True
            out.안전_차단 = True
            out.차단_이유 = f"안정시 BP {p.bp_sbp}/{p.bp_dbp} ≥ 180/110"
            out.의료_의뢰.append("내과 진료 후 운동 시작")

    # L07: 이상지질혈증
    if "이상지질혈증" in p.질환:
        l = populations.l07_dyslipidemia_prescription()
        out.add(RuleHit(populations.L07, summary="이상지질혈증 처방", output=l))
        # LDL>190 → 부하검사
        if p.ldl is not None and p.ldl > 190:
            out.의료_의뢰.append("심혈관내과 운동부하검사 (LDL>190)")

    # L08: 골관절염
    if "골관절염_무릎" in p.질환 or "골관절염_고관절" in p.질환:
        oa = populations.l08_oa_prescription()
        out.add(RuleHit(populations.L08, summary="OA 처방", output=oa))
        out.경고.append(f"통증 NRS≤{oa['통증_NRS_상한']} 유지 / 회피 동작: {', '.join(oa['회피_동작'])}")

    return blocked


# ============================================================================
# 2. 레벨
# ============================================================================
def _classify_level(p: UserProfile, out: RoutineRecommendation) -> None:
    level = populations.l04_classify_level(p.훈련_월)
    if p.사용자레벨 != level:
        p.사용자레벨 = level
    out.add(RuleHit(populations.L04, summary=f"레벨: {level} (훈련 {p.훈련_월}개월)", output=level))


# ============================================================================
# 3. 영양 (BMR / TDEE / 목표 칼로리)
# ============================================================================
def _compute_nutrition(p: UserProfile, out: RoutineRecommendation) -> None:
    # K19 / K20 자동 분기
    if p.체지방률_pct is not None:
        bmr = nutrition.k20_bmr_katch(p.체중_kg, p.체지방률_pct)
        out.add(RuleHit(nutrition.K20, summary=f"BMR {bmr}kcal (Katch-McArdle)", output=bmr))
    else:
        bmr = nutrition.k19_bmr_mifflin(p.성별, p.체중_kg, p.키_cm, p.나이)
        out.add(RuleHit(nutrition.K19, summary=f"BMR {bmr}kcal (Mifflin)", output=bmr))
    out.BMR_kcal = bmr

    # K22 → K21
    cat = nutrition.k22_classify_activity(p.직업유형, p.추가_운동빈도)
    tdee = nutrition.k21_tdee(bmr, cat)
    out.add(RuleHit(nutrition.K22, summary=f"활동: {cat}", output=cat))
    out.add(RuleHit(nutrition.K21, summary=f"TDEE {tdee}kcal (BMR × {cat})", output=tdee))
    out.TDEE_kcal = tdee

    # 목표 칼로리: 다이어트 -500, 벌크업 +300, 근육량 증가 +200, 그 외 유지
    delta = {"다이어트": -500, "벌크업": 300, "근육량 증가": 200}.get(p.목표, 0)
    out.목표_칼로리 = tdee + delta


# ============================================================================
# 4. 분할/프로그램
# ============================================================================
def _pick_program(p: UserProfile, out: RoutineRecommendation) -> None:
    # D05: 분할
    split = periodization.d05_pick_split(p.주가용일, p.사용자레벨)
    out.분할_형태 = split
    out.add(RuleHit(periodization.D05, summary=f"분할: {split}", output=split))

    # D06/D07/D08/D09/D10 — 레벨 + 목표 + 가용일에 따라
    program: dict
    cite = periodization.D06
    if p.사용자레벨 == "초보":
        program = periodization.d06_starting_strength()
        cite = periodization.D06
    elif p.목표 == "스트렝스" and p.사용자레벨 == "중급":
        program = periodization.d07_531(p.one_rm_kg or {"스쿼트": 80, "벤치프레스": 50, "데드리프트": 100, "오버헤드프레스": 30})
        cite = periodization.D07
    elif p.목표 == "스트렝스":
        program = periodization.d08_gzclp()
        cite = periodization.D08
    elif p.목표 in ("벌크업", "근육량 증가") and p.사용자레벨 == "중급" and p.주가용일 >= 4:
        program = periodization.d10_phul_phat(p.주가용일)
        cite = periodization.D10
    else:
        program = periodization.d06_starting_strength()
        cite = periodization.D06

    out.추천_프로그램 = program["이름"]
    out.add(RuleHit(cite, summary=f"프로그램: {program['이름']}", output=program))

    # 주간 스케줄 표시 (D06 케이스)
    if "A루틴" in program:
        days = ["월", "수", "금"][:p.주가용일]
        for i, d in enumerate(days):
            routine = "A루틴" if i % 2 == 0 else "B루틴"
            out.주간_스케줄.append(f"{d}: {routine}")


# ============================================================================
# 5. 시작 무게
# ============================================================================
def _set_start_weights(p: UserProfile, out: RoutineRecommendation) -> None:
    if p.사용자레벨 != "초보":
        # 중급+ 사용자는 자기 1RM 기반
        if p.one_rm_kg:
            out.시작_무게_kg = {m: round(rm * 0.8, 1) for m, rm in p.one_rm_kg.items()}
        return

    # D11/D12: 초보 디폴트 시작 무게
    if p.성별 == "남":
        weights = periodization.d11_male_start_weights()
        out.add(RuleHit(periodization.D11, summary="남성 초보 시작 무게", output=weights))
    else:
        weights = periodization.d12_female_start_weights(p.헬스장_여성바_15kg)
        out.add(RuleHit(periodization.D12, summary="여성 초보 시작 무게", output=weights))

    # D14: 첫 세션 워크셋 상한 클램프 (체중 비례)
    clamped = {}
    for movement, kg in weights.items():
        new_kg, msg = periodization.d14_clamp_first_workset(kg, movement, p.성별, p.체중_kg)
        clamped[movement] = new_kg
        if msg:
            out.add(RuleHit(periodization.D14, summary=msg, output=new_kg))
    out.시작_무게_kg = clamped

    # D15: 증량 폭
    out.증량_폭_kg = {m: periodization.d15_increment_by_movement(m, is_early_phase=True) for m in clamped}
    out.add(RuleHit(periodization.D15, summary="초기 증량 폭 (하체 +10/상체 +5)", output=out.증량_폭_kg))


# ============================================================================
# 6. 강도 / 볼륨
# ============================================================================
def _set_intensity_volume(p: UserProfile, out: RoutineRecommendation) -> None:
    # C02: 목표 → 렙범위 + %1RM
    cont = intensity.c02_continuum(p.목표)
    out.렙범위 = cont["렙범위"]
    out.pct_1rm범위 = cont["pct"]
    out.add(RuleHit(intensity.C02, summary=f"렙 {cont['렙범위']}, %1RM {cont['pct']}", output=cont))

    # C05: RIR
    out.세트당_RIR = intensity.c05_default_rir("compound")
    out.add(RuleHit(intensity.C05, summary=f"기본 RIR {out.세트당_RIR}", output=out.세트당_RIR))

    # C06: 빈도
    out.근육군당_주빈도 = intensity.c06_min_frequency_per_muscle()

    # C07: 휴식
    out.휴식_초 = intensity.c07_rest_table(p.목표)
    out.add(RuleHit(intensity.C07, summary=f"휴식 {out.휴식_초}", output=out.휴식_초))

    # B02: 시작 볼륨 (근육군별)
    main_muscles = ["가슴", "등", "어깨", "다리", "이두", "삼두"]
    out.근육군별_주간세트 = {m: volume.b02_starting_volume(m) for m in main_muscles}
    out.add(RuleHit(volume.B02, summary="MEV 시작 볼륨", output=out.근육군별_주간세트))

    # B05: 권장 볼륨 범위 안내
    rng = volume.b05_recommended_volume_range(p.목표)
    out.add(RuleHit(volume.B05, summary=f"주당 권장 {rng[0]}~{rng[1]}세트", output=rng))


# ============================================================================
# 7. 주기화 / 디로드
# ============================================================================
def _set_periodization(p: UserProfile, out: RoutineRecommendation) -> None:
    # D01/D02 — 레벨에 맞는 주기화
    if p.사용자레벨 == "초보":
        # LP만 사용 (I01)
        out.add(RuleHit(knowledge.I01, summary="초보 — Linear Progression 사용", output=True))
    elif p.사용자레벨 == "중급":
        out.add(RuleHit(periodization.D02, summary="중급+ → DUP", output=periodization.d02_weekly_dup()))
    else:
        out.add(RuleHit(periodization.D03, summary="고급 → Block Periodization",
                        output=periodization.d03_block_schedule()))

    # G01 / G10 — 디로드 주기
    cycle = recovery.g01_deload_cycle()
    korean = recovery.g10_korean_deload_cycle(p.사용자레벨)
    out.디로드_주기_주 = korean["기본_주기_주"] or 5
    out.메조_주차수 = (out.디로드_주기_주 or 5) + 1   # 5주 훈련 + 1주 디로드
    out.add(RuleHit(recovery.G01, summary=f"디로드 {cycle['디로드_일']}일", output=cycle))
    out.add(RuleHit(recovery.G10, summary=f"한국 사용자 디로드 {out.디로드_주기_주}주", output=korean))

    # G05 처방 미리 채움 (디로드 주가 오면 적용)
    avg_weight = {m: w for m, w in out.시작_무게_kg.items()}
    avg_sets = out.근육군별_주간세트.copy()
    out.디로드_처방 = recovery.g05_deload_quantitative(avg_sets, avg_weight)


# ============================================================================
# 8. 운동 선택
# ============================================================================
def _set_exercise_selection(p: UserProfile, out: RoutineRecommendation) -> None:
    # J05: 컴파운드/아이솔 비율
    ratio = exercise_select.j05_compound_isolation_ratio(p.사용자레벨)
    out.컴파운드_아이솔_비율 = ratio
    out.add(RuleHit(exercise_select.J05, summary=f"컴파운드:아이솔 {ratio[0]}:{ratio[1]}", output=ratio))

    # J03: 자유중량/머신 비율
    fw_m = exercise_select.j03_freeweight_machine_ratio(p.사용자레벨, p.목표,
                                                        prefer_safety=("당뇨" in p.질환 or "고혈압" in p.질환))
    out.add(RuleHit(exercise_select.J03, summary=f"자유중량:머신 {fw_m[0]}:{fw_m[1]}", output=fw_m))

    # J02: 장비 환경에 맞는 운동 풀
    pool = {
        "스쿼트": ["백스쿼트"], "벤치프레스": ["벤치프레스"], "데드리프트": ["데드리프트"],
        "OHP": ["OHP"], "바벨로우": ["바벨로우"], "풀업": ["풀업"],
    }
    filtered = {k: [exercise_select.j02_filter_by_equipment(k, p.장비)] for k in pool}
    out.운동_풀 = filtered
    out.add(RuleHit(exercise_select.J02, summary="장비 매칭", output=list(filtered.keys())))

    # I03: 운동 순서
    main_movements = list(filtered.keys())
    out.운동_순서 = exercise_select.i03_order_session(main_movements)
    out.add(RuleHit(exercise_select.I03, summary="컴파운드 우선 정렬", output=out.운동_순서))

    # F05/J01: 부상 부위가 있으면 대체 운동 자동 매핑
    for inj in p.부상이력:
        site = inj.split("_")[0]
        for mv in main_movements:
            alt = exercise_select.j01_alternatives(site, mv)
            if alt:
                out.대체_운동.setdefault(mv, []).extend(alt)
                out.add(RuleHit(exercise_select.J01, summary=f"{mv}→{alt[0]} ({site} 부상)", output=alt))


# ============================================================================
# 9. 워밍업 / 스트레칭
# ============================================================================
def _set_warmup_stretch(p: UserProfile, out: RoutineRecommendation) -> None:
    # I05
    out.일반_워밍업 = warmup_stretch.i05_general_warmup(p.세션가용분)
    out.add(RuleHit(warmup_stretch.I05, summary=out.일반_워밍업, output=out.일반_워밍업))

    # I06: 컴파운드 워크업 (스쿼트 시작 무게 기준 예시)
    if "스쿼트" in out.시작_무게_kg:
        wu = warmup_stretch.i06_compound_warmup(out.시작_무게_kg["스쿼트"])
        out.특이적_워밍업 = [f"{x['무게']}kg × {x['렙']}렙 × {x['세트']}세트" for x in wu]
        out.add(RuleHit(warmup_stretch.I06, summary="컴파운드 워크업", output=wu))

    # P01/P05: 정적 스트레칭 회피
    out.add(RuleHit(warmup_stretch.P01, summary="워밍업 정적 스트레칭 회피, 동적 우선",
                    output=warmup_stretch.p01_warmup_stretch_policy()))
    out.스트레칭_가이드.append(warmup_stretch.p05_warmup_static_warning())
    out.add(RuleHit(warmup_stretch.P05, summary="P05 경고", output=None))

    # P03: SMR 30~60s/부위
    out.스트레칭_가이드.append("폼롤러 30~60초/부위 (P03)")

    # P04: 모빌리티
    out.스트레칭_가이드.extend(warmup_stretch.p04_default_mobility())


# ============================================================================
# 10. 카디오
# ============================================================================
def _set_cardio(p: UserProfile, out: RoutineRecommendation) -> None:
    # 다이어트/건강증진은 카디오 권장, 그 외는 보조
    weekly_freq = 2 if p.목표 in ("다이어트", "건강증진") else 1
    minutes = 30
    interference = cardio.o01_interference_check(weekly_freq, minutes)
    modality = cardio.o02_pick_modality(p.주가용일, p.세션가용분)
    placement = cardio.o03_cardio_placement(strength_focus=True, leg_day=False)
    out.카디오_권고 = f"{modality}, {placement}"
    out.add(RuleHit(cardio.O01, summary="간섭 검사", output=interference))
    out.add(RuleHit(cardio.O02, summary=f"카디오 모드: {modality}", output=modality))
    out.add(RuleHit(cardio.O03, summary=placement, output=placement))


# ============================================================================
# 11. 회복 / 수면
# ============================================================================
def _set_recovery(p: UserProfile, out: RoutineRecommendation) -> None:
    out.수면_권장_h = recovery.k05_sleep_target(p.나이)
    out.add(RuleHit(recovery.K05, summary=f"수면 {out.수면_권장_h[0]}~{out.수면_권장_h[1]}h", output=out.수면_권장_h))

    out.add(RuleHit(recovery.K06, summary="수면 <8h 시 부상 위험 1.7배", output=recovery.k06_warning_threshold()))

    ar = recovery.k07_active_recovery()
    out.능동_회복 = f"{ar['분'][0]}~{ar['분'][1]}분 저강도 ({', '.join(ar['예시'])})"
    out.add(RuleHit(recovery.K07, summary="능동 회복", output=ar))


# ============================================================================
# 12. 부상 이력별 가산
# ============================================================================
def _apply_injury_history(p: UserProfile, out: RoutineRecommendation) -> None:
    for inj in p.부상이력:
        if inj.startswith("허리"):
            r = injury_recovery.q04_low_back_protocol(days_since_onset=30, pain_nprs=2)
            out.add(RuleHit(injury_recovery.Q04, summary=f"요추 {r['단계']}", output=r))
            if r.get("차단"):
                out.안전_차단 = True
                out.차단_이유 = r["이유"]
                out.의료_의뢰.append(r["의뢰"])
        elif inj.startswith("어깨"):
            r = injury_recovery.q05_shoulder_protocol(days_since_onset=30, pain_nprs=2)
            out.add(RuleHit(injury_recovery.Q05, summary=f"어깨 {r['단계']}", output=r))
        elif inj.startswith("무릎"):
            r = injury_recovery.q06_pfps_protocol(days_since_onset=30, pain_nprs=2)
            out.add(RuleHit(injury_recovery.Q06, summary=f"무릎 {r['단계']}", output=r))


# ============================================================================
# 13. 행동 + 교육
# ============================================================================
def _add_behavior_and_education(p: UserProfile, out: RoutineRecommendation) -> None:
    # R10: 한국 직장인 행동
    sched = knowledge.r10_korean_schedule_advice(has_dinner_today=False, available_days=p.주가용일)
    out.한국_사용자_조정.append(f"주간 볼륨 조정: {sched['주간_볼륨_조정']}")
    out.add(RuleHit(knowledge.R10, summary="한국 직장인 가이드", output=sched))

    # N02: 신경 적응 vs 근비대 기대값
    n02_msg = knowledge.n02_expectation_message(p.훈련_월)
    out.교육_메시지.append(n02_msg)
    out.add(RuleHit(knowledge.N02, summary=n02_msg, output=n02_msg))

    # N04: 렙범위 교육
    n04_msg = knowledge.n04_rep_range_education()
    out.교육_메시지.append(n04_msg)
    out.add(RuleHit(knowledge.N04, summary=n04_msg, output=n04_msg))

    # M03: 측정 방법
    measure = knowledge.m03_pick_method(p.사용자레벨, p.나이)
    out.교육_메시지.append(f"1RM 측정: {measure}")
    out.add(RuleHit(knowledge.M03, summary=f"측정 방식: {measure}", output=measure))
