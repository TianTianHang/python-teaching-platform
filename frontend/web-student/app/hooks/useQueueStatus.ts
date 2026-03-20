/**
 * 获取队列容量的 Hook
 *
 * 功能：
 * - 获取队列容量状态
 * - 自动刷新
 * - 错误处理
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { getQueueCapacity } from "~/utils/http/submission";
import type { QueueStatusRes } from "~/types/submission";

export interface UseQueueStatusOptions {
  /** 是否自动刷新，默认 false */
  autoRefresh?: boolean;
  /** 刷新间隔（毫秒），默认 5000ms */
  refreshInterval?: number;
  /** 是否在组件挂载时立即加载，默认 true */
  immediate?: boolean;
}

export interface UseQueueStatusReturn {
  /** 队列状态数据 */
  queueStatus: QueueStatusRes | null;
  /** 是否正在加载 */
  isLoading: boolean;
  /** 错误信息 */
  error: string | null;
  /** 手动刷新 */
  refresh: () => Promise<void>;
  /** 停止自动刷新 */
  stopAutoRefresh: () => void;
  /** 开始自动刷新 */
  startAutoRefresh: () => void;
}

/**
 * 获取队列状态的 Hook
 */
export function useQueueStatus(
  options: UseQueueStatusOptions = {}
): UseQueueStatusReturn {
  const {
    autoRefresh = false,
    refreshInterval = 5000,
    immediate = true,
  } = options;

  const [queueStatus, setQueueStatus] = useState<QueueStatusRes | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isAutoRefreshEnabled, setIsAutoRefreshEnabled] = useState(autoRefresh);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const fetchQueueStatus = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await getQueueCapacity();
      setQueueStatus(data);
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : "获取队列状态失败";
      setError(errorMsg);
      console.error("Failed to fetch queue status:", err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    await fetchQueueStatus();
  }, [fetchQueueStatus]);

  const stopAutoRefresh = useCallback(() => {
    setIsAutoRefreshEnabled(false);
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startAutoRefresh = useCallback(() => {
    setIsAutoRefreshEnabled(true);
  }, []);

  // 初始加载
  useEffect(() => {
    if (immediate) {
      fetchQueueStatus();
    }
  }, [immediate, fetchQueueStatus]);

  // 自动刷新
  useEffect(() => {
    if (isAutoRefreshEnabled && refreshInterval > 0) {
      intervalRef.current = setInterval(fetchQueueStatus, refreshInterval);
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [isAutoRefreshEnabled, refreshInterval, fetchQueueStatus]);

  return {
    queueStatus,
    isLoading,
    error,
    refresh,
    stopAutoRefresh,
    startAutoRefresh,
  };
}

export default useQueueStatus;