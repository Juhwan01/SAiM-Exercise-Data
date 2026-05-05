# 룰베이스 구현 명세 (IMPLEMENTATION.md)

근거 기반 운동 코칭 앱의 153개 룰을 **코드로 바로 옮길 수 있는** 형태로 정리한 문서. PM·개발자·디자이너·도메인 전문가가 같이 읽는다.

## 이 문서가 뭐냐
- 룰 카드 153장(`rules/{ID}.yaml`)을 사람이 읽기 쉬운 형태로 다시 펼친 것
- 룰 한 개 = 함수 한 개. 입력·계산·출력·근거를 명시
- **추측은 들어가지 않는다**. 모든 줄은 마스터 CSV 행 또는 룰 카드 필드에서 왔고, 출처는 매 항목 옆에 붙어 있다

## 데이터가 어디서 왔는지 (중요)
```
workout_knowledge_base.csv (153행, 14컬럼)   ← 진실의 원천
        ↓ 1:1 변환
rules/{ID}.yaml (153장)                     ← 정형 룰 카드
        ↓ 모듈/목표/근거로 그룹핑
IMPLEMENTATION.md (이 문서)                  ← 사람이 읽고 코드로 옮기는 명세
        ↓ 함수 1개씩 구현
실제 코드 (다음 단계)
```
- 마스터 CSV 컬럼: `ID, 분류, 항목, 적용 시점, 운동 추천, 실시간 코칭, 지식베이스, 핵심 룰 (한 줄), 입력값, 출력값/동작, 활용 예시, 출처, URL, 신뢰도`
- 매 룰 블록 상단 `데이터` 줄에서 **CSV 몇 행에서 왔는지**를 명시한다 (예: `workout_knowledge_base.csv 11행 (ID A11)`)

## 룰 1장 명세 양식
```
### {ID} — {이름}
- 데이터: CSV 몇 행 → rules/{ID}.yaml
- 근거: 출처 — URL — 별 1~3개
- 분류 / 시점 / 쓰임새

무슨 룰: 한 문장 요약
받는 정보: 입력 변수 목록
내놓는 것: 출력 1줄
예시: 활용 사례 1개

[모듈 내 어느 목표에 들어가는지] / [별도 레이어 소속]

함수 시그니처(제안):
def {rid}_{name}(...): ...
```

## 모듈 7개 + 별도 레이어 3개

| # | 이름 | 언제 작동 | 룰 수(고유) |
|---|---|---|---|
| 1 | 온보딩 | 최초 1회 | 25 |
| 2 | 세션 시작 | 매 세션 시작 | 11 |
| 3 | 세트별 처방 | 매 세트 직전 | 39 |
| 4 | 세트 후 학습 | 매 세트 직후 | 13 |
| 5 | 메조사이클 관리 | 주 단위 | 28 |
| 6 | 영양·회복 | 일 단위 | 26 |
| 7 | 행동·안전 | 백그라운드 | 14 |
| L | 모집단 분기 | 매 룰 호출 직전 (가드) | 7 |
| Q | 부상 이벤트 트리거 | 사용자 통증 입력 시 | 6 |
| F | 메타 룰 | 운동 선택 가중치 | 1 |

총 룰 카드: **153장** (마스터 CSV 153행과 1:1)

## 신뢰도 표기
- ★★★ — 메타분석·포지션 스테이트먼트·합의 가이드라인
- ★★☆ — 좋은 1차 연구·표준 교과서·평판 있는 코칭 매뉴얼
- ★☆☆ — 블로그·수정 의견·업계 통계 (소수만 사용)

분포(GAPS.md 기준): ★★★ 95개(62%) · ★★☆ 52개(34%) · ★☆☆ 6개(4%)

---


## 모듈 1 — 온보딩

최초 1회. 사용자 분류·안전 게이트·1RM 추정·영양 모드·시작 무게를 잡는다. 이 모듈이 끝나면 그 사람만의 시작점이 생긴다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | C09, C10, D05, K19, K20, K21, K22, K23, L04, M01, M03, M04 |
| 벌크업 | C09, C10, D02, D05, D06, D10, D11, D12, D13, D14, D15, K19, K20, K21, K22, L04, M01, M03, M04 |
| 스트렝스 | C09, C10, D06, D07, D08, D09, D11, D12, D13, D14, D15, L04, M01, M03, M04 |
| 근육량 증가 | C09, C10, D02, D03, D05, D10, D11, D12, D13, D14, D15, K19, K20, K21, K22, L04, M01, M03, M04 |
| 건강증진 | C04, K19, K20, K21, K22, L04, M01 |

**고유 룰 수: 25**

### 분류: 세트/렙/강도 처방

### C09 — Epley 1RM 공식

