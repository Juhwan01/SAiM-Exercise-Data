"""운동 루틴 추천 통합 테스트.

각 룰 카드의 활용예시·한줄설명 숫자를 진입 함수 결과에서 직접 검증한다.
"""

from __future__ import annotations

from rule_engine import recommend_routine
from rule_engine.routine_rules import (
    cardio, exercise_select, intensity, knowledge, nutrition,
    periodization, populations, recovery, rpe_meta, volume, warmup_stretch,
)
from rule_engine.types import UserProfile


# --------------------------------------------------------------------------
# 룰 카드 활용예시 직접 검증
# --------------------------------------------------------------------------
def test_k19_card_example():
    # 룰 카드 예시: 70kg/175cm/30세 남 BMR ≈ 1649
    assert nutrition.k19_bmr_mifflin("남", 70, 175, 30) == 1649


def test_k21_card_example():
    # 룰 카드: BMR 1648 × 1.375 = 2266
    assert nutrition.k21_tdee(1648, "가벼움") == int(round(1648 * 1.375))


def test_l04_card_thresholds():
    # 룰 카드: 초보 <6개월, 중급 6~24개월, 고급 24+
    assert populations.l04_classify_level(3) == "초보"
    assert populations.l04_classify_level(6) == "중급"
    assert populations.l04_classify_level(24) == "고급"


def test_d11_male_starting_weights():
    # 룰 카드: 남성 초보 빅3+OHP — 빈 봉 20kg, 데드 40kg
    w = periodization.d11_male_start_weights()
    assert w["스쿼트"] == 20.0 and w["데드리프트"] == 40.0


def test_d12_female_starting_weights_with_15kg_bar():
    # 룰 카드: 15kg 여성용 바 있으면 우선
    w = periodization.d12_female_start_weights(has_15kg_bar=True)
    assert w["스쿼트"] == 15.0


def test_d05_pick_split():
    # 룰 카드: 풀바디(2~3) 초보, 상하분할(4) 중급, PPL(5~6) 고급
    assert "풀바디" in periodization.d05_pick_split(3, "초보")
    assert "상하분할" in periodization.d05_pick_split(4, "중급")
    assert "PPL" in periodization.d05_pick_split(5, "중급")


def test_c01_card_examples():
    # 룰 카드: 5RM=87%, 8RM=80%, 10RM=75%, 12RM=67%
    assert intensity.c01_pct_for_reps(5) == 87.0
    assert intensity.c01_pct_for_reps(8) == 80.0
    assert intensity.c01_pct_for_reps(10) == 75.0


def test_c09_epley_card():
    # 1RM = 무게 × (1 + 렙수/30)
    assert intensity.c09_epley_1rm(100, 8) == round(100 * (1 + 8 / 30), 1)


def test_c14_reset_card():
    # Reset = -10%
    assert intensity.c14_reset(100) == 90.0


def test_b02_starting_volume_card():
    # 한줄설명: 가슴 8, 등 10
    assert volume.b02_starting_volume("가슴") == 8
    assert volume.b02_starting_volume("등") == 10


def test_b05_volume_range_card():
    # 한줄설명: 12~20세트 권장
    assert volume.b05_recommended_volume_range("벌크업") == (12, 20)


def test_g01_deload_card():
    # 디로드 = 5~7일, 평균 4~6주마다
    c = recovery.g01_deload_cycle()
    assert c["디로드_일"] == (5, 7) and c["주기_주"] == (4, 6)


def test_q04_red_flags():
    # 적색기 신호: 안장마비 → 차단·신경외과
    r = injury_recovery_q04 = __import__("rule_engine.routine_rules.injury_recovery",
                                         fromlist=["q04_low_back_protocol"]).q04_low_back_protocol(
        days_since_onset=1, pain_nprs=6, red_flags=["안장마비"]
    )
    assert r["차단"] is True
    assert "응급실" in r["의뢰"] or "신경외과" in r["의뢰"]


def test_a07_session_pct():
    # 룰 카드: 5렙 RPE 8 = 81.1%
    assert rpe_meta.a07_session_pct(5, 8.0) == 81.1


