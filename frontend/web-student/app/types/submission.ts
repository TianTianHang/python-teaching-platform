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
  status: string;
  executionTime: number | null;
  memoryUsed: number | null;
  stdout: string | null;
  stderr: string | null;
}