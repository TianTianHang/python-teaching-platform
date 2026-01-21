import { useState, useEffect, useRef } from "react";
import { useFetcher } from "react-router";
import type { SubmissionFreelyRes, SubmissionReq, SubmissionRes, UnifiedOutput } from "~/types/submission";

type ExecuteOptions = {
  onSuccess?: (output: UnifiedOutput) => void;
  onError?: (error: string) => void;
  onSaveDraft?: (code: string) => Promise<void>;
};

const useSubmission = () => {
  const [output, setOutput] = useState<UnifiedOutput | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [problemId, setProblemId] = useState<number | null>(null);

  const fetcherSubmission = useFetcher<SubmissionFreelyRes | SubmissionRes>();
  const fretcherMark = useFetcher();

  // 使用 ref 保存最新的回调，避免 useEffect 闭包问题
  const callbacksRef = useRef<ExecuteOptions>({});

  // 自动标记为已解决（保持原有逻辑）
  useEffect(() => {
    if (
      problemId != null &&
      fetcherSubmission.state === "idle" &&
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
  }, [output?.status, problemId, fetcherSubmission.state]);

  // 处理提交结果
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

  const executeCode = async (params: SubmissionReq, options?: ExecuteOptions) => {
    setIsLoading(true);
    setOutput(null);
    setError(null);
    setProblemId(params.problem_id || null);

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

    fetcherSubmission.submit(
      { ...params },
      { action: "/submission", method: "post" }
    );
  };

  return {
    isLoading: isLoading || fetcherSubmission.state !== "idle",
    error,
    output,
    executeCode,
  };
};

export default useSubmission;