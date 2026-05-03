#!/usr/bin/env python3
"""Build RULEBASE_V2.md from master_index.json + rewrites.json.

Output structure:
  1. 머리말
  2. 5목표 × 7모듈 매트릭스
  3. 모듈별 본문 (7섹션)
  4. 별도 레이어 (모집단 분기 / 부상 트리거 / 메타 룰)
  5. 부록 — 153행 역참조 인덱스
"""

import json
from collections import OrderedDict, defaultdict
from pathlib import Path

ROOT = Path("/home/pc1/workout-knowledge")
MASTER = json.loads((ROOT / ".scripts/master_index.json").read_text(encoding="utf-8"))
REW = json.loads((ROOT / ".scripts/rewrites.json").read_text(encoding="utf-8"))
OUT = ROOT / "RULEBASE_V2.md"

GOALS = ["다이어트", "벌크업", "스트렝스", "근육량 증가", "건강증진"]
MODULES = [
    ("1", "온보딩", "최초 1회. 사용자 분류·안전 게이트·1RM 추정·영양 모드·프로그램 선택을 결정."),
    ("2", "세션 시작", "운동을 시작할 때마다 워밍업과 그날 컨디션을 반영해 첫 무게를 보정."),
    ("3", "세트별 처방", "세트마다 무게·휴식·폼큐·호흡을 결정."),
    ("4", "세트 후 학습", "세트가 끝날 때마다 사용자 입력을 받아 다음 세트·다음 세션 무게를 보정."),
    ("5", "메조사이클 관리", "주 단위로 운동량(볼륨)을 늘리고 주기적으로 디로드(쉬어가는 주)를 배치."),
    ("6", "영양·회복", "하루 단위로 칼로리·단백질·수분·수면·보충제를 처방."),
    ("7", "행동·안전", "백그라운드로 동기·습관·이탈을 관리하고 한국 환경(직장인·회식)에 맞춤."),
]
MODULE_NAMES = {m[0]: m[1] for m in MODULES}
MODULE_KEYS = [m[0] for m in MODULES]

# ----- Goal × Module → ID list -----------------------------------------------
# 기본 원칙: 모듈 설계(project_rule_base_design.md) + 5목표 매핑 가이드(project_workout_goals.md) 병합.
# 한 룰이 여러 목표에 공통이면 모든 목표에 등장 (중복 OK).

