/**
 * useRetryableError - 可重试错误管理 Hook
 *
 * 提供错误重试功能，支持自动重试和手动重试
 * 可以集成到任何需要错误重试的组件中
 */

import { useCallback, useState } from 'react';

interface RetryOptions {
  /** 最大重试次数 */
  maxRetries?: number;
  /** 重试间隔（毫秒） */
  interval?: number;
  /** 重试延迟函数（动态间隔） */
  delayFunction?: (attempt: number) => number;
}

interface RetryableErrorState {
  /** 当前重试次数 */
  retryCount: number;
  /** 是否正在重试中 */
  isRetrying: boolean;
  /** 错误信息 */
  error: string | null;
  /** 错误状态码 */
  status: number | string | null;
  /** 自动重试定时器 ID */
  timerId: NodeJS.Timeout | null;
}

interface UseRetryableErrorReturn {
  /** 重试状态 */
  state: RetryableErrorState;
  /** 重试函数 */
  retry: (callback: () => Promise<any>) => Promise<void>;
  /** 手动重试 */
  manualRetry: (callback: () => Promise<any>) => Promise<void>;
  /** 自动重试 */
  autoRetry: (callback: () => Promise<any>, options?: RetryOptions) => Promise<void>;
  /** 停止重试 */
  stopRetry: () => void;
  /** 重置状态 */
  reset: () => void;
}

/**
 * 计算重试延迟时间（使用指数退避算法）
 */
function calculateRetryDelay(
  attempt: number,
  baseInterval: number,
  maxInterval: number = 30000
): number {
  // 指数退避：baseInterval * 2^(attempt-1)
  let delay = baseInterval * Math.pow(2, attempt - 1);
  // 添加随机抖动（±25%）避免所有客户端同时重试
  const jitter = delay * (0.25 * (Math.random() * 2 - 1));
  delay += jitter;
  // 限制最大延迟时间
  return Math.min(delay, maxInterval);
}

/**
 * useRetryableError Hook
 */
export function useRetryableError(): UseRetryableErrorReturn {
  const [state, setState] = useState<RetryableErrorState>({
    retryCount: 0,
    isRetrying: false,
    error: null,
    status: null,
    timerId: null,
  });

  
  /**
   * 重试函数（基本功能）
   */
  const retry: UseRetryableErrorReturn['retry'] = useCallback(async (callback) => {
    if (state.isRetrying) return;

    setState(prev => ({ ...prev, isRetrying: true }));

    try {
      await callback();
      // 成功则重置状态
      setState(prev => ({
        ...prev,
        isRetrying: false,
        retryCount: 0,
        error: null,
        status: null,
      }));
    } catch (error: any) {
      const errorMessage = error.message || '操作失败';
      const errorStatus = error.response?.status;

      // 更新错误状态
      setState(prev => ({
        ...prev,
        isRetrying: false,
        error: errorMessage,
        status: errorStatus || prev.status,
      }));

      // 重新抛出错误
      throw error;
    }
  }, [state.isRetrying]);

  /**
   * 手动重试
   */
  const manualRetry: UseRetryableErrorReturn['manualRetry'] = useCallback(async (callback) => {
    try {
      await retry(callback);
    } catch (error) {
      // 错误已在 retry 中处理
    }
  }, [retry]);

  /**
   * 自动重试
   */
  const autoRetry: UseRetryableErrorReturn['autoRetry'] = useCallback(async (callback, options = {}) => {
    const {
      maxRetries = 3,
      interval = 2000,
      delayFunction = (attempt) => calculateRetryDelay(attempt, interval)
    } = options;

    // 如果已经达到最大重试次数，停止
    if (state.retryCount >= maxRetries) {
      return;
    }

    // 清除之前的定时器
    if (state.timerId) {
      clearTimeout(state.timerId);
    }

    setState(prev => ({ ...prev, isRetrying: true }));

    try {
      await callback();
      // 成功则重置状态
      setState(prev => ({
        ...prev,
        isRetrying: false,
        retryCount: 0,
        error: null,
        status: null,
        timerId: null,
      }));
    } catch (error: any) {
      const errorMessage = error.message || '操作失败';
      const errorStatus = error.response?.status;

      // 更新重试计数和错误状态
      const newRetryCount = state.retryCount + 1;
      setState(prev => ({
        ...prev,
        isRetrying: false,
        retryCount: newRetryCount,
        error: errorMessage,
        status: errorStatus || prev.status,
      }));

      // 如果还有重试次数，安排下次重试
      if (newRetryCount < maxRetries) {
        const delay = delayFunction(newRetryCount);
        const timerId = setTimeout(() => {
          autoRetry(callback, options);
        }, delay);

        setState(prev => ({
          ...prev,
          timerId,
        }));
      }
    }
  }, [state.retryCount, state.timerId]);

  /**
   * 停止重试
   */
  const stopRetry: UseRetryableErrorReturn['stopRetry'] = useCallback(() => {
    if (state.timerId) {
      clearTimeout(state.timerId);
      setState(prev => ({
        ...prev,
        timerId: null,
        isRetrying: false,
      }));
    }
  }, [state.timerId]);

  /**
   * 重置状态
   */
  const reset: UseRetryableErrorReturn['reset'] = useCallback(() => {
    if (state.timerId) {
      clearTimeout(state.timerId);
    }
    setState({
      retryCount: 0,
      isRetrying: false,
      error: null,
      status: null,
      timerId: null,
    });
  }, [state.timerId]);

  return {
    state,
    retry,
    manualRetry,
    autoRetry,
    stopRetry,
    reset,
  };
}