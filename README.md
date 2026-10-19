# 한국방산협의회 홈페이지

베트남에 진출했거나 진출을 준비하는 한국 방산·산업협력 기업의 민간 실무협의체 홈페이지입니다. 공개 신뢰 형성, 기관·기업 단위 회원 네트워크 안내, 방산 인사이트 요약과 회원 전용 자료실을 중심으로 구성했습니다.

## 주요 기능

- 한국어 중심 신뢰형 단일 페이지
- 협의회 미션·비전과 4대 역할 안내
- 개인명과 연락처를 제외한 기관·기업 단위 회원 네트워크
- 검증된 공식 활동사진과 최신 일정
- 공개 요약과 승인 회원 전용 자료의 분리
- ChatGPT 로그인 및 D1 회원 승인 상태 기반 접근 제어
- 개인정보 입력형 공개 가입폼 대신 총무 문의 방식 적용

## 로컬 실행

```bash
npm install
npm run db:generate
npm run dev
```

기본 로컬 주소는 `http://localhost:3000`입니다.

## 빌드

```bash
npm run build
```

## 환경변수

관리자 계정은 `ADMIN_EMAILS`에 쉼표로 구분해 등록합니다.

```env
ADMIN_EMAILS=admin@example.com,manager@example.com
```

## 주요 파일

- `app/page.tsx`: 공개 홈페이지와 회원 자료실 UI
- `app/data.ts`: 검증된 공개 콘텐츠와 회원 접근정보 조회
- `db/schema.ts`: D1 데이터베이스 테이블 정의
- `public/council-hero.jpg`, `public/council-embassy.jpg`: 선별된 공식 활동사진
- `public/k-defense-council-logo.png`: 협의회 가로형 로고

## 공개정보 원칙

개인 회원 연락처, 내부 협의 내용과 회원 전용 보고서는 공개하지 않습니다. 기관·기업명, 사진과 일정은 확인된 자료를 기준으로 하며 변경 시 재검토합니다.
