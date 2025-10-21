import { useState, useCallback, useEffect, useRef } from "react";
import judge from "~/utils/judge"
import type { SubmissionResponse, SubmissionRequest } from "~/utils/judge/type";
import type { SubmissionStatus } from "./type.";
import { useRequest } from 'ahooks';

export const useSubmission = () => {
  const [token, setToken] = useState<string | null>(null);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // 1. 提交代码的函数（手动触发）
  const submitCode = useCallback(async (request: SubmissionRequest) => {
    try {
      const res = await judge.submission(request);
      setToken(res.token);
      setSubmitError(null);
      return res.token;
    } catch (err: any) {
      const msg = err.message || '提交失败';
      setSubmitError(msg);
      throw err;
    }
  }, []);

  // 2. 轮询获取结果（仅当 token 存在时激活）
  const {
    data: result,
    loading: isPolling,
    error: pollError,
    run: startPolling,
    cancel: stopPolling,
  } = useRequest(
    (pollToken: string) => judge.getResult(pollToken),
    {
      // 初始不执行
      manual: true,
      // 轮询配置
      pollingInterval: 500,
      // 当 status_id >= 4 时停止轮询
      pollingWhenHidden: false,
      onSuccess: (data, params) => {
        if (data.status.id >= 4) {
          stopPolling();
        }
      },
      onError: () => {
        stopPolling();
      },
    }
  );

  // 当 token 变化时自动开始轮询
  // 注意：不能直接在 useEffect 中调用 run，因为 useRequest 的 run 是稳定的
  // 所以我们通过一个副作用来触发
  const prevTokenRef = useRef<string | null>(null);
  useEffect(() => {
    if (token && token !== prevTokenRef.current) {
      prevTokenRef.current = token;
      startPolling(token);
    }
  }, [token, startPolling]);

  // 综合状态判断
  const isLoading = isPolling || !!submitError; // 提交中由 submitCode 控制，这里只反映轮询
  const error = submitError || (pollError?.message ?? null);

  return {
    // 状态
    isSubmitting: false, // ahooks 不直接暴露“提交中”，可通过 submitCode 的 async/await 控制按钮
    isPolling,
    isLoading,
    error,

    // 数据
    result: result as SubmissionResponse | null,
    token,

    // 操作
    submitCode,
    stopPolling,
  };
};