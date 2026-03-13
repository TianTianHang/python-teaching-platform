import { useState, useEffect, useRef, useCallback } from "react";
import { useFetcher } from "react-router";
import type { SubmissionFreelyRes, SubmissionReq, SubmissionRes, UnifiedOutput, Submission, AsyncSubmissionResponse } from "~/types/submission";
import { submitCode, pollSubmissionStatus } from "~/utils/http/submission";

type ExecuteOptions = {
  onSuccess?: (output: UnifiedOutput) => void;
  onError?: (error: string) => void;
  onSaveDraft?: (code: string) => Promise<void>;
  /** 自动重试次数，默认 0 */
  retryCount?: number;
  /** 重试延迟（毫秒），默认 1000ms */
  retryDelay?: number;
};

const useSubmission = () => {
  const [output, setOutput] = useState<UnifiedOutput | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [problemId, setProblemId] = useState<number | null>(null);
  const [submissionId, setSubmissionId] = useState<number | null>(null);
  const [isPolling, setIsPolling] = useState<boolean>(false);

  const fetcherSubmission = useFetcher<SubmissionFreelyRes | SubmissionRes>();
  const fretcherMark = useFetcher();
  const abortControllerRef = useRef<AbortController | null>(null);

  // 使用 ref 保存最新的回调，避免 useEffect 闭包问题
  const callbacksRef = useRef<ExecuteOptions>({});

  // 取消轮询
  const cancelPolling = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setIsPolling(false);
  }, []);

  // 自动标记为已解决（保持原有逻辑）
  useEffect(() => {
    if (
      problemId != null &&
      output?.status === "accepted"
    ) {
      fretcherMark.submit(
        { solved: true },
        {
          action: `/problems/${problemId}/mark_as_solved`,
          method: "post",
        }
      );
    }
  }, [output?.status, problemId]);

  // 处理同步提交结果（useFetcher）
  useEffect(() => {
    if (fetcherSubmission.state === "idle" && fetcherSubmission.data) {
      setIsLoading(false);

      try {
        const result = fetcherSubmission.data;
        let unified: UnifiedOutput;

        if ("status" in result && "execution_time" in result && "output" in result) {
          const data = result as SubmissionRes;
          unified = {
            status: data.status,
            executionTime: data.execution_time,
            memoryUsed: data.memory_used,
            stdout: data.output,
            stderr: data.error,
          };
        } else {
          const data = result as SubmissionFreelyRes;
          unified = {
            status: data.status || "completed",
            executionTime: data.execution_time ?? null,
            memoryUsed: data.memory_used ?? null,
            stdout: data.stdout || null,
            stderr: data.stderr || null,
          };
        }

        setOutput(unified);
        setError(null);
        setIsPolling(false);

        // ✅ 调用成功回调
        if (callbacksRef.current.onSuccess) {
          callbacksRef.current.onSuccess(unified);
        }
      } catch {
        const errorMsg = "Failed to parse submission result";
        setError(errorMsg);
        if (callbacksRef.current.onError) {
          callbacksRef.current.onError(errorMsg);
        }
      }
    }
  }, [fetcherSubmission.state, fetcherSubmission.data]);

  // 处理异步提交结果（轮询）
  useEffect(() => {
    if (!submissionId || !isPolling) {
      return;
    }

    abortControllerRef.current = new AbortController();

    const pollSubmission = async () => {
      try {
        const result = await pollSubmissionStatus(submissionId, {
          maxAttempts: 60,
          interval: 2000,
          timeout: 120000,
          onStatusUpdate: (submission) => {
            // 更新中间状态（可选）
            console.log('Polling update:', submission.status);
          },
        });

        if (result.success && result.submission) {
          const submission = result.submission;
          const unified: UnifiedOutput = {
            status: submission.status,
            executionTime: submission.execution_time,
            memoryUsed: submission.memory_used,
            stdout: submission.output,
            stderr: submission.error,
          };

          setOutput(unified);
          setError(null);
          setIsPolling(false);

          // 调用成功回调
          if (callbacksRef.current.onSuccess) {
            callbacksRef.current.onSuccess(unified);
          }
        } else if (result.error) {
          setError(result.error);
          setIsPolling(false);
          if (callbacksRef.current.onError) {
            callbacksRef.current.onError(result.error);
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          const errorMsg = err.message || '轮询失败';
          setError(errorMsg);
          setIsPolling(false);
          if (callbacksRef.current.onError) {
            callbacksRef.current.onError(errorMsg);
          }
        }
      }
    };

    pollSubmission();

    return () => {
      cancelPolling();
    };
  }, [submissionId, isPolling, cancelPolling]);

  /**
   * 解析错误信息
   */
  const parseError = (err: any): string => {
    // 队列已满错误
    if (err.response?.status === 429) {
      return '评测队列已满，请稍后再试';
    }

    // 网络错误
    if (err.code === 'NETWORK_ERROR' || err.message?.includes('Network Error')) {
      return '网络连接失败，请检查网络后重试';
    }

    // 超时错误
    if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
      return '请求超时，请稍后重试';
    }

    // 服务器错误
    if (err.response?.status >= 500) {
      return `服务器错误 (${err.response.status})，请稍后重试`;
    }

    // 客户端错误
    if (err.response?.status >= 400 && err.response?.status < 500) {
      return err.response?.data?.detail || err.response?.data?.error || '请求失败';
    }

    // 其他错误
    return err.message || '提交失败';
  };

  const executeCode = async (
    params: SubmissionReq,
    options?: ExecuteOptions,
    currentRetry = 0
  ) => {
    setIsLoading(true);
    setIsPolling(false);
    setOutput(null);
    setError(null);
    setProblemId(params.problem_id || null);
    setSubmissionId(null);

    // 保存回调（使用 ref 避免闭包）
    callbacksRef.current = options || {};

    // 如果提供了 problem_id 和 onSaveDraft 回调，先保存草稿
    if (params.problem_id && options?.onSaveDraft && params.code) {
      try {
        await options.onSaveDraft(params.code);
      } catch (error) {
        console.warn('Failed to save draft before submission:', error);
        // 草稿保存失败不影响提交
      }
    }

    try {
      // 使用新的 API 提交代码
      const result = await submitCode(params);

      // 判断是否是异步响应
      if ('task_id' in result) {
        // 异步提交，开始轮询
        const asyncResult = result as AsyncSubmissionResponse;
        setSubmissionId(asyncResult.id);
        setIsPolling(true);
        // 设置一个初始的 loading 状态
        setOutput({
          status: 'pending',
          executionTime: null,
          memoryUsed: null,
          stdout: null,
          stderr: null,
        });
      } else {
        // 同步提交，直接处理结果
        const syncResult = result as Submission;
        const unified: UnifiedOutput = {
          status: syncResult.status,
          executionTime: syncResult.execution_time,
          memoryUsed: syncResult.memory_used,
          stdout: syncResult.output,
          stderr: syncResult.error,
        };

        setOutput(unified);
        setError(null);
        setIsLoading(false);

        if (callbacksRef.current.onSuccess) {
          callbacksRef.current.onSuccess(unified);
        }
      }
    } catch (err: any) {
      const errorMsg = parseError(err);
      const maxRetries = options?.retryCount || 0;
      const retryDelay = options?.retryDelay || 1000;

      // 自动重试（仅针对网络错误和服务器错误）
      const shouldRetry =
        currentRetry < maxRetries &&
        (err.code === 'NETWORK_ERROR' ||
          err.message?.includes('Network Error') ||
          err.response?.status >= 500);

      if (shouldRetry) {
        console.log(
          `提交失败，${retryDelay}ms 后重试 (${currentRetry + 1}/${maxRetries})`
        );
        await new Promise((resolve) => setTimeout(resolve, retryDelay));
        return executeCode(params, options, currentRetry + 1);
      }

      setError(errorMsg);
      setIsLoading(false);
      setIsPolling(false);

      if (callbacksRef.current.onError) {
        callbacksRef.current.onError(errorMsg);
      }
    }
  };

  return {
    isLoading: isLoading || isPolling,
    isPolling,
    error,
    output,
    executeCode,
    cancelPolling,
  };
};

export default useSubmission;