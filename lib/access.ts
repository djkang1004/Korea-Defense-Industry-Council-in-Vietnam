import { env } from 'cloudflare:workers';

export function isAdminEmail(email: string) {
  const adminEmails = (env as { ADMIN_EMAILS?: string }).ADMIN_EMAILS ?? '';

  return adminEmails
    .split(',')
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean)
    .includes(email.toLowerCase());
}
