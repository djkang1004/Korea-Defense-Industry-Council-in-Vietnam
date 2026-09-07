import Image from 'next/image';
import {
  ArrowRight,
  BookOpen,
  Building2,
  CalendarDays,
  CheckCircle2,
  FileText,
  Globe2,
  LockKeyhole,
  Mail,
  Search,
  ShieldCheck,
  Users,
} from 'lucide-react';
import {
  getApplicationsForAdmin,
  reviewMembershipApplication,
  submitMembershipApplication,
} from './actions';
import { chatGPTSignInPath, chatGPTSignOutPath } from './chatgpt-auth';
import { getSiteData, getUserAccess } from './data';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Textarea } from '@/components/ui/textarea';

const navItems = [
  ['협의회소개', '#about'],
  ['회원사 정보', '#members'],
  ['알림마당', '#notice'],
  ['정보마당', '#resources'],
  ['회원센터', '#member-center'],
];

const serviceLinks = [
  { label: '회원가입 신청', href: '#member-center', icon: Users },
  { label: '회원사 현황', href: '#members', icon: Building2 },
  { label: '행사정보', href: '#notice', icon: CalendarDays },
  { label: '정책자료', href: '#resources', icon: FileText },
];

const coreWorks = [
  '베트남 방산·안보 협력 의제 발굴',
  '회원사 네트워킹과 현지 애로사항 접수',
  '정책·시장 동향 보고서 공유',
  '공공기관·기업 간 협력 채널 운영',
];

const formatDate = (date: Date) =>
  new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(date);

