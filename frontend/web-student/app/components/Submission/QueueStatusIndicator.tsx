/**
 * 队列状态指示器组件
 *
 * 显示当前评测队列的状态，包括：
 * - 队列繁忙程度 (available/busy/full)
 * - 等待中的任务数
 * - 正在执行的任务数
 * - 预估等待时间
 */

import { Box, Chip, Typography, LinearProgress, Tooltip, Skeleton } from "@mui/material";
import {
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from "@mui/icons-material";
import type { QueueStatusRes } from "~/types/submission";

export interface QueueStatusIndicatorProps {
  /** 队列状态数据 */
  queueStatus: QueueStatusRes | null;
  /** 是否正在加载 */
  isLoading?: boolean;
  /** 紧凑模式 */
  compact?: boolean;
}

/**
 * 获取状态配置
 */
function getStatusConfig(status: QueueStatusRes["system_status"]) {
  const configs = {
    available: {
      label: "空闲",
      color: "success" as const,
      icon: CheckCircleIcon,
      description: "队列畅通，可立即执行",
    },
    busy: {
      label: "繁忙",
      color: "warning" as const,
      icon: WarningIcon,
      description: "队列有积压，可能需要等待",
    },
    full: {
      label: "已满",
      color: "error" as const,
      icon: ErrorIcon,
      description: "队列已满，请稍后再试",
    },
  };
  return configs[status];
}

/**
 * 队列状态指示器组件
 */
export function QueueStatusIndicator({
  queueStatus,
  isLoading = false,
  compact = false,
}: QueueStatusIndicatorProps) {
  // 加载中状态
  if (isLoading) {
    if (compact) {
      return <Skeleton width={80} height={24} />;
    }
    return (
      <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
        <Skeleton width={120} height={24} />
        <Skeleton width={80} height={24} />
      </Box>
    );
  }

  // 无数据状态
  if (!queueStatus) {
    return null;
  }

  const statusConfig = getStatusConfig(queueStatus.system_status);
  const StatusIcon = statusConfig.icon;
  const usagePercent = Math.round(
    ((queueStatus.pending_count + queueStatus.running_count) /
      queueStatus.total_capacity) *
      100
  );

  // 紧凑模式：只显示状态标签
  if (compact) {
    return (
      <Tooltip title={statusConfig.description}>
        <Chip
          icon={<StatusIcon />}
          label={statusConfig.label}
          color={statusConfig.color}
          size="small"
          variant="outlined"
        />
      </Tooltip>
    );
  }

  // 完整模式
  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 1.5 }}>
      {/* 状态标签和预估时间 */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <StatusIcon fontSize="small" color={statusConfig.color} />
          <Typography variant="body2" color="text.secondary">
            队列状态：
          </Typography>
          <Chip
            label={statusConfig.label}
            color={statusConfig.color}
            size="small"
          />
        </Box>

        {/* 显示状态消息（如果有） */}
        {queueStatus.status_message && (
          <Typography variant="body2" color="text.secondary">
            {queueStatus.status_message}
          </Typography>
        )}
      </Box>

      {/* 进度条 */}
      <Box>
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            mb: 0.5,
          }}
        >
          <Typography variant="caption" color="text.secondary">
            队列使用率
          </Typography>
          <Typography variant="caption" color="text.secondary">
            {queueStatus.running_count} 运行中 /{" "}
            {queueStatus.pending_count} 等待中 /{" "}
            {queueStatus.available_slots} 可用
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={usagePercent}
          color={statusConfig.color}
          sx={{
            height: 6,
            borderRadius: 3,
            bgcolor: "action.hover",
          }}
        />
      </Box>
    </Box>
  );
}

export default QueueStatusIndicator;