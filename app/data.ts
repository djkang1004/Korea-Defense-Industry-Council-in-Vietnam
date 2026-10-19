import { eq } from 'drizzle-orm';
import { getChatGPTUser } from './chatgpt-auth';
import { getDb } from '@/db';
import { memberCompanies } from '@/db/schema';
import { isAdminEmail } from '@/lib/access';

export type UserAccess = {
  user: Awaited<ReturnType<typeof getChatGPTUser>>;
  isAdmin: boolean;
  isApprovedMember: boolean;
};

export const fallbackCompanies = [
  {
    id: 'seed-smbl',
    category: '기업',
    companyName: 'SMBL',
    representative: '비공개',
    role: '회원사',
    location: '하노이',
    note: '2026년 8월 17일 회원사 현황 기준',
    contactEmail: null,
    approvedAt: null,
  },
];

export const fallbackAnnouncements = [
  {
    id: 'notice-23',
    title: '주간 국제정세·방산 보고서 제23호 안내',
    category: '자료안내',
    summary: '10월 주요 국제정세와 베트남 방산환경 관련 동향을 회원사에 공유했습니다.',
    publishedAt: new Date('2026-10-19'),
    memberOnly: false,
  },
  {
    id: 'notice-onboarding',
    title: '한국방산협의회 회원사 온보딩 자료 안내',
    category: '회원안내',
    summary: '협의회 운영 방향, 핵심 가치와 참여 절차를 정리했습니다.',
    publishedAt: new Date('2026-08-17'),
    memberOnly: false,
  },
  {
    id: 'notice-embassy',
    title: '주베트남 대한민국 대사관 예방',
    category: '주요활동',
    summary: '베트남 내 K-방산 협력 확대를 위한 주요 관심 의제를 교환했습니다.',
    publishedAt: new Date('2026-08-24'),
    memberOnly: false,
  },
];

export const fallbackEvents = [
  {
    id: 'event-admm',
    title: '제20차 ADMM 및 제13차 ADMM+ 일정',
    eventDate: new Date('2026-10-26'),
    location: '하노이',
    summary: '베트남 국방외교 관련 주요 공개 일정',
  },
  {
    id: 'event-kdex',
    title: 'K-DEX 2026',
    eventDate: new Date('2026-12-08'),
    location: '대한민국',
    summary: '대한민국 방위산업 전시·교류 일정',
  },
  {
    id: 'event-vietnam-defence',
    title: 'Vietnam Defence Expo 2026',
    eventDate: new Date('2026-12-10'),
    location: '하노이',
    summary: '베트남 국제방위산업전시회 일정',
  },
];

export const fallbackResources = [
  {
    id: 'resource-intro',
    title: '한국방산협의회 소개와 운영 원칙',
    category: '협의회 소개',
    fileName: '한국방산협의회_소개.pdf',
    summary: '설립 목적, 핵심 역할, 회원 체계와 운영 원칙을 안내합니다.',
    memberOnly: false,
    publishedAt: new Date('2026-08-17'),
  },
  {
    id: 'resource-23',
    title: '주간 국제정세·방산 보고서 제23호',
    category: '주간보고서',
    fileName: '주간 국제정세·방산 보고서_제23호.pdf',
    summary: '주요국 방산환경 변화와 베트남 관련 핵심 동향을 정리한 회원 보고서입니다.',
    memberOnly: true,
    publishedAt: new Date('2026-10-19'),
  },
  {
    id: 'resource-onboarding',
    title: '신입회원사 온보딩 브로슈어',
    category: '회원안내',
    fileName: '한국방산협의회_신입회원사 온보딩 브로슈어v0.2.pdf',
    summary: '회원 참여 절차와 운영 원칙 안내 자료입니다.',
    memberOnly: true,
    publishedAt: new Date('2026-08-17'),
  },
];

export async function getUserAccess(): Promise<UserAccess> {
  const user = await getChatGPTUser();
  if (!user) return { user: null, isAdmin: false, isApprovedMember: false };

  try {
    const [member] = await getDb()
      .select()
      .from(memberCompanies)
      .where(eq(memberCompanies.contactEmail, user.email))
      .limit(1);
    return {
      user,
      isAdmin: isAdminEmail(user.email),
      isApprovedMember: Boolean(member),
    };
  } catch {
    return {
      user,
      isAdmin: isAdminEmail(user.email),
      isApprovedMember: false,
    };
  }
}

export async function getSiteData() {
  // 공개 화면은 검증이 끝난 고정 콘텐츠만 사용합니다.
  // 기존 D1의 오래된 일정·회원 기본값이 다시 노출되지 않도록 분리합니다.
  return {
    companies: fallbackCompanies,
    announcements: fallbackAnnouncements,
    events: fallbackEvents,
    resources: fallbackResources,
  };
}
