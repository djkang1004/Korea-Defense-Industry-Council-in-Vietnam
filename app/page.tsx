import Image from 'next/image';
import {
  ArrowRight, BookOpen, BriefcaseBusiness, CalendarDays, FileText,
  Handshake, LockKeyhole, Mail, MapPin, Network, Phone, ShieldCheck,
} from 'lucide-react';
import { chatGPTSignInPath, chatGPTSignOutPath } from './chatgpt-auth';
import { getSiteData, getUserAccess } from './data';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const navItems = [
  ['협의회 소개', '#about'], ['주요 역할', '#work'], ['회원 네트워크', '#members'],
  ['인사이트', '#insights'], ['주요 활동', '#activities'], ['가입·문의', '#contact'],
];

const principles = [
  { icon: BookOpen, title: '시장정보', text: '베트남 방산정책, 조달환경, 법제와 시장동향을 정리해 회원사와 공유합니다.' },
  { icon: Network, title: '회원 네트워크', text: '완제품, 부품·소재, ICT, 상사와 물류기업을 연결해 협업 기반을 넓힙니다.' },
  { icon: Handshake, title: '기관협력', text: '공공기관 및 유관기관과의 합법적이고 투명한 산업협력 소통을 지원합니다.' },
  { icon: BriefcaseBusiness, title: '사업협력', text: '현지 파트너 탐색, 공동 관심 의제와 회원사 간 협력 기회 발굴을 돕습니다.' },
];

const memberGroups = [
  { title: '유관·지원기관', members: ['주베트남 대한민국 대사관', 'KOTRA 하노이 무역관', '한국수출입은행 하노이사무소'] },
  { title: '산업·기업 회원', members: ['현대코퍼레이션 하노이지사', '쉘라인 베트남 대표사무소', 'HS 효성베트남', 'VINATech 그룹', '㈜비츠로셀', 'SMBL'] },
  { title: '전문 협력 네트워크', members: ['파이낸셜뉴스 동남아취재본부'] },
];

const activities = [
  { image: '/council-hero.jpg', label: '회원 네트워크', title: '현장에서 쌓아가는 신뢰와 협력', text: '회원사 간 정례 교류를 통해 시장 경험과 공통 관심 의제를 공유합니다.' },
  { image: '/council-embassy.jpg', label: '기관 교류', title: '주베트남 대한민국 대사관 예방', text: '한·베 산업협력과 K-방산의 지속 가능한 현지 기반에 관한 의견을 교환했습니다.' },
];

const formatDate = (date: Date) => new Intl.DateTimeFormat('ko-KR', {
  year: 'numeric', month: '2-digit', day: '2-digit',
}).format(date);

