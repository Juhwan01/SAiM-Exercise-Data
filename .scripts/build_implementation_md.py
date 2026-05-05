#!/usr/bin/env python3
"""
IMPLEMENTATION.md 생성기

입력:
- rules/{ID}.yaml (153장)
- workout_knowledge_base.csv (마스터, 행 번호 추적용)
- RULEBASE.md (5목표 × 7모듈 매트릭스)

출력:
- IMPLEMENTATION.md
  · 룰 153개 각각을 "코드로 바로 옮길 수 있는" 명세로 정리
  · 모듈 7개 + 별도 레이어 3개로 그룹핑
  · 사용자/PM/개발자/디자이너가 같이 읽도록 평이한 한국어
"""

from __future__ import annotations

import csv
import re
import sys
from collections import OrderedDict, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = ROOT / "rules"
MASTER_CSV = ROOT / "workout_knowledge_base.csv"
RULEBASE_MD = ROOT / "RULEBASE.md"
OUT = ROOT / "IMPLEMENTATION.md"


MODULES = [
    "온보딩",
    "세션 시작",
    "세트별 처방",
    "세트 후 학습",
    "메조사이클 관리",
    "영양·회복",
    "행동·안전",
]
GOALS = ["다이어트", "벌크업", "스트렝스", "근육량 증가", "건강증진"]


def load_rules() -> dict[str, dict]:
    rules: dict[str, dict] = {}
    for path in sorted(RULES_DIR.glob("*.yaml")):
        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        rules[data["ID"]] = data
    return rules


