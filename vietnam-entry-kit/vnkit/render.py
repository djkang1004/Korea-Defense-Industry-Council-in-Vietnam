"""마크다운 산출물 렌더링: 진단서, 실행 로드맵, 보고서(고객 제출본/내부 검토본)."""

from __future__ import annotations

from datetime import date

from . import kb

LEVEL = {3: "상", 2: "중", 1: "하"}


def _owner(owner_id: str, audience: str) -> str:
    t = kb.team()
    for m in t["members"]:
        if m["id"] == owner_id:
            return m["external_name"] if audience == "external" else f"{m['name']}({m['role']})"
    return t["pm"]["external_name"] if audience == "external" else t["pm"]["name"]


def _module_owner(module_id: str) -> str:
    for m in kb.team()["members"]:
        if module_id in m.get("owns", []):
            return m["id"]
    return "PM"


def _tbl(header: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "/").replace("\n", " ") for x in r) + " |")
    return "\n".join(out)


# ---------------------------------------------------------------- 리스크
def risk_matrix(data: dict, diag: dict) -> list[dict]:
    f = diag["flags"]
    v = data["vietnam"]
    rec = diag["recommendation"]["primary"]["id"]
    risks = [
        {"cat": "법률", "lvl": 3 if f.get("defense_or_military") else 2,
         "desc": "업종 시장접근 제한·인허가 범위 오해에 따른 무허가 영업 리스크",
         "mit": "VSIC·시장접근 조건을 현지 로펌 서면 의견으로 확정", "expert": "현지 투자 전문 변호사"},
        {"cat": "세무", "lvl": 2,
         "desc": "외국계약자세(FCT)·이전가격·부가세 처리 오류, 신법인세법 전환기 해석 차이",
         "mit": "거래 구조 확정 전 세무 자문, 본사-현지 간 계약서 정비", "expert": "현지 세무사·한국 국제조세 전문가"},
        {"cat": "규제", "lvl": 3 if (f.get("regulated_health") or f.get("dual_use_or_strategic")) else 2,
         "desc": "제품 등록·인증·전문검사 지연으로 출시 일정 지연", "mit": "등록 소요 기간을 일정에 버퍼로 반영, 명의자 전략 사전 결정",
         "expert": "인허가 대행 전문기관"},
        {"cat": "평판", "lvl": 3 if f.get("defense_or_military") else 1,
         "desc": "파트너 부정·SNS 이슈" + ("·방산 관련 국내외 여론" if f.get("defense_or_military") else "·제품 안전 이슈 확산" if f.get("regulated_health") else ""), "mit": "파트너 실사, 위기 커뮤니케이션 프로토콜", "expert": "PR 자문"},
        {"cat": "정치", "lvl": 3 if (f.get("defense_or_military") or f.get("government_customer")) else 1,
         "desc": "정책 변동·지정학·정부 조직개편에 따른 창구 변경", "mit": "정부 관계자 직접 접촉 이력 관리, 대사관·KOTRA 채널 병행",
         "expert": "대관 자문"},
        {"cat": "파트너", "lvl": 3 if rec in ("distributor", "joint_venture") else 2,
         "desc": "파트너 의존·독점권 분쟁·이해충돌", "mit": "KPI 연동 독점, 해지·명의 이관 조항, 단계적 권한 부여",
         "expert": "국제계약 변호사"},
        {"cat": "실행", "lvl": 2 if not (isinstance(v.get("timeline_months"), (int, float)) and v["timeline_months"] <= 3) else 3,
         "desc": "서류 공증·영사확인·인력 채용 지연", "mit": "선행 작업 병렬 진행, 주간 진척 관리", "expert": "—"},
        {"cat": "회수", "lvl": 2,
         "desc": "환율(VND) 변동, 이익 송금 요건(감사 완료·결손 없음), 대금 지급 지연 관행",
         "mit": "결제 조건(선수금·L/C) 설계, 송금 요건 사전 점검", "expert": "은행 외환 담당·회계법인"},
    ]
    if f.get("defense_or_military") or f.get("dual_use_or_strategic"):
        risks.insert(1, {"cat": "수출통제", "lvl": 3,
                         "desc": "한국 수출허가 미취득·재수출 통제·제3국 제재 저촉", "mit": "전략물자 판정·수출허가 선행, EUC 확보",
                         "expert": "무역안보 전문 변호사·방위사업청 상담"})
    return risks