MAPPING = {
    # ============ 다이어트 ============
    ("다이어트", "1"): ["L04", "K19", "K20", "K21", "K22", "K23", "D05", "M01", "M03", "M04", "C09", "C10"],
    ("다이어트", "2"): ["I05", "I06", "I07", "I08", "P05", "E02", "E09"],
    ("다이어트", "3"): ["A01", "A02", "A07", "A08", "C02", "C04", "C07", "E07", "E08", "E10", "E13", "E14", "E16", "J02"],
    ("다이어트", "4"): ["A04", "A09", "A11", "C08", "C12", "C13", "C14"],
    ("다이어트", "5"): ["B01", "B02", "G01", "G02", "G05", "G09", "G10"],
    ("다이어트", "6"): ["K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08", "K09", "K10",
                      "K12", "K13", "K14", "K15", "K16", "K17", "K18",
                      "K19", "K20", "K21", "K22", "K23", "O01", "O02", "O03"],
    ("다이어트", "7"): ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R09", "R10"],

    # ============ 벌크업 ============
    ("벌크업", "1"): ["L04", "K19", "K20", "K21", "K22", "D05", "D06", "D02", "D10", "M01", "M03", "M04",
                    "D11", "D12", "D13", "D14", "D15", "C09", "C10"],
    ("벌크업", "2"): ["I05", "I06", "I07", "P05", "E02", "E09"],
    ("벌크업", "3"): ["A01", "A02", "A03", "A05", "A07", "A08", "A10", "C01", "C02", "C03", "C05", "C07", "C08",
                    "E05", "E07", "E08", "E10", "E11", "E12", "E13", "E14", "E16", "E17", "J02"],
    ("벌크업", "4"): ["A04", "A09", "A11", "A12", "A13", "C08", "C12", "C13", "C14", "C15"],
    ("벌크업", "5"): ["B01", "B02", "B03", "B04", "B05", "D01", "D02", "D03", "G01", "G02", "G03",
                    "G05", "G07", "G10", "G11", "C06", "C11"],
    ("벌크업", "6"): ["K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08", "K09", "K10", "K11",
                    "K12", "K13", "K14", "K15", "K16", "K17", "K18", "O01"],
    ("벌크업", "7"): ["R01", "R02", "R03", "R04", "R06", "R07", "R10"],

    # ============ 스트렝스 ============
    ("스트렝스", "1"): ["L04", "D06", "D07", "D08", "D09", "M01", "M03", "M04",
                      "D11", "D12", "D13", "D14", "D15", "C09", "C10"],
    ("스트렝스", "2"): ["I05", "I06", "I08", "P05", "E02", "E09"],
    ("스트렝스", "3"): ["A01", "A02", "A03", "A05", "A07", "A08", "A10", "A14",
                      "C01", "C02", "C03", "C05", "C07",
                      "E05", "E06", "E07", "E08", "E10", "E11", "E12", "E13", "E14", "E16", "E17",
                      "E01", "E03", "J02"],
    ("스트렝스", "4"): ["A04", "A09", "A11", "A12", "A13", "A14", "C08", "C12", "C13", "C14", "C15", "E04"],
    ("스트렝스", "5"): ["B01", "B02", "B05", "D01", "D02", "D04", "D06", "D07", "D08", "D09",
                      "G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10", "G11",
                      "C06", "C11", "I01"],
    ("스트렝스", "6"): ["K01", "K02", "K05", "K06", "K07", "K09", "K10"],
    ("스트렝스", "7"): ["R01", "R03", "R04", "R06", "R07", "R10"],

    # ============ 근육량 증가 ============
    ("근육량 증가", "1"): ["L04", "K19", "K20", "K21", "K22", "D05", "D02", "D03", "D10", "M01", "M03", "M04",
                       "D11", "D12", "D13", "D14", "D15", "C09", "C10"],
    ("근육량 증가", "2"): ["I05", "I06", "I07", "P05", "E02", "E09"],
    ("근육량 증가", "3"): ["A01", "A02", "A03", "A05", "A07", "A08", "A10", "C01", "C02", "C03", "C05", "C07",
                       "E05", "E14", "E07", "E08", "E10", "E11", "E12", "E13", "E16", "E17",
                       "F05", "J02", "J03", "J04", "J05", "J07"],
    ("근육량 증가", "4"): ["A04", "A09", "A11", "A12", "A13", "C08", "C12", "C13", "C14", "C15", "E04"],
    ("근육량 증가", "5"): ["B01", "B02", "B03", "B04", "B05", "D01", "D02", "D03", "D04", "D05",
                       "G01", "G02", "G03", "G04", "G05", "G06", "G07", "G08", "G09", "G10", "G11",
                       "C06", "C11"],
    ("근육량 증가", "6"): ["K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08", "K09", "K10", "K11",
                       "K12", "K13", "K14", "K15", "K16", "K17", "K18", "O01"],
    ("근육량 증가", "7"): ["R01", "R02", "R03", "R04", "R06", "R07", "R10",
                       "N01", "N02", "N03", "N04"],

    # ============ 건강증진 ============
    ("건강증진", "1"): ["L04", "K19", "K20", "K21", "K22", "C04", "M01"],
    ("건강증진", "2"): ["I05", "I06", "I07", "I08", "P05", "P01", "P02", "P03", "P04", "E09"],
    ("건강증진", "3"): ["A01", "A02", "A06", "C02", "C04", "C07", "C11",
                      "E05", "E06", "E07", "E08", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17",
                      "I02", "I03"],
    ("건강증진", "4"): ["A04", "C08", "I04"],
    ("건강증진", "5"): ["B01", "B02", "C06", "G01", "G02", "G05", "G09", "G10", "I01"],
    ("건강증진", "6"): ["K01", "K02", "K03", "K04", "K05", "K06", "K07", "K08", "O01", "O02", "O03"],
    ("건강증진", "7"): ["R01", "R02", "R03", "R04", "R05", "R06", "R07", "R08", "R10"],
}

# ----- 별도 레이어 (5목표 위/옆) ------------------------------------------------
LAYER_POPULATION = ["L02", "L03", "L04", "L05", "L06", "L07", "L08"]
LAYER_INJURY = ["Q01", "Q02", "Q03", "Q04", "Q05", "Q06", "J01"]
LAYER_META = ["F05"]

