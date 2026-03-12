/**
 * QueueStatusCard - 评测队列状态显示组件
 *
 * 显示异步代码提交的队列状态和进度信息
 *
 * 功能：
 * - 显示当前状态（等待中、评测中、已完成等）
 * - 显示队列位置和预估等待时间
 * - 显示实际等待时间和执行时间
 * - 错误信息显示
 * - 视觉进度指示器
 */

import { Paper, Stack, Typography, Box, CircularProgress, Chip } from '@mui/material';
import {
  Schedule,
  PlayArrow,
  CheckCircle,
  Error,
  AccessTime,
  HourglassEmpty,
} from '@mui/icons-material';
import { spacing, borderRadius } from '~/design-system/tokens';
import type { JudgingQueueStats, QueueStatsStatus } from '~/types/submission';

interface QueueStatusCardProps {
  /** 队列状态信息 */
  queueStats: JudgingQueueStats;
  /** 是否为紧凑模式（用于小卡片） */
  compact?: boolean;
}

/**
 * 获取状态对应的图标
 */
function getStatusIcon(status: QueueStatsStatus) {
  switch (status) {
    case 'pending':
      return <Schedule sx={{ fontSize: 32, color: 'warning.main' }} />;
    case 'started':
      return <PlayArrow sx={{ fontSize: 32, color: 'info.main' }} />;
    case 'success':
      return <CheckCircle sx={{ fontSize: 32, color: 'success.main' }} />;
    case 'failed':
      return <Error sx={{ fontSize: 32, color: 'error.main' }} />;
    case 'timeout':
      return <HourglassEmpty sx={{ fontSize: 32, color: 'error.main' }} />;
    case 'cancelled':
      return <Error sx={{ fontSize: 32, color: 'text.disabled' }} />;
    default:
      return <Schedule sx={{ fontSize: 32 }} />;
  }
}

/**
 * 获取状态对应的颜色
 */
function getStatusColor(status: QueueStatsStatus): 'warning' | 'info' | 'success' | 'error' | 'default' {
  switch (status) {
    case 'pending':
      return 'warning';
    case 'started':
      return 'info';
    case 'success':
      return 'success';
    case 'failed':
    case 'timeout':
      return 'error';
    case 'cancelled':
      return 'default';
    default:
      return 'default';
  }
}

/**
 * 获取状态对应的中文标签
 */
function getStatusLabel(status: QueueStatsStatus): string {
  switch (status) {
    case 'pending':
      return '等待中';
    case 'started':
      return '评测中';
    case 'success':
      return '已完成';
    case 'failed':
      return '失败';
    case 'timeout':
      return '超时';
    case 'cancelled':
      return '已取消';
    default:
      return '未知';
  }
}

/**
 * 格式化时间为可读格式
 */
function formatTime(seconds?: number): string {
  if (!seconds) return '-';

  if (seconds < 60) {
    return `${seconds}秒`;
  } else if (seconds < 3600) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return remainingSeconds > 0 ? `${minutes}分${remainingSeconds}秒` : `${minutes}分钟`;
  } else {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return minutes > 0 ? `${hours}小时${minutes}分` : `${hours}小时`;
  }
}

/**
 * QueueStatusCard 主组件
 */
