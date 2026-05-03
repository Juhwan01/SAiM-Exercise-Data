# Workout Knowledge — Project Notes

근거 기반 운동 코칭 앱을 위한 지식베이스. 한 개의 마스터 CSV에서 세 개의 목적별 CSV가 파생되고, 다시 Google Sheets에 붙여 넣을 TSV로 빌드된다.

---

## 1. 작업 개요 (지금까지 한 것)

| 단계 | 산출물 | 비고 |
|---|---|---|
| 1. 1차 지식 수집 | `workout_knowledge_base.csv` (99 rows, 18 카테고리) | RPE·볼륨·주기화·영양·회복·부상·생리학 등 망라 |
| 2. 출처 신뢰도 검증 | `.scripts/fetch_check.py`, `fetch_retry.py`, `validate_candidates.py`, `find_replacements.py` | URL 살아있는지 확인 + 신뢰도 ★ 평가 |
| 3. 죽은 링크 / 약한 출처 교체 | `.scripts/apply_updates.py` (URL 24건 패치) | NSCA·Schoenfeld·StartingStrength·StrongerByScience 우선 |
| 4. 유료/책 광고 페이지 제거 | `.scripts/drop_paid_sources.py` — H01·H02·J06·M02 (Helms 피라미드 책) 삭제 | 무료 1차 출처만 남김 |
| 5. 목적별 분기 | `goal1_session_recommendation.csv` (67), `goal2_realtime_coaching.csv` (39), `goal3_knowledge_base.csv` (94) | 마스터의 `운동 추천 / 실시간 코칭 / 지식베이스` Y 플래그로 필터 |
| 6. Sheets 붙여넣기용 TSV 빌드 | `.scripts/build_tsv.py` → `output/sheet_*.tsv` (3개) | 4열: A(빈) · B(내용) · C(출처) · D(URL) |
| 7. 평이한 한국어 리라이트 | `.scripts/rewrites.json` | 분류·항목·핵심·적용시점을 일반 사용자용 문장으로 |
| 8. 출처 표기 정리 | `.scripts/fix_attribution.py` | 저자/매체 표기 일관화 |
| 9. MCP 연동 | `.mcp.json` + `.mcp-servers/google-sheets-mcp/` | Sheets 직접 입력 가능 (OAuth 토큰은 `.credentials/`) |

> `.bak` (`goal1.bak`, `goal2.bak`, `goal3.bak`)는 직전 안정본 스냅샷.
> `.scripts/backup/`에 변경 직전 상태 자동 보존됨 (`drop_paid_sources` 등이 타임스탬프 폴더로 백업).

---

## 2. 디렉터리 구조

```
workout-knowledge/
├─ workout_knowledge_base.csv           # 마스터 (99 rows, 14열)
├─ goal1_session_recommendation.csv     # 운동 추천 Y 필터 (67 rows)
├─ goal2_realtime_coaching.csv          # 실시간 코칭 Y 필터 (39 rows)
├─ goal3_knowledge_base.csv             # 지식베이스 Y 필터 (94 rows)
├─ goal{1,2,3}.bak                       # 직전 안정본
├─ output/
│  ├─ sheet_운동 루틴 세션.tsv          # goal1 → Sheets paste
│  ├─ sheet_실시간 코칭.tsv             # goal2 → Sheets paste
│  └─ sheet_운동 지식베이스.tsv          # goal3 → Sheets paste
├─ .scripts/
│  ├─ build_tsv.py                       # CSV → TSV 빌드
│  ├─ apply_updates.py                   # URL 일괄 패치 + TSV 재빌드
│  ├─ drop_paid_sources.py               # 유료/책 광고 행 제거
│  ├─ validate.py                        # goal 파일 ↔ 마스터 일관성 검증
│  ├─ fetch_check.py / fetch_retry.py    # URL liveness
│  ├─ find_replacements*.py              # 대체 출처 탐색
│  ├─ validate_candidates.py             # 후보 출처 신뢰도 평가
│  ├─ fix_attribution.py                 # 저자/매체 표기 정리
│  ├─ final_attempt.py / final_attempt2.py
│  ├─ rewrites.json                      # 한국어 평이 리라이트 사전
│  ├─ fetched/                           # WebFetch 캐시
│  └─ backup/                            # 변경 직전 자동 백업
├─ .mcp.json                             # google-sheets-mcp 서버 정의
├─ .mcp-servers/google-sheets-mcp/       # 빌드된 MCP 서버 (gitignore)
├─ .credentials/                         # OAuth 키 (gitignore)
├─ .claude/settings.local.json           # 도메인 화이트리스트
└─ .gitignore
```

