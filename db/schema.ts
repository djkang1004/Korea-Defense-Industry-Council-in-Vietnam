import { integer, sqliteTable, text } from 'drizzle-orm/sqlite-core';

export const memberApplications = sqliteTable('member_applications', {
  id: text('id').primaryKey(),
  companyName: text('company_name').notNull(),
  contactName: text('contact_name').notNull(),
  position: text('position').notNull(),
  phone: text('phone').notNull(),
  email: text('email').notNull(),
  location: text('location').notNull(),
  interestArea: text('interest_area').notNull(),
  purpose: text('purpose').notNull(),
  status: text('status').notNull().default('대기'),
  reviewerEmail: text('reviewer_email'),
  createdAt: integer('created_at', { mode: 'timestamp_ms' }).notNull(),
  reviewedAt: integer('reviewed_at', { mode: 'timestamp_ms' }),
});

export const memberCompanies = sqliteTable('member_companies', {
  id: text('id').primaryKey(),
  category: text('category').notNull(),
  companyName: text('company_name').notNull(),
  representative: text('representative').notNull(),
  role: text('role').notNull(),
  location: text('location').notNull(),
  note: text('note'),
  contactEmail: text('contact_email'),
  approvedAt: integer('approved_at', { mode: 'timestamp_ms' }),
});

export const announcements = sqliteTable('announcements', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  category: text('category').notNull(),
  summary: text('summary').notNull(),
  publishedAt: integer('published_at', { mode: 'timestamp_ms' }).notNull(),
  memberOnly: integer('member_only', { mode: 'boolean' }).notNull().default(false),
});

export const events = sqliteTable('events', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  eventDate: integer('event_date', { mode: 'timestamp_ms' }).notNull(),
  location: text('location').notNull(),
  summary: text('summary').notNull(),
});

export const resources = sqliteTable('resources', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  category: text('category').notNull(),
  fileName: text('file_name').notNull(),
  summary: text('summary').notNull(),
  memberOnly: integer('member_only', { mode: 'boolean' }).notNull().default(true),
  publishedAt: integer('published_at', { mode: 'timestamp_ms' }).notNull(),
});
