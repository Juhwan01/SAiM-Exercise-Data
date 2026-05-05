"""루틴 추천 — 지식·행동·측정 (5 룰): N02, N04, M03, R10, I01.

함수 형태로 호출하면 사용자에게 보여줄 교육 메시지/처방을 반환.
"""

from __future__ import annotations

from rule_engine.types import Citation


# ============================================================================
# N02 — 신경 적응 vs 근비대 적응
# ----------------------------------------------------------------------------
# rules/N02.yaml | csv 105행
# 출처: Sale 1988 / Counts 2017
# URL : https://pubmed.ncbi.nlm.nih.gov/3057313/  ★★★
# ============================================================================
N02 = Citation(
    rule_id="N02", name="신경 적응 vs 근비대",
    source="Sale 1988 / Counts 2017",
    url="https://pubmed.ncbi.nlm.nih.gov/3057313/",
    confidence="★★★",
)

def n02_expectation_message(training_months: int) -> str:
    """N02: 사용자 기대값 조정 메시지."""
    if training_months < 2:
        return "초기 4~8주는 주로 신경 적응 — 근력은 빠르게 늘지만 사이즈 변화는 작다"
    if training_months < 8:
        return "8주 부근부터 근비대가 본격적으로 시작된다"
    return "고급 단계 — 근비대 위주, 진보 속도는 느리지만 누적은 크다"


# ============================================================================
# N04 — 근섬유 타입 (Type I / II)
# ----------------------------------------------------------------------------
# rules/N04.yaml | csv 107행
# 출처: Schoenfeld 2021
# URL : https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/  ★★★
# ============================================================================
N04 = Citation(
    rule_id="N04", name="근섬유 타입",
    source="Schoenfeld 2021",
    url="https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/",
    confidence="★★★",
)

def n04_rep_range_education() -> str:
    return "근비대는 6~30렙 모두 효과적. '저렙=속근만 자극' 단순화 오류"


# ============================================================================
# M03 — 1RM 측정 방법
# ----------------------------------------------------------------------------
# rules/M03.yaml | csv 124행
# 출처: Reynolds 2006 / NSCA
# URL : https://pubmed.ncbi.nlm.nih.gov/16937972/  ★★★
# ============================================================================
M03 = Citation(
    rule_id="M03", name="1RM 측정 방법",
    source="Reynolds 2006 / NSCA",
    url="https://pubmed.ncbi.nlm.nih.gov/16937972/",
    confidence="★★★",
)

def m03_pick_method(level: str, age: int = 30, allow_max_lift: bool = True) -> str:
    """M03: 사용자 레벨/연령 → 측정 방식.

    초보·고령은 추정만, 중급+ 는 8주마다 AMRAP, 고급은 1RM 옵션.
    """
    if level == "초보" or age >= 60:
        return "AMRAP_추정만"   # C09/C10 사용
    if level == "중급":
        return "AMRAP_8주마다"
    if allow_max_lift:
        return "1RM_테스트_옵션"
    return "AMRAP_8주마다"


# ============================================================================
# R10 — 한국 직장인 시간 충돌·회식 대응
# ----------------------------------------------------------------------------
# rules/R10.yaml | csv 144행
# 출처: KOSIS + Parr 2014
# URL : https://kosis.kr/statHtml/statHtml.do?orgId=118&tblId=DT_118N_PAYM55  ★☆☆
# ============================================================================
R10 = Citation(
    rule_id="R10", name="한국 직장인 회식 대응",
    source="KOSIS + Parr 2014",
    url="https://kosis.kr/statHtml/statHtml.do?orgId=118&tblId=DT_118N_PAYM55",
    confidence="★☆☆",
)

def r10_korean_schedule_advice(
    has_dinner_today: bool, available_days: int,
) -> dict:
    """R10: 회식·근무 시간 변수 반영.

    회식 당일 = 휴식, 익일 = 20분 압축 루틴(메인 3종 5x5).
    """
    if has_dinner_today:
        return {
            "오늘": "휴식 권고 (회식·음주)",
            "내일": "20분 압축 루틴: 메인 3종 5x5",
            "주간_볼륨_조정": "-10~15% 자동 조정",
            "메모": "음주 후 24h는 근비대 신호 -37% — 폼 위주",
        }
    return {"오늘": "정상 진행", "주간_볼륨_조정": "유지"}


# ============================================================================
# I01 — 초보자 Linear Progression (추천 컨텍스트)
# ----------------------------------------------------------------------------
# rules/I01.yaml | csv 91행
# 출처: Mark Rippetoe (Starting Strength)
# URL : https://startingstrength.com/get-started/programs  ★★★
# ============================================================================
I01 = Citation(
    rule_id="I01", name="초보자 LP",
    source="Rippetoe",
    url="https://startingstrength.com/get-started/programs",
    confidence="★★★",
)

def i01_use_linear_progression(level: str, training_months: int) -> bool:
    """I01: 초보면 자율조절 끄고 LP 사용."""
    return level == "초보" or training_months < 6
