"""명령행 인터페이스.

  python -m vnkit init "고객사명"            인테이크 시트 생성
  python -m vnkit build intake/고객사.yaml    진단·프롬프트·로드맵·보고서 초안 생성
  python -m vnkit run-llm output/고객사       (선택) Claude로 조사 자동 실행
  python -m vnkit merge output/고객사         LLM 답변 교차검증
  python -m vnkit report output/고객사 --docx 검증 결과 반영 보고서 재생성
  python -m vnkit all intake/고객사.yaml      build → (run-llm) → merge → report 일괄
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


from . import analyze, merge as merge_mod, prompts, render
from .intake import load_intake, slugify
from .kb import KIT_ROOT

INTAKE_TEMPLATE = KIT_ROOT / "intake" / "company_template.yaml"


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _load_project(out_dir: Path):
    intake_path = out_dir / "00_intake.yaml"
    if not intake_path.exists():
        sys.exit(f"{intake_path}가 없습니다. 먼저 build를 실행하십시오.")
    data = load_intake(intake_path)
    return data, analyze.diagnose(data)


def cmd_init(args) -> int:
    dest = KIT_ROOT / "intake" / f"{slugify(args.name)}.yaml"
    if dest.exists():
        sys.exit(f"이미 존재합니다: {dest}")
    text = INTAKE_TEMPLATE.read_text(encoding="utf-8").replace('  name: ""                   # 고객사명', f'  name: "{args.name}"', 1)
    _write(dest, text)
    print(f"인테이크 시트 생성: {dest}")
    return 0


def build(intake_path: Path, out_root: Path) -> Path:
    data = load_intake(intake_path)
    diag = analyze.diagnose(data)
    out_dir = out_root / data["_slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(intake_path, out_dir / "00_intake.yaml")
    _write(out_dir / "01_diagnosis.md", render.render_diagnosis(data, diag))
    prompts.write_prompt_pack(out_dir, data, diag)
    _write_reports(out_dir, data, diag, None, docx=False)
    return out_dir


def _write_reports(out_dir: Path, data: dict, diag: dict, merged: dict | None, docx: bool) -> list[Path]:
    paths = []
    for aud in ("external", "internal"):
        paths.append(_write(out_dir / f"05_roadmap_{aud}.md", render.render_roadmap(data, diag, aud)))
        rp = _write(out_dir / f"06_report_{aud}.md", render.render_report(data, diag, merged, aud))
        paths.append(rp)
        if docx:
            from .docx_export import md_to_docx

            paths.append(md_to_docx(rp.read_text(encoding="utf-8"), rp.with_suffix(".docx")))
    return paths


def cmd_build(args) -> int:
    out_dir = build(Path(args.intake), Path(args.out))
    data, diag = _load_project(out_dir)
    miss = diag["missing"]
    print(f"생성 완료: {out_dir}")
    print(f"  업종: {diag['context']['sector']} / 추천: {diag['recommendation']['primary']['name']}")
    print(f"  조사 모듈 {len(diag['modules'])}개: {', '.join(m['id'] for m in diag['modules'])}")
    if miss["critical"] or miss["decision"]:
        print(f"  ⚠ 미입력 항목: {', '.join(miss['critical'] + miss['decision'])}")
    return 0


def cmd_run_llm(args) -> int:
    from .llm import run_all

    out_dir = Path(args.project)
    written = run_all(out_dir, effort=args.effort, only=args.only)
    print(f"Claude 답변 {len(written)}건 저장")
    return 0


def cmd_merge(args) -> int:
    out_dir = Path(args.project)
    data, diag = _load_project(out_dir)
    payload = merge_mod.merge(out_dir, diag["modules"])
    print(f"교차검증 완료 (LLM: {', '.join(payload['llms']) or '없음'}): {json.dumps(payload['summary'], ensure_ascii=False)}")
    print(f"  → {out_dir / '04_crossvalidation.md'}")
    return 0


def cmd_report(args) -> int:
    out_dir = Path(args.project)
    data, diag = _load_project(out_dir)
    cv = out_dir / "04_crossvalidation.json"
    merged = json.loads(cv.read_text(encoding="utf-8")) if cv.exists() else None
    for p in _write_reports(out_dir, data, diag, merged, docx=args.docx):
        print(f"  → {p}")
    return 0


def cmd_all(args) -> int:
    out_dir = build(Path(args.intake), Path(args.out))
    if args.with_claude:
        from .llm import run_all

        run_all(out_dir, effort=args.effort)
    data, diag = _load_project(out_dir)
    merged = merge_mod.merge(out_dir, diag["modules"])
    _write_reports(out_dir, data, diag, merged, docx=args.docx)
    print(f"전체 파이프라인 완료: {out_dir}")
    return 0


def cmd_export_kb(args) -> int:
    """웹 앱용으로 kb/*.yaml 전체를 하나의 JSON으로 내보낸다."""
    from . import kb

    names = ["entity_types", "sector_profiles", "common_rules", "research_modules", "setup_steps", "team"]
    payload = {n: kb.load(n) for n in names}
    dest = Path(args.dest)
    _write(dest, json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"지식베이스 내보내기: {dest}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="vnkit", description="베트남 진출 자동화 키트")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init", help="인테이크 시트 생성")
    p.add_argument("name")
    p.set_defaults(fn=cmd_init)

    p = sub.add_parser("build", help="진단·프롬프트·보고서 초안 생성")
    p.add_argument("intake")
    p.add_argument("-o", "--out", default=str(KIT_ROOT / "output"))
    p.set_defaults(fn=cmd_build)

    p = sub.add_parser("run-llm", help="Claude API로 조사 자동 실행 (선택)")
    p.add_argument("project")
    p.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    p.add_argument("--only", nargs="*", help="특정 모듈만 (예: MKT REG)")
    p.set_defaults(fn=cmd_run_llm)

    p = sub.add_parser("merge", help="LLM 답변 교차검증")
    p.add_argument("project")
    p.set_defaults(fn=cmd_merge)

    p = sub.add_parser("report", help="보고서 재생성")
    p.add_argument("project")
    p.add_argument("--docx", action="store_true")
    p.set_defaults(fn=cmd_report)

    p = sub.add_parser("all", help="일괄 실행")
    p.add_argument("intake")
    p.add_argument("-o", "--out", default=str(KIT_ROOT / "output"))
    p.add_argument("--with-claude", action="store_true")
    p.add_argument("--effort", default="high")
    p.add_argument("--docx", action="store_true")
    p.set_defaults(fn=cmd_all)

    p = sub.add_parser("export-kb", help="웹 앱용 지식베이스 JSON 내보내기")
    p.add_argument("dest")
    p.set_defaults(fn=cmd_export_kb)

    args = ap.parse_args(argv)
    return args.fn(args)
