/**
 * API 封装用于代码提交，支持同步和异步提交模式
 *
 * 功能：
 * - 提交代码（自动选择同步/异步模式）
 * - 查询提交状态
 * - 查询队列状态
 * - 轮询任务状态
 */

import { clientHttp } from './client';
import type {
  Submission,
  SubmissionReq,
  AsyncSubmissionResponse,
  JudgingQueueStats,
  SubmissionStatus,
  QueueStatusRes,
  TaskStatusRes,
  SubmissionFreelyRes,
} from '~/types/submission';

/**
 * 提交代码到评测系统
 *
 * 后端会根据当前队列情况自动选择同步或异步模式：
 * - 如果队列较短，可能直接返回评测结果（同步）
 * - 如果队列较长，返回 202 Accepted 和 task_id（异步）
 * - 如果没有提供 problem_id，返回自由运行结果（SubmissionFreelyRes）
 *
 * @param data 提交数据
 * @returns 提交结果（可能是同步结果、异步响应或自由运行结果）
 */
export async function submitCode(
  data: SubmissionReq
): Promise<Submission | AsyncSubmissionResponse | SubmissionFreelyRes> {
  try {
    const response = await clientHttp.post<
      Submission | AsyncSubmissionResponse | SubmissionFreelyRes
    >('/submissions/', data);

    // 检查是否是异步响应（包含 task_id）
    if ('task_id' in response) {
      return response as AsyncSubmissionResponse;
    }

    // 同步响应（可能是 Submission 或 SubmissionFreelyRes）
    return response;
  } catch (error: any) {
    // 如果后端返回 202，这是正常的异步响应
    if (error.response?.status === 202) {
      return error.response.data as AsyncSubmissionResponse;
    }
    throw error;
  }
}

/**
 * 获取提交详情
 *
 * @param submissionId 提交ID
 * @returns 提交详情
 */
export async function getSubmission(
  submissionId: number
): Promise<Submission> {
  return clientHttp.get<Submission>(`/submissions/${submissionId}/`);
}

/**
 * 获取队列状态统计信息
 *
 * @param submissionId 提交ID
 * @returns 队列状态信息
 */
export async function getQueueStats(
  submissionId: number
): Promise<JudgingQueueStats> {
  return clientHttp.get<JudgingQueueStats>(
    `/submissions/${submissionId}/queue_stats/`
  );
}

/**
 * 获取队列容量状态
 *
 * @returns 队列容量信息
 */
export async function getQueueCapacity(): Promise<QueueStatusRes> {
  return clientHttp.get<QueueStatusRes>('/submissions/queue_status/');
}

/**
 * 获取任务状态
 *
 * @param submissionId 提交ID
 * @returns 任务状态信息
 */
export async function getTaskStatus(
  submissionId: number
): Promise<TaskStatusRes> {
  return clientHttp.get<TaskStatusRes>(
    `/submissions/${submissionId}/task_status/`
  );
}

/**
 * 轮询配置
 */
export interface PollingOptions {
  /** 最大轮询次数，默认 60 次 */
  maxAttempts?: number;
  /** 轮询间隔（毫秒），默认 2000ms */
  interval?: number;
  /** 轮询超时时间（毫秒），默认 120000ms (2分钟) */
  timeout?: number;
  /** 状态更新回调 */
  onStatusUpdate?: (submission: Submission) => void;
  /** 队列状态更新回调 */
  onQueueUpdate?: (queueStats: JudgingQueueStats) => void;
  /** 轮询开始回调 */
  onPollStart?: () => void;
  /** 轮询结束回调 */
  onPollEnd?: () => void;
}

/**
 * 轮询结果
 */
export interface PollingResult {
  success: boolean;
  submission?: Submission;
  error?: string;
  attempts: number;
  totalTime: number;
}

/**
 * 判断提交状态是否为终态（不会改变）
 */
