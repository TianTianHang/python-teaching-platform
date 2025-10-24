// src/utils/http/index.ts
import axios from 'axios';
import { Http } from './http';
import type { CustomInternalRequestConfig, CustomRequestConfig, InterceptorHooks } from './types';
import { handleHttpError } from './error';
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
  headers: {
    'Content-Type': 'application/json;charset=UTF-8',
    'Accept': 'application/json', // 明确告诉 DRF 我们需要 JSON
  },
};
// ----------------- 延迟引用：用于重发请求 -----------------
let currentHttpInstance: Http | null = null;
// ----------------- 全局拦截器钩子 (可选) -----------------
let isRefreshing = false;
let refreshPromise: Promise<string> | null = null; // 缓存刷新 Promise，避免重复请求
const globalHooks: InterceptorHooks = {
  requestInterceptor: (config) => {
    // 示例：启动全局 loading
    // startLoading(); 
    if (!isServer) {
      // 2. 添加通用逻辑，例如 Token
      // 假设你使用 DRF 的 TokenAuthentication 或 JWTAuthentication
      const token = localStorage.getItem('accessToken');
      if (token && config.headers) {
        // DRF 默认使用 'Authorization: Token <token>' 或 'Bearer <token>'
        config.headers.Authorization = `Bearer ${token}`;
        // 如果你使用 'Token' 方案，请改为 `Token ${token}`
      }
    }
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
    // 仅处理 401 且不是重试过的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // 如果正在刷新，等待刷新完成后再重试
        try {
          const newToken = await refreshPromise!;
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return currentHttpInstance?.request(originalRequest); // 注意：这里需要能访问到 axios 实例
        } catch (err) {
          // 刷新失败，跳转登录
          handleTokenRefreshFailure();
          return Promise.reject(err);
        }
      }

      // 开始刷新流程
      originalRequest._retry = true;
      isRefreshing = true;
      if (!isServer) {
        const token = localStorage.getItem('refreshToken');
        if (token) {
          // 创建刷新 Promise（确保多个请求共享同一个刷新过程）
          refreshPromise = refreshToken(token)
            .then((newToken) => {
              localStorage.setItem('accessToken', newToken);
              isRefreshing = false;
              refreshPromise = null;
              return newToken;
            })
            .catch((err) => {
              isRefreshing = false;
              refreshPromise = null;
              handleTokenRefreshFailure();
              throw err;
            });

          try {
            const newToken = await refreshPromise;
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return currentHttpInstance?.request(originalRequest); // 重发原请求
          } catch (err) {
            return Promise.reject(err);
          }
        }
      }
    }


    handleHttpError(error, originalRequest);
    return Promise.reject(error);
  }
};
// ----------------- 辅助函数 -----------------

// 调用后端刷新接口
async function refreshToken(refresh: string): Promise<string> {

  const response = await axios.post<{ access: string }>(`${getBaseURL()}/auth/refresh`, { refresh });
  return response.data.access; // 根据后端返回结构调整
}

// 刷新失败处理：清除本地 token，跳转登录
function handleTokenRefreshFailure() {
  localStorage.removeItem('accessToken');
  // 可选：跳转到登录页
  if (!isServer) {
    window.location.href = '/auth/login';
  }
}
// ----------------- 导出单例 -----------------
const http = new Http(globalConfig, globalHooks);
currentHttpInstance = http;
export default http;

// ----------------- 导出类型和工具 -----------------
export * from './types';
export { Http } from './http';