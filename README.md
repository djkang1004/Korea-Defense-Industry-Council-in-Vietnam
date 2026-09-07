# 한국방산협의회 홈페이지

베트남 K-방산 협력과 회원사 네트워크를 지원하는 한국방산협의회 홈페이지입니다. KDIA식 기관형 정보 구조를 참고해 협의회 소개, 회원사 현황, 공지/행사, 정보마당, 회원가입 신청과 관리자 승인 기능을 포함했습니다.

## 주요 기능

- 한국어 중심 기관형 홈페이지
- 회원가입 신청서 제출
- 관리자 승인/반려 처리
- 승인 회원 전용 자료 표시
- D1 기반 데이터베이스 스키마
- ChatGPT 로그인 기반 접근 제어

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

- `app/page.tsx`: 홈페이지 화면과 회원센터 UI
- `app/actions.ts`: 회원가입 신청 및 관리자 승인 서버 액션
- `app/data.ts`: 화면 데이터 조회와 기본 콘텐츠
- `db/schema.ts`: D1 데이터베이스 테이블 정의
- `public/council-activity.jpg`, `public/embassy-visit.jpg`: 현장 활동 이미지
