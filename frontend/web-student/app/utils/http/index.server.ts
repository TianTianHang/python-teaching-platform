// src/utils/http/index.ts
import { Http } from './http';
import type { CustomInternalRequestConfig, CustomRequestConfig, } from './types';
import { handleHttpError, UnauthorizedRedirectError } from './error';
import { redirect } from 'react-router';
const isServer = typeof window === 'undefined';
const getBaseURL = () => {
  if (isServer) {
    // 服务端：必须用完整后端地址（不能依赖代理）
    return process.env.API_BASE_URL || 'http://localhost:8080/api/v1';
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



// 工厂函数：创建带 token 的 HTTP 客户端
export function createHttp(request: Request, {
  onUnauthorized,
}: {
  onUnauthorized?: () => Response; // 返回 redirect 响应
} = {
  onUnauthorized: () => {
    const url = new URL(request.url);
    return redirect(`/refresh?back=${encodeURIComponent(url.pathname)}`);
  },
  }) {

  return new Http(
    globalConfig,
    request,
    {
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
        // 🔥 关键：检测 401 且提供了 onUnauthorized
        if (
          error.response?.status === 401 &&
          onUnauthorized &&
          !originalRequest._retry &&// 防止无限重试（可选）
          originalRequest.url!=="/auth/refresh"
        ) {
          // 抛出自定义错误，携带 redirect 响应
          const error = new UnauthorizedRedirectError(onUnauthorized());
          throw error
        }
        handleHttpError(error, originalRequest);

        return Promise.reject(error);
      }
    },
  );
}
// ----------------- 导出单例 -----------------
export default createHttp;

// ----------------- 导出类型和工具 -----------------
export * from './types';