// src/utils/http/index.ts
import axios from 'axios';
import { Http } from './http';
import type { CustomRequestConfig, InterceptorHooks } from './types';
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

// ----------------- 全局拦截器钩子 (可选) -----------------
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
    const config = error.config as CustomRequestConfig;
    handleHttpError(error, config);
    return Promise.reject(error);
  }
};

// ----------------- 导出单例 -----------------
const http = new Http(globalConfig, globalHooks);

export default http;

// ----------------- 导出类型和工具 -----------------
export * from './types';
export { Http } from './http';