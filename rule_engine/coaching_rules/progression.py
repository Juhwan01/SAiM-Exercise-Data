"""실시간 코칭 — 진행/증량 룰 (5개): I01, I04, C08, D14, D15.

세트가 끝났을 때 다음 세션의 무게/렙 결정에 쓰인다.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# I01 — 초보자 Linear Progression
# ----------------------------------------------------------------------------
# rules/I01.yaml | csv 91행
# 출처: Mark Rippetoe (Starting Strength)
# URL : https://startingstrength.com/get-started/programs  ★★★
# ============================================================================
I01 = Citation(
    rule_id="I01", name="초보자 Linear Progression",
    source="Rippetoe (Starting Strength)",
    url="https://startingstrength.com/get-started/programs",
    confidence="★★★",
)

def i01_should_use_linear(level: str, training_months: int) -> bool:
    """I01: 초보(<6개월)이면 자율조절 끄고 LP 사용. 그 외엔 자율조절."""
    return level == "초보" or training_months < 6


# ============================================================================
# I04 — ACWR (급성/만성 부하비)
# ----------------------------------------------------------------------------
# rules/I04.yaml | csv 94행
# 출처: Gabbett 2016
# URL : https://www.scienceforsport.com/acutechronic-workload-ratio/  ★★☆
#
# 7일 부하 / 28일 부하. 0.8~1.3 안전, 1.5+ 부상 위험.
# ============================================================================
I04 = Citation(
    rule_id="I04", name="ACWR (급성/만성 부하비)",
    source="Gabbett 2016",
    url="https://www.scienceforsport.com/acutechronic-workload-ratio/",
    confidence="★★☆",
)

def i04_acwr(load_7d: float, load_28d: float) -> dict:
    """I04: ACWR 계산 + 라벨."""
    if load_28d <= 0:
        return {"acwr": 0.0, "라벨": "데이터부족"}
    acwr = load_7d / (load_28d / 4)   # 7d / (28d 평균 주당 부하)
    if acwr < 0.8:
        return {"acwr": round(acwr, 2), "라벨": "저부하_적응부족"}
    if acwr > 1.5:
        return {"acwr": round(acwr, 2), "라벨": "고부상위험"}
    if acwr > 1.3:
        return {"acwr": round(acwr, 2), "라벨": "주의"}
    return {"acwr": round(acwr, 2), "라벨": "안전"}


# ============================================================================
# C08 — Double Progression
# ----------------------------------------------------------------------------
# rules/C08.yaml | csv 27행
# 출처: Legion / Bret Contreras
# URL : https://legionathletics.com/double-progression/  ★★★
#
# 렙 범위 처방. 모든 세트가 상한 도달 → 무게 +2.5~5% 인상, 렙 하한 리셋.
# ============================================================================
C08 = Citation(
    rule_id="C08", name="Double Progression",
    source="Legion / Bret Contreras",
    url="https://legionathletics.com/double-progression/",
    confidence="★★★",
)

def c08_double_progression(
    all_sets_hit_upper_rep: bool,
    current_kg: float,
    current_reps: int,
    rep_range: tuple[int, int] = (8, 12),
    increment_pct: float = 0.025,
) -> tuple[float, int]:
    """C08: 모든 세트가 상한 렙 달성 → 무게 인상 + 렙 하한 리셋.

    Returns:
        (다음_무게_kg, 다음_시작_렙)
    """
    lower, upper = rep_range
    if all_sets_hit_upper_rep:
        next_w = round(current_kg * (1 + increment_pct), 1)
        return next_w, lower
    # 상한 미달이면 무게 유지·렙 +1 시도
    return current_kg, min(current_reps + 1, upper)


# ============================================================================
# D14 — 초보자 첫 세션 워크셋 상한 가이드
# ----------------------------------------------------------------------------
# rules/D14.yaml | csv 36행
# 출처: Rippetoe (Starting Strength: Basic Barbell Training)
# URL : https://startingstrength.com/article/incremental_increases  ★★☆
#
# 평균 체중 완전 초보 남성이 첫 스쿼트 워크셋에서 65kg(145lb) 5x3 을 넘는 경우는 드물다.
# 사용자가 80kg 입력 시 "첫날엔 65kg 정도가 적정" 으로 다운그레이드.
# ============================================================================
D14 = Citation(
    rule_id="D14", name="초보자 첫 세션 워크셋 상한",
    source="Rippetoe (Starting Strength)",
    url="https://startingstrength.com/article/incremental_increases",
    confidence="★★☆",
)

def d14_clamp_first_workset(
    requested_kg: float,
    movement: str,
    sex: str,
    body_weight_kg: float,
    is_first_session: bool,
) -> tuple[float, str | None]:
    """D14: 사용자 입력 무게가 초보 첫 세션 상한을 넘으면 클램프.

    Returns:
        (클램프된 무게, 메모(있으면))
    """
    if not is_first_session:
        return requested_kg, None
    # 룰 카드 기준은 평균 체중 남성 스쿼트 65kg. 다른 종목/성별은 비례 조정.
    base_caps = {  # (남, 여)
        "스쿼트":     (65.0, 35.0),
        "데드리프트": (70.0, 40.0),
        "벤치프레스": (40.0, 25.0),
        "오버헤드프레스": (30.0, 18.0),
    }
    male_cap, female_cap = base_caps.get(movement, (60.0, 30.0))
    cap = male_cap if sex == "남" else female_cap
    # 평균 체중 70kg(남)/55kg(여) 기준에서 비례 보정
    ref = 70.0 if sex == "남" else 55.0
    cap = cap * (body_weight_kg / ref)
    if requested_kg > cap:
        return round(cap, 1), f"첫 세션 상한 — {movement} {round(cap,1)}kg 권장"
    return requested_kg, None


# ============================================================================
# D15 — 초보자 증량 폭(점프) 디폴트
# ----------------------------------------------------------------------------
# rules/D15.yaml | csv 37행
# 출처: Rippetoe "Incremental Increases"
# URL : https://startingstrength.com/article/incremental_increases  ★★☆
#
# 하체(스쿼트·데드): 세션당 +5kg (초기 +10kg 가능)
# 상체(벤치·OHP·로우): +2.5kg (초기 +5kg)
# 실패 시 절반 또는 디로드.
# ============================================================================
D15 = Citation(
    rule_id="D15", name="초보자 증량 폭",
    source="Rippetoe",
    url="https://startingstrength.com/article/incremental_increases",
    confidence="★★☆",
)

_D15_LOWER = ("스쿼트", "데드리프트")
_D15_UPPER = ("벤치프레스", "오버헤드프레스", "바벨로우", "OHP")

def d15_next_weight(
    movement: str,
    last_session_success: bool,
    current_kg: float,
    is_early_phase: bool = False,    # True 면 처음 몇 주(초기 +10/+5kg)
) -> float:
    """D15: 다음 세션 무게 자동 계산."""
    is_lower = movement in _D15_LOWER or any(m in movement for m in _D15_LOWER)
    if last_session_success:
        if is_lower:
            return round(current_kg + (10.0 if is_early_phase else 5.0), 1)
        return round(current_kg + (5.0 if is_early_phase else 2.5), 1)
    # 실패 시: 무게 절반(=원본의 50%) 으로 떨어뜨림 (룰 카드: 절반 또는 디로드)
    return round(current_kg * 0.5, 1)
