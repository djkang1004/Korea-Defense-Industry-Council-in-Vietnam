"""조사 프롬프트 패키지 생성.

모든 프롬프트는 LLM 중립적이며(ChatGPT·Gemini·Perplexity·Claude 공통 투입),
답변을 '코드 | 항목 | 답변 | 구분 | 출처 | 기준일' 표로 강제해 merge 단계에서 자동 정렬된다.
"""

from __future__ import annotations

from pathlib import Path

ROW_HEADER = "| 코드 | 항목 | 답변 | 구분 | 출처 | 기준일 |"
ROW_RULE = "|---|---|---|---|---|---|"

OUTPUT_RULES = f"""## 답변 규칙 (반드시 준수)
1. 아래 표 형식으로만 답하십시오. 질문 코드 1개당 1행, 코드는 그대로 유지합니다.
{ROW_HEADER}
{ROW_RULE}
2. **구분** 칸에는 다음 셋 중 하나만 씁니다.
   - `확인된 사실`: 공식 통계·법령·기관 발표·신뢰 가능한 보도로 출처 URL 제시 가능
   - `추정`: 출처 자료를 근거로 한 합리적 추정(계산 근거를 답변에 명시)
   - `미확인`: 신뢰 가능한 근거를 찾지 못함 — 추측으로 채우지 말 것
3. **출처** 칸에는 기관·매체명과 URL을 씁니다. URL이 없으면 `확인된 사실`로 분류할 수 없습니다.
4. 수치에는 단위·통화·연도를 반드시 붙이고, 환산했다면 환율·기준일을 밝힙니다.
5. 법령은 번호(예: Decree 31/2021/ND-CP)와 시행일·개정 여부를 함께 씁니다. 2025년 베트남 정부조직·행정구역 개편 이후 변경 사항을 반영하십시오.
6. 표 아래에 다음 두 소절을 추가합니다.
   - `### 출처 간 상충` — 자료마다 수치·해석이 다른 경우
   - `### 추가 확인 권고` — 현지 기관 문의·전문가 검토가 필요한 사항
7. 이 답변은 법률·세무 자문이 아닌 조사 자료입니다. 결론을 단정하지 말고 근거 수준을 명확히 하십시오.
"""


def company_brief(data: dict, diag: dict) -> str:
    c, v = data["company"], data["vietnam"]
    ctx = diag["context"]
    lines = [
        f"- 기업: {ctx['company']} ({c.get('country') or '대한민국'}, 설립 {c.get('established_year') or '미상'}, 임직원 {c.get('employees') or '미상'}명)",
        f"- 업종: {c.get('industry') or '미상'} / 사업모델: {c.get('business_model') or '미상'}",
        f"- 주력 제품: {ctx['products']} ({ctx['hs_codes']})",
        f"- 수출 경험: {c.get('export_experience') or '미상'}",
        f"- 보유 인증: {', '.join(c.get('certifications') or []) or '미상'}",
        f"- 베트남 현황: {v.get('current_presence')} / 기존 파트너: {v.get('existing_partners') or '없음'}",
        f"- 목표: {ctx['objective']} / 목표 고객: {ctx['customers']} / 목표 지역: {ctx['cities']}",
        f"- 진출 단계: {v.get('entry_stage')} / 예산: {v.get('budget_usd_k') or '미상'}천 달러 / 목표 시점: {v.get('timeline_months') or '미상'}개월",
    ]
    if data.get("constraints"):
        lines.append(f"- 제약 조건: {data['constraints']}")
    return "\n".join(lines)


def render_module_prompt(module: dict, data: dict, diag: dict) -> str:
    ctx = diag["context"]
    qs = "\n".join(f"- **{q['code']}** {q['q'].format(**ctx)}" for q in module["questions"])
    return f"""# [{module['id']}] {module['title']} — 조사 요청

당신은 {module['role']}입니다. 한국 기업의 베트남 진출을 지원하는 컨설팅 보고서의 근거 자료를 조사합니다.
가능하면 웹 검색으로 최신 자료(2024~2026년)를 확인하고, 베트남어·영어 1차 자료를 우선하십시오.

## 고객사 개요
{company_brief(data, diag)}

## 조사 질문
{qs}

{OUTPUT_RULES}"""


def write_prompt_pack(out_dir: Path, data: dict, diag: dict) -> list[Path]:
    pdir = out_dir / "02_prompts"
    pdir.mkdir(parents=True, exist_ok=True)
    paths = []
    for m in diag["modules"]:
        p = pdir / f"{m['id']}_{m['title'].replace('·', '_').replace(' ', '')}.md"
        p.write_text(render_module_prompt(m, data, diag), encoding="utf-8")
        paths.append(p)
        (out_dir / "03_responses" / m["id"]).mkdir(parents=True, exist_ok=True)

    guide = ["# 프롬프트 실행 가이드", "",
             "1. 각 프롬프트 파일을 2개 이상 LLM(예: ChatGPT, Gemini, Perplexity, Claude)에 그대로 붙여넣습니다.",
             "2. 답변 전문을 `03_responses/<모듈코드>/<LLM이름>.md`로 저장합니다. (예: `03_responses/MKT/chatgpt.md`)",
             "3. `python -m vnkit merge <이 폴더>` 실행 → 교차검증표(04_crossvalidation.md) 생성",
             "4. `python -m vnkit report <이 폴더> --docx` 실행 → 검증 결과가 반영된 보고서 생성", "",
             "Claude API 키가 있으면 `python -m vnkit run-llm <이 폴더>`로 Claude 답변을 자동 수집할 수 있습니다.", "",
             "| 모듈 | 파일 | 질문 수 |", "|---|---|---|"]
    for m, p in zip(diag["modules"], paths):
        guide.append(f"| {m['id']} {m['title']} | `{p.name}` | {len(m['questions'])} |")
    (pdir / "README.md").write_text("\n".join(guide) + "\n", encoding="utf-8")
    return paths
