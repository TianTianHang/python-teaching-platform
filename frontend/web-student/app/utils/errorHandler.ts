import { redirect } from 'react-router';
import type { ErrorResult } from '~/types/errors';
import { parseError } from './errorParser';

/**
 * 错误处理选项
 */
export interface ErrorHandlerOptions {
  /** 是否重定向到登录页 */
  redirectToLogin?: boolean;
  /** 是否显示错误通知 */
  showNotification?: boolean;
  /** 自定义错误消息 */
  customMessage?: string;
  /** 错误回调函数 */
  onError?: (result: ErrorResult) => void;
}

/**
 * 处理API错误
 */
export function handleApiError(
  error: unknown,
  options: ErrorHandlerOptions = {}
): never {
  const result = parseError(error);

  // 调用错误回调
  if (options.onError) {
    options.onError(result);
  }

  // 401错误重定向到登录页
  if (options.redirectToLogin !== false && result.status === 401) {
    throw redirect('/auth/login');
  }

  // 抛出响应错误
  throw new Response(
    JSON.stringify({
      message: options.customMessage || result.message,
      code: result.code,
      details: result.details
    }),
    {
      status: result.status || 500,
      statusText: 'Error'
    }
  );
}

/**
 * 创建错误处理包装器
 */
export function withErrorHandling<T extends (...args: any[]) => any>(
  handler: T,
  options: ErrorHandlerOptions = {}
): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await handler(...args);
    } catch (error) {
      handleApiError(error, options);
    }
  }) as T;
}

/**
 * 创建带认证的加载器包装器
 */
export function withAuthLoader<T extends (...args: any[]) => any>(
  loader: T
): T {
  return withErrorHandling(loader, { redirectToLogin: true });
}
