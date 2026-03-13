/**
 * 任务状态进度组件
 *
 * 显示异步提交任务的执行进度，包括：
 * - 当前状态（等待中/评测中/完成）
 * - 队列位置
 * - 等待时间
 * - 执行时间
 * - 取消按钮
 */

import { Box, Typography, Button, CircularProgress, Alert } from "@mui/material";
import {
  HourglassEmpty as HourglassEmptyIcon,
  PlayCircle as PlayCircleIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Cancel as CancelIcon,
  Timer as TimerIcon,
} from "@mui/icons-material";
import type { TaskStatusRes, QueueStatsStatus } from "~/types/submission";

export interface TaskProgressProps {
  /** 任务状态数据 */
  taskStatus: TaskStatusRes | null;
  /** 是否正在加载 */
  isLoading?: boolean;
  /** 取消回调 */
  onCancel?: () => void;
  /** 是否可以取消 */
  canCancel?: boolean;
}

/**
 * 获取队列状态配置
 */
function getQueueStatusConfig(status: QueueStatsStatus) {
  const configs = {
    pending: {
      label: "等待中",
      icon: HourglassEmptyIcon,
      color: "warning" as const,
      description: "任务在队列中等待执行",
    },
    started: {
      label: "执行中",
      icon: PlayCircleIcon,
      color: "info" as const,
      description: "Worker 正在执行评测",
    },
    success: {
      label: "成功",
      icon: CheckCircleIcon,
      color: "success" as const,
      description: "评测已完成",
    },
    failed: {
      label: "失败",
      icon: ErrorIcon,
      color: "error" as const,
      description: "评测失败",
    },
    timeout: {
      label: "超时",
      icon: CancelIcon,
      color: "error" as const,
      description: "任务执行超时",
    },
    cancelled: {
      label: "已取消",
      icon: CancelIcon,
      color: "inherit" as const,
      description: "任务已被取消",
    },
  };
  return configs[status];
}

/**
 * 格式化时间（秒）
 */
function formatSeconds(seconds: number | null): string {
  if (seconds === null || seconds === undefined) {
    return "--";
  }
  if (seconds < 60) {
    return `${Math.round(seconds)} 秒`;
  }
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.round(seconds % 60);
  return `${minutes} 分 ${remainingSeconds} 秒`;
}

/**
 * 任务状态进度组件
 */
export function TaskProgress({
  taskStatus,
  isLoading = false,
  onCancel,
  canCancel = false,
}: TaskProgressProps) {
  // 加载中状态
  if (isLoading) {
    return (
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: 2,
          py: 3,
        }}
      >
        <CircularProgress size={24} />
        <Typography variant="body2" color="text.secondary">
          加载任务状态...
        </Typography>
      </Box>
    );
  }

  // 无数据状态
  if (!taskStatus) {
    return null;
  }

  const queueConfig = getQueueStatusConfig(taskStatus.queue_status);
  const StatusIcon = queueConfig.icon;
  const isTerminal =
    taskStatus.queue_status === "success" ||
    taskStatus.queue_status === "failed" ||
    taskStatus.queue_status === "timeout" ||
    taskStatus.queue_status === "cancelled";
  const isPending = taskStatus.queue_status === "pending";
  const isStarted = taskStatus.queue_status === "started";

  return (
    <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      {/* 状态标题 */}
      <Box
        sx={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          {isPending || isStarted ? (
            <CircularProgress size={20} color={queueConfig.color} />
          ) : (
            <StatusIcon color={queueConfig.color} />
          )}
          <Typography variant="body1" fontWeight="medium">
            {queueConfig.label}
          </Typography>
        </Box>

        {/* 取消按钮 */}
        {!isTerminal && canCancel && onCancel && (
          <Button
            size="small"
            variant="outlined"
            color="error"
            onClick={onCancel}
            startIcon={<CancelIcon />}
          >
            取消任务
          </Button>
        )}
      </Box>

      {/* 进度信息 */}
      {(isPending || isStarted) && (
        <Alert severity="info" icon={<TimerIcon />}>
          {isPending && "任务正在队列中等待，请耐心等待..."}
          {isStarted && "任务正在执行中，请稍候..."}
        </Alert>
      )}

      {/* 时间信息 */}
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(120px, 1fr))",
          gap: 2,
        }}
      >
        {/* 队列等待时间 */}
        <Box>
          <Typography variant="caption" color="text.secondary" display="block">
            队列等待
          </Typography>
          <Typography variant="body2" fontWeight="medium">
            {formatSeconds(taskStatus.queue_wait_seconds)}
          </Typography>
        </Box>

        {/* 执行时间 */}
        <Box>
          <Typography variant="caption" color="text.secondary" display="block">
            执行时间
          </Typography>
          <Typography variant="body2" fontWeight="medium">
            {formatSeconds(taskStatus.execution_seconds)}
          </Typography>
        </Box>

        {/* 总耗时 */}
        <Box>
          <Typography variant="caption" color="text.secondary" display="block">
            总耗时
          </Typography>
          <Typography variant="body2" fontWeight="medium">
            {formatSeconds(taskStatus.total_seconds)}
          </Typography>
        </Box>
      </Box>

      {/* 错误信息 */}
      {taskStatus.error_message && (
        <Alert severity="error" icon={<ErrorIcon />}>
          {taskStatus.error_message}
        </Alert>
      )}
    </Box>
  );
}

export default TaskProgress;