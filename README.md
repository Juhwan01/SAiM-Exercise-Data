<div align="center">

# SAiM Exercise Data

**근거 기반 운동 코칭을 위한 통합 지식베이스**

153개의 검증된 룰 · 449개 운동 풀 · 5목표 × 7모듈 매트릭스

[![Rules](https://img.shields.io/badge/rules-153-1f6feb)](./RULEBASE.md)
[![Cards](https://img.shields.io/badge/rule_cards-153_yaml-2da44e)](./rules/)
[![DSL](https://img.shields.io/badge/DSL-spec-8957e5)](./DSL.md)
[![Exercises](https://img.shields.io/badge/exercises-449-2da44e)](./exercise_library.csv)
[![Sources](https://img.shields.io/badge/sources-1차_검증-brightgreen)](#출처-정책)
[![License](https://img.shields.io/badge/license-private-d1242f)](#라이선스)

[자세한 활용 가이드 →](./GUIDE.md)

</div>

---

## TL;DR — 어디로 갈까

| 무엇을 하고 싶은가 | 어디로 |
|---|---|
| 룰 전체를 한눈에 보고 싶다 | [`RULEBASE.md`](./RULEBASE.md) |
| 룰 한 장씩 카드로 보고 싶다 | [`rules/`](./rules/) 폴더 (분류별 인덱스 있음) |
| 룰 형식이 어떻게 생겼는지 알고 싶다 | [`DSL.md`](./DSL.md) |
| 자료 부족한 부분이 어디인지 보고 싶다 | [`GAPS.md`](./GAPS.md) |
| 새 행을 추가하려고 한다 | [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) (마스터) |
| 자세한 활용 가이드를 원한다 | [`GUIDE.md`](./GUIDE.md) |

---

## 한 줄 요약

> 운동 코칭 앱이 사용자에게 **어떤 판단을, 어떤 근거로** 내릴지 모아둔 룰베이스. 모든 룰은 NSCA·ACSM·Helms·Schoenfeld 등 1차 출처에서 가져왔고, 신뢰도 별점(★~★★★)이 붙어 있다. 마스터 CSV(153행)가 진실의 원천이고, 사람이 읽는 카탈로그(`RULEBASE.md`)와 앱이 읽는 룰 카드(`rules/*.yaml`)가 그 파생물이다.

---

## 메인 산출물 (먼저 보세요)

| 파일 | 무엇 | 누가 보면 됨 |
|---|---|---|
| **[`RULEBASE.md`](./RULEBASE.md)** | 5목표 × 7모듈 매트릭스 + 모든 룰 본문 + 부록 | **사람이 읽는 메인 문서** — PM, 트레이너, 검수자 |
| **[`rules/*.yaml`](./rules/)** | 153개 정형 룰 카드 (한 행 → 한 카드) | **앱/엔진이 읽는 단위** — 백엔드 개발자 |
| **[`DSL.md`](./DSL.md)** | 룰 한 장이 어떤 형식으로 적히는지 정의 | 룰을 추가/수정할 모든 사람 |
| **[`GAPS.md`](./GAPS.md)** | 자료 빈틈 리포트 (셀별 카운트·신뢰도 분포·미등록 ID) | 보강 우선순위 잡을 때 |
| **[`workout_knowledge_base.csv`](./workout_knowledge_base.csv)** | 153행 마스터. **진실의 원천** | 행을 추가할 때만 직접 편집 |

> 위 5개가 룰베이스의 핵심입니다. 나머지(goal_*.csv, output/, exercise_*.csv)는 모두 마스터에서 파생된 보조 파일.

---

## 목차

- [어떤 자료인가요](#어떤-자료인가요)
- [어떻게 활용하나요](#어떻게-활용하나요)
- [Quick Start (역할별)](#quick-start-역할별)
- [데이터 구조](#데이터-구조)
- [자료 통계](#자료-통계)
- [디렉터리 구조](#디렉터리-구조)
- [핵심 원칙](#핵심-원칙)
- [출처 정책](#출처-정책)
- [변경 이력](#변경-이력)
- [라이선스](#라이선스)

---

## 어떤 자료인가요

운동 앱이 사용자에게 무엇을 추천할지 결정할 때 참고할 **룰 카탈로그**입니다. 각 룰은 한 줄로 압축되어 있고, 클릭하면 1차 출처(논문·교과서·검증된 코치 글)로 바로 이동합니다.

**구성**

| 축 | 내용 |
|---|---|
| **5운동목표** | 다이어트 · 벌크업 · 스트렝스 · 근육량 증가 · 건강증진 |
| **7모듈** | 온보딩 → 세션 시작 → 세트별 처방 → 세트 후 학습 → 메조사이클 관리 → 영양·회복 → 행동·안전 |
| **별도 레이어** | 모집단 분기(노인·청소년·만성질환) · 부상 이벤트 트리거 · 메타 룰(SFR) |

**18개 분류** (괄호는 풀어 쓴 한국어)

| 분류 | 한 줄 설명 |
|---|---|
| RPE 자율조절 | 체감 난이도(0~10)로 무게 자동 조절 |
| 주간 볼륨 기준 | 근육군당 주간 세트 수의 4단계 기준 |
| 세트/렙/강도 처방 | 목표별 적정 횟수·강도 변환표 |
| 주기화 모델 | 여러 주에 걸친 무게 진행 방식 (LP/DUP/블록 등) |
| 실시간 코칭 | 운동 중 즉시 피드백 (자세 큐·호흡·ROM) |
| 운동 선택 | 부상·장비별 대체 운동·종목 선정 |
| 측정/평가 | 1RM·체성분·시작 무게 측정 방법 |
| 회복 / 회복·디로드 | 쉬어가는 주(디로드) 처방·자동 감지 |
| 영양 / 보충제 | 칼로리·단백질·수분·크레아틴·카페인·한식 환산 |
| 생리학 | 근비대 메커니즘·신경 적응 등 배경 지식 |
| 부상 관리 | 급성 처치·통증 단계별 프로토콜 |
| 스트레칭 | 정적·동적·PNF·폼롤러·모빌리티 |
| 카디오 | 유산소 간섭·HIIT vs LISS·타이밍 |
| 특수 모집단 | 노인·청소년·당뇨·고혈압 등 안전 필터 |
| 행동 코칭 | 동기·습관·이탈·한국 직장인 환경 |
| 기타 | 워밍업·템포·운동 순서 등 |

---

## 어떻게 활용하나요

### 사용 시나리오

| 누가 | 무엇을 하려고 | 어떤 파일을 보면 됨 |
|---|---|---|
| 기획팀 / PM | 룰 전체를 한눈에 보고 의사결정 | [`RULEBASE.md`](./RULEBASE.md) |
| 트레이너 / 도메인 검수 | 출처 검증, 룰 추가/수정 제안 | [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) |
| 백엔드 / 룰엔진 개발자 | 정형 룰 한 장씩 import | [`rules/*.yaml`](./rules/) + [`DSL.md`](./DSL.md) |
| DB 시드 작업자 | 마스터 한 번에 import | [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) |
| 챗봇 / RAG 개발자 | 출처가 붙은 답변 생성 | [`goal3_knowledge_base.csv`](./goal3_knowledge_base.csv) + [`rules/`](./rules/) |
| 협업 시트 작업자 | Google Sheets에 그대로 붙여넣기 | [`output/sheet_*.tsv`](./output/) |
| 자료 보강 우선순위 잡을 때 | 빈 셀·미등록 ID·신뢰도 분포 확인 | [`GAPS.md`](./GAPS.md) |

> **상세 가이드는 [`GUIDE.md`](./GUIDE.md)에 있습니다.** 역할별 진입점, 파일별 컬럼 설명, 7가지 실전 시나리오, FAQ, 용어집까지 포함.

---

## Quick Start (역할별)

### "5분 만에 자료 파악하고 싶다"

```
1. RULEBASE.md 열기 (큰 문서라 1~3초 기다리세요)
2. 상단 ## 2 매트릭스에서 (목표 × 모듈) 칸 하나 골라 점프
3. 룰 옆 [ID★URL] 클릭하면 1차 출처로 이동
```

### "룰 한 장이 어떻게 생겼는지 보고 싶다"

```
1. rules/ 폴더로 가면 README가 분류별 인덱스를 보여줌
2. 관심 있는 ID(예: A11) 클릭 → yaml 카드 한 장
3. 카드의 14개 필드가 무엇을 뜻하는지는 DSL.md §2에서 확인
```

### "Google Sheets에 붙여넣고 싶다"

```
1. output/sheet_운동 루틴 세션.tsv 열기
2. 전체 복사
3. Sheets 해당 탭 A3 클릭 → 붙여넣기
4. 4열 자동 분리: 빈칸 / 내용 / 출처 / URL
```

### "앱에 import 하고 싶다"

```python
import yaml, glob
rules = {}
for f in glob.glob("rules/*.yaml"):
    card = yaml.safe_load(open(f))
    rules[card["ID"]] = card
# 153개 룰 카드. 카드별 "필요한_정보" / "하는_일" / "적용_위치" 구조
```

또는 마스터를 통째로:

```python
import pandas as pd
df = pd.read_csv("workout_knowledge_base.csv")
# 153행 × 14열. ID 컨벤션은 알파벳 prefix (A*=RPE, B*=볼륨, ...)
```

### "사용자 화면 문구가 필요하다"

```python
import json
rewrites = json.load(open(".scripts/rewrites.json"))
# 마스터 ID → 평이한 한국어 매핑. jargon 0%
```

---

## 데이터 구조

### 마스터 CSV 스키마

`workout_knowledge_base.csv` (153행 × 14열)

| 컬럼 | 설명 |
|---|---|
| `ID` | 고유 식별자 (분류별 알파벳 prefix) |
| `분류` | 18개 분류 중 하나 |
| `항목` | 룰 제목 |
| `적용 시점` | 언제 이 룰을 발동시킬지 |
| `운동 추천` | Y/- (goal1 분기 플래그) |
| `실시간 코칭` | Y/- (goal2 분기 플래그) |
| `지식베이스` | Y/- (goal3 분기 플래그) |
| `핵심 룰 (한 줄)` | 룰의 본문 |
| `입력값` / `출력값/동작` / `활용 예시` | 시스템 통합용 |
| `출처` | 저자 / 매체 |
| `URL` | 1차 출처 링크 |
| `신뢰도` | ★~★★★ |

### 룰 카드 스키마 (`rules/{ID}.yaml`)

DSL.md에 정의된 14필드 형식. 마스터 CSV 1행과 1:1 대응 + RULEBASE.md 매트릭스 위치 정보. 자세한 내용은 [`DSL.md`](./DSL.md) 참조.

### 신뢰도 별점

| 별점 | 의미 |
|---|---|
| ★★★ | 메타분석 / 학회 포지션 스테이트먼트 (NSCA, ACSM, ISSN) |
| ★★☆ | 좋은 1차 연구 / 정평 있는 교과서 (Helms, Israetel, Rippetoe) |
| ★☆☆ | 신뢰할 만한 코치의 수정 글 / 보조 자료 |

### ID 컨벤션 (분류별 prefix)

| Prefix | 분류 | 범위 |
|---|---|---|
| `A*` | RPE 자율조절 | A01~A14 (14개) |
| `B*` | 주간 볼륨 기준 | B01~B05 (5개) |
| `C*` | 세트/렙/강도 처방 | C01~C15 (15개) |
| `D*` | 주기화 모델 | D01~D15 (15개) |
| `E*` | 실시간 코칭 | E01~E17 (17개) |
| `F*` | 메타 룰 (SFR) | F05 (1개) |
| `G*` | 회복 / 디로드 | G01~G11 (11개) |
| `I*` | 기타 (워밍업·템포 등) | I01~I08 (8개) |
| `J*` | 운동 선택 | J01~J05, J07 (6개) |
| `K*` | 영양 | K01~K23 (23개) |
| `L*` | 특수 모집단 | L02~L08 (7개) |
| `M*` | 측정/평가 | M01, M03, M04 (3개) |
| `N*` | 생리학 | N01~N04 (4개) |
| `O*` | 카디오 | O01~O03 (3개) |
| `P*` | 스트레칭 | P01~P05 (5개) |
| `Q*` | 부상 이벤트 | Q01~Q06 (6개) |
| `R*` | 행동 코칭 / 한국 환경 | R01~R10 (10개) |

---

## 자료 통계

```
153  rules         (마스터 CSV)
153  rule cards    (rules/*.yaml — 마스터 1:1)
 67  rules         (운동 추천 분기)
 39  rules         (실시간 코칭 분기)
 94  rules         (지식베이스 분기)
449  exercises     (운동 풀 — 부위·장비별 메타데이터 포함)
161  rewrites      (사용자 노출용 평이 한국어)
 18  categories
  5  goals
  7  modules
 35  cells in matrix (모든 셀에 1개 이상의 룰 등록)
```

신뢰도 분포: ★★★ 95개(62%) / ★★☆ 52개(34%) / ★☆☆ 6개(4%) — 자세한 분포는 [`GAPS.md`](./GAPS.md)

---

## 디렉터리 구조

```
SAiM-Exercise-Data/
│
├─ README.md                            ← 이 파일
├─ GUIDE.md                             ← 자세한 활용 가이드 (필독)
│
├─ RULEBASE.md                          ★ 사람이 읽는 룰 카탈로그 (5×7 매트릭스 + 본문 + 부록)
├─ DSL.md                               ★ 룰 한 장의 표기법 정의
├─ GAPS.md                              ★ 자료 빈틈 리포트
├─ rules/                               ★ 153개 정형 룰 카드 (yaml)
│  ├─ A01.yaml ~ A14.yaml
│  ├─ B01.yaml ~ B05.yaml
│  ├─ ... (153개)
│  └─ R01.yaml ~ R10.yaml
│
├─ workout_knowledge_base.csv           ★ 마스터. 진실의 원천 (153행)
├─ exercise_library.csv                   449개 운동 풀
├─ exercise_pool.csv                      운동 종목 간이 풀
├─ goal1_session_recommendation.csv       운동 추천 분기 (67행)
├─ goal2_realtime_coaching.csv            실시간 코칭 분기 (39행)
├─ goal3_knowledge_base.csv               지식베이스 분기 (94행)
├─ staging_new_rows.csv                   새 행 추가 작업 영역
│
├─ output/                              ← Google Sheets paste용 TSV
│  ├─ sheet_운동 루틴 세션.tsv
│  ├─ sheet_실시간 코칭.tsv
│  └─ sheet_운동 지식베이스.tsv
│
└─ .scripts/                           ← 빌드/검증 스크립트
   ├─ master_index.json                  ID → 메타 빠른 조회
   ├─ rewrites.json                      평이 한국어 사전
   ├─ sync_goals.py                      마스터 → goal1/2/3 재생성
   ├─ build_tsv.py                       goal → Sheets TSV 빌드
   ├─ validate.py                        일관성 검증
   ├─ fetch_check.py                     URL liveness 점검
   └─ ... (기타 보조 스크립트)
```

> 룰베이스 변환 스크립트(`build_rulebase_v2.py`)는 작업 종료 후 삭제됨. 마스터 CSV가 갱신되면 [`DSL.md`](./DSL.md) 명세를 기반으로 새 변환기를 작성해 `RULEBASE.md` / `rules/*.yaml`을 재생성.

---

## 핵심 원칙

1. **마스터 CSV가 진실의 원천** — `workout_knowledge_base.csv`만 직접 편집. `rules/*.yaml`, `RULEBASE.md`, `goal_*.csv`, TSV는 모두 파생물.

2. **무료 1차 출처만** — 유료 책 광고 페이지·SNS만 있는 출처는 제거. NSCA·ACSM·Helms 무료 PDF·Schoenfeld 논문 우선.

3. **신뢰도 별점은 명시적으로** — 메타분석급(★★★)을 코치 블로그(★☆☆)와 섞지 않는다. 강등은 항상 사유를 남긴다.

4. **사용자 노출 문구는 `rewrites.json`** — 마스터 원본은 전문 용어 포함. 앱 화면에는 `rewrites.json`의 평이 한국어를 사용.

5. **파생물은 자동 생성물** — `rules/*.yaml`, `RULEBASE.md`, `GAPS.md`, TSV, goal_*.csv 모두 직접 편집 금지. 마스터 변경 시 [`DSL.md`](./DSL.md) 명세를 따라 재생성.

6. **빈틈은 명시적으로 기록** — 자료가 부족한 부분은 [`GAPS.md`](./GAPS.md)에 사실 그대로 카운트해서 보강 우선순위를 보여준다.

---

## 출처 정책

모든 룰은 다음 출처군에서 가져왔습니다.

| 카테고리 | 대표 출처 |
|---|---|
| 학회·포지션 스테이트먼트 | NSCA, ACSM, ISSN |
| 메타분석 / 1차 연구 | Schoenfeld, Helms, Israetel (PubMed) |
| 정평 있는 교과서 | Starting Strength (Rippetoe), Renaissance Periodization |
| 검증된 코치 글 | Tuchscherer (RTS), Stronger By Science |

**제외 기준**

- 유료 책 / SNS 단독 출처
- 출처 없는 블로그
- 죽은 링크 (URL liveness 검증으로 재배치)

---

## 변경 이력

| 날짜 | 마일스톤 |
|---|---|
| 2026-05-04 | **룰베이스 정리** — `DSL.md` 명세 + `rules/*.yaml` 153개 카드 + `GAPS.md` 빈틈 리포트 추가. `RULEBASE_V2.md` → `RULEBASE.md`로 통합. 임시 변환 스크립트 삭제 |
| 2026-05-03 | **v1.0 — 자료정리 종료**. 마스터 153행 확정, 룰베이스 832줄 발행, 2차 검수 PASS |
| 2026-05-03 | 운동 풀 449개 자동 추출 완료 |
| 2026-05-02 | 1차 검수 발견 20건 모두 해소 |
| 2026-04-** | 죽은 링크 / 약한 출처 24건 패치, 유료 출처 4건 제거 |
| 2026-04-** | 마스터 CSV 99행 → 153행 확장 (룰베이스 v2 7모듈 설계 반영) |

---

## 라이선스

**Private** — SAiM 내부용. 무단 외부 공유 금지.

본 자료는 외부 1차 출처(논문·교과서·코치 글)를 인용·요약한 것이며, 각 출처의 저작권은 원저자에게 있습니다. 자료 활용 시 인용 표기를 유지해 주세요.

---

<div align="center">

**더 자세한 내용은 [`GUIDE.md`](./GUIDE.md)를 참고하세요.**

질문이나 룰 추가 제안은 이슈로 남겨주세요.

</div>