export default async function Home() {
  const [{ companies, announcements, events, resources }, access, applications] =
    await Promise.all([
      getSiteData(),
      getUserAccess(),
      getApplicationsForAdmin(),
    ]);

  const visibleResources =
    access.isApprovedMember || access.isAdmin
      ? resources
      : resources.filter((resource) => !resource.memberOnly);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-border bg-background/92 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-6 px-5 py-4">
          <a
            href="#"
            className="flex items-center gap-3"
            aria-label="한국방산협의회 홈"
          >
            <span className="flex size-10 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <ShieldCheck className="size-5" />
            </span>
            <span>
              <strong className="block text-base">한국방산협의회</strong>
              <span className="text-xs text-muted-foreground">
                K-Defense Council Vietnam
              </span>
            </span>
          </a>
          <nav className="hidden items-center gap-6 text-sm font-medium text-muted-foreground lg:flex">
            {navItems.map(([label, href]) => (
              <a
                key={label}
                href={href}
                className="transition hover:text-foreground"
              >
                {label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            {access.user ? (
              <Button
                variant="outline"
                size="sm"
                render={<a href={chatGPTSignOutPath('/')} />}
              >
                로그아웃
              </Button>
            ) : (
              <Button
                variant="outline"
                size="sm"
                render={<a href={chatGPTSignInPath('/')} />}
              >
                로그인
              </Button>
            )}
            <Button size="sm" render={<a href="#member-center" />}>
              가입신청
            </Button>
          </div>
        </div>
      </header>

      <section className="border-b border-border bg-[linear-gradient(135deg,#f8fbff_0%,#eef4f8_42%,#fff_100%)]">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 py-12 lg:grid-cols-[1.02fr_0.98fr] lg:py-16">
          <div className="flex flex-col justify-center">
            <Badge
              variant="outline"
              className="mb-5 w-fit border-primary/30 bg-white text-primary"
            >
              베트남 K-방산 협력 네트워크
            </Badge>
            <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-normal text-balance md:text-6xl">
              한국 방산기업의 베트남 협력을 연결하는 실무형 협의체
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-muted-foreground">
              한국방산협의회는 회원사, 공공기관, 현지 파트너가 함께 시장
              정보와 협력 의제를 공유하고 K-방산의 지속 가능한 현지 기반을
              넓혀갑니다.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" render={<a href="#member-center" />}>
                회원가입 신청 <ArrowRight className="size-4" />
              </Button>
              <Button variant="outline" size="lg" render={<a href="#resources" />}>
                자료 확인
              </Button>
            </div>
            <dl className="mt-10 grid max-w-2xl grid-cols-3 gap-4">
              {[
                ['회원·협력기관', `${companies.length}+`],
                ['주간 보고서', '정례'],
                ['거점', '하노이'],
              ].map(([label, value]) => (
                <div key={label} className="border-l border-primary/25 pl-4">
                  <dt className="text-sm text-muted-foreground">{label}</dt>
                  <dd className="mt-1 text-2xl font-semibold">{value}</dd>
                </div>
              ))}
            </dl>
          </div>
          <div className="relative min-h-[420px] overflow-hidden rounded-lg border border-border bg-card shadow-sm">
            <Image
              src="/council-activity.jpg"
              alt="한국방산협의회 주요 활동 단체 사진"
              fill
              priority
              className="object-cover"
            />
            <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-slate-950/85 to-transparent p-6 text-white">
              <p className="text-sm text-white/80">주요활동</p>
              <h2 className="mt-1 text-2xl font-semibold">
                현지 네트워크와 함께 움직이는 협의회
              </h2>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-border bg-card">
        <div className="mx-auto grid max-w-7xl gap-4 px-5 py-6 md:grid-cols-4">
          {serviceLinks.map(({ label, href, icon: Icon }) => (
            <a
              key={label}
              href={href}
              className="flex items-center justify-between rounded-lg border border-border bg-background px-4 py-4 text-sm font-semibold transition hover:border-primary/40 hover:text-primary"
            >
              <span className="flex items-center gap-3">
                <Icon className="size-5 text-primary" />
                {label}
              </span>
              <ArrowRight className="size-4" />
            </a>
          ))}
        </div>
      </section>

      <section
        id="about"
        className="mx-auto grid max-w-7xl gap-10 px-5 py-16 lg:grid-cols-[0.8fr_1.2fr]"
      >
        <div>
          <p className="section-kicker">협의회소개</p>
          <h2 className="mt-3 text-3xl font-semibold">
            현지 정보, 제도 이해, 기업 협력을 한곳에서 다룹니다.
          </h2>
        </div>
        <div className="grid gap-5 md:grid-cols-2">
          {coreWorks.map((work) => (
            <div key={work} className="rounded-lg border border-border bg-card p-5">
              <CheckCircle2 className="mb-5 size-6 text-primary" />
              <p className="text-lg font-semibold leading-7">{work}</p>
            </div>
          ))}
        </div>
      </section>

      <section id="notice" className="bg-muted/35">
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-16 lg:grid-cols-[1fr_0.8fr]">
          <div>
            <div className="mb-6 flex items-end justify-between gap-4">
              <div>
                <p className="section-kicker">알림마당</p>
                <h2 className="mt-3 text-3xl font-semibold">
                  공지사항과 행사정보
                </h2>
              </div>
              <Button variant="outline" size="sm" render={<a href="#member-center" />}>
                회원문의
              </Button>
            </div>
            <div className="space-y-3">
              {announcements.map((item) => (
                <article
                  key={item.id}
                  className="rounded-lg border border-border bg-card p-5"
                >
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <Badge variant={item.memberOnly ? 'secondary' : 'outline'}>
                      {item.category}
                    </Badge>
                    {item.memberOnly ? <Badge variant="outline">회원전용</Badge> : null}
                    <time className="text-sm text-muted-foreground">
                      {formatDate(item.publishedAt)}
                    </time>
                  </div>
                  <h3 className="text-xl font-semibold">{item.title}</h3>
                  <p className="mt-2 leading-7 text-muted-foreground">
                    {item.summary}
                  </p>
                </article>
              ))}
            </div>
          </div>
          <aside className="rounded-lg border border-border bg-card p-6">
            <div className="mb-5 flex items-center gap-3">
              <CalendarDays className="size-6 text-primary" />
              <h3 className="text-xl font-semibold">다가오는 일정</h3>
            </div>
            <div className="space-y-5">
              {events.map((event) => (
                <article key={event.id} className="border-l border-primary/35 pl-4">
                  <time className="text-sm font-semibold text-primary">
                    {formatDate(event.eventDate)}
                  </time>
                  <h4 className="mt-1 font-semibold">{event.title}</h4>
                  <p className="mt-1 text-sm text-muted-foreground">
                    {event.location} · {event.summary}
                  </p>
                </article>
              ))}
            </div>
          </aside>
        </div>
      </section>

      <section id="members" className="mx-auto max-w-7xl px-5 py-16">
        <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <p className="section-kicker">회원사 정보</p>
            <h2 className="mt-3 text-3xl font-semibold">회원사 현황</h2>
            <p className="mt-3 max-w-2xl text-muted-foreground">
              초기 회원사 현황 자료를 바탕으로 구성했으며, 승인된 회원사는
              관리자 검토 후 목록에 반영됩니다.
            </p>
          </div>
          <div className="flex min-w-[260px] items-center gap-2 rounded-lg border border-border bg-card px-3 py-2 text-muted-foreground">
            <Search className="size-4" />
            <span className="text-sm">검색 기능 확장 준비</span>
          </div>
        </div>
        <div className="rounded-lg border border-border bg-card">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>구분</TableHead>
                <TableHead>업체명</TableHead>
                <TableHead>대표/담당</TableHead>
                <TableHead>역할</TableHead>
                <TableHead>소재지</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {companies.map((company) => (
                <TableRow key={company.id}>
                  <TableCell>{company.category}</TableCell>
                  <TableCell className="font-semibold">
                    {company.companyName}
                  </TableCell>
                  <TableCell>{company.representative}</TableCell>
                  <TableCell>{company.role}</TableCell>
                  <TableCell>{company.location}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </section>

      <section
        id="resources"
        className="border-y border-border bg-slate-950 text-white"
      >
        <div className="mx-auto grid max-w-7xl gap-8 px-5 py-16 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <p className="section-kicker text-sky-200">정보마당</p>
            <h2 className="mt-3 text-3xl font-semibold">
              정책자료와 주간 방산보고서
            </h2>
            <p className="mt-4 leading-7 text-slate-300">
              회원 승인 후에는 협의회 내부 보고서와 회원 전용 공지를 확인할
              수 있습니다. 비회원에게는 공개 자료만 표시됩니다.
            </p>
            <div className="mt-6 flex items-center gap-3 text-sm text-slate-300">
              <LockKeyhole className="size-4" />
              {access.isApprovedMember || access.isAdmin
                ? '회원 전용 자료 접근 가능'
                : '로그인 및 승인 후 전체 자료 접근 가능'}
            </div>
          </div>
          <div className="grid gap-4">
            {visibleResources.length ? (
              visibleResources.map((resource) => (
                <article
                  key={resource.id}
                  className="rounded-lg border border-white/15 bg-white/8 p-5"
                >
                  <div className="mb-3 flex flex-wrap items-center gap-2">
                    <Badge className="bg-sky-200 text-slate-950">
                      {resource.category}
                    </Badge>
                    {resource.memberOnly ? (
                      <Badge variant="outline" className="border-white/25 text-white">
                        회원전용
                      </Badge>
                    ) : null}
                    <time className="text-sm text-slate-300">
                      {formatDate(resource.publishedAt)}
                    </time>
                  </div>
                  <h3 className="text-xl font-semibold">{resource.title}</h3>
                  <p className="mt-2 text-slate-300">{resource.summary}</p>
                  <p className="mt-3 text-sm text-slate-400">
                    {resource.fileName}
                  </p>
                </article>
              ))
            ) : (
              <div className="rounded-lg border border-white/15 bg-white/8 p-6">
                <BookOpen className="mb-4 size-6 text-sky-200" />
                <h3 className="text-xl font-semibold">
                  회원 승인 후 자료가 표시됩니다.
                </h3>
                <p className="mt-2 text-slate-300">
                  회원센터에서 가입 신청을 제출해 주세요.
                </p>
              </div>
            )}
          </div>
        </div>
      </section>

      <section className="mx-auto grid max-w-7xl gap-8 px-5 py-16 lg:grid-cols-2">
        <div className="relative min-h-[360px] overflow-hidden rounded-lg border border-border">
          <Image
            src="/embassy-visit.jpg"
            alt="주베트남 대한민국 대사관 공식 예방 활동 사진"
            fill
            className="object-cover"
          />
        </div>
        <div className="flex flex-col justify-center">
          <p className="section-kicker">주요활동</p>
          <h2 className="mt-3 text-3xl font-semibold">
            공공외교와 산업협력을 잇는 현장 활동
          </h2>
          <p className="mt-4 leading-8 text-muted-foreground">
            협의회는 현지 기관 예방, 회원사 정례 교류, 정책 자료 공유를 통해
            베트남 내 K-방산 협력 기반을 넓히고 있습니다.
          </p>
        </div>
      </section>

      <section id="member-center" className="bg-muted/35">
        <div className="mx-auto max-w-7xl px-5 py-16">
          <p className="section-kicker">회원센터</p>
          <h2 className="mt-3 text-3xl font-semibold">
            회원가입 신청과 승인 관리
          </h2>
          <Tabs defaultValue="apply" className="mt-8">
            <TabsList className="w-full justify-start overflow-x-auto md:w-fit">
              <TabsTrigger value="apply">가입신청</TabsTrigger>
              <TabsTrigger value="status">내 접근상태</TabsTrigger>
              {access.isAdmin ? (
                <TabsTrigger value="admin">관리자 승인</TabsTrigger>
              ) : null}
            </TabsList>
            <TabsContent value="apply" className="mt-6">
              <form
                action={submitMembershipApplication}
                className="grid gap-4 rounded-lg border border-border bg-card p-6 md:grid-cols-2"
              >
                <Field name="companyName" label="회사명" />
                <Field name="contactName" label="담당자명" />
                <Field name="position" label="직책" />
                <Field name="phone" label="연락처" />
                <Field name="email" label="이메일" type="email" />
                <Field name="location" label="소재지" />
                <Field name="interestArea" label="관심 분야" />
                <label className="md:col-span-2">
                  <span className="mb-2 block text-sm font-medium">가입 목적</span>
                  <Textarea
                    name="purpose"
                    required
                    placeholder="협의회 참여 목적과 필요한 지원 사항을 입력해 주세요."
                    className="min-h-28 bg-background"
                  />
                </label>
                <div className="md:col-span-2">
                  <Button type="submit" size="lg">
                    신청서 제출 <Mail className="size-4" />
                  </Button>
                </div>
              </form>
            </TabsContent>
            <TabsContent value="status" className="mt-6">
              <div className="rounded-lg border border-border bg-card p-6">
                <div className="flex items-start gap-4">
                  <Globe2 className="mt-1 size-6 text-primary" />
                  <div>
                    <h3 className="text-xl font-semibold">
                      {access.user
                        ? `${access.user.displayName} 님`
                        : '로그인이 필요합니다.'}
                    </h3>
                    <p className="mt-2 text-muted-foreground">
                      {access.isAdmin
                        ? '관리자 권한으로 회원 신청을 검토할 수 있습니다.'
                        : access.isApprovedMember
                          ? '승인 회원으로 회원 전용 자료에 접근할 수 있습니다.'
                          : '회원 전용 자료는 로그인 후 관리자 승인을 받은 계정에 표시됩니다.'}
                    </p>
                    <div className="mt-5">
                      {access.user ? (
                        <Button
                          variant="outline"
                          render={<a href={chatGPTSignOutPath('/')} />}
                        >
                          로그아웃
                        </Button>
                      ) : (
                        <Button render={<a href={chatGPTSignInPath('/')} />}>
                          ChatGPT로 로그인
                        </Button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </TabsContent>
            {access.isAdmin ? (
              <TabsContent value="admin" className="mt-6">
                <div className="rounded-lg border border-border bg-card">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>상태</TableHead>
                        <TableHead>회사명</TableHead>
                        <TableHead>담당자</TableHead>
                        <TableHead>이메일</TableHead>
                        <TableHead>검토</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {applications.length ? (
                        applications.map((application) => (
                          <TableRow key={application.id}>
                            <TableCell>
                              <Badge variant="outline">{application.status}</Badge>
                            </TableCell>
                            <TableCell className="font-semibold">
                              {application.companyName}
                            </TableCell>
                            <TableCell>{application.contactName}</TableCell>
                            <TableCell>{application.email}</TableCell>
                            <TableCell>
                              <form
                                action={reviewMembershipApplication}
                                className="flex gap-2"
                              >
                                <input
                                  type="hidden"
                                  name="applicationId"
                                  value={application.id}
                                />
                                <Button
                                  type="submit"
                                  name="status"
                                  value="승인"
                                  size="sm"
                                >
                                  승인
                                </Button>
                                <Button
                                  type="submit"
                                  name="status"
                                  value="반려"
                                  size="sm"
                                  variant="outline"
                                >
                                  반려
                                </Button>
                              </form>
                            </TableCell>
                          </TableRow>
                        ))
                      ) : (
                        <TableRow>
                          <TableCell
                            colSpan={5}
                            className="py-8 text-center text-muted-foreground"
                          >
                            검토할 신청서가 없습니다.
                          </TableCell>
                        </TableRow>
                      )}
                    </TableBody>
                  </Table>
                </div>
              </TabsContent>
            ) : null}
          </Tabs>
        </div>
      </section>

      <footer className="border-t border-border bg-card">
        <div className="mx-auto flex max-w-7xl flex-col gap-4 px-5 py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between">
          <p>한국방산협의회 · K-Defense Council Vietnam</p>
          <p>회원문의 · contact@k-defense-council.kr</p>
        </div>
      </footer>
    </main>
  );
}

function Field({
  label,
  name,
  type = 'text',
}: {
  label: string;
  name: string;
  type?: string;
}) {
  return (
    <label>
      <span className="mb-2 block text-sm font-medium">{label}</span>
      <Input name={name} type={type} required className="bg-background" />
    </label>
  );
}
