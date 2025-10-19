// src/utils/http/index.ts
import { Http } from './http';
import type { CustomRequestConfig, InterceptorHooks } from './types';
const getBaseURL = () => {
  if (typeof window === 'undefined') {
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
    return config;
  },
  responseInterceptor: (response) => {
    // 示例：关闭全局 loading
    // endLoading();
    return response;
  },
  responseInterceptorCatch: (error) => {
    // 示例：关闭全局 loading
    // endLoading();
    return Promise.reject(error);
  }
};

// ----------------- 导出单例 -----------------
const http = new Http(globalConfig, globalHooks);

export default http;

// ----------------- 导出类型和工具 -----------------
export * from './types';
export { Http } from './http';