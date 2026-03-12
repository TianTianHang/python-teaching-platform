/**
 * SubmissionWithPolling - 带轮询功能的代码提交组件
 *
 * 这个组件整合了代码提交、状态轮询和UI显示
 *
 * 功能：
 * - 提交代码到评测系统
 * - 自动轮询评测状态
 * - 显示提交信息
 * - 显示队列状态和进度
 * - 错误处理和重试机制
 */

import React, { useState } from 'react';
import { Paper, Stack, Box, CircularProgress, Typography } from '@mui/material';
import { spacing, borderRadius, transitions } from '~/design-system/tokens';
import { submitAndWait } from '~/utils/http/submission';
import { useSubmissionPolling } from '~/hooks/useSubmissionPolling';
import { QueueStatusCard } from '~/components/Submission/QueueStatusCard';
import type { SubmissionReq } from '~/types/submission';

interface SubmissionWithPollingProps {
  /** 提交数据 */
  submissionData: SubmissionReq;
  /** 提交成功回调 */
  onSuccess?: (submission: any) => void;
  /** 提交失败回调 */
  onFailure?: (error: string) => void;
}

/**
 * SubmitButton - 提交按钮组件
 */
interface SubmitButtonProps {
  /** 是否正在提交 */
  isSubmitting: boolean;
  /** 是否正在轮询 */
  isPolling: boolean;
  /** 点击回调 */
  onClick: () => void;
  /** 防止重复提交的 cooldown */
  cooldown?: number;
}

function SubmitButton({ isSubmitting, isPolling, onClick, cooldown }: SubmitButtonProps) {
  return (
    <Box sx={{ display: 'flex', justifyContent: 'center' }}>
      {isSubmitting || isPolling ? (
        <CircularProgress
          size={48}
          thickness={2}
          sx={{
            color: 'primary.main',
          }}
        />
      ) : (
        <Paper
          component="button"
          onClick={onClick}
          disabled={!!cooldown}
          sx={{
            px: spacing.lg,
            py: spacing.md,
            borderRadius: borderRadius.sm,
            bgcolor: 'primary.main',
            color: 'primary.contrastText',
            fontSize: '1rem',
            fontWeight: 'bold',
            textTransform: 'none',
            cursor: cooldown ? 'not-allowed' : 'pointer',
            boxShadow: 2,
            transition: transitions.interactive,
            '&:hover': {
              bgcolor: 'primary.dark',
              boxShadow: 3,
              transform: 'translateY(-1px)',
            },
            '&:active': {
              transform: 'translateY(0)',
            },
          }}
        >
          {cooldown ? `${cooldown}秒后可提交` : '提交代码'}
        </Paper>
      )}
    </Box>
  );
}

/**
 * SubmissionWithPolling 主组件
 */