# ---------------------------------------------------------------- 공통 블록
def _situation(data: dict, diag: dict) -> str:
    c, v = data["company"], data["vietnam"]
    ctx = diag["context"]
    return "\n".join([
        f"{ctx['company']}은(는) {c.get('industry') or '해당 업종'} 분야 기업으로, 주력 제품은 {ctx['products']}입니다. "
        f"베트남 진출 목적은 '{ctx['objective']}'이며, 목표 고객은 {ctx['customers']}, 우선 검토 지역은 {ctx['cities']}입니다.",
        "",
        f"- 판별 업종: {ctx['sector']}",
        f"- 현재 베트남 내 거점: {v.get('current_presence')} / 진출 단계: {v.get('entry_stage')}",
        f"- 의뢰 범위: {', '.join(_deliverable_names(data))}",
    ])


def _deliverable_names(data: dict) -> list[str]:
    names = {"market_research": "시장조사", "marketing_research": "마케팅 조사", "entity_setup": "법인·지사 설립 지원", "trade": "수출입(통관·관세·인증)"}
    return [names[d] for d in data["project"]["deliverables"]]


def _issues_block(diag: dict) -> str:
    return _tbl(["No", "구분", "핵심 쟁점", "판단 근거"],
                [[i + 1, x["kind"], x["title"], x["why"]] for i, x in enumerate(diag["issues"])])


def _options_block(diag: dict, top: int = 4) -> str:
    rows = []
    for r in diag["entities"][:top]:
        rows.append([r["name"], r["score"], " / ".join(r["pros"][:2]), " / ".join(r["cons"][:2]),
                     " / ".join(r["risks"][:1]), "★" * r["difficulty"], "; ".join(r["blockers"]) or "—"])
    return _tbl(["옵션", "적합도 점수", "장점", "단점", "주요 리스크", "실행 난이도", "제약 사항"], rows)


def _recommend_block(diag: dict, audience: str) -> str:
    rec = diag["recommendation"]
    p, a = rec["primary"], rec["alternative"]
    verb = "권고합니다" if audience == "external" else "추천"
    lines = [f"**추천안: {p['name']}** — 적합도 {p['score']}점", "",
             "판단 근거:"]
    lines += [f"- {r}" for r in p["reasons"]] or ["- (판단 근거 입력 부족)"]
    if a:
        lines += ["", f"**대안: {a['name']}** — 적합도 {a['score']}점"]
    if rec["phased"]:
        lines += ["", f"**단계적 경로({verb}):** {rec['phased']}"]
    lines += ["", f"- 법적 근거: {p['legal_basis']}", f"- 관할: {p['licensing']}",
              f"- 소요 기간: 법정 {p['timeline_statutory']} / 실무 {p['timeline_practical']}",
              f"- 자본금: {p['capital']}",
              "", "> 적합도 점수는 인테이크 정보 기반 규칙 점수이며, 최종 결정 전 현지 법률 검토가 필요합니다."]
    return "\n".join(lines)


def _regulation_block(diag: dict) -> str:
    rows = []
    for s in diag["sectors"]:
        for r in s["key_rules"]:
            rows.append([s["name"], r["text"], r["status"]])
    for r in diag["common_rules"]:
        rows.append([r["area"], r["text"], r["status"]])
    return _tbl(["영역", "주요 내용", "검증 상태"], rows)


def _risk_block(data: dict, diag: dict) -> str:
    rows = [[r["cat"], LEVEL[r["lvl"]], r["desc"], r["mit"], r["expert"]] for r in risk_matrix(data, diag)]
    return _tbl(["리스크", "수준", "내용", "대응 방안", "전문가 검토"], rows)