# --------------------------------------------------------------------------
# 진입 함수 통합 시나리오
# --------------------------------------------------------------------------
def test_beginner_male_bulk_returns_full_routine():
    p = UserProfile(
        성별="남", 체중_kg=70, 키_cm=175, 나이=30,
        훈련_월=2, 목표="벌크업", 주가용일=3, 세션가용분=60,
    )
    r = recommend_routine(p)

    assert r.안전_차단 is False
    assert r.BMR_kcal == 1649
    assert r.TDEE_kcal is not None and r.TDEE_kcal > r.BMR_kcal
    assert r.목표_칼로리 is not None and r.목표_칼로리 > r.TDEE_kcal   # 벌크는 +
    assert r.추천_프로그램 == "Starting Strength"
    assert r.분할_형태 == "풀바디_주3"
    assert "월: A루틴" in r.주간_스케줄
    assert r.시작_무게_kg["스쿼트"] == 20.0
    assert r.증량_폭_kg["스쿼트"] == 10.0   # 초기 +10kg
    assert r.렙범위 == (6, 12)
    assert r.디로드_주기_주 is not None
    assert len(r.발동_룰) > 20
    # 모든 룰에 출처 URL 박혀있는지
    assert all(h.citation.url.startswith("http") for h in r.발동_룰)


def test_hypertension_with_high_bp_blocks():
    p = UserProfile(
        성별="남", 체중_kg=80, 키_cm=170, 나이=55,
        훈련_월=0, 목표="건강증진", 주가용일=3,
        질환=["고혈압"], bp_sbp=200, bp_dbp=115,
    )
    r = recommend_routine(p)
    assert r.안전_차단 is True
    assert "BP" in (r.차단_이유 or "")
    assert "내과" in r.의료_의뢰[0]


def test_diabetes_includes_warnings():
    p = UserProfile(
        성별="여", 체중_kg=65, 키_cm=160, 나이=45,
        훈련_월=12, 목표="다이어트", 주가용일=4,
        질환=["당뇨"],
    )
    r = recommend_routine(p)
    assert any("RPE" in w or "혈당" in w or "유산소" in w or "Valsalva" in w
               for w in r.경고 + sum([h.summary for h in r.발동_룰 if isinstance(h.summary, list)], []))
    # L05 룰이 발동되어야 함
    assert any(h.citation.rule_id == "L05" for h in r.발동_룰)


def test_oa_knee_includes_avoid_movements():
    p = UserProfile(
        성별="남", 체중_kg=80, 키_cm=175, 나이=55,
        훈련_월=6, 목표="건강증진", 주가용일=3,
        질환=["골관절염_무릎"],
    )
    r = recommend_routine(p)
    assert any(h.citation.rule_id == "L08" for h in r.발동_룰)
    assert any("회피" in w for w in r.경고)


def test_intermediate_strength_uses_531():
    p = UserProfile(
        성별="남", 체중_kg=85, 키_cm=180, 나이=35,
        훈련_월=18, 목표="스트렝스", 주가용일=4,
        one_rm_kg={"스쿼트": 130, "벤치프레스": 90, "데드리프트": 160},
    )
    r = recommend_routine(p)
    assert r.추천_프로그램 == "5/3/1 Wendler"
    # 1RM 80% 가 시작 무게
    assert r.시작_무게_kg["스쿼트"] == round(130 * 0.8, 1)


def test_evidence_urls_present_for_every_hit():
    p = UserProfile(성별="남", 체중_kg=70, 키_cm=175, 나이=30, 훈련_월=2,
                    목표="벌크업", 주가용일=3)
    r = recommend_routine(p)
    for h in r.발동_룰:
        c = h.citation
        assert c.rule_id and c.url and c.confidence
        assert c.url.startswith(("http://", "https://"))


# --------------------------------------------------------------------------
# 인라인 러너
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
        except Exception as e:
            failed += 1
            print(f"ERROR {n}  ({type(e).__name__}: {e})")
    print(f"\n{len(fns)-failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
