# rule_engine — SAiM 운동 코칭 룰 엔진

`workout_knowledge_base.csv`(153행) → `rules/{ID}.yaml`(153장) 에서 1:1 로 파생된
**근거 기반** 룰을 함수로 옮긴 엔진. 외부에서는 서비스 진입 함수 2 개만 보이고,
안에서 분류별 모듈이 룰 단위로 동작한다.

## 두 서비스, 두 진입점

```python
from rule_engine import realtime_coaching, recommend_routine
```

| 서비스 | 함수 | 입력 | 출력 | 룰 수 |
|---|---|---|---|---|
| 실시간 코칭 | `realtime_coaching(state)` | `CoachingState` (현재 세트 상황) | `CoachingResult` (다음 무게·휴식·큐·호흡) | 50 |
| 운동 루틴 추천 | `recommend_routine(profile)` | `UserProfile` (사용자 프로필) | `RoutineRecommendation` (주간 프로그램) | 97 |

두 서비스는 서로 호출하지 않는다. 같은 룰이 양쪽에 등장(21개)할 때는 **각 폴더에 따로 구현**해서, 한쪽 변경이 다른 쪽을 깨지 않게 한다.

## 폴더 구조

```
rule_engine/
├── README.md                     이 파일
├── __init__.py                   외부 노출 (lazy-import 진입 함수 2개)
├── types.py                      공통 타입
│
├── realtime_coaching.py          서비스 1 진입 함수
└── coaching_rules/               서비스 1의 50 룰
    ├── rpe.py                    A01·A02·A03·A04·A06·A07·A08·A09·A11·A12·A13·A14
    ├── form_cues.py              E01~E08·E10~E17 (16개)
    ├── safety.py                 Q01·L05·L06·L07·L08·K06·K08
    ├── deload.py                 G02·G04·G07
    ├── progression.py            I01·I04·C08·D14·D15
    └── misc.py                   C07·P04·P05·K04·B04·I02·D04
│
├── recommend_routine.py          서비스 2 진입 함수
└── routine_rules/                서비스 2의 97 룰
    ├── nutrition.py              K19·K20·K21·K22
    ├── volume.py                 B01·B02·B03·B04·B05
    ├── intensity.py              C01~C15
    ├── periodization.py          D01~D15
    ├── populations.py            L02·L03·L04·L05·L06·L07·L08
    ├── exercise_select.py        F05·J01·J02·J03·J04·J05·J07·E14·E17·I03
    ├── recovery.py               K05·K06·K07·G01·G03·G04·G05·G06·G08·G09·G10·G11
    ├── injury_recovery.py        Q02·Q03·Q04·Q05·Q06
    ├── warmup_stretch.py         I05·I06·I07·I08·P01·P02·P03·P04·P05·E02·E09
    ├── cardio.py                 O01·O02·O03
    ├── rpe_meta.py               A02·A05·A07·A10·A13
    └── knowledge.py              N02·N04·M03·R10·I01
│
└── tests/
    ├── test_realtime_coaching.py
    └── test_recommend_routine.py
```

## 사용 예 1 — 실시간 코칭

```python
from rule_engine import realtime_coaching
from rule_engine.types import CoachingState

state = CoachingState(
    운동명="스쿼트", 운동종류="compound", 근육군="lower_compound",
    세트번호=2, 현재무게_kg=100, 최대무게_추정_kg=130,
    목표RPE=8.0, 목표렙=5, 입력RPE=9.0,
    사용자레벨="중급", 체중_kg=70,
)
r = realtime_coaching(state)

print(r.다음_무게_kg)      # 보정된 다음 세트 무게
print(r.휴식_초)            # 휴식 타이머
print(r.폼_큐)              # 외적 큐 리스트
print(r.호흡_가이드)        # Valsalva or 일반
print(r.근거_요약())        # 발동 룰 출처
```

## 사용 예 2 — 루틴 추천

