import { useState, useEffect } from "react";
import { useFetcher } from "react-router";
import type { SubmissionFreelyRes, SubmissionReq, SubmissionRes, UnifiedOutput } from "~/types/submission";

const useSubmission = () => {
  const [output, setOutput] = useState<UnifiedOutput | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const fetcher = useFetcher();

  // 监听 fetcher 状态变化
  useEffect(() => {
    if (fetcher.state === "idle" && fetcher.data) {
      // 请求已完成，处理数据
      setIsLoading(false);
      setError(null);

      try {
        const result = fetcher.data as SubmissionFreelyRes | SubmissionRes;

        let unified: UnifiedOutput;
        // 假设你通过某种方式知道是哪种类型，比如看是否有 problem_id
        // 但注意：fetcher.data 里可能没有 problem_id，所以建议后端返回一个字段标识类型
        // 或者你在 submit 时记录一个临时状态

        // 更安全的做法：让后端统一返回结构，或在提交时保存上下文
        // 这里暂时沿用你的逻辑，但需注意风险
        if ("status" in result && "execution_time" in result && "output" in result) {
          // 判断为 SubmissionRes
          const data = result as SubmissionRes;
          unified = {
            status: data.status,
            executionTime: data.execution_time,
            memoryUsed: data.memory_used,
            stdout: data.output,
            stderr: data.error,
          };
        } else {
          // 否则视为 SubmissionFreelyRes
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
      } catch (err) {
        setError("Failed to parse submission result");
      }
    }
  }, [fetcher.state, fetcher.data]);

  const executeCode = (params: SubmissionReq) => {
    // 开始加载
    setIsLoading(true);
    setOutput(null);
    setError(null);

    // 提交表单（注意：useFetcher.submit 会自动序列化）
    fetcher.submit({...params}, { action: "/submission", method: "post" });
  };

  return {
    isLoading: isLoading || fetcher.state !== "idle", // 更准确的 loading 状态
    error,
    output,
    executeCode,
  };
};

export default useSubmission;