import type { ApiErrorData, ErrorResult } from '~/types/errors';
import { isApiError, isNetworkError, isTimeoutError } from './typeGuards';

/**
 * 解析DRF错误响应
 * DRF 400错误通常返回: { "field_name": ["error message"] }
 * DRF 401/403/404错误通常返回: { "detail": "error message" }
 */
export function parseDRError(data: unknown): string {
  if (!data) {
    return '请求失败，但未收到错误详情';
  }

  // 1. { "detail": "..." }
  if (typeof data === 'object' && data !== null && 'detail' in data) {
    const detail = (data as ApiErrorData).detail;
    if (typeof detail === 'string') {
      return detail;
    }
  }

  // 2. { "field_name": ["..."] } 或 { "non_field_errors": ["..."] }
  if (typeof data === 'object' && data !== null) {
    const errorMessages: string[] = [];
    for (const key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        const value = (data as Record<string, unknown>)[key];
        const errorList = Array.isArray(value) ? value : [value];
        errorMessages.push(`[${key}]: ${errorList.join(', ')}`);
      }
    }
    if (errorMessages.length > 0) {
      return errorMessages.join('; ');
    }
  }

  // 3. 兜底，如果是字符串或数组
  if (typeof data === 'string') {
    return data;
  }
  if (Array.isArray(data)) {
    return data.join('; ');
  }

  return '解析错误响应失败';
}

/**
 * 解析错误为统一结果
 */
export function parseError(error: unknown): ErrorResult {
  if (isApiError(error)) {
    const status = error.response?.status || 500;
    const message = parseDRError(error.response?.data);

    return {
      type: 'api',
      status,
      message,
      details: error.response?.data,
      originalError: error
    };
  }

  if (isTimeoutError(error)) {
    return {
      type: 'timeout',
      code: error.code,
      message: '请求超时，请稍后重试',
      originalError: error
    };
  }

  if (isNetworkError(error)) {
    return {
      type: 'network',
      code: error.code,
      message: '网络连接失败，请检查网络后重试',
      originalError: error
    };
  }

  if (error instanceof Error) {
    return {
      type: 'unknown',
      message: error.message || '未知错误',
      originalError: error
    };
  }

  return {
    type: 'unknown',
    message: '发生未知错误',
    originalError: error
  };
}
