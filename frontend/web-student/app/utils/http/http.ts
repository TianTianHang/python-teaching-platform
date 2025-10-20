// src/utils/http/http.ts
import axios from 'axios';
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import type { CustomRequestConfig, IHttp, InterceptorHooks } from './types';
import { handleHttpError } from './error';


export class Http implements IHttp {
  private instance: AxiosInstance;

  constructor(config: CustomRequestConfig, hooks?: InterceptorHooks) {
    // 1. 创建 Axios 实例
    this.instance = axios.create(config);

    // 2. 设置拦截器
    this.setupInterceptors(hooks);
  }

  // --------------------------------------------------
  // 拦截器设置
  // --------------------------------------------------
  private setupInterceptors(hooks?: InterceptorHooks) {
    // ----------------- 请求拦截器 (不变) -----------------
    this.instance.interceptors.request.use(
      (config) => {
        // 1. 优先执行传入的钩子
        if (hooks?.requestInterceptor) {
          return config = hooks.requestInterceptor(config);
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

        // 3. HTTP 状态码 2xx (成功)
        // DRF/Restful 风格, 2xx 状态码, response.data 就是业务所需的数据
        // 我们直接返回 data
        return response.data;
      },
      (error: AxiosError) => {
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