"""공통 타입.

이 파일에는 두 서비스(실시간 코칭 · 루틴 추천)가 같이 쓰는 데이터 형태만 둔다.
룰 자체의 로직은 들어 있지 않다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# --------------------------------------------------------------------------
# 출처(근거) 표기
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class Citation:
    """룰 1개의 출처 정보. rules/{ID}.yaml 의 `근거` 블록과 1:1 대응."""

    rule_id: str          # 예: "A11"
    name: str             # 예: "세트 간 무게 보정 (Helms 룰)"
    source: str           # 출처 문자열 (저자/매체)
    url: str              # 1차 출처 링크
    confidence: str       # "★★★" / "★★☆" / "★☆☆"

    def short(self) -> str:
        """사람이 읽는 한 줄: 'A11 ★★★ Helms — rippedbody.com/rpe'"""
        return f"{self.rule_id} {self.confidence} {self.source} — {self.url}"


@dataclass
class RuleHit:
    """룰 1개가 발동했을 때 남기는 흔적. 결과를 사용자에게 설명할 때 쓴다."""

    citation: Citation
    summary: str          # 사람이 읽는 한 문장 (예: "RPE 9 입력 → 다음 세트 -4%")
    output: Any = None    # 룰의 실제 계산 결과 (룰마다 타입 다름)


# --------------------------------------------------------------------------
# 실시간 코칭 입출력
# --------------------------------------------------------------------------
@dataclass
class CoachingState:
    """실시간 코칭에 필요한 모든 정보를 담는 입력 객체.

    필드는 룰 카드 `필요한_정보`의 합집합이다. 누락된 필드는 None 으로 두면
    해당 룰이 자동으로 비활성화된다 (스킵).
    """

    # ── 운동 정보 ────────────────────────────────────────────────
    운동명: str                     # "스쿼트" / "벤치프레스" / "데드리프트" 등
    운동종류: str = "compound"       # "compound" or "isolation" — A12, A14, C07 가 사용
    근육군: str = "lower_compound"   # "lower_compound"/"upper_compound"/"single_joint"

    # ── 현재 세트 상황 ──────────────────────────────────────────
    세트번호: int = 1               # 1-indexed
    총_세트: int = 5
    현재무게_kg: float = 0.0
    최대무게_추정_kg: float = 0.0   # 1RM 추정치 (C09/C10/M03 결과)
    목표RPE: float = 8.0
    목표렙: int = 5

    # ── 직전 세트 사용자 입력 (있으면) ─────────────────────────
    입력RPE: float | None = None    # 0~10 (Zourdos)
    실제렙: int | None = None       # 실패한 경우 < 목표렙
    톱셋_무게_kg: float | None = None  # A03 fatigue percent용
    톱셋_RPE: float | None = None

    # ── 사용자 프로필 (안전 게이트용) ──────────────────────────
    사용자레벨: str = "초보"        # "초보"/"중급"/"고급" — L04
    경험_월: int = 0                # 훈련 개월 — L04, I01
    성별: str = "남"                # "남"/"여"
    체중_kg: float = 70.0
    질환: list[str] = field(default_factory=list)
        # 가능 값: "당뇨"(L05), "고혈압"(L06), "이상지질혈증"(L07), "골관절염_무릎"(L08),
        #         "골관절염_고관절"(L08), "혈압_미조절", "공복혈당_고", "망막증" 등

    # ── 부상/통증 입력 (있으면) ───────────────────────────────
    통증부위: str | None = None     # "허리"/"무릎"/"어깨" 등 — Q01, E15
    통증강도_0_10: int | None = None
    통증_시작_h: float | None = None   # 몇 시간 전 발생 (Q01 단계 분기)
    통증패턴: str | None = None        # "예리한"/"둔한"/"국소"/"양측대칭" — E15
    관절통_NPRS: int | None = None     # 0~10 — G07

    # ── 컨디션·회복 ────────────────────────────────────────────
    수면_h: float | None = None      # 어젯밤 수면 — K06
    최근_3일_수면_h: list[float] = field(default_factory=list)  # K06 누적 판정
    동기_1_5: int | None = None       # G07 다지표 디로드
    근육통_시작_h: float | None = None  # K08

    # ── 추적/메모리 (앱 DB에서 불러옴) ──────────────────────────
    최근_RPE_drift: float = 0.0     # 같은 무게×렙에서 RPE 변화 평균 — A13, G02, G07
    이번주_볼륨_세트: dict[str, int] = field(default_factory=dict)  # 근육군별 누적 — B04, G04
    지난주_볼륨_세트: dict[str, int] = field(default_factory=dict)  # G04 비교용
    최근_PR_경과일: int | None = None  # G07
    렙별_바벨속도_ms: list[float] = field(default_factory=list)   # E01-E04 VBT 옵션


@dataclass
class CoachingResult:
    """실시간 코칭이 한 번 호출되었을 때의 결과 묶음."""

    # ── 안전 게이트 ────────────────────────────────────────────
    차단됨: bool = False           # 운동 즉시 중단해야 하는가
    차단_이유: str | None = None    # 사용자에게 보여줄 한 줄
    의뢰_권고: str | None = None    # "심장내과 상담" 같은 적색기 안내

    # ── 다음 한 행동 ───────────────────────────────────────────
    다음_무게_kg: float | None = None
    휴식_초: int | None = None
    세트_종료_권고: bool = False    # A03 fatigue percent / E03 velocity loss

    # ── 폼/호흡/체크리스트 ────────────────────────────────────
    셋업_체크리스트: list[str] = field(default_factory=list)  # E16
    폼_큐: list[str] = field(default_factory=list)             # E05~E12, E14
    호흡_가이드: str | None = None                              # E13
    그립_가이드: str | None = None                              # E17

    # ── 가벼운 안내/경고 ──────────────────────────────────────
    경고: list[str] = field(default_factory=list)
    제안: list[str] = field(default_factory=list)
        # 예: "다음 주 디로드 권장" (G02/G07), "수면 보충 후 재진입" (K06)

    # ── 발동된 룰 추적 (감사 로그) ─────────────────────────────
    발동_룰: list[RuleHit] = field(default_factory=list)

    def add(self, hit: RuleHit) -> None:
        """룰 1개의 결과를 결과 묶음에 누적."""
        self.발동_룰.append(hit)

    def 근거_요약(self) -> list[str]:
        """결과를 만들 때 쓴 룰의 한 줄 요약 모음."""
        return [h.citation.short() for h in self.발동_룰]


# --------------------------------------------------------------------------
# 운동 루틴 추천 입출력
# --------------------------------------------------------------------------
@dataclass
class UserProfile:
    """루틴 추천 진입 시 받는 프로필 (온보딩 결과 그대로).

    필드는 룰 카드들의 `필요한_정보` 합집합. 모르는 값은 None 으로 두면
    해당 룰이 자동 스킵된다.
    """

    # ── 신체 ────────────────────────────────────────────────
    성별: str = "남"                  # "남" / "여"
    체중_kg: float = 70.0
    키_cm: float = 175.0
    나이: int = 30
    체지방률_pct: float | None = None  # 인바디로 알면 K20, 아니면 K19

    # ── 훈련 이력 ──────────────────────────────────────────
    훈련_월: int = 0                   # 운동 경력 (개월) — L04
    사용자레벨: str = "초보"           # "초보"/"중급"/"고급" — L04 결과
    목표: str = "건강증진"             # "다이어트"/"벌크업"/"스트렝스"/"근육량 증가"/"건강증진"

    # ── 가용성/환경 ──────────────────────────────────────
    주가용일: int = 3                  # 주당 운동 가능 일수 — D05
    세션가용분: int = 60               # 세션 가용 시간 (분) — C11, I08
    장비: list[str] = field(default_factory=lambda: ["바벨", "덤벨", "머신"])  # J02
    헬스장_여성바_15kg: bool = False    # D12 분기

    # ── 활동량 ──────────────────────────────────────────
    직업유형: str = "사무직"           # "사무직"/"서비스"/"육체노동" — K22
    추가_운동빈도: str = "주1~3회"      # K22 5단계 매핑 입력

    # ── 안전/질환 ──────────────────────────────────────
    질환: list[str] = field(default_factory=list)
        # 가능 값(L02~L08): "고령(50+)", "청소년(<18)", "당뇨", "고혈압",
        #                  "이상지질혈증", "골관절염_무릎", "골관절염_고관절"
    복용약물: list[str] = field(default_factory=list)
    bp_sbp: float | None = None
    bp_dbp: float | None = None
    ldl: float | None = None
    안정시통증_NRS: int | None = None

    # ── 부상 이력 ──────────────────────────────────────
    부상이력: list[str] = field(default_factory=list)
        # 예: "허리_요추", "어깨_RCRSP", "무릎_PFPS"

    # ── 컨디션 ────────────────────────────────────────
    좌우_불균형_pct: float | None = None  # J04
    약점부위: list[str] = field(default_factory=list)  # J05

    # ── 1RM 추정 (있으면) ─────────────────────────────
    one_rm_kg: dict[str, float] = field(default_factory=dict)
        # {"스쿼트": 80, "벤치프레스": 50, ...}


@dataclass
class RoutineRecommendation:
    """루틴 추천 결과 묶음."""

    # ── 게이트 결과 ───────────────────────────────
    안전_차단: bool = False
    차단_이유: str | None = None
    의료_의뢰: list[str] = field(default_factory=list)

    # ── 영양 ─────────────────────────────────────
    BMR_kcal: int | None = None
    TDEE_kcal: int | None = None
    목표_칼로리: int | None = None      # 다이어트=-500, 벌크=+200~400 식 적용

    # ── 프로그램 ─────────────────────────────────
    추천_프로그램: str | None = None    # "Starting Strength" 등
    분할_형태: str | None = None        # "풀바디 주3"/"상하분할 주4"/"PPL 주5"
    주간_스케줄: list[str] = field(default_factory=list)   # ["월: A루틴", ...]

    # ── 시작 무게 ────────────────────────────────
    시작_무게_kg: dict[str, float] = field(default_factory=dict)
    증량_폭_kg: dict[str, float] = field(default_factory=dict)

    # ── 강도/볼륨 처방 ─────────────────────────
    렙범위: tuple[int, int] | None = None
    pct_1rm범위: tuple[float, float] | None = None
    세트당_RIR: int | None = None
    근육군별_주간세트: dict[str, int] = field(default_factory=dict)
    근육군당_주빈도: int | None = None
    휴식_초: dict[str, int] = field(default_factory=dict)  # "compound": 240 식

    # ── 디로드/메조사이클 ────────────────────────
    메조_주차수: int | None = None
    디로드_주기_주: int | None = None   # G01·G10
    디로드_처방: dict | None = None      # G05/G06 결과

    # ── 운동 선택 ────────────────────────────────
    운동_풀: dict[str, list[str]] = field(default_factory=dict)  # 근육군→운동들
    대체_운동: dict[str, list[str]] = field(default_factory=dict)  # 부상→대체
    컴파운드_아이솔_비율: tuple[int, int] | None = None
    운동_순서: list[str] = field(default_factory=list)

    # ── 워밍업/스트레칭 ─────────────────────────
    일반_워밍업: str | None = None       # I05
    특이적_워밍업: list[str] = field(default_factory=list)  # I06/I07
    스트레칭_가이드: list[str] = field(default_factory=list)

    # ── 회복/수면/카디오 ────────────────────────
    수면_권장_h: tuple[float, float] | None = None
    카디오_권고: str | None = None
    능동_회복: str | None = None

    # ── 제약/주의사항 ──────────────────────────
    경고: list[str] = field(default_factory=list)
    한국_사용자_조정: list[str] = field(default_factory=list)  # R10
    교육_메시지: list[str] = field(default_factory=list)        # N02·N04 등 KB

    # ── 발동 룰 추적 ───────────────────────────
    발동_룰: list[RuleHit] = field(default_factory=list)

    def add(self, hit: RuleHit) -> None:
        self.발동_룰.append(hit)

    def 근거_요약(self) -> list[str]:
        return [h.citation.short() for h in self.발동_룰]


# --------------------------------------------------------------------------
# 헬퍼
# --------------------------------------------------------------------------
def round_to_plate(weight_kg: float, increment_kg: float = 1.25) -> float:
    """헬스장 가용 단위(보통 1.25kg/2.5kg)로 라운딩.

    라운딩이 룰 자체에 명시된 건 아니지만(YAML에는 식만), 실제 사용자에게
    숫자를 보여줄 때 0.1kg 단위는 의미가 없으므로 마지막 표시 단계에서 적용.
    """
    if weight_kg <= 0 or increment_kg <= 0:
        return 0.0
    return round(round(weight_kg / increment_kg) * increment_kg, 2)
