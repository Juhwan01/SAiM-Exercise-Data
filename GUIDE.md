# SAiM Exercise Data — 활용 가이드

이 문서는 SAiM Exercise Data 저장소의 자료를 **누가, 언제, 어떻게 쓰는지** 처음 보는 사람도 막히지 않고 따라갈 수 있게 정리한 가이드입니다.

빠른 개요는 [`README.md`](./README.md)에, 룰 본문은 [`RULEBASE_V2.md`](./RULEBASE_V2.md)에 있습니다.

---

## 목차

1. [시작하며 — 5분 안에 이해하기](#1-시작하며--5분-안에-이해하기)
2. [역할별 진입점](#2-역할별-진입점)
3. [파일 한 줄 요약표](#3-파일-한-줄-요약표)
4. [파일별 상세 설명](#4-파일별-상세-설명)
5. [데이터 스키마](#5-데이터-스키마)
6. [신뢰도 별점 시스템](#6-신뢰도-별점-시스템)
7. [ID 컨벤션 — 분류별 prefix](#7-id-컨벤션--분류별-prefix)
8. [실전 활용 시나리오 7선](#8-실전-활용-시나리오-7선)
9. [자료 수정 / 재생성 절차](#9-자료-수정--재생성-절차)
10. [FAQ](#10-faq)
11. [용어집](#11-용어집)
12. [출처 정책 상세](#12-출처-정책-상세)
13. [문의 / 기여](#13-문의--기여)

---

## 1. 시작하며 — 5분 안에 이해하기

### SAiM Exercise Data가 답하려는 한 가지 질문

> *"운동 코칭 앱이 사용자에게 어떤 판단을, 어떤 근거로 내려야 하는가?"*

### 자료의 3축

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│   목표 (5)         ×   모듈 (7)        +   레이어 (3)  │
│                                                        │
│   다이어트              온보딩              모집단 분기 │
│   벌크업                세션 시작           부상 트리거 │
│   스트렝스              세트별 처방         메타 룰    │
│   근육량 증가           세트 후 학습                    │
│   건강증진              메조사이클 관리                 │
│                         영양·회복                       │
│                         행동·안전                       │
│                                                        │
└────────────────────────────────────────────────────────┘
```

5개 운동 목표 각각에 대해, 7개 모듈에서 어떤 룰을 발동시킬지 **5×7 매트릭스로 정리**되어 있습니다. 그 위에 모집단(노인·청소년·만성질환) 분기, 부상 이벤트, 메타 룰(SFR)이 별도 레이어로 얹힙니다.

### 자료의 신뢰도

153개 룰 모두 **1차 출처 + 신뢰도 별점** 표기. 출처는 NSCA·ACSM·Helms·Schoenfeld 등 학계/현장 표준에서 인용했으며, 죽은 링크와 유료 출처는 모두 제거되었습니다.

### 자료가 설계된 시점

**2026-05-03 시점 v1.0 발행** — 자료정리 단계는 완전히 종료. 이후 작업은 앱 통합·구현 영역입니다.

---

## 2. 역할별 진입점

### 처음 합류한 분께

먼저 [`README.md`](./README.md)로 5분 개요 → 본 가이드 [`#3 파일 한 줄 요약표`](#3-파일-한-줄-요약표)에서 어떤 파일이 있는지 → [`RULEBASE_V2.md`](./RULEBASE_V2.md) 첫 100줄로 톤·구조 감 잡기.

### PM / 기획자

**메인**: [`RULEBASE_V2.md`](./RULEBASE_V2.md)

5×7 매트릭스 헤더에서 관심 있는 (목표×모듈) 셀로 점프 → 그 셀에 들어 있는 ID 목록 확인 → 본문에서 룰 한 줄 읽기 → 옆 링크 클릭으로 출처 확인. 룰 추가/수정 제안은 마스터 CSV에서 해당 ID 행을 찾아 코멘트로 남기거나, Sheets 협업 탭에서 직접 편집.

### 트레이너 / 도메인 검수자

**메인**: [`workout_knowledge_base.csv`](./workout_knowledge_base.csv)

각 룰의 `핵심 룰 (한 줄)` + `출처` + `URL` + `신뢰도` 컬럼을 검토. 출처가 약하다고 판단되면 더 강한 출처로 교체 제안. 신규 룰은 [`#9 자료 수정 / 재생성 절차`](#9-자료-수정--재생성-절차)를 따라 추가.

### 백엔드 / 룰엔진 개발자

**메인**: [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) + [`.scripts/master_index.json`](./.scripts/master_index.json)

마스터 CSV를 DB seed로 import. 룰엔진은 ID → 메타 조회를 위해 `master_index.json`을 캐시 레이어로 사용. 5×7 매트릭스 라우팅은 `(목표, 모듈)` 키로 ID 리스트를 fetch.

### 프론트 / UI 개발자

**메인**: [`.scripts/rewrites.json`](./.scripts/rewrites.json) + [`exercise_library.csv`](./exercise_library.csv)

마스터 CSV의 원본 한국어는 *전문 용어를 포함*합니다 (예: "FFMI(제지방량 지수)", "RIR 2 캡"). 사용자 화면에는 반드시 `rewrites.json`의 `핵심_평이`/`항목_평이`를 사용. 운동 선택 UI는 `exercise_library.csv` 449개 풀에서 부위·장비별로 필터링.

### 챗봇 / RAG 개발자

**메인**: [`goal3_knowledge_base.csv`](./goal3_knowledge_base.csv)

지식 응답형 질문(예: "단백질 얼마나 먹어야 해?")은 goal3로 인덱싱. RAG retrieval 시 `핵심 룰` + `출처` + `URL`을 함께 반환해서 답변에 출처 인용을 붙임. 신뢰도 별점이 ★★★ 인 룰을 우선순위로.

### 협업 시트 작업자

**메인**: [`output/`](./output/) 디렉터리의 4개 TSV

Google Sheets 각 탭의 `A3` 셀 클릭 → TSV 파일 내용 전체 복사 → 붙여넣기. 4열로 자동 분리됩니다 (A 빈칸 / B 내용 / C 출처 / D URL). TSV는 자동 생성물이므로 직접 편집하지 말고, 마스터 CSV 수정 후 `build_tsv.py`로 재생성.

---

## 3. 파일 한 줄 요약표

### 사람이 직접 읽는 문서

| 파일 | 한 줄 |
|---|---|
| [`README.md`](./README.md) | 저장소 소개 + 빠른 개요 |
| [`GUIDE.md`](./GUIDE.md) | 본 가이드 — 모든 팀원 대상 활용 가이드 |
| [`RULEBASE_V2.md`](./RULEBASE_V2.md) | 팀 회람용 메인. 5×7 매트릭스 + 모든 룰 인라인 |

### 데이터 (CSV)

| 파일 | 행수 | 한 줄 |
|---|---:|---|
| [`workout_knowledge_base.csv`](./workout_knowledge_base.csv) | 153 | **★ 마스터, 진실의 원천**. DB seed / 룰엔진 import |
| [`goal1_session_recommendation.csv`](./goal1_session_recommendation.csv) | 97 | 운동 추천(세션 처방) 분기 |
| [`goal2_realtime_coaching.csv`](./goal2_realtime_coaching.csv) | 50 | 실시간 코칭(RPE 자율조절) 분기 |
| [`goal3_knowledge_base.csv`](./goal3_knowledge_base.csv) | 148 | 지식베이스(챗봇/RAG) 분기 |
| [`exercise_library.csv`](./exercise_library.csv) | 449 | 운동 종목 풀 — 부위·장비별 메타데이터 |

### Google Sheets 협업용 (TSV)

| 파일 | 행수 | Sheets 탭 |
|---|---:|---|
| [`output/sheet_마스터.tsv`](./output/) | 154 | "마스터" |
| [`output/sheet_운동 루틴 세션.tsv`](./output/) | 97 | "운동 루틴 세션" |
| [`output/sheet_실시간 코칭.tsv`](./output/) | 50 | "실시간 코칭" |
| [`output/sheet_운동 지식베이스.tsv`](./output/) | 148 | "운동 지식베이스" |

> 모두 A3 셀에 붙여넣기. 4열: 빈칸 / 내용 / 출처 / URL.

### 시스템용 데이터

| 파일 | 한 줄 |
|---|---|
| [`.scripts/master_index.json`](./.scripts/master_index.json) | ID → 메타 빠른 조회. RULEBASE_V2 빌드 입력 |
| [`.scripts/rewrites.json`](./.scripts/rewrites.json) | 사용자 노출용 평이 한국어 사전 (161건) |

### 빌드 / 검증 스크립트

| 스크립트 | 언제 |
|---|---|
| [`.scripts/sync_goals.py`](./.scripts/sync_goals.py) | 마스터 행 추가/Y플래그 변경 후 → goal1/2/3 재생성 |
| [`.scripts/build_tsv.py`](./.scripts/build_tsv.py) | goal 동기화 후 → Sheets TSV 재빌드 |
| [`.scripts/build_rulebase_v2.py`](./.scripts/build_rulebase_v2.py) | rewrites/마스터 변경 후 → RULEBASE_V2.md 재생성 |
| [`.scripts/validate.py`](./.scripts/validate.py) | 마지막 점검 — Y플래그 ↔ goal 행수 일치 확인 |
| [`.scripts/fetch_check.py`](./.scripts/fetch_check.py) | URL liveness 점검 |

---

## 4. 파일별 상세 설명

### `workout_knowledge_base.csv` — 마스터 (진실의 원천)

**행수**: 153 / **컬럼 수**: 14 / **인코딩**: UTF-8

이 파일이 모든 다른 파일의 원본입니다. **이 파일만 직접 편집하고**, 다른 파생 파일은 스크립트로 재생성하세요.

각 행은 하나의 룰입니다. 룰은 다음 7개 모듈 중 하나에 속하며, 분류·항목·핵심 룰·출처·신뢰도가 함께 묶여 있습니다.

**컬럼 구조** ([#5 데이터 스키마](#5-데이터-스키마) 참조)

**왜 153행인가**: 룰베이스 v2 설계 (5목표 × 7모듈 + 별도 레이어 3개)에 필요한 최소 룰셋. 99행 → 153행 확장은 모듈 매트릭스 빈칸을 채우기 위한 것이었습니다.

### `goal1_session_recommendation.csv` — 운동 추천 분기

**행수**: 97

마스터에서 `운동 추천` 컬럼이 `Y`인 행만 모은 파생 파일. 세션 처방(어떤 운동을 몇 세트 몇 렙으로) 모듈이 읽습니다. 여기엔 RPE·볼륨·세트/렙·주기화·운동 선택 룰이 모여 있습니다.

### `goal2_realtime_coaching.csv` — 실시간 코칭 분기

**행수**: 50

마스터에서 `실시간 코칭` Y인 행. 세션 *중* 사용자 입력(RPE 점수, 폼 큐, 통증 신호)에 반응하는 룰셋. 비전/센서가 아닌 **RPE 자율조절** 기반입니다.

### `goal3_knowledge_base.csv` — 지식베이스 분기

**행수**: 148

마스터에서 `지식베이스` Y인 행. 챗봇이나 FAQ 답변에 쓰일 자료. 거의 모든 룰이 포함되며, 사용자 질문에 1차 출처 인용으로 답하기 위한 인덱스 소스입니다.

### `exercise_library.csv` — 운동 종목 풀

**행수**: 449

종목별 메타데이터 — 명칭(한/영), 주동근, 보조근, 장비, 난이도, 카테고리(컴파운드/아이솔레이션) 등. 운동 선택 UI나 종목 추천 로직의 **풀(pool)**로 사용. 룰베이스와 별도 자료입니다.

> 운동 영상 매핑은 v2 (다음 버전) 과제로 미뤄짐.

### `RULEBASE_V2.md` — 팀 회람 메인

**832줄, 206 KB**

매트릭스 + 본문 + 부록 구조:
1. **5×7 매트릭스** — 한눈에 보는 (목표×모듈) 룰 ID 매핑 표
2. **본문** — 모듈별·목표별 룰 리스트. 각 룰 옆에 `[ID ★신뢰도 - 평이항목명](URL)` 인라인 링크
3. **부록** — 153행 역참조 표

`build_rulebase_v2.py`로 마스터 + rewrites + master_index에서 자동 생성.

### `.scripts/master_index.json`

ID를 키로 한 빠른 메타 조회 JSON. 분류·항목·신뢰도·출처를 즉시 lookup. 룰엔진 캐시 / RULEBASE_V2 빌드 입력.

### `.scripts/rewrites.json` (161건)

마스터 원본 한국어를 평이한 한국어로 다시 쓴 사전. 키는 마스터 ID, 값은 다음 필드들:

```json
{
  "K19": {
    "분류_평이": "영양",
    "항목_평이": "기초대사량(BMR) 계산하는 가장 정확한 공식",
    "핵심_평이": "남성: 10×체중(kg) + 6.25×키(cm) - 5×나이 + 5...",
    "적용시점_평이": "최초 1회 온보딩 / 정체기 재계산 시"
  }
}
```

마스터에 jargon이 있어도 사용자 화면에는 이쪽을 사용. 누락 시 마스터 원본이 fallback.

---

## 5. 데이터 스키마

### 마스터 CSV 14개 컬럼

| # | 컬럼 | 타입 | 예시 | 설명 |
|---|---|---|---|---|
| 1 | `ID` | string | `K19` | 고유 식별자. 분류별 알파벳 prefix |
| 2 | `분류` | enum | `영양` | 18개 분류 중 하나 |
| 3 | `항목` | string | `Mifflin-St Jeor 공식으로 BMR 계산` | 룰 제목 |
| 4 | `적용 시점` | string | `온보딩 / 정체기 재계산` | 언제 발동시킬지 |
| 5 | `운동 추천` | `Y` / `-` | `Y` | goal1 분기 플래그 |
| 6 | `실시간 코칭` | `Y` / `-` | `-` | goal2 분기 플래그 |
| 7 | `지식베이스` | `Y` / `-` | `Y` | goal3 분기 플래그 |
| 8 | `핵심 룰 (한 줄)` | string | `남성: 10×체중 + 6.25×키...` | 룰 본문 |
| 9 | `입력값` | string | `체중, 키, 나이, 성별` | 시스템 입력 |
| 10 | `출력값/동작` | string | `BMR(kcal/day)` | 시스템 출력 |
| 11 | `활용 예시` | string | `60kg 30세 남성 → BMR≈1,470` | 예시 케이스 |
| 12 | `출처` | string | `Mifflin et al., 1990` | 저자/매체 |
| 13 | `URL` | URL | `https://pubmed.ncbi.nlm.nih.gov/2305711/` | 1차 출처 |
| 14 | `신뢰도` | enum | `★★★` | 별점 1~3개 |

### 18개 분류 (`분류` 컬럼)

```
RPE 자율조절          주간 볼륨 기준        세트/렙/강도 처방
주기화 모델           실시간 코칭           운동 선택
측정/평가             회복                  회복/디로드
영양                  보충제                생리학
부상 관리             스트레칭              카디오
특수 모집단           운동 데이터셋         기타
```

### 7개 모듈 (RULEBASE_V2 구조)

| # | 모듈 | 단위 | 설명 |
|---|---|---|---|
| 1 | 온보딩 | 최초 1회 | 사용자 분류·안전 게이트·1RM 추정·영양 모드·프로그램 선택 |
| 2 | 세션 시작 | 매 세션 | 워밍업·컨디션 체크·첫 무게 보정 |
| 3 | 세트별 처방 | 매 세트 | 무게·휴식·폼 큐·호흡 결정 |
| 4 | 세트 후 학습 | 매 세트 | 사용자 입력 → 다음 세트/세션 보정 |
| 5 | 메조사이클 관리 | 주 단위 | 볼륨 증가·디로드 배치 |
| 6 | 영양·회복 | 일 단위 | 칼로리·단백질·수분·수면·보충제 |
| 7 | 행동·안전 | 백그라운드 | 동기·습관·이탈·한국 환경 맞춤 |

### 5개 운동 목표

```
다이어트          체지방 감량
벌크업            체중·근육량 동시 증가
스트렝스          최대 근력(1RM) 향상
근육량 증가       하이퍼트로피, 근육 크기
건강증진          전반적 컨디션·만성질환 예방
```

---

## 6. 신뢰도 별점 시스템

| 별점 | 의미 | 대표 출처 |
|---|---|---|
| ★★★ | 메타분석 / 학회 포지션 스테이트먼트 | NSCA, ACSM, ISSN, Cochrane |
| ★★☆ | 좋은 1차 연구 / 정평 있는 교과서 | Schoenfeld 논문, Helms, Israetel, Rippetoe |
| ★☆☆ | 신뢰할 만한 코치의 수정 글 / 보조 자료 | Stronger By Science, RTS, RP 블로그 |

### 별점이 떨어지는 사유 (강등은 명시)

- 메타분석 미존재 → ★★☆
- 단일 코호트 / 작은 샘플 → ★★☆
- 코치 경험 + 다수 코호트 관찰 → ★☆☆
- 단순 블로그 정리 → 제외 (수록 안 함)

### 활용 가이드

- **앱 챗봇 답변 생성 시**: ★★★ → ★★☆ → ★☆☆ 순으로 우선 인용
- **트레이너 검수 시**: ★☆☆ 룰은 반드시 ★★☆ 이상으로 업그레이드 가능한지 검토
- **신뢰도 강등 시**: 마스터 `신뢰도` 컬럼 수정 + 사유를 커밋 메시지에 명시

---

## 7. ID 컨벤션 — 분류별 prefix

| Prefix | 분류 | 예시 |
|---|---|---|
| `A*` | RPE 자율조절 | A01 RPE 정의, A07 RIR 변환표 |
| `B*` | 주간 볼륨 기준 | B01 MEV/MAV/MRV |
| `C*` | 세트/렙/강도 처방 | C09 1RM Epley 공식 |
| `D*` | 주기화 모델 | D02 블록 주기화 |
| `E*` | 실시간 코칭 | E07 폼 큐, E10 호흡 패턴 |
| `F*` | 메타 룰 (SFR) | F05 자극 대비 피로 비율 |
| `G*` | 회복 / 디로드 | G05 디로드 트리거 |
| `I*` | 측정 / 평가 | I05 워밍업 프로토콜 |
| `J*` | 운동 선택 | J02 컴파운드 우선 |
| `K*` | 영양 | K01 단백질 일일 권장량 |
| `L*` | 모집단 분기 | L02 노인, L03 청소년 |
| `M*` | 도구 / 측정 장비 | M01 인바디 vs DEXA |
| `N*` | 행동·습관 | N01 습관 형성 21일 |
| `O*` | 보충제 | O01 크레아틴 |
| `P*` | 생리학 | P05 근비대 메커니즘 |
| `Q*` | 부상 이벤트 트리거 | Q01 통증 발생 시 즉시 중단 |
| `R*` | 한국 환경 / 행동·안전 | R01 한식 단백질 옵션 |

> 새 룰 추가 시 같은 prefix 안에서 빈 번호를 사용하세요. ID 충돌 검사는 `validate.py`가 합니다.

---

## 8. 실전 활용 시나리오 7선

### 시나리오 1: 룰 추가 (트레이너 → 마스터 → 파생까지)

```bash
# 1) workout_knowledge_base.csv에 새 행 추가 (예: K24 신규 영양 룰)
#    - ID 충돌 없는지 확인
#    - 출처 URL 확인 + 신뢰도 별점 표기
#    - 운동 추천/실시간 코칭/지식베이스 Y 플래그 결정

# 2) 파생 파일 재생성
python3 .scripts/sync_goals.py        # goal1/2/3 재생성
python3 .scripts/build_tsv.py         # Sheets TSV 재빌드
python3 .scripts/build_rulebase_v2.py # RULEBASE_V2.md 재생성

# 3) 검증
python3 .scripts/validate.py
```

### 시나리오 2: 팀 회람용 한 장 요약

[`RULEBASE_V2.md`](./RULEBASE_V2.md) 링크를 슬랙/노션에 공유. 첫 화면의 5×7 매트릭스가 그대로 한 장 요약 역할을 합니다.

### 시나리오 3: 기획팀 Google Sheets 작업

```
1. output/sheet_마스터.tsv 열기
2. 전체 복사 (Ctrl+A → Ctrl+C)
3. Sheets "마스터" 탭 A3 클릭 → Ctrl+V
4. 자동으로 4열 분리: 빈칸 / 내용 / 출처 / URL
5. 다른 3개 탭(루틴/코칭/지식베이스)도 동일하게 반복
```

### 시나리오 4: 앱 화면 텍스트 가져오기

```python
import json
import pandas as pd

master = pd.read_csv("workout_knowledge_base.csv")
rewrites = json.load(open(".scripts/rewrites.json"))

def display_text(rule_id: str) -> dict:
    """앱 화면에 보여줄 평이 한국어 텍스트"""
    if rule_id in rewrites:
        return rewrites[rule_id]
    # fallback to master original
    row = master[master["ID"] == rule_id].iloc[0]
    return {
        "분류_평이": row["분류"],
        "항목_평이": row["항목"],
        "핵심_평이": row["핵심 룰 (한 줄)"],
        "적용시점_평이": row["적용 시점"],
    }

print(display_text("K19"))
```

### 시나리오 5: 챗봇 RAG 인덱싱

```python
import pandas as pd

kb = pd.read_csv("goal3_knowledge_base.csv")

# 각 행을 "본문 + 출처 인용" 형태로 인덱싱
docs = []
for _, row in kb.iterrows():
    text = f"{row['항목']}: {row['핵심 룰 (한 줄)']}"
    citation = f"[{row['출처']}]({row['URL']}) {row['신뢰도']}"
    docs.append({"id": row["ID"], "text": text, "citation": citation})

# 사용자 질문 → top-k retrieval → 답변 생성 시 citation 함께 반환
```

### 시나리오 6: 룰엔진 라우팅 ((목표, 모듈) → 룰 ID 리스트)

```python
# RULEBASE_V2.md의 5×7 매트릭스를 그대로 코드로:
ROUTING = {
    ("다이어트", "온보딩"): ["L04", "K19", "K20", "K21", ...],
    ("다이어트", "세션 시작"): ["I05", "I06", "I07", ...],
    ("벌크업", "온보딩"): ["L04", "K19", "K20", ...],
    # ...
}

def get_rules(goal: str, module: str) -> list[dict]:
    ids = ROUTING[(goal, module)]
    return [master_index[id] for id in ids]
```

### 시나리오 7: 출처 신뢰도 감사 (정기 점검)

```bash
# URL liveness 체크
python3 .scripts/fetch_check.py

# 신뢰도 분포 확인
python3 -c "
import pandas as pd
df = pd.read_csv('workout_knowledge_base.csv')
print(df['신뢰도'].value_counts())
"
```

---

## 9. 자료 수정 / 재생성 절차

### 황금률

> **마스터 CSV가 진실의 원천. 다른 모든 파일은 파생물.**

goal_*.csv, output/*.tsv, RULEBASE_V2.md, master_index.json은 모두 마스터에서 자동 생성됩니다. **직접 편집하지 마세요.**

### 표준 작업 순서

```
1. workout_knowledge_base.csv 수정
        ↓
2. python3 .scripts/sync_goals.py
   → goal1/goal2/goal3.csv 재생성
        ↓
3. python3 .scripts/build_tsv.py
   → output/sheet_*.tsv 재빌드
        ↓
4. python3 .scripts/build_rulebase_v2.py
   → RULEBASE_V2.md + master_index.json 재생성
        ↓
5. python3 .scripts/validate.py
   → Y플래그 ↔ goal 행수 일치 검증
```

### 수정 유형별 가이드

| 수정 유형 | 추가 절차 |
|---|---|
| 핵심 룰 본문만 수정 | 위 표준 절차만 |
| URL 교체 | `fetch_check.py`로 liveness 사전 확인 |
| 신뢰도 강등/승격 | 사유를 커밋 메시지에 명시 |
| 새 룰 추가 | ID 충돌 검사 (`validate.py`) |
| Y 플래그 변경 | goal 분기 행수가 의도대로인지 `validate.py` 확인 |
| 평이 한국어 추가 | `.scripts/rewrites.json`에 ID 키로 추가 |

### 주의

- **TSV 직접 편집 금지** — 항상 `build_tsv.py`로 재생성
- **goal_*.csv 직접 편집 금지** — 항상 `sync_goals.py`로 재생성
- **RULEBASE_V2.md 직접 편집 금지** — 항상 `build_rulebase_v2.py`로 재생성

---

## 10. FAQ

**Q. 마스터 CSV와 goal_*.csv가 다르면 어떻게 하나요?**
A. `validate.py`를 돌리면 어디가 어긋났는지 알려줍니다. 마스터를 정답으로 두고 `sync_goals.py`로 재생성하세요.

**Q. 새 운동 종목을 추가하고 싶어요.**
A. 룰베이스(`workout_knowledge_base.csv`)가 아닌 [`exercise_library.csv`](./exercise_library.csv)에 추가합니다. 두 자료는 별개입니다.

**Q. 한국어 룰이 너무 어려워요. 사용자한테 그대로 보여줘도 되나요?**
A. 안 됩니다. 마스터의 한국어는 의도적으로 정확한 전문 용어를 씁니다. 사용자 화면에는 [`.scripts/rewrites.json`](./.scripts/rewrites.json)의 `핵심_평이`/`항목_평이`를 사용하세요.

**Q. 출처 URL이 죽었어요.**
A. `fetch_check.py`로 일괄 점검 후, 같은 자료의 대체 위치(저자 사이트·웨이백머신)를 찾아 마스터의 URL 컬럼만 교체. `apply_updates.py`의 패턴으로 일괄 패치 가능합니다.

**Q. 신뢰도 ★★★과 ★★☆의 경계가 모호해요.**
A. 메타분석 또는 학회 공식 입장이면 ★★★, 그 외 학술 1차 자료/정평 교과서는 ★★☆로 보세요. 애매하면 보수적으로 ★★☆를 적용합니다.

**Q. 5목표 외에 다른 목표(예: 재활)는 어떻게 처리하나요?**
A. 현재 v1에서는 5목표만 다룹니다. 재활은 부상 이벤트 트리거(Q*) 레이어에서 부분적으로 다루며, 본격적인 재활 모듈은 v2 과제입니다.

**Q. 영상은 없나요?**
A. 운동 영상 매핑은 v2 과제로 미뤄졌습니다. 현재 449개 운동 풀에는 텍스트 메타데이터만 있습니다.

**Q. 외부에 공유해도 되나요?**
A. **안 됩니다.** Private 저장소이며, 외부 공유 시 SAiM 내부 승인을 받으세요. 출처 자료의 저작권은 원저자에게 있습니다.

**Q. 룰을 발견 못 하겠어요. 검색은 어떻게 하나요?**
A. 두 가지 방법:
- ID 알면: [`RULEBASE_V2.md`](./RULEBASE_V2.md)에서 Ctrl+F로 ID 검색
- 키워드: [`workout_knowledge_base.csv`](./workout_knowledge_base.csv)를 엑셀/Numbers에서 열고 컬럼 필터

---

## 11. 용어집

운동 과학 / 자료 구조에서 자주 쓰는 용어 정리.

### 운동 과학 용어

| 용어 | 풀이 |
|---|---|
| **RPE** | Rate of Perceived Exertion. 자각된 운동 강도(1~10). RPE 8 = "2개 더 들 수 있을 것 같다" |
| **RIR** | Reps In Reserve. 한계까지 남은 횟수. RIR 2 = 한계까지 2회 남김 |
| **1RM** | One-Rep Max. 한 번에 들 수 있는 최대 무게 |
| **BMR** | Basal Metabolic Rate. 기초대사량. 가만히 있어도 쓰는 하루 칼로리 |
| **TDEE** | Total Daily Energy Expenditure. 하루 총 소비 칼로리 (BMR × 활동계수) |
| **PAL** | Physical Activity Level. 활동 계수 (1.2 ~ 1.9) |
| **LBM** | Lean Body Mass. 지방을 뺀 체중 (근육+뼈+장기) |
| **FFMI** | Fat-Free Mass Index. 제지방량 지수 |
| **MEV / MAV / MRV** | Minimum Effective / Maximum Adaptive / Maximum Recoverable Volume. 주간 볼륨의 3구간 |
| **하이퍼트로피** | 근비대. 근섬유 횡단면적 증가 |
| **메조사이클** | 4~8주 단위 훈련 묶음. 한 사이클 끝에 디로드 배치 |
| **디로드** | 의도적 강도/볼륨 감소 주(週). 회복과 적응 통합용 |
| **컴파운드** | 다관절 운동 (스쿼트, 데드리프트, 벤치프레스) |
| **아이솔레이션** | 단관절 운동 (컬, 익스텐션) |
| **SFR** | Stimulus-to-Fatigue Ratio. 자극 대비 피로 비율. 운동 선택 가중치 |
| **PPL** | Push-Pull-Legs. 밀기·당기기·다리 분할 |
| **OHP** | Overhead Press. 머리 위로 미는 운동 |
| **DEXA** | Dual-Energy X-ray Absorptiometry. 가장 정확한 체성분 측정 (오차 ±2%) |

### 자료 구조 용어

| 용어 | 풀이 |
|---|---|
| **마스터 CSV** | `workout_knowledge_base.csv`. 모든 다른 파일의 원본 |
| **파생 파일** | 마스터에서 자동 생성되는 파일 (goal_*.csv, output/*.tsv, RULEBASE_V2.md) |
| **goal 분기** | 마스터의 `운동 추천` / `실시간 코칭` / `지식베이스` Y 플래그로 필터된 파생 |
| **5×7 매트릭스** | 5목표 × 7모듈로 룰을 라우팅하는 표 |
| **ID prefix** | 분류별 알파벳 (`A*`=RPE, `K*`=영양, `R*`=한국 환경 등) |
| **별점** | 신뢰도 표기 (★~★★★) |
| **rewrites** | 사용자 화면용 평이 한국어 사전 |

---

## 12. 출처 정책 상세

### 채택 기준

1. **메타분석 / 학회 포지션 스테이트먼트**
   - NSCA Position Stand
   - ACSM Position Stand
   - ISSN Position Paper
   - Cochrane Review

2. **정평 있는 1차 연구 / 교과서**
   - Schoenfeld 박사 논문군 (근비대 분야)
   - Helms 등의 자연 보디빌딩 피라미드 (무료 PDF)
   - Israetel (RP) 과학적 자료
   - Rippetoe Starting Strength

3. **검증된 코치의 수정 글**
   - Stronger By Science (Greg Nuckols)
   - Reactive Training Systems (Mike Tuchscherer)
   - Renaissance Periodization 블로그

### 제외 기준

- 유료 책 광고 페이지 (구매 유도가 주목적인 페이지)
- SNS 단독 출처 (Instagram·YouTube만)
- 출처 표기 없는 블로그
- 죽은 링크 (URL liveness 검증 통과 못 한 것)

### 한국 자료

한국어 1차 자료가 충분하지 않은 분야가 많아, **영어 원자료를 인용하고 한국어로 평이하게 다시 쓰는** 방식을 채택했습니다. 한국 환경 적용 룰(R 시리즈, K22 등)에는 한국 직장인 생활 패턴·한식 단백질 옵션 등을 별도로 추가했습니다.

### URL liveness

`fetch_check.py`로 정기 점검합니다. 죽은 링크가 발견되면:
1. 같은 저자/매체에서 같은 자료를 다른 URL에서 재호스팅했는지 확인
2. 웨이백머신(archive.org) 스냅샷이 있는지 확인
3. 둘 다 안 되면 같은 결론을 가진 다른 출처로 교체 + 신뢰도 재평가

---

## 13. 문의 / 기여

### 룰 추가/수정 제안

마스터 CSV의 해당 행에 변경사항을 적고 PR을 올리거나, 이슈로 룰 ID + 변경 사유 + 새 출처를 함께 남겨주세요.

### 출처 신뢰도 이의제기

별점 강등/승격 의견은 다음을 함께 제시해 주세요:
- 현재 별점
- 제안 별점
- 근거 (메타분석/학회 입장/대체 출처)

### 새 분류 / 새 모듈 제안

7모듈 / 18분류 구조 변경은 v2 영역입니다. 기획팀과 협의 후 진행합니다.

### 도움이 안 됐을 때

이 가이드로 답이 안 나오면:
- 1차: [`RULEBASE_V2.md`](./RULEBASE_V2.md) 매트릭스에서 키워드 검색
- 2차: [`workout_knowledge_base.csv`](./workout_knowledge_base.csv)에서 컬럼 필터
- 3차: 이슈 생성 (어떤 시나리오에서 막혔는지 명시)

---

<div align="center">

**SAiM Exercise Data v1.0** · 2026-05-03 발행

이 자료는 사용자에게 더 나은 운동 코칭을 제공하기 위한 근거가 됩니다.
출처는 명확히, 룰은 검증 가능하게, 사용자 안전은 최우선으로.

</div>
