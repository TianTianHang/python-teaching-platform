import {
  Box,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  type SxProps,
  type Theme,
} from '@mui/material';
import { CheckCircle as CheckCircleIcon, Schedule as ScheduleIcon } from '@mui/icons-material';
import type { PrerequisiteProgress, ChapterUnlockStatus } from '~/types/course';

interface PrerequisiteProgressProps {
  progress: PrerequisiteProgress;
  unlockStatus?: ChapterUnlockStatus;
  showUnlockCountdown?: boolean;
  sx?: SxProps<Theme>;
}

const progressContainerSx: SxProps<Theme> = {
  display: 'flex',
  flexDirection: 'column',
  gap: 2,
  p: 2,
};

export function PrerequisiteProgressComponent({
  progress,
  unlockStatus,
  showUnlockCountdown = true,
  sx,
}: PrerequisiteProgressProps) {
  const progressPercentage = progress.total > 0
    ? (progress.completed / progress.total) * 100
    : 0;

  // 格式化倒计时显示
  const formatTimeUntil = (timeUntil: { days: number; hours: number; minutes: number } | null): string => {
    if (!timeUntil) return '';
    const parts = [];
    if (timeUntil.days > 0) parts.push(`${timeUntil.days}天`);
    if (timeUntil.hours > 0) parts.push(`${timeUntil.hours}小时`);
    if (timeUntil.minutes > 0) parts.push(`${timeUntil.minutes}分钟`);
    return parts.join(' ') || '即将解锁';
  };

  const unlockCountdown = unlockStatus?.time_until_unlock
    ? formatTimeUntil(unlockStatus.time_until_unlock)
    : null;

  const isAllCompleted = progress.completed >= progress.total;

  return (
    <Box sx={[progressContainerSx, ...(Array.isArray(sx) ? sx : [sx])]}>
      {/* Progress Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <Typography variant="h6" component="h3" sx={{ flexGrow: 1 }}>
          前置条件进度
        </Typography>
        <Chip
          label={`${progress.completed}/${progress.total}`}
          size="small"
          color={isAllCompleted ? 'success' : 'default'}
          icon={isAllCompleted ? (
            <CheckCircleIcon fontSize="small" />
          ) : undefined}
        />
      </Box>

      {/* Progress Bar */}
      <Box sx={{ mb: 2 }}>
        <LinearProgress
          variant="determinate"
          value={progressPercentage}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: 'divider',
          }}
        />
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ display: 'block', mt: 1, textAlign: 'right' }}
        >
          {Math.round(progressPercentage)}% 完成
        </Typography>
      </Box>

      {/* Completed Prerequisites */}
      {progress.completed > 0 && (
        <Box>
          <Typography variant="subtitle2" color="success.main" sx={{ mb: 1 }}>
            已完成章节
          </Typography>
          <Typography variant="body2" color="success.dark">
            已完成 {progress.completed} 个前置章节
          </Typography>
        </Box>
      )}

      {/* Remaining Prerequisites */}
      {progress.remaining.length > 0 && (
        <Box>
          <Typography variant="subtitle2" color="warning.main" sx={{ mb: 1 }}>
            待完成章节
          </Typography>
          <List dense sx={{ bgcolor: 'warning.light', borderRadius: 1 }}>
            {progress.remaining.map((chapter) => (
              <ListItem key={`remaining-${chapter.id}`} disablePadding sx={{ pl: 2 }}>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ScheduleIcon color="warning" fontSize="small" />
                      <Typography variant="body2" color="warning.dark">
                        {chapter.title}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Unlock Countdown */}
      {showUnlockCountdown && unlockStatus?.is_locked && unlockCountdown && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            bgcolor: 'info.light',
            borderRadius: 1,
            borderLeft: 3,
            borderColor: 'info.main',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <ScheduleIcon color="info" fontSize="small" />
            <Typography variant="subtitle2" color="info.dark">
              预计解锁时间
            </Typography>
          </Box>
          <Typography variant="body1" color="info.contrastText">
            {unlockCountdown}
          </Typography>
        </Box>
      )}

      {/* Unlock Status Message */}
      {isAllCompleted && !unlockStatus?.is_locked && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            bgcolor: 'success.light',
            borderRadius: 1,
            borderLeft: 3,
            borderColor: 'success.main',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
            <CheckCircleIcon color="success" fontSize="small" />
            <Typography variant="subtitle2" color="success.dark">
              前置条件已完成！
            </Typography>
          </Box>
          <Typography variant="body2" color="success.contrastText">
            章节已解锁，可以开始学习。
          </Typography>
        </Box>
      )}
    </Box>
  );
}