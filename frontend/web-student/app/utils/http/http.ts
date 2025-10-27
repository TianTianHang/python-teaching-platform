// src/utils/http/http.ts
import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError, AxiosRequestConfig } from 'axios';
import type { CustomRequestConfig, IHttp, InterceptorHooks } from './types';




export class Http implements IHttp {
  private instance: AxiosInstance;
  private getToken: () => { access: string, refresh: string } | null | Promise<{ access: string, refresh: string } | null>;
  private setToken: (newToken:{ access: string, refresh: string })=>Promise<void>;
  private refreshTokenUrl: string; // 用于刷新 token 的 API 地址
  private isRefreshing = false;
  private failedQueue: Array<{
    resolve: (value?: AxiosRequestConfig) => void;
    reject: (error?: any) => void;
    originalRequest: CustomRequestConfig
  }> = [];
  constructor(config: CustomRequestConfig,
    getToken: () => { access: string, refresh: string } | null | Promise<{ access: string, refresh: string } | null>,
    setToken:(newToken:{ access: string, refresh: string })=>Promise<void>,
    refreshTokenUrl: string, // 新增：刷新 token 的 endpoint
    hooks?: InterceptorHooks) {
    // 1. 创建 Axios 实例
    this.instance = axios.create(config);
    this.getToken = getToken;
    this.setToken = setToken;
    this.refreshTokenUrl = refreshTokenUrl;
    // 2. 设置拦截器
    this.setupInterceptors(hooks);
  }

  // --------------------------------------------------
  // 拦截器设置
  // --------------------------------------------------
  private setupInterceptors(hooks?: InterceptorHooks) {
    // ----------------- 请求拦截器 (不变) -----------------
    this.instance.interceptors.request.use(
      async (config) => {
        const token = await this.getToken();
        if (token && config.headers&&!config.headers.Authorization) {
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

        // 仅处理 401 且不是重试请求
        if (error.response?.status === 401 && !originalRequest._retry) {
          if (this.isRefreshing) {
            return new Promise((resolve, reject) => {
              this.failedQueue.push({ resolve, reject, originalRequest }); // ← 保存 originalRequest
            }).then((config) => {
              return this.instance(config as CustomRequestConfig); // config 是修补后的完整请求
            });
          }

          this.isRefreshing = true;
          originalRequest._retry = true;

          try {
            const token = await this.getToken();
            if (!token?.refresh) {
              throw new Error('No refresh token available');
            }

            // 调用刷新接口
            const response = await this.post<{ access: string,refresh:string }>(this.refreshTokenUrl, {
              refresh: token.refresh,
            });

            const newToken = { access: response.access, refresh: response.refresh };
            // 通常这里会调用一个 setToken 回调来更新本地存储（你可能需要从外部传入）
            await this.setToken(newToken);

            // 重试所有排队的请求
            this.processQueue(null, newToken.access);

            // 重试原始请求
            originalRequest.headers!.Authorization = `Bearer ${newToken.access}`;
            return this.instance(originalRequest);
          } catch (refreshError) {
            this.processQueue(refreshError, null);
            // 可在此处触发登出逻辑（如清除 token、跳转登录页）
            return Promise.reject(refreshError);
          } finally {
            this.isRefreshing = false;
          }
        }
        // 1. 优先执行传入的钩子
        if (hooks?.responseInterceptorCatch) {
          return hooks.responseInterceptorCatch(error);
        }

        // 3. 必须将 error reject 出去，业务层的 .catch() 才能捕获
        return Promise.reject(error);
      }
    );
  }
  // 处理队列中的请求
  private processQueue(error: any, token: string | null = null) {
  this.failedQueue.forEach(({ resolve, reject, originalRequest }) => {
    if (error) {
      reject(error);
    } else if (token) {
      // 用新 token 修补原始请求
      const newConfig = {
        ...originalRequest,
        headers: {
          ...originalRequest.headers,
          Authorization: `Bearer ${token}`,
        },
      };
      resolve(newConfig); // ← resolve 完整的请求配置
    }
  });
  this.failedQueue = [];
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