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
  task_id?: string;            // Celery 异步任务ID
  estimated_wait_seconds?: number;  // 预估等待时间（秒）
}

// 异步提交响应类型（202 Accepted）
export interface AsyncSubmissionResponse {
  id:number;
  submission_id: number;        // 提交ID（后端返回的字段名）
  task_id: string | null;       // Celery 任务ID（事务提交后生成，初始为 null）
  estimated_wait_seconds: number;  // 预估等待时间（秒）
  status: 'pending' | 'judging';
  message: string;              // 提示信息
  queue_position?: number | string;  // 队列位置
  system_status?: 'available' | 'busy' | 'full';  // 系统状态
  warning?: string;             // 警告信息
}

// 队列状态类型
export type QueueStatsStatus =
  | 'pending'
  | 'started'
  | 'success'
  | 'failed'
  | 'timeout'
  | 'cancelled';

export interface JudgingQueueStats {
  id: number;
  status: QueueStatsStatus;
  queue_position?: number;     // 队列中的位置
  estimated_start_time?: string;  // 预估开始时间
  started_at?: string;         // 实际开始时间
  completed_at?: string;       // 完成时间
  queue_wait_seconds?: number; // 实际等待时间（秒）
  execution_seconds?: number;  // 执行时长（秒）
  worker_name?: string;        // Worker 名称
  retry_count: number;         // 重试次数
  error_message?: string;      // 错误信息
  created_at: string;
  updated_at: string;
  submission: number;          // 关联的 Submission ID
}

// 队列容量状态响应类型
export interface QueueStatusRes {
  system_status: 'available' | 'busy' | 'full';  // 队列状态（后端字段名）
  pending_count: number;       // 等待中的任务数
  running_count: number;       // 正在执行的任务数
  total_capacity: number;      // 总容量
  available_slots: number;     // 可用槽位
  status_message?: string;     // 状态消息
  warning_threshold?: number;  // 警告阈值
  max_queue_size?: number;     // 最大队列大小
}

// 任务状态响应类型
export interface TaskStatusRes {
  submission_id: number;
  task_id: string;
  submission_status: SubmissionStatus;
  queue_status: QueueStatsStatus;
  queued_at: string;
  started_at: string | null;
  completed_at: string | null;
  queue_wait_seconds: number | null;
  execution_seconds: number | null;
  total_seconds: number | null;
  error_message: string | null;
}