# ----- helpers ---------------------------------------------------------------

def item_label(rid: str) -> str:
    """평이 항목명 우선, 없으면 마스터 항목."""
    rw = REW.get(rid, {})
    return rw.get("항목_평이") or MASTER[rid]["항목"]

def core_text(rid: str) -> str:
    """평이 핵심 우선, 없으면 마스터 핵심."""
    rw = REW.get(rid, {})
    return rw.get("핵심_평이") or MASTER[rid]["핵심"]

def url(rid: str) -> str:
    return MASTER[rid]["URL"]

def cred(rid: str) -> str:
    return MASTER[rid]["신뢰도"]

def inline(rid: str) -> str:
    """[ID ★ - 평이항목](URL)"""
    return f"[{rid} {cred(rid)} - {item_label(rid)}]({url(rid)})"

CLINICAL_IDS = {"L05", "L06", "L07", "L08"}

def rule_block(rid: str) -> str:
    """- [ID ★ - 평이항목명](URL)\n  핵심 한 줄.

    L05~L08(만성질환)은 임상 처방이라 단락 내부를 줄바꿈으로 분리해
    빈도·강도·시간·형태·적색기 신호가 시각적으로 구분되게 함.
    """
    base = inline(rid)
    text = core_text(rid)
    if rid in CLINICAL_IDS:
        # ' · ' 또는 '; ' 로 구분된 임상 항목들을 마크다운 줄바꿈(2칸 + \n)으로 분리
        text = text.replace(" · ", "  \n    · ").replace("; ", "  \n    · ")
        header = "> **안전 가이드 (만성질환)** — 사전 의사 상담 필요. 적색기 신호 발생 시 즉시 운동 중단·병원 상담."
        return f"{header}\n- {base}\n    · {text}"
    return f"- {base}\n  - {text}"

# ----- build -----------------------------------------------------------------
out = []
A = out.append

# === 1. 머리말 ===
A("# 룰베이스 v2 — 운동 코칭 앱 룰 카탈로그")
A("")
A("이 문서는 운동 코칭 앱이 사용자에게 어떤 판단을 어떤 근거로 내릴지 모아둔 룰 카탈로그다. 모든 룰은 마스터 데이터셋(153행)에서 가져왔고, 각 룰 옆 링크를 누르면 1차 출처(논문·교과서·코치 글)로 바로 이동한다.")
A("")
A("## 5운동목표")
A("- **다이어트** — 체지방 감량")
A("- **벌크업** — 체중·근육량 동시 증가")
A("- **스트렝스** — 최대 근력(1회에 들 수 있는 최대 무게) 향상")
A("- **근육량 증가** — 하이퍼트로피, 근육 크기 키우기")
A("- **건강증진** — 전반적 컨디션·만성질환 예방·기초 체력")
A("")
A("## 7모듈")
A("- **[1] 온보딩** — 최초 1회. 사용자 분류·안전 게이트·1RM(한 번에 들 수 있는 최대 무게) 추정·영양 모드·프로그램을 선택")
A("- **[2] 세션 시작** — 매 세션. 워밍업과 그날 컨디션을 반영해 첫 무게를 보정")
A("- **[3] 세트별 처방** — 매 세트. 무게·휴식·폼큐·호흡을 결정")
A("- **[4] 세트 후 학습** — 매 세트. 사용자 입력을 받아 다음 세트·다음 세션 무게를 보정")
A("- **[5] 메조사이클 관리** — 주 단위. 운동량(볼륨)을 늘리고 주기적으로 디로드(쉬어가는 주)를 배치")
A("- **[6] 영양·회복** — 일 단위. 칼로리·단백질·수분·수면·보충제를 처방")
A("- **[7] 행동·안전** — 백그라운드. 동기·습관·이탈을 관리하고 한국 환경에 맞춤")
A("")
A("## 별도 레이어 3개")
A("- **모집단 분기 (안전 필터)** — L02 노인, L03 청소년, L04 사용자 분류, L05~L08 만성질환 4종. 5목표 위에 얹는 안전 필터")
A("- **부상 이벤트 트리거** — Q01~Q06. \"운동 중 통증\" 입력 시 발동되는 별도 모듈")
A("- **메타 룰** — F05 SFR(자극 대비 피로 비율). 운동 선택 단계의 가중치")
A("")
A("## 인라인 표기 규칙")
A("`[ID ★신뢰도 - 평이항목명](URL)` 형식. 신뢰도는 별 1~3개 (★★★ = 메타분석/포지션 스테이트먼트, ★★☆ = 좋은 1차 연구·교과서, ★☆☆ = 수정·블로그). 클릭하면 1차 출처로 이동.")
A("")

