"""인테이크 YAML 로드·정규화·결측 점검."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

ALL_DELIVERABLES = ("market_research", "marketing_research", "entity_setup", "trade")

# 결측 시 판단 품질에 큰 영향을 주는 항목 (경로, 설명)
CRITICAL_FIELDS = [
    ("company.name", "고객사명"),
    ("company.industry", "업종"),
    ("company.products", "주력 제품·서비스"),
    ("vietnam.objective", "진출 목적"),
    ("vietnam.target_customers", "목표 고객"),
]
DECISION_FIELDS = [
    ("company.established_year", "설립연도 (사무소·지점 자격 판단)"),
    ("vietnam.needs_local_invoicing", "현지 직접 판매·인보이스 필요 여부"),
    ("vietnam.local_manufacturing", "현지 생산 계획"),
    ("vietnam.budget_usd_k", "초기 예산"),
    ("vietnam.timeline_months", "목표 시점"),
    ("vietnam.local_hiring_plan", "현지 채용 계획"),
]


def _get(d: dict, dotted: str):
    cur = d
    for key in dotted.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _empty(v) -> bool:
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, list):
        return not any(
            (not _empty(x)) if not isinstance(x, dict) else any(not _empty(y) for y in x.values())
            for x in v
        )
    return False


def slugify(name: str) -> str:
    s = re.sub(r"[^\w가-힣-]+", "_", name.strip()).strip("_")
    return s or "client"


def load_intake(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return normalize(data)


def normalize(data: dict) -> dict:
    data.setdefault("project", {})
    data.setdefault("company", {})
    data.setdefault("vietnam", {})
    data.setdefault("sensitivity", {})
    p, c, v = data["project"], data["company"], data["vietnam"]

    p["report_audience"] = (p.get("report_audience") or "external").strip()
    dels = p.get("deliverables") or list(ALL_DELIVERABLES)
    p["deliverables"] = [d for d in dels if d in ALL_DELIVERABLES]

    products = [x for x in (c.get("products") or []) if isinstance(x, dict) and not _empty(x.get("name"))]
    c["products"] = products
    if isinstance(v.get("target_cities"), str):
        v["target_cities"] = [s.strip() for s in v["target_cities"].split(",") if s.strip()]
    v["target_cities"] = v.get("target_cities") or ["호찌민", "하노이"]
    v["entry_stage"] = v.get("entry_stage") or "exploring"
    v["current_presence"] = v.get("current_presence") or "none"
    for k, val in list(data["sensitivity"].items()):
        data["sensitivity"][k] = bool(val)
    data["_slug"] = slugify(c.get("name") or "client")
    return data


def missing_fields(data: dict) -> dict[str, list[str]]:
    return {
        "critical": [label for path, label in CRITICAL_FIELDS if _empty(_get(data, path))],
        "decision": [label for path, label in DECISION_FIELDS if _empty(_get(data, path))],
    }


def product_text(data: dict) -> str:
    names = [p["name"] for p in data["company"]["products"]]
    return ", ".join(names) if names else (data["company"].get("industry") or "주력 제품")


def hs_text(data: dict) -> str:
    codes = [str(p.get("hs_code")).strip() for p in data["company"]["products"] if not _empty(p.get("hs_code"))]
    if codes:
        return "HS " + ", ".join(codes)
    return f"{product_text(data)} 해당 HS코드(미확정 — 후보 HS코드 6단위 제시 요망)"
