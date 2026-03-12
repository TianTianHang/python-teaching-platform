/**
 * SubmissionWithEnhancedErrorHandling - 帢增强错误处理的代码提交组件
 *
 * 集成了：
 * - 错误重试机制
 * - 自动重试策略
 * - 友好的错误提示
 * - 网络错误恢复
 */

import { useState } from 'react';
import { Box, Stack, Typography } from '@mui/material';
import { submitAndWait } from '~/utils/http/submission';
import { useRetryableError } from '~/hooks/useRetryableError';
import { RetryableError } from '~/components/Submission/RetryableError';
import { QueueStatusCard } from '~/components/Submission/QueueStatusCard';
import type { SubmissionReq } from '~/types/submission';

interface SubmissionWithEnhancedErrorHandlingProps {
  /** 提交数据 */
  submissionData: SubmissionReq;
  /** 提交成功回调 */
  onSuccess?: (submission: any) => void;
  /** 提交失败回调 */
  onFailure?: (error: string) => void;
}

/**
 * 自动重试策略配置 */
const AUTO_RETRY_CONFIG = {
  // 网络错误重试次数
  networkRetryCount: 3,
  // 服务器错误重试次数
  serverErrorRetryCount: 2,
  // 限流错误重试次数
  rateLimitRetryCount: 3,
  // 重试间隔（毫秒）
  retryInterval: 2000,
  // 限流等待时间（毫秒）
  rateLimitWaitTime: 5000,
} as const;

/**
 * SubmissionWithEnhancedErrorHandling 主组件
 */
export function SubmissionWithEnhancedErrorHandling({
  submissionData,
  onSuccess,
  onFailure
}: SubmissionWithEnhancedErrorHandlingProps) {
  // 提交状态
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionId, setSubmissionId] = useState<number | null>(null);

  // 错误重试状态
  const { state: errorState, manualRetry, autoRetry, reset } = useRetryableError();

  /**
   * 获取重试配置
   */
  const getRetryConfig = (status?: number | string) => {
    const statusCode = typeof status === 'number' ? status : parseInt(String(status) || '0');

    if (statusCode === 429) {
      // 限流错误
      return {
        maxRetries: AUTO_RETRY_CONFIG.rateLimitRetryCount,
        interval: AUTO_RETRY_CONFIG.rateLimitWaitTime,
      };
    } else if (statusCode >= 500) {
      // 服务器错误
      return {
        maxRetries: AUTO_RETRY_CONFIG.serverErrorRetryCount,
        interval: AUTO_RETRY_CONFIG.retryInterval,
      };
    } else if (!status) {
      // 网络错误
      return {
        maxRetries: AUTO_RETRY_CONFIG.networkRetryCount,
        interval: AUTO_RETRY_CONFIG.retryInterval,
      };
    } else {
      // 其他错误
      return {
        maxRetries: 0, // 不可重试
        interval: 0,
      };
    }
  };

  /**
   * 处理代码提交
   */
  const handleSubmit = async (isAutoRetry: boolean = false) => {
    if (isSubmitting) return;

    setIsSubmitting(true);

    try {
      const result = await submitAndWait(submissionData);

      if (result.success && result.submission) {
        // 同步提交完成
        setSubmissionId((result.submission as any).id);
        onSuccess?.(result.submission);
        // 重置错误状态
        reset();
      } else if (result.success && (result.submission as any).task_id) {
        // 异步提交，开始轮询
        setSubmissionId((result.submission as any).id);
        setIsSubmitting(false);
      } else {
        // 提交失败
        const errorMessage = result.error || '提交失败';
        const errorStatus = typeof result.error === 'object' ?
          (result.error as any).status : undefined;

        // 设置错误状态
        if (!isAutoRetry) {
          // 首次提交失败，显示重试选项
          if (getRetryConfig(errorStatus).maxRetries > 0) {
            manualRetry(() => handleSubmit());
          }
        }

        onFailure?.(errorMessage);
        setIsSubmitting(false);
      }
    } catch (error: any) {
      const errorMessage = error.message || '提交失败';
      const errorStatus = error.response?.status;

      // 设置错误状态
      if (!isAutoRetry) {
        // 首次提交失败，显示重试选项
        if (getRetryConfig(errorStatus || undefined).maxRetries > 0) {
          manualRetry(() => handleSubmit());
        }
      }

      onFailure?.(errorMessage);
      setIsSubmitting(false);
    }
  };

  /**
   * 处理自动重试
   */
  const handleAutoRetry = async () => {
    if (!errorState.error) return;

    const config = getRetryConfig(errorState.status);
    if (config.maxRetries > 0) {
      autoRetry(() => handleSubmit(true), {
        maxRetries: config.maxRetries,
        interval: config.interval,
      });
    }
  };

  
  return (
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      {/* 提交按钮 */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
        {isSubmitting ? (
          <div>提交中...</div>
        ) : (
          <div onClick={() => handleSubmit()}>
            {submissionId ? '重新提交' : '提交代码'}
          </div>
        )}
      </Box>

      {/* 错误重试组件 */}
      {errorState.error && (
        <RetryableError
          error={errorState.error}
          status={errorState.status || undefined}
          onRetry={handleAutoRetry}
          autoRetryCount={getRetryConfig(errorState.status || undefined).maxRetries}
          retryInterval={getRetryConfig(errorState.status || undefined).interval}
          showAutoRetry={true}
          manualRetryDisabled={isSubmitting}
        />
      )}

      {/* 提交状态信息 */}
      {submissionId && (
        <Stack spacing={2}>
          <Typography variant="subtitle2" color="text.secondary" textAlign="center">
            提交 ID: {submissionId}
          </Typography>

          {/* 队列状态卡片 */}
          <QueueStatusCard queueStats={{
            id: 1,
            status: 'pending',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            retry_count: 0,
            submission: submissionId
          }} />
        </Stack>
      )}
    </Box>
  );
}

// 导出配置供自定义使用
export { AUTO_RETRY_CONFIG };