/**
 * RetryableError - 可重试错误组件
 *
 * 用于显示可重试的错误信息，并提供重试按钮
 * 支持自动重试机制和手动重试
 */

import { useState, useCallback } from 'react';
import { Paper, Stack, Typography, Box, Button, CircularProgress } from '@mui/material';
import { Refresh, Error, RestartAlt } from '@mui/icons-material';
import { spacing } from '~/design-system/tokens';

interface RetryableErrorProps {
  /** 错误信息 */
  error: string;
  /** 错误类型或状态码 */
  status?: number | string;
  /** 重试回调函数 */
  onRetry: () => void;
  /** 自动重试次数 */
  autoRetryCount?: number;
  /** 重试间隔（毫秒） */
  retryInterval?: number;
  /** 是否显示自动重试状态 */
  showAutoRetry?: boolean;
  /** 是否阻止手动重试 */
  manualRetryDisabled?: boolean;
}

/**
 * 判断错误是否可重试
 */
function isRetriableError(status?: number | string): boolean {
  if (!status) return true; // 网络错误默认可重试

  const statusCode = typeof status === 'number' ? status : parseInt(String(status));

  // 5xx 错误可重试
  if (statusCode >= 500 && statusCode < 600) {
    return true;
  }

  // 429 Too Many Requests 可重试
  if (statusCode === 429) {
    return true;
  }

  // 默认不可重试
  return false;
}

/**
 * RetryableError 主组件
 */
export function RetryableError({
  error,
  status,
  onRetry,
  autoRetryCount = 0,
  retryInterval = 2000,
  showAutoRetry = true,
  manualRetryDisabled = false,
}: RetryableErrorProps) {
  const [isAutoRetrying, setIsAutoRetrying] = useState(false);
  const [autoRetryAttempt, setAutoRetryAttempt] = useState(0);
  const [timerId, setTimerId] = useState<NodeJS.Timeout | null>(null);

  // 检查错误是否可重试
  const canRetry = isRetriableError(status);
  const shouldShowAutoRetry = canRetry && showAutoRetry && autoRetryCount > 0;

  /**
   * 处理手动重试
   */
  const handleManualRetry = useCallback(() => {
    // 取消自动重试
    if (timerId) {
      clearTimeout(timerId);
      setTimerId(null);
      setIsAutoRetrying(false);
      setAutoRetryAttempt(0);
    }
    onRetry();
  }, [timerId, onRetry]);

  /**
   * 处理自动重试
   */
  const handleAutoRetry = useCallback(() => {
    setAutoRetryAttempt(prev => prev + 1);

    if (autoRetryAttempt < autoRetryCount) {
      const id = setTimeout(() => {
        onRetry();
      }, retryInterval);
      setTimerId(id);
    } else {
      // 达到最大重试次数，停止自动重试
      setIsAutoRetrying(false);
      setTimerId(null);
    }
  }, [autoRetryAttempt, autoRetryCount, retryInterval, onRetry]);

  /**
   * 开始自动重试
   */
  const startAutoRetry = useCallback(() => {
    setIsAutoRetrying(true);
    setAutoRetryAttempt(0);
    handleAutoRetry();
  }, [handleAutoRetry]);

  /**
   * 取消自动重试
   */
  const cancelAutoRetry = useCallback(() => {
    if (timerId) {
      clearTimeout(timerId);
      setTimerId(null);
    }
    setIsAutoRetrying(false);
    setAutoRetryAttempt(0);
  }, [timerId]);

  // 获取错误类型的颜色
  const getErrorColor = () => {
    const statusCode = typeof status === 'number' ? status : parseInt(String(status) || '0');

    if (statusCode >= 500) return 'error';
    if (statusCode === 429) return 'warning';
    if (statusCode >= 400) return 'primary';
    return 'error';
  };

  // 获取友好的错误描述
  const getErrorDescription = () => {
    if (status === 429) return '请求过于频繁，请稍后重试';
    if (status && typeof status === 'number' && status >= 500) return '服务器暂时不可用，请稍后重试';
    if (!status) return '网络连接失败，请检查网络后重试';
    return error;
  };

  // 自动重试状态显示
  const autoRetryStatus = shouldShowAutoRetry && isAutoRetrying ? (
    <Stack direction="row" alignItems="center" spacing={spacing.sm}>
      <CircularProgress size={16} thickness={2} />
      <Typography variant="body2" color="text.secondary">
        自动重试中 ({autoRetryAttempt}/{autoRetryCount})
      </Typography>
    </Stack>
  ) : shouldShowAutoRetry && !isAutoRetrying ? (
    <Button
      variant="outlined"
      size="small"
      onClick={startAutoRetry}
      disabled={manualRetryDisabled}
      startIcon={<RestartAlt />}
    >
      开始自动重试
    </Button>
  ) : null;

  return (
    <Paper
      elevation={0}
      sx={{
        p: spacing.lg,
        border: '1px solid',
        borderColor: `${getErrorColor()}.main`,
        borderRadius: 2,
        bgcolor: `${getErrorColor()}.50`,
      }}
    >
      <Stack spacing={spacing.md}>
        {/* 错误图标和标题 */}
        <Stack direction="row" alignItems="center" gap={spacing.sm}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '50%',
              bgcolor: `${getErrorColor()}.main`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Error
              sx={{
                fontSize: 24,
                color: `${getErrorColor()}.contrastText`,
              }}
            />
          </Box>
          <Box>
            <Typography variant="h6" color={`${getErrorColor()}.dark`}>
              {canRetry ? '遇到问题，可以重试' : '出现错误'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              状态码: {status || '网络错误'}
            </Typography>
          </Box>
        </Stack>

        {/* 错误详情 */}
        <Box>
          <Typography variant="subtitle2" color="text.secondary" gutterBottom>
            错误信息:
          </Typography>
          <Typography variant="body2" color={getErrorColor() === 'primary' ? 'error' : 'text.primary'}>
            {getErrorDescription()}
          </Typography>
        </Box>

        {/* 重试选项 */}
        <Box>
          <Stack direction="row" alignItems="center" gap={spacing.sm}>
            {!isAutoRetrying && (
              <Button
                variant="contained"
                onClick={handleManualRetry}
                startIcon={<Refresh />}
                disabled={manualRetryDisabled}
                color="primary"
              >
                立即重试
              </Button>
            )}

            {autoRetryStatus}

            {isAutoRetrying && (
              <Button
                variant="outlined"
                onClick={cancelAutoRetry}
                size="small"
                color="inherit"
              >
                取消重试
              </Button>
            )}
          </Stack>
        </Box>

        {/* 重试说明 */}
        {canRetry && autoRetryCount > 0 && !isAutoRetrying && (
          <Typography variant="caption" color="text.secondary" textAlign="center">
            系统将在 {autoRetryCount} 次尝试后停止
          </Typography>
        )}
      </Stack>
    </Paper>
  );
}

// 导出工具函数
export { isRetriableError };