def load_master_rows() -> dict[str, int]:
    """ID → 마스터 CSV 행 번호 (1-indexed, 헤더 제외)."""
    rows: dict[str, int] = {}
    with MASTER_CSV.open(encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for i, row in enumerate(reader, start=1):
            rows[row[0]] = i
    return rows


def function_name(rule_id: str, name: str) -> str:
    """ID + 이름을 합쳐 코드용 함수명 후보 생성."""
    base = re.sub(r"[^\w]+", "_", name).strip("_").lower()
    base = re.sub(r"_+", "_", base)
    if not base:
        base = "rule"
    return f"{rule_id.lower()}_{base}"


def goal_module_index(rules: dict[str, dict]) -> dict[str, dict[str, list[str]]]:
    """모듈 → 목표 → [ID 리스트]"""
    idx: dict[str, dict[str, list[str]]] = {m: {g: [] for g in GOALS} for m in MODULES}
    for rid, rule in rules.items():
        for slot in (rule.get("적용_위치") or {}).get("매트릭스") or []:
            mod = slot["모듈"]
            goal = slot["목표"]
            if mod in idx and goal in idx[mod]:
                if rid not in idx[mod][goal]:
                    idx[mod][goal].append(rid)
    return idx


def unique_ids_for_module(matrix_idx, module: str) -> list[str]:
    seen: list[str] = []
    for goal in GOALS:
        for rid in matrix_idx[module][goal]:
            if rid not in seen:
                seen.append(rid)
    return seen


def goals_for_rule_in_module(matrix_idx, module: str, rid: str) -> list[str]:
    return [g for g in GOALS if rid in matrix_idx[module][g]]


def render_rule_block(rule: dict, master_rows: dict[str, int], context_module: str | None,
                      matrix_idx) -> str:
    rid = rule["ID"]
    name = rule.get("이름", "")
    classification = rule.get("분류", "")
    one_line = (rule.get("한줄설명") or "").strip()
    when = (rule.get("언제_발동") or "").strip()
    inputs = rule.get("필요한_정보") or []
    output = (rule.get("하는_일") or "").strip()
    example = (rule.get("활용_예시") or "").strip()

    evidence = rule.get("근거") or {}
    src = evidence.get("출처", "")
    url = (evidence.get("주소") or "").strip()
    star = evidence.get("신뢰도", "")

    usage = rule.get("쓰임새") or {}
    usage_tags = []
    if usage.get("운동_추천"):
        usage_tags.append("운동 추천")
    if usage.get("실시간_코칭"):
        usage_tags.append("실시간 코칭")
    if usage.get("지식베이스"):
        usage_tags.append("지식베이스")

    matrix_slots = (rule.get("적용_위치") or {}).get("매트릭스") or []
    layers = (rule.get("적용_위치") or {}).get("별도_레이어") or []

    row_num = master_rows.get(rid)

    fname = function_name(rid, name)

    lines: list[str] = []
    lines.append(f"### {rid} — {name}")
    lines.append("")
    # 데이터 추적 1줄
    csv_ref = f"`workout_knowledge_base.csv` {row_num}행 (ID `{rid}`)" if row_num else f"ID `{rid}`"
    lines.append(f"- **데이터**: {csv_ref} → [`rules/{rid}.yaml`](./rules/{rid}.yaml)")
    if url:
        lines.append(f"- **근거**: {src} — [{url}]({url}) — {star}")
    else:
        lines.append(f"- **근거**: {src} — {star}")
    lines.append(f"- **분류**: {classification}")
    if when:
        lines.append(f"- **시점**: {when}")
    if usage_tags:
        lines.append(f"- **쓰임새**: {', '.join(usage_tags)}")
    lines.append("")

    # 한줄설명
    if one_line:
        lines.append(f"**무슨 룰**: {one_line}")
        lines.append("")

    # 받는 정보
    if inputs:
        lines.append("**받는 정보**")
        for x in inputs:
            lines.append(f"- {x}")
    else:
        lines.append("**받는 정보**: 없음 (지식베이스 표시용)")
    lines.append("")

    # 내놓는 것
    if output:
        lines.append(f"**내놓는 것**: {output}")
        lines.append("")

    # 예시
    if example:
        lines.append(f"**예시**: {example}")
        lines.append("")

    # 들어가는 칸 (해당 모듈 컨텍스트면 어떤 목표에 들어가는지만, 외부 컨텍스트면 전체)
    if context_module:
        goals_here = goals_for_rule_in_module(matrix_idx, context_module, rid)
        if goals_here:
            lines.append(f"**[{context_module}]에서 적용 목표**: {' · '.join(goals_here)}")
        # 다른 모듈에도 등장하면 알려줌
        other_mods = sorted({s["모듈"] for s in matrix_slots if s["모듈"] != context_module})
        if other_mods:
            lines.append(f"**다른 모듈에도 등장**: {', '.join(other_mods)}")
    else:
        # 모듈 외 컨텍스트(별도 레이어 섹션 등)
        if matrix_slots:
            grouped = defaultdict(list)
            for s in matrix_slots:
                grouped[s["모듈"]].append(s["목표"])
            cells = []
            for mod, gs in grouped.items():
                cells.append(f"{mod}({' · '.join(gs)})")
            lines.append(f"**들어가는 매트릭스 칸**: {' / '.join(cells)}")
    if layers:
        lines.append(f"**별도 레이어**: {', '.join(layers)}")
    lines.append("")

    # 함수 시그니처 제안
    lines.append("**함수 시그니처(제안)**")
    lines.append("```python")
    if inputs:
        param_lines = [param_with_comment(x) for x in inputs]
        body = "\n    ".join(param_lines)
        lines.append(f"def {fname}(\n    {body}\n):")
    else:
        lines.append(f"def {fname}():")
    out_short = (output[:60] + "…") if len(output) > 60 else output
    lines.append(f"    \"\"\"{rid}: {name}. {out_short}\"\"\"")
    lines.append(f"    ...  # 근거: {url or src}")
    lines.append("```")
    lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def normalize_param(s: str) -> str:
    """필요한_정보 한 줄 → 파이썬 파라미터 이름만 (식별자 규칙 보장)."""
    s = s.strip().rstrip(".")
    base = re.sub(r"\s*\(.*?\)\s*", "", s).strip()
    base = re.sub(r"[^\w가-힣]+", "_", base).strip("_").lower()
    if not base:
        base = "x"
    if base[0].isdigit():
        base = "_" + base
    return base


def param_with_comment(s: str) -> str:
    """파라미터 한 줄: `name,  # 원문` 형식. 콤마는 주석 앞에."""
    s_clean = s.strip().rstrip(".")
    name = normalize_param(s)
    if name == s_clean.lower():
        return f"{name},"
    return f"{name},  # {s_clean}"


# ---------------- 문서 빌드 ----------------

def build_module_section(module: str, matrix_idx, rules, master_rows) -> str:
    out: list[str] = []
    ids = unique_ids_for_module(matrix_idx, module)
    out.append(f"## 모듈 {MODULES.index(module)+1} — {module}")
    out.append("")
    out.append(_module_intro(module, len(ids)))
    out.append("")
    # 룰 카운트 표
    out.append("| 목표 | 들어가는 룰 |")
    out.append("|---|---|")
    for g in GOALS:
        out.append(f"| {g} | {', '.join(matrix_idx[module][g]) or '—'} |")
    out.append("")
    out.append(f"**고유 룰 수: {len(ids)}**")
    out.append("")

    # 분류별로 그룹
    groups = group_by_class(ids, rules)
    for cls, group_ids in groups.items():
        out.append(f"### 분류: {cls}")
        out.append("")
        for rid in group_ids:
            out.append(render_rule_block(rules[rid], master_rows, module, matrix_idx))
    return "\n".join(out)


def group_by_class(ids: list[str], rules: dict[str, dict]) -> "OrderedDict[str, list[str]]":
    groups: "OrderedDict[str, list[str]]" = OrderedDict()
    for rid in ids:
        cls = rules[rid].get("분류", "기타")
        groups.setdefault(cls, []).append(rid)
    return groups


_MODULE_INTROS = {
    "온보딩": "최초 1회. 사용자 분류·안전 게이트·1RM 추정·영양 모드·시작 무게를 잡는다. 이 모듈이 끝나면 그 사람만의 시작점이 생긴다.",
    "세션 시작": "매 세션. 워밍업과 그날 컨디션을 반영해 첫 무게를 잡고, 가벼운 안전 점검을 한다.",
    "세트별 처방": "매 세트 직전. 무게·횟수·휴식·폼큐·호흡을 결정해 화면에 띄운다.",
    "세트 후 학습": "매 세트 직후. 사용자 입력(RPE/실패 여부)을 받아 다음 세트와 다음 세션 무게를 보정한다.",
    "메조사이클 관리": "주 단위. 운동량(볼륨)을 늘리거나 줄이고, 회복주(디로드)를 배치한다.",
    "영양·회복": "일 단위. 칼로리·단백질·수분·수면·보충제를 처방한다.",
    "행동·안전": "백그라운드. 동기·습관·이탈을 관리하고 한국 환경(헬스장·식당·날씨)에 맞춘다.",
}


def _module_intro(module: str, n: int) -> str:
    return _MODULE_INTROS.get(module, "")


def build_layer_section(rules, master_rows) -> str:
    out: list[str] = []
    out.append("## 별도 레이어 — 모듈 위에 얹는 안전 필터")
    out.append("")
    out.append("매트릭스 룰을 실행하기 **전에** 항상 먼저 통과해야 하는 가드들. 사용자 상태(나이·질환·부상·피로)에 따라 매트릭스 룰을 차단·치환·완화한다.")
    out.append("")

    layer_buckets: "OrderedDict[str, list[str]]" = OrderedDict([
        ("모집단 분기", []),
        ("부상 이벤트 트리거", []),
        ("메타 룰", []),
    ])
    for rid, rule in sorted(rules.items()):
        for layer in (rule.get("적용_위치") or {}).get("별도_레이어") or []:
            if layer in layer_buckets and rid not in layer_buckets[layer]:
                layer_buckets[layer].append(rid)

    layer_intros = {
        "모집단 분기": "노인·청소년·만성질환(당뇨·고혈압·이상지질혈증·골관절염) 사용자에 대해 일반 룰을 차단하거나 강도를 낮춘다. 온보딩에서 한 번 분류된 라벨이 평생 따라다니며 매 룰 호출 직전에 검사된다.",
        "부상 이벤트 트리거": "사용자가 운동 중 통증을 입력하면 즉시 발동. 일반 매트릭스를 중단시키고 부상 전용 흐름(통증 평가 → 대체 운동 → 의료 의뢰)으로 갈아탄다.",
        "메타 룰": "운동 선택 단계에서 ‘어떤 종목을 쓸지’의 가중치 함수. 다른 룰의 입력값을 만든다.",
    }

    for layer, ids in layer_buckets.items():
        out.append(f"### {layer}")
        out.append("")
        out.append(layer_intros[layer])
        out.append("")
        out.append(f"**들어가는 룰**: {', '.join(ids) if ids else '없음'}")
        out.append("")
        for rid in ids:
            out.append(render_rule_block(rules[rid], master_rows, None, None))
    return "\n".join(out)


def build_orphan_section(rules, master_rows, all_module_ids: set[str], all_layer_ids: set[str]) -> str:
    """매트릭스에도 별도 레이어에도 안 들어간 룰 (J01 등)."""
    out: list[str] = []
    orphans = [rid for rid in sorted(rules) if rid not in all_module_ids and rid not in all_layer_ids]
    if not orphans:
        return ""
    out.append("## 부록 A — 매핑 미정 룰")
    out.append("")
    out.append("매트릭스에도 별도 레이어에도 자동 매핑되지 않은 룰. `GAPS.md` §2 참고. 자료 추가 후 매핑 결정 필요.")
    out.append("")
    for rid in orphans:
        out.append(render_rule_block(rules[rid], master_rows, None, None))
    return "\n".join(out)


def build_function_index(rules) -> str:
    out: list[str] = []
    out.append("## 부록 B — 함수 시그니처 인덱스 (개발자용)")
    out.append("")
    out.append("ID 순. 코드에 옮길 때 import 표 대신 사용.")
    out.append("")
    out.append("| ID | 분류 | 함수명 후보 | 받음 | 내놓음 |")
    out.append("|---|---|---|---|---|")
    for rid in sorted(rules):
        r = rules[rid]
        name = r.get("이름", "")
        cls = r.get("분류", "")
        fname = function_name(rid, name)
        ins = ", ".join(r.get("필요한_정보") or []) or "—"
        out_ = (r.get("하는_일") or "").replace("|", "／") or "—"
        out.append(f"| {rid} | {cls} | `{fname}` | {ins} | {out_} |")
    return "\n".join(out)


def build_header(n_rules: int, n_per_module: list[int], n_layers: list[int]) -> str:
    return f"""# 룰베이스 구현 명세 (IMPLEMENTATION.md)

근거 기반 운동 코칭 앱의 153개 룰을 **코드로 바로 옮길 수 있는** 형태로 정리한 문서. PM·개발자·디자이너·도메인 전문가가 같이 읽는다.

## 이 문서가 뭐냐
- 룰 카드 153장(`rules/{{ID}}.yaml`)을 사람이 읽기 쉬운 형태로 다시 펼친 것
- 룰 한 개 = 함수 한 개. 입력·계산·출력·근거를 명시
- **추측은 들어가지 않는다**. 모든 줄은 마스터 CSV 행 또는 룰 카드 필드에서 왔고, 출처는 매 항목 옆에 붙어 있다

## 데이터가 어디서 왔는지 (중요)
```
workout_knowledge_base.csv (153행, 14컬럼)   ← 진실의 원천
        ↓ 1:1 변환
rules/{{ID}}.yaml (153장)                     ← 정형 룰 카드
        ↓ 모듈/목표/근거로 그룹핑
IMPLEMENTATION.md (이 문서)                  ← 사람이 읽고 코드로 옮기는 명세
        ↓ 함수 1개씩 구현
실제 코드 (다음 단계)
```
- 마스터 CSV 컬럼: `ID, 분류, 항목, 적용 시점, 운동 추천, 실시간 코칭, 지식베이스, 핵심 룰 (한 줄), 입력값, 출력값/동작, 활용 예시, 출처, URL, 신뢰도`
- 매 룰 블록 상단 `데이터` 줄에서 **CSV 몇 행에서 왔는지**를 명시한다 (예: `workout_knowledge_base.csv 11행 (ID A11)`)

## 룰 1장 명세 양식
```
### {{ID}} — {{이름}}
- 데이터: CSV 몇 행 → rules/{{ID}}.yaml
- 근거: 출처 — URL — 별 1~3개
- 분류 / 시점 / 쓰임새

무슨 룰: 한 문장 요약
받는 정보: 입력 변수 목록
내놓는 것: 출력 1줄
예시: 활용 사례 1개

[모듈 내 어느 목표에 들어가는지] / [별도 레이어 소속]

함수 시그니처(제안):
def {{rid}}_{{name}}(...): ...
```

## 모듈 7개 + 별도 레이어 3개

| # | 이름 | 언제 작동 | 룰 수(고유) |
|---|---|---|---|
| 1 | 온보딩 | 최초 1회 | {n_per_module[0]} |
| 2 | 세션 시작 | 매 세션 시작 | {n_per_module[1]} |
| 3 | 세트별 처방 | 매 세트 직전 | {n_per_module[2]} |
| 4 | 세트 후 학습 | 매 세트 직후 | {n_per_module[3]} |
| 5 | 메조사이클 관리 | 주 단위 | {n_per_module[4]} |
| 6 | 영양·회복 | 일 단위 | {n_per_module[5]} |
| 7 | 행동·안전 | 백그라운드 | {n_per_module[6]} |
| L | 모집단 분기 | 매 룰 호출 직전 (가드) | {n_layers[0]} |
| Q | 부상 이벤트 트리거 | 사용자 통증 입력 시 | {n_layers[1]} |
| F | 메타 룰 | 운동 선택 가중치 | {n_layers[2]} |

총 룰 카드: **{n_rules}장** (마스터 CSV 153행과 1:1)

## 신뢰도 표기
- ★★★ — 메타분석·포지션 스테이트먼트·합의 가이드라인
- ★★☆ — 좋은 1차 연구·표준 교과서·평판 있는 코칭 매뉴얼
- ★☆☆ — 블로그·수정 의견·업계 통계 (소수만 사용)

분포(GAPS.md 기준): ★★★ 95개(62%) · ★★☆ 52개(34%) · ★☆☆ 6개(4%)

---

"""


def main() -> None:
    rules = load_rules()
    master_rows = load_master_rows()
    matrix_idx = goal_module_index(rules)

    n_per_module = [len(unique_ids_for_module(matrix_idx, m)) for m in MODULES]
    layer_counts = {"모집단 분기": 0, "부상 이벤트 트리거": 0, "메타 룰": 0}
    for rule in rules.values():
        for layer in (rule.get("적용_위치") or {}).get("별도_레이어") or []:
            if layer in layer_counts:
                layer_counts[layer] += 1
    n_layers = [layer_counts["모집단 분기"], layer_counts["부상 이벤트 트리거"], layer_counts["메타 룰"]]

    parts: list[str] = []
    parts.append(build_header(len(rules), n_per_module, n_layers))

    for module in MODULES:
        parts.append(build_module_section(module, matrix_idx, rules, master_rows))
        parts.append("")

    parts.append(build_layer_section(rules, master_rows))
    parts.append("")

    all_module_ids: set[str] = set()
    for module in MODULES:
        all_module_ids.update(unique_ids_for_module(matrix_idx, module))
    all_layer_ids: set[str] = set()
    for rid, rule in rules.items():
        if (rule.get("적용_위치") or {}).get("별도_레이어"):
            all_layer_ids.add(rid)
    orphan = build_orphan_section(rules, master_rows, all_module_ids, all_layer_ids)
    if orphan:
        parts.append(orphan)
        parts.append("")

    parts.append(build_function_index(rules))

    OUT.write_text("\n".join(parts), encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
