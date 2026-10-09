"""진단 엔진: 업종 판별 → 플래그 → 핵심 쟁점 → 진출형태 점수화 → 조사 모듈 선택.

모든 판단은 규칙 기반이며 근거(reasons)를 함께 남겨, 보고서에서 '왜 이 안을 추천하는가'를
설명할 수 있게 한다. 점수는 의사결정 보조용이며 최종 판단은 PM 검토를 전제로 한다.
"""

from __future__ import annotations

from datetime import date

from . import kb
from .intake import hs_text, missing_fields, product_text


# ---------------------------------------------------------------- 업종 판별
def detect_sectors(data: dict) -> list[dict]:
    c = data["company"]
    text = " ".join(
        [c.get("industry") or "", c.get("business_model") or ""]
        + [f"{p.get('name', '')} {p.get('description', '')}" for p in c["products"]]
    ).lower()
    hits = []
    for s in kb.sectors():
        score = sum(1 for kw in s["keywords"] if kw.lower() in text)
        if score:
            hits.append((score, s))
    hits.sort(key=lambda x: -x[0])
    found = [s for _, s in hits[:2]]
    if data["sensitivity"].get("defense_or_military") and not any(s["id"] == "defense_dual_use" for s in found):
        found.insert(0, next(s for s in kb.sectors() if s["id"] == "defense_dual_use"))
    if not found:
        found = [next(s for s in kb.sectors() if s["id"] == "general")]
    return found


def effective_flags(data: dict, sectors: list[dict]) -> dict[str, bool]:
    flags = dict(data["sensitivity"])
    for s in sectors:
        for f in s.get("force_flags", []):
            flags[f] = True
    if (data["company"].get("business_model") or "").upper().find("B2G") >= 0:
        flags["government_customer"] = True
    return flags


# ---------------------------------------------------------------- 핵심 쟁점
def key_issues(data: dict, sectors: list[dict], flags: dict) -> list[dict]:
    v, c = data["vietnam"], data["company"]
    dels = data["project"]["deliverables"]
    issues: list[dict] = []

    def add(title, why, kind="전략"):
        issues.append({"title": title, "why": why, "kind": kind})

    add(
        "목표 시장의 실재성과 규모",
        f"{product_text(data)}에 대한 베트남 내 지불 의사 있는 수요가 진출 비용을 정당화할 만큼 존재하는지가 1차 판단 기준",
    )
    if not any(p.get("hs_code") for p in c["products"]):
        add("HS코드·업종코드 미확정", "관세·인증·시장접근 판단이 모두 HS/VSIC 코드에 의존 — 조기 확정 필요", "규제")
    if "entity_setup" in dels or v.get("needs_local_invoicing"):
        add(
            "진출형태 선택 (매출 발생 구조)",
            "현지 판매·인보이스 필요 여부에 따라 대표사무소는 부적합하고 법인 설립이 필요할 수 있음",
        )
    if flags.get("regulated_health"):
        add("제품 등록·공표 명의 전략", "등록 명의자를 파트너로 두면 브랜드 통제권과 파트너 교체 유연성 상실", "규제")
    if flags.get("defense_or_military") or flags.get("dual_use_or_strategic"):
        add(
            "수출통제·조달 접근 경로",
            "한국 측 수출허가(방위사업청·전략물자)와 베트남 국방 조달 구조가 거래 가능 여부를 결정 — 일반 상업 진출 논리 적용 불가",
            "규제",
        )
        add("정치·평판 리스크", "방산 거래는 외교·제재·여론 변수에 민감 — 단계별 공개 수위 관리 필요", "리스크")
    if flags.get("government_customer"):
        add("B2G 영업 구조와 반부패 통제", "입찰·조달 과정의 중개인 활용이 형사 리스크로 전이될 수 있음", "리스크")
    if flags.get("personal_data"):
        add("개인정보·데이터 현지화", "개인정보보호법(2026 시행)·사이버보안법상 영향평가·국외이전 의무", "규제")
    if v.get("local_manufacturing"):
        add("생산 거점 입지·인센티브", "공단·경제구역별 인센티브·인력·물류 조건 비교 필요", "실행")
    if "marketing_research" in dels:
        add("포지셔닝과 채널 우선순위", "한국 브랜드 프리미엄 활용 가능성과 중국산 대비 가격 경쟁력 판단", "전략")
    if v.get("current_presence") in ("distributor",):
        add("기존 유통 파트너와의 관계 정리", "직접 진출 시 독점권·재고·등록 명의 이관 조건이 협상 쟁점", "파트너")
    budget = v.get("budget_usd_k")
    if isinstance(budget, (int, float)) and budget < 50 and "entity_setup" in dels:
        add("예산 대비 진출 형태 적정성", f"초기 예산 {budget}천 달러는 법인 설립·1년 운영비에 부족할 가능성 (추정)", "실행")
    add("투자 회수 가능성", "송금·환율·대금 회수 관행을 고려한 손익분기 시점 검증 필요", "리스크")
    return issues


