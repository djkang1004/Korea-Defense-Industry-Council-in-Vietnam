"""(선택) Claude API로 조사 프롬프트를 자동 실행해 03_responses/<모듈>/claude.md로 저장.

필요: `pip install anthropic` + ANTHROPIC_API_KEY (또는 `ant auth login` 프로필).
웹 검색 서버 도구를 사용하므로 별도 검색 API는 필요 없다.
"""

from __future__ import annotations

from pathlib import Path

MODEL = "claude-opus-5-5"
SYSTEM = (
    "당신은 베트남 시장 진출 컨설팅을 위한 리서처입니다. 웹 검색으로 최신 1차 자료를 확인하고, "
    "요청된 표 형식을 정확히 지키십시오. 근거를 찾지 못한 항목은 '미확인'으로 표시하고 추측하지 마십시오."
)


def _text(message) -> str:
    return "\n".join(b.text for b in message.content if b.type == "text")


def run_prompt(client, prompt: str, effort: str = "high") -> str:
    messages = [{"role": "user", "content": prompt}]
    for _ in range(5):  # pause_turn(장시간 서버 도구 실행) 재개 상한
        with client.beta.messages.stream(
            model=MODEL,
            max_tokens=64000,
            system=SYSTEM,
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            tools=[{"type": "web_search_20260209", "name": "web_search", "max_uses": 15}],
            messages=messages,
            betas=["server-side-fallback-2026-07-01"],
            extra_body={"fallbacks": "default"},
        ) as stream:
            msg = stream.get_final_message()
        if msg.stop_reason == "refusal":
            raise RuntimeError(f"모델이 요청을 거절했습니다: {getattr(msg, 'stop_details', None)}")
        if msg.stop_reason != "pause_turn":
            return _text(msg)
        messages.append({"role": "assistant", "content": msg.content})
    return _text(msg)


def run_all(out_dir: Path, effort: str = "high", only: list[str] | None = None) -> list[Path]:
    try:
        import anthropic
    except ImportError as e:  # pragma: no cover
        raise SystemExit("anthropic 패키지가 없습니다: pip install anthropic") from e

    client = anthropic.Anthropic()
    written = []
    for p in sorted((out_dir / "02_prompts").glob("*.md")):
        if p.name == "README.md":
            continue
        mid = p.name.split("_", 1)[0]
        if only and mid not in only:
            continue
        print(f"[{mid}] Claude 조사 실행 중…", flush=True)
        try:
            answer = run_prompt(client, p.read_text(encoding="utf-8"), effort)
        except anthropic.APIStatusError as e:
            print(f"[{mid}] API 오류 {e.status_code}: {e.message} — 건너뜀")
            continue
        except anthropic.APIConnectionError as e:
            print(f"[{mid}] 연결 오류: {e} — 건너뜀")
            continue
        dest = out_dir / "03_responses" / mid / "claude.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(answer, encoding="utf-8")
        written.append(dest)
    return written
