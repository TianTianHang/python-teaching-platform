/**
 * 基础错误接口
 */
export interface BaseError extends Error {
  code?: string;
  timestamp?: number;
}

/**
 * API错误响应数据
 */
export interface ApiErrorData {
  detail?: string;
  [key: string]: unknown;
}

/**
 * API错误响应
 */
export interface ApiErrorResponse {
  status: number;
  statusText?: string;
  data?: ApiErrorData;
  headers?: Record<string, string>;
}

/**
 * API错误类型
 */
export interface ApiError extends BaseError {
  response?: ApiErrorResponse;
  config?: unknown;
  request?: unknown;
}

/**
 * 网络错误类型
 */
export interface NetworkError extends BaseError {
  code: 'NETWORK_ERROR' | 'ECONNABORTED' | 'ETIMEDOUT';
  request?: unknown;
}

/**
 * 超时错误类型
 */
export interface TimeoutError extends BaseError {
  code: 'ECONNABORTED';
  timeout?: number;
}

/**
 * 验证错误类型
 */
export interface ValidationError extends BaseError {
  fields?: Record<string, string[]>;
}

/**
 * 业务逻辑错误类型
 */
export interface BusinessError extends BaseError {
  businessCode?: string;
  businessMessage?: string;
}

/**
 * 联合错误类型
 */
export type AppError =
  | ApiError
  | NetworkError
  | TimeoutError
  | ValidationError
  | BusinessError;

/**
 * 错误处理结果
 */
export interface ErrorResult {
  type: 'api' | 'network' | 'timeout' | 'validation' | 'business' | 'unknown';
  status?: number;
  code?: string;
  message: string;
  details?: unknown;
  originalError?: unknown;
}
