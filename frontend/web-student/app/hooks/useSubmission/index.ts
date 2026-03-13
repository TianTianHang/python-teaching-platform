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
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false); // ✅ 新增：防止重复提交

  // 仅用于标记题目为已解决
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
    setIsSubmitting(false); // ✅ 取消轮询，允许新的提交
  }, []);

  // 自动标记为已解决
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

  // 处理异步提交结果（轮询）
  useEffect(() => {
    if (!submissionId || !isPolling) {
      console.log("⏸️ Polling skipped:", { submissionId, isPolling });
      return;
    }

    console.log("🚀 Starting polling for submission:", submissionId);
    abortControllerRef.current = new AbortController();

    const pollSubmission = async () => {
      try {
        console.log("🔄 Polling submission status...", { submissionId, attempt: 1 });
        const result = await pollSubmissionStatus(submissionId, {
          maxAttempts: 60,
          interval: 2000,
          timeout: 120000,
          onStatusUpdate: (submission) => {
            // 更新中间状态（可选）
            console.log('📊 Status update:', submission.status, submission.id);
          },
        });

        if (result.success && result.submission) {
          const submission = result.submission;
          console.log("✅ Polling completed successfully:", {
            status: submission.status,
            execution_time: submission.execution_time,
            output: submission.output?.substring(0, 100)
          });

          const unified: UnifiedOutput = {
            status: submission.status,
            executionTime: submission.execution_time,
            memoryUsed: submission.memory_used,
            stdout: submission.output,
            stderr: submission.error,
          };

          console.log("🎯 Updating UI with final result");
          setOutput(unified);
          setError(null);
          setIsPolling(false);
          setIsLoading(false); // ✅ 确保关闭 loading 状态
          setSubmissionId(null); // ✅ 清除 submissionId 防止重复轮询
          setIsSubmitting(false); // ✅ 轮询完成，允许新的提交

          // 调用成功回调
          if (callbacksRef.current.onSuccess) {
            console.log("📞 Calling onSuccess callback");
            callbacksRef.current.onSuccess(unified);
          }
        } else if (result.error) {
          console.error("❌ Polling failed:", result.error);
          setError(result.error);
          setIsPolling(false);
          setIsLoading(false); // ✅ 确保关闭 loading 状态
          setSubmissionId(null); // ✅ 清除 submissionId
          setIsSubmitting(false); // ✅ 轮询失败，允许新的提交
          if (callbacksRef.current.onError) {
            callbacksRef.current.onError(result.error);
          }
        }
      } catch (err: any) {
        if (err.name !== 'AbortError') {
          const errorMsg = err.message || '轮询失败';
          console.error("❌ Polling error:", errorMsg);
          setError(errorMsg);
          setIsPolling(false);
          setIsLoading(false); // ✅ 确保关闭 loading 状态
          setIsSubmitting(false); // ✅ 轮询错误，允许新的提交
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
    // ✅ 防止重复提交
    if (isSubmitting || isLoading || isPolling) {
      console.warn("⚠️ Submission already in progress, skipping...");
      return;
    }

    console.log("🚀 Starting code submission...");
    setIsSubmitting(true);
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
      console.log("📦 Received result from submitCode:", result);

      // 判断是否是异步响应
      if ('task_id' in result) {
        // 异步提交，开始轮询
        const asyncResult = result as AsyncSubmissionResponse;
        console.log("🔄 Async submission detected:", {
          submission_id: asyncResult.submission_id,
          task_id: asyncResult.task_id,
          estimated_wait: asyncResult.estimated_wait_seconds
        });
        setSubmissionId(asyncResult.submission_id);
        setIsPolling(true);
        setIsLoading(false); // ✅ 异步提交已发出，不再 loading
        // ❌ 移除：不在这里重置 isSubmitting，等轮询完成后再重置
        // setIsSubmitting(false);
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
        // 需要区分两种类型：Submission（有 problem_id）和 SubmissionFreelyRes（无 problem_id）
        let unified: UnifiedOutput;

        if ("output" in result) {
          // Submission 类型（算法题提交）
          // console.log("✅ Processing as Submission (problem submission)");
          const syncResult = result as Submission;
          unified = {
            status: syncResult.status,
            executionTime: syncResult.execution_time,
            memoryUsed: syncResult.memory_used,
            stdout: syncResult.output,
            stderr: syncResult.error,
          };
        } else {
          // SubmissionFreelyRes 类型（自由运行）
          // console.log("✅ Processing as SubmissionFreelyRes (free run)");
          const freeResult = result as SubmissionFreelyRes;
          unified = {
            status: freeResult.status || "completed",
            executionTime: freeResult.execution_time ?? null,
            memoryUsed: freeResult.memory_used ?? null,
            stdout: freeResult.stdout || null,
            stderr: freeResult.stderr || null,
          };
        }

        // console.log("🎯 Unified output:", unified);
        setOutput(unified);
        setError(null);
        setIsLoading(false);
        setIsSubmitting(false); // ✅ 提交完成，允许新的提交

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
      setIsSubmitting(false); // ✅ 提交失败，允许新的提交

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