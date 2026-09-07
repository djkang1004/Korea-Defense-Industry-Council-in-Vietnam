import { desc, eq } from 'drizzle-orm';
import { getChatGPTUser } from './chatgpt-auth';
import { getDb } from '@/db';
import {
  announcements,
  events,
  memberCompanies,
  resources,
} from '@/db/schema';
import { isAdminEmail } from '@/lib/access';

export type UserAccess = {
  user: Awaited<ReturnType<typeof getChatGPTUser>>;
  isAdmin: boolean;
  isApprovedMember: boolean;
};

export const fallbackCompanies = [
  {
    id: 'seed-kotra',
    category: '공공지원',
    companyName: 'KOTRA 하노이 무역관',
    representative: '협력 담당',
    role: '수출지원',
    location: '하노이',
    note: '초기 회원사 현황 자료 기반',
    contactEmail: null,
    approvedAt: null,
  },
  {
    id: 'seed-smbl',
    category: '운영/자문',
    companyName: 'SMBL',
    representative: '운영진',
    role: '협의회 운영',
    location: '하노이',
    note: '초기 회원사 현황 자료 기반',
    contactEmail: null,
    approvedAt: null,
  },
  {
    id: 'seed-vinatech',
    category: '제조/협력',
    companyName: 'VINATech Group',
    representative: '현지 대표',
    role: '산업협력',
    location: '하노이',
    note: '초기 회원사 현황 자료 기반',
    contactEmail: null,
    approvedAt: null,
  },
];

export const fallbackAnnouncements = [
  {
    id: 'notice-1',
    title: '한국방산협의회 회원사 온보딩 자료 안내',
    category: '일반공지',
    summary: '신규 회원사를 위한 협의회 운영 방향과 참여 절차를 정리했습니다.',
    publishedAt: new Date('2026-08-17'),
    memberOnly: false,
  },
  {
    id: 'notice-2',
    title: '주간 국제정세·방산 보고서 9월 2주 배포',
    category: '자료안내',
    summary: '회원 전용 정보마당에서 최신 주간 보고서를 확인할 수 있습니다.',
    publishedAt: new Date('2026-09-07'),
    memberOnly: true,
  },
  {
    id: 'notice-3',
    title: '주베트남 대한민국 대사관 공식 예방 결과 공유',
    category: '주요활동',
    summary: '베트남 내 K-방산 협력 확대를 위한 주요 논의 내용을 정리했습니다.',
    publishedAt: new Date('2026-08-25'),
    memberOnly: false,
  },
];

export const fallbackEvents = [
  {
    id: 'event-1',
    title: '정례 회원사 네트워킹 미팅',
    eventDate: new Date('2026-09-24'),
    location: '하노이',
    summary: '회원사 애로사항 공유와 베트남 방산 협력 의제 발굴',
  },
  {
    id: 'event-2',
    title: 'K-방산 베트남 진출 전략 세션',
    eventDate: new Date('2026-10-15'),
    location: '온라인/하노이',
    summary: '수출, 현지 파트너십, 제도 동향을 함께 점검',
  },
];

export const fallbackResources = [
  {
    id: 'resource-1',
    title: '주간 국제정세·방산 보고서 9월 2주',
    category: '주간보고서',
    fileName: '주간 국제정세·방산 보고서_9월2주.pdf',
    summary: '베트남 및 주요국 방산 환경 변화와 수출 협력 포인트',
    memberOnly: true,
    publishedAt: new Date('2026-09-07'),
  },
  {
    id: 'resource-2',
    title: '신입회원사 온보딩 브로슈어',
    category: '회원안내',
    fileName: '한국방산협의회_신입회원사 온보딩 브로슈어v0.2.pdf',
    summary: '협의회 참여 절차와 운영 원칙 안내',
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
  try {
    const db = getDb();
    const [companies, notices, eventItems, resourceItems] = await Promise.all([
      db.select().from(memberCompanies),
      db.select().from(announcements).orderBy(desc(announcements.publishedAt)),
      db.select().from(events).orderBy(events.eventDate),
      db.select().from(resources).orderBy(desc(resources.publishedAt)),
    ]);

    return {
      companies: companies.length ? companies : fallbackCompanies,
      announcements: notices.length ? notices : fallbackAnnouncements,
      events: eventItems.length ? eventItems : fallbackEvents,
      resources: resourceItems.length ? resourceItems : fallbackResources,
    };
  } catch {
    return {
      companies: fallbackCompanies,
      announcements: fallbackAnnouncements,
      events: fallbackEvents,
      resources: fallbackResources,
    };
  }
}
