// src/utils/http/error.ts
import type { AxiosError } from 'axios';
import type { CustomRequestConfig } from './types';
import { showNotification } from '~/components/Notification';



/**
 * @description 解析 DRF 的错误响应
 * DRF 400 错误通常返回: { "field_name": ["error message"] }
 * DRF 401/403/404 错误通常返回: { "detail": "error message" }
 * @param {any} data - error.response.data
 * @returns {string} - 解析后的错误信息
 */
const parseDRError = (data: any): string => {
  if (!data) {
    return '请求失败，但未收到错误详情';
  }

  // 1. { "detail": "..." }
  if (typeof data.detail === 'string') {
    return data.detail;
  }

  // 2. { "field_name": ["..."] } 或 { "non_field_errors": ["..."] }
  if (typeof data === 'object' && Object.keys(data).length > 0) {
    let errorMessages: string[] = [];
    for (const key in data) {
      if (Object.prototype.hasOwnProperty.call(data, key)) {
        const errorList = Array.isArray(data[key]) ? data[key] : [data[key]];
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
};


/**
 * @description 处理 HTTP 错误（HTTP 状态码非 2xx）
 */
export const handleHttpError = (error: AxiosError, config: CustomRequestConfig) => {
  if (config.skipErrorHandler) {
    return;
  }

  let title = '请求错误';
  let message = '';
  const responseData = error.response?.data;

  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    message = '请求超时，请检查您的网络';
    title = '网络错误';
  } else if (error.response) {
    // 服务器返回了响应 (4xx, 5xx)
    const status = error.response.status;
    title = `HTTP 错误: ${status}`;

    // 使用 parseDRError 解析 DRF 的错误信息
    const drfMessage = parseDRError(responseData);

    switch (status) {
      case 400: // Bad Request (通常是 DRF 验证错误)
        title = '请求无效 (400)';
        message = drfMessage || '请求参数或格式不正确';
        break;
      case 401: // Unauthorized
        title = '未授权 (401)';
        message = drfMessage || '您没有登录或登录已过期，请重新登录';
        // TODO: 在这里执行跳转到登录页的操作
        // window.location.href = '/login';
        break;
      case 403: // Forbidden
        title = '无权限 (403)';
        message = drfMessage || '您没有权限执行此操作';
        break;
      case 404: // Not Found
        title = '未找到 (404)';
        message = drfMessage || '请求的资源不存在';
        break;
      case 500:
      case 502:
      case 503:
      case 504:
        title = `服务器错误 (${status})`;
        message = drfMessage || `服务器开小差了，请稍后再试 (${status})`;
        break;
      default:
        message = drfMessage || `连接错误 (${status})!`;
    }
  } else if (error.request) {
    // 请求已发出，但未收到响应（例如网络断开）
    title = '网络错误';
    message = '网络连接失败，请检查您的网络设置';
  } else {
    // 设置请求时发生错误
    title = '请求失败';
    message = error.message || '未知错误';
  }
  error.message = message
};