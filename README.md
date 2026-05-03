<div align="center">

# SAiM Exercise Data

**근거 기반 운동 코칭을 위한 통합 지식베이스**

153개의 검증된 룰 · 449개 운동 풀 · 5목표 × 7모듈 매트릭스

[![Rules](https://img.shields.io/badge/rules-153-1f6feb)](./workout_knowledge_base.csv)
[![Exercises](https://img.shields.io/badge/exercises-449-2da44e)](./exercise_library.csv)
[![Categories](https://img.shields.io/badge/categories-18-8957e5)](./RULEBASE_V2.md)
[![Sources](https://img.shields.io/badge/sources-1차_검증-brightgreen)](#출처-정책)
[![Status](https://img.shields.io/badge/audit-PASS-success)](#변경-이력)
[![License](https://img.shields.io/badge/license-private-d1242f)](#라이선스)

[자세한 활용 가이드 →](./GUIDE.md)

</div>

---

## 한 줄 요약

> 운동 코칭 앱이 사용자에게 **어떤 판단을, 어떤 근거로** 내릴지 모아둔 카탈로그. 모든 룰은 NSCA·ACSM·Helms·Schoenfeld 등 1차 출처에서 가져왔고, 신뢰도 별점(★~★★★)이 붙어 있다.

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

**18개 분류**

`RPE 자율조절` `주간 볼륨 기준` `세트/렙/강도 처방` `주기화 모델` `실시간 코칭` `운동 선택` `측정/평가` `회복` `회복/디로드` `영양` `보충제` `생리학` `부상 관리` `스트레칭` `카디오` `특수 모집단` `운동 데이터셋` `기타`

---

## 어떻게 활용하나요

### 사용 시나리오

| 누가 | 무엇을 하려고 | 어떤 파일을 보면 됨 |
|---|---|---|
| 기획팀 / PM | 룰 전체를 한눈에 보고 의사결정 | [`RULEBASE_V2.md`](./RULEBASE_V2.md) |
| 트레이너 / 도메인 검수 | 출처 검증, 룰 추가/수정 제안 | [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) |
| 백엔드 개발자 | DB seed, 룰엔진 import | [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) + [`master_index.json`](./.scripts/master_index.json) |
| 프론트 개발자 | UI에 표시할 평이 한국어 문구 | [`rewrites.json`](./.scripts/rewrites.json) + [`exercise_library.csv`](./exercise_library.csv) |
| 챗봇 / RAG 개발자 | 출처가 붙은 답변 생성 | [`goal3_knowledge_base.csv`](./goal3_knowledge_base.csv) |
| 협업 시트 작업자 | Google Sheets에 그대로 붙여넣기 | [`output/sheet_*.tsv`](./output/) |

> **상세 가이드는 [`GUIDE.md`](./GUIDE.md)에 있습니다.** 역할별 진입점, 파일별 컬럼 설명, 7가지 실전 시나리오, FAQ, 용어집까지 포함.

---

## Quick Start (역할별)

### "5분 만에 자료 파악하고 싶다"

```
1. RULEBASE_V2.md 열기
2. 목차에서 관심 있는 모듈로 점프
3. 룰 옆 [ID★URL] 클릭하면 1차 출처로 이동
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

### 신뢰도 별점

| 별점 | 의미 |
|---|---|
| ★★★ | 메타분석 / 학회 포지션 스테이트먼트 (NSCA, ACSM, ISSN) |
| ★★☆ | 좋은 1차 연구 / 정평 있는 교과서 (Helms, Israetel, Rippetoe) |
| ★☆☆ | 신뢰할 만한 코치의 수정 글 / 보조 자료 |

### ID 컨벤션 (분류별 prefix)

| Prefix | 분류 | 예시 |
|---|---|---|
| `A*` | RPE 자율조절 | A01, A02, ... |
| `B*` | 주간 볼륨 기준 | B01~B05 |
| `C*` | 세트/렙/강도 처방 | C01~C15 |
| `D*` | 주기화 모델 | D01~D15 |
| `E*` | 실시간 코칭 | E01~E17 |
| `F*` | 메타 룰 (SFR) | F05 |
| `G*` | 회복 / 디로드 | G01~G11 |
| `I*` | 측정 / 평가 | I01~I08 |
| `J*` | 운동 선택 | J02~J07 |
| `K*` | 영양 | K01~K23 |
| `L*` | 모집단 분기 | L02~L08 |
| `M*` | 도구 | M01~M04 |
| `N*` | 행동·습관 | N01~N04 |
| `O*` | 보충제 | O01~O03 |
| `P*` | 생리학 | P01~P05 |
| `Q*` | 부상 이벤트 | Q01~Q06 |
| `R*` | 한국 환경 / 행동·안전 | R01~R10 |

---

## 자료 통계

```
153  rules         (마스터)
 97  rules         (운동 추천 분기)
 50  rules         (실시간 코칭 분기)
148  rules         (지식베이스 분기)
449  exercises     (운동 풀 — 부위·장비별 메타데이터 포함)
161  rewrites      (사용자 노출용 평이 한국어)
 18  categories
  5  goals
  7  modules
```

---

## 디렉터리 구조

```
SAiM-Exercise-Data/
│
├─ README.md                            ← 이 파일
├─ GUIDE.md                             ← 자세한 활용 가이드 (필독)
├─ RULEBASE_V2.md                       ← 팀 회람용 메인. 5×7 매트릭스 + 모든 룰 인라인
│
├─ workout_knowledge_base.csv           ★ 마스터. 진실의 원천 (153행)
├─ exercise_library.csv                   449개 운동 풀
├─ goal1_session_recommendation.csv       운동 추천 분기 (97행)
├─ goal2_realtime_coaching.csv            실시간 코칭 분기 (50행)
├─ goal3_knowledge_base.csv               지식베이스 분기 (148행)
│
├─ output/                              ← Google Sheets paste용
│  ├─ sheet_마스터.tsv
│  ├─ sheet_운동 루틴 세션.tsv
│  ├─ sheet_실시간 코칭.tsv
│  └─ sheet_운동 지식베이스.tsv
│
└─ .scripts/                           ← 빌드/검증 스크립트
   ├─ master_index.json                  ID → 메타 빠른 조회
   ├─ rewrites.json                      평이 한국어 사전
   ├─ sync_goals.py                      마스터 → goal1/2/3 재생성
   ├─ build_tsv.py                       goal → Sheets TSV 빌드
   ├─ build_rulebase_v2.py               RULEBASE_V2.md 재생성
   └─ validate.py                        일관성 검증
```

---

## 핵심 원칙

1. **마스터 CSV가 진실의 원천** — `workout_knowledge_base.csv`만 직접 편집. goal_*.csv와 TSV는 모두 파생물이라 `sync_goals.py` → `build_tsv.py` 순서로 재생성.

2. **무료 1차 출처만** — 유료 책 광고 페이지·SNS만 있는 출처는 제거. NSCA·ACSM·Helms 무료 PDF·Schoenfeld 논문 우선.

3. **신뢰도 별점은 명시적으로** — 메타분석급(★★★)을 코치 블로그(★☆☆)와 섞지 않는다. 강등은 항상 사유를 남긴다.

4. **사용자 노출 문구는 `rewrites.json`** — 마스터 원본은 전문 용어 포함. 앱 화면에는 `rewrites.json`의 평이 한국어를 사용.

5. **TSV는 자동 생성물** — 직접 편집 금지. 항상 `build_tsv.py`로 재빌드.

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
| 2026-05-03 | **v1.0 — 자료정리 종료**. 마스터 153행 확정, RULEBASE_V2.md 832줄 발행, 2차 검수 PASS |
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
