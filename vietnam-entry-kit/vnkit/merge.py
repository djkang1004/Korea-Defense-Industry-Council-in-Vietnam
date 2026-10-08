"""여러 LLM 답변 교차검증.

03_responses/<모듈>/<LLM>.md 파일의 표를 질문 코드 기준으로 정렬하고,
구분(사실/추정/미확인)·출처 유무·수치 상충을 자동 판정한다.
수치 상충 탐지는 휴리스틱이므로 판정 결과는 반드시 담당자가 원문과 대조해야 한다.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

CODE_RE = re.compile(r"^[A-Z]{3}-\d{2}$")
NUM_RE = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+(?:\.\d+)?)")

FACT, EST, UNK = "확인된 사실", "추정", "미확인"
STATUS_ORDER = ["교차확인", "단일출처", "상충", "추정", "미확인"]


def _norm_class(s: str) -> str:
    s = s.replace("*", "").strip()
    if "미확인" in s or "unknown" in s.lower():
        return UNK
    if "추정" in s or "estimate" in s.lower():
        return EST
    if "사실" in s or "확인" in s or "fact" in s.lower():
        return FACT
    return UNK


def parse_response(text: str) -> dict[str, dict]:
    rows = {}
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        code = cells[0].replace("*", "").strip() if cells else ""
        if not CODE_RE.match(code):
            continue
        cells += [""] * (6 - len(cells))
        rows[code] = {
            "item": cells[1],
            "answer": cells[2],
            "class": _norm_class(cells[3]),
            "source": cells[4],
            "as_of": cells[5],
            "has_url": "http" in cells[4],
        }
    return rows


def _key_number(answer: str) -> float | None:
    """답변에서 연도를 제외한 가장 큰 수치를 대표값으로 사용 (휴리스틱)."""
    vals = []
    for m in NUM_RE.findall(answer):
        try:
            x = float(m.replace(",", ""))
        except ValueError:
            continue
        if 1990 <= x <= 2100 and float(x).is_integer():
            continue
        vals.append(x)
    return max(vals) if vals else None


def judge(per_llm: dict[str, dict]) -> tuple[str, list[str]]:
    notes = []
    if not per_llm:
        return "미확인", ["답변 없음"]
    facts = [n for n, r in per_llm.items() if r["class"] == FACT and r["has_url"]]
    facts_no_url = [n for n, r in per_llm.items() if r["class"] == FACT and not r["has_url"]]
    if facts_no_url:
        notes.append(f"출처 URL 없는 '사실' 주장: {', '.join(facts_no_url)} → 추정으로 강등")
    nums = {n: _key_number(r["answer"]) for n, r in per_llm.items() if r["class"] != UNK}
    nums = {n: x for n, x in nums.items() if x}
    conflict = False
    if len(nums) >= 2:
        lo, hi = min(nums.values()), max(nums.values())
        if lo > 0 and hi / lo > 1.25:
            conflict = True
            notes.append("수치 상충: " + ", ".join(f"{n}={x:g}" for n, x in nums.items()))
    classes = {r["class"] for r in per_llm.values()}
    if FACT in classes and UNK in classes:
        notes.append("일부 LLM은 '미확인'으로 응답 — 사실 주장 출처 열람 확인 필요")
    if conflict:
        return "상충", notes
    if len(facts) >= 2:
        return "교차확인", notes
    if len(facts) == 1:
        return "단일출처", notes
    if all(r["class"] == UNK for r in per_llm.values()):
        return "미확인", notes
    return "추정", notes


def merge(out_dir: Path, modules: list[dict]) -> dict:
    resp_dir = out_dir / "03_responses"
    results: dict[str, dict] = {}
    llms_seen: set[str] = set()
    for m in modules:
        mdir = resp_dir / m["id"]
        parsed = {}
        if mdir.exists():
            for f in sorted(mdir.glob("*.md")):
                parsed[f.stem] = parse_response(f.read_text(encoding="utf-8"))
                llms_seen.add(f.stem)
        for q in m["questions"]:
            per = {llm: rows[q["code"]] for llm, rows in parsed.items() if q["code"] in rows}
            status, notes = judge(per)
            best = _pick_best(per)
            results[q["code"]] = {
                "module": m["id"],
                "question": q["q"],
                "status": status,
                "notes": notes,
                "answers": per,
                "best": best,
            }
    summary = {s: sum(1 for r in results.values() if r["status"] == s) for s in STATUS_ORDER}
    payload = {"llms": sorted(llms_seen), "summary": summary, "results": results}
    (out_dir / "04_crossvalidation.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_md(out_dir, modules, payload)
    _write_csv(out_dir, payload)
    return payload


def _pick_best(per: dict[str, dict]) -> dict | None:
    """보고서 반영용 대표 답변: 출처 있는 사실 > 사실 > 추정 > 미확인 순."""
    if not per:
        return None
    rank = lambda r: (r["class"] == FACT and r["has_url"], r["class"] == FACT, r["class"] == EST, len(r["answer"]))
    llm, row = max(per.items(), key=lambda kv: rank(kv[1]))
    return {"llm": llm, **row}


def _clip(s: str, n: int = 80) -> str:
    s = s.replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[: n - 1] + "…"


def _write_md(out_dir: Path, modules: list[dict], payload: dict) -> None:
    llms = payload["llms"]
    lines = ["# 교차검증 매트릭스", "",
             f"- 비교 대상 LLM: {', '.join(llms) if llms else '(답변 파일 없음)'}",
             "- 판정 기준: 교차확인(2개 이상 LLM이 출처 URL과 함께 사실로 제시, 수치 일치) / 단일출처 / 상충(대표 수치 25% 이상 차이) / 추정 / 미확인",
             "- ⚠ LLM이 제시한 URL은 실재하지 않을 수 있습니다. '교차확인' 항목도 담당자가 URL을 직접 열람해 '열람확인' 칸을 채운 뒤 보고서에 반영하십시오.",
             "", "## 판정 요약", "", "| " + " | ".join(STATUS_ORDER) + " |", "|" + "---|" * len(STATUS_ORDER),
             "| " + " | ".join(str(payload["summary"][s]) for s in STATUS_ORDER) + " |", ""]
    for m in modules:
        lines += [f"## [{m['id']}] {m['title']}", "",
                  "| 코드 | 판정 | " + " | ".join(llms) + " | 비고 | 열람확인 |",
                  "|---|---|" + "---|" * len(llms) + "---|---|"]
        for q in m["questions"]:
            r = payload["results"][q["code"]]
            cells = []
            for llm in llms:
                a = r["answers"].get(llm)
                cells.append(f"[{a['class']}] {_clip(a['answer'])}" if a else "—")
            lines.append(f"| {q['code']} | **{r['status']}** | " + " | ".join(cells) + f" | {_clip('; '.join(r['notes']), 120)} | ☐ |")
        lines.append("")
    (out_dir / "04_crossvalidation.md").write_text("\n".join(lines), encoding="utf-8")


def _write_csv(out_dir: Path, payload: dict) -> None:
    with (out_dir / "04_crossvalidation.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["코드", "모듈", "질문", "판정", "LLM", "구분", "답변", "출처", "기준일", "비고", "열람확인"])
        for code, r in payload["results"].items():
            if not r["answers"]:
                w.writerow([code, r["module"], r["question"], r["status"], "", "", "", "", "", "; ".join(r["notes"]), ""])
            for llm, a in r["answers"].items():
                w.writerow([code, r["module"], r["question"], r["status"], llm, a["class"], a["answer"], a["source"], a["as_of"], "; ".join(r["notes"]), ""])