export function QueueStatusCard({ queueStats, compact = false }: QueueStatusCardProps) {
  const statusColor = getStatusColor(queueStats.status);
  const statusLabel = getStatusLabel(queueStats.status);

  // 计算进度百分比（用于进度条）
  const getProgressValue = (): number => {
    switch (queueStats.status) {
      case 'pending':
        // 等待中：根据队列位置估算（最多等待100个位置）
        if (queueStats.queue_position) {
          return Math.max(10, 100 - queueStats.queue_position);
        }
        return 10;
      case 'started':
        // 评测中：显示为50%
        return 50;
      case 'success':
      case 'failed':
      case 'timeout':
      case 'cancelled':
        // 完成状态：100%
        return 100;
      default:
        return 0;
    }
  };

  if (compact) {
    // 紧凑模式：用于小卡片
    return (
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: spacing.sm,
          p: spacing.sm,
          bgcolor: `${statusColor}.main`,
          borderRadius: borderRadius.sm,
        }}
      >
        {getStatusIcon(queueStats.status)}
        <Box>
          <Typography variant="body2" color="text.primary" fontWeight="medium">
            {statusLabel}
          </Typography>
          {queueStats.queue_position && (
            <Typography variant="caption" color="text.secondary">
              队列位置: {queueStats.queue_position}
            </Typography>
          )}
        </Box>
      </Box>
    );
  }

  // 完整模式
  return (
    <Paper
      elevation={0}
      sx={{
        p: spacing.lg,
        border: '1px solid',
        borderColor: `${statusColor}.main`,
        borderRadius: 2,
        bgcolor: `${statusColor}.50`,
      }}
    >
      <Stack spacing={spacing.md}>
        {/* 头部：状态图标和标签 */}
        <Stack direction="row" alignItems="center" spacing={spacing.md}>
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: '50%',
              bgcolor: `${statusColor}.main`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            {getStatusIcon(queueStats.status)}
          </Box>
          <Box flex={1}>
            <Typography variant="h6" color="text.primary">
              评测状态: {statusLabel}
            </Typography>
            {queueStats.worker_name && (
              <Typography variant="caption" color="text.secondary">
                Worker: {queueStats.worker_name}
              </Typography>
            )}
          </Box>
          <Chip
            label={queueStats.status.toUpperCase()}
            color={statusColor}
            size="small"
            variant="outlined"
          />
        </Stack>

        {/* 进度条 */}
        <Box>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: spacing.xs,
            }}
          >
            <Typography variant="body2" color="text.secondary">
              评测进度
            </Typography>
            {queueStats.status !== 'success' &&
              queueStats.status !== 'failed' &&
              queueStats.status !== 'timeout' &&
              queueStats.status !== 'cancelled' && (
                <CircularProgress size={20} thickness={4} />
              )}
          </Box>
          <Box
            sx={{
              width: '100%',
              height: 8,
              bgcolor: 'action.disabledBackground',
              borderRadius: 1,
              overflow: 'hidden',
            }}
          >
            <Box
              sx={{
                width: `${getProgressValue()}%`,
                height: '100%',
                bgcolor: `${statusColor}.main`,
                transition: 'width 0.3s ease-in-out',
              }}
            />
          </Box>
        </Box>

        {/* 详细信息网格 */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: spacing.md,
          }}
        >
          {/* 队列位置 */}
          {queueStats.queue_position !== undefined && queueStats.queue_position !== null && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: spacing.sm,
              }}
            >
              <Schedule color="action" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  队列位置
                </Typography>
                <Typography variant="body2" color="text.primary" fontWeight="medium">
                  第 {queueStats.queue_position} 位
                </Typography>
              </Box>
            </Box>
          )}

          {/* 预估等待时间 */}
          {queueStats.estimated_start_time && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: spacing.sm,
              }}
            >
              <AccessTime color="action" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  预计开始时间
                </Typography>
                <Typography variant="body2" color="text.primary" fontWeight="medium">
                  {new Date(queueStats.estimated_start_time).toLocaleTimeString('zh-CN', {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Typography>
              </Box>
            </Box>
          )}

          {/* 实际等待时间 */}
          {queueStats.queue_wait_seconds !== undefined &&
            queueStats.queue_wait_seconds !== null && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: spacing.sm,
                }}
              >
                <HourglassEmpty color="action" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    等待时长
                  </Typography>
                  <Typography variant="body2" color="text.primary" fontWeight="medium">
                    {formatTime(queueStats.queue_wait_seconds)}
                  </Typography>
                </Box>
              </Box>
            )}

          {/* 执行时间 */}
          {queueStats.execution_seconds !== undefined &&
            queueStats.execution_seconds !== null && (
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: spacing.sm,
                }}
              >
                <PlayArrow color="action" fontSize="small" />
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    执行时长
                  </Typography>
                  <Typography variant="body2" color="text.primary" fontWeight="medium">
                    {formatTime(queueStats.execution_seconds)}
                  </Typography>
                </Box>
              </Box>
            )}

          {/* 重试次数 */}
          {queueStats.retry_count > 0 && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: spacing.sm,
              }}
            >
              <Error color="action" fontSize="small" />
              <Box>
                <Typography variant="caption" color="text.secondary">
                  重试次数
                </Typography>
                <Typography variant="body2" color="text.primary" fontWeight="medium">
                  {queueStats.retry_count} 次
                </Typography>
              </Box>
            </Box>
          )}
        </Box>

        {/* 错误信息 */}
        {queueStats.error_message && (
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
              错误信息
            </Typography>
            <Typography variant="body2" color="error.dark">
              {queueStats.error_message}
            </Typography>
          </Box>
        )}

        {/* 时间戳 */}
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            pt: spacing.sm,
            borderTop: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Typography variant="caption" color="text.secondary">
            创建时间: {new Date(queueStats.created_at).toLocaleString('zh-CN')}
          </Typography>
          {queueStats.updated_at !== queueStats.created_at && (
            <Typography variant="caption" color="text.secondary">
              更新时间: {new Date(queueStats.updated_at).toLocaleString('zh-CN')}
            </Typography>
          )}
        </Box>
      </Stack>
    </Paper>
  );
}
