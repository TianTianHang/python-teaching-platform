import {
  Box,
  Typography,
  Button,
  Link,
  Alert,
  Chip,
  Card,
  CardContent,
  Divider,
  type SxProps,
  type Theme,
} from '@mui/material';
import {
  Lock as LockIcon,
  ArrowBack as ArrowBackIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router';
import { PrerequisiteProgressComponent } from './PrerequisiteProgress';
import type { ChapterUnlockStatus } from '~/types/course';

interface ChapterLockScreenProps {
  chapter: {
    id: number;
    title: string;
    course_title: string;
  };
  unlockStatus: ChapterUnlockStatus;
  courseId: string;
  navigateBack?: boolean;
  sx?: SxProps<Theme>;
}

const lockScreenContainerSx: SxProps<Theme> = {
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  p: 2,
  bgcolor: 'background.default',
};

const lockCardSx: SxProps<Theme> = {
  maxWidth: 600,
  width: '100%',
  p: 3,
};

export function ChapterLockScreen({
  chapter,
  unlockStatus,
  courseId,
  navigateBack = true,
  sx,
}: ChapterLockScreenProps) {
  const navigate = useNavigate();

  const handleGoBack = () => {
    if (navigateBack) {
      navigate(`/courses/${courseId}/chapters`);
    }
  };

  const handleGoToPrerequisite = (chapterId: number) => {
    navigate(`/courses/${courseId}/chapters/${chapterId}`);
  };

  // 格式化倒计时显示
  const formatTimeUntil = (timeUntil: { days: number; hours: number; minutes: number }): string => {
    const parts = [];
    if (timeUntil.days > 0) parts.push(`${timeUntil.days}天`);
    if (timeUntil.hours > 0) parts.push(`${timeUntil.hours}小时`);
    if (timeUntil.minutes > 0) parts.push(`${timeUntil.minutes}分钟`);
    return parts.join(' ') || '即将解锁';
  };
  return (
    <Box sx={[lockScreenContainerSx, ...(Array.isArray(sx) ? sx : [sx])]}>
      <Card sx={lockCardSx}>
        <CardContent sx={{ p: 0 }}>
          {/* Header */}
          <Box
            sx={{
              p: 3,
              pb: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
              borderBottom: 1,
              borderColor: 'divider',
            }}
          >
            <LockIcon color="error" sx={{ fontSize: 48 }} />
            <Box sx={{ flexGrow: 1 }}>
              <Typography variant="h4" component="h1" gutterBottom>
                章节已锁定
              </Typography>
              <Typography variant="h6" color="text.secondary">
                {chapter.title}
              </Typography>
            </Box>
          </Box>

          {/* Alert */}
          <Alert
            severity="info"
            sx={{
              m: 3,
              mb: 2,
              '& .MuiAlert-icon': {
                fontSize: 24,
              },
            }}
          >
            <Typography variant="body1">
              您需要完成前置条件才能解锁此章节。
            </Typography>
          </Alert>

          {/* Course Info */}
          <Box sx={{ m: 3, mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              所属课程：
              <Link
                href={`/courses/${chapter.course_title}`}
                sx={{
                  ml: 1,
                  color: 'primary.main',
                  textDecoration: 'none',
                  fontWeight: 'medium',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                {chapter.course_title}
              </Link>
            </Typography>
          </Box>

          <Divider sx={{ m: 0 }} />

          {/* Unlock Condition Info */}
          <Box sx={{ m: 3, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              解锁条件
            </Typography>

            {unlockStatus.reason === 'prerequisite' && (
              <Box>
                <Chip
                  label="需要完成前置章节"
                  color="default"
                  size="small"
                  icon={<CheckCircleIcon />}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  需要先完成以下章节才能解锁。
                </Typography>
              </Box>
            )}

            {unlockStatus.reason === 'date' && (
              <Box>
                <Chip
                  label="定时解锁"
                  color="default"
                  size="small"
                  icon={<ScheduleIcon />}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  此章节将在特定时间后解锁。
                </Typography>
                {unlockStatus.time_until_unlock && (
                  <Typography variant="body1" color="warning.main" sx={{ mt: 1 }}>
                    倒计时：{formatTimeUntil(unlockStatus.time_until_unlock)}
                  </Typography>
                )}
              </Box>
            )}

            {unlockStatus.reason === 'both' && (
              <Box>
                <Chip
                  label="所有条件"
                  color="default"
                  size="small"
                  icon={<CheckCircleIcon />}
                  sx={{ mb: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  需要同时完成前置章节并等待解锁时间。
                </Typography>
                {unlockStatus.time_until_unlock && (
                  <Typography variant="body1" color="warning.main" sx={{ mt: 1 }}>
                    倒计时：{formatTimeUntil(unlockStatus.time_until_unlock)}
                  </Typography>
                )}
              </Box>
            )}
          </Box>

          <Divider sx={{ m: 0 }} />

          {/* Prerequisites Progress */}
          {unlockStatus.prerequisite_progress && (
            <Box sx={{ m: 3, mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                前置进度
              </Typography>
              <PrerequisiteProgressComponent
                progress={unlockStatus.prerequisite_progress}
                unlockStatus={unlockStatus}
                showUnlockCountdown={true}
              />
            </Box>
          )}

          {/* Action Buttons */}
          <Box
            sx={{
              p: 3,
              pt: 2,
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
            }}
          >
            {navigateBack && (
              <Button
                variant="outlined"
                startIcon={<ArrowBackIcon />}
                onClick={handleGoBack}
                fullWidth
              >
                返回章节列表
              </Button>
            )}

            {unlockStatus.prerequisite_progress && unlockStatus.prerequisite_progress.remaining?.length > 0 && (
              <Button
                variant="contained"
                onClick={() => {
                  // Navigate to the first remaining prerequisite
                  const firstPrerequisite = unlockStatus.prerequisite_progress?.remaining[0]?.id;
                  if (firstPrerequisite) {
                    handleGoToPrerequisite(firstPrerequisite);
                  }
                }}
                fullWidth
              >
                前往第一个前置章节
              </Button>
            )}

            {unlockStatus.prerequisite_progress &&
              unlockStatus.prerequisite_progress.completed >= unlockStatus.prerequisite_progress.total &&
              unlockStatus.is_locked && (
              <Button
                variant="contained"
                disabled
                fullWidth
                sx={{
                  color: 'text.disabled',
                  bgcolor: 'grey.200',
                }}
              >
                等待解锁时间...
              </Button>
            )}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}