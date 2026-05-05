"""루틴 추천 — 주기화 모델 + 시작 무게 (15 룰): D01~D15.

D01-D04: 주기화 모델 (LP·DUP·블록·플렉시블)
D05    : 분할 루틴 비교
D06-D10: 프로그램 템플릿 (Starting Strength·5/3/1·GZCLP·nSuns·PHUL/PHAT)
D11-D15: 초보자 시작 무게 + 워크업 + 증량 폭
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# D01 — Linear Periodization
# ----------------------------------------------------------------------------
# rules/D01.yaml | csv 31행
# 출처: Bompa / NSCA
# URL : https://www.strongerbyscience.com/periodization-data/  ★★★
#
# 1~4주 비대(8~12렙) → 5~8주 근력(3~6렙) → 9~12주 파워. 초보~중급 적합.
# ============================================================================
D01 = Citation(
    rule_id="D01", name="Linear Periodization",
    source="Bompa / NSCA",
    url="https://www.strongerbyscience.com/periodization-data/",
    confidence="★★★",
)

def d01_phase_for_week(week: int) -> dict:
    """D01: 12주 LP 사이클 — 주차에 따른 변수 반환."""
    if week <= 4:
        return {"단계": "비대", "렙": (8, 12), "pct": (67.0, 75.0)}
    if week <= 8:
        return {"단계": "근력", "렙": (3, 6), "pct": (85.0, 92.0)}
    return {"단계": "파워", "렙": (1, 3), "pct": (90.0, 100.0)}


# ============================================================================
# D02 — Daily Undulating Periodization (DUP)
# ----------------------------------------------------------------------------
# rules/D02.yaml | csv 32행
# 출처: Painter 2012 / Colquhoun 2017
# URL : https://pubmed.ncbi.nlm.nih.gov/22173008/  ★★★
#
# 같은 주 내 일별 비대-근력-파워. 9~12주에 LP보다 약간 우월. 중급+ 권장.
# ============================================================================
D02 = Citation(
    rule_id="D02", name="DUP",
    source="Painter 2012 / Colquhoun 2017",
    url="https://pubmed.ncbi.nlm.nih.gov/22173008/",
    confidence="★★★",
)

def d02_weekly_dup() -> list[dict]:
    """D02: 주 3일 DUP 디폴트 — [월=비대, 수=근력, 금=파워]."""
    return [
        {"요일_idx": 0, "단계": "비대",  "렙": (8, 12), "pct": (67.0, 75.0)},
        {"요일_idx": 2, "단계": "근력",  "렙": (3, 6),  "pct": (85.0, 92.0)},
        {"요일_idx": 4, "단계": "파워",  "렙": (1, 3),  "pct": (90.0, 100.0)},
    ]


# ============================================================================
# D03 — Block Periodization
# ----------------------------------------------------------------------------
# rules/D03.yaml | csv 33행
# 출처: Issurin / Verkhoshansky
# URL : https://www.strongerbyscience.com/periodization-data/  ★★☆
#
# 3~4주 단위 블록(축적-변환-실현). 고급 선수용.
# ============================================================================
D03 = Citation(
    rule_id="D03", name="Block Periodization",
    source="Issurin / Verkhoshansky",
    url="https://www.strongerbyscience.com/periodization-data/",
    confidence="★★☆",
)

def d03_block_schedule() -> list[dict]:
    """D03: 3블록(각 3~4주). 고급 사용자용."""
    return [
        {"블록": "축적", "주차": (1, 4),  "초점": "볼륨↑·강도↓"},
        {"블록": "변환", "주차": (5, 7),  "초점": "강도↑·볼륨↓"},
        {"블록": "실현", "주차": (8, 10), "초점": "최대 강도·테이퍼"},
    ]


# ============================================================================
# D04 — Flexible DUP
# ----------------------------------------------------------------------------
# rules/D04.yaml | csv 34행
# 출처: McNamara & Stearne 2010
# URL : https://pubmed.ncbi.nlm.nih.gov/20042923/  ★★★
# ============================================================================
D04 = Citation(
    rule_id="D04", name="Flexible DUP",
    source="McNamara & Stearne 2010",
    url="https://pubmed.ncbi.nlm.nih.gov/20042923/",
    confidence="★★★",
)

def d04_session_by_condition(condition: str) -> str:
    """D04: 사용자 컨디션 입력 → 그날 세션 타입."""
    return {"좋음": "근력", "보통": "비대", "피곤": "회복"}.get(condition, "비대")


# ============================================================================
# D05 — 분할 루틴 비교
# ----------------------------------------------------------------------------
# rules/D05.yaml | csv 35행
# 출처: Schoenfeld 2016 / Israetel
# URL : https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter  ★★★
# ============================================================================
D05 = Citation(
    rule_id="D05", name="분할 루틴 비교",
    source="Schoenfeld 2016 / Israetel",
    url="https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter",
    confidence="★★★",
)

def d05_pick_split(available_days: int, level: str) -> str:
    """D05: 가용 일수 + 레벨 → 권장 분할."""
    if available_days <= 3 or level == "초보":
        return "풀바디_주" + str(available_days)
    if available_days == 4:
        return "상하분할_주4"
    if available_days >= 5:
        return "PPL_주" + str(available_days)
    return "풀바디_주3"


# ============================================================================
# D06 — Starting Strength (5x5/5x3)
# ----------------------------------------------------------------------------
# rules/D06.yaml | csv 36행
# 출처: Mark Rippetoe
# URL : https://startingstrength.com/get-started/programs  ★★★
# ============================================================================
D06 = Citation(
    rule_id="D06", name="Starting Strength",
    source="Rippetoe",
    url="https://startingstrength.com/get-started/programs",
    confidence="★★★",
)

def d06_starting_strength() -> dict:
    """D06: 초보용 LP 프로그램. 월수금 A/B 교대."""
    return {
        "이름": "Starting Strength",
        "분할": "FullBody_AB",
        "주_빈도": 3,
        "A루틴": ["스쿼트 5x3", "벤치프레스 5x3", "데드리프트 1x5"],
        "B루틴": ["스쿼트 5x3", "오버헤드프레스 5x3", "파워클린 5x3 또는 바벨로우 5x5"],
        "증량": "세션당 +2.5~5kg",
        "기간": "6~12개월",
        "대상_레벨": "초보",
    }


# ============================================================================
# D07 — 5/3/1 Wendler
# ----------------------------------------------------------------------------
# rules/D07.yaml | csv 37행
# 출처: Jim Wendler
# URL : https://thefitness.wiki/routines/5-3-1-for-beginners/  ★★★
# ============================================================================
D07 = Citation(
    rule_id="D07", name="5/3/1 Wendler",
    source="Wendler",
    url="https://thefitness.wiki/routines/5-3-1-for-beginners/",
    confidence="★★★",
)

def d07_531(one_rm_kg: dict[str, float]) -> dict:
    """D07: 4주 사이클. TM = 1RM × 0.9.

    1주차: 5렙×3 (65/75/85% TM)
    2주차: 3렙×3 (70/80/90% TM)
    3주차: 5/3/1+ (75/85/95% TM, 마지막 AMRAP)
    4주차: 디로드 (40/50/60% TM × 5렙)
    """
    tm = {k: round(v * 0.9, 1) for k, v in one_rm_kg.items()}
    return {
        "이름": "5/3/1 Wendler",
        "TM": tm,
        "주차_표": [
            {"주": 1, "렙_세트": "5x3", "pct": (65.0, 75.0, 85.0)},
            {"주": 2, "렙_세트": "3x3", "pct": (70.0, 80.0, 90.0)},
            {"주": 3, "렙_세트": "5/3/1+ AMRAP", "pct": (75.0, 85.0, 95.0)},
            {"주": 4, "렙_세트": "5x3 디로드", "pct": (40.0, 50.0, 60.0)},
        ],
        "사이클당_TM_증가": "+2.5~5kg",
        "대상_레벨": "중급",
    }


# ============================================================================
# D08 — GZCLP
# ----------------------------------------------------------------------------
# rules/D08.yaml | csv 38행
# 출처: Cody LeFever / r/Fitness wiki
# URL : https://thefitness.wiki/routines/gzclp/  ★★☆
# ============================================================================
D08 = Citation(
    rule_id="D08", name="GZCLP",
    source="LeFever / r/Fitness wiki",
    url="https://thefitness.wiki/routines/gzclp/",
    confidence="★★☆",
)

def d08_gzclp() -> dict:
    """D08: 3-tier 구조."""
    return {
        "이름": "GZCLP",
        "T1": "메인 컴파운드 5+렙 (탑셋 + 백오프 5x3)",
        "T2": "보조 컴파운드 10+렙 (3x10)",
        "T3": "아이솔레이션 15+렙 (3x15)",
        "주_빈도": 4,
        "대상_레벨": "초보~중급",
    }


# ============================================================================
# D09 — nSuns LP
# ----------------------------------------------------------------------------
# rules/D09.yaml | csv 39행
# 출처: nSuns / r/Fitness wiki
# URL : https://thefitness.wiki/routines/nsuns-lp/  ★★☆
# ============================================================================
D09 = Citation(
    rule_id="D09", name="nSuns LP",
    source="nSuns",
    url="https://thefitness.wiki/routines/nsuns-lp/",
    confidence="★★☆",
)

def d09_nsuns() -> dict:
    return {
        "이름": "nSuns LP",
        "주_빈도": 6,
        "패턴": "메인+보조 모두 5/3/1",
        "용도": "5/3/1 정체기 돌파 / 중급+",
        "대상_레벨": "중급",
    }


# ============================================================================
# D10 — PHUL/PHAT (하이브리드)
# ----------------------------------------------------------------------------
# rules/D10.yaml | csv 40행
# 출처: Layne Norton / Brandon Campbell
# URL : https://www.muscleandstrength.com/workouts/phat-power-hypertrophy-adaptive-training  ★★☆
# ============================================================================
D10 = Citation(
    rule_id="D10", name="PHUL/PHAT",
    source="Norton / Campbell",
    url="https://www.muscleandstrength.com/workouts/phat-power-hypertrophy-adaptive-training",
    confidence="★★☆",
)

def d10_phul_phat(days: int) -> dict:
    """D10: 가용 일수에 따른 선택."""
    return {
        "이름": "PHUL" if days <= 4 else "PHAT",
        "주_빈도": days,
        "패턴": "근력일+근비대일 결합",
        "대상_레벨": "중급+",
    }


# ============================================================================
# D11 — 초보자 빅3+OHP 디폴트 시작 무게 (남성)
# ----------------------------------------------------------------------------
# rules/D11.yaml | csv 41행
# 출처: StrongLifts 5x5 (Mehdi Hadim)
# URL : https://stronglifts.com/stronglifts-5x5/workout-program/  ★★☆
# ============================================================================
D11 = Citation(
    rule_id="D11", name="초보자 시작 무게 (남)",
    source="StrongLifts 5x5",
    url="https://stronglifts.com/stronglifts-5x5/workout-program/",
    confidence="★★☆",
)

def d11_male_start_weights() -> dict[str, float]:
    """D11: 남성 초보 디폴트 시작 무게 — 룰 카드 한줄설명 그대로."""
    return {
        "스쿼트":         20.0,   # 빈 바벨
        "벤치프레스":     20.0,
        "오버헤드프레스": 20.0,
        "데드리프트":     40.0,   # 바 + 양쪽 10kg
    }


# ============================================================================
# D12 — 초보자 빅3+OHP 디폴트 시작 무게 (여성)
# ----------------------------------------------------------------------------
# rules/D12.yaml | csv 42행
# 출처: IPF Technical Rules Book 2024
# URL : https://www.powerlifting.sport/rules/codes/info/technical-rules  ★★★
# ============================================================================
D12 = Citation(
    rule_id="D12", name="초보자 시작 무게 (여)",
    source="IPF Technical Rules 2024",
    url="https://www.powerlifting.sport/rules/codes/info/technical-rules",
    confidence="★★★",
)

def d12_female_start_weights(has_15kg_bar: bool = False) -> dict[str, float]:
    """D12: 여성 초보 디폴트.

    헬스장에 15kg 여성용 바 있으면 우선, 없으면 20kg.
    """
    bar = 15.0 if has_15kg_bar else 20.0
    return {
        "스쿼트":         bar,
        "벤치프레스":     bar,
        "오버헤드프레스": bar,
        "데드리프트":     35.0,   # 30~40 중간
    }


# ============================================================================
# D13 — 빈 바벨로 시작하는 원칙
# ----------------------------------------------------------------------------
# rules/D13.yaml | csv 43행
# 출처: Rippetoe "Incremental Increases"
# URL : https://startingstrength.com/article/incremental_increases  ★★☆
# ============================================================================
D13 = Citation(
    rule_id="D13", name="빈 바벨 워크업",
    source="Rippetoe",
    url="https://startingstrength.com/article/incremental_increases",
    confidence="★★☆",
)

def d13_warmup_progression(workset_kg: float, bar_kg: float = 20.0) -> list[float]:
    """D13: 빈 바 → 50% → 70% → 90% → 100% 워크업 무게 시퀀스."""
    if workset_kg <= bar_kg:
        return [bar_kg]
    return [
        bar_kg,
        round(workset_kg * 0.5, 1),
        round(workset_kg * 0.7, 1),
        round(workset_kg * 0.9, 1),
        workset_kg,
    ]


# ============================================================================
# D14 — 초보자 첫 세션 워크셋 상한 가이드
# ----------------------------------------------------------------------------
# rules/D14.yaml | csv 44행
# 출처: Rippetoe (Starting Strength)
# URL : https://startingstrength.com/article/incremental_increases  ★★☆
# ============================================================================
D14 = Citation(
    rule_id="D14", name="초보자 첫 세션 워크셋 상한",
    source="Rippetoe",
    url="https://startingstrength.com/article/incremental_increases",
    confidence="★★☆",
)

def d14_clamp_first_workset(requested_kg: float, movement: str, sex: str, body_weight_kg: float) -> tuple[float, str | None]:
    """D14: 첫 세션 무게가 상한 초과면 65kg(스쿼트, 평균 체중 남) 기준으로 클램프."""
    base_caps = {  # (남, 여)
        "스쿼트":         (65.0, 35.0),
        "데드리프트":     (70.0, 40.0),
        "벤치프레스":     (40.0, 25.0),
        "오버헤드프레스": (30.0, 18.0),
    }
    cap_m, cap_f = base_caps.get(movement, (60.0, 30.0))
    cap = cap_m if sex == "남" else cap_f
    ref = 70.0 if sex == "남" else 55.0
    cap = cap * (body_weight_kg / ref)
    if requested_kg > cap:
        return round(cap, 1), f"첫 세션 상한 — {movement} {round(cap,1)}kg 권장"
    return requested_kg, None


# ============================================================================
# D15 — 초보자 증량 폭(점프) 디폴트
# ----------------------------------------------------------------------------
# rules/D15.yaml | csv 45행
# 출처: Rippetoe "Incremental Increases"
# URL : https://startingstrength.com/article/incremental_increases  ★★☆
# ============================================================================
D15 = Citation(
    rule_id="D15", name="초보자 증량 폭",
    source="Rippetoe",
    url="https://startingstrength.com/article/incremental_increases",
    confidence="★★☆",
)

def d15_increment_by_movement(movement: str, is_early_phase: bool = False) -> float:
    """D15: 운동별 디폴트 증량 폭 (kg/세션).

    하체(스쿼트·데드): +5 (초기 +10)
    상체(벤치·OHP·로우): +2.5 (초기 +5)
    """
    is_lower = movement in ("스쿼트", "데드리프트")
    if is_lower:
        return 10.0 if is_early_phase else 5.0
    return 5.0 if is_early_phase else 2.5
