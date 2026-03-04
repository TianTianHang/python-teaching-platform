// Client-side HTTP client using localStorage for tokens
import axios, { type AxiosInstance, type AxiosError } from 'axios';
import type { Token } from '~/types/user';
import type { CustomRequestConfig, InterceptorHooks } from './types';

const TOKEN_KEY = 'auth_token';

// 保留两个 API_BASE_URL
// VITE_API_BASE_URL: 客户端直连后端（需要后端配置 CORS）
// API_BASE_URL: 服务端转发用
const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    // 客户端：优先使用直连后端地址
    return import.meta.env.VITE_API_BASE_URL || '/api/v1';
  }
  // 服务端：使用服务端转发地址（用于 SSR）
  return process.env.API_BASE_URL || 'http://localhost:8080/api/v1';
};

// 获取存储的 token
function getStoredToken(): Token | null {
  if (typeof window === 'undefined') return null;
  const tokenStr = localStorage.getItem(TOKEN_KEY);
  if (!tokenStr) return null;
  try {
    return JSON.parse(tokenStr);
  } catch {
    return null;
  }
}

// 存储 token
function setStoredToken(token: Token): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, JSON.stringify(token));
}

// 清除 token
function clearStoredToken(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
}

// 创建客户端 axios 实例
function createAxiosInstance(): AxiosInstance {
  const instance = axios.create({
    baseURL: getApiBaseUrl(),
    timeout: 10000,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
  });

  // 请求拦截器 - 自动添加 token
  instance.interceptors.request.use(
    (config) => {
      const token = getStoredToken();
      if (token?.access && config.headers) {
        config.headers.Authorization = `Bearer ${token.access}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // 响应拦截器 - 处理 401 自动刷新
  instance.interceptors.response.use(
    (response) => response.data,
    async (error: AxiosError) => {
      const originalRequest = error.config as CustomRequestConfig;

      // 如果 401 且不是刷新请求本身，尝试刷新 token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        const token = getStoredToken();
        if (token?.refresh) {
          try {
            const refreshResponse = await axios.post<Token>(
              `${getApiBaseUrl()}/auth/refresh`,
              { refresh: token.refresh }
            );
            const newToken = refreshResponse.data;
            setStoredToken(newToken);

            // 重试原请求
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken.access}`;
            }
            return instance(originalRequest);
          } catch (refreshError) {
            // 刷新失败，清除 token
            clearStoredToken();
            // 可以在这里触发全局登出事件
            window.location.href = '/auth/login';
            return Promise.reject(refreshError);
          }
        }
      }

      return Promise.reject(error);
    }
  );

  return instance;
}

// 全局 axios 实例（单例）
let clientHttpInstance: AxiosInstance | null = null;

function getClientHttp(): AxiosInstance {
  if (!clientHttpInstance) {
    clientHttpInstance = createAxiosInstance();
  }
  return clientHttpInstance;
}

// 客户端 HTTP 客户端 API
export const clientHttp = {
  // 直接获取 axios 实例（用于自定义配置）
  getInstance: getClientHttp,

  // GET 请求
  get: <T = any>(url: string, params?: object, config?: CustomRequestConfig): Promise<T> => {
    return getClientHttp().get(url, { params, ...config });
  },

  // POST 请求
  post: <T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T> => {
    return getClientHttp().post(url, data, config);
  },

  // PUT 请求
  put: <T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T> => {
    return getClientHttp().put(url, data, config);
  },

  // DELETE 请求
  delete: <T = any>(url: string, params?: object, config?: CustomRequestConfig): Promise<T> => {
    return getClientHttp().delete(url, { params, ...config });
  },

  // PATCH 请求
  patch: <T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T> => {
    return getClientHttp().patch(url, data, config);
  },
};

// Auth 工具
export const clientAuth = {
  // 获取当前 token
  getToken: getStoredToken,

  // 设置 token
  setToken: setStoredToken,

  // 清除 token
  clearToken: clearStoredToken,

  // 检查是否已登录
  isAuthenticated: (): boolean => {
    const token = getStoredToken();
    return !!token?.access;
  },

  // 登录（直接调用后端 API）
  login: async (username: string, password: string): Promise<{ token: Token; user: any }> => {
    const response = await axios.post<Token>(
      `${getApiBaseUrl()}/auth/login`,
      { username, password }
    );

    const token = response.data;
    setStoredToken(token);

    // 获取用户信息
    const userResponse = await axios.get(
      `${getApiBaseUrl()}/auth/me`,
      {
        headers: { Authorization: `Bearer ${token.access}` },
      }
    );

    return { token, user: userResponse.data };
  },

  // 登出
  logout: async (): Promise<void> => {
    const token = getStoredToken();
    if (token?.refresh) {
      try {
        await axios.post(
          `${getApiBaseUrl()}/auth/logout`,
          { refresh: token.refresh }
        );
      } catch {
        // 忽略错误
      }
    }
    clearStoredToken();
  },
};

export default clientHttp;
