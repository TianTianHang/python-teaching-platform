/**
 * useSubmissionPolling Hook 测试用例
 */

import { act, renderHook, waitFor } from '@testing-library/react';
import { useSubmissionPolling } from './useSubmissionPolling';
import {
  createMockSubmission,
  createMockQueueStats
} from '../../test/mocks/submission';
import type { Submission, JudgingQueueStats } from '~/types/submission';

// Mock API
const mockPollSubmissionStatus = jest.fn();
const mockGetSubmission = jest.fn();
const mockGetQueueStats = jest.fn();

jest.mock('../../utils/http/submission', () => ({
  pollSubmissionStatus: mockPollSubmissionStatus,
}));

describe('useSubmissionPolling Hook', () => {
  const mockSubmission = createMockSubmission();
  const mockQueueStats = createMockQueueStats();

  beforeEach(() => {
    jest.useFakeTimers();
    mockPollSubmissionStatus.mockReset();
    mockGetSubmission.mockReset();
    mockGetQueueStats.mockReset();
  });

  afterEach(() => {
    jest.useRealTimers();
    jest.clearAllMocks();
  });

  describe('当 submissionId 为 null 时', () => {
    it('不应该开始轮询', () => {
      const { result } = renderHook(() =>
        useSubmissionPolling({
          submissionId: null,
        })
      );

      expect(result.current.isPolling).toBe(false);
      expect(result.current.submission).toBe(null);
      expect(result.current.queueStats).toBe(null);
    });
  });

  describe('当启用轮询时', () => {
    it('应该开始轮询并正确获取数据', async () => {
      mockPollSubmissionStatus.mockResolvedValue({
        success: true,
        submission: mockSubmission,
        attempts: 3,
        totalTime: 5000,
      });

      const { result } = renderHook(() =>
        useSubmissionPolling({
          submissionId: mockSubmission.id,
        })
      );

      // 初始状态
      expect(result.current.isPolling).toBe(true);
      expect(result.current.attempts).toBe(0);

      // 快进时间
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(result.current.isPolling).toBe(false);
        expect(result.current.submission).toEqual(mockSubmission);
        expect(result.current.attempts).toBe(3);
        expect(result.current.totalTime).toBe(5000);
      });
    });

    it('应该处理轮询失败的情况', async () => {
      mockPollSubmissionStatus.mockRejectedValue(new Error('网络错误'));

      const { result } = renderHook(() =>
        useSubmissionPolling({
          submissionId: mockSubmission.id,
        })
      );

      act(() => {
        jest.advanceTimersByTime(5000);
      });

      await waitFor(() => {
        expect(result.current.isPolling).toBe(false);
        expect(result.current.error).toBe('网络错误');
        expect(result.current.success).toBe(false);
      });
    });

    it('应该支持回调函数', async () => {
      const mockOnComplete = jest.fn();
      const mockOnError = jest.fn();

      mockPollSubmissionStatus.mockResolvedValue({
        success: false,
        error: '提交失败',
        attempts: 1,
        totalTime: 2000,
      });

      renderHook(() =>
        useSubmissionPolling({
          submissionId: mockSubmission.id,
          onComplete: mockOnComplete,
          onError: mockOnError,
        })
      );

      act(() => {
        jest.advanceTimersByTime(3000);
      });

      await waitFor(() => {
        expect(mockOnError).toHaveBeenCalledWith('提交失败');
      });
    });
  });

  describe('取消轮询', () => {
    it('应该能够取消轮询', async () => {
      let resolvePoll: Function;
      const pollPromise = new Promise((resolve) => {
        resolvePoll = resolve;
      });

      mockPollSubmissionStatus.mockReturnValue(pollPromise);

      const { result } = renderHook(() =>
        useSubmissionPolling({
          submissionId: mockSubmission.id,
        })
      );

      // 取消轮询
      act(() => {
        result.current.cancel();
      });

      // 快进时间
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      // 确保轮询已取消
      expect(result.current.isPolling).toBe(false);

      // 完成 promise
      resolvePoll({
        success: true,
        submission: mockSubmission,
        attempts: 5,
        totalTime: 8000,
      });

      await expect(pollPromise).resolves.toMatchObject({
        success: true,
      });
    });
  });

  describe('手动重试', () => {
    it('应该支持手动重试', async () => {
      mockPollSubmissionStatus
        .mockRejectedValueOnce(new Error('第一次失败'))
        .mockResolvedValueOnce({
          success: true,
          submission: mockSubmission,
          attempts: 1,
          totalTime: 2000,
        });

      const { result } = renderHook(() =>
        useSubmissionPolling({
          submissionId: mockSubmission.id,
        })
      );

      // 第一次失败
      act(() => {
        jest.advanceTimersByTime(2000);
      });

      await waitFor(() => {
        expect(result.current.error).toBe('第一次失败');
      });

      // 手动重试
      act(() => {
        result.current.refetch();
      });

      act(() => {
        jest.advanceTimersByTime(2000);
      });

      await waitFor(() => {
        expect(result.current.submission).toEqual(mockSubmission);
        expect(result.current.error).toBe(null);
      });
    });
  });

  describe('轮询超时', () => {
    it('应该在超时后停止轮询', async () => {
      mockPollSubmissionStatus.mockImplementation(() =>
        new Promise(() => {})
      );

      const { result } = renderHook(() =>
        useSubmissionPolling({
          submissionId: mockSubmission.id,
          timeout: 1000,
        })
      );

      // 快进到超时
      act(() => {
        jest.advanceTimersByTime(1000);
      });

      await waitFor(() => {
        expect(result.current.isPolling).toBe(false);
        expect(result.current.error).toBe('轮询超时');
      });
    });
  });
});