# ---------------------------------------------------------------- 진출형태 점수화
def _years_in_business(data: dict) -> int | None:
    y = data["company"].get("established_year")
    try:
        return date.today().year - int(y)
    except (TypeError, ValueError):
        return None


def score_entities(data: dict, flags: dict) -> list[dict]:
    v = data["vietnam"]
    stage = v.get("entry_stage")
    years = _years_in_business(data)
    budget = v.get("budget_usd_k")
    months = v.get("timeline_months")
    hiring = v.get("local_hiring_plan")

    results = []
    for opt in kb.entity_options():
        oid = opt["id"]
        score, reasons, blockers = 5.0, [], []

        def adj(delta, why):
            nonlocal score
            if not delta:
                return
            score += delta
            reasons.append(f"{'+' if delta > 0 else ''}{delta:g} {why}")

        if v.get("needs_local_invoicing") is True:
            adj({"rep_office": -4, "distributor": 0, "branch": 2, "fdi_llc": 3, "joint_venture": 2, "bcc": 1}[oid],
                "현지 직접 판매·인보이스 필요")
        elif v.get("needs_local_invoicing") is False:
            adj({"rep_office": 2, "distributor": 2, "branch": -1, "fdi_llc": -1, "joint_venture": -1, "bcc": 0}[oid],
                "현지 매출 발생 불요")
        if v.get("local_manufacturing"):
            adj({"rep_office": -5, "distributor": -3, "branch": -3, "fdi_llc": 3, "joint_venture": 2, "bcc": 0}[oid],
                "현지 생산 계획")
        if stage == "exploring":
            adj({"rep_office": 2, "distributor": 3, "branch": -1, "fdi_llc": -1, "joint_venture": -2, "bcc": -1}[oid],
                "타당성 검토 단계 — 가역적·저비용 형태 선호")
        elif stage in ("committed", "expanding"):
            adj({"rep_office": -1, "distributor": -1, "branch": 0, "fdi_llc": 2, "joint_venture": 1, "bcc": 0}[oid],
                "진출 결정 단계 — 통제력 확보 선호")
        if isinstance(budget, (int, float)):
            if budget < 50:
                adj({"rep_office": 1, "distributor": 2, "branch": -1, "fdi_llc": -2, "joint_venture": -1, "bcc": 0}[oid],
                    f"초기 예산 {budget}천 달러(소규모)")
            elif budget >= 300:
                adj({"rep_office": 0, "distributor": -1, "branch": 0, "fdi_llc": 1, "joint_venture": 1, "bcc": 0}[oid],
                    f"초기 예산 {budget}천 달러(충분)")
        if isinstance(months, (int, float)) and months <= 3:
            adj({"rep_office": 1, "distributor": 2, "branch": -2, "fdi_llc": -1, "joint_venture": -3, "bcc": -2}[oid],
                f"목표 시점 {months}개월 이내 — 단기 실행 가능성")
        if isinstance(hiring, (int, float)) and hiring >= 5:
            adj({"rep_office": 0, "distributor": -2, "branch": 1, "fdi_llc": 1, "joint_venture": 1, "bcc": -1}[oid],
                f"현지 채용 {hiring}명 이상 계획")
        if flags.get("defense_or_military"):
            adj({"rep_office": 1, "distributor": 1, "branch": -2, "fdi_llc": -2, "joint_venture": 2, "bcc": 1}[oid],
                "방산 — 외국인 단독 진입 제한, 현지 국영·지정업체 협력 구조 일반적 (검증필요)")
        if flags.get("government_customer") and not flags.get("defense_or_military"):
            adj({"rep_office": 0, "distributor": 1, "branch": 0, "fdi_llc": 0, "joint_venture": 1, "bcc": 0}[oid],
                "B2G — 현지 파트너의 조달 자격·네트워크 활용")
        if flags.get("regulated_health"):
            adj({"rep_office": 0, "distributor": -1, "branch": 0, "fdi_llc": 1, "joint_venture": 0, "bcc": 0}[oid],
                "보건 규제 품목 — 등록 명의 자사 보유 시 통제력 확보")

        if oid == "rep_office" and years is not None and years < 1:
            blockers.append("설립 1년 미만 — 대표사무소 자격 미충족 (Decree 07/2016)")
        if oid == "branch" and years is not None and years < 5:
            blockers.append("설립 5년 미만 — 지점 자격 미충족 (Decree 07/2016)")
        if oid in ("rep_office", "branch") and years is None:
            reasons.append("설립연도 미입력 — 자격 요건 확인 필요")
        if oid == "rep_office" and v.get("needs_local_invoicing"):
            blockers.append("대표사무소는 영리활동·인보이스 발행 불가")

        results.append({**opt, "score": round(score, 1), "reasons": reasons, "blockers": blockers})

    results.sort(key=lambda r: (bool(r["blockers"]), -r["score"]))
    return results


