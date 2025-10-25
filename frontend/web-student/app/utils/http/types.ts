// src/utils/http/types.ts
import type { AxiosRequestConfig, AxiosResponse, InternalAxiosRequestConfig } from 'axios';

/**
 * @description 自定义 AxiosRequestConfig
 * 允许我们添加一些自定义的配置，例如是否跳过全局错误处理
 */
export interface CustomRequestConfig extends AxiosRequestConfig {
  /**
   * @description 是否跳过全局错误处理
   * @default false
   */
  skipErrorHandler?: boolean;
  /**
   * @description 是否跳过通知
   * @default false
   */
  skipNotification?: boolean;
  _retry?:boolean ;
}
// --------------------------------------------------
// ******** 新增类型 ********
/**
 * @description 拦截器内部使用的自定义配置类型
 * 它合并了 InternalAxiosRequestConfig (headers 必选) 
 * 和 CustomRequestConfig (自定义字段)
 */
export type CustomInternalRequestConfig = InternalAxiosRequestConfig & CustomRequestConfig;
// --------------------------------------------------
/**
 * @description 封装的请求方法的接口
 * @template T 成功时响应体 `response.data` 的类型
 */
export interface IHttp {
  request<T = any>(config: CustomRequestConfig): Promise<T>;
  get<T = any>(url: string, params?: object, config?: CustomRequestConfig): Promise<T>;
  post<T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T>;
  put<T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T>;
  delete<T = any>(url: string, params?: object, config?: CustomRequestConfig): Promise<T>;
  patch<T = any>(url: string, data?: object, config?: CustomRequestConfig): Promise<T>;
}

/**
 * @description 拦截器钩子
 */
export interface InterceptorHooks {
  requestInterceptor?: (
    config: CustomInternalRequestConfig
  ) => CustomInternalRequestConfig| Promise<CustomInternalRequestConfig>;
  requestInterceptorCatch?: (error: any) => any;
  responseInterceptor?: (response: AxiosResponse) => AxiosResponse | Promise<AxiosResponse>;
  responseInterceptorCatch?: (error: any) => any;
}