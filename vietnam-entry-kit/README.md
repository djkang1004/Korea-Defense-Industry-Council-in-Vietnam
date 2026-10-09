# 베트남 진출 자동화 키트 (Vietnam Entry Kit)

고객사 정보 YAML 하나만 입력하면 베트남 **시장조사 · 마케팅 조사 · 수출입 · 법인/지사/사무소 설립** 컨설팅의
1차 산출물을 자동 생성합니다.

```
인테이크 입력 → 진단(업종·쟁점·진출형태 점수화) → 조사 프롬프트 패키지 → 여러 LLM 실행
→ 교차검증(사실/추정/미확인·상충 자동 판정) → 보고서(고객 제출본·내부 검토본, .md/.docx)
```

## 설치
```bash
cd vietnam-entry-kit
pip install -r requirements.txt          # Claude 자동 조사까지 쓰려면: pip install anthropic
```

## 사용법 (5단계)
```bash
# 1) 인테이크 시트 생성 후 고객사 정보 입력
python -m vnkit init "고객사명"            # → intake/고객사명.yaml

# 2) 진단·프롬프트·로드맵·보고서 초안 생성
python -m vnkit build intake/고객사명.yaml  # → output/고객사명/

# 3) 02_prompts/*.md 를 ChatGPT·Gemini·Perplexity 등에 붙여넣고
#    답변을 03_responses/<모듈>/<LLM이름>.md 로 저장
#    (선택) Claude API로 자동 실행:
python -m vnkit run-llm output/고객사명

# 4) 교차검증
python -m vnkit merge output/고객사명       # → 04_crossvalidation.md / .csv / .json

# 5) 검증 결과 반영 보고서 재생성
python -m vnkit report output/고객사명 --docx
```
한 번에 실행: `python -m vnkit all intake/고객사명.yaml --with-claude --docx`

## 산출물 (output/<고객사>/)
| 파일 | 내용 | 용도 |
|---|---|---|
| `01_diagnosis.md` | 결측 점검, 고객사에 먼저 물을 질문 1개, 쟁점, 진출형태 점수 근거 | 내부 |
| `02_prompts/` | 모듈별 조사 프롬프트(코드화된 질문 + 표 형식 강제) | LLM 투입 |
| `03_responses/` | LLM별 답변 저장 위치 | 입력 |
| `04_crossvalidation.*` | 코드별 판정: 교차확인 / 단일출처 / 상충 / 추정 / 미확인 | 검증 |
| `05_roadmap_internal.md` | 직원 A·B·C 업무 배분 실행계획 | 내부 |
| `05_roadmap_external.md` | 기능 조직(시장분석팀 등)으로 추상화한 로드맵 | 외부 |
| `06_report_external.*` | 고객사 제출용 보고서 — 권고 어투, 담당자명 미노출 | 외부 |
| `06_report_internal.*` | 내부 검토본 — 담당자 배분형 | 내부 |

## 구조
```
kb/                     판단 기준(코드 수정 없이 편집 가능)
  entity_types.yaml     진출형태 6종: 법적 근거·허용 활동·기간·장단점·리스크
  sector_profiles.yaml  업종 9종: 키워드·규제기관·핵심 규정·채널·데이터 출처
  common_rules.yaml     세무·관세·외환·노무·개인정보 공통 규정
  research_modules.yaml 조사 모듈 9종과 코드화된 질문
  setup_steps.yaml      진출형태별 실행 단계·담당·소요 주차
  team.yaml             직원 실명 ↔ 외부 표기 기능조직명
vnkit/                  엔진 (analyze, prompts, merge, render, llm, docx_export, cli)
examples/               가상 고객사 예시 2종 (방산 광학, K-뷰티)
```

## 판단 로직의 한계 (반드시 읽어 주십시오)
- **진출형태 점수**는 인테이크 답변에 따른 규칙 점수입니다. 근거가 모두 표시되며, 최종 결정은 현지 법률 검토가 필요합니다.
- **지식베이스 규정**은 `status: 확인/검증필요`로 구분되어 있습니다. 2025년 베트남 정부조직·행정구역 개편, 신법인세법·개인정보보호법·
  노동허가 시행령 등 최근 개정 사항은 `검증필요`로 표시했으며, 분기마다 `last_reviewed`를 갱신하십시오.
- **교차검증의 수치 상충 탐지**는 휴리스틱(대표 수치 25% 이상 차이)입니다. LLM이 제시한 URL은 실재하지 않을 수 있으므로
  '교차확인' 항목도 담당자가 URL을 열람해 `열람확인` 칸을 채운 뒤 보고서에 반영하십시오.

## 웹 버전과 동기화
웹 버전(강동조 이력서 사이트 `vietnam-entry/`)은 같은 지식베이스를 JSON으로 사용합니다. `kb/*.yaml`을 수정했다면 다음을 실행해 웹 버전에 반영하십시오.
```bash
python -m vnkit export-kb <dongjo_kang_resume 경로>/vietnam-entry/kb.json
```

## 테스트
```bash
python tests/test_pipeline.py
```
