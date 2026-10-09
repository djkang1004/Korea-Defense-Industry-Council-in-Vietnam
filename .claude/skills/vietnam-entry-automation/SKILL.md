---
name: vietnam-entry-automation
description: 고객사 정보를 받아 베트남 시장조사·마케팅 조사·수출입·법인/지사/사무소 설립 컨설팅 산출물(진단서, 조사 프롬프트, 교차검증표, 고객 제출용/내부 보고서)을 vietnam-entry-kit으로 자동 생성한다. 사용자가 "고객사 베트남 진출 분석", "이 회사 베트남 시장조사", "법인 설립 검토", "인테이크 돌려줘" 등을 요청하면 사용한다.
---

# 베트남 진출 자동화 워크플로

키트 위치: `vietnam-entry-kit/` (사용법은 그 폴더의 README.md)

1. **인테이크 작성**: 사용자가 준 고객사 정보를 `vietnam-entry-kit/intake/company_template.yaml` 형식으로
   `intake/<고객사>.yaml`에 옮긴다. 판단에 필요한 정보가 비면 추측하지 말고, 가장 중요한 항목 하나만 되묻는다
   (우선순위: 현지 직접 판매·인보이스 필요 여부 → 진출 단계 → 예산).
2. **빌드**: `cd vietnam-entry-kit && python -m vnkit build intake/<고객사>.yaml`
3. **조사**: `output/<고객사>/02_prompts/*.md`를 직접 웹 검색으로 수행해 답변을 표 형식 그대로
   `03_responses/<모듈>/claude.md`에 저장한다. 사용자가 다른 LLM 답변을 주면 `03_responses/<모듈>/<LLM>.md`로 저장한다.
4. **검증·보고서**: `python -m vnkit merge output/<고객사>` → `python -m vnkit report output/<고객사> --docx`
5. **검토 보고**: 04_crossvalidation.md의 상충·미확인 항목, 01_diagnosis.md의 결측 항목을 사용자에게 요약하고,
   배포 전 수정이 필요한 부분을 표시한다. 고객 제출본은 smbl-market-report 스킬로 레터지 서식 전환을 제안한다.

원칙: 확인된 사실·추정·미확인을 구분하고, 법률·세무 판단은 전문가 검토 필요 지점으로 표시한다.
