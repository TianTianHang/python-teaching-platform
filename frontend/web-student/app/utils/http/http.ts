// src/utils/http/http.ts
import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError, AxiosRequestConfig } from 'axios';
import type { CustomRequestConfig, IHttp, InterceptorHooks } from './types';
import { commitSession, getSession } from '~/sessions.server';



const refreshLocks = new Map<number, Promise<{ access: string, refresh: string }>>();

// 请求上下文存储（每个请求独立）
export const responseContext = new WeakMap<Request, { setCookie?: string }>();

export function setResponseSetCookie(request: Request, setCookie: string) {
  if (!responseContext.has(request)) {
    responseContext.set(request, {});
  }
  responseContext.get(request)!.setCookie = setCookie;
}

export class Http implements IHttp {
  private instance: AxiosInstance;
  private ctx: Request;
  constructor(config: CustomRequestConfig,
    ctx: Request,
    hooks?: InterceptorHooks) {
    // 1. 创建 Axios 实例
    this.instance = axios.create(config);
    this.ctx = ctx;
   
    // 2. 设置拦截器
    this.setupInterceptors(hooks);
  }
  private async getToken() {
    const session = await getSession(this.ctx.headers.get('Cookie'));
    return { access: session.get('accessToken'), refresh: session.get('refreshToken') };
  }
  private async getUserId() {
    const session = await getSession(this.ctx.headers.get('Cookie'));
    return session.get("user")?.id;
  }
  private async setToken(newToken: { access: string, refresh: string }) {
    const session = await getSession(this.ctx.headers.get('Cookie'));

    session.set("accessToken", newToken.access);
    session.set('refreshToken', newToken.refresh);
    const setCookie = await commitSession(session);
    setResponseSetCookie(this.ctx, setCookie);
  }
  // --------------------------------------------------
  // 拦截器设置
  // --------------------------------------------------
  private setupInterceptors(hooks?: InterceptorHooks) {
    // ----------------- 请求拦截器 (不变) -----------------
    this.instance.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token && config.headers && !config.headers.Authorization) {
          // DRF 默认使用 'Authorization: Token <token>' 或 'Bearer <token>'
          config.headers.Authorization = `Bearer ${token.access}`;
          // 如果你使用 'Token' 方案，请改为 `Token ${token}`
        }
        if (hooks?.requestInterceptor) {
          return hooks.requestInterceptor(config);
        }

        return config;
      },
      (error) => {
        if (hooks?.requestInterceptorCatch) {
          return hooks.requestInterceptorCatch(error);
        }
        return Promise.reject(error);
      }
    );

    // ----------------- 响应拦截器 (!! 核心修改 !!) -----------------
    this.instance.interceptors.response.use(
      async <T = any>(response: AxiosResponse<T>) => {


        // 1. 优先执行传入的钩子
        if (hooks?.responseInterceptor) {
          response = await hooks.responseInterceptor(response);
        }

        // 2. 处理文件流/Blob (如果 responseType 不是 'json')
        // 如果是文件流，直接返回完整的 response，让业务层处理
        if (response.config.responseType !== 'json' || response.data instanceof Blob) {
          return response;
        }



        // DRF/Restful 风格, 2xx 状态码, response.data 就是业务所需的数据
        // 我们直接返回 data
        return response.data;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as CustomRequestConfig;

        // // 仅处理 401 且不是重试请求
        // if (error.response?.status === 401 && !originalRequest._retry) {
        //   const userId = await this.getUserId();
        //   if (userId == null) {
        //     return Promise.reject(error);
        //   }
        //   const existingRefresh = refreshLocks.get(userId);
        //   if (existingRefresh) {
        //     const newToken = await existingRefresh;
        //     originalRequest.headers!.Authorization = `Bearer ${newToken.access}`;
        //     return this.instance(originalRequest)
        //   }


        //   originalRequest._retry = true;
        //   // 2. 没有刷新正在进行，自己来
        //   const refreshPromise = (async () => {
        //     try {
        //       const token = await this.getToken();
        //       if (!token?.refresh) {
        //         throw new Error('No refresh token available');
        //       }

        //       // 调用刷新接口
        //       const response = await this.post<{ access: string, refresh: string }>(this.refreshTokenUrl, {
        //         refresh: token.refresh,
        //       });

        //       const newToken = { access: response.access, refresh: response.refresh };

        //       return newToken;
        //     } finally {
        //       // 无论成功失败，都要释放锁
        //       refreshLocks.delete(userId);
        //     }
        //   })();

        //   // 3. 设置锁
        //   refreshLocks.set(userId, refreshPromise);

        //   // 4. 等待自己完成
        //   try {
        //     const newToken = await refreshPromise; // <-- 潜在的异常点

        //     // 5. 成功：保存新 token 并重试
        //     await this.setToken(newToken);
        //     // 重试原始请求
        //     originalRequest.headers!.Authorization = `Bearer ${newToken.access}`;
        //     return this.instance(originalRequest);
        //   } catch (refreshError) {
        //     // 6. 失败：刷新 token 失败，清除 session，并拒绝原始请求
        //     // 此时锁已在 refreshPromise 的 finally 中释放
        //     // 可以选择在这里清除过期的 token session (可选，视业务要求)
        //     // 也可以直接返回错误，让上层知道需要重新登录
            
        //     // 必须拒绝原始请求
        //     return Promise.reject(refreshError); 
        //   }

        // }
        // 1. 优先执行传入的钩子
        if (hooks?.responseInterceptorCatch) {
          return hooks.responseInterceptorCatch(error);
        }

        // 3. 必须将 error reject 出去，业务层的 .catch() 才能捕获
        return Promise.reject(error);
      }
    );
  }

  // --------------------------------------------------
  // 核心请求方法
  // --------------------------------------------------

  /**
   * @description 核心请求方法
   * @template T 响应数据 `response.data` 的类型
   * @param {CustomRequestConfig} config axios 配置
   * @returns {Promise<T>} 返回一个 Promise，它会 resolve 为 `response.data`
   */
  public request<T = any>(config: CustomRequestConfig): Promise<T> {
    // 响应拦截器会处理 `response.data` 的提取
    return this.instance.request(config);
  }

  // --------------------------------------------------
  // 封装的便捷方法 (不变)
  // --------------------------------------------------

  public get<T = any>(url: string, params?: object, config?: CustomRequestConfig): Promise<T> {
    return this.instance.get(url, { params, ...config });
  }

  public post<T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T> {
    return this.instance.post(url, data, config);
  }

  public put<T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T> {
    return this.instance.put(url, data, config);
  }

  public delete<T = any>(url: string, params?: object, config?: CustomRequestConfig): Promise<T> {
    return this.instance.delete(url, { params, ...config });
  }

  public patch<T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T> {
    return this.instance.patch(url, data, config);
  }

  // --------------------------------------------------
  // 静态工具方法 (不变)
  // --------------------------------------------------

  /**
   * @description 检查是否为 Axios 取消错误
   */
  public static isCancel(error: any): boolean {
    return axios.isCancel(error);
  }
}