/**
 * 提交相关的模拟数据
 */

import type {
  Submission,
  AsyncSubmissionResponse,
  JudgingQueueStats,
  QueueStatsStatus,
} from '~/types/submission';

// 模拟提交数据
export function createMockSubmission(partial: Partial<Submission> = {}): Submission {
  return {
    id: 1,
    username: 'testuser',
    problem_title: '两数之和',
    code: 'print("Hello World")',
    language: 'python',
    status: 'accepted',
    execution_time: 100,
    memory_used: 64,
    output: 'Hello World',
    error: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    ...partial,
  };
}

// 模拟异步提交响应
export function createMockAsyncResponse(
  submissionId: number = 1,
  partial: Partial<AsyncSubmissionResponse> = {}
): AsyncSubmissionResponse {
  return {
    id: submissionId,
    task_id: 'task-12345',
    estimated_wait_seconds: 60,
    status: 'pending',
    message: '提交成功，正在排队等待评测',
    ...partial,
  };
}

// 模拟队列状态
export function createMockQueueStats(
  submissionId: number = 1,
  partial: Partial<JudgingQueueStats> = {}
): JudgingQueueStats {
  return {
    id: 1,
    status: 'pending' as QueueStatsStatus,
    queue_position: 5,
    estimated_start_time: '2024-01-01T00:00:30Z',
    started_at: '2024-01-01T00:00:30Z',
    completed_at: '2024-01-01T00:01:30Z',
    queue_wait_seconds: 30,
    execution_seconds: 60,
    worker_name: 'worker-001',
    retry_count: 0,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:01:30Z',
    submission: submissionId,
    ...partial,
  };
}

// 测试用例数据集
export const testSubmissions = {
  accepted: createMockSubmission({
    status: 'accepted',
    execution_time: 100,
    memory_used: 64,
  }),
  wrongAnswer: createMockSubmission({
    status: 'wrong_answer',
    output: 'Test failed',
    error: 'Wrong answer',
  }),
  timeLimitExceeded: createMockSubmission({
    status: 'time_limit_exceeded',
    error: 'Time limit exceeded',
  }),
  compilationError: createMockSubmission({
    status: 'compilation_error',
    error: 'SyntaxError: invalid syntax',
  }),
  runtimeError: createMockSubmission({
    status: 'runtime_error',
    error: 'NameError: name \'x\' is not defined',
  }),
};

export const testQueueStats = {
  pending: createMockQueueStats(1, {
    status: 'pending',
    queue_position: 10,
  }),
  started: createMockQueueStats(1, {
    status: 'started',
    queue_position: 1,
    started_at: new Date().toISOString(),
  }),
  success: createMockQueueStats(1, {
    status: 'success',
    queue_wait_seconds: 120,
    execution_seconds: 80,
  }),
  failed: createMockQueueStats(1, {
    status: 'failed',
    error_message: 'Worker process crashed',
  }),
  timeout: createMockQueueStats(1, {
    status: 'timeout',
    error_message: 'Execution timed out',
  }),
};