export function SubmissionWithPolling({
  submissionData,
  onSuccess,
  onFailure
}: SubmissionWithPollingProps) {
  // 提交状态
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionId, setSubmissionId] = useState<number | null>(null);
  const [cooldown, setCooldown] = useState(0);

  // 轮询状态
  const {
    isPolling,
    submission,
    queueStats,
    error,
    cancel,
  } = useSubmissionPolling({
    submissionId,
    enabled: !!submissionId,
    onComplete: (submission) => {
      onSuccess?.(submission);
    },
    onError: (error) => {
      onFailure?.(error);
    },
  });

  /**
   * 处理代码提交
   */
  const handleSubmit = async () => {
    if (isSubmitting) return;

    setIsSubmitting(true);
    setCooldown(0);

    try {
      const result = await submitAndWait(submissionData);

      if (result.success && result.submission) {
        // 同步提交完成
        setSubmissionId((result.submission as any).id);
        onSuccess?.(result.submission);
      } else if (result.success && (result.submission as any).task_id) {
        // 异步提交，开始轮询
        setSubmissionId((result.submission as any).id);
        setIsSubmitting(false);
      } else {
        // 提交失败
        const errorMessage = result.error || '提交失败';
        onFailure?.(errorMessage);
        setIsSubmitting(false);
      }
    } catch (error: any) {
      const errorMessage = error.message || '提交失败';
      onFailure?.(errorMessage);
      setIsSubmitting(false);
    } finally {
      // 设置防重复提交的 cooldown
      for (let i = 5; i > 0; i--) {
        setCooldown(i);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      setIsSubmitting(false);
    }
  };

  /**
   * 取消轮询
   */
  const handleCancel = () => {
    cancel();
    setSubmissionId(null);
  };

  return (
    <Stack spacing={spacing.lg}>
      {/* 提交按钮 */}
      <SubmitButton
        isSubmitting={isSubmitting}
        isPolling={isPolling}
        onClick={handleSubmit}
        cooldown={isSubmitting ? 0 : cooldown}
      />

      {/* 提交状态信息 */}
      {submissionId && (
        <Box>
          <Typography
            variant="subtitle2"
            color="text.secondary"
            textAlign="center"
          >
            提交 ID: {submissionId}
          </Typography>

          {/* 队列状态卡片 */}
          {queueStats ? (
            <QueueStatusCard queueStats={queueStats} />
          ) : isPolling && !submission ? (
            // 显示轮询中的状态
            <Box
              sx={{
                p: spacing.lg,
                border: '1px solid',
                borderColor: 'info.main',
                borderRadius: 2,
                bgcolor: 'info.50',
                textAlign: 'center',
              }}
            >
              <Stack alignItems="center" spacing={spacing.sm}>
                <CircularProgress size={40} thickness={2} />
                <Typography variant="body1" color="text.primary">
                  正在查询评测状态...
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  首次查询需要几秒钟，请稍候
                </Typography>
              </Stack>
            </Box>
          ) : null}

          {/* 提交结果显示 */}
          {submission && (
            <Paper
              elevation={0}
              sx={{
                p: spacing.lg,
                border: '1px solid',
                borderColor: 'success.main',
                borderRadius: 2,
                bgcolor: 'success.50',
              }}
            >
              <Stack spacing={spacing.md}>
                <Typography
                  variant="h6"
                  color="success.dark"
                  textAlign="center"
                >
                  评测完成！
                </Typography>

                <Stack
                  sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: spacing.sm }}
                >
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      状态:
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="medium"
                      color="text.primary"
                    >
                      {submission.status}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      用时:
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="medium"
                      color="text.primary"
                    >
                      {submission.execution_time}ms
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      内存:
                    </Typography>
                    <Typography
                      variant="body2"
                      fontWeight="medium"
                      color="text.primary"
                    >
                      {submission.memory_used}MB
                    </Typography>
                  </Box>
                </Stack>

                {submission.error && (
                  <Box
                    sx={{
                      p: spacing.md,
                      bgcolor: 'error.50',
                      border: '1px solid',
                      borderColor: 'error.main',
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="subtitle2" color="error.dark" gutterBottom>
                      错误信息:
                    </Typography>
                    <Typography
                      variant="body2"
                      color="error.dark"
                      sx={{ wordBreak: 'break-word' }}
                    >
                      {submission.error}
                    </Typography>
                  </Box>
                )}
              </Stack>
            </Paper>
          )}

          {/* 错误显示 */}
          {error && (
            <Box
              sx={{
                p: spacing.lg,
                border: '1px solid',
                borderColor: 'error.main',
                borderRadius: 2,
                bgcolor: 'error.50',
              }}
            >
              <Typography
                variant="h6"
                color="error.dark"
                gutterBottom
              >
                评测失败
              </Typography>
              <Typography
                variant="body2"
                color="error.dark"
                textAlign="center"
              >
                {error}
              </Typography>
            </Box>
          )}

          {/* 取消按钮 */}
          {isPolling && (
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <Paper
                component="button"
                onClick={handleCancel}
                sx={{
                  px: spacing.lg,
                  py: spacing.md,
                  borderRadius: borderRadius.sm,
                  bgcolor: 'grey.200',
                  color: 'grey.800',
                  fontSize: '0.875rem',
                  fontWeight: 'medium',
                  textTransform: 'none',
                  cursor: 'pointer',
                  transition: transitions.interactive,
                  '&:hover': {
                    bgcolor: 'grey.300',
                  },
                }}
              >
                取消轮询
              </Paper>
            </Box>
          )}
        </Box>
      )}
    </Stack>
  );
}