---

## 3. 마스터 CSV 스키마

```
ID, 분류, 항목, 적용 시점,
운동 추천, 실시간 코칭, 지식베이스,        # Y/-: 어느 goal 파일로 분기되는지
핵심 룰 (한 줄),
입력값, 출력값/동작, 활용 예시,
출처, URL, 신뢰도                          # ★★★ ~ ★☆☆
```

**분류(18종)**: RPE 자율조절 · 주간 볼륨 기준 · 세트/렙/강도 처방 · 주기화 모델 · 실시간 코칭 · 운동 선택 · 측정/평가 · 회복 · 회복/디로드 · 영양 · 보충제 · 생리학 · 부상 관리 · 스트레칭 · 카디오 · 특수 모집단 · 운동 데이터셋 · 기타

**ID 컨벤션**: 분류별 알파벳 prefix (`A*`=RPE, `B*`=볼륨, `C*`=세트/렙, `D*`=주기화, `E*`=실시간, …)

---

## 4. 빌드 / 재실행 절차

전체 파이프라인은 항상 **마스터 CSV가 진실의 원천**이다. goal/TSV는 파생물.

```bash
cd C:/users/jungj/desktop/workout-knowledge

# 마스터 수정 후 goal 파일은 Y 플래그로 자동 필터되므로
# 일단은 수동 동기화 필요. validate.py로 일관성 점검:
python3 .scripts/validate.py

# URL 일괄 패치 (UPDATES 딕셔너리 수정 후)
python3 .scripts/apply_updates.py        # CSV 4개 동시 패치 + TSV 재빌드

# Sheets paste용 TSV만 다시 만들기
python3 .scripts/build_tsv.py

# 유료/책 광고 행 제거 같은 정리
python3 .scripts/drop_paid_sources.py

# URL liveness 점검
python3 .scripts/fetch_check.py
```

**TSV → Google Sheets**: 시트 탭에서 `A3` (또는 다음 빈 행) 클릭 → `output/sheet_*.tsv` 내용 그대로 붙여넣기. 4열 구조(A 빈칸 / B 내용 / C 출처 / D URL).

---

## 5. 작업 원칙

- **마스터가 진실**. goal_*.csv를 직접 손대지 말고 마스터에서 수정한 뒤 파생을 재생성하거나 일관성을 검증.
- **출처는 무료·1차**. 유료 책 광고 페이지나 SNS만 있는 출처는 제거 (`drop_paid_sources.py` 패턴).
- **신뢰도 표기 유지**. ★★★(메타분석/포지션 스테이트먼트), ★★☆(좋은 1차 연구·교과서), ★☆☆(수정·블로그). 강등은 명시적으로.
- **한국어 평이 리라이트**는 `rewrites.json`에서 ID 단위로 관리. 누락 시 원본 한국어가 fallback.
- **TSV는 자동 생성물**. 직접 편집 금지 — 항상 `build_tsv.py`로 재생성.
- **변경 전 백업**. 큰 정리 작업은 `.scripts/backup/<타임스탬프>_<목적>/`에 자동 보존.

---

## 6. 다음에 할 만한 것 (메모)

- 마스터 → goal_*.csv 자동 동기화 스크립트 (현재는 `validate.py`로 사후 검증만).
- 신규 행 추가용 템플릿/체크리스트 — ID 충돌·신뢰도·URL liveness 자동 점검.
- 카테고리별 대시보드 (행 수, 신뢰도 분포, 출처 도메인 분포).