function isTerminalStatus(status: SubmissionStatus): boolean {
  return [
    'accepted',
    'wrong_answer',
    'time_limit_exceeded',
    'memory_limit_exceeded',
    'runtime_error',
    'compilation_error',
    'internal_error',
  ].includes(status);
}

/**
 * 轮询提交状态直到完成
 *
 * @param submissionId 提交ID
 * @param options 轮询配置
 * @returns 轮询结果
 */
export async function pollSubmissionStatus(
  submissionId: number,
  options: PollingOptions = {}
): Promise<PollingResult> {
  const {
    maxAttempts = 60,
    interval = 2000,
    timeout = 120000,
    onStatusUpdate,
    onQueueUpdate,
    onPollStart,
    onPollEnd,
  } = options;

  console.log("🔄 pollSubmissionStatus started:", {
    submissionId,
    maxAttempts,
    interval,
    timeout
  });

  onPollStart?.();

  const startTime = Date.now();
  let attempts = 0;
  let lastError: string | undefined;

  try {
    while (attempts < maxAttempts) {
      // 检查超时
      if (Date.now() - startTime > timeout) {
        lastError = '轮询超时';
        break;
      }

      attempts++;

      try {
        console.log(`📡 Polling attempt ${attempts}/${maxAttempts} for submission ${submissionId}`);
        // 获取提交状态
        const submission = await getSubmission(submissionId);
        console.log(`📊 Submission status: ${submission.status}`);
        onStatusUpdate?.(submission);

        // 如果是终态，返回结果
        if (isTerminalStatus(submission.status)) {
          onPollEnd?.();
          return {
            success: true,
            submission,
            attempts,
            totalTime: Date.now() - startTime,
          };
        }

        // 尝试获取队列状态（如果存在）
        try {
          const queueStats = await getQueueStats(submissionId);
          onQueueUpdate?.(queueStats);

          // 如果队列状态显示失败或超时，提前终止
          if (queueStats.status === 'failed' || queueStats.status === 'timeout') {
            lastError = queueStats.error_message || '评测失败';
            break;
          }
        } catch {
          // 队列状态可能还不存在，忽略错误
        }

        // 等待下次轮询
        if (attempts < maxAttempts && !isTerminalStatus(submission.status)) {
          await new Promise((resolve) => setTimeout(resolve, interval));
        }
      } catch (error: any) {
        // 网络错误，继续尝试
        console.warn('轮询错误:', error);
        if (attempts >= maxAttempts) {
          lastError = error.message || '网络错误';
          break;
        }
        // 继续下次尝试
        await new Promise((resolve) => setTimeout(resolve, interval));
      }
    }

    onPollEnd?.();
    return {
      success: false,
      error: lastError || '轮询次数已达上限',
      attempts,
      totalTime: Date.now() - startTime,
    };
  } catch (error: any) {
    onPollEnd?.();
    return {
      success: false,
      error: error.message || '未知错误',
      attempts,
      totalTime: Date.now() - startTime,
    };
  }
}

/**
 * 提交并等待结果（自动轮询）
 *
 * 这是一个便捷方法，它会：
 * 1. 提交代码
 * 2. 如果是异步提交，自动轮询直到完成
 * 3. 返回最终结果
 *
 * @param data 提交数据
 * @param options 轮询配置
 * @returns 提交结果
 */
export async function submitAndWait(
  data: SubmissionReq,
  options: PollingOptions = {}
): Promise<PollingResult> {
  try {
    // 提交代码
    const submitResult = await submitCode(data);

    // 如果是异步提交
    if ('task_id' in submitResult) {
      // 轮询状态
      return pollSubmissionStatus(submitResult.id, options);
    }

    // 同步提交，直接返回结果
    return {
      success: isTerminalStatus((submitResult as Submission).status),
      submission: submitResult as Submission,
      attempts: 1,
      totalTime: 0,
    };
  } catch (error: any) {
    return {
      success: false,
      error: error.message || '提交失败',
      attempts: 0,
      totalTime: 0,
    };
  }
}