def recommendation(scored: list[dict], data: dict) -> dict:
    viable = [r for r in scored if not r["blockers"]]
    primary = viable[0] if viable else scored[0]
    alt = viable[1] if len(viable) > 1 else None
    phased = None
    # 단계적 경로: 탐색 단계에서 법인형 안이 2위권이면 '선 저비용 → 후 법인' 제시
    if alt and {primary["id"], alt["id"]} & {"distributor", "rep_office"} and {primary["id"], alt["id"]} & {"fdi_llc", "joint_venture"}:
        first, second = (primary, alt) if primary["id"] in ("distributor", "rep_office") else (alt, primary)
        phased = f"1단계 {first['name']}로 시장 검증(6~12개월) → 성과 기준 충족 시 2단계 {second['name']} 전환"
    return {"primary": primary, "alternative": alt, "phased": phased}


# ---------------------------------------------------------------- 조사 모듈
def select_modules(data: dict, flags: dict) -> list[dict]:
    keys = set(data["project"]["deliverables"]) | {k for k, val in flags.items() if val}
    return [m for m in kb.modules() if keys & set(m["when"])]


def build_context(data: dict) -> dict:
    c, v = data["company"], data["vietnam"]
    sec_names = [s["name"] for s in data["_sectors"]]
    return {
        "company": c.get("name") or "고객사",
        "products": product_text(data),
        "sector": "·".join(sec_names),
        "cities": ", ".join(v["target_cities"]),
        "customers": v.get("target_customers") or "목표 고객(미정의)",
        "objective": v.get("objective") or "베트남 시장 진출",
        "hs_codes": hs_text(data),
    }


def diagnose(data: dict) -> dict:
    sectors = detect_sectors(data)
    data["_sectors"] = sectors
    flags = effective_flags(data, sectors)
    scored = score_entities(data, flags)
    return {
        "sectors": sectors,
        "flags": flags,
        "missing": missing_fields(data),
        "issues": key_issues(data, sectors, flags),
        "entities": scored,
        "recommendation": recommendation(scored, data),
        "modules": select_modules(data, flags),
        "context": build_context(data),
        "common_rules": kb.common_rules(),
    }