def _findings_block(diag: dict, merged: dict | None, audience: str) -> str:
    if not merged or not merged.get("llms"):
        return ("> 조사 결과 미반영 상태입니다. `02_prompts`의 프롬프트를 실행하고 `merge` 후 보고서를 다시 생성하면 "
                "이 섹션이 자동으로 채워집니다.")
    out = []
    for m in diag["modules"]:
        rows = []
        for q in m["questions"]:
            r = merged["results"].get(q["code"])
            if not r:
                continue
            b = r["best"]
            ans = b["answer"] if b else "조사 결과 없음"
            src = b["source"] if b else "—"
            rows.append([q["code"], b["item"] if b and b["item"] else q["q"][:40], ans, r["status"], src])
        out += [f"### {m['title']}", "", _tbl(["코드", "항목", "주요 내용", "검증 판정", "출처"], rows), ""]
    return "\n".join(out)


def _fact_split_block(diag: dict, merged: dict | None) -> str:
    """확인된 사실 / 추정 / 미확인·검증 필요 3분류 표 (사용자 기준 형식)."""
    facts, ests, unks = [], [], []
    if merged and merged.get("llms"):
        for code, r in merged["results"].items():
            b = r["best"]
            text = f"{code} {b['answer'][:90]}" if b else f"{code} {r['question'][:60]}"
            if r["status"] == "교차확인":
                facts.append(text)
            elif r["status"] in ("단일출처", "추정"):
                ests.append(text + (" (단일출처)" if r["status"] == "단일출처" else ""))
            else:
                unks.append(text + (f" [{r['status']}]"))
    for s in diag["sectors"]:
        for rule in s["key_rules"]:
            (facts if rule["status"] == "확인" else unks).append(rule["text"][:90] + " (법령 근거)")
    n = max(len(facts), len(ests), len(unks), 1)
    pad = lambda xs: xs + [""] * (n - len(xs))
    return _tbl(["확인된 사실", "합리적 추정", "미확인·검증 필요"], list(zip(pad(facts), pad(ests), pad(unks))))


def _conflicts_block(merged: dict | None) -> str:
    if not merged or not merged.get("llms"):
        return "- (교차검증 전)"
    rows = [[code, "; ".join(r["notes"])] for code, r in merged["results"].items() if r["status"] == "상충"]
    return _tbl(["코드", "상충 내용"], rows) if rows else "- 자동 탐지된 출처 간 상충 없음 (원문 대조 권장)"


# ---------------------------------------------------------------- 진단서 (내부)
def render_diagnosis(data: dict, diag: dict) -> str:
    miss = diag["missing"]
    flags = [k for k, v in diag["flags"].items() if v]
    ent_rows = [[r["name"], r["score"], "; ".join(r["reasons"]) or "—", "; ".join(r["blockers"]) or "—"] for r in diag["entities"]]
    q = "\n".join(f"- {x}" for x in miss["critical"] + miss["decision"]) or "- 없음"
    top_q = (miss["critical"] + miss["decision"])[:1]
    return f"""# 01. 사전 진단서 (내부 검토용)

생성일: {date.today().isoformat()} · 고객사: {diag['context']['company']}

## 1. 상황 정리
{_situation(data, diag)}

## 2. 입력 결측 점검
{q}

{"**고객사에 가장 먼저 확인할 질문 1개:** " + top_q[0] if top_q else "핵심 입력 결측 없음"}

## 3. 활성화된 리스크 플래그
{", ".join(flags) or "없음"}

## 4. 핵심 쟁점
{_issues_block(diag)}

## 5. 진출형태 점수 상세 (규칙 근거)
{_tbl(["옵션", "점수", "가감 근거", "차단 사유"], ent_rows)}

## 6. 추천안
{_recommend_block(diag, "internal")}

## 7. 생성된 조사 모듈
{_tbl(["모듈", "제목", "질문 수", "담당"], [[m["id"], m["title"], len(m["questions"]), _owner(_module_owner(m["id"]), "internal")] for m in diag["modules"]])}
"""