- **데이터**: `workout_knowledge_base.csv` 28행 (ID `C09`) → [`rules/C09.yaml`](./rules/C09.yaml)
- **근거**: Epley 1985 — [https://en.wikipedia.org/wiki/One-repetition_maximum](https://en.wikipedia.org/wiki/One-repetition_maximum) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 초기 셋업 / 세트 직후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 1RM = 무게 × (1 + 렙수/30). 6~10렙에서 정확

**받는 정보**
- 무게
- 렙수

**내놓는 것**: 추정 1RM

**예시**: 신규 사용자 첫 세션 시 '6~10렙 가능한 무게'로 1RM 자동 추정

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c09_epley_1rm_공식(
    무게,
    렙수,
):
    """C09: Epley 1RM 공식. 추정 1RM"""
    ...  # 근거: https://en.wikipedia.org/wiki/One-repetition_maximum
```

---

### C10 — Brzycki 1RM 공식

- **데이터**: `workout_knowledge_base.csv` 29행 (ID `C10`) → [`rules/C10.yaml`](./rules/C10.yaml)
- **근거**: Brzycki 1993 — [https://en.wikipedia.org/wiki/One-repetition_maximum](https://en.wikipedia.org/wiki/One-repetition_maximum) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 초기 셋업 / 세트 직후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 1RM = 무게 × 36 / (37 - 렙수). 1~6렙에서 더 정확

**받는 정보**
- 무게
- 렙수(저렙)

**내놓는 것**: 추정 1RM

**예시**: 저렙 테스트 시 Brzycki, 중렙 시 Epley로 자동 분기

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c10_brzycki_1rm_공식(
    무게,
    렙수,  # 렙수(저렙)
):
    """C10: Brzycki 1RM 공식. 추정 1RM"""
    ...  # 근거: https://en.wikipedia.org/wiki/One-repetition_maximum
```

---

### C04 — ACSM 일반인 가이드라인

- **데이터**: `workout_knowledge_base.csv` 23행 (ID `C04`) → [`rules/C04.yaml`](./rules/C04.yaml)
- **근거**: ACSM 2026 Position Stand — [https://acsm.org/resistance-training-guidelines-update-2026/](https://acsm.org/resistance-training-guidelines-update-2026/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 건강 성인: 주 2~3회, 근육군당 1~4세트, 8~20렙, 40~70% 1RM (강화 시 60~80%, 8~12렙, 2~3분 휴식)

**받는 정보**
- 사용자 프로필(건강 목적)

**내놓는 것**: 초보·일반인 디폴트 처방

**예시**: 운동 목적이 '건강'인 사용자의 시작 디폴트값

**[온보딩]에서 적용 목표**: 건강증진
**다른 모듈에도 등장**: 세트별 처방

**함수 시그니처(제안)**
```python
def c04_acsm_일반인_가이드라인(
    사용자_프로필,  # 사용자 프로필(건강 목적)
):
    """C04: ACSM 일반인 가이드라인. 초보·일반인 디폴트 처방"""
    ...  # 근거: https://acsm.org/resistance-training-guidelines-update-2026/
```

---

### 분류: 주기화 모델

### D05 — 분할 루틴 비교

- **데이터**: `workout_knowledge_base.csv` 39행 (ID `D05`) → [`rules/D05.yaml`](./rules/D05.yaml)
- **근거**: Schoenfeld 2016 / Israetel — [https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter](https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter) — ★★★
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 풀바디(주2~3) = 초보, 상하분할(주4) = 중급, PPL(주5~6) = 고급. 빈도×볼륨 동일하면 효과 동등

**받는 정보**
- 가용 일수
- 사용자 레벨

**내놓는 것**: 권장 분할 형태 자동 매핑

**예시**: 주 3회 가용 → 풀바디, 주 5회 → PPL 추천

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d05_분할_루틴_비교(
    가용_일수,  # 가용 일수
    사용자_레벨,  # 사용자 레벨
):
    """D05: 분할 루틴 비교. 권장 분할 형태 자동 매핑"""
    ...  # 근거: https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter
```

---

### D02 — Daily Undulating (DUP)

- **데이터**: `workout_knowledge_base.csv` 36행 (ID `D02`) → [`rules/D02.yaml`](./rules/D02.yaml)
- **근거**: Painter 2012 / Colquhoun 2017 — [https://pubmed.ncbi.nlm.nih.gov/22173008/](https://pubmed.ncbi.nlm.nih.gov/22173008/) — ★★★
- **분류**: 주기화 모델
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 같은 주 내 일별 비대-근력-파워 변경. 9~12주에 LP보다 약간 우월. 중급+ 권장

**받는 정보**
- 사용자 레벨(중·고급)

**내놓는 것**: 요일별 변수 다른 처방

**예시**: 월=비대(10렙), 수=근력(5렙), 금=파워(3렙) 자동 분배

**[온보딩]에서 적용 목표**: 벌크업 · 근육량 증가
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d02_daily_undulating_dup(
    사용자_레벨,  # 사용자 레벨(중·고급)
):
    """D02: Daily Undulating (DUP). 요일별 변수 다른 처방"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/22173008/
```

---

### D06 — Starting Strength (5x5/5x3)

- **데이터**: `workout_knowledge_base.csv` 40행 (ID `D06`) → [`rules/D06.yaml`](./rules/D06.yaml)
- **근거**: Mark Rippetoe — [https://startingstrength.com/get-started/programs](https://startingstrength.com/get-started/programs) — ★★★
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초보용 LP. 스쿼트/벤치/오버헤드/데드 5렙×3세트, 매 세션 +2.5~5kg 인상. 6~12개월 적합

**받는 정보**
- 사용자 레벨(초보)
- 1RM

**내놓는 것**: 프로그램 처방 (월수금 A/B 교대)

**예시**: 6개월 미만 사용자 디폴트 추천

**[온보딩]에서 적용 목표**: 벌크업 · 스트렝스
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d06_starting_strength_5x5_5x3(
    사용자_레벨,  # 사용자 레벨(초보)
    _1rm,  # 1RM
):
    """D06: Starting Strength (5x5/5x3). 프로그램 처방 (월수금 A/B 교대)"""
    ...  # 근거: https://startingstrength.com/get-started/programs
```

---

### D10 — PHUL/PHAT (하이브리드)

- **데이터**: `workout_knowledge_base.csv` 44행 (ID `D10`) → [`rules/D10.yaml`](./rules/D10.yaml)
- **근거**: Layne Norton / Brandon Campbell — [https://www.muscleandstrength.com/workouts/phat-power-hypertrophy-adaptive-training](https://www.muscleandstrength.com/workouts/phat-power-hypertrophy-adaptive-training) — ★★☆
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근력일+근비대일 결합 분할. 상/하분할 위에 일별 포커스 다름 (PHUL=4일, PHAT=5일)

**받는 정보**
- 사용자 레벨(중급+) / 목표(파워+근비대)

**내놓는 것**: 분할 처방

**예시**: 근력+사이즈 동시 추구하는 중급자

**[온보딩]에서 적용 목표**: 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def d10_phul_phat_하이브리드(
    사용자_레벨_목표,  # 사용자 레벨(중급+) / 목표(파워+근비대)
):
    """D10: PHUL/PHAT (하이브리드). 분할 처방"""
    ...  # 근거: https://www.muscleandstrength.com/workouts/phat-power-hypertrophy-adaptive-training
```

---

### D11 — 초보자 빅3+OHP 디폴트 시작 무게 (남성)

- **데이터**: `workout_knowledge_base.csv` 45행 (ID `D11`) → [`rules/D11.yaml`](./rules/D11.yaml)
- **근거**: StrongLifts 5x5 (Mehdi Hadim) — [https://stronglifts.com/stronglifts-5x5/workout-program/](https://stronglifts.com/stronglifts-5x5/workout-program/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 첫 세션 / 프로그램 진입
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 남성 초보는 스쿼트·벤치·OHP를 빈 바벨(20kg)로, 데드리프트는 40kg(20kg 바+10kg 양쪽)부터 시작

**받는 정보**
- 성별=남
- 운동 경험=없음
- 바벨 종류=20kg 표준

**내놓는 것**: 스쿼트/벤치/OHP 20kg, 데드리프트 40kg 첫 세트

**예시**: "오늘 첫 운동" 입력 시 5x5 20kg 스쿼트로 시작

**[온보딩]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d11_초보자_빅3_ohp_디폴트_시작_무게_남성(
    성별_남,  # 성별=남
    운동_경험_없음,  # 운동 경험=없음
    바벨_종류_20kg_표준,  # 바벨 종류=20kg 표준
):
    """D11: 초보자 빅3+OHP 디폴트 시작 무게 (남성). 스쿼트/벤치/OHP 20kg, 데드리프트 40kg 첫 세트"""
    ...  # 근거: https://stronglifts.com/stronglifts-5x5/workout-program/
```

---

### D12 — 초보자 빅3+OHP 디폴트 시작 무게 (여성)

- **데이터**: `workout_knowledge_base.csv` 46행 (ID `D12`) → [`rules/D12.yaml`](./rules/D12.yaml)
- **근거**: IPF Technical Rules Book 2024 (15kg 여성 바) — [https://www.powerlifting.sport/rules/codes/info/technical-rules](https://www.powerlifting.sport/rules/codes/info/technical-rules) — ★★★
- **분류**: 주기화 모델
- **시점**: 첫 세션 / 프로그램 진입
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 여성 초보는 15kg 여성용 바벨(없으면 20kg) 빈 바로 스쿼트·벤치·OHP, 데드리프트는 30~40kg부터 시작

**받는 정보**
- 성별=여
- 운동 경험=없음
- 바벨 종류=15kg 또는 20kg

**내놓는 것**: 스쿼트/벤치/OHP 15~20kg, 데드리프트 30~40kg

**예시**: 헬스장에 15kg 바 있으면 우선, 없으면 20kg 빈 바 + 폼 점검

**[온보딩]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d12_초보자_빅3_ohp_디폴트_시작_무게_여성(
    성별_여,  # 성별=여
    운동_경험_없음,  # 운동 경험=없음
    바벨_종류_15kg_또는_20kg,  # 바벨 종류=15kg 또는 20kg
):
    """D12: 초보자 빅3+OHP 디폴트 시작 무게 (여성). 스쿼트/벤치/OHP 15~20kg, 데드리프트 30~40kg"""
    ...  # 근거: https://www.powerlifting.sport/rules/codes/info/technical-rules
```

---

### D13 — 빈 바벨로 시작하는 원칙

- **데이터**: `workout_knowledge_base.csv` 47행 (ID `D13`) → [`rules/D13.yaml`](./rules/D13.yaml)
- **근거**: Mark Rippetoe, "Incremental Increases" (Starting Strength) — [https://startingstrength.com/article/incremental_increases](https://startingstrength.com/article/incremental_increases) — ★★☆
- **분류**: 주기화 모델
- **시점**: 첫 세션 / 운동 신규 진입
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 새로운 바벨 운동은 빈 바벨로 시작해 워크셋을 정하고 그 차이를 균등 분할로 워밍업

**받는 정보**
- 운동 종목
- 목표 워크셋 무게

**내놓는 것**: 빈 바 → 50% → 70% → 90% → 100% 분할 제안

**예시**: 초보 첫 스쿼트: 20kg → 30 → 40 → 50kg 워크셋

**[온보딩]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d13_빈_바벨로_시작하는_원칙(
    운동_종목,  # 운동 종목
    목표_워크셋_무게,  # 목표 워크셋 무게
):
    """D13: 빈 바벨로 시작하는 원칙. 빈 바 → 50% → 70% → 90% → 100% 분할 제안"""
    ...  # 근거: https://startingstrength.com/article/incremental_increases
```

---

### D14 — 초보자 첫 세션 워크셋 상한 가이드

- **데이터**: `workout_knowledge_base.csv` 48행 (ID `D14`) → [`rules/D14.yaml`](./rules/D14.yaml)
- **근거**: Mark Rippetoe, Starting Strength: Basic Barbell Training (Blue Book) — [https://startingstrength.com/article/incremental_increases](https://startingstrength.com/article/incremental_increases) — ★★☆
- **분류**: 주기화 모델
- **시점**: 첫 세션 워크셋 결정 시
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 평균 체중 완전 초보 남성이 첫 스쿼트 워크셋에서 65kg(145lb) 5x3을 넘는 경우는 드물다 — 욕심 내지 말 것

**받는 정보**
- 성별
- 체중
- 훈련 이력

**내놓는 것**: 첫 워크셋 상한 65kg(스쿼트, 평균 체중 남성 기준)로 클램프

**예시**: 사용자가 80kg 시작 입력 시 "첫날엔 65kg 정도가 적정"으로 다운그레이드 권장

**[온보딩]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d14_초보자_첫_세션_워크셋_상한_가이드(
    성별,
    체중,
    훈련_이력,  # 훈련 이력
):
    """D14: 초보자 첫 세션 워크셋 상한 가이드. 첫 워크셋 상한 65kg(스쿼트, 평균 체중 남성 기준)로 클램프"""
    ...  # 근거: https://startingstrength.com/article/incremental_increases
```

---

### D15 — 초보자 증량 폭(점프) 디폴트

- **데이터**: `workout_knowledge_base.csv` 49행 (ID `D15`) → [`rules/D15.yaml`](./rules/D15.yaml)
- **근거**: Mark Rippetoe, "Incremental Increases" — [https://startingstrength.com/article/incremental_increases](https://startingstrength.com/article/incremental_increases) — ★★☆
- **분류**: 주기화 모델
- **시점**: 매 세션 성공 후
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 하체(스쿼트·데드)는 세션당 +5kg(초기 +10kg 가능), 상체(벤치·OHP·로우)는 +2.5kg(초기 +5kg). 실패 시 절반 또는 디로드

**받는 정보**
- 직전 세션 성공/실패
- 운동 종목

**내놓는 것**: 다음 세션 무게 자동 계산

**예시**: 60kg 스쿼트 5x5 성공 → 다음 세션 62.5kg 제안

**[온보딩]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d15_초보자_증량_폭_점프_디폴트(
    직전_세션_성공_실패,  # 직전 세션 성공/실패
    운동_종목,  # 운동 종목
):
    """D15: 초보자 증량 폭(점프) 디폴트. 다음 세션 무게 자동 계산"""
    ...  # 근거: https://startingstrength.com/article/incremental_increases
```

---

### D07 — 5/3/1 Wendler

- **데이터**: `workout_knowledge_base.csv` 41행 (ID `D07`) → [`rules/D07.yaml`](./rules/D07.yaml)
- **근거**: Jim Wendler — [https://thefitness.wiki/routines/5-3-1-for-beginners/](https://thefitness.wiki/routines/5-3-1-for-beginners/) — ★★★
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 메인 4주 사이클 (5/3/1+/디로드). TM(트레이닝맥스)=1RM의 90%로 시작, 사이클당 +2.5~5kg

**받는 정보**
- 사용자 레벨(중급)
- 1RM

**내놓는 것**: 4주 처방 자동 생성

**예시**: SS 졸업한 중급자 디폴트 추천

**[온보딩]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d07_5_3_1_wendler(
    사용자_레벨,  # 사용자 레벨(중급)
    _1rm,  # 1RM
):
    """D07: 5/3/1 Wendler. 4주 처방 자동 생성"""
    ...  # 근거: https://thefitness.wiki/routines/5-3-1-for-beginners/
```

---

### D08 — GZCLP

- **데이터**: `workout_knowledge_base.csv` 42행 (ID `D08`) → [`rules/D08.yaml`](./rules/D08.yaml)
- **근거**: Cody LeFever / r/Fitness wiki — [https://thefitness.wiki/routines/gzclp/](https://thefitness.wiki/routines/gzclp/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초·중급 LP. T1(메인 5+렙)→T2(보조 10+렙)→T3(아이솔 15+렙) 3-tier 구조

**받는 정보**
- 사용자 레벨
- 1RM

**내놓는 것**: 프로그램 처방

**예시**: SS 대안. 헬스장 초보~중급 사용자

**[온보딩]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d08_gzclp(
    사용자_레벨,  # 사용자 레벨
    _1rm,  # 1RM
):
    """D08: GZCLP. 프로그램 처방"""
    ...  # 근거: https://thefitness.wiki/routines/gzclp/
```

---

### D09 — nSuns LP

- **데이터**: `workout_knowledge_base.csv` 43행 (ID `D09`) → [`rules/D09.yaml`](./rules/D09.yaml)
- **근거**: nSuns / r/Fitness wiki — [https://thefitness.wiki/routines/nsuns-lp/](https://thefitness.wiki/routines/nsuns-lp/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: Wendler 변형. 주 6일, 메인+보조 모두 5/3/1 패턴. 빠른 무게 진행 (정체기 돌파용)

**받는 정보**
- 사용자 레벨(중급+)

**내놓는 것**: 프로그램 처방

**예시**: 5/3/1 정체기 사용자 옵션

**[온보딩]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d09_nsuns_lp(
    사용자_레벨,  # 사용자 레벨(중급+)
):
    """D09: nSuns LP. 프로그램 처방"""
    ...  # 근거: https://thefitness.wiki/routines/nsuns-lp/
```

---

### D03 — Block Periodization

- **데이터**: `workout_knowledge_base.csv` 37행 (ID `D03`) → [`rules/D03.yaml`](./rules/D03.yaml)
- **근거**: Issurin / Verkhoshansky — [https://www.strongerbyscience.com/periodization-data/](https://www.strongerbyscience.com/periodization-data/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 3~4주 단위 블록(축적-변환-실현). 한 적응 자극 집중. 고급 선수용

**받는 정보**
- 사용자 레벨(고급)

**내놓는 것**: 블록당 1개 적응 우선

**예시**: 고급 모드 옵션, 대회 준비 사용자에게 적합

**[온보딩]에서 적용 목표**: 근육량 증가
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def d03_block_periodization(
    사용자_레벨,  # 사용자 레벨(고급)
):
    """D03: Block Periodization. 블록당 1개 적응 우선"""
    ...  # 근거: https://www.strongerbyscience.com/periodization-data/
```

---

### 분류: 영양

### K19 — Mifflin-St Jeor BMR 공식 (1순위)

- **데이터**: `workout_knowledge_base.csv` 111행 (ID `K19`) → [`rules/K19.yaml`](./rules/K19.yaml)
- **근거**: Mifflin & St Jeor 1990 (Am J Clin Nutr 51:241-7) — [https://pubmed.ncbi.nlm.nih.gov/2305711/](https://pubmed.ncbi.nlm.nih.gov/2305711/) — ★★★
- **분류**: 영양
- **시점**: 온보딩 / 체중 변동 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 남: BMR=10×W(kg)+6.25×H(cm)-5×나이+5 / 여: 동일식 -161. 비만·정상 모두 가장 정확(±10%)한 1차 권장식

**받는 정보**
- 성별
- 체중(kg)
- 키(cm)
- 나이(년)

**내놓는 것**: BMR (kcal/일) — 활동계수 곱하기 전 기초대사량

**예시**: 온보딩에서 키/몸무게/나이/성별 입력 → BMR 자동 산출. 체중 ±2kg 변동 시 재계산

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진
**다른 모듈에도 등장**: 영양·회복

**함수 시그니처(제안)**
```python
def k19_mifflin_st_jeor_bmr_공식_1순위(
    성별,
    체중,  # 체중(kg)
    키,  # 키(cm)
    나이,  # 나이(년)
):
    """K19: Mifflin-St Jeor BMR 공식 (1순위). BMR (kcal/일) — 활동계수 곱하기 전 기초대사량"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/2305711/
```

---

### K20 — Katch-McArdle BMR 공식 (체지방률 알 때)

- **데이터**: `workout_knowledge_base.csv` 112행 (ID `K20`) → [`rules/K20.yaml`](./rules/K20.yaml)
- **근거**: Aragon et al. 2017 ISSN Position Stand (J Int Soc Sports Nutr) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/) — ★★★
- **분류**: 영양
- **시점**: 인바디·체지방률 입력 후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: BMR=370+(21.6×LBM kg). LBM=체중×(1-체지방률). 근육량 많은 사용자에서 Mifflin보다 정확

**받는 정보**
- 체중(kg)
- 체지방률(%)

**내놓는 것**: BMR (kcal/일) — 제지방량 기반

**예시**: 인바디 결과 입력한 사용자에 한해 K19 대신 자동 사용. 체지방률 미입력 시 K19로 폴백

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진
**다른 모듈에도 등장**: 영양·회복

**함수 시그니처(제안)**
```python
def k20_katch_mcardle_bmr_공식_체지방률_알_때(
    체중,  # 체중(kg)
    체지방률,  # 체지방률(%)
):
    """K20: Katch-McArdle BMR 공식 (체지방률 알 때). BMR (kcal/일) — 제지방량 기반"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/
```

---

### K21 — 활동계수(PAL) 표 → TDEE 산출

- **데이터**: `workout_knowledge_base.csv` 113행 (ID `K21`) → [`rules/K21.yaml`](./rules/K21.yaml)
- **근거**: FAO/WHO/UNU 2001 Human Energy Requirements (PAL 표준) — [https://www.fao.org/4/y5686e/y5686e07.htm](https://www.fao.org/4/y5686e/y5686e07.htm) — ★★★
- **분류**: 영양
- **시점**: 온보딩 / 활동량 변경 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: TDEE=BMR×PAL. 좌식 1.2 / 가벼움 1.375 / 보통 1.55 / 활발 1.725 / 매우 활발 1.9

**받는 정보**
- BMR(kcal)
- 활동 카테고리(5단계)

**내놓는 것**: TDEE (kcal/일) — 일일 총 에너지 소비량

**예시**: 온보딩 마지막 단계 직업·주당 운동일수 묻고 5단계 매핑 → BMR×PAL로 유지 칼로리

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진
**다른 모듈에도 등장**: 영양·회복

**함수 시그니처(제안)**
```python
def k21_활동계수_pal_표_tdee_산출(
    bmr,  # BMR(kcal)
    활동_카테고리,  # 활동 카테고리(5단계)
):
    """K21: 활동계수(PAL) 표 → TDEE 산출. TDEE (kcal/일) — 일일 총 에너지 소비량"""
    ...  # 근거: https://www.fao.org/4/y5686e/y5686e07.htm
```

---

### K22 — 활동 카테고리 한국 사용자 매핑

- **데이터**: `workout_knowledge_base.csv` 114행 (ID `K22`) → [`rules/K22.yaml`](./rules/K22.yaml)
- **근거**: FAO/WHO/UNU 2001 PAL 범위 — [https://www.fao.org/4/y5686e/y5686e07.htm](https://www.fao.org/4/y5686e/y5686e07.htm) — ★★☆
- **분류**: 영양
- **시점**: 온보딩
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 사무직+운동X=좌식(1.2) / 주1~3회 헬스=가벼움(1.375) / 주3~5회 중강도=보통(1.55) / 주6~7회 또는 격렬=활발(1.725) / 육체노동+격한 훈련=매우 활발(1.9)

**받는 정보**
- 직업 유형
- 주당 운동 빈도
- 운동 강도(RPE)

**내놓는 것**: 5단계 중 1개 카테고리 자동 선택

**예시**: 한국 직장인 다수=좌식(1.2)+주3회 헬스 → 보수적 1.375 권장(과다추정 방지)

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진
**다른 모듈에도 등장**: 영양·회복

**함수 시그니처(제안)**
```python
def k22_활동_카테고리_한국_사용자_매핑(
    직업_유형,  # 직업 유형
    주당_운동_빈도,  # 주당 운동 빈도
    운동_강도,  # 운동 강도(RPE)
):
    """K22: 활동 카테고리 한국 사용자 매핑. 5단계 중 1개 카테고리 자동 선택"""
    ...  # 근거: https://www.fao.org/4/y5686e/y5686e07.htm
```

---

### K23 — 추정식 정확도 한계·재측정 권장

- **데이터**: `workout_knowledge_base.csv` 115행 (ID `K23`) → [`rules/K23.yaml`](./rules/K23.yaml)
- **근거**: Frankenfield, Roth-Yousey, Compher 2005 (J Am Diet Assoc 105:775) — [https://pubmed.ncbi.nlm.nih.gov/15883556/](https://pubmed.ncbi.nlm.nih.gov/15883556/) — ★★★
- **분류**: 영양
- **시점**: 4주마다 / 체중 정체 시
- **쓰임새**: 지식베이스

**무슨 룰**: Mifflin도 ±10% 오차 존재. 2주간 칼로리 일정+체중 변화로 실측 보정. 정체 시 ±10~15% 조정

**받는 정보**
- 2주 평균 칼로리
- 2주 체중 변화(kg)

**내놓는 것**: TDEE 보정값 = 입력칼로리 ± (체중변화×7700/14)

**예시**: 유지 칼로리 정했는데 2주간 체중 -1kg → 실제 TDEE 추정치보다 -500kcal 낮음. 자동 재보정 알림

**[온보딩]에서 적용 목표**: 다이어트
**다른 모듈에도 등장**: 영양·회복

**함수 시그니처(제안)**
```python
def k23_추정식_정확도_한계_재측정_권장(
    _2주_평균_칼로리,  # 2주 평균 칼로리
    _2주_체중_변화,  # 2주 체중 변화(kg)
):
    """K23: 추정식 정확도 한계·재측정 권장. TDEE 보정값 = 입력칼로리 ± (체중변화×7700/14)"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/15883556/
```

---

### 분류: 특수 모집단

### L04 — 초보/중급/고급 정의

- **데이터**: `workout_knowledge_base.csv` 118행 (ID `L04`) → [`rules/L04.yaml`](./rules/L04.yaml)
- **근거**: Rippetoe (Practical Programming) — [https://startingstrength.com/article/training_age](https://startingstrength.com/article/training_age) — ★★★
- **분류**: 특수 모집단
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초보=훈련 <6개월, 매 세션 진보 가능. 중급=6개월~2년, 주간 진보. 고급=2년+, 메조사이클 단위

**받는 정보**
- 훈련 기간
- 1RM 비율

**내놓는 것**: 레벨 분류

**예시**: 레벨 → 알고리즘 분기 (LP vs 자율조절 vs 블록)

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진
**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l04_초보_중급_고급_정의(
    훈련_기간,  # 훈련 기간
    _1rm_비율,  # 1RM 비율
):
    """L04: 초보/중급/고급 정의. 레벨 분류"""
    ...  # 근거: https://startingstrength.com/article/training_age
```

---

### 분류: 측정/평가

### M01 — 체성분 측정 도구

- **데이터**: `workout_knowledge_base.csv` 123행 (ID `M01`) → [`rules/M01.yaml`](./rules/M01.yaml)
- **근거**: ACSM — [https://www.acsm.org/](https://www.acsm.org/) — ★★★
- **분류**: 측정/평가
- **시점**: 4~6주
- **쓰임새**: 지식베이스

**무슨 룰**: DEXA(±2%) > BIA(±5%) > 줄자/사진 > 체중계. 일관성 > 정확도. 같은 시각·조건 측정

**받는 정보**
- 사용자 측정 환경

**내놓는 것**: 측정 도구 권장

**예시**: 4주마다 사진+줄자 자동 알림

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def m01_체성분_측정_도구(
    사용자_측정_환경,  # 사용자 측정 환경
):
    """M01: 체성분 측정 도구. 측정 도구 권장"""
    ...  # 근거: https://www.acsm.org/
```

---

### M03 — 1RM 측정 방법

- **데이터**: `workout_knowledge_base.csv` 124행 (ID `M03`) → [`rules/M03.yaml`](./rules/M03.yaml)
- **근거**: Reynolds 2006 / NSCA — [https://pubmed.ncbi.nlm.nih.gov/16937972/](https://pubmed.ncbi.nlm.nih.gov/16937972/) — ★★★
- **분류**: 측정/평가
- **시점**: 초기 셋업 / 정기 평가
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 직접 1RM=가장 정확, 부상 위험. AMRAP×Epley/Brzycki=±5% 정확. 초보·고령은 추정만

**받는 정보**
- 사용자 레벨
- 위험 허용도

**내놓는 것**: 측정 방법 분기

**예시**: 중급+ → 8주마다 AMRAP / 고급 → 1RM 테스트 옵션

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def m03_1rm_측정_방법(
    사용자_레벨,  # 사용자 레벨
    위험_허용도,  # 위험 허용도
):
    """M03: 1RM 측정 방법. 측정 방법 분기"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/16937972/
```

---

### M04 — 체중 대비 초보 무게 표준 (Untrained)

- **데이터**: `workout_knowledge_base.csv` 125행 (ID `M04`) → [`rules/M04.yaml`](./rules/M04.yaml)
- **근거**: ExRx.net Strength Standards — [https://exrx.net/Testing/WeightLifting/StrengthStandards](https://exrx.net/Testing/WeightLifting/StrengthStandards) — ★☆☆
- **분류**: 측정/평가
- **시점**: 시작 무게 합리성 검증
- **쓰임새**: 지식베이스

**무슨 룰**: ExRx Untrained: 남 스쿼트 0.75x·벤치 0.5x·데드 1.0x·OHP 0.35x BW; 여 스쿼트 0.4x·벤치 0.25x·데드 0.5x·OHP 0.2x BW

**받는 정보**
- 성별
- 체중

**내놓는 것**: 사용자 시작 무게가 Untrained 범위 내인지 검증 / 과대 입력 차단

**예시**: 70kg 남성 첫날 벤치 60kg 입력 → "Untrained 35kg 수준" 안내

**[온보딩]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def m04_체중_대비_초보_무게_표준_untrained(
    성별,
    체중,
):
    """M04: 체중 대비 초보 무게 표준 (Untrained). 사용자 시작 무게가 Untrained 범위 내인지 검증 / 과대 입력 차단"""
    ...  # 근거: https://exrx.net/Testing/WeightLifting/StrengthStandards
```

---


## 모듈 2 — 세션 시작

매 세션. 워밍업과 그날 컨디션을 반영해 첫 무게를 잡고, 가벼운 안전 점검을 한다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | E02, E09, I05, I06, I07, I08, P05 |
| 벌크업 | E02, E09, I05, I06, I07, P05 |
| 스트렝스 | E02, E09, I05, I06, I08, P05 |
| 근육량 증가 | E02, E09, I05, I06, I07, P05 |
| 건강증진 | E09, I05, I06, I07, I08, P01, P02, P03, P04, P05 |

**고유 룰 수: 11**

### 분류: 실시간 코칭

### E02 — Load-Velocity Profile

- **데이터**: `workout_knowledge_base.csv` 51행 (ID `E02`) → [`rules/E02.yaml`](./rules/E02.yaml)
- **근거**: Vitruve — [https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/](https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 실시간 코칭

**무슨 룰**: 개인별 운동별 무게-속도 선형관계. 워밍업 세트 속도 → 그날의 1RM 추정

**받는 정보**
- 워밍업 세트 무게/속도

**내놓는 것**: 당일 1RM 추정 → 무게 자동 보정

**예시**: 세션 시작 시 워밍업으로 그날 컨디션 반영한 무게 자동 조정

**[세션 시작]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def e02_load_velocity_profile(
    워밍업_세트_무게_속도,  # 워밍업 세트 무게/속도
):
    """E02: Load-Velocity Profile. 당일 1RM 추정 → 무게 자동 보정"""
    ...  # 근거: https://vitruve.fit/blog/vbt-guide-creating-a-load-velocity-profile/
```

---

### E09 — RAMP 워밍업 프로토콜

- **데이터**: `workout_knowledge_base.csv` 58행 (ID `E09`) → [`rules/E09.yaml`](./rules/E09.yaml)
- **근거**: Ian Jeffreys 2007 — [https://humankinetics.me/2019/03/04/what-is-the-ramp-warm-up/](https://humankinetics.me/2019/03/04/what-is-the-ramp-warm-up/) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: R(심박↑)-A(타깃 활성)-M(가동성)-P(종목 점증세트). 정적 스트레칭 회피

**받는 정보**
- 메인 운동
- 작업 무게

**내놓는 것**: 워밍업 시퀀스 자동 생성

**예시**: 바벨 스쿼트 100kg 작업 → 50%×5/70%×3/85%×2 자동 처방

**[세션 시작]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e09_ramp_워밍업_프로토콜(
    메인_운동,  # 메인 운동
    작업_무게,  # 작업 무게
):
    """E09: RAMP 워밍업 프로토콜. 워밍업 시퀀스 자동 생성"""
    ...  # 근거: https://humankinetics.me/2019/03/04/what-is-the-ramp-warm-up/
```

---

### 분류: 기타

### I05 — 일반 워밍업 (전신 체온 상승)

- **데이터**: `workout_knowledge_base.csv` 83행 (ID `I05`) → [`rules/I05.yaml`](./rules/I05.yaml)
- **근거**: NSCA, Introduction to Dynamic Warm-Up — [https://www.nsca.com/education/articles/kinetic-select/introduction-to-dynamic-warm-up/](https://www.nsca.com/education/articles/kinetic-select/introduction-to-dynamic-warm-up/) — ★★★
- **분류**: 기타
- **시점**: 운동 시작 직전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 본 운동 전 5~10분 저강도 유산소(조깅·자전거 등)로 심박·근온도·관절액 가동

**받는 정보**
- 사용자 첫 메인 운동
- 가용 시간

**내놓는 것**: 5~10분 저강도 유산소 권장(땀 살짝 날 정도)

**예시**: 첫 종목 스쿼트 시작 전 사이클 8분 추천

**[세션 시작]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def i05_일반_워밍업_전신_체온_상승(
    사용자_첫_메인_운동,  # 사용자 첫 메인 운동
    가용_시간,  # 가용 시간
):
    """I05: 일반 워밍업 (전신 체온 상승). 5~10분 저강도 유산소 권장(땀 살짝 날 정도)"""
    ...  # 근거: https://www.nsca.com/education/articles/kinetic-select/introduction-to-dynamic-warm-up/
```

---

### I06 — 특이적 워밍업 (워크업 세트) — 컴파운드

- **데이터**: `workout_knowledge_base.csv` 84행 (ID `I06`) → [`rules/I06.yaml`](./rules/I06.yaml)
- **근거**: Mark Rippetoe, Starting Strength — Warmup — [https://startingstrength.com/training/warmup](https://startingstrength.com/training/warmup) — ★★☆
- **분류**: 기타
- **시점**: 메인 컴파운드 첫 세트 직전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 빈 봉 ×5×2세트 → 작업중량의 40%×5 → 60%×3 → 80%×2 → 본 세트 (Starting Strength 표준)

**받는 정보**
- 본 세트 무게(kg)
- 종목(스쿼트/벤치/데드/프레스)

**내놓는 것**: 빈 봉 2세트 + 40/60/80% 워크업 자동 계산

**예시**: 작업 100kg 스쿼트 → 20×5×2, 40×5, 60×3, 80×2, 100×5

**[세션 시작]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def i06_특이적_워밍업_워크업_세트_컴파운드(
    본_세트_무게,  # 본 세트 무게(kg)
    종목,  # 종목(스쿼트/벤치/데드/프레스)
):
    """I06: 특이적 워밍업 (워크업 세트) — 컴파운드. 빈 봉 2세트 + 40/60/80% 워크업 자동 계산"""
    ...  # 근거: https://startingstrength.com/training/warmup
```

---

### I07 — 특이적 워밍업 — 아이솔레이션·머신

- **데이터**: `workout_knowledge_base.csv` 85행 (ID `I07`) → [`rules/I07.yaml`](./rules/I07.yaml)
- **근거**: Greg Nuckols, Stronger by Science — Your Warm-up Doesn't Need to Be That Complicated — [https://www.strongerbyscience.com/warm-up/](https://www.strongerbyscience.com/warm-up/) — ★★☆
- **분류**: 기타
- **시점**: 보조/머신 종목 첫 세트 직전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 아이솔레이션·머신은 1~2 워크업 세트면 충분(약 50%×8, 80%×3); 컴파운드만큼 신경계 준비 불필요

**받는 정보**
- 종목 유형(아이솔레이션/머신)
- 본 세트 무게

**내놓는 것**: 1~2 워크업 세트 권장 (50%×8, 80%×3)

**예시**: 레그익스텐션 50kg → 25×8, 40×3, 50×목표

**[세션 시작]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def i07_특이적_워밍업_아이솔레이션_머신(
    종목_유형,  # 종목 유형(아이솔레이션/머신)
    본_세트_무게,  # 본 세트 무게
):
    """I07: 특이적 워밍업 — 아이솔레이션·머신. 1~2 워크업 세트 권장 (50%×8, 80%×3)"""
    ...  # 근거: https://www.strongerbyscience.com/warm-up/
```

---

### I08 — 무거운 워크업 우선 권고 (시간 부족 시)

- **데이터**: `workout_knowledge_base.csv` 86행 (ID `I08`) → [`rules/I08.yaml`](./rules/I08.yaml)
- **근거**: Greg Nuckols, Stronger by Science — Heavier Warm-ups Are Best — [https://www.strongerbyscience.com/heavier-warm-ups/](https://www.strongerbyscience.com/heavier-warm-ups/) — ★★☆
- **분류**: 기타
- **시점**: 시간 부족 시 워크업 단축 결정
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 시간 부족하면 가벼운 세트 생략하고 무거운 워크업(작업의 80% 부근 ×3~5)을 살릴 것 — 10RM의 80% 워밍업이 총 볼륨 최다

**받는 정보**
- 사용 가능 시간
- 본 세트 무게

**내놓는 것**: 3세트 못할 시 80%×3~5만 1세트 권장

**예시**: 시간 5분 남음 → 빈 봉·40·60% 생략, 80%×3 → 본 세트 진행

**[세션 시작]에서 적용 목표**: 다이어트 · 스트렝스 · 건강증진

**함수 시그니처(제안)**
```python
def i08_무거운_워크업_우선_권고_시간_부족_시(
    사용_가능_시간,  # 사용 가능 시간
    본_세트_무게,  # 본 세트 무게
):
    """I08: 무거운 워크업 우선 권고 (시간 부족 시). 3세트 못할 시 80%×3~5만 1세트 권장"""
    ...  # 근거: https://www.strongerbyscience.com/heavier-warm-ups/
```

---

### 분류: 스트레칭

### P05 — 정적 스트레칭 회피 (워밍업 시)

- **데이터**: `workout_knowledge_base.csv` 137행 (ID `P05`) → [`rules/P05.yaml`](./rules/P05.yaml)
- **근거**: Simic et al. 2013, Scand J Med Sci Sports — meta-analysis — [https://pubmed.ncbi.nlm.nih.gov/22316148/](https://pubmed.ncbi.nlm.nih.gov/22316148/) — ★★★
- **분류**: 스트레칭
- **시점**: 본 세트 직전 60분 이내
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 워밍업 단계에서 ≥45~60초 정적 스트레칭은 최대 근력 평균 -5.4% 감소 — 동적 스트레칭으로 대체

**받는 정보**
- 사용자의 워밍업 루틴 입력

**내놓는 것**: 정적 스트레칭 감지 시 동적(레그스윙·아키바이크)으로 대체 안내

**예시**: 사용자가 "햄스트링 30초 정적 스트레칭" 입력 → 동적 대체 권고 메시지

**[세션 시작]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def p05_정적_스트레칭_회피_워밍업_시(
    사용자의_워밍업_루틴_입력,  # 사용자의 워밍업 루틴 입력
):
    """P05: 정적 스트레칭 회피 (워밍업 시). 정적 스트레칭 감지 시 동적(레그스윙·아키바이크)으로 대체 안내"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/22316148/
```

---

### P01 — 운동 전 스트레칭 (정/동적)

- **데이터**: `workout_knowledge_base.csv` 133행 (ID `P01`) → [`rules/P01.yaml`](./rules/P01.yaml)
- **근거**: Behm 2016 메타분석 — [https://pubmed.ncbi.nlm.nih.gov/26642915/](https://pubmed.ncbi.nlm.nih.gov/26642915/) — ★★★
- **분류**: 스트레칭
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 운동 전 정적 스트레칭(60s+)은 근력↓. 동적 스트레칭이 워밍업에 우월. 정적은 운동 후/별도 세션

**받는 정보**
- 세션 시점

**내놓는 것**: 워밍업 시퀀스 제외/포함

**예시**: RAMP 워밍업 시 정적 스트레칭 자동 제외

**[세션 시작]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def p01_운동_전_스트레칭_정_동적(
    세션_시점,  # 세션 시점
):
    """P01: 운동 전 스트레칭 (정/동적). 워밍업 시퀀스 제외/포함"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/26642915/
```

---

### P02 — PNF 스트레칭

- **데이터**: `workout_knowledge_base.csv` 134행 (ID `P02`) → [`rules/P02.yaml`](./rules/P02.yaml)
- **근거**: Hindle 2012 — [https://pubmed.ncbi.nlm.nih.gov/23487249/](https://pubmed.ncbi.nlm.nih.gov/23487249/) — ★★☆
- **분류**: 스트레칭
- **시점**: 세션 후 / 회복일
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: Contract-relax-contract 패턴. 정적/동적보다 ROM 향상 우월. 단 파트너 필요

**받는 정보**
- 사용자 환경

**내놓는 것**: PNF vs 일반 스트레칭 분기

**예시**: 모빌리티 부족 부위 PNF 처방

**[세션 시작]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def p02_pnf_스트레칭(
    사용자_환경,  # 사용자 환경
):
    """P02: PNF 스트레칭. PNF vs 일반 스트레칭 분기"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/23487249/
```

---

### P03 — 자가근막이완 (SMR/폼롤러)

- **데이터**: `workout_knowledge_base.csv` 135행 (ID `P03`) → [`rules/P03.yaml`](./rules/P03.yaml)
- **근거**: Wiewelhove 2019 메타 — [https://www.frontiersin.org/articles/10.3389/fphys.2019.00376/full](https://www.frontiersin.org/articles/10.3389/fphys.2019.00376/full) — ★★★
- **분류**: 스트레칭
- **시점**: 세션 전후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 30~60s/부위. 운동 전: ROM↑, 근력 영향 없음. 운동 후: DOMS 약간 감소

**받는 정보**
- 세션 시점

**내놓는 것**: 폼롤러 시퀀스

**예시**: 워밍업에 30s/근육군 폼롤러 자동 추가

**[세션 시작]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def p03_자가근막이완_smr_폼롤러(
    세션_시점,  # 세션 시점
):
    """P03: 자가근막이완 (SMR/폼롤러). 폼롤러 시퀀스"""
    ...  # 근거: https://www.frontiersin.org/articles/10.3389/fphys.2019.00376/full
```

---

### P04 — 관절 모빌리티 워크

- **데이터**: `workout_knowledge_base.csv` 136행 (ID `P04`) → [`rules/P04.yaml`](./rules/P04.yaml)
- **근거**: Page 2012 (스트레칭·모빌리티 리뷰) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/) — ★★☆
- **분류**: 스트레칭
- **시점**: 세션 전 / 회복일
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 고관절·발목·흉추 모빌리티 부족이 컴파운드 폼 에러 주원인. 부위별 동적 모빌리티 5~10분

**받는 정보**
- 폼 분석 결과

**내놓는 것**: 부위별 모빌리티 처방

**예시**: 스쿼트 깊이 부족 → 발목/고관절 모빌리티 자동 처방

**[세션 시작]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def p04_관절_모빌리티_워크(
    폼_분석_결과,  # 폼 분석 결과
):
    """P04: 관절 모빌리티 워크. 부위별 모빌리티 처방"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC3273886/
```

---


## 모듈 3 — 세트별 처방

매 세트 직전. 무게·횟수·휴식·폼큐·호흡을 결정해 화면에 띄운다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | A01, A02, A07, A08, C02, C04, C07, E07, E08, E10, E13, E14, E16, J02 |
| 벌크업 | A01, A02, A03, A05, A07, A08, A10, C01, C02, C03, C05, C07, C08, E05, E07, E08, E10, E11, E12, E13, E14, E16, E17, J02 |
| 스트렝스 | A01, A02, A03, A05, A07, A08, A10, A14, C01, C02, C03, C05, C07, E01, E03, E05, E06, E07, E08, E10, E11, E12, E13, E14, E16, E17, J02 |
| 근육량 증가 | A01, A02, A03, A05, A07, A08, A10, C01, C02, C03, C05, C07, E05, E07, E08, E10, E11, E12, E13, E14, E16, E17, F05, J02, J03, J04, J05, J07 |
| 건강증진 | A01, A02, A06, C02, C04, C07, C11, E05, E06, E07, E08, E10, E11, E12, E13, E14, E15, E16, E17, I02, I03 |

**고유 룰 수: 39**

### 분류: RPE 자율조절

### A01 — RPE 정의

- **데이터**: `workout_knowledge_base.csv` 1행 (ID `A01`) → [`rules/A01.yaml`](./rules/A01.yaml)
- **근거**: Zourdos 2016 (Tuchscherer RPE 검증) — [https://pubmed.ncbi.nlm.nih.gov/26049792/](https://pubmed.ncbi.nlm.nih.gov/26049792/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 세트 후 "몇 회 더 가능했나"(RIR)로 강도 측정. 1회 남으면 RPE9, 2회 남으면 RPE8

**받는 정보**
- 사용자가 입력한 RPE (0~10)

**내놓는 것**: RIR로 변환 → 다음 세트 보정의 기준값

**예시**: 앱 UI: '이 세트 RPE는?' 슬라이더 → DB 저장 → 다음 세트 알고리즘 입력

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def a01_rpe_정의(
    사용자가_입력한_rpe,  # 사용자가 입력한 RPE (0~10)
):
    """A01: RPE 정의. RIR로 변환 → 다음 세트 보정의 기준값"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/26049792/
```

---

### A02 — RPE-1RM% 변환표

- **데이터**: `workout_knowledge_base.csv` 2행 (ID `A02`) → [`rules/A02.yaml`](./rules/A02.yaml)
- **근거**: Tuchscherer / PowerliftingToWin — [https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/](https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세션 전 / 세트 직후
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 렙수×목표RPE → 1RM 대비 % 자동 계산. 예: RPE9 3렙=88%, RPE8 5렙=80%

**받는 정보**
- 목표 RPE
- 렙수
- 사용자 1RM

**내놓는 것**: 추천 무게 (kg)

**예시**: 세션 처방: '오늘 5렙 RPE8 목표' → 1RM의 80% 자동 계산해 무게 제시

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def a02_rpe_1rm_변환표(
    목표_rpe,  # 목표 RPE
    렙수,
    사용자_1rm,  # 사용자 1RM
):
    """A02: RPE-1RM% 변환표. 추천 무게 (kg)"""
    ...  # 근거: https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/
```

---

### A07 — RTS Generalized RPE×렙 → %1RM 풀 매트릭스

- **데이터**: `workout_knowledge_base.csv` 7행 (ID `A07`) → [`rules/A07.yaml`](./rules/A07.yaml)
- **근거**: Tuchscherer / RTS · PowerliftingToWin 정리 — [https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/](https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세션 전 / 세트 직후
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: Tuchscherer RTS 표준 변환표. 셀=%1RM. 1렙: RPE10=100·9=95.5·8=92.2 / 5렙: RPE10=86.3·9=83.7·8=81.1 / 8렙: RPE10=78.6·9=76.2·8=74.0 / 12렙: RPE10=71.3·9=70.3·8=67.5 (전체 매트릭스 RPE 6.5~10 × 렙 1~12)

**받는 정보**
- 목표 RPE
- 목표 렙수
- 사용자 1RM

**내놓는 것**: 추천 무게 = 1RM × 셀(%)

**예시**: 오늘 5렙 RPE8 입력 → 표 (5,8) = 81.1% → 1RM 100kg면 81kg 처방

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a07_rts_generalized_rpe_렙_1rm_풀_매트릭스(
    목표_rpe,  # 목표 RPE
    목표_렙수,  # 목표 렙수
    사용자_1rm,  # 사용자 1RM
):
    """A07: RTS Generalized RPE×렙 → %1RM 풀 매트릭스. 추천 무게 = 1RM × 셀(%)"""
    ...  # 근거: https://www.powerliftingtowin.com/a-review-of-mike-tuchscherer-reactive-training-systems-rts/
```

---

### A08 — RIR ↔ RPE 매핑 정의

- **데이터**: `workout_knowledge_base.csv` 8행 (ID `A08`) → [`rules/A08.yaml`](./rules/A08.yaml)
- **근거**: Zourdos 2016 (RIR-based RPE Scale, J Strength Cond Res 30(1):267-275) — [https://pubmed.ncbi.nlm.nih.gov/26049792/](https://pubmed.ncbi.nlm.nih.gov/26049792/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: RPE 10=0 RIR(완전 실패), 9.5=0.5, 9=1, 8.5=1.5, 8=2, 7.5=2.5, 7=3, 6.5=3.5 RIR. 6 이하는 워밍업 영역

**받는 정보**
- 사용자 입력 RPE

**내놓는 것**: 내부 RIR 값으로 변환 → 다음 세트 무게 산출 입력

**예시**: 코칭 UI: '1회 더 가능했음' 탭 → RPE 9 → DB에 RIR=1 기록

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a08_rir_rpe_매핑_정의(
    사용자_입력_rpe,  # 사용자 입력 RPE
):
    """A08: RIR ↔ RPE 매핑 정의. 내부 RIR 값으로 변환 → 다음 세트 무게 산출 입력"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/26049792/
```

---

### A03 — Fatigue Percent (피로 누적률)

- **데이터**: `workout_knowledge_base.csv` 3행 (ID `A03`) → [`rules/A03.yaml`](./rules/A03.yaml)
- **근거**: Tuchscherer / All Things Gym — [https://www.allthingsgym.com/mike-tuchscherer-auto-regulation-fundamentals-fatigue-percentages/](https://www.allthingsgym.com/mike-tuchscherer-auto-regulation-fundamentals-fatigue-percentages/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세션 중
- **쓰임새**: 실시간 코칭

**무슨 룰**: 톱셋(RPE9) 후 무게를 N% 줄여 같은 RPE 도달까지 백오프 세트 누적. 정해진 누적량 도달 시 운동 종료

**받는 정보**
- 톱셋 무게/RPE
- 백오프 세트 RPE

**내놓는 것**: '운동 종료' 신호 또는 '한 세트 더' 신호

**예시**: 컨디션 좋은 날엔 자연스럽게 세트 수 늘어남, 나쁜 날엔 줄어듦. 사용자 부담 없이 자동 조절

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a03_fatigue_percent_피로_누적률(
    톱셋_무게_rpe,  # 톱셋 무게/RPE
    백오프_세트_rpe,  # 백오프 세트 RPE
):
    """A03: Fatigue Percent (피로 누적률). '운동 종료' 신호 또는 '한 세트 더' 신호"""
    ...  # 근거: https://www.allthingsgym.com/mike-tuchscherer-auto-regulation-fundamentals-fatigue-percentages/
```

---

### A05 — 자율조절 vs 고정 %

- **데이터**: `workout_knowledge_base.csv` 5행 (ID `A05`) → [`rules/A05.yaml`](./rules/A05.yaml)
- **근거**: MASS Research — [https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/](https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: RPE 기반 자율조절이 고정 %1RM보다 장기 근력 향상에 우월 (근비대는 차이 미미)

**받는 정보**
- 사용자 목표(근력/근비대)

**내놓는 것**: 근력 목표 → 자율조절 우선, 근비대 → 볼륨 우선 알고리즘 분기

**예시**: '근력 모드'와 '근비대 모드'에서 다른 보정 알고리즘 선택

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a05_자율조절_vs_고정(
    사용자_목표,  # 사용자 목표(근력/근비대)
):
    """A05: 자율조절 vs 고정 %. 근력 목표 → 자율조절 우선, 근비대 → 볼륨 우선 알고리즘 분기"""
    ...  # 근거: https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/
```

---

### A10 — 종목·근육군별 변환 보정

- **데이터**: `workout_knowledge_base.csv` 10행 (ID `A10`) → [`rules/A10.yaml`](./rules/A10.yaml)
- **근거**: Helms RPE accuracy 시리즈 (MASS) / Tuchscherer 종목별 차트 — [https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/](https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세션 전 무게 추천 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 단관절·소근육·고렙 영역에서 같은 RPE라도 실제 %1RM이 표보다 낮음. 스쿼트·벤치는 표에 가깝고 데드는 RPE9~10에서 +1~2%p 더 무거움. 8렙 초과/팔·어깨 단관절은 -3~5%p 하향

**받는 정보**
- 운동 종목
- 근육군

**내놓는 것**: 표 셀 결과 × 종목 보정계수 (스쿼트 1.00 / 벤치 1.00 / 데드 1.01 / 단관절 0.95)

**예시**: '사이드 레터럴 12렙 RPE8' → 표 67.5% × 0.95 = 64% 처방

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a10_종목_근육군별_변환_보정(
    운동_종목,  # 운동 종목
    근육군,
):
    """A10: 종목·근육군별 변환 보정. 표 셀 결과 × 종목 보정계수 (스쿼트 1.00 / 벤치 1.00 / 데드 1.01 / 단관절 0.95)"""
    ...  # 근거: https://massresearchreview.com/2023/05/22/rpe-and-rir-the-complete-guide/
```

---

### A14 — 강도 의존성 보정 (>85% 1RM)

- **데이터**: `workout_knowledge_base.csv` 14행 (ID `A14`) → [`rules/A14.yaml`](./rules/A14.yaml)
- **근거**: Tuchscherer RPE 차트 (RM 간격: 1-2RM 4.5% → 9-10RM 2.3%) — [https://www.exodus-strength.com/forum/viewtopic.php?t=2967](https://www.exodus-strength.com/forum/viewtopic.php?t=2967) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 고강도 영역(<5렙, ≥85% 1RM)에선 1 RPE 오차당 RM 변화가 4.5%로 큼. 보수적으로 -5%(컴파운드)/디폴트 +1단계 더 깎기. 저강도(>10렙)는 2~3%만

**받는 정보**
- 현재 %1RM 추정치
- 렙수

**내놓는 것**: 보정 폭 자동 조정 (5%/3%/2%)

**예시**: 데드 3렙 90% 1RM RPE9 입력(목표8): -5%. 사이드레터럴 15렙 70% RPE9: -2%

**[세트별 처방]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 세트 후 학습

**함수 시그니처(제안)**
```python
def a14_강도_의존성_보정_85_1rm(
    현재_1rm_추정치,  # 현재 %1RM 추정치
    렙수,
):
    """A14: 강도 의존성 보정 (>85% 1RM). 보정 폭 자동 조정 (5%/3%/2%)"""
    ...  # 근거: https://www.exodus-strength.com/forum/viewtopic.php?t=2967
```

---

### A06 — OMNI-RES 스케일

- **데이터**: `workout_knowledge_base.csv` 6행 (ID `A06`) → [`rules/A06.yaml`](./rules/A06.yaml)
- **근거**: Robertson 2003 — [https://pubmed.ncbi.nlm.nih.gov/12569225/](https://pubmed.ncbi.nlm.nih.gov/12569225/) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 초기 셋업
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 0~10 시각형 RPE 스케일. Borg와 r=0.94~0.97. 초보·노인·재활용 검증

**받는 정보**
- 사용자 경험 레벨

**내놓는 것**: 대안 RPE 입력 UI 제공

**예시**: 초보자에게는 시각적 0~10 스케일, 숙련자에게는 RIR 기반 스케일 토글

**[세트별 처방]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def a06_omni_res_스케일(
    사용자_경험_레벨,  # 사용자 경험 레벨
):
    """A06: OMNI-RES 스케일. 대안 RPE 입력 UI 제공"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/12569225/
```

---

### 분류: 세트/렙/강도 처방

### C02 — Repetition Continuum

- **데이터**: `workout_knowledge_base.csv` 21행 (ID `C02`) → [`rules/C02.yaml`](./rules/C02.yaml)
- **근거**: Schoenfeld 2021 / NSCA — [https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근력 ≥85%/1~6렙, 근비대 67~85%/6~12렙, 근지구력 ≤67%/12+렙 (단 근비대는 6~30렙 폭넓게 가능)

**받는 정보**
- 사용자 목표

**내놓는 것**: 렙범위 + %1RM 자동 매핑

**예시**: 목표 선택 → 렙범위와 강도 자동 결정

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def c02_repetition_continuum(
    사용자_목표,  # 사용자 목표
):
    """C02: Repetition Continuum. 렙범위 + %1RM 자동 매핑"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/
```

---

### C04 — ACSM 일반인 가이드라인

- **데이터**: `workout_knowledge_base.csv` 23행 (ID `C04`) → [`rules/C04.yaml`](./rules/C04.yaml)
- **근거**: ACSM 2026 Position Stand — [https://acsm.org/resistance-training-guidelines-update-2026/](https://acsm.org/resistance-training-guidelines-update-2026/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 건강 성인: 주 2~3회, 근육군당 1~4세트, 8~20렙, 40~70% 1RM (강화 시 60~80%, 8~12렙, 2~3분 휴식)

**받는 정보**
- 사용자 프로필(건강 목적)

**내놓는 것**: 초보·일반인 디폴트 처방

**예시**: 운동 목적이 '건강'인 사용자의 시작 디폴트값

**[세트별 처방]에서 적용 목표**: 다이어트 · 건강증진
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def c04_acsm_일반인_가이드라인(
    사용자_프로필,  # 사용자 프로필(건강 목적)
):
    """C04: ACSM 일반인 가이드라인. 초보·일반인 디폴트 처방"""
    ...  # 근거: https://acsm.org/resistance-training-guidelines-update-2026/
```

---

### C07 — 휴식 시간

- **데이터**: `workout_knowledge_base.csv` 26행 (ID `C07`) → [`rules/C07.yaml`](./rules/C07.yaml)
- **근거**: Schoenfeld 2016 / de Salles — [https://pubmed.ncbi.nlm.nih.gov/26605807/](https://pubmed.ncbi.nlm.nih.gov/26605807/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세트 직후
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 근력/파워 3~5분, 컴파운드 근비대 2~3분, 아이솔레이션 1~2분. 1분 < 3분 (Schoenfeld 2016)

**받는 정보**
- 운동 종류
- 목표

**내놓는 것**: 휴식 타이머 자동 카운트다운

**예시**: 세트 종료 후 운동 타입에 맞는 타이머 자동 시작

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def c07_휴식_시간(
    운동_종류,  # 운동 종류
    목표,
):
    """C07: 휴식 시간. 휴식 타이머 자동 카운트다운"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/26605807/
```

---

### C01 — NSCA RM-1RM% 표

- **데이터**: `workout_knowledge_base.csv` 20행 (ID `C01`) → [`rules/C01.yaml`](./rules/C01.yaml)
- **근거**: NSCA Essentials 4판 — [https://www.nsca.com/contentassets/61d813865e264c6e852cadfe247eae52/nsca_training_load_chart.pdf](https://www.nsca.com/contentassets/61d813865e264c6e852cadfe247eae52/nsca_training_load_chart.pdf) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: RM-%1RM 변환표 (예: 5RM=87%, 8RM=80%, 10RM=75%, 12RM=67%)

**받는 정보**
- 목표 렙수
- 1RM

**내놓는 것**: 추천 무게 (kg)

**예시**: 가장 핵심적인 룩업 테이블. 모든 처방의 기반

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c01_nsca_rm_1rm_표(
    목표_렙수,  # 목표 렙수
    _1rm,  # 1RM
):
    """C01: NSCA RM-1RM% 표. 추천 무게 (kg)"""
    ...  # 근거: https://www.nsca.com/contentassets/61d813865e264c6e852cadfe247eae52/nsca_training_load_chart.pdf
```

---

### C03 — NSCA 단계별 처방

- **데이터**: `workout_knowledge_base.csv` 22행 (ID `C03`) → [`rules/C03.yaml`](./rules/C03.yaml)
- **근거**: NSCA / Bompa — [https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/](https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근비대기: 50~75% 1RM, 8~20렙, 3~6세트 / 근력기: 80~95% 1RM, 2~6렙, 2~6세트

**받는 정보**
- 훈련 단계

**내놓는 것**: 세트수+렙수+강도 처방

**예시**: 훈련 단계 전환 시 변수 자동 변경

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c03_nsca_단계별_처방(
    훈련_단계,  # 훈련 단계
):
    """C03: NSCA 단계별 처방. 세트수+렙수+강도 처방"""
    ...  # 근거: https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/
```

---

### C05 — 실패 vs RIR

- **데이터**: `workout_knowledge_base.csv` 24행 (ID `C05`) → [`rules/C05.yaml`](./rules/C05.yaml)
- **근거**: Refalo / Pelland 2024 — [https://pmc.ncbi.nlm.nih.gov/articles/PMC10161210/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10161210/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근력은 실패/비실패 차이 미미, 근비대는 실패 가까울수록 약간 우월. RIR 0~3 모두 유사 효과

**받는 정보**
- 운동 종류

**내놓는 것**: 컴파운드 RIR 2~3 / 아이솔레이션 RIR 0~2 디폴트

**예시**: 실패 강요 X, 운동 종류별 안전한 디폴트 RIR 처방

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c05_실패_vs_rir(
    운동_종류,  # 운동 종류
):
    """C05: 실패 vs RIR. 컴파운드 RIR 2~3 / 아이솔레이션 RIR 0~2 디폴트"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC10161210/
```

---

### C08 — Double Progression

- **데이터**: `workout_knowledge_base.csv` 27행 (ID `C08`) → [`rules/C08.yaml`](./rules/C08.yaml)
- **근거**: Legion / Bret Contreras — [https://legionathletics.com/double-progression/](https://legionathletics.com/double-progression/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 후
- **쓰임새**: 운동 추천, 실시간 코칭

**무슨 룰**: 렙 범위 처방(예: 8~12렙). 모든 세트가 상한 도달 → 무게 +2.5~5% 인상, 렙 하한 리셋

**받는 정보**
- 지난 세션 모든 세트 성공 여부

**내놓는 것**: 다음 세션 무게 자동 인상 또는 유지

**예시**: 세션 끝 → '모두 12렙 성공' → 다음 세션 +2.5kg, 8렙으로 시작

**[세트별 처방]에서 적용 목표**: 벌크업
**다른 모듈에도 등장**: 세트 후 학습

**함수 시그니처(제안)**
```python
def c08_double_progression(
    지난_세션_모든_세트_성공_여부,  # 지난 세션 모든 세트 성공 여부
):
    """C08: Double Progression. 다음 세션 무게 자동 인상 또는 유지"""
    ...  # 근거: https://legionathletics.com/double-progression/
```

---

### C11 — 세션 길이 가이드

- **데이터**: `workout_knowledge_base.csv` 30행 (ID `C11`) → [`rules/C11.yaml`](./rules/C11.yaml)
- **근거**: NSCA Essentials — [https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/](https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/) — ★★☆
- **분류**: 세트/렙/강도 처방
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 효율 세션 45~75분. 분할로 길이 조절. 90분+ 코르티솔 주장은 1차 출처 약함

**받는 정보**
- 가용 시간
- 분할

**내놓는 것**: 세션 운동 수/세트 수 자동 조정

**예시**: '40분만 가능' 입력 → 운동 4~5개로 압축한 세션 자동 빌드

**[세트별 처방]에서 적용 목표**: 건강증진
**다른 모듈에도 등장**: 메조사이클 관리

**함수 시그니처(제안)**
```python
def c11_세션_길이_가이드(
    가용_시간,  # 가용 시간
    분할,
):
    """C11: 세션 길이 가이드. 세션 운동 수/세트 수 자동 조정"""
    ...  # 근거: https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/
```

---

### 분류: 실시간 코칭

### E07 — 벤치프레스 폼 큐

- **데이터**: `workout_knowledge_base.csv` 56행 (ID `E07`) → [`rules/E07.yaml`](./rules/E07.yaml)
- **근거**: PowerliftingTechnique / Starting Strength — [https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology](https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 발 고정·광배 활성·어깨 후퇴/하강·바 패스 가슴하부→어깨위·팔꿈치 45~75°

**받는 정보**
- 운동명·셋업 단계

**내놓는 것**: 셋업 체크리스트·큐 출력

**예시**: 세트 시작 전 체크리스트 표시 + 음성 코칭

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e07_벤치프레스_폼_큐(
    운동명_셋업_단계,  # 운동명·셋업 단계
):
    """E07: 벤치프레스 폼 큐. 셋업 체크리스트·큐 출력"""
    ...  # 근거: https://startingstrength.com/article/the-bench-press-anatomy-and-kinesiology
```

---

### E08 — 데드리프트 폼 큐

- **데이터**: `workout_knowledge_base.csv` 57행 (ID `E08`) → [`rules/E08.yaml`](./rules/E08.yaml)
- **근거**: PowerliftingTechnique / Men's Journal — [https://powerliftingtechnique.com/deadlift-cues/](https://powerliftingtechnique.com/deadlift-cues/) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 바 발 위 중간·광배 잠금·척추 중립·다리로 밀기·밸살바 호흡

**받는 정보**
- 운동명·셋업 단계

**내놓는 것**: 셋업 체크리스트·큐 출력

**예시**: 세트 시작 전 셋업 가이드 자동 안내

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e08_데드리프트_폼_큐(
    운동명_셋업_단계,  # 운동명·셋업 단계
):
    """E08: 데드리프트 폼 큐. 셋업 체크리스트·큐 출력"""
    ...  # 근거: https://powerliftingtechnique.com/deadlift-cues/
```

---

### E10 — 오버헤드프레스 폼 큐

- **데이터**: `workout_knowledge_base.csv` 59행 (ID `E10`) → [`rules/E10.yaml`](./rules/E10.yaml)
- **근거**: Starting Strength / Stronger By Science — [https://startingstrength.com/article/the-press](https://startingstrength.com/article/the-press) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 발 어깨너비, 코어/둔근 잠금, 바 코끝 → 머리 위 직선 경로, 락아웃 시 머리 통과

**받는 정보**
- 운동명·셋업 단계

**내놓는 것**: 셋업 체크리스트·외적 큐 출력

**예시**: 셋업 가이드 + 세트 중 '천장 밀어' 같은 외적 큐 안내

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e10_오버헤드프레스_폼_큐(
    운동명_셋업_단계,  # 운동명·셋업 단계
):
    """E10: 오버헤드프레스 폼 큐. 셋업 체크리스트·외적 큐 출력"""
    ...  # 근거: https://startingstrength.com/article/the-press
```

---

### E13 — Valsalva 호흡

- **데이터**: `workout_knowledge_base.csv` 62행 (ID `E13`) → [`rules/E13.yaml`](./rules/E13.yaml)
- **근거**: NSCA Essentials / Hackett 2013 — [https://pubmed.ncbi.nlm.nih.gov/23222073/](https://pubmed.ncbi.nlm.nih.gov/23222073/) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 고중량(>80%) 시 들숨 → 호흡정지로 복강내압 형성 → 하강 → 상승 후 배출. 고혈압자 주의

**받는 정보**
- 무게 비율
- 운동 종류

**내놓는 것**: 호흡 큐 자동 출력

**예시**: 컴파운드 80%+ 세트 시작 전 호흡 안내

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e13_valsalva_호흡(
    무게_비율,  # 무게 비율
    운동_종류,  # 운동 종류
):
    """E13: Valsalva 호흡. 호흡 큐 자동 출력"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/23222073/
```

---

### E14 — 가동범위 (ROM) 기준

- **데이터**: `workout_knowledge_base.csv` 63행 (ID `E14`) → [`rules/E14.yaml`](./rules/E14.yaml)
- **근거**: Pedrosa 2022 (Eur J Sport Sci) — [https://pubmed.ncbi.nlm.nih.gov/33977835/](https://pubmed.ncbi.nlm.nih.gov/33977835/) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 풀ROM이 부분반복보다 근비대·근력 우월. 단 신장 위치 강조 부분반복은 풀ROM 동등 또는 우월

**받는 정보**
- 운동명
- 사용자 ROM 데이터

**내놓는 것**: ROM 부족 시 큐 출력

**예시**: 스쿼트 깊이 부족 감지 → '엉덩이 더 내려' 큐

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e14_가동범위_rom_기준(
    운동명,
    사용자_rom_데이터,  # 사용자 ROM 데이터
):
    """E14: 가동범위 (ROM) 기준. ROM 부족 시 큐 출력"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/33977835/
```

---

### E16 — 컴파운드 셋업 체크리스트

- **데이터**: `workout_knowledge_base.csv` 65행 (ID `E16`) → [`rules/E16.yaml`](./rules/E16.yaml)
- **근거**: NSCA / Starting Strength — [https://startingstrength.com/article/the_squat](https://startingstrength.com/article/the_squat) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 직전
- **쓰임새**: 실시간 코칭

**무슨 룰**: ①발 위치 ②그립 너비 ③척추 중립 ④광배/코어 잠금 ⑤호흡 셋팅 5단계

**받는 정보**
- 운동명

**내놓는 것**: 단계별 체크리스트 UI

**예시**: 모든 컴파운드 첫 세트 전 자동 표시

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e16_컴파운드_셋업_체크리스트(
    운동명,
):
    """E16: 컴파운드 셋업 체크리스트. 단계별 체크리스트 UI"""
    ...  # 근거: https://startingstrength.com/article/the_squat
```

---

### E05 — External vs Internal 큐

- **데이터**: `workout_knowledge_base.csv` 54행 (ID `E05`) → [`rules/E05.yaml`](./rules/E05.yaml)
- **근거**: Wulf — [https://www.thestrengthathlete.com/blog/external-cues](https://www.thestrengthathlete.com/blog/external-cues) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 외적 큐("천장으로 밀어") > 내적 큐("가슴 사용"). 학습·수행 모두 외적 큐 우월

**받는 정보**
- 운동명·동작 단계

**내놓는 것**: 운동별 외적 큐 텍스트/음성 출력

**예시**: 세트 시작 전 '바닥을 찢어내듯' 같은 외적 큐 자동 안내

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e05_external_vs_internal_큐(
    운동명_동작_단계,  # 운동명·동작 단계
):
    """E05: External vs Internal 큐. 운동별 외적 큐 텍스트/음성 출력"""
    ...  # 근거: https://www.thestrengthathlete.com/blog/external-cues
```

---

### E11 — 풀업/친업 폼 큐

- **데이터**: `workout_knowledge_base.csv` 60행 (ID `E11`) → [`rules/E11.yaml`](./rules/E11.yaml)
- **근거**: Stronger By Science — [https://startingstrength.com/article/chins-and-pullups](https://startingstrength.com/article/chins-and-pullups) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 어깨 후퇴/하강 시작 → 가슴을 바에 → 턱이 바 위. 발 교차/킵핑 금지

**받는 정보**
- 운동명·셋업 단계

**내놓는 것**: 셋업 체크리스트·큐 출력

**예시**: 셋업 가이드 + 음성 코칭

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e11_풀업_친업_폼_큐(
    운동명_셋업_단계,  # 운동명·셋업 단계
):
    """E11: 풀업/친업 폼 큐. 셋업 체크리스트·큐 출력"""
    ...  # 근거: https://startingstrength.com/article/chins-and-pullups
```

---

### E12 — 바벨 로우 폼 큐

- **데이터**: `workout_knowledge_base.csv` 61행 (ID `E12`) → [`rules/E12.yaml`](./rules/E12.yaml)
- **근거**: Strength Log — [https://www.strengthlog.com/barbell-row/](https://www.strengthlog.com/barbell-row/) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 힙힌지 45도, 척추 중립, 바를 배꼽 하단으로, 팔꿈치 옆구리 향함, 견갑 후퇴

**받는 정보**
- 운동명·셋업

**내놓는 것**: 셋업 체크리스트·큐 출력

**예시**: 셋업 가이드 + 외적 큐

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e12_바벨_로우_폼_큐(
    운동명_셋업,  # 운동명·셋업
):
    """E12: 바벨 로우 폼 큐. 셋업 체크리스트·큐 출력"""
    ...  # 근거: https://www.strengthlog.com/barbell-row/
```

---

### E17 — 그립 너비/유형

- **데이터**: `workout_knowledge_base.csv` 66행 (ID `E17`) → [`rules/E17.yaml`](./rules/E17.yaml)
- **근거**: PowerliftingTechnique / SBS — [https://startingstrength.com/article/grip-width-on-the-bench-press](https://startingstrength.com/article/grip-width-on-the-bench-press) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 벤치: 어깨너비 1.5배. 데드: 어깨너비. 풀업: 광배=와이드, 이두=내로우/언더. 후크그립=고중량 데드

**받는 정보**
- 운동명
- 목표 근육

**내놓는 것**: 권장 그립 너비/유형 출력

**예시**: 운동 선택 시 그립 옵션 안내

**[세트별 처방]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def e17_그립_너비_유형(
    운동명,
    목표_근육,  # 목표 근육
):
    """E17: 그립 너비/유형. 권장 그립 너비/유형 출력"""
    ...  # 근거: https://startingstrength.com/article/grip-width-on-the-bench-press
```

---

### E01 — VBT (속도 기반 훈련)

- **데이터**: `workout_knowledge_base.csv` 50행 (ID `E01`) → [`rules/E01.yaml`](./rules/E01.yaml)
- **근거**: NSCA SCJ 2021 — [https://journals.lww.com/nsca-scj/fulltext/2021/04000/velocity_based_training__from_theory_to.4.aspx](https://journals.lww.com/nsca-scj/fulltext/2021/04000/velocity_based_training__from_theory_to.4.aspx) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 바벨 속도(m/s) 측정으로 강도/피로 실시간 모니터링. 1RM 추정·동기·피로 감지

**받는 정보**
- 바벨 속도 데이터(센서/카메라)

**내놓는 것**: 실시간 피로 알림·1RM 추정

**예시**: 폰 카메라 컴퓨터비전으로 속도 추정 가능

**[세트별 처방]에서 적용 목표**: 스트렝스

**함수 시그니처(제안)**
```python
def e01_vbt_속도_기반_훈련(
    바벨_속도_데이터,  # 바벨 속도 데이터(센서/카메라)
):
    """E01: VBT (속도 기반 훈련). 실시간 피로 알림·1RM 추정"""
    ...  # 근거: https://journals.lww.com/nsca-scj/fulltext/2021/04000/velocity_based_training__from_theory_to.4.aspx
```

---

### E03 — Velocity Loss 임계

- **데이터**: `workout_knowledge_base.csv` 52행 (ID `E03`) → [`rules/E03.yaml`](./rules/E03.yaml)
- **근거**: Pareja-Blanco / Sports Med 2022 — [https://pmc.ncbi.nlm.nih.gov/articles/PMC9807551/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9807551/) — ★★★
- **분류**: 실시간 코칭
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 첫 렙 대비 속도 감소율로 종료. 파워 10~20%, 근력 20~25%, 근비대 25~40%. 35%+ 지속 권장X

**받는 정보**
- 렙별 속도
- 목표

**내놓는 것**: 속도 감소 임계 도달 시 세트 강제 종료

**예시**: 목표별 임계값 다름. '근력 모드'면 25% 도달 시 종료

**[세트별 처방]에서 적용 목표**: 스트렝스

**함수 시그니처(제안)**
```python
def e03_velocity_loss_임계(
    렙별_속도,  # 렙별 속도
    목표,
):
    """E03: Velocity Loss 임계. 속도 감소 임계 도달 시 세트 강제 종료"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC9807551/
```

---

### E06 — 스쿼트 폼 에러·큐

- **데이터**: `workout_knowledge_base.csv` 55행 (ID `E06`) → [`rules/E06.yaml`](./rules/E06.yaml)
- **근거**: Power Rack Strength / TPS — [https://www.powerrackstrength.com/3-common-squat-mistakes/](https://www.powerrackstrength.com/3-common-squat-mistakes/) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세트 중 / 세트 후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 무릎 내회전·깊이 부족·중심 이동·골반 윙크 → 외적 큐 매핑

**받는 정보**
- 폼 분석(영상/사용자 보고) 결과

**내놓는 것**: 에러 → 큐 매핑 출력

**예시**: 비전 모델로 에러 감지 후 해당 큐 음성 안내

**[세트별 처방]에서 적용 목표**: 스트렝스 · 건강증진

**함수 시그니처(제안)**
```python
def e06_스쿼트_폼_에러_큐(
    폼_분석결과,  # 폼 분석(영상/사용자 보고) 결과
):
    """E06: 스쿼트 폼 에러·큐. 에러 → 큐 매핑 출력"""
    ...  # 근거: https://www.powerrackstrength.com/3-common-squat-mistakes/
```

---

### E15 — 부상 신호 vs 근육통

- **데이터**: `workout_knowledge_base.csv` 64행 (ID `E15`) → [`rules/E15.yaml`](./rules/E15.yaml)
- **근거**: Cheung 2003 (DOMS 리뷰) — [https://pubmed.ncbi.nlm.nih.gov/12617692/](https://pubmed.ncbi.nlm.nih.gov/12617692/) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세션 중 / 세션 후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 관절통·날카로운 통증·국소 통증=부상 신호. 양측 대칭 둔통 24~72h=DOMS(정상)

**받는 정보**
- 사용자 통증 위치/강도/시점

**내놓는 것**: 운동 중단 권고 또는 정상 신호 분기

**예시**: 통증 입력 → 부위/패턴 분석 → 중단/계속 분기

**[세트별 처방]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def e15_부상_신호_vs_근육통(
    사용자_통증_위치_강도_시점,  # 사용자 통증 위치/강도/시점
):
    """E15: 부상 신호 vs 근육통. 운동 중단 권고 또는 정상 신호 분기"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/12617692/
```

---

### 분류: 운동 선택

### J02 — 장비별 대체 운동

- **데이터**: `workout_knowledge_base.csv` 88행 (ID `J02`) → [`rules/J02.yaml`](./rules/J02.yaml)
- **근거**: Free Exercise DB / wger — [https://github.com/yuhonas/free-exercise-db](https://github.com/yuhonas/free-exercise-db) — ★★★
- **분류**: 운동 선택
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 바벨 없음→덤벨/케틀벨. 헬스장 없음→맨몸+밴드. 머신 없음→자유중량+케이블. 기능 동일성 우선

**받는 정보**
- 사용자 장비 환경

**내놓는 것**: 운동 라이브러리 필터링

**예시**: '집에서 운동' 선택 → 맨몸/밴드/덤벨 운동만 추천

**[세트별 처방]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def j02_장비별_대체_운동(
    사용자_장비_환경,  # 사용자 장비 환경
):
    """J02: 장비별 대체 운동. 운동 라이브러리 필터링"""
    ...  # 근거: https://github.com/yuhonas/free-exercise-db
```

---

### F05 — SFR (자극/피로 비율)

- **데이터**: `workout_knowledge_base.csv` 67행 (ID `F05`) → [`rules/F05.yaml`](./rules/F05.yaml)
- **근거**: Israetel / RP — [https://www.strongerbyscience.com/exercise-selection/](https://www.strongerbyscience.com/exercise-selection/) — ★★☆
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 컴파운드 SFR 보통, 머신/아이솔 SFR 우수. 부상·피로 시 SFR 높은 운동으로 대체

**받는 정보**
- 부상 부위
- 피로 상태

**내놓는 것**: 대체 운동 후보 추천

**예시**: 무릎 통증 입력 → 백스쿼트 대신 레그프레스 추천

**[세트별 처방]에서 적용 목표**: 근육량 증가
**별도 레이어**: 메타 룰

**함수 시그니처(제안)**
```python
def f05_sfr_자극_피로_비율(
    부상_부위,  # 부상 부위
    피로_상태,  # 피로 상태
):
    """F05: SFR (자극/피로 비율). 대체 운동 후보 추천"""
    ...  # 근거: https://www.strongerbyscience.com/exercise-selection/
```

---

### J03 — 자유중량 vs 머신

- **데이터**: `workout_knowledge_base.csv` 89행 (ID `J03`) → [`rules/J03.yaml`](./rules/J03.yaml)
- **근거**: Schwanbeck 2020 / Haugen 2023 — [https://pubmed.ncbi.nlm.nih.gov/32358310/](https://pubmed.ncbi.nlm.nih.gov/32358310/) — ★★★
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근비대는 동등. 근력 전이는 자유중량 약간 우월. 안전성/단독훈련은 머신 우월

**받는 정보**
- 사용자 목표/환경/경험

**내놓는 것**: 운동 풀 분기

**예시**: 초보+안전 선호 → 머신 비중↑ / 근력 목표 → 자유중량↑

**[세트별 처방]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def j03_자유중량_vs_머신(
    사용자_목표_환경_경험,  # 사용자 목표/환경/경험
):
    """J03: 자유중량 vs 머신. 운동 풀 분기"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/32358310/
```

---

### J04 — 편측 vs 양측 운동

- **데이터**: `workout_knowledge_base.csv` 90행 (ID `J04`) → [`rules/J04.yaml`](./rules/J04.yaml)
- **근거**: McCurdy 2005 / NSCA — [https://pubmed.ncbi.nlm.nih.gov/15705051/](https://pubmed.ncbi.nlm.nih.gov/15705051/) — ★★☆
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 양측 강도↑·시간 효율 우월. 편측은 좌우 불균형 교정·코어 자극·재활 유리. 둘 다 포함 권장

**받는 정보**
- 사용자 불균형 데이터

**내놓는 것**: 운동 선택 비율 조정

**예시**: 좌우 불균형 입력 → 편측 운동 비중 증가

**[세트별 처방]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def j04_편측_vs_양측_운동(
    사용자_불균형_데이터,  # 사용자 불균형 데이터
):
    """J04: 편측 vs 양측 운동. 운동 선택 비율 조정"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/15705051/
```

---

### J05 — 컴파운드:아이솔 비율

- **데이터**: `workout_knowledge_base.csv` 91행 (ID `J05`) → [`rules/J05.yaml`](./rules/J05.yaml)
- **근거**: Israetel / NSCA — [https://www.strongerbyscience.com/exercise-selection/](https://www.strongerbyscience.com/exercise-selection/) — ★★☆
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초보 70:30, 중급 60:40, 고급 50:50. 약점 부위만 아이솔로 보강

**받는 정보**
- 사용자 레벨
- 약점 부위

**내놓는 것**: 세션 운동 구성 비율

**예시**: 자동 세션 빌드 시 비율 적용

**[세트별 처방]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def j05_컴파운드_아이솔_비율(
    사용자_레벨,  # 사용자 레벨
    약점_부위,  # 약점 부위
):
    """J05: 컴파운드:아이솔 비율. 세션 운동 구성 비율"""
    ...  # 근거: https://www.strongerbyscience.com/exercise-selection/
```

---

### J07 — 근육군 매핑 (primary/secondary)

- **데이터**: `workout_knowledge_base.csv` 92행 (ID `J07`) → [`rules/J07.yaml`](./rules/J07.yaml)
- **근거**: wger / Free Exercise DB — [https://wger.de/en/software/api](https://wger.de/en/software/api) — ★★★
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 각 운동의 주작용근/보조근 명시. 주간 볼륨 카운트 시 primary는 1.0 / secondary는 0.5 가중

**받는 정보**
- 운동 ID

**내놓는 것**: 근육군별 가중 볼륨 카운트

**예시**: 주간 볼륨 추적 알고리즘에 사용

**[세트별 처방]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def j07_근육군_매핑_primary_secondary(
    운동_id,  # 운동 ID
):
    """J07: 근육군 매핑 (primary/secondary). 근육군별 가중 볼륨 카운트"""
    ...  # 근거: https://wger.de/en/software/api
```

---

### 분류: 기타

### I02 — Tempo Notation

- **데이터**: `workout_knowledge_base.csv` 80행 (ID `I02`) → [`rules/I02.yaml`](./rules/I02.yaml)
- **근거**: NSCA — [https://www.strongerbyscience.com/tempo-for-muscle/](https://www.strongerbyscience.com/tempo-for-muscle/) — ★☆☆
- **분류**: 기타
- **시점**: 세트 중
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 4-숫자 표기(예: 3-1-1-0): 이심성-바닥-구심성-탑. 이심성 2~4초, 구심성 1~2초

**받는 정보**
- 운동 처방 템포

**내놓는 것**: 세트 내 메트로놈/비프음 코칭

**예시**: 옵션 기능: 비프음으로 템포 안내

**[세트별 처방]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def i02_tempo_notation(
    운동_처방_템포,  # 운동 처방 템포
):
    """I02: Tempo Notation. 세트 내 메트로놈/비프음 코칭"""
    ...  # 근거: https://www.strongerbyscience.com/tempo-for-muscle/
```

---

### I03 — 운동 순서 (컴파운드 우선)

- **데이터**: `workout_knowledge_base.csv` 81행 (ID `I03`) → [`rules/I03.yaml`](./rules/I03.yaml)
- **근거**: NSCA Essentials — [https://www.strongerbyscience.com/exercise-order-video/](https://www.strongerbyscience.com/exercise-order-video/) — ★★★
- **분류**: 기타
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 컴파운드 → 보조 컴파운드 → 아이솔레이션 순서. 신경피로·안전성 이유

**받는 정보**
- 세션 운동 목록

**내놓는 것**: 세션 내 운동 순서 자동 정렬

**예시**: 세션 빌더가 운동 추가 시 자동 정렬

**[세트별 처방]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def i03_운동_순서_컴파운드_우선(
    세션_운동_목록,  # 세션 운동 목록
):
    """I03: 운동 순서 (컴파운드 우선). 세션 내 운동 순서 자동 정렬"""
    ...  # 근거: https://www.strongerbyscience.com/exercise-order-video/
```

---


## 모듈 4 — 세트 후 학습

매 세트 직후. 사용자 입력(RPE/실패 여부)을 받아 다음 세트와 다음 세션 무게를 보정한다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | A04, A09, A11, C08, C12, C13, C14 |
| 벌크업 | A04, A09, A11, A12, A13, C08, C12, C13, C14, C15 |
| 스트렝스 | A04, A09, A11, A12, A13, A14, C08, C12, C13, C14, C15, E04 |
| 근육량 증가 | A04, A09, A11, A12, A13, C08, C12, C13, C14, C15, E04 |
| 건강증진 | A04, C08, I04 |

**고유 룰 수: 13**

### 분류: RPE 자율조절

### A04 — RIR 예측 정확도 보정

- **데이터**: `workout_knowledge_base.csv` 4행 (ID `A04`) → [`rules/A04.yaml`](./rules/A04.yaml)
- **근거**: MASS Research / Bastos 2024 — [https://pmc.ncbi.nlm.nih.gov/articles/PMC11127506/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11127506/) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 사용자는 RIR을 평균 1회 정도 과소예측 (특히 RIR≥3 입력 시 더 부정확)

**받는 정보**
- 사용자 입력 RIR

**내놓는 것**: 내부값 = 입력값 + 보정계수(0~+1)

**예시**: 초보자/노인은 +1 보정 강하게. 중·고급자는 약하게. 정확한 강도 추정에 필수

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def a04_rir_예측_정확도_보정(
    사용자_입력_rir,  # 사용자 입력 RIR
):
    """A04: RIR 예측 정확도 보정. 내부값 = 입력값 + 보정계수(0~+1)"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC11127506/
```

---

### A09 — RPE 변환표 정확도/검증 한계

- **데이터**: `workout_knowledge_base.csv` 9행 (ID `A09`) → [`rules/A09.yaml`](./rules/A09.yaml)
- **근거**: Zourdos 2016 / Helms 2017 RPE accuracy — [https://pubmed.ncbi.nlm.nih.gov/26049792/](https://pubmed.ncbi.nlm.nih.gov/26049792/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세션 후 캘리브레이션
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 표는 경험적(Tuchscherer 코칭)이며 Zourdos 2016에서 RIR 매핑은 검증됐으나 셀별 %1RM은 ±2~5%p 오차. 경험자가 1RM에서 RPE 더 정확. 초보·RIR≥3 구간은 과소예측 (A04와 동일 보정 필요)

**받는 정보**
- 사용자 경험 레벨
- 종목

**내놓는 것**: 보정계수: 초보 ±5%p · 중급 ±3%p · 고급 ±2%p 신뢰구간

**예시**: '예상 RPE 8 → 실제 RPE 9.5'가 3세션 연속이면 표 수치를 -3%p 자동 캘리브레이션

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a09_rpe_변환표_정확도_검증_한계(
    사용자_경험_레벨,  # 사용자 경험 레벨
    종목,
):
    """A09: RPE 변환표 정확도/검증 한계. 보정계수: 초보 ±5%p · 중급 ±3%p · 고급 ±2%p 신뢰구간"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/26049792/
```

---

### A11 — 세트 간 무게 보정 (Helms 룰)

- **데이터**: `workout_knowledge_base.csv` 11행 (ID `A11`) → [`rules/A11.yaml`](./rules/A11.yaml)
- **근거**: Helms (Muscle and Strength Pyramid) / Ripped Body — [https://rippedbody.com/rpe/](https://rippedbody.com/rpe/) — ★★★
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 목표 RPE 대비 0.5점 차이당 무게 ±2% (1점=±4%, 2점=±8%). 동일 세션의 다음 세트에 즉시 적용

**받는 정보**
- 목표 RPE
- 입력 RPE
- 현재 무게

**내놓는 것**: 다음 세트 추천 무게 (kg)

**예시**: 5렙 RPE8 목표 + 입력 RPE9 → 다음 세트 -4% (100kg → 96kg). RPE7 입력 → +4% (104kg)

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a11_세트_간_무게_보정_helms_룰(
    목표_rpe,  # 목표 RPE
    입력_rpe,  # 입력 RPE
    현재_무게,  # 현재 무게
):
    """A11: 세트 간 무게 보정 (Helms 룰). 다음 세트 추천 무게 (kg)"""
    ...  # 근거: https://rippedbody.com/rpe/
```

---

### A12 — 세트 간 무게 보정 (RTS 룰)

- **데이터**: `workout_knowledge_base.csv` 12행 (ID `A12`) → [`rules/A12.yaml`](./rules/A12.yaml)
- **근거**: Tuchscherer Reactive Training Systems / Exodus Strength 분석 — [https://www.exodus-strength.com/forum/viewtopic.php?t=2967](https://www.exodus-strength.com/forum/viewtopic.php?t=2967) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: RTS 차트 기반: 컴파운드 1 RPE차당 4~5%, 아이솔레이션·고렙(>8렙) 2~3%. RPE+2 이상이면 즉시 -7~10% 또는 운동 종료

**받는 정보**
- 운동 종류(컴파운드/아이솔레이션)
- 렙수
- RPE 차이

**내놓는 것**: 다음 세트 추천 무게 + 종료 트리거

**예시**: 스쿼트 3렙 RPE8 목표 → 실제 RPE10: -10% 후 백오프 또는 종료. 이두컬 12렙 RPE8 → 9: -2.5%

**[세트 후 학습]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a12_세트_간_무게_보정_rts_룰(
    운동_종류,  # 운동 종류(컴파운드/아이솔레이션)
    렙수,
    rpe_차이,  # RPE 차이
):
    """A12: 세트 간 무게 보정 (RTS 룰). 다음 세트 추천 무게 + 종료 트리거"""
    ...  # 근거: https://www.exodus-strength.com/forum/viewtopic.php?t=2967
```

---

### A13 — 세션 간 RPE drift 보정

- **데이터**: `workout_knowledge_base.csv` 13행 (ID `A13`) → [`rules/A13.yaml`](./rules/A13.yaml)
- **근거**: Tuchscherer "Deloading Effectively" / Helms 자율조절 원칙 — [https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively](https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세션 시작 시
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 같은 무게·렙에서 RPE가 2주 이상 +1점 drift → 회복 부족. 다음 세션 -5% 또는 디로드. RPE -1점 drift → 적응 완료, +2.5~5% 진행

**받는 정보**
- 최근 2~3 세션의 동일 운동 RPE 추이

**내놓는 것**: 다음 세션 무게 자동 조정 또는 디로드 권고

**예시**: 벤치 80kg×5 RPE8→8.5→9 추세: 다음 세션 76kg 또는 디로드. RPE8→7→6.5 추세: 82.5kg

**[세트 후 학습]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def a13_세션_간_rpe_drift_보정(
    최근_2_3_세션의_동일_운동_rpe_추이,  # 최근 2~3 세션의 동일 운동 RPE 추이
):
    """A13: 세션 간 RPE drift 보정. 다음 세션 무게 자동 조정 또는 디로드 권고"""
    ...  # 근거: https://store.reactivetrainingsystems.com/blogs/advanced-concepts/deloading-effectively
```

---

### A14 — 강도 의존성 보정 (>85% 1RM)

- **데이터**: `workout_knowledge_base.csv` 14행 (ID `A14`) → [`rules/A14.yaml`](./rules/A14.yaml)
- **근거**: Tuchscherer RPE 차트 (RM 간격: 1-2RM 4.5% → 9-10RM 2.3%) — [https://www.exodus-strength.com/forum/viewtopic.php?t=2967](https://www.exodus-strength.com/forum/viewtopic.php?t=2967) — ★★☆
- **분류**: RPE 자율조절
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 고강도 영역(<5렙, ≥85% 1RM)에선 1 RPE 오차당 RM 변화가 4.5%로 큼. 보수적으로 -5%(컴파운드)/디폴트 +1단계 더 깎기. 저강도(>10렙)는 2~3%만

**받는 정보**
- 현재 %1RM 추정치
- 렙수

**내놓는 것**: 보정 폭 자동 조정 (5%/3%/2%)

**예시**: 데드 3렙 90% 1RM RPE9 입력(목표8): -5%. 사이드레터럴 15렙 70% RPE9: -2%

**[세트 후 학습]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 세트별 처방

**함수 시그니처(제안)**
```python
def a14_강도_의존성_보정_85_1rm(
    현재_1rm_추정치,  # 현재 %1RM 추정치
    렙수,
):
    """A14: 강도 의존성 보정 (>85% 1RM). 보정 폭 자동 조정 (5%/3%/2%)"""
    ...  # 근거: https://www.exodus-strength.com/forum/viewtopic.php?t=2967
```

---

### 분류: 세트/렙/강도 처방

### C08 — Double Progression

- **데이터**: `workout_knowledge_base.csv` 27행 (ID `C08`) → [`rules/C08.yaml`](./rules/C08.yaml)
- **근거**: Legion / Bret Contreras — [https://legionathletics.com/double-progression/](https://legionathletics.com/double-progression/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 후
- **쓰임새**: 운동 추천, 실시간 코칭

**무슨 룰**: 렙 범위 처방(예: 8~12렙). 모든 세트가 상한 도달 → 무게 +2.5~5% 인상, 렙 하한 리셋

**받는 정보**
- 지난 세션 모든 세트 성공 여부

**내놓는 것**: 다음 세션 무게 자동 인상 또는 유지

**예시**: 세션 끝 → '모두 12렙 성공' → 다음 세션 +2.5kg, 8렙으로 시작

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진
**다른 모듈에도 등장**: 세트별 처방

**함수 시그니처(제안)**
```python
def c08_double_progression(
    지난_세션_모든_세트_성공_여부,  # 지난 세션 모든 세트 성공 여부
):
    """C08: Double Progression. 다음 세션 무게 자동 인상 또는 유지"""
    ...  # 근거: https://legionathletics.com/double-progression/
```

---

### C12 — 마지막 세트만 미달 (Top-set drop-off)

- **데이터**: `workout_knowledge_base.csv` 31행 (ID `C12`) → [`rules/C12.yaml`](./rules/C12.yaml)
- **근거**: Rippetoe & Kilgore, Practical Programming for Strength Training 3rd ed. — [https://startingstrength.com/article/training](https://startingstrength.com/article/training) — ★★☆
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 종료 직후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 첫 1~2세트는 목표 달성, 마지막 세트만 1~2렙 부족이면 무게 유지하고 다음 세션 동일 무게 재시도 (정상적 피로 반응)

**받는 정보**
- 세트별 목표렙 vs 실제렙
- 미달 세트 위치

**내놓는 것**: 다음 세션 무게 동일, 부족분 다음 세션에 회수 시도

**예시**: 벤치 60kg×5,5,4 (목표 5,5,5) → 다음 세션 60kg×5,5,5 도전

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c12_마지막_세트만_미달_top_set_drop_off(
    세트별_목표렙_vs_실제렙,  # 세트별 목표렙 vs 실제렙
    미달_세트_위치,  # 미달 세트 위치
):
    """C12: 마지막 세트만 미달 (Top-set drop-off). 다음 세션 무게 동일, 부족분 다음 세션에 회수 시도"""
    ...  # 근거: https://startingstrength.com/article/training
```

---

### C13 — 모든 세트 동일 미달 (Stall 1회차)

- **데이터**: `workout_knowledge_base.csv` 32행 (ID `C13`) → [`rules/C13.yaml`](./rules/C13.yaml)
- **근거**: Greg Nuckols, Stronger By Science — How to Deal with Failed Reps — [https://www.strongerbyscience.com/reps-sets/](https://www.strongerbyscience.com/reps-sets/) — ★★☆
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 종료 직후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 모든 워킹 세트가 목표렙 미달이면 1주 더 동일 무게 유지(밀어내기). 그래도 미달이면 C13 적용

**받는 정보**
- 세트별 미달 횟수
- 연속 stall 주차

**내놓는 것**: 무게·렙 유지, 1주 재시도. 수면/영양/스트레스 체크 프롬프트

**예시**: 스쿼트 3×5 100kg에서 4,4,3 → 다음 주 100kg 재시도

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c13_모든_세트_동일_미달_stall_1회차(
    세트별_미달_횟수,  # 세트별 미달 횟수
    연속_stall_주차,  # 연속 stall 주차
):
    """C13: 모든 세트 동일 미달 (Stall 1회차). 무게·렙 유지, 1주 재시도. 수면/영양/스트레스 체크 프롬프트"""
    ...  # 근거: https://www.strongerbyscience.com/reps-sets/
```

---

### C14 — 2주(3세션) 연속 미달 → Reset (-10%)

- **데이터**: `workout_knowledge_base.csv` 33행 (ID `C14`) → [`rules/C14.yaml`](./rules/C14.yaml)
- **근거**: Rippetoe, Starting Strength: Basic Barbell Training 3rd ed. — Reset 절차 — [https://startingstrength.com/article/the_first_three_questions](https://startingstrength.com/article/the_first_three_questions) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 진행 정체 감지 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 동일 무게에서 3세션 연속 목표렙 미달 시 작업 무게 -10% 후 점진 재진입 (Starting Strength reset rule)

**받는 정보**
- 연속 stall 세션 수
- 직전 작업 무게

**내놓는 것**: 무게 ×0.9, 4~6주에 걸쳐 직전 PR 회복 후 초과 시도

**예시**: 100kg 3세션 정체 → 90kg 재시작 → 주당 +2.5kg 점진

**[세트 후 학습]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c14_2주_3세션_연속_미달_reset_10(
    연속_stall_세션_수,  # 연속 stall 세션 수
    직전_작업_무게,  # 직전 작업 무게
):
    """C14: 2주(3세션) 연속 미달 → Reset (-10%). 무게 ×0.9, 4~6주에 걸쳐 직전 PR 회복 후 초과 시도"""
    ...  # 근거: https://startingstrength.com/article/the_first_three_questions
```

---

### C15 — Double Progression 미달 처리 보강

- **데이터**: `workout_knowledge_base.csv` 34행 (ID `C15`) → [`rules/C15.yaml`](./rules/C15.yaml)
- **근거**: Helms, Valdez & Morgan, The Muscle and Strength Pyramid: Training 2nd ed. — [https://muscleandstrengthpyramids.com/](https://muscleandstrengthpyramids.com/) — ★★☆
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 직후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 렙 레인지(예: 8~12) 상단 미달 시 무게 유지·렙 누적, 하단(8) 미달 2세션 연속이면 -5~10% 후 재축적

**받는 정보**
- 직전 세션 렙
- 레인지 하한 미달 횟수

**내놓는 것**: 무게 유지/감량 자동 분기, 누적 후 다음 세션 +1렙 시도

**예시**: 8~12 레인지 70kg 7,7 → 다음 세션 65kg 9,9로 재축적

**[세트 후 학습]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def c15_double_progression_미달_처리_보강(
    직전_세션_렙,  # 직전 세션 렙
    레인지_하한_미달_횟수,  # 레인지 하한 미달 횟수
):
    """C15: Double Progression 미달 처리 보강. 무게 유지/감량 자동 분기, 누적 후 다음 세션 +1렙 시도"""
    ...  # 근거: https://muscleandstrengthpyramids.com/
```

---

### 분류: 실시간 코칭

### E04 — 실시간 피드백 효과

- **데이터**: `workout_knowledge_base.csv` 53행 (ID `E04`) → [`rules/E04.yaml`](./rules/E04.yaml)
- **근거**: Weakley 2023 (Sports Med meta) — [https://pubmed.ncbi.nlm.nih.gov/37410360/](https://pubmed.ncbi.nlm.nih.gov/37410360/) — ★★☆
- **분류**: 실시간 코칭
- **시점**: 세트 직후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 렙별 속도 피드백은 동기·집중·움직임 질↑, 인지 노력↓

**받는 정보**
- 세트 데이터

**내놓는 것**: 세트 후 시각적 피드백 표시

**예시**: 세트 후 '이번 세트 평균 속도 0.8m/s' 그래프 표시 → 동기부여

**[세트 후 학습]에서 적용 목표**: 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def e04_실시간_피드백_효과(
    세트_데이터,  # 세트 데이터
):
    """E04: 실시간 피드백 효과. 세트 후 시각적 피드백 표시"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/37410360/
```

---

### 분류: 기타

### I04 — ACWR (급성/만성 부하비)

- **데이터**: `workout_knowledge_base.csv` 82행 (ID `I04`) → [`rules/I04.yaml`](./rules/I04.yaml)
- **근거**: Gabbett 2016 — [https://www.scienceforsport.com/acutechronic-workload-ratio/](https://www.scienceforsport.com/acutechronic-workload-ratio/) — ★★☆
- **분류**: 기타
- **시점**: 주간 단위
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 7일 부하 / 28일 부하. 0.8~1.3 안전, 1.5+ 부상 위험

**받는 정보**
- 최근 7일/28일 볼륨

**내놓는 것**: 위험 구간 진입 시 알림

**예시**: 고강도 사용자 모니터링용 추가 지표

**[세트 후 학습]에서 적용 목표**: 건강증진

**함수 시그니처(제안)**
```python
def i04_acwr_급성_만성_부하비(
    최근_7일_28일_볼륨,  # 최근 7일/28일 볼륨
):
    """I04: ACWR (급성/만성 부하비). 위험 구간 진입 시 알림"""
    ...  # 근거: https://www.scienceforsport.com/acutechronic-workload-ratio/
```

---


## 모듈 5 — 메조사이클 관리

주 단위. 운동량(볼륨)을 늘리거나 줄이고, 회복주(디로드)를 배치한다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | B01, B02, G01, G02, G05, G09, G10 |
| 벌크업 | B01, B02, B03, B04, B05, C06, C11, D01, D02, D03, G01, G02, G03, G05, G07, G10, G11 |
| 스트렝스 | B01, B02, B05, C06, C11, D01, D02, D04, D06, D07, D08, D09, G01, G02, G03, G04, G05, G06, G07, G08, G09, G10, G11, I01 |
| 근육량 증가 | B01, B02, B03, B04, B05, C06, C11, D01, D02, D03, D04, D05, G01, G02, G03, G04, G05, G06, G07, G08, G09, G10, G11 |
| 건강증진 | B01, B02, C06, G01, G02, G05, G09, G10, I01 |

**고유 룰 수: 28**

### 분류: 주간 볼륨 기준

### B01 — MV (유지 볼륨)

- **데이터**: `workout_knowledge_base.csv` 15행 (ID `B01`) → [`rules/B01.yaml`](./rules/B01.yaml)
- **근거**: Israetel / RP Strength — [https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth](https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth) — ★★★
- **분류**: 주간 볼륨 기준
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근육군당 주 6세트 정도가 현재 근육량 유지 최소치

**받는 정보**
- 근육군
- 주차

**내놓는 것**: 유지기/디로드 주차 처방값

**예시**: 디로드 주에 자동 적용, 또는 비활성 사용자 추적

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def b01_mv_유지_볼륨(
    근육군,
    주차,
):
    """B01: MV (유지 볼륨). 유지기/디로드 주차 처방값"""
    ...  # 근거: https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth
```

---

### B02 — MEV (성장 시작 볼륨)

- **데이터**: `workout_knowledge_base.csv` 16행 (ID `B02`) → [`rules/B02.yaml`](./rules/B02.yaml)
- **근거**: Israetel — [https://drmikeisraetel.com/dr-mike-israetel-mv-mev-mav-mrv-explained/](https://drmikeisraetel.com/dr-mike-israetel-mv-mev-mav-mrv-explained/) — ★★★
- **분류**: 주간 볼륨 기준
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 성장 일으키는 최소 볼륨. 가슴 8, 등 10, 다리 6~8세트/주 등 근육군별 다름

**받는 정보**
- 근육군

**내놓는 것**: 메조사이클 1주차 볼륨 시작값

**예시**: 새 메조사이클 시작 시 근육군별 MEV로 자동 설정

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def b02_mev_성장_시작_볼륨(
    근육군,
):
    """B02: MEV (성장 시작 볼륨). 메조사이클 1주차 볼륨 시작값"""
    ...  # 근거: https://drmikeisraetel.com/dr-mike-israetel-mv-mev-mav-mrv-explained/
```

---

### B03 — MAV (최적 적응 볼륨)

- **데이터**: `workout_knowledge_base.csv` 17행 (ID `B03`) → [`rules/B03.yaml`](./rules/B03.yaml)
- **근거**: Israetel / RP — [https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth](https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth) — ★★★
- **분류**: 주간 볼륨 기준
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: MEV~MRV 사이의 "성장 존". 매주 +1~2세트 점진 증가 필요

**받는 정보**
- 현재 주 볼륨
- 진행 주차

**내놓는 것**: 다음 주 볼륨 = 이번 주 + 1~2세트

**예시**: 메조사이클 4~5주 동안 매주 자동으로 세트 추가

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def b03_mav_최적_적응_볼륨(
    현재_주_볼륨,  # 현재 주 볼륨
    진행_주차,  # 진행 주차
):
    """B03: MAV (최적 적응 볼륨). 다음 주 볼륨 = 이번 주 + 1~2세트"""
    ...  # 근거: https://rpstrength.com/blogs/articles/training-volume-landmarks-muscle-growth
```

---

### B04 — MRV (회복 가능 최대 볼륨)

- **데이터**: `workout_knowledge_base.csv` 18행 (ID `B04`) → [`rules/B04.yaml`](./rules/B04.yaml)
- **근거**: Israetel — [https://propanefitness.com/maximum-recoverable-volume/](https://propanefitness.com/maximum-recoverable-volume/) — ★★★
- **분류**: 주간 볼륨 기준
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 근육군당 주 18~25+세트. 초과 시 오버트레이닝 신호 (수면·식욕·관절통·RPE 상승)

**받는 정보**
- 근육군별 누적 주간 볼륨

**내놓는 것**: MRV 도달 + 수행도 하락 시 디로드 자동 권고

**예시**: 앱 알림: '가슴 볼륨이 한계치 도달, 다음 주 디로드 추천'

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def b04_mrv_회복_가능_최대_볼륨(
    근육군별_누적_주간_볼륨,  # 근육군별 누적 주간 볼륨
):
    """B04: MRV (회복 가능 최대 볼륨). MRV 도달 + 수행도 하락 시 디로드 자동 권고"""
    ...  # 근거: https://propanefitness.com/maximum-recoverable-volume/
```

---

### B05 — Volume Dose-Response 메타

- **데이터**: `workout_knowledge_base.csv` 19행 (ID `B05`) → [`rules/B05.yaml`](./rules/B05.yaml)
- **근거**: Schoenfeld / Krieger — [https://www.strongerbyscience.com/volume/](https://www.strongerbyscience.com/volume/) — ★★★
- **분류**: 주간 볼륨 기준
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 주당 10+ 세트가 1세트보다 효과 큼(ES 0.44 vs 0.24). 12~20세트 권장. 20+ 추가효과 미미

**받는 정보**
- 사용자 목표(근비대)

**내놓는 것**: 주당 권장 볼륨 자동 처방 (12~20세트)

**예시**: 근비대 목표 사용자에게 디폴트 주당 12~20세트 처방

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def b05_volume_dose_response_메타(
    사용자_목표,  # 사용자 목표(근비대)
):
    """B05: Volume Dose-Response 메타. 주당 권장 볼륨 자동 처방 (12~20세트)"""
    ...  # 근거: https://www.strongerbyscience.com/volume/
```

---

### 분류: 회복/디로드

### G01 — 디로드 정의·주기

- **데이터**: `workout_knowledge_base.csv` 68행 (ID `G01`) → [`rules/G01.yaml`](./rules/G01.yaml)
- **근거**: Bell et al / Frontiers — [https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2022.1073223/full](https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2022.1073223/full) — ★★★
- **분류**: 회복/디로드
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 훈련 자극 의도적 감소 (5~7일). 평균 4~6주마다 시행

**받는 정보**
- 주차 누적
- 사용자 입력

**내놓는 것**: 4~6주마다 자동 디로드 주차 스케줄

**예시**: 메조사이클 5주차에 자동 디로드 주 삽입

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def g01_디로드_정의_주기(
    주차_누적,  # 주차 누적
    사용자_입력,  # 사용자 입력
):
    """G01: 디로드 정의·주기. 4~6주마다 자동 디로드 주차 스케줄"""
    ...  # 근거: https://www.frontiersin.org/journals/sports-and-active-living/articles/10.3389/fspor.2022.1073223/full
```

---

### G02 — 디로드 트리거 (자동 감지)

- **데이터**: `workout_knowledge_base.csv` 69행 (ID `G02`) → [`rules/G02.yaml`](./rules/G02.yaml)
- **근거**: Israetel / Bell 2024 — [https://shura.shu.ac.uk/35313/3/Bell-APracticalApproach(AM).pdf](https://shura.shu.ac.uk/35313/3/Bell-APracticalApproach(AM).pdf) — ★★★
- **분류**: 회복/디로드
- **시점**: 세션 후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 같은 무게에 RPE +2 상승, 수면·식욕 악화, 관절통 누적, 동기 저하 → 디로드 신호

**받는 정보**
- 최근 3+ 세션 RPE drift
- 수면
- 통증

**내놓는 것**: 디로드 권고 알림

**예시**: 3세션 연속 RPE drift +2 → '이번 주 디로드 권장' 푸시

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def g02_디로드_트리거_자동_감지(
    최근_3_세션_rpe_drift,  # 최근 3+ 세션 RPE drift
    수면,
    통증,
):
    """G02: 디로드 트리거 (자동 감지). 디로드 권고 알림"""
    ...  # 근거: https://shura.shu.ac.uk/35313/3/Bell-APracticalApproach(AM).pdf
```

---

### G05 — 디로드 주 볼륨/강도 정량 처방

- **데이터**: `workout_knowledge_base.csv` 72행 (ID `G05`) → [`rules/G05.yaml`](./rules/G05.yaml)
- **근거**: Helms 3DMJ "How Do We Deload? Pt.1" + Renaissance Periodization — [https://www.3dmusclejourney.com/blog/how-do-we-deload-part-1](https://www.3dmusclejourney.com/blog/how-do-we-deload-part-1) — ★★★
- **분류**: 회복/디로드
- **시점**: 디로드 주 1회
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 직전 마이크로사이클 대비 세트 수 50% 감축, 무게는 그대로(또는 -10%), 빈도는 유지. 기간은 5~7일(1주)

**받는 정보**
- 직전 주 세트 수
- 평균 무게
- 훈련 빈도

**내놓는 것**: 디로드 주 처방: 세트 수 ½, 무게 90~100% 유지, 같은 분할

**예시**: 6주 메조 종료 후: 가슴 16세트→8세트, 벤치 100kg→90~100kg, 주 4회 그대로

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def g05_디로드_주_볼륨_강도_정량_처방(
    직전_주_세트_수,  # 직전 주 세트 수
    평균_무게,  # 평균 무게
    훈련_빈도,  # 훈련 빈도
):
    """G05: 디로드 주 볼륨/강도 정량 처방. 디로드 주 처방: 세트 수 ½, 무게 90~100% 유지, 같은 분할"""
    ...  # 근거: https://www.3dmusclejourney.com/blog/how-do-we-deload-part-1
```

---

### G09 — 활성 디로드 vs 완전 휴식 선택

- **데이터**: `workout_knowledge_base.csv` 76행 (ID `G09`) → [`rules/G09.yaml`](./rules/G09.yaml)
- **근거**: Coleman et al. 2024 PeerJ (1주 완전 휴식 RCT) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC10809978/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10809978/) — ★★★
- **분류**: 회복/디로드
- **시점**: 디로드 주 결정 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 기본은 활성 디로드(G05 처방)로 strength 손실 방지. 완전 휴식 1주는 하체 strength 소폭 감소 위험, 부상·번아웃·수면<5h 지속 시에만 사용

**받는 정보**
- 부상 여부
- 번아웃 척도
- 수면 평균

**내놓는 것**: "활성"(권장) 또는 "패시브 1주" 선택 후 처방 분기

**예시**: 7개월 연속 훈련 + 동기 1/5 → 1주 완전 휴식 허용. 그 외엔 활성 권장

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def g09_활성_디로드_vs_완전_휴식_선택(
    부상_여부,  # 부상 여부
    번아웃_척도,  # 번아웃 척도
    수면_평균,  # 수면 평균
):
    """G09: 활성 디로드 vs 완전 휴식 선택. "활성"(권장) 또는 "패시브 1주" 선택 후 처방 분기"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC10809978/
```

---

### G10 — 한국 사용자 디로드 주기 기본값

- **데이터**: `workout_knowledge_base.csv` 77행 (ID `G10`) → [`rules/G10.yaml`](./rules/G10.yaml)
- **근거**: Renaissance Periodization 메조 가이드 — [https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/](https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/) — ★★☆
- **분류**: 회복/디로드
- **시점**: 메조 설계 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 절대초보·초보: 사용자 신호 기반 자동(G07). 중·고급: 4~6주마다 강제 디로드(직장인 누적 피로·회식·출장 변수 고려해 6주 상한)

**받는 정보**
- 사용자 레벨
- 메조 시작 주차

**내놓는 것**: 5주차 종료 후 "다음 주 디로드 추천" 푸시 + G05 처방 미리 채움

**예시**: 직장인 중급자 메조 시작 → 5주 훈련 + 1주 디로드 = 6주 메조 사이클 자동 설정

**[메조사이클 관리]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def g10_한국_사용자_디로드_주기_기본값(
    사용자_레벨,  # 사용자 레벨
    메조_시작_주차,  # 메조 시작 주차
):
    """G10: 한국 사용자 디로드 주기 기본값. 5주차 종료 후 "다음 주 디로드 추천" 푸시 + G05 처방 미리 채움"""
    ...  # 근거: https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/
```

---

### G03 — 디로드 처방 방법

- **데이터**: `workout_knowledge_base.csv` 70행 (ID `G03`) → [`rules/G03.yaml`](./rules/G03.yaml)
- **근거**: Bell 2024 / RP — [https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/) — ★★★
- **분류**: 회복/디로드
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 볼륨 -50%, 강도 -10~20%, 빈도 유지

**받는 정보**
- 현재 주간 처방

**내놓는 것**: 디로드 주차 처방값 자동 생성

**예시**: 디로드 주: 세트 절반·무게 85% 자동 적용

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def g03_디로드_처방_방법(
    현재_주간_처방,  # 현재 주간 처방
):
    """G03: 디로드 처방 방법. 디로드 주차 처방값 자동 생성"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/
```

---

### G07 — 디로드 트리거 신호 (다지표 자동)

- **데이터**: `workout_knowledge_base.csv` 74행 (ID `G07`) → [`rules/G07.yaml`](./rules/G07.yaml)
- **근거**: Bell et al. 2023 Delphi Consensus (Sports Medicine - Open) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/) — ★★★
- **분류**: 회복/디로드
- **시점**: 매주말 자동 평가
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 다음 중 ≥2개 충족 시 익주 디로드 자동 권고: ①RPE drift +1.5 이상 ②수면 <6h 주 4일+ ③관절통 NPRS ≥4 ④동기 ≤2/5 ⑤최근 PR 후 14일 경과

**받는 정보**
- 주간 RPE 추이
- 수면
- 통증 NPRS
- 동기 점수

**내놓는 것**: "디로드 권고" 알림 + 다음 주 처방 자동 G05/G06으로 전환

**예시**: 4주차 종료 시 RPE +1.7 & 수면 5.2h 평균 → 5주차 자동 디로드 처방

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def g07_디로드_트리거_신호_다지표_자동(
    주간_rpe_추이,  # 주간 RPE 추이
    수면,
    통증_nprs,  # 통증 NPRS
    동기_점수,  # 동기 점수
):
    """G07: 디로드 트리거 신호 (다지표 자동). "디로드 권고" 알림 + 다음 주 처방 자동 G05/G06으로 전환"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC10511399/
```

---

### G11 — 미달 누적 디로드 트리거

- **데이터**: `workout_knowledge_base.csv` 78행 (ID `G11`) → [`rules/G11.yaml`](./rules/G11.yaml)
- **근거**: Israetel et al., Scientific Principles of Hypertrophy Training — Fatigue Management — [https://rpstrength.com/blogs/articles/in-defense-of-set-increases-within-the-hypertrophy-mesocycle](https://rpstrength.com/blogs/articles/in-defense-of-set-increases-within-the-hypertrophy-mesocycle) — ★★☆
- **분류**: 회복/디로드
- **시점**: 주간 검토 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 다관절 메인리프트 2개 이상이 같은 주에 stall + RPE 9~10 누적이면 1주 디로드 (볼륨 -50%, 강도 -10%)

**받는 정보**
- 주간 stall 리프트 수
- 평균 RPE

**내놓는 것**: 다음 주 디로드 프로그램 자동 처방 후 재진입

**예시**: 스쿼트·벤치 동시 stall + 평균 RPE 9.5 → 디로드 1주

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def g11_미달_누적_디로드_트리거(
    주간_stall_리프트_수,  # 주간 stall 리프트 수
    평균_rpe,  # 평균 RPE
):
    """G11: 미달 누적 디로드 트리거. 다음 주 디로드 프로그램 자동 처방 후 재진입"""
    ...  # 근거: https://rpstrength.com/blogs/articles/in-defense-of-set-increases-within-the-hypertrophy-mesocycle
```

---

### G04 — 주간 부하 +10% 룰 (부상 예방)

- **데이터**: `workout_knowledge_base.csv` 71행 (ID `G04`) → [`rules/G04.yaml`](./rules/G04.yaml)
- **근거**: Gabbett ACWR — [https://gymaware.com/progressive-overload-the-ultimate-guide/](https://gymaware.com/progressive-overload-the-ultimate-guide/) — ★★★
- **분류**: 회복/디로드
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 주간 총 부하 증가는 10% 이내. 초과 시 부상 위험. ACWR 0.8~1.3 안전 구간

**받는 정보**
- 이번주 vs 지난주 총볼륨

**내놓는 것**: 초과 시 경고/상한 적용

**예시**: 주간 볼륨 +15% 이상 증가 시 '부상 위험' 경고

**[메조사이클 관리]에서 적용 목표**: 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def g04_주간_부하_10_룰_부상_예방(
    이번주_vs_지난주_총볼륨,  # 이번주 vs 지난주 총볼륨
):
    """G04: 주간 부하 +10% 룰 (부상 예방). 초과 시 경고/상한 적용"""
    ...  # 근거: https://gymaware.com/progressive-overload-the-ultimate-guide/
```

---

### G06 — 고피로 시 강도까지 동시 감축

- **데이터**: `workout_knowledge_base.csv` 73행 (ID `G06`) → [`rules/G06.yaml`](./rules/G06.yaml)
- **근거**: Israetel / Renaissance Periodization "Advanced Deload Strategies" — [https://renaissanceperiodization.com/dr-mike-israetel-compilation/](https://renaissanceperiodization.com/dr-mike-israetel-compilation/) — ★★☆
- **분류**: 회복/디로드
- **시점**: 디로드 주 (피로 高)
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 피로가 매우 높으면(관절통·수면 저하 동반) 세트도 ½ + 무게도 50% 동시 감축. 일반 피로면 볼륨만 ½

**받는 정보**
- 누적 피로 신호(관절통·수면·동기 점수)

**내놓는 것**: 강도 감축 여부 결정: 일반=무게 유지 / 고피로=무게 50%

**예시**: 디로드 직전 4주 RPE 평균 9 초과 + 수면 6h 미만 → 무게 50%·세트 ½

**[메조사이클 관리]에서 적용 목표**: 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def g06_고피로_시_강도까지_동시_감축(
    누적_피로_신호,  # 누적 피로 신호(관절통·수면·동기 점수)
):
    """G06: 고피로 시 강도까지 동시 감축. 강도 감축 여부 결정: 일반=무게 유지 / 고피로=무게 50%"""
    ...  # 근거: https://renaissanceperiodization.com/dr-mike-israetel-compilation/
```

---

### G08 — MRV 도달 시 강제 디로드

- **데이터**: `workout_knowledge_base.csv` 75행 (ID `G08`) → [`rules/G08.yaml`](./rules/G08.yaml)
- **근거**: Israetel — Volume Landmarks (Renaissance Periodization) — [https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/](https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/) — ★★☆
- **분류**: 회복/디로드
- **시점**: 메조 4~6주차
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 부위별 주간 세트가 MRV(보통 18~25세트) 도달하고 RPE가 같은 무게에서 +1 이상 상승하면 다음 주 강제 디로드. 메조 최대 6주 초과 금지

**받는 정보**
- 부위별 누적 세트
- RPE drift
- 주차 카운터

**내놓는 것**: 다음 주 G05 처방 강제 + 다음 메조는 MEV(10~12세트)에서 재시작

**예시**: 등 24세트/주 6주차 RPE +1.2 → 7주차 디로드, 8주차 새 메조는 12세트로 시작

**[메조사이클 관리]에서 적용 목표**: 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def g08_mrv_도달_시_강제_디로드(
    부위별_누적_세트,  # 부위별 누적 세트
    rpe_drift,  # RPE drift
    주차_카운터,  # 주차 카운터
):
    """G08: MRV 도달 시 강제 디로드. 다음 주 G05 처방 강제 + 다음 메조는 MEV(10~12세트)에서 재시작"""
    ...  # 근거: https://renaissanceperiodization.com/training-volume-landmarks-muscle-growth/
```

---

### 분류: 세트/렙/강도 처방

### C06 — 훈련 빈도

- **데이터**: `workout_knowledge_base.csv` 25행 (ID `C06`) → [`rules/C06.yaml`](./rules/C06.yaml)
- **근거**: Schoenfeld 2016/2018 — [https://pubmed.ncbi.nlm.nih.gov/27102172/](https://pubmed.ncbi.nlm.nih.gov/27102172/) — ★★★
- **분류**: 세트/렙/강도 처방
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 볼륨 동일 시 빈도는 비대에 무의미. 단 주 2회 이상 분할이 볼륨 분산에 유리

**받는 정보**
- 주간 볼륨
- 분할 형태

**내놓는 것**: 근육군당 최소 주 2회 분할 권장

**예시**: 분할 추천 알고리즘에서 근육군이 주 2회 이상 자극되도록 자동 배치

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def c06_훈련_빈도(
    주간_볼륨,  # 주간 볼륨
    분할_형태,  # 분할 형태
):
    """C06: 훈련 빈도. 근육군당 최소 주 2회 분할 권장"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/27102172/
```

---

### C11 — 세션 길이 가이드

- **데이터**: `workout_knowledge_base.csv` 30행 (ID `C11`) → [`rules/C11.yaml`](./rules/C11.yaml)
- **근거**: NSCA Essentials — [https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/](https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/) — ★★☆
- **분류**: 세트/렙/강도 처방
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 효율 세션 45~75분. 분할로 길이 조절. 90분+ 코르티솔 주장은 1차 출처 약함

**받는 정보**
- 가용 시간
- 분할

**내놓는 것**: 세션 운동 수/세트 수 자동 조정

**예시**: '40분만 가능' 입력 → 운동 4~5개로 압축한 세션 자동 빌드

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가
**다른 모듈에도 등장**: 세트별 처방

**함수 시그니처(제안)**
```python
def c11_세션_길이_가이드(
    가용_시간,  # 가용 시간
    분할,
):
    """C11: 세션 길이 가이드. 세션 운동 수/세트 수 자동 조정"""
    ...  # 근거: https://www.nsca.com/education/articles/nsca-coach/using-intensity-based-on-sets-and-repetitions-over-50-years-of-experience-a-brief-overview-of-load-setting-and-programming-strategy/
```

---

### 분류: 주기화 모델

### D01 — Linear Periodization

- **데이터**: `workout_knowledge_base.csv` 35행 (ID `D01`) → [`rules/D01.yaml`](./rules/D01.yaml)
- **근거**: Bompa / NSCA — [https://www.strongerbyscience.com/periodization-data/](https://www.strongerbyscience.com/periodization-data/) — ★★★
- **분류**: 주기화 모델
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 1~4주 비대(8~12렙) → 5~8주 근력(3~6렙) → 9~12주 파워. 초보~중급 적합

**받는 정보**
- 사용자 레벨
- 진행 주차

**내놓는 것**: 주차별 변수 자동 변경

**예시**: 초보 사용자 12주 프로그램 자동 생성

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d01_linear_periodization(
    사용자_레벨,  # 사용자 레벨
    진행_주차,  # 진행 주차
):
    """D01: Linear Periodization. 주차별 변수 자동 변경"""
    ...  # 근거: https://www.strongerbyscience.com/periodization-data/
```

---

### D02 — Daily Undulating (DUP)

- **데이터**: `workout_knowledge_base.csv` 36행 (ID `D02`) → [`rules/D02.yaml`](./rules/D02.yaml)
- **근거**: Painter 2012 / Colquhoun 2017 — [https://pubmed.ncbi.nlm.nih.gov/22173008/](https://pubmed.ncbi.nlm.nih.gov/22173008/) — ★★★
- **분류**: 주기화 모델
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 같은 주 내 일별 비대-근력-파워 변경. 9~12주에 LP보다 약간 우월. 중급+ 권장

**받는 정보**
- 사용자 레벨(중·고급)

**내놓는 것**: 요일별 변수 다른 처방

**예시**: 월=비대(10렙), 수=근력(5렙), 금=파워(3렙) 자동 분배

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 스트렝스 · 근육량 증가
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d02_daily_undulating_dup(
    사용자_레벨,  # 사용자 레벨(중·고급)
):
    """D02: Daily Undulating (DUP). 요일별 변수 다른 처방"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/22173008/
```

---

### D03 — Block Periodization

- **데이터**: `workout_knowledge_base.csv` 37행 (ID `D03`) → [`rules/D03.yaml`](./rules/D03.yaml)
- **근거**: Issurin / Verkhoshansky — [https://www.strongerbyscience.com/periodization-data/](https://www.strongerbyscience.com/periodization-data/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 주간 단위
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 3~4주 단위 블록(축적-변환-실현). 한 적응 자극 집중. 고급 선수용

**받는 정보**
- 사용자 레벨(고급)

**내놓는 것**: 블록당 1개 적응 우선

**예시**: 고급 모드 옵션, 대회 준비 사용자에게 적합

**[메조사이클 관리]에서 적용 목표**: 벌크업 · 근육량 증가
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d03_block_periodization(
    사용자_레벨,  # 사용자 레벨(고급)
):
    """D03: Block Periodization. 블록당 1개 적응 우선"""
    ...  # 근거: https://www.strongerbyscience.com/periodization-data/
```

---

### D04 — Flexible DUP

- **데이터**: `workout_knowledge_base.csv` 38행 (ID `D04`) → [`rules/D04.yaml`](./rules/D04.yaml)
- **근거**: McNamara & Stearne 2010 — [https://pubmed.ncbi.nlm.nih.gov/20042923/](https://pubmed.ncbi.nlm.nih.gov/20042923/) — ★★★
- **분류**: 주기화 모델
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 고정 순서 대신 사용자가 그날 컨디션 선택. 전통 DUP와 동등 효과

**받는 정보**
- 당일 사용자 컨디션 입력

**내놓는 것**: 오늘 비대/근력/파워 중 추천

**예시**: 앱 시작 시 '오늘 어떤 느낌?' → 추천 세션 타입

**[메조사이클 관리]에서 적용 목표**: 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def d04_flexible_dup(
    당일_사용자_컨디션_입력,  # 당일 사용자 컨디션 입력
):
    """D04: Flexible DUP. 오늘 비대/근력/파워 중 추천"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/20042923/
```

---

### D06 — Starting Strength (5x5/5x3)

- **데이터**: `workout_knowledge_base.csv` 40행 (ID `D06`) → [`rules/D06.yaml`](./rules/D06.yaml)
- **근거**: Mark Rippetoe — [https://startingstrength.com/get-started/programs](https://startingstrength.com/get-started/programs) — ★★★
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초보용 LP. 스쿼트/벤치/오버헤드/데드 5렙×3세트, 매 세션 +2.5~5kg 인상. 6~12개월 적합

**받는 정보**
- 사용자 레벨(초보)
- 1RM

**내놓는 것**: 프로그램 처방 (월수금 A/B 교대)

**예시**: 6개월 미만 사용자 디폴트 추천

**[메조사이클 관리]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d06_starting_strength_5x5_5x3(
    사용자_레벨,  # 사용자 레벨(초보)
    _1rm,  # 1RM
):
    """D06: Starting Strength (5x5/5x3). 프로그램 처방 (월수금 A/B 교대)"""
    ...  # 근거: https://startingstrength.com/get-started/programs
```

---

### D07 — 5/3/1 Wendler

- **데이터**: `workout_knowledge_base.csv` 41행 (ID `D07`) → [`rules/D07.yaml`](./rules/D07.yaml)
- **근거**: Jim Wendler — [https://thefitness.wiki/routines/5-3-1-for-beginners/](https://thefitness.wiki/routines/5-3-1-for-beginners/) — ★★★
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 메인 4주 사이클 (5/3/1+/디로드). TM(트레이닝맥스)=1RM의 90%로 시작, 사이클당 +2.5~5kg

**받는 정보**
- 사용자 레벨(중급)
- 1RM

**내놓는 것**: 4주 처방 자동 생성

**예시**: SS 졸업한 중급자 디폴트 추천

**[메조사이클 관리]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d07_5_3_1_wendler(
    사용자_레벨,  # 사용자 레벨(중급)
    _1rm,  # 1RM
):
    """D07: 5/3/1 Wendler. 4주 처방 자동 생성"""
    ...  # 근거: https://thefitness.wiki/routines/5-3-1-for-beginners/
```

---

### D08 — GZCLP

- **데이터**: `workout_knowledge_base.csv` 42행 (ID `D08`) → [`rules/D08.yaml`](./rules/D08.yaml)
- **근거**: Cody LeFever / r/Fitness wiki — [https://thefitness.wiki/routines/gzclp/](https://thefitness.wiki/routines/gzclp/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초·중급 LP. T1(메인 5+렙)→T2(보조 10+렙)→T3(아이솔 15+렙) 3-tier 구조

**받는 정보**
- 사용자 레벨
- 1RM

**내놓는 것**: 프로그램 처방

**예시**: SS 대안. 헬스장 초보~중급 사용자

**[메조사이클 관리]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d08_gzclp(
    사용자_레벨,  # 사용자 레벨
    _1rm,  # 1RM
):
    """D08: GZCLP. 프로그램 처방"""
    ...  # 근거: https://thefitness.wiki/routines/gzclp/
```

---

### D09 — nSuns LP

- **데이터**: `workout_knowledge_base.csv` 43행 (ID `D09`) → [`rules/D09.yaml`](./rules/D09.yaml)
- **근거**: nSuns / r/Fitness wiki — [https://thefitness.wiki/routines/nsuns-lp/](https://thefitness.wiki/routines/nsuns-lp/) — ★★☆
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: Wendler 변형. 주 6일, 메인+보조 모두 5/3/1 패턴. 빠른 무게 진행 (정체기 돌파용)

**받는 정보**
- 사용자 레벨(중급+)

**내놓는 것**: 프로그램 처방

**예시**: 5/3/1 정체기 사용자 옵션

**[메조사이클 관리]에서 적용 목표**: 스트렝스
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d09_nsuns_lp(
    사용자_레벨,  # 사용자 레벨(중급+)
):
    """D09: nSuns LP. 프로그램 처방"""
    ...  # 근거: https://thefitness.wiki/routines/nsuns-lp/
```

---

### D05 — 분할 루틴 비교

- **데이터**: `workout_knowledge_base.csv` 39행 (ID `D05`) → [`rules/D05.yaml`](./rules/D05.yaml)
- **근거**: Schoenfeld 2016 / Israetel — [https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter](https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter) — ★★★
- **분류**: 주기화 모델
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 풀바디(주2~3) = 초보, 상하분할(주4) = 중급, PPL(주5~6) = 고급. 빈도×볼륨 동일하면 효과 동등

**받는 정보**
- 가용 일수
- 사용자 레벨

**내놓는 것**: 권장 분할 형태 자동 매핑

**예시**: 주 3회 가용 → 풀바디, 주 5회 → PPL 추천

**[메조사이클 관리]에서 적용 목표**: 근육량 증가
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def d05_분할_루틴_비교(
    가용_일수,  # 가용 일수
    사용자_레벨,  # 사용자 레벨
):
    """D05: 분할 루틴 비교. 권장 분할 형태 자동 매핑"""
    ...  # 근거: https://rpstrength.com/blogs/articles/your-training-split-doesn-t-matter
```

---

### 분류: 기타

### I01 — 초보자 Linear Progression

- **데이터**: `workout_knowledge_base.csv` 79행 (ID `I01`) → [`rules/I01.yaml`](./rules/I01.yaml)
- **근거**: Mark Rippetoe (Starting Strength) — [https://startingstrength.com/get-started/programs](https://startingstrength.com/get-started/programs) — ★★★
- **분류**: 기타
- **시점**: 세션 후
- **쓰임새**: 운동 추천, 실시간 코칭

**무슨 룰**: 초보(<6개월)는 매 세션 +2.5~5lb 가능. 자율조절 불필요

**받는 정보**
- 사용자 레벨

**내놓는 것**: 초보면 단순 LP 룰 사용

**예시**: 초보 모드: 자율조절 끄고 매 세션 자동 무게 인상

**[메조사이클 관리]에서 적용 목표**: 스트렝스 · 건강증진

**함수 시그니처(제안)**
```python
def i01_초보자_linear_progression(
    사용자_레벨,  # 사용자 레벨
):
    """I01: 초보자 Linear Progression. 초보면 단순 LP 룰 사용"""
    ...  # 근거: https://startingstrength.com/get-started/programs
```

---


## 모듈 6 — 영양·회복

일 단위. 칼로리·단백질·수분·수면·보충제를 처방한다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | K01, K02, K03, K04, K05, K06, K07, K08, K09, K10, K12, K13, K14, K15, K16, K17, K18, K19, K20, K21, K22, K23, O01, O02, O03 |
| 벌크업 | K01, K02, K03, K04, K05, K06, K07, K08, K09, K10, K11, K12, K13, K14, K15, K16, K17, K18, O01 |
| 스트렝스 | K01, K02, K05, K06, K07, K09, K10 |
| 근육량 증가 | K01, K02, K03, K04, K05, K06, K07, K08, K09, K10, K11, K12, K13, K14, K15, K16, K17, K18, O01 |
| 건강증진 | K01, K02, K03, K04, K05, K06, K07, K08, O01, O02, O03 |

**고유 룰 수: 26**

### 분류: 영양

### K01 — 단백질 섭취량

- **데이터**: `workout_knowledge_base.csv` 93행 (ID `K01`) → [`rules/K01.yaml`](./rules/K01.yaml)
- **근거**: Morton 2018 / Helms 2014 — [https://pubmed.ncbi.nlm.nih.gov/28698222/](https://pubmed.ncbi.nlm.nih.gov/28698222/) — ★★★
- **분류**: 영양
- **시점**: 일일
- **쓰임새**: 지식베이스

**무슨 룰**: 근비대/근력 시 체중당 1.6~2.2g/일. 컷 시 2.3~3.1g (제지방 기준). 4~6시간 간격 분배

**받는 정보**
- 체중
- 목표(벌크/컷/유지)

**내놓는 것**: 일일 단백질 g 알림

**예시**: 체중 70kg 벌크 → 112~154g/일 알림

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k01_단백질_섭취량(
    체중,
    목표,  # 목표(벌크/컷/유지)
):
    """K01: 단백질 섭취량. 일일 단백질 g 알림"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/28698222/
```

---

### K02 — 칼로리 가이드

- **데이터**: `workout_knowledge_base.csv` 94행 (ID `K02`) → [`rules/K02.yaml`](./rules/K02.yaml)
- **근거**: ISSN / Helms — [https://jissn.biomedcentral.com/articles/10.1186/1550-2783-11-20](https://jissn.biomedcentral.com/articles/10.1186/1550-2783-11-20) — ★★★
- **분류**: 영양
- **시점**: 일일
- **쓰임새**: 지식베이스

**무슨 룰**: 벌크 +200~500kcal, 컷 -300~500kcal, 유지=TDEE. 주당 체중 ±0.5% 목표

**받는 정보**
- 체중
- 활동량
- 목표

**내놓는 것**: 일일 칼로리 처방

**예시**: TDEE 계산 → 목표별 자동 처방

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k02_칼로리_가이드(
    체중,
    활동량,
    목표,
):
    """K02: 칼로리 가이드. 일일 칼로리 처방"""
    ...  # 근거: https://jissn.biomedcentral.com/articles/10.1186/1550-2783-11-20
```

---

### K03 — 탄수화물 타이밍

- **데이터**: `workout_knowledge_base.csv` 95행 (ID `K03`) → [`rules/K03.yaml`](./rules/K03.yaml)
- **근거**: Kerksick ISSN 2017 — [https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0189-4](https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0189-4) — ★★★
- **분류**: 영양
- **시점**: 세션 전후
- **쓰임새**: 지식베이스

**무슨 룰**: 총량이 타이밍보다 우선. 단 세션 1~3h 전 1~3g/kg 권장, 후 글리코겐 회복은 1~1.2g/kg/h

**받는 정보**
- 세션 시각
- 체중

**내놓는 것**: 식사 타이밍 권고

**예시**: '운동 2시간 전 식사' 알림

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k03_탄수화물_타이밍(
    세션_시각,  # 세션 시각
    체중,
):
    """K03: 탄수화물 타이밍. 식사 타이밍 권고"""
    ...  # 근거: https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0189-4
```

---

### K04 — 수분 가이드

- **데이터**: `workout_knowledge_base.csv` 96행 (ID `K04`) → [`rules/K04.yaml`](./rules/K04.yaml)
- **근거**: ACSM Position Stand — [https://www.acsm.org/docs/default-source/files-for-resource-library/exercise-fluid-replacement.pdf](https://www.acsm.org/docs/default-source/files-for-resource-library/exercise-fluid-replacement.pdf) — ★★★
- **분류**: 영양
- **시점**: 세션 전중후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 기본 30~35ml/kg + 운동 시간당 +500~1000ml. 2% 탈수에서 수행 저하

**받는 정보**
- 체중
- 세션 시간

**내놓는 것**: 수분 섭취 알림

**예시**: 세션 중 15분마다 수분 알림

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k04_수분_가이드(
    체중,
    세션_시간,  # 세션 시간
):
    """K04: 수분 가이드. 수분 섭취 알림"""
    ...  # 근거: https://www.acsm.org/docs/default-source/files-for-resource-library/exercise-fluid-replacement.pdf
```

---

### K12 — 한식 주식·곡류 단백질 환산

- **데이터**: `workout_knowledge_base.csv` 104행 (ID `K12`) → [`rules/K12.yaml`](./rules/K12.yaml)
- **근거**: 농촌진흥청 국가표준식품성분DB 10.3 — [https://koreanfood.rda.go.kr/kfi/fct/fctIntro/list?menuId=PS03562](https://koreanfood.rda.go.kr/kfi/fct/fctIntro/list?menuId=PS03562) — ★★★
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 흰밥 1공기(210g) 약 6g | 잡곡밥 1공기(210g) 7~8g | 현미밥 1공기(210g) 6~7g | 흰죽 1공기(250g) 약 4g | 라면 1봉(120g) 약 10g | 칼국수 1그릇(700g) 약 18g | 우동 1그릇(700g) 약 14g | 짜장면 1그릇(800g) 약 27g | 짬뽕 1그릇(800g) 약 29g

**받는 정보**
- 섭취 식품·양 (한식 단위)

**내놓는 것**: 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력

**예시**: 사용자 '오늘 점심 잡곡밥 한 공기 먹었어' → 챗봇 '단백질 약 7g 적립. 오늘 목표 112g 중 6%.'

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k12_한식_주식_곡류_단백질_환산(
    섭취_식품_양,  # 섭취 식품·양 (한식 단위)
):
    """K12: 한식 주식·곡류 단백질 환산. 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력"""
    ...  # 근거: https://koreanfood.rda.go.kr/kfi/fct/fctIntro/list?menuId=PS03562
```

---

### K13 — 한식 단백질 반찬 환산

- **데이터**: `workout_knowledge_base.csv` 105행 (ID `K13`) → [`rules/K13.yaml`](./rules/K13.yaml)
- **근거**: 농촌진흥청 국가표준식품성분DB 10.3 / 식약처 식품영양성분DB — [https://various.foodsafetykorea.go.kr/nutrient/general/food/firstList.do](https://various.foodsafetykorea.go.kr/nutrient/general/food/firstList.do) — ★★★
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 닭가슴살(생) 100g 23g | 소고기 등심 100g 16g | 소고기 사태 100g 22g | 돼지고기 목심 100g 17g | 돼지고기 안심 100g 21g | 삼겹살 100g 17g | 계란 1개(50g) 6g | 삶은계란 1개 6g | 두부 100g 8~10g | 청국장 100g 19g | 낫토 100g 19g | 콩(대두) 100g 36g

**받는 정보**
- 섭취 식품·양 (한식 단위)

**내놓는 것**: 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력

**예시**: 사용자 '닭가슴살 200g 먹었음' → 챗봇 '단백질 약 46g. 70kg 사용자 목표(112g)의 41% 달성.'

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k13_한식_단백질_반찬_환산(
    섭취_식품_양,  # 섭취 식품·양 (한식 단위)
):
    """K13: 한식 단백질 반찬 환산. 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력"""
    ...  # 근거: https://various.foodsafetykorea.go.kr/nutrient/general/food/firstList.do
```

---

### K14 — 한식 국·찌개 단백질 환산

- **데이터**: `workout_knowledge_base.csv` 106행 (ID `K14`) → [`rules/K14.yaml`](./rules/K14.yaml)
- **근거**: 공공데이터포털 전국통합식품영양성분(음식)표준데이터 / 식약처 식품안전나라 — [https://www.data.go.kr/data/15100070/standard.do](https://www.data.go.kr/data/15100070/standard.do) — ★★☆
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 삼계탕 1인분(900g 통째) 약 96g | 삼계탕 살코기만(240g) 약 36g | 갈비탕 1인분(400g 국물 포함) 약 14g | 설렁탕 1인분(600g) 약 18~20g [확인 필요] | 김치찌개(돼지고기) 1인분(200g) 약 8.5g | 된장찌개 1인분(250g) 약 8~10g [확인 필요] | 순두부찌개 1인분(300g) 약 12g [확인 필요]

**받는 정보**
- 섭취 식품·양 (한식 단위)

**내놓는 것**: 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력

**예시**: 사용자 '점심 갈비탕 먹음' → 챗봇 '단백질 약 14g. 국물보다 고기 양이 단백질 좌우. 추가 단백질 반찬 권장.'

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k14_한식_국_찌개_단백질_환산(
    섭취_식품_양,  # 섭취 식품·양 (한식 단위)
):
    """K14: 한식 국·찌개 단백질 환산. 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력"""
    ...  # 근거: https://www.data.go.kr/data/15100070/standard.do
```

---

### K15 — 분식·외식 단백질 환산

- **데이터**: `workout_knowledge_base.csv` 107행 (ID `K15`) → [`rules/K15.yaml`](./rules/K15.yaml)
- **근거**: 공공데이터포털 전국통합식품영양성분(음식)표준데이터 / 식약처 식품안전나라 — [https://www.data.go.kr/data/15100070/standard.do](https://www.data.go.kr/data/15100070/standard.do) — ★★☆
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 비빔밥 1인분(450g) 약 18~20g | 김밥 1줄(230g) 약 10~14g (속재료별 차이) | 떡볶이 1인분(200g) 약 7g | 짜장면 1그릇 약 27g | 짬뽕 1그릇 약 29g | 김치볶음밥 1인분(300g) 약 12g [확인 필요] | 제육볶음 1인분(250g) 약 30g | 후라이드치킨 1조각(100g 가식부) 약 22g [확인 필요] | 양념치킨 1조각(100g) 약 18g [확인 필요] | 국밥류 1인분 약 18~25g | 분식김밥(참치/불고기) 1줄 11~14g

**받는 정보**
- 섭취 식품·양 (한식 단위)

**내놓는 것**: 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력

**예시**: 사용자 '비빔밥 한 그릇' → 챗봇 '단백질 약 19g. 계란/소고기 토핑 추가 시 +6~10g.'

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k15_분식_외식_단백질_환산(
    섭취_식품_양,  # 섭취 식품·양 (한식 단위)
):
    """K15: 분식·외식 단백질 환산. 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력"""
    ...  # 근거: https://www.data.go.kr/data/15100070/standard.do
```

---

### K16 — 편의점·간편식 단백질 환산

- **데이터**: `workout_knowledge_base.csv` 108행 (ID `K16`) → [`rules/K16.yaml`](./rules/K16.yaml)
- **근거**: 편의점 3사 영양정보 자율공시 (CU/GS25/세븐일레븐) / 매일유업 셀렉스 공식 공시 — [https://www.maeil.com/brand/view_brand1.jsp?dpid=A0000467](https://www.maeil.com/brand/view_brand1.jsp?dpid=A0000467) — ★☆☆
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 편의점 도시락 1개 평균 18~25g (브랜드별 라벨 확인 필수) | 일반 삼각김밥 1개 5~7g | GS25 프로틴 삼각김밥 약 10g | 컵밥 1개 약 15~22g [확인 필요] | 김밥(편의점) 1줄 10~14g | 컵라면 1개(70~90g) 약 7~9g | 셀렉스 프로틴음료 125ml 8g | 마이밀/하이뮨 등 일반 프로틴음료 250~300ml 약 18~25g (제품별 라벨 확인)

**받는 정보**
- 섭취 식품·양 (한식 단위)

**내놓는 것**: 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력

**예시**: 사용자 '편의점 도시락+프로틴음료' → 챗봇 '평균 약 25g+15g=40g. 70kg 목표 112g의 36%.'

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k16_편의점_간편식_단백질_환산(
    섭취_식품_양,  # 섭취 식품·양 (한식 단위)
):
    """K16: 편의점·간편식 단백질 환산. 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력"""
    ...  # 근거: https://www.maeil.com/brand/view_brand1.jsp?dpid=A0000467
```

---

### K17 — 한국 단백질 보충 식품 환산

- **데이터**: `workout_knowledge_base.csv` 109행 (ID `K17`) → [`rules/K17.yaml`](./rules/K17.yaml)
- **근거**: 농촌진흥청 국가표준식품성분DB 10.3 / 매일유업 셀렉스 — [https://koreanfood.rda.go.kr/kfi/fct/fctIntro/list?menuId=PS03562](https://koreanfood.rda.go.kr/kfi/fct/fctIntro/list?menuId=PS03562) — ★★★
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 우유 200ml 약 6~7g | 두유 200ml 약 6~7g | 검은콩두유 190ml 4~9g (제품별) | 그릭요거트 100g 8~10g (필라이즈/매일유업) | 일반 플레인요거트 100g 약 4g | 아몬드 100g 약 21g (10알 약 1.5g) | 호두 100g 약 15g | 고등어(생) 100g 약 23g | 연어(생) 100g 약 21g | 명태 100g 약 18g | 캔참치(살코기) 100g 약 26g [확인 필요] | 멸치(자건) 100g 약 47g [확인 필요]

**받는 정보**
- 섭취 식품·양 (한식 단위)

**내놓는 것**: 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력

**예시**: 사용자 '간식으로 그릭요거트 200g+아몬드 30g' → 챗봇 '단백질 약 16g+6g=22g. 운동 후 단백질 보충에 적합.'

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k17_한국_단백질_보충_식품_환산(
    섭취_식품_양,  # 섭취 식품·양 (한식 단위)
):
    """K17: 한국 단백질 보충 식품 환산. 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력"""
    ...  # 근거: https://koreanfood.rda.go.kr/kfi/fct/fctIntro/list?menuId=PS03562
```

---

### K18 — 한식 1회 제공량 표준 단위 환산 룰

- **데이터**: `workout_knowledge_base.csv` 110행 (ID `K18`) → [`rules/K18.yaml`](./rules/K18.yaml)
- **근거**: 식약처 1회 섭취 참고량 가이드 / 농촌진흥청 — [https://www.foodsafetykorea.go.kr/portal/board/boardDetail.do?menu_no=3714&bbs_no=bbs420&ntctxt_no=1069325&menu_grp=MENU_NEW03](https://www.foodsafetykorea.go.kr/portal/board/boardDetail.do?menu_no=3714&bbs_no=bbs420&ntctxt_no=1069325&menu_grp=MENU_NEW03) — ★★☆
- **분류**: 영양
- **시점**: 세션 외 / 식단 작성
- **쓰임새**: 지식베이스

**무슨 룰**: 밥 1공기=약 210g (식약처 권장 표준 1회량) | 국·찌개 1그릇=약 200~300g | 김밥 1줄=약 200~250g | 도시락 1개=약 350~500g | 고기 1인분(외식)=약 150~200g (가식부) | 회 1접시=약 150g | 면 1그릇=약 600~800g (국물 포함) | 닭가슴살 1조각(편의점)=약 100g | 계란 1개=약 50g(껍질 제외 45g) — 사용자가 양을 정확히 기억 못해도 표준 단위로 자동 환산

**받는 정보**
- 사용자 입력 (예: '밥 한 공기·치킨 두 조각')

**내놓는 것**: 정량 g → K12~K17 환산표 자동 매칭

**예시**: 사용자 '대충 한 공기' → 챗봇 자동 210g으로 환산 → 단백질 6g 적용

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k18_한식_1회_제공량_표준_단위_환산_룰(
    사용자_입력,  # 사용자 입력 (예: '밥 한 공기·치킨 두 조각')
):
    """K18: 한식 1회 제공량 표준 단위 환산 룰. 정량 g → K12~K17 환산표 자동 매칭"""
    ...  # 근거: https://www.foodsafetykorea.go.kr/portal/board/boardDetail.do?menu_no=3714&bbs_no=bbs420&ntctxt_no=1069325&menu_grp=MENU_NEW03
```

---

### K19 — Mifflin-St Jeor BMR 공식 (1순위)

- **데이터**: `workout_knowledge_base.csv` 111행 (ID `K19`) → [`rules/K19.yaml`](./rules/K19.yaml)
- **근거**: Mifflin & St Jeor 1990 (Am J Clin Nutr 51:241-7) — [https://pubmed.ncbi.nlm.nih.gov/2305711/](https://pubmed.ncbi.nlm.nih.gov/2305711/) — ★★★
- **분류**: 영양
- **시점**: 온보딩 / 체중 변동 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 남: BMR=10×W(kg)+6.25×H(cm)-5×나이+5 / 여: 동일식 -161. 비만·정상 모두 가장 정확(±10%)한 1차 권장식

**받는 정보**
- 성별
- 체중(kg)
- 키(cm)
- 나이(년)

**내놓는 것**: BMR (kcal/일) — 활동계수 곱하기 전 기초대사량

**예시**: 온보딩에서 키/몸무게/나이/성별 입력 → BMR 자동 산출. 체중 ±2kg 변동 시 재계산

**[영양·회복]에서 적용 목표**: 다이어트
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def k19_mifflin_st_jeor_bmr_공식_1순위(
    성별,
    체중,  # 체중(kg)
    키,  # 키(cm)
    나이,  # 나이(년)
):
    """K19: Mifflin-St Jeor BMR 공식 (1순위). BMR (kcal/일) — 활동계수 곱하기 전 기초대사량"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/2305711/
```

---

### K20 — Katch-McArdle BMR 공식 (체지방률 알 때)

- **데이터**: `workout_knowledge_base.csv` 112행 (ID `K20`) → [`rules/K20.yaml`](./rules/K20.yaml)
- **근거**: Aragon et al. 2017 ISSN Position Stand (J Int Soc Sports Nutr) — [https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/) — ★★★
- **분류**: 영양
- **시점**: 인바디·체지방률 입력 후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: BMR=370+(21.6×LBM kg). LBM=체중×(1-체지방률). 근육량 많은 사용자에서 Mifflin보다 정확

**받는 정보**
- 체중(kg)
- 체지방률(%)

**내놓는 것**: BMR (kcal/일) — 제지방량 기반

**예시**: 인바디 결과 입력한 사용자에 한해 K19 대신 자동 사용. 체지방률 미입력 시 K19로 폴백

**[영양·회복]에서 적용 목표**: 다이어트
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def k20_katch_mcardle_bmr_공식_체지방률_알_때(
    체중,  # 체중(kg)
    체지방률,  # 체지방률(%)
):
    """K20: Katch-McArdle BMR 공식 (체지방률 알 때). BMR (kcal/일) — 제지방량 기반"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC5470183/
```

---

### K21 — 활동계수(PAL) 표 → TDEE 산출

- **데이터**: `workout_knowledge_base.csv` 113행 (ID `K21`) → [`rules/K21.yaml`](./rules/K21.yaml)
- **근거**: FAO/WHO/UNU 2001 Human Energy Requirements (PAL 표준) — [https://www.fao.org/4/y5686e/y5686e07.htm](https://www.fao.org/4/y5686e/y5686e07.htm) — ★★★
- **분류**: 영양
- **시점**: 온보딩 / 활동량 변경 시
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: TDEE=BMR×PAL. 좌식 1.2 / 가벼움 1.375 / 보통 1.55 / 활발 1.725 / 매우 활발 1.9

**받는 정보**
- BMR(kcal)
- 활동 카테고리(5단계)

**내놓는 것**: TDEE (kcal/일) — 일일 총 에너지 소비량

**예시**: 온보딩 마지막 단계 직업·주당 운동일수 묻고 5단계 매핑 → BMR×PAL로 유지 칼로리

**[영양·회복]에서 적용 목표**: 다이어트
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def k21_활동계수_pal_표_tdee_산출(
    bmr,  # BMR(kcal)
    활동_카테고리,  # 활동 카테고리(5단계)
):
    """K21: 활동계수(PAL) 표 → TDEE 산출. TDEE (kcal/일) — 일일 총 에너지 소비량"""
    ...  # 근거: https://www.fao.org/4/y5686e/y5686e07.htm
```

---

### K22 — 활동 카테고리 한국 사용자 매핑

- **데이터**: `workout_knowledge_base.csv` 114행 (ID `K22`) → [`rules/K22.yaml`](./rules/K22.yaml)
- **근거**: FAO/WHO/UNU 2001 PAL 범위 — [https://www.fao.org/4/y5686e/y5686e07.htm](https://www.fao.org/4/y5686e/y5686e07.htm) — ★★☆
- **분류**: 영양
- **시점**: 온보딩
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 사무직+운동X=좌식(1.2) / 주1~3회 헬스=가벼움(1.375) / 주3~5회 중강도=보통(1.55) / 주6~7회 또는 격렬=활발(1.725) / 육체노동+격한 훈련=매우 활발(1.9)

**받는 정보**
- 직업 유형
- 주당 운동 빈도
- 운동 강도(RPE)

**내놓는 것**: 5단계 중 1개 카테고리 자동 선택

**예시**: 한국 직장인 다수=좌식(1.2)+주3회 헬스 → 보수적 1.375 권장(과다추정 방지)

**[영양·회복]에서 적용 목표**: 다이어트
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def k22_활동_카테고리_한국_사용자_매핑(
    직업_유형,  # 직업 유형
    주당_운동_빈도,  # 주당 운동 빈도
    운동_강도,  # 운동 강도(RPE)
):
    """K22: 활동 카테고리 한국 사용자 매핑. 5단계 중 1개 카테고리 자동 선택"""
    ...  # 근거: https://www.fao.org/4/y5686e/y5686e07.htm
```

---

### K23 — 추정식 정확도 한계·재측정 권장

- **데이터**: `workout_knowledge_base.csv` 115행 (ID `K23`) → [`rules/K23.yaml`](./rules/K23.yaml)
- **근거**: Frankenfield, Roth-Yousey, Compher 2005 (J Am Diet Assoc 105:775) — [https://pubmed.ncbi.nlm.nih.gov/15883556/](https://pubmed.ncbi.nlm.nih.gov/15883556/) — ★★★
- **분류**: 영양
- **시점**: 4주마다 / 체중 정체 시
- **쓰임새**: 지식베이스

**무슨 룰**: Mifflin도 ±10% 오차 존재. 2주간 칼로리 일정+체중 변화로 실측 보정. 정체 시 ±10~15% 조정

**받는 정보**
- 2주 평균 칼로리
- 2주 체중 변화(kg)

**내놓는 것**: TDEE 보정값 = 입력칼로리 ± (체중변화×7700/14)

**예시**: 유지 칼로리 정했는데 2주간 체중 -1kg → 실제 TDEE 추정치보다 -500kcal 낮음. 자동 재보정 알림

**[영양·회복]에서 적용 목표**: 다이어트
**다른 모듈에도 등장**: 온보딩

**함수 시그니처(제안)**
```python
def k23_추정식_정확도_한계_재측정_권장(
    _2주_평균_칼로리,  # 2주 평균 칼로리
    _2주_체중_변화,  # 2주 체중 변화(kg)
):
    """K23: 추정식 정확도 한계·재측정 권장. TDEE 보정값 = 입력칼로리 ± (체중변화×7700/14)"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/15883556/
```

---

### 분류: 회복

### K05 — 수면-근비대 관계

- **데이터**: `workout_knowledge_base.csv` 97행 (ID `K05`) → [`rules/K05.yaml`](./rules/K05.yaml)
- **근거**: Knowles 2018 / Mah 2011 — [https://pubmed.ncbi.nlm.nih.gov/29422383/](https://pubmed.ncbi.nlm.nih.gov/29422383/) — ★★★
- **분류**: 회복
- **시점**: 일일
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 성인 7~9h 권장. 6h 미만 4주 시 근감소·테스토스테론↓·인슐린저항↑

**받는 정보**
- 수면 시간 입력

**내놓는 것**: 수면 부족 시 강도 자동 하향

**예시**: 수면 5h 입력 → 그날 RPE -1, 볼륨 -20%

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k05_수면_근비대_관계(
    수면_시간_입력,  # 수면 시간 입력
):
    """K05: 수면-근비대 관계. 수면 부족 시 강도 자동 하향"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/29422383/
```

---

### K06 — 수면 부족 → 부상 위험

- **데이터**: `workout_knowledge_base.csv` 98행 (ID `K06`) → [`rules/K06.yaml`](./rules/K06.yaml)
- **근거**: Milewski 2014 — [https://pubmed.ncbi.nlm.nih.gov/25028798/](https://pubmed.ncbi.nlm.nih.gov/25028798/) — ★★★
- **분류**: 회복
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: <8h 수면 시 부상 위험 1.7배↑ (Milewski 청소년). 만성 부족은 ACWR 변동성↑

**받는 정보**
- 수면 데이터
- 훈련 부하

**내놓는 것**: 부상 위험 알림

**예시**: 3일 연속 6h 미만 → 디로드 권고

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k06_수면_부족_부상_위험(
    수면_데이터,  # 수면 데이터
    훈련_부하,  # 훈련 부하
):
    """K06: 수면 부족 → 부상 위험. 부상 위험 알림"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/25028798/
```

---

### K07 — 능동 회복 (active recovery)

- **데이터**: `workout_knowledge_base.csv` 99행 (ID `K07`) → [`rules/K07.yaml`](./rules/K07.yaml)
- **근거**: Dupuy 2018 / Frontiers — [https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full](https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full) — ★★★
- **분류**: 회복
- **시점**: 세션 후 / 회복일
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 저강도 유산소(20~40% VO2max) 10~30분이 완전 휴식보다 회복 속도↑

**받는 정보**
- 사용자 피로도

**내놓는 것**: 능동 회복 처방

**예시**: 회복일에 가벼운 자전거/걷기 추천

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k07_능동_회복_active_recovery(
    사용자_피로도,  # 사용자 피로도
):
    """K07: 능동 회복 (active recovery). 능동 회복 처방"""
    ...  # 근거: https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full
```

---

### K08 — 근육통 (DOMS) 관리

- **데이터**: `workout_knowledge_base.csv` 100행 (ID `K08`) → [`rules/K08.yaml`](./rules/K08.yaml)
- **근거**: Dupuy 2018 — [https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full](https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full) — ★★☆
- **분류**: 회복
- **시점**: 세션 후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 24~72h 피크. 가벼운 운동·마사지·온/냉찜질 효과 미미~보통. 7일+ 지속 시 부상 의심

**받는 정보**
- 통증 시작 시점
- 강도

**내놓는 것**: 정상/이상 분류

**예시**: 7일+ 지속 통증 → 부상 신호 알림

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def k08_근육통_doms_관리(
    통증_시작_시점,  # 통증 시작 시점
    강도,
):
    """K08: 근육통 (DOMS) 관리. 정상/이상 분류"""
    ...  # 근거: https://www.frontiersin.org/articles/10.3389/fphys.2018.00403/full
```

---

### 분류: 보충제

### K09 — 크레아틴 모노하이드레이트

- **데이터**: `workout_knowledge_base.csv` 101행 (ID `K09`) → [`rules/K09.yaml`](./rules/K09.yaml)
- **근거**: ISSN 2017 Position Stand — [https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0173-z](https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0173-z) — ★★★
- **분류**: 보충제
- **시점**: 일일
- **쓰임새**: 지식베이스

**무슨 룰**: 5g/일 꾸준 섭취. 근력 +5~15%, 근비대 +1~2kg(4주). 안전성 최고. 로딩 불필요

**받는 정보**
- 사용자 보충제 사용 여부

**내놓는 것**: 크레아틴 권장

**예시**: 신규 사용자에게 1순위 보충제 안내

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def k09_크레아틴_모노하이드레이트(
    사용자_보충제_사용_여부,  # 사용자 보충제 사용 여부
):
    """K09: 크레아틴 모노하이드레이트. 크레아틴 권장"""
    ...  # 근거: https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0173-z
```

---

### K10 — 카페인

- **데이터**: `workout_knowledge_base.csv` 102행 (ID `K10`) → [`rules/K10.yaml`](./rules/K10.yaml)
- **근거**: ISSN 2021 — [https://jissn.biomedcentral.com/articles/10.1186/s12970-020-00383-4](https://jissn.biomedcentral.com/articles/10.1186/s12970-020-00383-4) — ★★★
- **분류**: 보충제
- **시점**: 세션 30~60분 전
- **쓰임새**: 지식베이스

**무슨 룰**: 3~6mg/kg, 세션 30~60분 전. 근력·지구력 향상. 9mg+ 부작용. 저녁 세션 시 수면 영향

**받는 정보**
- 체중
- 세션 시각

**내놓는 것**: 카페인 양/타이밍 처방

**예시**: 70kg 사용자 → 210~420mg

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가

**함수 시그니처(제안)**
```python
def k10_카페인(
    체중,
    세션_시각,  # 세션 시각
):
    """K10: 카페인. 카페인 양/타이밍 처방"""
    ...  # 근거: https://jissn.biomedcentral.com/articles/10.1186/s12970-020-00383-4
```

---

### K11 — 베타알라닌

- **데이터**: `workout_knowledge_base.csv` 103행 (ID `K11`) → [`rules/K11.yaml`](./rules/K11.yaml)
- **근거**: ISSN 2015 — [https://jissn.biomedcentral.com/articles/10.1186/s12970-015-0090-y](https://jissn.biomedcentral.com/articles/10.1186/s12970-015-0090-y) — ★★☆
- **분류**: 보충제
- **시점**: 일일
- **쓰임새**: 지식베이스

**무슨 룰**: 3~6g/일, 4주+ 누적. 1~4분 고강도 지속력↑ (10+렙·인터벌). 저렙 근력엔 효과 미미

**받는 정보**
- 사용자 목표(고렙/지구력)

**내놓는 것**: 권장 여부

**예시**: 근지구력/HIIT 사용자에게 추천

**[영양·회복]에서 적용 목표**: 벌크업 · 근육량 증가

**함수 시그니처(제안)**
```python
def k11_베타알라닌(
    사용자_목표,  # 사용자 목표(고렙/지구력)
):
    """K11: 베타알라닌. 권장 여부"""
    ...  # 근거: https://jissn.biomedcentral.com/articles/10.1186/s12970-015-0090-y
```

---

### 분류: 카디오

### O01 — 근력+유산소 간섭효과

- **데이터**: `workout_knowledge_base.csv` 130행 (ID `O01`) → [`rules/O01.yaml`](./rules/O01.yaml)
- **근거**: Wilson 2012 메타분석 — [https://pubmed.ncbi.nlm.nih.gov/22002517/](https://pubmed.ncbi.nlm.nih.gov/22002517/) — ★★★
- **분류**: 카디오
- **시점**: 주간
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 주 3회 미만/30분 이하 카디오는 근력 간섭 미미. 같은 날엔 근력 먼저 또는 6h+ 분리

**받는 정보**
- 사용자 카디오 빈도/시간

**내놓는 것**: 간섭 위험 평가

**예시**: 매일 1시간 러닝+근력 → 분리 권장 알림

**[영양·회복]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def o01_근력_유산소_간섭효과(
    사용자_카디오_빈도_시간,  # 사용자 카디오 빈도/시간
):
    """O01: 근력+유산소 간섭효과. 간섭 위험 평가"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/22002517/
```

---

### O02 — HIIT vs LISS

- **데이터**: `workout_knowledge_base.csv` 131행 (ID `O02`) → [`rules/O02.yaml`](./rules/O02.yaml)
- **근거**: Schoenfeld / Helms — [https://www.strongerbyscience.com/concurrent-training/](https://www.strongerbyscience.com/concurrent-training/) — ★★★
- **분류**: 카디오
- **시점**: 주간
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: HIIT=시간 효율, 회복 부담↑. LISS=회복 쉬움, 시간 길음. 근력 유저는 LISS 우선

**받는 정보**
- 사용자 가용 시간
- 회복 상태

**내놓는 것**: 카디오 종류 추천

**예시**: 주 5회 근력 → LISS 30분 / 시간 부족 → HIIT 15분

**[영양·회복]에서 적용 목표**: 다이어트 · 건강증진

**함수 시그니처(제안)**
```python
def o02_hiit_vs_liss(
    사용자_가용_시간,  # 사용자 가용 시간
    회복_상태,  # 회복 상태
):
    """O02: HIIT vs LISS. 카디오 종류 추천"""
    ...  # 근거: https://www.strongerbyscience.com/concurrent-training/
```

---

### O03 — 카디오 타이밍

- **데이터**: `workout_knowledge_base.csv` 132행 (ID `O03`) → [`rules/O03.yaml`](./rules/O03.yaml)
- **근거**: Robineau 2016 — [https://pubmed.ncbi.nlm.nih.gov/25546450/](https://pubmed.ncbi.nlm.nih.gov/25546450/) — ★★☆
- **분류**: 카디오
- **시점**: 세션 전후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 근력 우선이면: 근력 후 카디오 또는 별도 세션. 다른 날 분리가 최선. 같은 부위 카디오 회피

**받는 정보**
- 세션 구성

**내놓는 것**: 카디오 배치 추천

**예시**: 다리 운동 후 러닝 자동 차단

**[영양·회복]에서 적용 목표**: 다이어트 · 건강증진

**함수 시그니처(제안)**
```python
def o03_카디오_타이밍(
    세션_구성,  # 세션 구성
):
    """O03: 카디오 타이밍. 카디오 배치 추천"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/25546450/
```

---


## 모듈 7 — 행동·안전

백그라운드. 동기·습관·이탈을 관리하고 한국 환경(헬스장·식당·날씨)에 맞춘다.

| 목표 | 들어가는 룰 |
|---|---|
| 다이어트 | R01, R02, R03, R04, R05, R06, R07, R08, R09, R10 |
| 벌크업 | R01, R02, R03, R04, R06, R07, R10 |
| 스트렝스 | R01, R03, R04, R06, R07, R10 |
| 근육량 증가 | N01, N02, N03, N04, R01, R02, R03, R04, R06, R07, R10 |
| 건강증진 | R01, R02, R03, R04, R05, R06, R07, R08, R10 |

**고유 룰 수: 14**

### 분류: 행동 코칭

### R01 — SMART 목표 설정

- **데이터**: `workout_knowledge_base.csv` 144행 (ID `R01`) → [`rules/R01.yaml`](./rules/R01.yaml)
- **근거**: Locke & Latham 2002 (American Psychologist) — [https://psycnet.apa.org/doi/10.1037/0003-066X.57.9.705](https://psycnet.apa.org/doi/10.1037/0003-066X.57.9.705) — ★★☆
- **분류**: 행동 코칭
- **시점**: 초기 온보딩
- **쓰임새**: 지식베이스

**무슨 룰**: 목표는 Specific(구체)·Measurable(측정)·Achievable(달성)·Relevant(관련)·Time-bound(기한) 5요소로 분해해야 수행과 지속이 향상됨. 모호한 목표("열심히 하기")보다 구체적·도전적 목표가 수행을 유의하게 높임

**받는 정보**
- 사용자가 입력한 목표 문장 + 현재 1RM/체중/주당 운동 횟수

**내놓는 것**: SMART 5요소 누락 항목 자동 점검 → 12주 단위 도전적 수치 목표로 재작성 (예: '벤치 80→90kg, 12주, 주 3회 5x5')

**예시**: 사용자 '근육 키우고 싶어요' 입력 → 챗봇 '구체적으로: ① 어느 부위 ② 12주 후 어느 수치(체중·둘레·1RM)까지 ③ 주 몇 회 운동 가능한가요?' 재질문

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r01_smart_목표_설정(
    사용자가_입력한_목표_문장_현재_1rm_체중_주당_운동_횟수,  # 사용자가 입력한 목표 문장 + 현재 1RM/체중/주당 운동 횟수
):
    """R01: SMART 목표 설정. SMART 5요소 누락 항목 자동 점검 → 12주 단위 도전적 수치 목표로 재작성 (예: '벤치 80→90k…"""
    ...  # 근거: https://psycnet.apa.org/doi/10.1037/0003-066X.57.9.705
```

---

### R02 — 습관 형성 평균 66일

- **데이터**: `workout_knowledge_base.csv` 145행 (ID `R02`) → [`rules/R02.yaml`](./rules/R02.yaml)
- **근거**: Lally et al. 2010 (Eur J Soc Psychol) — [https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674](https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674) — ★★☆
- **분류**: 행동 코칭
- **시점**: 초기 4주
- **쓰임새**: 지식베이스

**무슨 룰**: 새 행동이 자동화되는 데 평균 66일(개인차 18~254일). cue(시각·시간·장소) → routine(행동) → reward(보상) 3요소를 같은 맥락에 묶을 때 형성 속도가 빨라짐

**받는 정보**
- 사용자의 운동 시작일 + 주당 출석 기록

**내놓는 것**: D+0~66일은 "습관 형성 구간"으로 표시. 매일 같은 시간·장소 권고. 1~2회 빼먹어도 자동화 곡선에 거의 영향 없음을 안내(과도한 죄책감 차단)

**예시**: 사용자 '3일 빠졌는데 다 망한 거죠?' → 챗봇 'Lally 2010 연구상 1~2일 결손은 자동화 곡선에 유의한 영향 없음. 내일 같은 시간·같은 장소로 복귀하세요. 평균 자동화까지 D+45일 남음'

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r02_습관_형성_평균_66일(
    사용자의_운동_시작일_주당_출석_기록,  # 사용자의 운동 시작일 + 주당 출석 기록
):
    """R02: 습관 형성 평균 66일. D+0~66일은 "습관 형성 구간"으로 표시. 매일 같은 시간·장소 권고. 1~2회 빼먹어도 자동화 곡선에 …"""
    ...  # 근거: https://onlinelibrary.wiley.com/doi/10.1002/ejsp.674
```

---

### R03 — 자기효능감 4가지 원천

- **데이터**: `workout_knowledge_base.csv` 146행 (ID `R03`) → [`rules/R03.yaml`](./rules/R03.yaml)
- **근거**: Bandura 1977 (Psychological Review) — [https://psycnet.apa.org/doi/10.1037/0033-295X.84.2.191](https://psycnet.apa.org/doi/10.1037/0033-295X.84.2.191) — ★★☆
- **분류**: 행동 코칭
- **시점**: 초기 온보딩 + 정체기
- **쓰임새**: 지식베이스

**무슨 룰**: 자기효능감("나는 할 수 있다") 형성 4원천: ①숙달 경험(직접 성공) ②대리 경험(타인 성공 관찰) ③언어적 설득(피드백) ④생리적 상태(피로·각오 해석). 숙달 경험이 가장 강력

**받는 정보**
- 사용자의 PR(개인 최고기록) 갱신 이력 + 출석 연속 일수

**내놓는 것**: 매주 작은 PR(중량·반복·세트)을 시각화해 "숙달 경험" 누적을 보여줌. 정체기에는 비슷한 체급 사용자 진척 사례(대리 경험) 제시

**예시**: 사용자 '저는 운동에 재능이 없는 것 같아요' → 챗봇 '지난 4주간 스쿼트 60→67.5kg(+12.5%) 갱신했습니다. 이게 Bandura가 말한 숙달 경험이에요. 같은 체급 사용자 평균 +8%보다 빠른 속도'.

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r03_자기효능감_4가지_원천(
    사용자의_pr갱신_이력_출석_연속_일수,  # 사용자의 PR(개인 최고기록) 갱신 이력 + 출석 연속 일수
):
    """R03: 자기효능감 4가지 원천. 매주 작은 PR(중량·반복·세트)을 시각화해 "숙달 경험" 누적을 보여줌. 정체기에는 비슷한 체급 사용자 진…"""
    ...  # 근거: https://psycnet.apa.org/doi/10.1037/0033-295X.84.2.191
```

---

### R04 — 자율적 동기 (자율성·유능감·관계성)

- **데이터**: `workout_knowledge_base.csv` 147행 (ID `R04`) → [`rules/R04.yaml`](./rules/R04.yaml)
- **근거**: Ryan & Deci 2000 (American Psychologist) — [https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf](https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf) — ★★☆
- **분류**: 행동 코칭
- **시점**: 상시
- **쓰임새**: 지식베이스

**무슨 룰**: 자기결정이론(SDT): 내재 동기는 ①자율성(스스로 선택) ②유능감(잘하고 있다는 감각) ③관계성(연결감) 3가지 기본심리욕구가 충족될 때 강화됨. 강제·외압은 동기를 갉아먹음

**받는 정보**
- 사용자의 프로그램 수행률 + 자율 선택 비율(추천 vs 직접 선택)

**내놓는 것**: 운동 종목·세트 수를 강제하지 않고 "오늘 컨디션상 80% / 100% / 110% 중 선택" 식 옵션 제공. 매주 1회 진척 그래프로 유능감 피드백

**예시**: 사용자 '코치가 짜준 프로그램 따라하기 싫어요' → 챗봇 '오늘은 메인 운동 3가지 중 직접 골라보세요(스쿼트/레그프레스/런지). SDT 자율성 충족이 장기 지속률을 높입니다'

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r04_자율적_동기_자율성_유능감_관계성(
    사용자의_프로그램_수행률_자율_선택_비율,  # 사용자의 프로그램 수행률 + 자율 선택 비율(추천 vs 직접 선택)
):
    """R04: 자율적 동기 (자율성·유능감·관계성). 운동 종목·세트 수를 강제하지 않고 "오늘 컨디션상 80% / 100% / 110% 중 선택" 식 옵션 제공…"""
    ...  # 근거: https://selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf
```

---

### R05 — 첫 6개월 이탈률

- **데이터**: `workout_knowledge_base.csv` 148행 (ID `R05`) → [`rules/R05.yaml`](./rules/R05.yaml)
- **근거**: IHRSA Health Club Consumer Report — [https://www.ihrsa.org/about/media-center/press-releases/](https://www.ihrsa.org/about/media-center/press-releases/) — ★☆☆
- **분류**: 행동 코칭
- **시점**: 초기 온보딩 + 1·3·6개월 체크포인트
- **쓰임새**: 지식베이스

**무슨 룰**: 미국 헬스장 신규 회원의 약 50%가 가입 첫 6개월 내 이탈(IHRSA 보고). 한국도 비슷한 패턴 보고됨. 첫 90일이 가장 위험 구간

**받는 정보**
- 사용자 가입일 + 최근 14일 출석 횟수

**내놓는 것**: D+0~180일 사용자는 "고위험 코호트"로 분류. 출석 5일 공백 시 푸시 알림 + 운동 강도 -20% 조정안 제시(부담 차단)

**예시**: 사용자 가입 후 D+45일에 7일째 미출석 → 챗봇 '신규 가입자 절반은 6개월 내 그만둡니다. 오늘은 20분 짧은 루틴 어떠세요?' 자동 발송

**[행동·안전]에서 적용 목표**: 다이어트 · 건강증진

**함수 시그니처(제안)**
```python
def r05_첫_6개월_이탈률(
    사용자_가입일_최근_14일_출석_횟수,  # 사용자 가입일 + 최근 14일 출석 횟수
):
    """R05: 첫 6개월 이탈률. D+0~180일 사용자는 "고위험 코호트"로 분류. 출석 5일 공백 시 푸시 알림 + 운동 강도 -20% 조…"""
    ...  # 근거: https://www.ihrsa.org/about/media-center/press-releases/
```

---

### R06 — 정체기 심리 대응

- **데이터**: `workout_knowledge_base.csv` 149행 (ID `R06`) → [`rules/R06.yaml`](./rules/R06.yaml)
- **근거**: Stronger by Science (Helms / Nuckols, deload guidance) — [https://www.strongerbyscience.com/deload/](https://www.strongerbyscience.com/deload/) — ★☆☆
- **분류**: 행동 코칭
- **시점**: 정체기 감지 시
- **쓰임새**: 지식베이스

**무슨 룰**: 4~6주 PR 정체 시 즉각 "실패"로 해석하지 말고 ①진척 정의 재설정(중량 외 볼륨·폼·컨디션) ②1주 디로드(볼륨 -40~50%) ③프로그램 구조 변경 순으로 대응. 심리적 burnout 방지

**받는 정보**
- 최근 4~6주 PR 갱신 여부 + 주관적 피로(RPE 추세)

**내놓는 것**: 4주 정체 + RPE 평균 ≥8 → 자동 "디로드 1주" 권고. 정체기 카드에 "중량은 멈췄지만 출석률·폼·총 볼륨은 +15%" 식 비-중량 진척 표기

**예시**: 사용자 '4주째 벤치 PR이 안 갱신돼요. 그만둘까 봐요' → 챗봇 'RPE 평균 8.5로 누적 피로 신호. 다음 주 디로드(볼륨 -50%) 후 재시도 제안. 출석률 92%는 그대로 진척입니다'

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r06_정체기_심리_대응(
    최근_4_6주_pr_갱신_여부_주관적_피로,  # 최근 4~6주 PR 갱신 여부 + 주관적 피로(RPE 추세)
):
    """R06: 정체기 심리 대응. 4주 정체 + RPE 평균 ≥8 → 자동 "디로드 1주" 권고. 정체기 카드에 "중량은 멈췄지만 출석률·폼·…"""
    ...  # 근거: https://www.strongerbyscience.com/deload/
```

---

### R07 — 사회적 지지·운동 파트너 효과

- **데이터**: `workout_knowledge_base.csv` 150행 (ID `R07`) → [`rules/R07.yaml`](./rules/R07.yaml)
- **근거**: Carron Hausenblas Mack 1996 / Burke et al. 2006 (group cohesion meta) — [https://journals.humankinetics.com/view/journals/jsep/18/1/article-p1.xml](https://journals.humankinetics.com/view/journals/jsep/18/1/article-p1.xml) — ★★☆
- **분류**: 행동 코칭
- **시점**: 초기 온보딩 + 정체기
- **쓰임새**: 지식베이스

**무슨 룰**: 운동 그룹 응집력(group cohesion)은 운동 출석·지속률에 중간 효과크기로 양의 영향. 파트너·소그룹·온라인 챌린지 모두 단독보다 지속률↑ (Carron 메타분석)

**받는 정보**
- 사용자의 운동 파트너 유무 + 그룹/챌린지 참여 여부

**내놓는 것**: 파트너 부재 시 "함께하기" 기능(친구 초대·앱 내 챌린지 매칭) 노출. 그룹 출석 시 개인 출석 가중 +1로 시각화

**예시**: 사용자 '혼자 하니까 자꾸 빼먹어요' → 챗봇 'Carron 메타분석상 그룹 운동이 단독 대비 출석률 유의 향상. 같은 시간대 운동하는 사용자 5명 매칭해드릴까요?'

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r07_사회적_지지_운동_파트너_효과(
    사용자의_운동_파트너_유무_그룹_챌린지_참여_여부,  # 사용자의 운동 파트너 유무 + 그룹/챌린지 참여 여부
):
    """R07: 사회적 지지·운동 파트너 효과. 파트너 부재 시 "함께하기" 기능(친구 초대·앱 내 챌린지 매칭) 노출. 그룹 출석 시 개인 출석 가중 +1…"""
    ...  # 근거: https://journals.humankinetics.com/view/journals/jsep/18/1/article-p1.xml
```

---

### R08 — 외부 보상 vs 내재 동기 (crowding-out)

- **데이터**: `workout_knowledge_base.csv` 151행 (ID `R08`) → [`rules/R08.yaml`](./rules/R08.yaml)
- **근거**: Deci, Koestner & Ryan 1999 (Psychological Bulletin meta-analysis) — [https://psycnet.apa.org/doi/10.1037/0033-2909.125.6.627](https://psycnet.apa.org/doi/10.1037/0033-2909.125.6.627) — ★★★
- **분류**: 행동 코칭
- **시점**: 보상 시스템 설계 시
- **쓰임새**: 지식베이스

**무슨 룰**: 흥미로운 활동에 "돈·뱃지·등수" 같은 유형 보상을 일률 지급하면 내재 동기를 평균 -0.36 SD 감소시킴(Deci 1999 메타분석, k=128). 예상치 못한 보상·정보적 피드백은 영향 없음

**받는 정보**
- 사용자가 운동을 ""재미있다""고 답한 빈도 + 보상 시스템 노출 여부

**내놓는 것**: 흥미·자율 동기가 이미 높은 사용자에게는 금전·뱃지 보상 노출 최소화. 대신 진척 데이터·개선 피드백 위주로 표시

**예시**: 설계 결정: 신규 사용자는 출석 뱃지 노출 / 6개월+ 자발 운동 사용자는 뱃지 OFF·진척 그래프 강조

**[행동·안전]에서 적용 목표**: 다이어트 · 건강증진

**함수 시그니처(제안)**
```python
def r08_외부_보상_vs_내재_동기_crowding_out(
    사용자가_운동을_재미있다_고_답한_빈도_보상_시스템_노출_여부,  # 사용자가 운동을 ""재미있다""고 답한 빈도 + 보상 시스템 노출 여부
):
    """R08: 외부 보상 vs 내재 동기 (crowding-out). 흥미·자율 동기가 이미 높은 사용자에게는 금전·뱃지 보상 노출 최소화. 대신 진척 데이터·개선 피드백 위주로…"""
    ...  # 근거: https://psycnet.apa.org/doi/10.1037/0033-2909.125.6.627
```

---

### R09 — 운동 강박·RED-S 스크리닝

- **데이터**: `workout_knowledge_base.csv` 152행 (ID `R09`) → [`rules/R09.yaml`](./rules/R09.yaml)
- **근거**: Mountjoy et al. 2018 IOC RED-S Consensus Update (BJSM) — [https://bjsm.bmj.com/content/52/11/687](https://bjsm.bmj.com/content/52/11/687) — ★★★
- **분류**: 행동 코칭
- **시점**: 상시 모니터링
- **쓰임새**: 지식베이스

**무슨 룰**: 저에너지가용성(LEA: <30 kcal/kg FFM/day) 지속 시 RED-S 위험. 신호: 급격한 체중 감소·휴식기 심박 변화·여성 무월경·만성 피로·강박적 운동. 의학적 진단·치료는 의료진 영역

**받는 정보**
- 주당 운동 시간 + 식사 빈도/총 칼로리 + (여성) 월경 주기 + 휴식기 심박

**내놓는 것**: 위험 신호 ≥3개 발견 시 "운동량 -30% 권고 + 의료/영양 전문가 상담 안내" 카드 표시. 챗봇은 진단·처방 금지(의료법 회피), "스포츠의학 전문의 상담을 권합니다"로 한정

**예시**: 사용자 '주 10회 운동, 식사 1500kcal, 3개월째 월경 없어요' → 챗봇 'IOC 2018 RED-S 기준상 위험 신호입니다. 운동량 일시 -30% 조정 + 스포츠의학 전문의/영양사 상담을 강하게 권합니다. 본 앱은 진단을 제공하지 않습니다'

**[행동·안전]에서 적용 목표**: 다이어트

**함수 시그니처(제안)**
```python
def r09_운동_강박_red_s_스크리닝(
    주당_운동_시간_식사_빈도_총_칼로리_월경_주기_휴식기_심박,  # 주당 운동 시간 + 식사 빈도/총 칼로리 + (여성) 월경 주기 + 휴식기 심박
):
    """R09: 운동 강박·RED-S 스크리닝. 위험 신호 ≥3개 발견 시 "운동량 -30% 권고 + 의료/영양 전문가 상담 안내" 카드 표시. 챗봇은 진단…"""
    ...  # 근거: https://bjsm.bmj.com/content/52/11/687
```

---

### R10 — 한국 직장인 시간 충돌·회식 대응

- **데이터**: `workout_knowledge_base.csv` 153행 (ID `R10`) → [`rules/R10.yaml`](./rules/R10.yaml)
- **근거**: KOSIS 임금근로일자리 근로시간 통계 + 자체 룰 (Parr 2014 알코올·근단백질합성 참고) — [https://kosis.kr/statHtml/statHtml.do?orgId=118&tblId=DT_118N_PAYM55](https://kosis.kr/statHtml/statHtml.do?orgId=118&tblId=DT_118N_PAYM55) — ★☆☆
- **분류**: 행동 코칭
- **시점**: 주간 일정 조정
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 한국 임금근로자 주당 평균 근로시간 약 38~40시간(KOSIS), 회식 빈도 월 2~4회 보고. 회식 당일은 운동 패스 대신 익일 보강(20분 단축 세션) + 알코올 24시간 내 근비대 신호 -37% 감소 고려

**받는 정보**
- 사용자의 근무 형태 + 회식 일정(캘린더 연동) + 주당 운동 가능 일수

**내놓는 것**: 회식 캘린더 감지 시: 당일은 휴식 권고 + 익일은 "20분 압축 루틴"(메인 운동 3개 5x5만) 자동 제안. 주간 볼륨 -10~15% 자동 조정으로 미달 보강

**예시**: 사용자 '오늘 회식이라 운동 못 가요' → 챗봇 '내일 20분 압축 세션(스쿼트·벤치·로우 5x5)으로 주간 볼륨 92% 회복 가능. 음주 후 24시간은 근비대 신호가 줄어드니 폼 위주로'.

**[행동·안전]에서 적용 목표**: 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진

**함수 시그니처(제안)**
```python
def r10_한국_직장인_시간_충돌_회식_대응(
    사용자의_근무_형태_회식_일정_주당_운동_가능_일수,  # 사용자의 근무 형태 + 회식 일정(캘린더 연동) + 주당 운동 가능 일수
):
    """R10: 한국 직장인 시간 충돌·회식 대응. 회식 캘린더 감지 시: 당일은 휴식 권고 + 익일은 "20분 압축 루틴"(메인 운동 3개 5x5만) 자동 제…"""
    ...  # 근거: https://kosis.kr/statHtml/statHtml.do?orgId=118&tblId=DT_118N_PAYM55
```

---

### 분류: 생리학

### N01 — 근비대 3 메커니즘

- **데이터**: `workout_knowledge_base.csv` 126행 (ID `N01`) → [`rules/N01.yaml`](./rules/N01.yaml)
- **근거**: Schoenfeld 2010 / Wackerhage 2019 — [https://pubmed.ncbi.nlm.nih.gov/20847704/](https://pubmed.ncbi.nlm.nih.gov/20847704/) — ★★★
- **분류**: 생리학
- **시점**: KB
- **쓰임새**: 지식베이스

**무슨 룰**: Mechanical tension(주요) · Metabolic stress(보조) · Muscle damage(부수). Tension이 핵심 드라이버

**받는 정보**
- -

**내놓는 것**: 처방 알고리즘 가중치

**예시**: tension 우선 → 풀ROM·진보적 과부하 알고리즘

**[행동·안전]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def n01_근비대_3_메커니즘(
    x,  # -
):
    """N01: 근비대 3 메커니즘. 처방 알고리즘 가중치"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/20847704/
```

---

### N02 — 신경 적응 vs 근비대 적응

- **데이터**: `workout_knowledge_base.csv` 127행 (ID `N02`) → [`rules/N02.yaml`](./rules/N02.yaml)
- **근거**: Sale 1988 / Counts 2017 — [https://pubmed.ncbi.nlm.nih.gov/3057313/](https://pubmed.ncbi.nlm.nih.gov/3057313/) — ★★★
- **분류**: 생리학
- **시점**: KB
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초보 4~8주: 주로 신경 적응(근력↑·사이즈 거의 X). 8주+: 근비대 시작. 고급은 비대 위주

**받는 정보**
- 훈련 기간

**내놓는 것**: 사용자 기대값 조정

**예시**: 신규 사용자에게 '4주 후 사이즈 변화 작음' 안내

**[행동·안전]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def n02_신경_적응_vs_근비대_적응(
    훈련_기간,  # 훈련 기간
):
    """N02: 신경 적응 vs 근비대 적응. 사용자 기대값 조정"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/3057313/
```

---

### N03 — 운동 호르몬 반응

- **데이터**: `workout_knowledge_base.csv` 128행 (ID `N03`) → [`rules/N03.yaml`](./rules/N03.yaml)
- **근거**: Morton 2016 (J Appl Physiol) — [https://pubmed.ncbi.nlm.nih.gov/27174923/](https://pubmed.ncbi.nlm.nih.gov/27174923/) — ★★★
- **분류**: 생리학
- **시점**: KB
- **쓰임새**: 지식베이스

**무슨 룰**: 급성 테스토스테론·GH 상승은 근비대와 약한 상관. 만성 코르티솔↑은 회복 저하. "호르몬 부스팅" 마케팅 주의

**받는 정보**
- -

**내놓는 것**: 사용자 교육 콘텐츠

**예시**: '레그데이로 테스토 폭증' 같은 미신 정정

**[행동·안전]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def n03_운동_호르몬_반응(
    x,  # -
):
    """N03: 운동 호르몬 반응. 사용자 교육 콘텐츠"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/27174923/
```

---

### N04 — 근섬유 타입 (Type I/II)

- **데이터**: `workout_knowledge_base.csv` 129행 (ID `N04`) → [`rules/N04.yaml`](./rules/N04.yaml)
- **근거**: Schoenfeld 2021 — [https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/) — ★★★
- **분류**: 생리학
- **시점**: KB
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: Type II(속근)도 고렙(15+)에서 비대. Type I(지근)도 모든 렙 범위 비대. '저렙=속근' 단순화 오류

**받는 정보**
- -

**내놓는 것**: 렙범위 권장 폭 확장

**예시**: 근비대 6~30렙 모두 효과적임을 사용자 교육

**[행동·안전]에서 적용 목표**: 근육량 증가

**함수 시그니처(제안)**
```python
def n04_근섬유_타입_type_i_ii(
    x,  # -
):
    """N04: 근섬유 타입 (Type I/II). 렙범위 권장 폭 확장"""
    ...  # 근거: https://pmc.ncbi.nlm.nih.gov/articles/PMC7927075/
```

---


## 별도 레이어 — 모듈 위에 얹는 안전 필터

매트릭스 룰을 실행하기 **전에** 항상 먼저 통과해야 하는 가드들. 사용자 상태(나이·질환·부상·피로)에 따라 매트릭스 룰을 차단·치환·완화한다.

### 모집단 분기

노인·청소년·만성질환(당뇨·고혈압·이상지질혈증·골관절염) 사용자에 대해 일반 룰을 차단하거나 강도를 낮춘다. 온보딩에서 한 번 분류된 라벨이 평생 따라다니며 매 룰 호출 직전에 검사된다.

**들어가는 룰**: L02, L03, L04, L05, L06, L07, L08

### L02 — 노인 (50+) sarcopenia 대응

- **데이터**: `workout_knowledge_base.csv` 116행 (ID `L02`) → [`rules/L02.yaml`](./rules/L02.yaml)
- **근거**: ACSM 2026 / ESPEN — [https://acsm.org/resistance-training-guidelines-update-2026/](https://acsm.org/resistance-training-guidelines-update-2026/) — ★★★
- **분류**: 특수 모집단
- **시점**: 처방 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 주 2~3회 저항운동 필수. 8~12렙×2~3세트, 60~80% 1RM. 단백질 1.2~1.6g/kg+, 점진과부하 보수적

**받는 정보**
- 사용자 연령

**내놓는 것**: 노인용 처방 분기

**예시**: 60세+ 사용자 → 안전 첫 8주 적응기

**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l02_노인_50_sarcopenia_대응(
    사용자_연령,  # 사용자 연령
):
    """L02: 노인 (50+) sarcopenia 대응. 노인용 처방 분기"""
    ...  # 근거: https://acsm.org/resistance-training-guidelines-update-2026/
```

---

### L03 — 청소년 가이드라인

- **데이터**: `workout_knowledge_base.csv` 117행 (ID `L03`) → [`rules/L03.yaml`](./rules/L03.yaml)
- **근거**: NSCA Youth Position Statement — [https://pubmed.ncbi.nlm.nih.gov/19620931/](https://pubmed.ncbi.nlm.nih.gov/19620931/) — ★★★
- **분류**: 특수 모집단
- **시점**: 처방 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 성장판 안전. 폼 우선, 6~15렙, 코치 감독 필수. 1RM 테스트 X, RPE 기반

**받는 정보**
- 사용자 연령

**내놓는 것**: 청소년용 처방 분기

**예시**: 17세 이하 → 1RM 테스트 잠금

**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l03_청소년_가이드라인(
    사용자_연령,  # 사용자 연령
):
    """L03: 청소년 가이드라인. 청소년용 처방 분기"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/19620931/
```

---

### L04 — 초보/중급/고급 정의

- **데이터**: `workout_knowledge_base.csv` 118행 (ID `L04`) → [`rules/L04.yaml`](./rules/L04.yaml)
- **근거**: Rippetoe (Practical Programming) — [https://startingstrength.com/article/training_age](https://startingstrength.com/article/training_age) — ★★★
- **분류**: 특수 모집단
- **시점**: 초기 셋업
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 초보=훈련 <6개월, 매 세션 진보 가능. 중급=6개월~2년, 주간 진보. 고급=2년+, 메조사이클 단위

**받는 정보**
- 훈련 기간
- 1RM 비율

**내놓는 것**: 레벨 분류

**예시**: 레벨 → 알고리즘 분기 (LP vs 자율조절 vs 블록)

**들어가는 매트릭스 칸**: 온보딩(다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진)
**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l04_초보_중급_고급_정의(
    훈련_기간,  # 훈련 기간
    _1rm_비율,  # 1RM 비율
):
    """L04: 초보/중급/고급 정의. 레벨 분류"""
    ...  # 근거: https://startingstrength.com/article/training_age
```

---

### L05 — 제2형 당뇨 운동 처방

- **데이터**: `workout_knowledge_base.csv` 119행 (ID `L05`) → [`rules/L05.yaml`](./rules/L05.yaml)
- **근거**: ACSM Guidelines for Exercise Testing and Prescription 11th ed (2022) + ADA Standards of Care 2024 + 대한당뇨병학회 2023 진료지침 — [https://www.acsm.org/education-resources/books/guidelines-exercise-testing-prescription/](https://www.acsm.org/education-resources/books/guidelines-exercise-testing-prescription/) — ★★★
- **분류**: 특수 모집단
- **시점**: 사용자 프로필 등록 시 / 강도 처방 시
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 빈도 유산소 3~7일/주(연속 2일 비활동 회피)+저항 2~3일/주 비연속일 | 강도 중강도 RPE5~7(40~60% HRR/VO2R, 50~70% HRmax) | 시간 유산소 150분/주(중강도) 또는 75분/주(고강도) · 저항 주요 근육군 8~10종목×1~3세트 | 형태 걷기·자전거·수영·기계식 저항 권장, 식후 30분 가벼운 걷기 = 식후혈당 변동↓ | 인슐린·SU계(글리메피리드/글리피지드) 복용자: 운동 전 혈당<100 mg/dL 시 탄수 15g 보충, 운동 중·후 저혈당 모니터 | 30분마다 일어서기/3~5분 가벼운 움직임 | 적색기(즉시 의뢰): 증식성 망막증·심한 비증식성 망막증→고강도/Valsalva/점프/머리숙임 동작 금지·안과 의뢰 / 자율신경병증·심한 신경병증·족부궤양→체중부하 운동 제한·내분비내과 의뢰 / 공복혈당>250 mg/dL+케톤 양성→운동 보류 / 저혈당 빈발(주 2회 이상) 또는 무자각성 저혈당→내분비내과 상담

**받는 정보**
- 진단명(제2형 당뇨)
- 복용 약물(인슐린·SU·메트포르민 등)
- 합병증(망막증/신증/신경병증/족부)
- HbA1c·공복혈당
- 운동 가능 시간

**내놓는 것**: FITT 권고(유산소 분/주·저항 회/주) + 회피 운동 리스트 + RPE 상한 + 운동 전후 혈당 모니터링 항목 + 의뢰 트리거 분기

**예시**: 사용자: "당뇨인데 데드리프트 해도 돼요?" → 챗봇: "제2형 당뇨이면서 망막·신장 합병증이 없다면 저항운동은 권장됩니다(주 2~3회). 다만 70kg 사용자 기준 RPE7 이하·8~12렙·세트 사이 호흡 정상 유지(Valsalva 회피)를 권고합니다. 인슐린/글리메피리드 복용 중이면 운동 시작 전 혈당 측정해 100 mg/dL 미만이면 탄수 15g(바나나 1/2개) 드시고 시작하세요. 망막증·심한 신경병증이 있다면 데드리프트는 피하고 내분비내과·안과 상담을 받으시는 것이 안전합니다."

**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l05_제2형_당뇨_운동_처방(
    진단명,  # 진단명(제2형 당뇨)
    복용_약물,  # 복용 약물(인슐린·SU·메트포르민 등)
    합병증,  # 합병증(망막증/신증/신경병증/족부)
    hba1c_공복혈당,  # HbA1c·공복혈당
    운동_가능_시간,  # 운동 가능 시간
):
    """L05: 제2형 당뇨 운동 처방. FITT 권고(유산소 분/주·저항 회/주) + 회피 운동 리스트 + RPE 상한 + 운동 전후 혈당 모니터링…"""
    ...  # 근거: https://www.acsm.org/education-resources/books/guidelines-exercise-testing-prescription/
```

---

### L06 — 고혈압 운동 처방

- **데이터**: `workout_knowledge_base.csv` 120행 (ID `L06`) → [`rules/L06.yaml`](./rules/L06.yaml)
- **근거**: ACSM Guidelines 11th ed (2022) + ACSM Pronouncement on Exercise & Hypertension 2023 + 대한고혈압학회 2022 진료지침 — [https://www.koreanhypertension.org/reference/guide?mode=read&idno=10081](https://www.koreanhypertension.org/reference/guide?mode=read&idno=10081) — ★★★
- **분류**: 특수 모집단
- **시점**: 사용자 프로필 등록 시 / 강도 처방 시
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 빈도 유산소 5~7일/주(가능하면 매일)+저항 2~3일/주 | 강도 중강도 RPE4~6(40~60% VO2R/HRR) - 저항운동은 RPE6 이하·1RM 60~70%로 보수적 | 시간 유산소 30분/일(또는 누적), 주 90~150분 · 저항 주요 근육군 8~12렙×2~4세트 | 형태 걷기·자전거·수영 등 유산소 우선 + 가벼운 머신 저항(프리웨이트 1RM 이상 고중량 회피) | Valsalva(호흡 참기) 절대 회피 - 들어올릴 때 호기, 내릴 때 흡기 / 운동 중 SBP>250 또는 DBP>115 시 즉시 중단 | β-차단제 복용자: 심박수 둔화 → HR 대신 RPE로 강도 관리 / 이뇨제: 탈수·전해질 주의 / α-차단제: 운동 후 기립성 저혈압 위험 → 쿨다운 5분 필수 | 적색기(즉시 의뢰): 안정시 BP≥180/110 mmHg → 운동 보류·내과 진료 / 가슴통증·심한 두통·시야 흐림·호흡곤란·실신감 → 즉시 중단·119 또는 응급실 / 미조절 고혈압(BP>160/100 지속)·표적장기 손상 의심 → 심장내과 상담

**받는 정보**
- 진단명(고혈압 1·2기)
- 복용 약물(β-차단제·이뇨제·ACEi·ARB·CCB)
- 안정시 BP 최근치
- 동반질환(CVD/당뇨)

**내놓는 것**: FITT 권고 + Valsalva 회피 안내 + RPE 상한(저항 RPE6) + 약물별 주의사항 + 의뢰 트리거 + 운동 중 BP 모니터링 권고

**예시**: 사용자: "고혈압 약(베타차단제) 먹는데 데드리프트 괜찮나요?" → 챗봇: "안정시 혈압이 140/90 이하로 조절되고 있다면 데드리프트가 절대 금지는 아닙니다. 다만 70kg 사용자 기준 1RM 60% 이하(약 60kg)·8~12렙·RPE6 이하로 가볍게, 호흡은 들어올릴 때 "후" 내쉬기를 지키세요(호흡 참기는 혈압 급상승의 가장 큰 원인). 베타차단제는 심박수를 둔화시키므로 심박수 대신 RPE로 강도를 가늠하시고, 운동 후 어지러움이 오면 5분 이상 천천히 걷는 쿨다운을 하세요. 안정시 BP가 180/110을 넘는 날엔 운동을 미루고 내과 상담이 필요합니다."

**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l06_고혈압_운동_처방(
    진단명,  # 진단명(고혈압 1·2기)
    복용_약물,  # 복용 약물(β-차단제·이뇨제·ACEi·ARB·CCB)
    안정시_bp_최근치,  # 안정시 BP 최근치
    동반질환,  # 동반질환(CVD/당뇨)
):
    """L06: 고혈압 운동 처방. FITT 권고 + Valsalva 회피 안내 + RPE 상한(저항 RPE6) + 약물별 주의사항 + 의뢰 트…"""
    ...  # 근거: https://www.koreanhypertension.org/reference/guide?mode=read&idno=10081
```

---

### L07 — 이상지질혈증·대사증후군 운동 처방

- **데이터**: `workout_knowledge_base.csv` 121행 (ID `L07`) → [`rules/L07.yaml`](./rules/L07.yaml)
- **근거**: ACSM Guidelines 11th ed (2022) + 한국지질·동맥경화학회 이상지질혈증 진료지침 5판 (2022) — [https://www.lipid.or.kr/uploaded/board/guideline/_50e8f3527d0798a82a29b8ef6c363cce2.pdf](https://www.lipid.or.kr/uploaded/board/guideline/_50e8f3527d0798a82a29b8ef6c363cce2.pdf) — ★★★
- **분류**: 특수 모집단
- **시점**: 사용자 프로필 등록 시 / 강도 처방 시
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 빈도 유산소 5~7일/주(가능하면 매일)+저항 2~3일/주(비연속일)+유연성 2~3일/주 | 강도 중강도 RPE4~6(40~70% HRR, HRmax 55~75%) - 체중감량 목표 시 강도보다 시간 우선 | 시간 유산소 30~60분/일·주 200~300분(체중감량/지질개선 최적), 최소 150분 · 주당 칼로리 소비 1,000~2,000 kcal | 형태 걷기·조깅·자전거·수영(유산소) + 상하지·체간 기계식 저항(주요 근육군) | 동반 위험인자(고혈압·당뇨·CVD)에 따라 L05/L06 안전기준 중복 적용 | 적색기(즉시 의뢰): 가족성 고콜레스테롤(LDL>190)·기왕 심혈관질환(MI/PCI/뇌졸중)·당뇨+50세 이상·운동 중 가슴통증/턱·왼팔 방사통/심한 호흡곤란 → 운동 시작 전 심혈관내과 운동부하검사 권고 / 미조절 대사증후군(혈압>180/110, 공복혈당>250) → 내과 의뢰 후 운동 시작

**받는 정보**
- 진단명(이상지질혈증·대사증후군)
- 지질 패널(LDL/HDL/TG)
- 복용 약물(스타틴·에제티미브·페노피브레이트)
- 동반질환
- BMI/허리둘레

**내놓는 것**: FITT 권고 + 주 칼로리 소비 목표 + 동반질환 시 L05/L06 규칙 중복 적용 + 의뢰 트리거

**예시**: 사용자: "중성지방 280인데 어떤 운동을 얼마나 해야 하나요?" → 챗봇: "중성지방 개선에는 유산소가 가장 효과적입니다. 빨리걷기·자전거·수영을 주 5일 이상, 회당 30~60분, 주 합계 200~300분을 권고합니다(중강도 RPE5 정도). 여기에 주 2~3회 저항운동을 더하면 LDL이 추가로 약 10% 더 낮아진다는 보고가 있습니다. 70kg 기준 주당 1,000~2,000 kcal 소비가 지질 개선 최적 구간입니다. 단, 가족성 고콜레스테롤(LDL>190)이거나 심혈관질환 이력이 있다면 시작 전 심장내과 운동부하검사를 받으시는 것이 안전합니다."

**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l07_이상지질혈증_대사증후군_운동_처방(
    진단명,  # 진단명(이상지질혈증·대사증후군)
    지질_패널,  # 지질 패널(LDL/HDL/TG)
    복용_약물,  # 복용 약물(스타틴·에제티미브·페노피브레이트)
    동반질환,
    bmi_허리둘레,  # BMI/허리둘레
):
    """L07: 이상지질혈증·대사증후군 운동 처방. FITT 권고 + 주 칼로리 소비 목표 + 동반질환 시 L05/L06 규칙 중복 적용 + 의뢰 트리거"""
    ...  # 근거: https://www.lipid.or.kr/uploaded/board/guideline/_50e8f3527d0798a82a29b8ef6c363cce2.pdf
```

---

### L08 — 골관절염(무릎·고관절) 운동 처방

- **데이터**: `workout_knowledge_base.csv` 122행 (ID `L08`) → [`rules/L08.yaml`](./rules/L08.yaml)
- **근거**: OARSI 2019 (Bannuru) + ACR 2019 (Kolasinski) + ACSM Guidelines 11th ed (2022) + 대한정형외과학회 무릎관절염 자료 — [https://www.oarsijournal.com/article/S1063-4584(19)31116-1/fulltext](https://www.oarsijournal.com/article/S1063-4584(19)31116-1/fulltext) — ★★★
- **분류**: 특수 모집단
- **시점**: 사용자 프로필 등록 시 / 강도 처방 시
- **쓰임새**: 운동 추천, 실시간 코칭, 지식베이스

**무슨 룰**: 빈도 저항(근력) 2~3일/주+유산소 3~5일/주+유연성/모빌리티 매일 | 강도 저항운동 RPE5~7(60~70% 1RM, 통증 NRS≤4 유지) - 통증 NRS>5면 즉시 강도/ROM 감량 | 시간 저항 8~10종목×8~15렙×1~3세트, 회당 30~60분 · 유산소 회당 20~30분(주 150분 목표) | 형태 핵심: 구조화된 지상 운동 프로그램(land-based) - 대퇴사두근/둔근/체간 강화·유산소(걷기·자전거·수영)·기능적 균형. 무릎 OA는 수중운동 추가 권고(체중부하↓). 태극권 권고(ACR 강력) | 회피: 통증 유발하는 깊은 스쿼트(>90도 굴곡)·점프/착지·갑작스런 방향전환·중량 런지 - 점진적 ROM 확장 | 동반 GI/CV 질환 시 NSAIDs 사용 보수적, 운동요법 우선 | 적색기(정형외과 의뢰): 야간통(잠 깨는 통증)·관절 잠김(locking)·갑작스런 무력감(giving way)·관절 발적·발열·외상성 부종·6주+ 보존치료에도 통증/기능 악화 → 정형외과 평가

**받는 정보**
- 진단명(무릎/고관절 OA)
- 통증 NRS(0~10)
- 발병 부위
- 동반질환(GI·CV)
- 보행/계단 가능 여부
- BMI

**내놓는 것**: FITT 권고(통증 NRS 기반 강도 캡) + 회피 동작 리스트 + 수중운동/태극권 옵션 + 정형외과 의뢰 트리거

**예시**: 사용자: "무릎관절염 진단받았는데 스쿼트 해도 되나요?" → 챗봇: "무릎 OA의 핵심 치료는 대퇴사두근 강화 + 유산소이며, 운동은 OARSI·ACR 모두 가장 강력하게 권고합니다. 스쿼트는 가능하지만 깊이는 무릎 90도까지 제한, 통증 NRS 4 이하로 유지하세요. 70kg 사용자 기준 박스 스쿼트 빈 봉~20kg×10렙×3세트, RPE6 이내로 시작해 2주마다 5% 점진 증가를 권고합니다. 통증이 NRS 5 이상이면 즉시 의자 스쿼트(부분 ROM)·레그 익스텐션 머신으로 대체하세요. 무릎이 잠기거나 갑자기 힘이 빠지는 느낌, 밤에 잠을 깰 정도의 통증, 발열·발적이 있다면 즉시 정형외과 진료가 필요합니다. 수중운동(아쿠아 워킹)과 태극권도 강력 권고됩니다."

**별도 레이어**: 모집단 분기

**함수 시그니처(제안)**
```python
def l08_골관절염_무릎_고관절_운동_처방(
    진단명,  # 진단명(무릎/고관절 OA)
    통증_nrs,  # 통증 NRS(0~10)
    발병_부위,  # 발병 부위
    동반질환,  # 동반질환(GI·CV)
    보행_계단_가능_여부,  # 보행/계단 가능 여부
    bmi,
):
    """L08: 골관절염(무릎·고관절) 운동 처방. FITT 권고(통증 NRS 기반 강도 캡) + 회피 동작 리스트 + 수중운동/태극권 옵션 + 정형외과 의뢰 …"""
    ...  # 근거: https://www.oarsijournal.com/article/S1063-4584(19)31116-1/fulltext
```

---

### 부상 이벤트 트리거

사용자가 운동 중 통증을 입력하면 즉시 발동. 일반 매트릭스를 중단시키고 부상 전용 흐름(통증 평가 → 대체 운동 → 의료 의뢰)으로 갈아탄다.

**들어가는 룰**: Q01, Q02, Q03, Q04, Q05, Q06

### Q01 — 급성 부상 처치 (PEACE & LOVE)

- **데이터**: `workout_knowledge_base.csv` 138행 (ID `Q01`) → [`rules/Q01.yaml`](./rules/Q01.yaml)
- **근거**: Dubois 2019 BJSM — [https://bjsm.bmj.com/content/54/2/72](https://bjsm.bmj.com/content/54/2/72) — ★★★
- **분류**: 부상 관리
- **시점**: 부상 후
- **쓰임새**: 실시간 코칭, 지식베이스

**무슨 룰**: 급성기(0~3d): Protect·Elevate·Avoid anti-inflam·Compress·Educate. 후속: Load·Optimism·Vascular·Exercise. RICE는 구식

**받는 정보**
- 부상 시점
- 부위

**내놓는 것**: 단계별 가이드

**예시**: 급성 부상 입력 → 자동 단계 안내

**별도 레이어**: 부상 이벤트 트리거

**함수 시그니처(제안)**
```python
def q01_급성_부상_처치_peace_love(
    부상_시점,  # 부상 시점
    부위,
):
    """Q01: 급성 부상 처치 (PEACE & LOVE). 단계별 가이드"""
    ...  # 근거: https://bjsm.bmj.com/content/54/2/72
```

---

### Q02 — 부상 복귀 단계

- **데이터**: `workout_knowledge_base.csv` 139행 (ID `Q02`) → [`rules/Q02.yaml`](./rules/Q02.yaml)
- **근거**: BJSM Return-to-Sport — [https://bjsm.bmj.com/content/50/14/853](https://bjsm.bmj.com/content/50/14/853) — ★★★
- **분류**: 부상 관리
- **시점**: 부상 후
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 1: 통증 0/10 휴식 → 2: 가동범위 회복 → 3: 무통 저강도 부하 → 4: 점진 부하 → 5: 복귀. 단계당 통증 0 확인

**받는 정보**
- 부상 단계
- 통증 점수

**내놓는 것**: 다음 단계 진행 여부

**예시**: 부상 복귀 자동 단계 진행

**별도 레이어**: 부상 이벤트 트리거

**함수 시그니처(제안)**
```python
def q02_부상_복귀_단계(
    부상_단계,  # 부상 단계
    통증_점수,  # 통증 점수
):
    """Q02: 부상 복귀 단계. 다음 단계 진행 여부"""
    ...  # 근거: https://bjsm.bmj.com/content/50/14/853
```

---

### Q03 — 운동 복귀 기준

- **데이터**: `workout_knowledge_base.csv` 140행 (ID `Q03`) → [`rules/Q03.yaml`](./rules/Q03.yaml)
- **근거**: Ardern 2016 — [https://bjsm.bmj.com/content/50/14/853](https://bjsm.bmj.com/content/50/14/853) — ★★★
- **분류**: 부상 관리
- **시점**: 복귀 시점
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: ①ROM 정상 ②양측 근력차 <10% ③무통 컴파운드 가능 ④2주 무통 유지. 4개 충족 후 복귀

**받는 정보**
- 측정 데이터

**내놓는 것**: 복귀 가능 여부

**예시**: 4개 체크리스트로 자동 복귀 판정

**별도 레이어**: 부상 이벤트 트리거

**함수 시그니처(제안)**
```python
def q03_운동_복귀_기준(
    측정_데이터,  # 측정 데이터
):
    """Q03: 운동 복귀 기준. 복귀 가능 여부"""
    ...  # 근거: https://bjsm.bmj.com/content/50/14/853
```

---

### Q04 — 요추 통증 단계별 프로토콜

- **데이터**: `workout_knowledge_base.csv` 141행 (ID `Q04`) → [`rules/Q04.yaml`](./rules/Q04.yaml)
- **근거**: NICE NG59 (2016/2020 surveillance) + Foster 2018 Lancet LBP series — [https://www.nice.org.uk/guidance/ng59](https://www.nice.org.uk/guidance/ng59) — ★★★
- **분류**: 부상 관리
- **시점**: 통증 발생 시 / 재활 단계별
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 급성 0~3일: 침상안정 회피, 통증 허용 범위 내 일상 활동 유지·통증 중심화 반응 보이는 자세(McKenzie 신전 우선) 탐색 | 아급성 3~14일: 그룹/개별 운동요법(스트레칭·근력·유산소·운동조절) 시작, 신경역동 운동·도수치료는 운동의 보조로만 | 복귀 14일~: 글루트·코어 활성화 후 힙힌지 재학습, 데드/스쿼트는 추정 1RM의 30%부터 주 +10% 이내 점진. 적색기(다리 양측 저림·안장마비·괄약근/배뇨이상·발열·암 병력 동반 통증·외상 후 통증)→즉시 의료기관 의뢰

**받는 정보**
- 통증 부위·강도(NPRS 0~10)·발생 동작·일수·다리 저림 유무

**내놓는 것**: 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유

**예시**: 사용자: '데드 110kg 후 허리 통증 NPRS 6, 어제 발생' → 출력: '급성기. 오늘은 가벼운 보행·골반 틸트·McKenzie 엎드려 신전 5×10회 시도. 데드/스쿼트 일시 중지. 3일 후 통증 NPRS 3 이하면 30kg(추정 1RM 30%)부터 RDL 재개. 다리 저림이 종아리 아래로 내려가거나 양측이면 의료기관 상담'

**별도 레이어**: 부상 이벤트 트리거

**함수 시그니처(제안)**
```python
def q04_요추_통증_단계별_프로토콜(
    통증_부위_강도_발생_동작_일수_다리_저림_유무,  # 통증 부위·강도(NPRS 0~10)·발생 동작·일수·다리 저림 유무
):
    """Q04: 요추 통증 단계별 프로토콜. 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유"""
    ...  # 근거: https://www.nice.org.uk/guidance/ng59
```

---

### Q05 — 어깨 임핀지·회전근개 통증(RCRSP) 단계별 프로토콜

- **데이터**: `workout_knowledge_base.csv` 142행 (ID `Q05`) → [`rules/Q05.yaml`](./rules/Q05.yaml)
- **근거**: Lewis 2016 Man Ther + Cools 2015 Braz J Phys Ther — [https://pubmed.ncbi.nlm.nih.gov/27083390/](https://pubmed.ncbi.nlm.nih.gov/27083390/) — ★★★
- **분류**: 부상 관리
- **시점**: 통증 발생 시 / 재활 단계별
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 급성 0~7일: 통증 유발 동작(오버헤드·behind-the-neck·딥 호리젠탈 어덕션) 회피, 통증 허용 ROM 내 진자운동·견갑 후퇴/하강 활성 | 아급성 1~6주: 점진적 근력부하(통증 NPRS≤4 허용)—외회전 강화(밴드 ER), 견갑 안정화(서라투스 펀치·로우), 후방관절낭 스트레칭(sleeper/cross-body), GIRD 교정 | 복귀 6주~: 어깨 압박 운동(벤치·OHP·풀업)을 추정 1RM 30%부터 점진(주 +10%), 오버헤드는 통증 0/10 + 외회전 좌우차 <10% 확인 후. 적색기(외상 후 거상 불가·진행성 위약·야간통+종괴·발열·상지 신경학적 결손)→정형외과 의뢰

**받는 정보**
- 통증 부위·강도(NPRS)·유발 동작·외상 유무

**내놓는 것**: 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유

**예시**: 사용자: '오버헤드 프레스 50kg 셋업 시 어깨 앞쪽 찌릿 NPRS 5' → 출력: '급성기. 오버헤드 1주 중지, behind-the-neck·업라이트 로우도 회피. 대신 풀업 행잉·진자운동·밴드 외회전 3×15. 1주 후 통증 감소 시 덤벨 OHP를 1RM 30%부터 재시작, 견갑 후퇴/하강 셋업 강조. 야간통이 심해지거나 팔 들 수 없으면 의뢰'

**별도 레이어**: 부상 이벤트 트리거

**함수 시그니처(제안)**
```python
def q05_어깨_임핀지_회전근개_통증_rcrsp_단계별_프로토콜(
    통증_부위_강도_유발_동작_외상_유무,  # 통증 부위·강도(NPRS)·유발 동작·외상 유무
):
    """Q05: 어깨 임핀지·회전근개 통증(RCRSP) 단계별 프로토콜. 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/27083390/
```

---

### Q06 — 무릎 PFPS(슬개대퇴 통증) 단계별 프로토콜

- **데이터**: `workout_knowledge_base.csv` 143행 (ID `Q06`) → [`rules/Q06.yaml`](./rules/Q06.yaml)
- **근거**: Powers 2017 BJSM consensus + Crossley 2016 BJSM Part 2 + Barton 2015 BJSM — [https://pubmed.ncbi.nlm.nih.gov/29109118/](https://pubmed.ncbi.nlm.nih.gov/29109118/) — ★★★
- **분류**: 부상 관리
- **시점**: 통증 발생 시 / 재활 단계별
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 급성 0~2주: 통증 유발 동작(딥 스쿼트·런지·계단 내려오기·오픈체인 레그익스텐션 90°→0°) 회피, 활동 수정·교육 우선 | 아급성 2~6주: 고관절(외전·외회전, 클램쉘·사이드 라잉 힙 어브덕션·몬스터 워크)+대퇴사두(미니 스쿼트 0~45°, 레그프레스 짧은 ROM) 복합 강화, 통증 NPRS≤3 허용. 단기 진통은 슬개골 테이핑 보조 가능 | 복귀 6주~: 스쿼트/런지 ROM을 통증 한도 내 점진 확장, 무게는 통증 무관 자세 가능 시 1RM 30%부터 주 +10%. 풀스쿼트는 통증 0/10 + 편측 근력차 <10% 확인 후. 적색기(외상 후 부종·잠김(locking)·이탈감·체중부하 불가·발적/발열)→정형외과 의뢰

**받는 정보**
- 통증 부위·강도(NPRS)·유발 동작·부종/잠김 유무

**내놓는 것**: 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유

**예시**: 사용자: '백스쿼트 80kg 바닥에서 무릎 앞쪽 통증 NPRS 5, 계단 내려올 때도 아픔' → 출력: '아급성기 진입. 풀ROM 스쿼트·계단 내려오기 2주 회피. 클램쉘 3×15·사이드 라잉 힙 어브덕션 3×15·미니 스쿼트(0~45°) 3×10·레그프레스 짧은 ROM 24kg(1RM 30%)부터. 4주 후 통증 NPRS≤2면 박스 스쿼트(평행)부터 점진 ROM 확장. 무릎 잠김/부종 새로 생기면 의뢰'

**별도 레이어**: 부상 이벤트 트리거

**함수 시그니처(제안)**
```python
def q06_무릎_pfps_슬개대퇴_통증_단계별_프로토콜(
    통증_부위_강도_유발_동작_부종_잠김_유무,  # 통증 부위·강도(NPRS)·유발 동작·부종/잠김 유무
):
    """Q06: 무릎 PFPS(슬개대퇴 통증) 단계별 프로토콜. 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유"""
    ...  # 근거: https://pubmed.ncbi.nlm.nih.gov/29109118/
```

---

### 메타 룰

운동 선택 단계에서 ‘어떤 종목을 쓸지’의 가중치 함수. 다른 룰의 입력값을 만든다.

**들어가는 룰**: F05

### F05 — SFR (자극/피로 비율)

- **데이터**: `workout_knowledge_base.csv` 67행 (ID `F05`) → [`rules/F05.yaml`](./rules/F05.yaml)
- **근거**: Israetel / RP — [https://www.strongerbyscience.com/exercise-selection/](https://www.strongerbyscience.com/exercise-selection/) — ★★☆
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 컴파운드 SFR 보통, 머신/아이솔 SFR 우수. 부상·피로 시 SFR 높은 운동으로 대체

**받는 정보**
- 부상 부위
- 피로 상태

**내놓는 것**: 대체 운동 후보 추천

**예시**: 무릎 통증 입력 → 백스쿼트 대신 레그프레스 추천

**들어가는 매트릭스 칸**: 세트별 처방(근육량 증가)
**별도 레이어**: 메타 룰

**함수 시그니처(제안)**
```python
def f05_sfr_자극_피로_비율(
    부상_부위,  # 부상 부위
    피로_상태,  # 피로 상태
):
    """F05: SFR (자극/피로 비율). 대체 운동 후보 추천"""
    ...  # 근거: https://www.strongerbyscience.com/exercise-selection/
```

---


## 부록 A — 매핑 미정 룰

매트릭스에도 별도 레이어에도 자동 매핑되지 않은 룰. `GAPS.md` §2 참고. 자료 추가 후 매핑 결정 필요.

### J01 — 부상별 대체 운동 매트릭스

- **데이터**: `workout_knowledge_base.csv` 87행 (ID `J01`) → [`rules/J01.yaml`](./rules/J01.yaml)
- **근거**: NASM / Israetel — [https://www.strongerbyscience.com/exercise-selection/](https://www.strongerbyscience.com/exercise-selection/) — ★★☆
- **분류**: 운동 선택
- **시점**: 세션 전
- **쓰임새**: 운동 추천, 지식베이스

**무슨 룰**: 무릎: 백스쿼트→레그프레스/벨트스쿼트. 어깨: 벤치→푸시업/덤벨프레스. 허리: 데드→힙쓰러스트/RDL. 손목: 백스쿼트→safety bar

**받는 정보**
- 부상 부위 입력

**내놓는 것**: 대체 운동 후보 리스트 출력

**예시**: 통증 입력 → 자동 운동 교체


**함수 시그니처(제안)**
```python
def j01_부상별_대체_운동_매트릭스(
    부상_부위_입력,  # 부상 부위 입력
):
    """J01: 부상별 대체 운동 매트릭스. 대체 운동 후보 리스트 출력"""
    ...  # 근거: https://www.strongerbyscience.com/exercise-selection/
```

---


## 부록 B — 함수 시그니처 인덱스 (개발자용)

ID 순. 코드에 옮길 때 import 표 대신 사용.

| ID | 분류 | 함수명 후보 | 받음 | 내놓음 |
|---|---|---|---|---|
| A01 | RPE 자율조절 | `a01_rpe_정의` | 사용자가 입력한 RPE (0~10) | RIR로 변환 → 다음 세트 보정의 기준값 |
| A02 | RPE 자율조절 | `a02_rpe_1rm_변환표` | 목표 RPE, 렙수, 사용자 1RM | 추천 무게 (kg) |
| A03 | RPE 자율조절 | `a03_fatigue_percent_피로_누적률` | 톱셋 무게/RPE, 백오프 세트 RPE | '운동 종료' 신호 또는 '한 세트 더' 신호 |
| A04 | RPE 자율조절 | `a04_rir_예측_정확도_보정` | 사용자 입력 RIR | 내부값 = 입력값 + 보정계수(0~+1) |
| A05 | RPE 자율조절 | `a05_자율조절_vs_고정` | 사용자 목표(근력/근비대) | 근력 목표 → 자율조절 우선, 근비대 → 볼륨 우선 알고리즘 분기 |
| A06 | RPE 자율조절 | `a06_omni_res_스케일` | 사용자 경험 레벨 | 대안 RPE 입력 UI 제공 |
| A07 | RPE 자율조절 | `a07_rts_generalized_rpe_렙_1rm_풀_매트릭스` | 목표 RPE, 목표 렙수, 사용자 1RM | 추천 무게 = 1RM × 셀(%) |
| A08 | RPE 자율조절 | `a08_rir_rpe_매핑_정의` | 사용자 입력 RPE | 내부 RIR 값으로 변환 → 다음 세트 무게 산출 입력 |
| A09 | RPE 자율조절 | `a09_rpe_변환표_정확도_검증_한계` | 사용자 경험 레벨, 종목 | 보정계수: 초보 ±5%p · 중급 ±3%p · 고급 ±2%p 신뢰구간 |
| A10 | RPE 자율조절 | `a10_종목_근육군별_변환_보정` | 운동 종목, 근육군 | 표 셀 결과 × 종목 보정계수 (스쿼트 1.00 / 벤치 1.00 / 데드 1.01 / 단관절 0.95) |
| A11 | RPE 자율조절 | `a11_세트_간_무게_보정_helms_룰` | 목표 RPE, 입력 RPE, 현재 무게 | 다음 세트 추천 무게 (kg) |
| A12 | RPE 자율조절 | `a12_세트_간_무게_보정_rts_룰` | 운동 종류(컴파운드/아이솔레이션), 렙수, RPE 차이 | 다음 세트 추천 무게 + 종료 트리거 |
| A13 | RPE 자율조절 | `a13_세션_간_rpe_drift_보정` | 최근 2~3 세션의 동일 운동 RPE 추이 | 다음 세션 무게 자동 조정 또는 디로드 권고 |
| A14 | RPE 자율조절 | `a14_강도_의존성_보정_85_1rm` | 현재 %1RM 추정치, 렙수 | 보정 폭 자동 조정 (5%/3%/2%) |
| B01 | 주간 볼륨 기준 | `b01_mv_유지_볼륨` | 근육군, 주차 | 유지기/디로드 주차 처방값 |
| B02 | 주간 볼륨 기준 | `b02_mev_성장_시작_볼륨` | 근육군 | 메조사이클 1주차 볼륨 시작값 |
| B03 | 주간 볼륨 기준 | `b03_mav_최적_적응_볼륨` | 현재 주 볼륨, 진행 주차 | 다음 주 볼륨 = 이번 주 + 1~2세트 |
| B04 | 주간 볼륨 기준 | `b04_mrv_회복_가능_최대_볼륨` | 근육군별 누적 주간 볼륨 | MRV 도달 + 수행도 하락 시 디로드 자동 권고 |
| B05 | 주간 볼륨 기준 | `b05_volume_dose_response_메타` | 사용자 목표(근비대) | 주당 권장 볼륨 자동 처방 (12~20세트) |
| C01 | 세트/렙/강도 처방 | `c01_nsca_rm_1rm_표` | 목표 렙수, 1RM | 추천 무게 (kg) |
| C02 | 세트/렙/강도 처방 | `c02_repetition_continuum` | 사용자 목표 | 렙범위 + %1RM 자동 매핑 |
| C03 | 세트/렙/강도 처방 | `c03_nsca_단계별_처방` | 훈련 단계 | 세트수+렙수+강도 처방 |
| C04 | 세트/렙/강도 처방 | `c04_acsm_일반인_가이드라인` | 사용자 프로필(건강 목적) | 초보·일반인 디폴트 처방 |
| C05 | 세트/렙/강도 처방 | `c05_실패_vs_rir` | 운동 종류 | 컴파운드 RIR 2~3 / 아이솔레이션 RIR 0~2 디폴트 |
| C06 | 세트/렙/강도 처방 | `c06_훈련_빈도` | 주간 볼륨, 분할 형태 | 근육군당 최소 주 2회 분할 권장 |
| C07 | 세트/렙/강도 처방 | `c07_휴식_시간` | 운동 종류, 목표 | 휴식 타이머 자동 카운트다운 |
| C08 | 세트/렙/강도 처방 | `c08_double_progression` | 지난 세션 모든 세트 성공 여부 | 다음 세션 무게 자동 인상 또는 유지 |
| C09 | 세트/렙/강도 처방 | `c09_epley_1rm_공식` | 무게, 렙수 | 추정 1RM |
| C10 | 세트/렙/강도 처방 | `c10_brzycki_1rm_공식` | 무게, 렙수(저렙) | 추정 1RM |
| C11 | 세트/렙/강도 처방 | `c11_세션_길이_가이드` | 가용 시간, 분할 | 세션 운동 수/세트 수 자동 조정 |
| C12 | 세트/렙/강도 처방 | `c12_마지막_세트만_미달_top_set_drop_off` | 세트별 목표렙 vs 실제렙, 미달 세트 위치 | 다음 세션 무게 동일, 부족분 다음 세션에 회수 시도 |
| C13 | 세트/렙/강도 처방 | `c13_모든_세트_동일_미달_stall_1회차` | 세트별 미달 횟수, 연속 stall 주차 | 무게·렙 유지, 1주 재시도. 수면/영양/스트레스 체크 프롬프트 |
| C14 | 세트/렙/강도 처방 | `c14_2주_3세션_연속_미달_reset_10` | 연속 stall 세션 수, 직전 작업 무게 | 무게 ×0.9, 4~6주에 걸쳐 직전 PR 회복 후 초과 시도 |
| C15 | 세트/렙/강도 처방 | `c15_double_progression_미달_처리_보강` | 직전 세션 렙, 레인지 하한 미달 횟수 | 무게 유지/감량 자동 분기, 누적 후 다음 세션 +1렙 시도 |
| D01 | 주기화 모델 | `d01_linear_periodization` | 사용자 레벨, 진행 주차 | 주차별 변수 자동 변경 |
| D02 | 주기화 모델 | `d02_daily_undulating_dup` | 사용자 레벨(중·고급) | 요일별 변수 다른 처방 |
| D03 | 주기화 모델 | `d03_block_periodization` | 사용자 레벨(고급) | 블록당 1개 적응 우선 |
| D04 | 주기화 모델 | `d04_flexible_dup` | 당일 사용자 컨디션 입력 | 오늘 비대/근력/파워 중 추천 |
| D05 | 주기화 모델 | `d05_분할_루틴_비교` | 가용 일수, 사용자 레벨 | 권장 분할 형태 자동 매핑 |
| D06 | 주기화 모델 | `d06_starting_strength_5x5_5x3` | 사용자 레벨(초보), 1RM | 프로그램 처방 (월수금 A/B 교대) |
| D07 | 주기화 모델 | `d07_5_3_1_wendler` | 사용자 레벨(중급), 1RM | 4주 처방 자동 생성 |
| D08 | 주기화 모델 | `d08_gzclp` | 사용자 레벨, 1RM | 프로그램 처방 |
| D09 | 주기화 모델 | `d09_nsuns_lp` | 사용자 레벨(중급+) | 프로그램 처방 |
| D10 | 주기화 모델 | `d10_phul_phat_하이브리드` | 사용자 레벨(중급+) / 목표(파워+근비대) | 분할 처방 |
| D11 | 주기화 모델 | `d11_초보자_빅3_ohp_디폴트_시작_무게_남성` | 성별=남, 운동 경험=없음, 바벨 종류=20kg 표준 | 스쿼트/벤치/OHP 20kg, 데드리프트 40kg 첫 세트 |
| D12 | 주기화 모델 | `d12_초보자_빅3_ohp_디폴트_시작_무게_여성` | 성별=여, 운동 경험=없음, 바벨 종류=15kg 또는 20kg | 스쿼트/벤치/OHP 15~20kg, 데드리프트 30~40kg |
| D13 | 주기화 모델 | `d13_빈_바벨로_시작하는_원칙` | 운동 종목, 목표 워크셋 무게 | 빈 바 → 50% → 70% → 90% → 100% 분할 제안 |
| D14 | 주기화 모델 | `d14_초보자_첫_세션_워크셋_상한_가이드` | 성별, 체중, 훈련 이력 | 첫 워크셋 상한 65kg(스쿼트, 평균 체중 남성 기준)로 클램프 |
| D15 | 주기화 모델 | `d15_초보자_증량_폭_점프_디폴트` | 직전 세션 성공/실패, 운동 종목 | 다음 세션 무게 자동 계산 |
| E01 | 실시간 코칭 | `e01_vbt_속도_기반_훈련` | 바벨 속도 데이터(센서/카메라) | 실시간 피로 알림·1RM 추정 |
| E02 | 실시간 코칭 | `e02_load_velocity_profile` | 워밍업 세트 무게/속도 | 당일 1RM 추정 → 무게 자동 보정 |
| E03 | 실시간 코칭 | `e03_velocity_loss_임계` | 렙별 속도, 목표 | 속도 감소 임계 도달 시 세트 강제 종료 |
| E04 | 실시간 코칭 | `e04_실시간_피드백_효과` | 세트 데이터 | 세트 후 시각적 피드백 표시 |
| E05 | 실시간 코칭 | `e05_external_vs_internal_큐` | 운동명·동작 단계 | 운동별 외적 큐 텍스트/음성 출력 |
| E06 | 실시간 코칭 | `e06_스쿼트_폼_에러_큐` | 폼 분석(영상/사용자 보고) 결과 | 에러 → 큐 매핑 출력 |
| E07 | 실시간 코칭 | `e07_벤치프레스_폼_큐` | 운동명·셋업 단계 | 셋업 체크리스트·큐 출력 |
| E08 | 실시간 코칭 | `e08_데드리프트_폼_큐` | 운동명·셋업 단계 | 셋업 체크리스트·큐 출력 |
| E09 | 실시간 코칭 | `e09_ramp_워밍업_프로토콜` | 메인 운동, 작업 무게 | 워밍업 시퀀스 자동 생성 |
| E10 | 실시간 코칭 | `e10_오버헤드프레스_폼_큐` | 운동명·셋업 단계 | 셋업 체크리스트·외적 큐 출력 |
| E11 | 실시간 코칭 | `e11_풀업_친업_폼_큐` | 운동명·셋업 단계 | 셋업 체크리스트·큐 출력 |
| E12 | 실시간 코칭 | `e12_바벨_로우_폼_큐` | 운동명·셋업 | 셋업 체크리스트·큐 출력 |
| E13 | 실시간 코칭 | `e13_valsalva_호흡` | 무게 비율, 운동 종류 | 호흡 큐 자동 출력 |
| E14 | 실시간 코칭 | `e14_가동범위_rom_기준` | 운동명, 사용자 ROM 데이터 | ROM 부족 시 큐 출력 |
| E15 | 실시간 코칭 | `e15_부상_신호_vs_근육통` | 사용자 통증 위치/강도/시점 | 운동 중단 권고 또는 정상 신호 분기 |
| E16 | 실시간 코칭 | `e16_컴파운드_셋업_체크리스트` | 운동명 | 단계별 체크리스트 UI |
| E17 | 실시간 코칭 | `e17_그립_너비_유형` | 운동명, 목표 근육 | 권장 그립 너비/유형 출력 |
| F05 | 운동 선택 | `f05_sfr_자극_피로_비율` | 부상 부위, 피로 상태 | 대체 운동 후보 추천 |
| G01 | 회복/디로드 | `g01_디로드_정의_주기` | 주차 누적, 사용자 입력 | 4~6주마다 자동 디로드 주차 스케줄 |
| G02 | 회복/디로드 | `g02_디로드_트리거_자동_감지` | 최근 3+ 세션 RPE drift, 수면, 통증 | 디로드 권고 알림 |
| G03 | 회복/디로드 | `g03_디로드_처방_방법` | 현재 주간 처방 | 디로드 주차 처방값 자동 생성 |
| G04 | 회복/디로드 | `g04_주간_부하_10_룰_부상_예방` | 이번주 vs 지난주 총볼륨 | 초과 시 경고/상한 적용 |
| G05 | 회복/디로드 | `g05_디로드_주_볼륨_강도_정량_처방` | 직전 주 세트 수, 평균 무게, 훈련 빈도 | 디로드 주 처방: 세트 수 ½, 무게 90~100% 유지, 같은 분할 |
| G06 | 회복/디로드 | `g06_고피로_시_강도까지_동시_감축` | 누적 피로 신호(관절통·수면·동기 점수) | 강도 감축 여부 결정: 일반=무게 유지 / 고피로=무게 50% |
| G07 | 회복/디로드 | `g07_디로드_트리거_신호_다지표_자동` | 주간 RPE 추이, 수면, 통증 NPRS, 동기 점수 | "디로드 권고" 알림 + 다음 주 처방 자동 G05/G06으로 전환 |
| G08 | 회복/디로드 | `g08_mrv_도달_시_강제_디로드` | 부위별 누적 세트, RPE drift, 주차 카운터 | 다음 주 G05 처방 강제 + 다음 메조는 MEV(10~12세트)에서 재시작 |
| G09 | 회복/디로드 | `g09_활성_디로드_vs_완전_휴식_선택` | 부상 여부, 번아웃 척도, 수면 평균 | "활성"(권장) 또는 "패시브 1주" 선택 후 처방 분기 |
| G10 | 회복/디로드 | `g10_한국_사용자_디로드_주기_기본값` | 사용자 레벨, 메조 시작 주차 | 5주차 종료 후 "다음 주 디로드 추천" 푸시 + G05 처방 미리 채움 |
| G11 | 회복/디로드 | `g11_미달_누적_디로드_트리거` | 주간 stall 리프트 수, 평균 RPE | 다음 주 디로드 프로그램 자동 처방 후 재진입 |
| I01 | 기타 | `i01_초보자_linear_progression` | 사용자 레벨 | 초보면 단순 LP 룰 사용 |
| I02 | 기타 | `i02_tempo_notation` | 운동 처방 템포 | 세트 내 메트로놈/비프음 코칭 |
| I03 | 기타 | `i03_운동_순서_컴파운드_우선` | 세션 운동 목록 | 세션 내 운동 순서 자동 정렬 |
| I04 | 기타 | `i04_acwr_급성_만성_부하비` | 최근 7일/28일 볼륨 | 위험 구간 진입 시 알림 |
| I05 | 기타 | `i05_일반_워밍업_전신_체온_상승` | 사용자 첫 메인 운동, 가용 시간 | 5~10분 저강도 유산소 권장(땀 살짝 날 정도) |
| I06 | 기타 | `i06_특이적_워밍업_워크업_세트_컴파운드` | 본 세트 무게(kg), 종목(스쿼트/벤치/데드/프레스) | 빈 봉 2세트 + 40/60/80% 워크업 자동 계산 |
| I07 | 기타 | `i07_특이적_워밍업_아이솔레이션_머신` | 종목 유형(아이솔레이션/머신), 본 세트 무게 | 1~2 워크업 세트 권장 (50%×8, 80%×3) |
| I08 | 기타 | `i08_무거운_워크업_우선_권고_시간_부족_시` | 사용 가능 시간, 본 세트 무게 | 3세트 못할 시 80%×3~5만 1세트 권장 |
| J01 | 운동 선택 | `j01_부상별_대체_운동_매트릭스` | 부상 부위 입력 | 대체 운동 후보 리스트 출력 |
| J02 | 운동 선택 | `j02_장비별_대체_운동` | 사용자 장비 환경 | 운동 라이브러리 필터링 |
| J03 | 운동 선택 | `j03_자유중량_vs_머신` | 사용자 목표/환경/경험 | 운동 풀 분기 |
| J04 | 운동 선택 | `j04_편측_vs_양측_운동` | 사용자 불균형 데이터 | 운동 선택 비율 조정 |
| J05 | 운동 선택 | `j05_컴파운드_아이솔_비율` | 사용자 레벨, 약점 부위 | 세션 운동 구성 비율 |
| J07 | 운동 선택 | `j07_근육군_매핑_primary_secondary` | 운동 ID | 근육군별 가중 볼륨 카운트 |
| K01 | 영양 | `k01_단백질_섭취량` | 체중, 목표(벌크/컷/유지) | 일일 단백질 g 알림 |
| K02 | 영양 | `k02_칼로리_가이드` | 체중, 활동량, 목표 | 일일 칼로리 처방 |
| K03 | 영양 | `k03_탄수화물_타이밍` | 세션 시각, 체중 | 식사 타이밍 권고 |
| K04 | 영양 | `k04_수분_가이드` | 체중, 세션 시간 | 수분 섭취 알림 |
| K05 | 회복 | `k05_수면_근비대_관계` | 수면 시간 입력 | 수면 부족 시 강도 자동 하향 |
| K06 | 회복 | `k06_수면_부족_부상_위험` | 수면 데이터, 훈련 부하 | 부상 위험 알림 |
| K07 | 회복 | `k07_능동_회복_active_recovery` | 사용자 피로도 | 능동 회복 처방 |
| K08 | 회복 | `k08_근육통_doms_관리` | 통증 시작 시점, 강도 | 정상/이상 분류 |
| K09 | 보충제 | `k09_크레아틴_모노하이드레이트` | 사용자 보충제 사용 여부 | 크레아틴 권장 |
| K10 | 보충제 | `k10_카페인` | 체중, 세션 시각 | 카페인 양/타이밍 처방 |
| K11 | 보충제 | `k11_베타알라닌` | 사용자 목표(고렙/지구력) | 권장 여부 |
| K12 | 영양 | `k12_한식_주식_곡류_단백질_환산` | 섭취 식품·양 (한식 단위) | 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력 |
| K13 | 영양 | `k13_한식_단백질_반찬_환산` | 섭취 식품·양 (한식 단위) | 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력 |
| K14 | 영양 | `k14_한식_국_찌개_단백질_환산` | 섭취 식품·양 (한식 단위) | 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력 |
| K15 | 영양 | `k15_분식_외식_단백질_환산` | 섭취 식품·양 (한식 단위) | 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력 |
| K16 | 영양 | `k16_편의점_간편식_단백질_환산` | 섭취 식품·양 (한식 단위) | 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력 |
| K17 | 영양 | `k17_한국_단백질_보충_식품_환산` | 섭취 식품·양 (한식 단위) | 단백질 g 환산값 → 일일 단백질 목표(K01) 달성률 계산 입력 |
| K18 | 영양 | `k18_한식_1회_제공량_표준_단위_환산_룰` | 사용자 입력 (예: '밥 한 공기·치킨 두 조각') | 정량 g → K12~K17 환산표 자동 매칭 |
| K19 | 영양 | `k19_mifflin_st_jeor_bmr_공식_1순위` | 성별, 체중(kg), 키(cm), 나이(년) | BMR (kcal/일) — 활동계수 곱하기 전 기초대사량 |
| K20 | 영양 | `k20_katch_mcardle_bmr_공식_체지방률_알_때` | 체중(kg), 체지방률(%) | BMR (kcal/일) — 제지방량 기반 |
| K21 | 영양 | `k21_활동계수_pal_표_tdee_산출` | BMR(kcal), 활동 카테고리(5단계) | TDEE (kcal/일) — 일일 총 에너지 소비량 |
| K22 | 영양 | `k22_활동_카테고리_한국_사용자_매핑` | 직업 유형, 주당 운동 빈도, 운동 강도(RPE) | 5단계 중 1개 카테고리 자동 선택 |
| K23 | 영양 | `k23_추정식_정확도_한계_재측정_권장` | 2주 평균 칼로리, 2주 체중 변화(kg) | TDEE 보정값 = 입력칼로리 ± (체중변화×7700/14) |
| L02 | 특수 모집단 | `l02_노인_50_sarcopenia_대응` | 사용자 연령 | 노인용 처방 분기 |
| L03 | 특수 모집단 | `l03_청소년_가이드라인` | 사용자 연령 | 청소년용 처방 분기 |
| L04 | 특수 모집단 | `l04_초보_중급_고급_정의` | 훈련 기간, 1RM 비율 | 레벨 분류 |
| L05 | 특수 모집단 | `l05_제2형_당뇨_운동_처방` | 진단명(제2형 당뇨), 복용 약물(인슐린·SU·메트포르민 등), 합병증(망막증/신증/신경병증/족부), HbA1c·공복혈당, 운동 가능 시간 | FITT 권고(유산소 분/주·저항 회/주) + 회피 운동 리스트 + RPE 상한 + 운동 전후 혈당 모니터링 항목 + 의뢰 트리거 분기 |
| L06 | 특수 모집단 | `l06_고혈압_운동_처방` | 진단명(고혈압 1·2기), 복용 약물(β-차단제·이뇨제·ACEi·ARB·CCB), 안정시 BP 최근치, 동반질환(CVD/당뇨) | FITT 권고 + Valsalva 회피 안내 + RPE 상한(저항 RPE6) + 약물별 주의사항 + 의뢰 트리거 + 운동 중 BP 모니터링 권고 |
| L07 | 특수 모집단 | `l07_이상지질혈증_대사증후군_운동_처방` | 진단명(이상지질혈증·대사증후군), 지질 패널(LDL/HDL/TG), 복용 약물(스타틴·에제티미브·페노피브레이트), 동반질환, BMI/허리둘레 | FITT 권고 + 주 칼로리 소비 목표 + 동반질환 시 L05/L06 규칙 중복 적용 + 의뢰 트리거 |
| L08 | 특수 모집단 | `l08_골관절염_무릎_고관절_운동_처방` | 진단명(무릎/고관절 OA), 통증 NRS(0~10), 발병 부위, 동반질환(GI·CV), 보행/계단 가능 여부, BMI | FITT 권고(통증 NRS 기반 강도 캡) + 회피 동작 리스트 + 수중운동/태극권 옵션 + 정형외과 의뢰 트리거 |
| M01 | 측정/평가 | `m01_체성분_측정_도구` | 사용자 측정 환경 | 측정 도구 권장 |
| M03 | 측정/평가 | `m03_1rm_측정_방법` | 사용자 레벨, 위험 허용도 | 측정 방법 분기 |
| M04 | 측정/평가 | `m04_체중_대비_초보_무게_표준_untrained` | 성별, 체중 | 사용자 시작 무게가 Untrained 범위 내인지 검증 / 과대 입력 차단 |
| N01 | 생리학 | `n01_근비대_3_메커니즘` | - | 처방 알고리즘 가중치 |
| N02 | 생리학 | `n02_신경_적응_vs_근비대_적응` | 훈련 기간 | 사용자 기대값 조정 |
| N03 | 생리학 | `n03_운동_호르몬_반응` | - | 사용자 교육 콘텐츠 |
| N04 | 생리학 | `n04_근섬유_타입_type_i_ii` | - | 렙범위 권장 폭 확장 |
| O01 | 카디오 | `o01_근력_유산소_간섭효과` | 사용자 카디오 빈도/시간 | 간섭 위험 평가 |
| O02 | 카디오 | `o02_hiit_vs_liss` | 사용자 가용 시간, 회복 상태 | 카디오 종류 추천 |
| O03 | 카디오 | `o03_카디오_타이밍` | 세션 구성 | 카디오 배치 추천 |
| P01 | 스트레칭 | `p01_운동_전_스트레칭_정_동적` | 세션 시점 | 워밍업 시퀀스 제외/포함 |
| P02 | 스트레칭 | `p02_pnf_스트레칭` | 사용자 환경 | PNF vs 일반 스트레칭 분기 |
| P03 | 스트레칭 | `p03_자가근막이완_smr_폼롤러` | 세션 시점 | 폼롤러 시퀀스 |
| P04 | 스트레칭 | `p04_관절_모빌리티_워크` | 폼 분석 결과 | 부위별 모빌리티 처방 |
| P05 | 스트레칭 | `p05_정적_스트레칭_회피_워밍업_시` | 사용자의 워밍업 루틴 입력 | 정적 스트레칭 감지 시 동적(레그스윙·아키바이크)으로 대체 안내 |
| Q01 | 부상 관리 | `q01_급성_부상_처치_peace_love` | 부상 시점, 부위 | 단계별 가이드 |
| Q02 | 부상 관리 | `q02_부상_복귀_단계` | 부상 단계, 통증 점수 | 다음 단계 진행 여부 |
| Q03 | 부상 관리 | `q03_운동_복귀_기준` | 측정 데이터 | 복귀 가능 여부 |
| Q04 | 부상 관리 | `q04_요추_통증_단계별_프로토콜` | 통증 부위·강도(NPRS 0~10)·발생 동작·일수·다리 저림 유무 | 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유 |
| Q05 | 부상 관리 | `q05_어깨_임핀지_회전근개_통증_rcrsp_단계별_프로토콜` | 통증 부위·강도(NPRS)·유발 동작·외상 유무 | 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유 |
| Q06 | 부상 관리 | `q06_무릎_pfps_슬개대퇴_통증_단계별_프로토콜` | 통증 부위·강도(NPRS)·유발 동작·부종/잠김 유무 | 단계 분류 + 허용/회피 운동 리스트 + 재시작 무게 % + 의뢰 사유 |
| R01 | 행동 코칭 | `r01_smart_목표_설정` | 사용자가 입력한 목표 문장 + 현재 1RM/체중/주당 운동 횟수 | SMART 5요소 누락 항목 자동 점검 → 12주 단위 도전적 수치 목표로 재작성 (예: '벤치 80→90kg, 12주, 주 3회 5x5') |
| R02 | 행동 코칭 | `r02_습관_형성_평균_66일` | 사용자의 운동 시작일 + 주당 출석 기록 | D+0~66일은 "습관 형성 구간"으로 표시. 매일 같은 시간·장소 권고. 1~2회 빼먹어도 자동화 곡선에 거의 영향 없음을 안내(과도한 죄책감 차단) |
| R03 | 행동 코칭 | `r03_자기효능감_4가지_원천` | 사용자의 PR(개인 최고기록) 갱신 이력 + 출석 연속 일수 | 매주 작은 PR(중량·반복·세트)을 시각화해 "숙달 경험" 누적을 보여줌. 정체기에는 비슷한 체급 사용자 진척 사례(대리 경험) 제시 |
| R04 | 행동 코칭 | `r04_자율적_동기_자율성_유능감_관계성` | 사용자의 프로그램 수행률 + 자율 선택 비율(추천 vs 직접 선택) | 운동 종목·세트 수를 강제하지 않고 "오늘 컨디션상 80% / 100% / 110% 중 선택" 식 옵션 제공. 매주 1회 진척 그래프로 유능감 피드백 |
| R05 | 행동 코칭 | `r05_첫_6개월_이탈률` | 사용자 가입일 + 최근 14일 출석 횟수 | D+0~180일 사용자는 "고위험 코호트"로 분류. 출석 5일 공백 시 푸시 알림 + 운동 강도 -20% 조정안 제시(부담 차단) |
| R06 | 행동 코칭 | `r06_정체기_심리_대응` | 최근 4~6주 PR 갱신 여부 + 주관적 피로(RPE 추세) | 4주 정체 + RPE 평균 ≥8 → 자동 "디로드 1주" 권고. 정체기 카드에 "중량은 멈췄지만 출석률·폼·총 볼륨은 +15%" 식 비-중량 진척 표기 |
| R07 | 행동 코칭 | `r07_사회적_지지_운동_파트너_효과` | 사용자의 운동 파트너 유무 + 그룹/챌린지 참여 여부 | 파트너 부재 시 "함께하기" 기능(친구 초대·앱 내 챌린지 매칭) 노출. 그룹 출석 시 개인 출석 가중 +1로 시각화 |
| R08 | 행동 코칭 | `r08_외부_보상_vs_내재_동기_crowding_out` | 사용자가 운동을 ""재미있다""고 답한 빈도 + 보상 시스템 노출 여부 | 흥미·자율 동기가 이미 높은 사용자에게는 금전·뱃지 보상 노출 최소화. 대신 진척 데이터·개선 피드백 위주로 표시 |
| R09 | 행동 코칭 | `r09_운동_강박_red_s_스크리닝` | 주당 운동 시간 + 식사 빈도/총 칼로리 + (여성) 월경 주기 + 휴식기 심박 | 위험 신호 ≥3개 발견 시 "운동량 -30% 권고 + 의료/영양 전문가 상담 안내" 카드 표시. 챗봇은 진단·처방 금지(의료법 회피), "스포츠의학 전문의 상담을 권합니다"로 한정 |
| R10 | 행동 코칭 | `r10_한국_직장인_시간_충돌_회식_대응` | 사용자의 근무 형태 + 회식 일정(캘린더 연동) + 주당 운동 가능 일수 | 회식 캘린더 감지 시: 당일은 휴식 권고 + 익일은 "20분 압축 루틴"(메인 운동 3개 5x5만) 자동 제안. 주간 볼륨 -10~15% 자동 조정으로 미달 보강 |