# === 2. 5목표 × 7모듈 매트릭스 ===
A("---")
A("")
A("## 2. 5목표 × 7모듈 매트릭스")
A("")
A("| 목표 \\ 모듈 | " + " | ".join(f"[{k}] {MODULE_NAMES[k]}" for k in MODULE_KEYS) + " |")
A("|" + "---|" * (len(MODULE_KEYS) + 1))
for goal in GOALS:
    cells = []
    for k in MODULE_KEYS:
        ids = MAPPING.get((goal, k), [])
        cells.append(", ".join(ids) if ids else "—")
    A(f"| **{goal}** | " + " | ".join(cells) + " |")
A("")

# === 3. 모듈별 본문 ===
A("---")
A("")
A("## 3. 모듈별 본문")
A("")
for mk, mname, mdesc in MODULES:
    A(f"### [{mk}] {mname}")
    A("")
    A(mdesc)
    A("")
    for goal in GOALS:
        ids = MAPPING.get((goal, mk), [])
        if not ids:
            continue
        A(f"#### {goal}")
        for rid in ids:
            A(rule_block(rid))
        A("")

# === 4. 별도 레이어 ===
A("---")
A("")
A("## 4. 별도 레이어")
A("")

A("### 4.1 모집단 분기 (안전 필터)")
A("")
A("5목표 위에 얹는 분기. 사용자 정보(나이·만성질환)에 따라 강도 자동 다운 또는 운동 종목 제한. 온보딩에서 한 번 분류하면 이후 모든 모듈 출력에 적용.")
A("")
for rid in LAYER_POPULATION:
    A(rule_block(rid))
A("")

A("### 4.2 부상 이벤트 트리거")
A("")
A("\"운동 중 통증\" 입력이 들어오면 정규 모듈 대신 발동되는 별도 분기. 급성 처치 → 단계별 복귀 → 운동 재개 기준 → 부위별 대체 운동 순으로 진행.")
A("")
for rid in LAYER_INJURY:
    A(rule_block(rid))
A("")

A("### 4.3 메타 룰 (운동 선택 가중치)")
A("")
A("운동 선택 단계에서 같은 부위 운동을 비교할 때 사용하는 가중치 룰. 5목표 모든 모듈 [3]에서 호출 가능.")
A("")
for rid in LAYER_META:
    A(rule_block(rid))
A("")

# === 5. 부록 — 전체 153행 역참조 인덱스 ===
A("---")
A("")
A("## 5. 부록 — 전체 153행 역참조 인덱스")
A("")
A("ID 알파벳 순. \"모듈\" 열은 해당 룰이 등장하는 모듈 번호(중복 등장 시 모두 표기), \"목표\" 열은 등장하는 목표(중복 시 모두 표기). 별도 레이어는 모듈 열에 `L`(모집단), `Q`(부상), `M`(메타)로 표기.")
A("")
A("### 부록 약어 사전 (본문에 자주 안 풀린 것)")
A("- **HIIT** = 고강도 인터벌 (짧고 강하게 - 쉬기 반복)")
A("- **LISS** = 저강도 지속 운동 (느리고 오래)")
A("- **OA** = 골관절염 (Osteoarthritis, 관절 연골 닳는 병)")
A("- **T2DM** = 제2형 당뇨병")
A("- **HDL / LDL** = 좋은 콜레스테롤 / 나쁜 콜레스테롤")
A("- **PFPS** = 무릎 앞쪽 통증 (Patellofemoral Pain Syndrome)")
A("- **SMART** = 목표 설정 5요소 (구체적·측정가능·달성가능·관련성·기한)")
A("- **SDT** = 자기결정성 이론 (Self-Determination Theory, 동기 부여 모델)")
A("- **DEXA** = 체성분 분석 정밀 측정 (이중에너지 X선 흡수계측)")
A("- **DUP** = 일별 변화 주기화 (Daily Undulating Periodization)")
A("- **DOMS** = 운동 후 늦게 오는 근육통 (24~72시간 후)")
A("- **PPL** = Push/Pull/Legs (밀기·당기기·하체 3분할)")
A("- **OHP** = 오버헤드 프레스 (서서 머리 위로 바벨 미는 어깨 운동)")
A("- **SS** = Starting Strength (초보 5x5 프로그램)")
A("- **GZCLP** = GZCL 초보 변형 (선형 진행 프로그램)")
A("")
A("| ID | 항목(평이) | 모듈 | 목표 | 신뢰도 | 출처 |")
A("|---|---|---|---|---|---|")

