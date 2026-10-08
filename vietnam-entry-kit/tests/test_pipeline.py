"""파이프라인 스모크 테스트: python -m pytest tests 또는 python tests/test_pipeline.py

LLM 답변은 테스트용 가상 데이터이며 실제 시장 정보가 아니다.
"""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vnkit import analyze, cli  # noqa: E402
from vnkit.intake import load_intake  # noqa: E402
from vnkit.merge import parse_response  # noqa: E402

FAKE_A = """| 코드 | 항목 | 답변 | 구분 | 출처 | 기준일 |
|---|---|---|---|---|---|
| MKT-01 | 시장규모 | 약 2,000 백만 달러 (테스트) | 확인된 사실 | 테스트기관 https://example.org/a | 2025 |
| **MKT-02** | 세그먼트 | 기초 60% | 추정 | — | 2025 |
| MKT-03 | 수입액 | 500 백만 달러 | 확인된 사실 | https://example.org/c | 2025 |
"""
FAKE_B = """| 코드 | 항목 | 답변 | 구분 | 출처 | 기준일 |
|---|---|---|---|---|---|
| MKT-01 | 시장규모 | 약 2,100 백만 달러 (테스트) | 확인된 사실 | https://example.org/b | 2025 |
| MKT-03 | 수입액 | 900 백만 달러 | 확인된 사실 | https://example.org/d | 2025 |
| MKT-04 | 고객 | 근거 없음 | 미확인 | — | — |
"""


def test_parse_response():
    rows = parse_response(FAKE_A)
    assert set(rows) == {"MKT-01", "MKT-02", "MKT-03"}
    assert rows["MKT-01"]["has_url"] and rows["MKT-02"]["class"] == "추정"


def test_diagnosis_defense_and_cosmetics():
    d = load_intake(ROOT / "examples" / "sample_defense_optics.yaml")
    diag = analyze.diagnose(d)
    assert diag["sectors"][0]["id"] == "defense_dual_use"
    assert any(m["id"] == "DEF" for m in diag["modules"])
    assert diag["recommendation"]["primary"]["id"] in ("distributor", "rep_office")

    c = load_intake(ROOT / "examples" / "sample_cosmetics.yaml")
    diag = analyze.diagnose(c)
    assert diag["sectors"][0]["id"] == "cosmetics"
    assert diag["recommendation"]["primary"]["id"] == "fdi_llc"
    rep = next(e for e in diag["entities"] if e["id"] == "rep_office")
    assert rep["blockers"], "인보이스 필요 시 대표사무소는 차단되어야 함"


def test_full_pipeline_with_merge():
    with tempfile.TemporaryDirectory() as tmp:
        out = cli.build(ROOT / "examples" / "sample_cosmetics.yaml", Path(tmp))
        (out / "03_responses" / "MKT" / "llm_a.md").write_text(FAKE_A, encoding="utf-8")
        (out / "03_responses" / "MKT" / "llm_b.md").write_text(FAKE_B, encoding="utf-8")
        assert cli.main(["merge", str(out)]) == 0
        cv = json.loads((out / "04_crossvalidation.json").read_text(encoding="utf-8"))
        r = cv["results"]
        assert r["MKT-01"]["status"] == "교차확인"
        assert r["MKT-03"]["status"] == "상충"
        assert r["MKT-02"]["status"] == "추정"
        assert r["MKT-04"]["status"] == "미확인"
        assert cli.main(["report", str(out), "--docx"]) == 0
        ext = (out / "06_report_external.md").read_text(encoding="utf-8")
        assert "즉시 실행 권고사항" in ext and "직원 A" not in ext
        assert "MKT-01" in ext
        assert (out / "06_report_external.docx").stat().st_size > 0
        internal = (out / "06_report_internal.md").read_text(encoding="utf-8")
        assert "지금 바로 할 수 있는 일 3가지" in internal and "직원 B" in internal


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