```python
from rule_engine import recommend_routine
from rule_engine.types import UserProfile

profile = UserProfile(
    성별="남", 체중_kg=70, 키_cm=175, 나이=30,
    훈련_월=2, 목표="벌크업", 주가용일=3, 세션가용분=60,
)
r = recommend_routine(profile)

print(r.BMR_kcal, r.TDEE_kcal, r.목표_칼로리)   # 1649 / 2267 / 2567
print(r.추천_프로그램)                            # 'Starting Strength'
print(r.분할_형태)                                # '풀바디_주3'
print(r.주간_스케줄)                              # ['월: A루틴', ...]
print(r.시작_무게_kg)                             # {스쿼트:20, 벤치:20, 데드:40, OHP:20}
print(r.근육군별_주간세트)                        # {가슴:8, 등:10, 어깨:8, ...}
print(r.디로드_주기_주, r.메조_주차수)            # 5, 6
print(r.근거_요약())                              # 발동 룰 30+개의 출처
```

## 룰 발동 순서

### 실시간 코칭
```
[1] 안전 게이트
   Q01 → E15 → L05 → L06 → L07 → L08 → K06 → K08
   ↓ 차단 신호 1개라도 나오면 즉시 종료

[2] 다음 세트 무게
   A04 (RIR 보정) → A11 (Helms) ⊕ A12 (RTS, 컴파운드) → A14 (고강도) → A03 (누적 피로)

[3] 휴식  C07
[4] 폼·호흡  E16 → E06~E12 → E05 → E13 → E17 → E03(VBT)
[5] 디로드 권고  G02 → G04 → G07 → B04
[6] 보조  K04(수분)
```

### 루틴 추천
```
[1] 모집단 안전 게이트  L02 → L03 → L05 → L06 → L07 → L08
[2] 레벨 분류  L04
[3] 영양  K19 또는 K20 → K22 → K21
[4] 분할/프로그램  D05 → D06/D07/D08/D09/D10
[5] 시작 무게  D11/D12 + D14 클램프 + D15 증량
[6] 강도/볼륨  C02 → C05 → C06 → C07 → B02 → B05
[7] 주기화/디로드  D01/D02/D03 + G01/G10/G05
[8] 운동 선택  J05 → J03 → J02 → I03 + (J01 부상 매핑)
[9] 워밍업/스트레칭  I05 → I06 → P01/P05 → P03/P04
[10] 카디오  O01 → O02 → O03
[11] 회복  K05 → K06 → K07
[12] 부상 이력  Q04/Q05/Q06
[13] 행동·교육  R10 → N02 → N04 → M03
```

## 근거 추적

각 룰은 모듈 상단에 `Citation` 으로 출처/URL/신뢰도가 박혀있다:

```python
A11 = Citation(
    rule_id="A11", name="세트 간 무게 보정 (Helms 룰)",
    source="Helms (M&S Pyramid) / Ripped Body",
    url="https://rippedbody.com/rpe/",
    confidence="★★★",
)
```

진입 함수는 발동된 룰을 `RuleHit` 리스트에 누적하고, 결과 객체의
`근거_요약()` 으로 한 줄씩 노출한다 — 사용자가 "왜?" 누르면 그 자리에서 보여줄 데이터.

## 테스트

```bash
PYTHONPATH=/path/to/SAiM-Exercise-Data python3 rule_engine/tests/test_realtime_coaching.py
PYTHONPATH=/path/to/SAiM-Exercise-Data python3 rule_engine/tests/test_recommend_routine.py
```

각 룰 카드의 활용예시·한줄설명 숫자를 그대로 검증한다.
마스터 CSV 또는 룰 카드가 변경되면 테스트가 먼저 깨진다.

현재 통과: **35/35** (15 + 20)

## 룰 추가/수정 흐름

1. `rules/{ID}.yaml` 또는 마스터 CSV 수정
2. 해당 분류의 모듈에 함수 추가 (실시간 코칭이면 `coaching_rules/`, 추천이면 `routine_rules/`, 양쪽이면 둘 다)
3. 함수 위에 `# rules/{ID}.yaml | csv N행` + 출처/URL/신뢰도 주석
4. `Citation` 객체 추가
5. 진입 함수의 단계 함수에 호출 추가
6. `tests/` 에 룰 카드 활용예시 직접 검증 케이스 추가

## 출처 신뢰도 분포

★★★ (메타분석/포지션 스테이트먼트): 다수
★★☆ (좋은 1차 연구·교과서·평판 매뉴얼): 일부
★☆☆ (블로그·수정의견·업계 통계): I02 (템포 표기), R10 (한국 통계) — 소수만 사용
