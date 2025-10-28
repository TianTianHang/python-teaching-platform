import type { AlgorithmProblem } from "./course";
import type { User } from "./user";

export interface SubmissionReq {
    code: string;
    language: string;
    problem_id?: number;
}
export type SubmissionStatus =
  | 'pending'
  | 'judging'
  | 'accepted'
  | 'wrong_answer'
  | 'time_limit_exceeded'
  | 'memory_limit_exceeded'
  | 'runtime_error'
  | 'compilation_error'
  | 'internal_error';
export interface SubmissionRes{
    id: number;
    user: User;
    username: string;
    problem: AlgorithmProblem;
    problem_title: string;
    code: string;
    language: string;
    status: SubmissionStatus;
    execution_time: number;
    memory_used: number;
    output: string | null;
    error: string | null;
    created_at: string;
    updated_at: string;
} 
export interface SubmissionFreelyRes{
    status: SubmissionStatus;
    stdout: string;
    stderr: string;
    execution_time: number;
    memory_used: number;
}
export interface UnifiedOutput {
  status: SubmissionStatus|"completed";
  executionTime: number | null;
  memoryUsed: number | null;
  stdout: string | null;
  stderr: string | null;
}

export interface Submission {
  id: number;    
  username: string;            // 用户名   
  problem_title: string;       // 题目标题
  code: string;                // 提交的代码
  language: string;            // 编程语言，如 "python"
  status: SubmissionStatus
  execution_time: number;      // 执行时间（毫秒或你定义的单位）
  memory_used: number;         // 内存使用（MB 或你定义的单位）
  output: string;              // 测试输出（可能包含多个测试用例结果）
  error: string;               // 错误信息（如编译错误、运行时异常）
  created_at: string;          // ISO 8601 时间字符串
  updated_at: string;          // ISO 8601 时间字符串
}