// app/sessions.ts
import { createCookieSessionStorage } from 'react-router';
import type { User } from './types/user';

// 你可以根据环境设置 secret（必须保密！）
const SESSION_SECRET = process.env.SESSION_SECRET || 'your-fallback-secret-for-dev';
type SessionData = {
  user: User;
  accessToken: string;
  refreshToken:string
  isAuthenticated:boolean;
};

type SessionFlashData = {
  error: string;
};
export const sessionStorage = createCookieSessionStorage<SessionData, SessionFlashData>({
  cookie: {
    name: '_session', // Cookie 名称
    httpOnly: true,   // 防止 XSS
    secure: process.env.NODE_ENV === 'production', // 仅 HTTPS
    sameSite: 'lax',  // CSRF 防护
    path: '/',
    maxAge: 60 * 60 * 24 * 7, // 7 天（秒）
    secrets: [SESSION_SECRET],
  },
});

// 导出常用方法
export const { getSession, commitSession, destroySession } = sessionStorage;