export default async function Home() {
  const [{ announcements, events, resources }, access] = await Promise.all([getSiteData(), getUserAccess()]);
  const visibleResources = access.isApprovedMember || access.isAdmin
    ? resources : resources.filter((resource) => !resource.memberOnly);

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-50 border-b border-border/80 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-5 px-5 py-3">
          <a href="#top" aria-label="한국방산협의회 홈">
            <Image src="/k-defense-council-logo.png" alt="한국방산협의회" width={250} height={81} priority className="h-11 w-auto object-contain" />
          </a>
          <nav className="hidden items-center gap-5 text-sm font-semibold text-slate-600 xl:flex">
            {navItems.map(([label, href]) => <a key={label} href={href} className="hover:text-primary">{label}</a>)}
          </nav>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" nativeButton={false}
              render={<a href={access.user ? chatGPTSignOutPath('/') : chatGPTSignInPath('/#member-library')} />}>
              {access.user ? '로그아웃' : '회원 로그인'}
            </Button>
            <Button size="sm" nativeButton={false} render={<a href="#contact" />}>가입 문의</Button>
          </div>
        </div>
      </header>

      <section id="top" className="hero-grid border-b border-border">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 py-14 lg:grid-cols-[1.02fr_0.98fr] lg:items-center lg:py-20">
          <div>
            <Badge variant="outline" className="border-primary/25 bg-white/80 text-primary">Korea Defense Council in Vietnam</Badge>
            <h1 className="mt-6 text-4xl font-bold leading-[1.16] tracking-[-0.035em] text-slate-950 md:text-6xl">
              한국 방산기업의<br />베트남 진출과 산업협력을 연결합니다
            </h1>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-slate-600">
              한국방산협의회는 베트남에 진출했거나 진출을 준비하는 한국 방산·산업협력 기업들이 시장정보와 현지 경험을 공유하고 지속 가능한 협력 기회를 발굴하는 민간 실무협의체입니다.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Button size="lg" nativeButton={false} render={<a href="#about" />}>협의회 알아보기 <ArrowRight className="size-4" /></Button>
              <Button variant="outline" size="lg" nativeButton={false} render={<a href="#insights" />}>최신 인사이트</Button>
            </div>
            <dl className="mt-10 grid max-w-2xl grid-cols-3 gap-4 border-t border-slate-200 pt-6">
              {[['출범', '2026'], ['창립회원', '11명'], ['정례 정보', '매주']].map(([label, value]) => (
                <div key={label}><dt className="text-sm text-slate-500">{label}</dt><dd className="mt-1 text-2xl font-bold text-primary">{value}</dd></div>
              ))}
            </dl>
            <p className="mt-3 text-xs text-slate-400">창립회원 수는 2026년 8월 17일 회원사 현황 기준</p>
          </div>
          <div className="relative min-h-[430px] overflow-hidden rounded-2xl bg-slate-900 shadow-2xl shadow-slate-900/15">
            <Image src="/council-hero.jpg" alt="한국방산협의회 회원 교류 활동" fill priority className="object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-slate-950/85 via-slate-950/10 to-transparent" />
            <div className="absolute inset-x-0 bottom-0 p-7 text-white">
              <p className="text-sm font-semibold text-sky-200">Team Korea in Vietnam</p>
              <p className="mt-2 text-xl font-semibold leading-8">신뢰를 기반으로 정보와 경험을 연결하는 현장 중심 네트워크</p>
            </div>
          </div>
        </div>
      </section>

      <section id="about" className="mx-auto max-w-7xl px-5 py-20">
        <div className="grid gap-12 lg:grid-cols-[0.8fr_1.2fr]">
          <div><p className="section-kicker">About the Council</p><h2 className="mt-4 text-3xl font-bold leading-tight md:text-4xl">개별 대응의 한계를 넘어<br />Team Korea의 협력 기반으로</h2></div>
          <div>
            <p className="text-lg leading-8 text-slate-600">베트남 방산시장은 정부 중심의 의사결정과 높은 진입장벽, 복합적인 현지화 요구가 공존합니다. 협의회는 한국 기업들이 각자 축적한 정보와 경험을 연결하고, 방산 밸류체인 전반의 협업 가능성을 찾기 위해 출범했습니다.</p>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="rounded-xl border bg-slate-50 p-6"><p className="text-sm font-bold text-primary">MISSION</p><p className="mt-3 font-semibold leading-7">한국 기업의 공동 진입·공동 성장 기반을 지원하는 실무 협력 플랫폼</p></div>
              <div className="rounded-xl border bg-slate-50 p-6"><p className="text-sm font-bold text-primary">VISION</p><p className="mt-3 font-semibold leading-7">베트남을 중심으로 신뢰받는 한국 방산 산업협력 네트워크 구축</p></div>
            </div>
            <div className="mt-6 flex flex-wrap gap-2">{['Team Korea', '신뢰', '전문성', '지속가능성'].map((v) => <span key={v} className="rounded-full border border-primary/20 bg-primary/5 px-4 py-2 text-sm font-semibold text-primary">{v}</span>)}</div>
          </div>
        </div>
      </section>

      <section id="work" className="border-y bg-slate-50">
        <div className="mx-auto max-w-7xl px-5 py-20">
          <p className="section-kicker">What We Do</p><h2 className="mt-4 text-3xl font-bold md:text-4xl">협의회가 집중하는 네 가지 역할</h2>
          <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-4">
            {principles.map(({ icon: Icon, title, text }, index) => (
              <article key={title} className="rounded-xl border bg-white p-6 shadow-sm">
                <div className="flex items-center justify-between"><span className="flex size-11 items-center justify-center rounded-lg bg-primary text-white"><Icon className="size-5" /></span><span className="font-bold text-slate-300">0{index + 1}</span></div>
                <h3 className="mt-6 text-xl font-bold">{title}</h3><p className="mt-3 text-sm leading-7 text-slate-600">{text}</p>
              </article>
            ))}
          </div>
        </div>
      </section>

      <section id="members" className="mx-auto max-w-7xl px-5 py-20">
        <div className="grid gap-10 lg:grid-cols-[0.65fr_1.35fr]">
          <div><p className="section-kicker">Member Network</p><h2 className="mt-4 text-3xl font-bold md:text-4xl">방산 밸류체인을 잇는 회원 네트워크</h2><p className="mt-5 leading-7 text-slate-600">개인의 이름과 연락처는 공개하지 않고, 확인된 기관·기업 중심으로 네트워크를 안내합니다.</p></div>
          <div className="grid gap-5">
            {memberGroups.map((group) => (
              <article key={group.title} className="rounded-xl border bg-white p-6"><h3 className="border-b pb-4 text-xl font-bold">{group.title}</h3><div className="mt-5 flex flex-wrap gap-2.5">{group.members.map((m) => <span key={m} className="rounded-md bg-slate-100 px-3.5 py-2 text-sm font-semibold text-slate-700">{m}</span>)}</div></article>
            ))}
            <p className="text-xs leading-6 text-slate-400">기관·기업 정보는 2026년 8월 협의회 자료 기준이며, 최신 참여 상태와 공개 범위에 따라 조정될 수 있습니다.</p>
          </div>
        </div>
      </section>

      <section id="insights" className="bg-slate-950 text-white">
        <div className="mx-auto max-w-7xl px-5 py-20">
          <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
            <div><p className="section-kicker text-sky-300">Defense Intelligence</p><h2 className="mt-4 text-3xl font-bold md:text-4xl">정책자료와 주간 방산 브리핑</h2><p className="mt-4 max-w-2xl leading-7 text-slate-300">공개 화면에는 제목과 요약을 제공하고, 전문과 내부자료는 승인 회원에게만 제공합니다.</p></div>
            <p className="flex items-center gap-2 text-sm text-slate-300"><LockKeyhole className="size-4 text-sky-300" /> 승인 회원 전용 자료 운영</p>
          </div>
          <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
            {visibleResources.length ? visibleResources.map((r) => (
              <article key={r.id} className="rounded-xl border border-white/15 bg-white/[0.06] p-6"><div className="flex justify-between gap-3"><Badge className="bg-sky-200 text-slate-950">{r.category}</Badge><time className="text-xs text-slate-400">{formatDate(r.publishedAt)}</time></div><h3 className="mt-5 text-xl font-bold">{r.title}</h3><p className="mt-3 text-sm leading-7 text-slate-300">{r.summary}</p>{r.memberOnly ? <p className="mt-5 text-xs font-semibold text-sky-300">회원 전용</p> : null}</article>
            )) : <article className="rounded-xl border border-white/15 bg-white/[0.06] p-6"><FileText className="size-6 text-sky-300" /><h3 className="mt-5 text-xl font-bold">공개 인사이트 준비 중</h3><p className="mt-3 text-sm text-slate-300">최신 브리핑 요약을 순차적으로 제공합니다.</p></article>}
          </div>
          <div id="member-library" className="mt-8 rounded-xl border border-white/15 bg-white/[0.04] p-6 md:flex md:items-center md:justify-between">
            <div><p className="font-bold">회원 전용 자료실</p><p className="mt-2 text-sm text-slate-300">주간보고서 전문과 내부 공지는 로그인 및 회원 승인 후 열람할 수 있습니다.</p></div>
            <div className="mt-4 md:mt-0"><Button nativeButton={false} render={<a href={access.user ? chatGPTSignOutPath('/') : chatGPTSignInPath('/#member-library')} />}>{access.user ? '로그아웃' : '회원 로그인'}</Button></div>
          </div>
        </div>
      </section>

      <section id="activities" className="mx-auto max-w-7xl px-5 py-20">
        <p className="section-kicker">Council Activities</p><h2 className="mt-4 text-3xl font-bold md:text-4xl">현장에서 이어가는 주요 활동</h2><p className="mt-4 text-slate-600">협의회 전용 폴더에서 확인된 공식 활동사진만 선별해 사용했습니다.</p>
        <div className="mt-10 grid gap-6 lg:grid-cols-2">
          {activities.map((item) => <article key={item.title} className="overflow-hidden rounded-xl border bg-white shadow-sm"><div className="relative aspect-[4/3]"><Image src={item.image} alt={item.title} fill className="object-cover" /></div><div className="p-6"><p className="text-xs font-bold uppercase tracking-wider text-primary">{item.label}</p><h3 className="mt-2 text-xl font-bold">{item.title}</h3><p className="mt-3 text-sm leading-7 text-slate-600">{item.text}</p></div></article>)}
        </div>
      </section>

      <section className="border-y bg-slate-50">
        <div className="mx-auto grid max-w-7xl gap-10 px-5 py-20 lg:grid-cols-[0.7fr_1.3fr]">
          <div><p className="section-kicker">News & Events</p><h2 className="mt-4 text-3xl font-bold">공지와 주요 일정</h2></div>
          <div className="grid gap-6 lg:grid-cols-2">
            <div><h3 className="mb-4 flex items-center gap-2 font-bold"><FileText className="size-5 text-primary" /> 최근 공지</h3><div className="space-y-3">{announcements.slice(0,3).map((item) => <article key={item.id} className="rounded-lg border bg-white p-5"><time className="text-xs text-slate-400">{formatDate(item.publishedAt)}</time><h4 className="mt-2 font-bold">{item.title}</h4><p className="mt-2 text-sm leading-6 text-slate-600">{item.summary}</p></article>)}</div></div>
            <div><h3 className="mb-4 flex items-center gap-2 font-bold"><CalendarDays className="size-5 text-primary" /> 주요 예정 일정</h3><div className="space-y-3">{events.slice(0,3).map((event) => <article key={event.id} className="rounded-lg border bg-white p-5"><time className="text-xs font-bold text-primary">{formatDate(event.eventDate)}</time><h4 className="mt-2 font-bold">{event.title}</h4><p className="mt-2 text-sm leading-6 text-slate-600">{event.location} · {event.summary}</p></article>)}</div></div>
          </div>
        </div>
      </section>

      <section id="contact" className="mx-auto max-w-7xl px-5 py-20">
        <div className="overflow-hidden rounded-2xl bg-primary text-white"><div className="grid lg:grid-cols-[1fr_0.9fr]">
          <div className="p-8 md:p-12"><p className="text-sm font-bold uppercase tracking-wider text-sky-200">Membership & Contact</p><h2 className="mt-4 text-3xl font-bold md:text-4xl">함께할 기업과 기관을 기다립니다</h2><p className="mt-5 max-w-xl leading-8 text-blue-100">방산 완제품뿐 아니라 부품·소재, ICT, 상사, 물류와 전문서비스 등 방산 밸류체인 전반의 기업이 참여할 수 있습니다. 가입과 활동 문의는 협의회 총무에게 연락해 주세요.</p><div className="mt-8 flex flex-wrap gap-3">{['정회원','일반회원','협력회원','특별회원'].map((v) => <span key={v} className="rounded-full border border-white/25 px-4 py-2 text-sm font-semibold">{v}</span>)}</div></div>
          <div className="bg-white p-8 text-slate-900 md:p-12"><p className="text-sm font-bold text-primary">한국방산협의회 문의처</p><h3 className="mt-3 text-xl font-bold">현대코퍼레이션 노채준 지사장 <span className="text-base font-medium text-slate-500">(총무)</span></h3><div className="mt-6 space-y-4 text-sm"><a href="tel:+84823755024" className="flex items-center gap-3 font-semibold hover:text-primary"><Phone className="size-5 text-primary" /> +84 823 755 024</a><a href="mailto:cjroh@hyundaicorp.com" className="flex items-center gap-3 font-semibold hover:text-primary"><Mail className="size-5 text-primary" /> cjroh@hyundaicorp.com</a><p className="flex items-start gap-3 leading-6 text-slate-600"><MapPin className="mt-0.5 size-5 shrink-0 text-primary" /> R1214, Keangnam Hanoi Landmark Tower, Yen Hoa Ward, Hanoi</p></div></div>
        </div></div>
      </section>

      <section id="privacy" className="border-t bg-slate-50"><div className="mx-auto max-w-7xl px-5 py-8 text-xs leading-6 text-slate-500"><strong className="text-slate-700">정보 이용 안내</strong> 공개 홈페이지에는 공개 승인 정보만 제공합니다. 회원 전용 보고서와 내부자료는 승인된 회원에게만 제공하며 개인 연락처와 내부 협의 내용은 공개하지 않습니다.</div></section>
      <footer className="bg-slate-950 text-slate-300"><div className="mx-auto flex max-w-7xl flex-col gap-5 px-5 py-8 md:flex-row md:items-center md:justify-between"><div className="flex items-center gap-3"><ShieldCheck className="size-5 text-sky-300" /><div><p className="font-bold text-white">한국방산협의회</p><p className="text-xs">Korea Defense Council in Vietnam</p></div></div><div className="flex gap-5 text-xs"><a href="#about">협의회 소개</a><a href="#privacy">정보 이용 안내</a><a href="#contact">문의</a></div></div></footer>
    </main>
  );
}
