"""실시간 코칭 통합 테스트.

각 룰 카드의 `활용_예시` 또는 한줄설명에 박힌 숫자를 그대로 검증한다.
출처가 변경되거나 룰 카드가 바뀌면 여기서 먼저 깨진다.
"""

from __future__ import annotations

from rule_engine import realtime_coaching
from rule_engine.coaching_rules import deload, form_cues, misc, progression, rpe, safety
from rule_engine.types import CoachingState


# --------------------------------------------------------------------------
# 룰 카드 한줄설명/활용예시 직접 검증
# --------------------------------------------------------------------------
def test_a11_helms_card_example():
    # rules/A11.yaml 활용예시: 5렙 RPE8 + 입력 RPE9 → 100kg → 96kg
    assert rpe.a11_helms_set_to_set(8, 9, 100) == 96.0
    # 활용예시: RPE7 입력 → 100kg → 104kg
    assert rpe.a11_helms_set_to_set(8, 7, 100) == 104.0


def test_a07_rts_card_example():
    # rules/A07.yaml 한줄설명: 5렙 RPE8 = 81.1
    assert rpe.a07_pct_1rm(5, 8.0) == 81.1
    # 1렙 RPE10 = 100
    assert rpe.a07_pct_1rm(1, 10.0) == 100.0


def test_a08_rir_mapping_card():
    # rules/A08.yaml 한줄설명: RPE9 = 1 RIR, RPE 8.5 = 1.5 RIR
    assert rpe.a08_precise_rir(9.0) == 1.0
    assert rpe.a08_precise_rir(8.5) == 1.5


def test_d15_increment_card_example():
    # rules/D15.yaml 활용예시: 60kg 스쿼트 5x5 성공 → 다음 세션 62.5kg... 잠깐
    # 룰카드 한줄설명에는 하체 +5kg 이라고 명시. 활용예시는 일반화 표현.
    assert progression.d15_next_weight("스쿼트", True, 60) == 65.0
    assert progression.d15_next_weight("벤치프레스", True, 60) == 62.5


def test_c07_rest_card():
    # rules/C07.yaml: 근력 3~5분, 컴파운드 근비대 2~3분, 아이솔 1~2분
    assert misc.c07_rest_seconds("compound", "스트렝스") == 240
    assert misc.c07_rest_seconds("compound", "근육량 증가") == 150
    assert misc.c07_rest_seconds("isolation", "근육량 증가") == 90


def test_g04_card_threshold():
    # rules/G04.yaml: 주간 +10% 이내. +15% 이상 경고
    assert deload.g04_weekly_load_check(115, 100)["초과"] is True
    assert deload.g04_weekly_load_check(110, 100)["초과"] is False


def test_g07_multi_indicator():
    # rules/G07.yaml: ≥2개 충족 시 디로드 권고
    g = deload.g07_multi_indicator_deload(rpe_drift=1.7, weekly_sleep_under_6h_days=4)
    assert g["권고_디로드"] is True
    g2 = deload.g07_multi_indicator_deload(rpe_drift=0.5)
    assert g2["권고_디로드"] is False


def test_l05_acute_red_flag():
    # rules/L05.yaml 적색기: 공복혈당>250 + 케톤(+) → 운동 보류
    r = safety.l05_diabetes_gate(True, fasting_glucose_mgdl=280, ketone_positive=True)
    assert r["차단"] is True


def test_l06_resting_bp_red_flag():
    # rules/L06.yaml: 안정시 BP≥180/110 → 운동 보류
    r = safety.l06_hypertension_gate(True, resting_sbp=200)
    assert r["차단"] is True


def test_q01_acute_phase():
    # rules/Q01.yaml: 급성기 0~3d (72h)
    assert safety.q01_acute_injury_protocol(24)["차단"] is True
    assert safety.q01_acute_injury_protocol(72.5)["차단"] is False


# --------------------------------------------------------------------------
# 진입 함수 통합 시나리오
# --------------------------------------------------------------------------
def test_normal_session_returns_recommendation():
    state = CoachingState(
        운동명="스쿼트", 운동종류="compound", 근육군="lower_compound",
        세트번호=2, 현재무게_kg=100.0, 최대무게_추정_kg=130.0,
        목표RPE=8.0, 목표렙=5, 입력RPE=9.0, 사용자레벨="중급", 체중_kg=70,
    )
    r = realtime_coaching(state)
    assert r.차단됨 is False
    assert r.다음_무게_kg is not None and r.다음_무게_kg < 100   # RPE 9 입력 → 무게↓
    assert r.휴식_초 == 150
    assert r.호흡_가이드 is not None
    assert len(r.발동_룰) >= 5
    assert all(h.citation.url.startswith("http") for h in r.발동_룰)


def test_acute_injury_blocks_session():
    state = CoachingState(
        운동명="스쿼트", 운동종류="compound", 통증부위="무릎",
        통증_시작_h=2.0, 통증패턴="예리한", 통증강도_0_10=7,
        현재무게_kg=80,
    )
    r = realtime_coaching(state)
    assert r.차단됨 is True
    assert "PEACE" in (r.차단_이유 or "")
    assert any("Protect" in s for s in r.제안)


def test_hypertension_caps_rpe_and_blocks_valsalva():
    state = CoachingState(
        운동명="데드리프트", 운동종류="compound", 세트번호=1,
        현재무게_kg=100, 최대무게_추정_kg=120,
        목표RPE=8, 목표렙=5, 사용자레벨="중급", 체중_kg=75,
        질환=["고혈압"],
    )
    r = realtime_coaching(state)
    assert "금지" in (r.호흡_가이드 or "")
    assert any("Valsalva" in w for w in r.경고)


def test_oa_warns_about_avoid_movements():
    state = CoachingState(
        운동명="깊은_스쿼트", 운동종류="compound", 통증강도_0_10=3,
        질환=["골관절염_무릎"], 목표RPE=8,
        현재무게_kg=60, 최대무게_추정_kg=80,
    )
    r = realtime_coaching(state)
    assert any("OA 회피" in w or "회피 동작" in w for w in r.경고)


def test_deload_triggers_aggregate():
    state = CoachingState(
        운동명="스쿼트", 운동종류="compound", 세트번호=1,
        현재무게_kg=100, 최대무게_추정_kg=130, 목표RPE=8,
        최근_RPE_drift=2.2, 관절통_NPRS=4,
        이번주_볼륨_세트={"가슴": 24}, 지난주_볼륨_세트={"가슴": 18},
    )
    r = realtime_coaching(state)
    assert any("디로드" in s for s in r.제안)
    assert any("가슴" in s for s in r.제안)


# --------------------------------------------------------------------------
# 인라인 러너 (pytest 없이도 실행 가능)
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import inspect, sys
    fns = [(n, f) for n, f in inspect.getmembers(sys.modules[__name__])
           if n.startswith("test_") and callable(f)]
    failed = 0
    for n, f in fns:
        try:
            f()
            print(f"PASS  {n}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {n}  ({e})")
    print(f"\n{len(fns)-failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
