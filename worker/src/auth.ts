import { SignJWT, jwtVerify } from 'jose';
import type { Env, User } from './types';

export async function hashPassword(password: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(password);
  const hash = await crypto.subtle.digest('SHA-256', data);
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const saltedData = new Uint8Array([...salt, ...new Uint8Array(hash)]);
  return btoa(String.fromCharCode(...saltedData));
}

export async function verifyPassword(password: string, stored: string): Promise<boolean> {
  const decoded = Uint8Array.from(atob(stored), c => c.charCodeAt(0));
  const salt = decoded.slice(0, 16);
  const storedHash = decoded.slice(16);
  const encoder = new TextEncoder();
  const hash = await crypto.subtle.digest('SHA-256', encoder.encode(password));
  const hashArr = new Uint8Array(hash);
  if (hashArr.length !== storedHash.length) return false;
  return hashArr.every((b, i) => b === storedHash[i]);
}

export async function createToken(userId: string, secret: string): Promise<string> {
  const key = new TextEncoder().encode(secret);
  return new SignJWT({ sub: userId })
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime('24h')
    .setIssuedAt()
    .sign(key);
}

export async function verifyToken(token: string, secret: string): Promise<string | null> {
  try {
    const key = new TextEncoder().encode(secret);
    const { payload } = await jwtVerify(token, key);
    return payload.sub as string;
  } catch {
    return null;
  }
}

export async function getUser(env: Env, request: Request): Promise<User | null> {
  const auth = request.headers.get('Authorization');
  if (!auth?.startsWith('Bearer ')) return null;

  const token = auth.slice(7);
  const userId = await verifyToken(token, env.JWT_SECRET);
  if (!userId) return null;

  const row = await env.DB.prepare(
    'SELECT id, email, display_name, preferred_language, canton, tier, is_admin, is_editor FROM users WHERE id = ?'
  ).bind(userId).first();

  if (!row) return null;
  return {
    id: row.id as string,
    email: row.email as string | null,
    display_name: row.display_name as string | null,
    preferred_language: row.preferred_language as string,
    canton: row.canton as string | null,
    tier: row.tier as string,
    is_admin: !!(row.is_admin as number),
    is_editor: !!(row.is_editor as number),
  };
}

export function requireAuth(user: User | null): User {
  if (!user) throw new Response('Unauthorized', { status: 401 });
  return user;
}

export function requireEditor(user: User | null): User {
  const u = requireAuth(user);
  if (!u.is_editor && !u.is_admin) throw new Response('Forbidden', { status: 403 });
  return u;
}
