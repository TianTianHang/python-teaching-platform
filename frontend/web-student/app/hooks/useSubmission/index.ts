import { useState } from "react";
import type { SubmissionFreelyRes, SubmissionReq, SubmissionRes, UnifiedOutput } from "~/types/submission";
import http from "~/utils/http";



const useSubmission = () => {
  const [output, setOutput] = useState<UnifiedOutput | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const executeCode = async (params: SubmissionReq) => {
    setIsLoading(true);
    setError(null);
    setOutput(null);

    try {
      const result = await http.post<SubmissionFreelyRes | SubmissionRes>(
        "/submissions/",
        params
      );

      let unified: UnifiedOutput;

      if (params.problem_id !== undefined) {
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
    } catch (err: any) {
      setError(
        err?.response?.data?.error ||
          err?.message ||
          "An error occurred while executing code"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return {
    isLoading,
    error,
    output, // 现在是结构化对象
    executeCode,
  };
};

export default useSubmission;