# Build reverse index
id_to_modules = defaultdict(set)
id_to_goals = defaultdict(set)
for (goal, mk), ids in MAPPING.items():
    for rid in ids:
        id_to_modules[rid].add(mk)
        id_to_goals[rid].add(goal)
for rid in LAYER_POPULATION:
    id_to_modules[rid].add("L")
for rid in LAYER_INJURY:
    id_to_modules[rid].add("Q")
for rid in LAYER_META:
    id_to_modules[rid].add("M")

# Goal short names for column compactness
goal_short = {"다이어트": "다", "벌크업": "벌", "스트렝스": "스", "근육량 증가": "근", "건강증진": "건"}

for rid in sorted(MASTER.keys()):
    label = item_label(rid)
    mods = id_to_modules.get(rid, set())
    # Order: 1-7 then L, Q, M
    mod_order = [k for k in MODULE_KEYS if k in mods] + [x for x in ["L", "Q", "M"] if x in mods]
    mod_str = ",".join(mod_order) if mod_order else "미매핑"
    goals = id_to_goals.get(rid, set())
    goal_order = [goal_short[g] for g in GOALS if g in goals]
    goal_str = ",".join(goal_order) if goal_order else "—"
    src_url = url(rid)
    A(f"| {rid} | {label} | {mod_str} | {goal_str} | {cred(rid)} | [link]({src_url}) |")

A("")
A("---")
A("")
A("## 검증 메모")
A("")
A("- 마스터 153행 전체가 부록에 등장한다 (빌드 스크립트가 자동 생성).")
A("- 5목표 각각 7모듈 중 7개 모듈 모두에 룰이 매핑돼 있다 (요구 최소 5개 충족).")
A("- 별도 레이어(L02·L03·L04·L05~L08·Q01~Q06·F05)는 5목표 매핑과 별개로 등장하며 모듈 열에 `L`/`Q`/`M`으로 표기.")
A("- 빌드 스크립트: `.scripts/build_rulebase_v2.py`. 마스터·rewrites 변경 시 재실행해 동기화.")
A("")

OUT.write_text("\n".join(out), encoding="utf-8")
print(f"Wrote {OUT} ({len(out)} lines)")

# ----- self-verify -----------------------------------------------------------
errors = []

# (1) Every master ID appears in appendix (always true since we iterate sorted MASTER.keys())
appendix_ids = set(MASTER.keys())
all_mapped_ids = set()
for ids in MAPPING.values():
    all_mapped_ids.update(ids)
all_mapped_ids.update(LAYER_POPULATION)
all_mapped_ids.update(LAYER_INJURY)
all_mapped_ids.update(LAYER_META)
unmapped = appendix_ids - all_mapped_ids
print(f"Unmapped IDs (no module/layer assignment): {sorted(unmapped)}")

# (2) Each goal must be in >= 5 modules
for goal in GOALS:
    mods_for_goal = sum(1 for k in MODULE_KEYS if MAPPING.get((goal, k)))
    print(f"{goal}: {mods_for_goal}/7 modules covered")
    if mods_for_goal < 5:
        errors.append(f"{goal} only in {mods_for_goal} modules")

# (3) All inline tags conform — spot check first
print("Sample inline:", inline("A02"))

# (4) Forbidden similes grep
content = OUT.read_text(encoding="utf-8")
forbidden = ["마치", "처럼", "같은 느낌", "느낌의"]
for tok in forbidden:
    cnt = content.count(tok)
    if cnt > 0:
        # Show context
        for i, line in enumerate(content.splitlines(), 1):
            if tok in line:
                print(f"  L{i}: {line[:120]}")
        errors.append(f"Forbidden token '{tok}' appears {cnt} times")
    else:
        print(f"Forbidden token '{tok}': 0")

if errors:
    print("ERRORS:", errors)
else:
    print("All checks passed.")
