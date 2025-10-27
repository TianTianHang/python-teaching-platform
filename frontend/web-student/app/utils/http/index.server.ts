// src/utils/http/index.ts
import { Http } from './http';
import type { CustomInternalRequestConfig, CustomRequest, CustomRequestConfig, InterceptorHooks } from './types';
import { handleHttpError } from './error';
import { commitSession, getSession } from '~/sessions.server';
import { data } from "react-router";
const isServer = typeof window === 'undefined';
const getBaseURL = () => {
  if (isServer) {
    // 服务端：必须用完整后端地址（不能依赖代理）
    return process.env.API_BASE_URL || 'http://localhost:8080';
  } else {
    // 客户端：可以用 Vite 代理前缀（如 /api），或完整 URL
    return import.meta.env.VITE_API_BASE_URL || '/api/v1';
  }
};
// ----------------- 全局默认配置 -----------------
const globalConfig: CustomRequestConfig = {
  // 确保这指向你的 DRF 后端 API 地址
  baseURL: getBaseURL(),
  timeout: 10000, // 10秒超时
  responseType: 'json',
  withCredentials: true, // Enable cookies for cross-origin requests
  headers: {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json', // 明确告诉 DRF 我们需要 JSON
  },
};

// ----------------- 全局拦截器钩子 (可选) -----------------
const globalHooks: InterceptorHooks = {
  requestInterceptor: async (config) => {
    // 示例：启动全局 loading
   
    return config;
  },
  requestInterceptorCatch(error) {
    return Promise.reject(error);
  },
  responseInterceptor: (response) => {
    // 示例：关闭全局 loading
    // endLoading();

    return response;
  },
  responseInterceptorCatch: async (error) => {
    // 示例：关闭全局 loading
    // endLoading();
    // 2. 处理 HTTP 错误 (4xx, 5xx, 网络错误)
    const originalRequest = error.config as CustomInternalRequestConfig;
  
    handleHttpError(error, originalRequest);
    return Promise.reject(error);
  }
};


// 请求上下文存储（每个请求独立）
const responseContext = new WeakMap<Request, { setCookie?: string }>();

export function setResponseSetCookie(request: Request, setCookie: string) {
  if (!responseContext.has(request)) {
    responseContext.set(request, {});
  }
  responseContext.get(request)!.setCookie = setCookie;
}

export function createResponse<T>(request: Request, d: T, init?: ResponseInit) {
  const ctx = responseContext.get(request);
  const headers = new Headers(init?.headers);
  
  if (ctx?.setCookie) {
    headers.append('Set-Cookie', ctx.setCookie);
  }

  return data<T>(d, { ...init, headers });
}
// 工厂函数：创建带 token 的 HTTP 客户端
export function createHttp(request: Request) {
  return new Http(
    globalConfig,
    async () => {
      // 👇 关键：从 request 的 Cookie 中读取 session
      const session = await getSession(request.headers.get('Cookie'));
      
      return {access:session.get('accessToken'),refresh:session.get('refreshToken')}; // 你之前存的是 'accessToken'
    },
    async (newToken)=>{
      const session = await getSession(request.headers.get('Cookie'));
      
      session.set("accessToken",newToken.access);
      session.set('refreshToken',newToken.refresh);
      const setCookie =await commitSession(session);
      setResponseSetCookie(request, setCookie);
    },
    "/auth/refresh",
    globalHooks
  );
}
// ----------------- 导出单例 -----------------
export default createHttp;

// ----------------- 导出类型和工具 -----------------
export * from './types';