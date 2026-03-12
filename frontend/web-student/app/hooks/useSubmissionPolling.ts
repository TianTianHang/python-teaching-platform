/**
 * useSubmissionPolling - 提交状态轮询 Hook
 *
 * 功能：
 * - 自动轮询提交状态
 * - 更新队列状态信息
 * - 提供加载状态和错误处理
 * - 支持手动取消轮询
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import type { Submission, JudgingQueueStats } from '~/types/submission';
import { pollSubmissionStatus } from '~/utils/http/submission';

interface UseSubmissionPollingOptions {
  /** 提交ID */
  submissionId: number | null;
  /** 是否启用轮询 */
  enabled?: boolean;
  /** 轮询间隔（毫秒），默认 2000ms */
  interval?: number;
  /** 最大轮询次数，默认 60 次 */
  maxAttempts?: number;
  /** 轮询超时时间（毫秒），默认 120000ms (2分钟) */
  timeout?: number;
  /** 轮询完成回调 */
  onComplete?: (submission: Submission) => void;
  /** 轮询失败回调 */
  onError?: (error: string) => void;
}

interface PollingState {
  /** 是否正在轮询 */
  isPolling: boolean;
  /** 提交信息 */
  submission: Submission | null;
  /** 队列状态 */
  queueStats: JudgingQueueStats | null;
  /** 错误信息 */
  error: string | null;
  /** 轮询次数 */
  attempts: number;
  /** 已用时间（毫秒） */
  elapsedTime: number;
}

/**
 * Hook 返回值
 */
interface UseSubmissionPollingReturn extends PollingState {
  /** 取消轮询 */
  cancel: () => void;
  /** 手动触发轮询 */
  refetch: () => Promise<void>;
}

/**
 * useSubmissionPolling Hook
 */
export function useSubmissionPolling({
  submissionId,
  enabled = true,
  interval = 2000,
  maxAttempts = 60,
  timeout = 120000,
  onComplete,
  onError,
}: UseSubmissionPollingOptions): UseSubmissionPollingReturn {
  const [state, setState] = useState<PollingState>({
    isPolling: false,
    submission: null,
    queueStats: null,
    error: null,
    attempts: 0,
    elapsedTime: 0,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const pollingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const startTimeRef = useRef<number | null>(null);

  /**
   * 取消轮询
   */
  const cancel = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current);
      pollingTimerRef.current = null;
    }
    startTimeRef.current = null;
    setState((prev) => ({
      ...prev,
      isPolling: false,
    }));
  }, []);

  /**
   * 手动触发轮询
   */
  const refetch = useCallback(async () => {
    if (!submissionId) {
      return;
    }

    try {
      const result = await pollSubmissionStatus(submissionId, {
        maxAttempts: 1,
        interval,
        timeout,
        onStatusUpdate: (submission) => {
          setState((prev) => ({
            ...prev,
            submission,
          }));
        },
        onQueueUpdate: (queueStats) => {
          setState((prev) => ({
            ...prev,
            queueStats,
          }));
        },
      });

      if (result.success && result.submission) {
        setState((prev) => ({
          ...prev,
          submission: result.submission || null,
          error: null,
        }));
      } else if (result.error) {
        setState((prev) => ({
          ...prev,
          error: result.error || null,
        }));
      }
    } catch (error: any) {
      setState((prev) => ({
        ...prev,
        error: error.message || '轮询失败',
      }));
    }
  }, [submissionId, interval, timeout]);

  /**
   * 启动轮询
   */
  useEffect(() => {
    if (!submissionId || !enabled) {
      return;
    }

    // 重置状态
    cancel();
    startTimeRef.current = Date.now();

    setState({
      isPolling: true,
      submission: null,
      queueStats: null,
      error: null,
      attempts: 0,
      elapsedTime: 0,
    });

    // 创建 AbortController
    abortControllerRef.current = new AbortController();

    // 更新已用时间的定时器
    pollingTimerRef.current = setInterval(() => {
      if (startTimeRef.current) {
        setState((prev) => ({
          ...prev,
          elapsedTime: Date.now() - startTimeRef.current!,
        }));
      }
    }, 100);

    // 启动轮询
    pollSubmissionStatus(submissionId, {
      maxAttempts,
      interval,
      timeout,
      onPollStart: () => {
        setState((prev) => ({
          ...prev,
          isPolling: true,
        }));
      },
      onPollEnd: () => {
        setState((prev) => ({
          ...prev,
          isPolling: false,
        }));
        if (pollingTimerRef.current) {
          clearInterval(pollingTimerRef.current);
          pollingTimerRef.current = null;
        }
      },
      onStatusUpdate: (submission) => {
        setState((prev) => ({
          ...prev,
          submission,
          attempts: prev.attempts + 1,
        }));
      },
      onQueueUpdate: (queueStats) => {
        setState((prev) => ({
          ...prev,
          queueStats,
        }));
      },
    })
      .then((result) => {
        if (result.success && result.submission) {
          setState((prev) => ({
            ...prev,
            submission: result.submission || null,
            error: null,
          }));
          onComplete?.(result.submission);
        } else if (result.error) {
          setState((prev) => ({
            ...prev,
            error: result.error || null,
          }));
          onError?.(result.error);
        }
      })
      .catch((error: any) => {
        const errorMessage = error.message || '轮询失败';
        setState((prev) => ({
          ...prev,
          error: errorMessage,
          isPolling: false,
        }));
        onError?.(errorMessage);
      })
      .finally(() => {
        if (pollingTimerRef.current) {
          clearInterval(pollingTimerRef.current);
          pollingTimerRef.current = null;
        }
        startTimeRef.current = null;
      });

    // 清理函数
    return () => {
      cancel();
      if (pollingTimerRef.current) {
        clearInterval(pollingTimerRef.current);
      }
    };
  }, [submissionId, enabled, maxAttempts, interval, timeout, onComplete, onError, cancel]);

  return {
    ...state,
    cancel,
    refetch,
  };
}