# ---------------------------------------------------------------- 로드맵
def roadmap_rows(diag: dict, audience: str) -> list[list]:
    steps_kb = kb.load("setup_steps")
    rec = diag["recommendation"]
    seq = []
    path = [rec["primary"]["id"]]
    if rec["phased"]:
        ids = [rec["primary"]["id"], rec["alternative"]["id"]]
        path = sorted(ids, key=lambda i: 0 if i in ("distributor", "rep_office") else 1)
    if diag["flags"].get("defense_or_military") or diag["flags"].get("dual_use_or_strategic"):
        seq += [("수출통제 선행", s) for s in steps_kb["defense_extra"]]
    if any(p != "distributor" for p in path):
        seq += [("공통 준비", s) for s in steps_kb["common_pre"]]
    for pid in path:
        name = next(o["name"] for o in kb.entity_options() if o["id"] == pid)
        seq += [(name, s) for s in steps_kb["steps"][pid]]
    phases = list(dict.fromkeys(ph for ph, _ in seq))
    seq = [(f"{phases.index(ph) + 1}. {ph}", s) for ph, s in seq]
    rows, week = [], 0
    for phase, s in seq:
        span = f"W{week + 1}" if s["weeks"] == 1 else f"W{week + 1}–W{week + s['weeks']}"
        rows.append([phase, s["step"], _owner(s["owner"], audience), span])
        week += max(1, s["weeks"] // 2)  # 단계 간 일부 병렬 진행 가정
    return rows


def render_roadmap(data: dict, diag: dict, audience: str) -> str:
    rows = roadmap_rows(diag, audience)
    title = "실행 로드맵" + (" (고객사 제출용)" if audience == "external" else " (내부 실행계획 — 직원별 배분)")
    body = [f"# 05. {title}", "", f"추천 경로: {diag['recommendation']['phased'] or diag['recommendation']['primary']['name']}", "",
            _tbl(["단계", "업무", "수행 조직" if audience == "external" else "담당", "예상 주차(추정)"], rows), "",
            "> 주차는 실무 경험 기반 추정이며, 일부 단계는 병렬 진행을 가정했습니다. 관할 기관 처리 기간에 따라 변동됩니다."]
    if audience == "internal":
        body += ["", "## 조사 모듈 담당 배분", "",
                 _tbl(["모듈", "담당", "산출물", "기한"],
                      [[f"{m['id']} {m['title']}", _owner(_module_owner(m["id"]), "internal"),
                        f"03_responses/{m['id']}/ 에 LLM 2개 이상 답변 저장 + 교차검증표 열람확인", "착수 후 1주"]
                       for m in diag["modules"]])]
    return "\n".join(body) + "\n"


# ---------------------------------------------------------------- 보고서
def render_report(data: dict, diag: dict, merged: dict | None, audience: str) -> str:
    ext = audience == "external"
    ctx = diag["context"]
    rec = diag["recommendation"]["primary"]
    imm = _immediate_actions(diag, ext)
    verify = _verify_items(diag, merged)
    nxt = _next_outputs(data)
    title_suffix = "" if ext else " (내부 검토본)"
    org = "SMBL" if ext else "SMBL 내부"
    return f"""# {ctx['company']} 베트남 진출 전략 보고서{title_suffix}

작성: {org} · 작성일: {date.today().isoformat()} · 범위: {', '.join(_deliverable_names(data))}

> 본 보고서는 공개 자료 및 다수 AI 리서치 결과를 교차검증해 작성한 초안이며, 법률·세무 자문을 대체하지 않습니다.
> 각 수치와 규정은 '확인된 사실 / 합리적 추정 / 미확인·검증 필요'로 구분 표기했습니다.

## 1. 요약
- 추천 진출형태: **{rec['name']}**{(' — ' + diag['recommendation']['phased']) if diag['recommendation']['phased'] else ''}
- 핵심 쟁점: {', '.join(i['title'] for i in diag['issues'][:4])}
- 최우선 리스크: {', '.join(r['cat'] for r in sorted(risk_matrix(data, diag), key=lambda r: -r['lvl'])[:3])}

## 2. 상황 정리
{_situation(data, diag)}

## 3. 핵심 쟁점
{_issues_block(diag)}

## 4. 시장·마케팅 조사 결과
{_findings_block(diag, merged, audience)}

## 5. 규제 환경
{_regulation_block(diag)}

## 6. 전략 옵션 비교
{_options_block(diag)}

## 7. 추천안
{_recommend_block(diag, audience)}

## 8. 리스크 및 전문가 검토 필요 지점
{_risk_block(data, diag)}

## 9. 실행 로드맵
{_tbl(["단계", "업무", "수행 조직" if ext else "담당", "예상 주차(추정)"], roadmap_rows(diag, audience))}

## 10. 근거 수준 구분
{_fact_split_block(diag, merged)}

### 출처 간 상충
{_conflicts_block(merged)}

## 11. {"즉시 실행 권고사항" if ext else "지금 바로 할 수 있는 일 3가지"}
{imm}

## 12. {"추가 확인이 필요한 사항" if ext else "추가 검증 필요 쟁점"}
{verify}

## 13. {"다음 단계 제안" if ext else "다음 단계에서 만들 수 있는 실무 산출물"}
{"후속 단계로 다음 산출물을 제공해 드릴 것을 제안드립니다." + chr(10) + chr(10) if ext else ""}{nxt}
"""


def _immediate_actions(diag: dict, ext: bool) -> str:
    rec = diag["recommendation"]["primary"]
    # (업무, 목적격 조사, 담당)
    acts = [
        ("HS코드·VSIC 업종코드 확정 및 시장접근 조건 서면 확인", "을", "B"),
        (f"{rec['name']} 추진을 위한 본사 서류 공증·영사확인 착수", "를", "B") if rec["id"] != "distributor"
        else ("현지 유통사 후보 롱리스트 작성 및 실사 착수", "를", "C"),
        ("목표 고객 10곳 대상 수요 검증 인터뷰(가격 수용도·구매 조건)", "를", "C"),
    ]
    if diag["flags"].get("defense_or_military") or diag["flags"].get("dual_use_or_strategic"):
        acts.insert(0, ("전략물자 사전판정 및 방위사업청 수출허가 사전 상담", "을", "B"))
        acts = acts[:3]
    if ext:
        return "\n".join(f"{i}. {a}{j} 권고합니다." for i, (a, j, _) in enumerate(acts, 1))
    return "\n".join(f"{i}. {a} — 담당: {_owner(o, 'internal')}" for i, (a, _, o) in enumerate(acts, 1))


def _verify_items(diag: dict, merged: dict | None) -> str:
    items = [f"- {x} (인테이크 미입력)" for x in diag["missing"]["critical"] + diag["missing"]["decision"]]
    for s in diag["sectors"]:
        items += [f"- {r['text']}" for r in s["key_rules"] if r["status"] != "확인"]
    items += [f"- {r['text']}" for r in diag["common_rules"] if r["status"] != "확인"][:5]
    if merged and merged.get("llms"):
        items += [f"- {code}: {r['question'][:60]} [{r['status']}]" for code, r in merged["results"].items()
                  if r["status"] in ("상충", "미확인")]
    return "\n".join(items[:20]) or "- 없음"


def _next_outputs(data: dict) -> str:
    outs = ["- 고객사 제출용 시장조사 보고서(SMBL 레터지 Word 서식)", "- 경영진 보고용 발표 슬라이드(10~15장 구조안)"]
    if "entity_setup" in data["project"]["deliverables"]:
        outs.append("- 설립 서류 체크리스트 및 신청서 초안 패키지")
    outs += ["- 현지 파트너 후보 롱리스트·실사표", "- 6개월 마케팅 실행계획 및 KPI 대시보드"]
    return "\n".join(outs)
