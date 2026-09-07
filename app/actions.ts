'use server';

import { revalidatePath } from 'next/cache';
import { desc, eq } from 'drizzle-orm';
import { env } from 'cloudflare:workers';
import { getChatGPTUser } from './chatgpt-auth';
import { getDb } from '@/db';
import { memberApplications, memberCompanies } from '@/db/schema';
import { isAdminEmail } from '@/lib/access';

const requiredApplicationFields = [
  'companyName',
  'contactName',
  'position',
  'phone',
  'email',
  'location',
  'interestArea',
  'purpose',
] as const;

export async function submitMembershipApplication(formData: FormData) {
  const values = Object.fromEntries(
    requiredApplicationFields.map((field) => [
      field,
      String(formData.get(field) ?? '').trim(),
    ]),
  ) as Record<(typeof requiredApplicationFields)[number], string>;

  const missing = requiredApplicationFields.some((field) => !values[field]);
  if (missing || !values.email.includes('@')) {
    return;
  }

  const db = getDb();
  await db.insert(memberApplications).values({
    id: crypto.randomUUID(),
    ...values,
    status: '대기',
    createdAt: new Date(),
  });

  revalidatePath('/');
}

export async function reviewMembershipApplication(formData: FormData) {
  const user = await getChatGPTUser();
  if (!user || !isAdminEmail(user.email)) return;

  const applicationId = String(formData.get('applicationId') ?? '');
  const status = String(formData.get('status') ?? '');
  if (!applicationId || !['승인', '반려'].includes(status)) return;

  const db = getDb();
  const [application] = await db
    .select()
    .from(memberApplications)
    .where(eq(memberApplications.id, applicationId))
    .limit(1);
  if (!application) return;

  await db
    .update(memberApplications)
    .set({
      status,
      reviewerEmail: user.email,
      reviewedAt: new Date(),
    })
    .where(eq(memberApplications.id, applicationId));

  if (status === '승인') {
    await db.insert(memberCompanies).values({
      id: crypto.randomUUID(),
      category: application.interestArea,
      companyName: application.companyName,
      representative: application.contactName,
      role: application.position,
      location: application.location,
      note: '회원가입 신청 승인',
      contactEmail: application.email,
      approvedAt: new Date(),
    });
  }

  revalidatePath('/');
}

export async function getApplicationsForAdmin() {
  const user = await getChatGPTUser();
  if (!user || !isAdminEmail(user.email)) return [];

  try {
    return await getDb()
      .select()
      .from(memberApplications)
      .orderBy(desc(memberApplications.createdAt));
  } catch {
    return [];
  }
}
