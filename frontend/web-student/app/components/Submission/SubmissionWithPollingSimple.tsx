/**
 * SubmissionWithPollingSimple - 简化的带轮询功能代码提交组件
 *
 * 这个组件提供了基本的代码提交和轮询功能
 */

import { useState } from 'react';
import { Paper, Stack, Box, CircularProgress, Typography } from '@mui/material';
import { spacing, borderRadius, transitions } from '~/design-system/tokens';
import { submitAndWait } from '~/utils/http/submission';
import { useSubmissionPolling } from '~/hooks/useSubmissionPolling';
import { QueueStatusCard } from '~/components/Submission/QueueStatusCard';
import type { SubmissionReq } from '~/types/submission';

interface SubmissionWithPollingSimpleProps {
  /** 提交数据 */
  submissionData: SubmissionReq;
  /** 提交成功回调 */
  onSuccess?: (submission: any) => void;
  /** 提交失败回调 */
  onFailure?: (error: string) => void;
}

export function SubmissionWithPollingSimple({
  submissionData,
  onSuccess,
  onFailure
}: SubmissionWithPollingSimpleProps) {
  // 提交状态
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submissionId, setSubmissionId] = useState<number | null>(null);

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
    <Box sx={{ maxWidth: 800, mx: 'auto' }}>
      {/* 提交按钮 */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mb: spacing.lg }}>
        {isSubmitting || isPolling ? (
          <CircularProgress size={48} thickness={2} />
        ) : (
          <Paper
            component="button"
            onClick={handleSubmit}
            sx={{
              px: spacing.lg,
              py: spacing.md,
              borderRadius: borderRadius.sm,
              bgcolor: 'primary.main',
              color: 'primary.contrastText',
              fontSize: '1rem',
              fontWeight: 'bold',
              textTransform: 'none',
              cursor: 'pointer',
              boxShadow: 2,
              transition: transitions.interactive,
              '&:hover': {
                bgcolor: 'primary.dark',
                boxShadow: 3,
              },
            }}
          >
            {submissionId ? '重新提交' : '提交代码'}
          </Paper>
        )}
      </Box>

      {/* 提交状态信息 */}
      {submissionId && (
        <Stack spacing={spacing.lg}>
          {/* 提交 ID */}
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
            <Paper
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
            </Paper>
          ) : null}

          {/* 提交结果显示 */}
          {submission && (
            <Paper
              sx={{
                p: spacing.lg,
                border: '1px solid',
                borderColor: 'success.main',
                borderRadius: 2,
                bgcolor: 'success.50',
              }}
            >
              <Stack spacing={spacing.md}>
                <Typography variant="h6" color="success.dark" textAlign="center">
                  评测完成！
                </Typography>

                <Stack sx={{
                  flexDirection: { xs: 'column', sm: 'row' },
                  alignItems: 'flex-start',
                  gap: spacing.sm,
                  justifyContent: 'space-between'
                }}>
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      状态:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {submission.status}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      用时:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
                      {submission.execution_time}ms
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      内存:
                    </Typography>
                    <Typography variant="body2" fontWeight="medium">
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
                    <Typography variant="body2" color="error.dark">
                      {submission.error}
                    </Typography>
                  </Box>
                )}
              </Stack>
            </Paper>
          )}

          {/* 错误显示 */}
          {error && (
            <Paper
              sx={{
                p: spacing.lg,
                border: '1px solid',
                borderColor: 'error.main',
                borderRadius: 2,
                bgcolor: 'error.50',
              }}
            >
              <Typography variant="h6" color="error.dark" gutterBottom>
                评测失败
              </Typography>
              <Typography variant="body2" color="error.dark" textAlign="center">
                {error}
              </Typography>
            </Paper>
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
        </Stack>
      )}
    </Box>
  );
}