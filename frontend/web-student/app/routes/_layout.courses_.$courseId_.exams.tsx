import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Grid,
  Button,
  Chip,
  Card,
  CardContent,
  CardActions,
  Badge,
  Alert,
  type ChipProps,
} from '@mui/material';
import type { Course, Exam } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { useNavigate } from 'react-router';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import type { Route } from './+types/_layout.courses_.$courseId_.exams';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: `${loaderData?.course.title} - 测验列表` },
  ];
}

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
  const course = await http.get<Course>(`/courses/${params.courseId}`);
  const exams = await http.get<Page<Exam>>(`/courses/${params.courseId}/exams`);
  return { exams, course };
})

// 状态映射
const statusLabels = {
  draft: '草稿',
  published: '已发布',
  archived: '已归档',
};

// 状态颜色
const statusColors: Record<string, ChipProps['color']> = {
  draft: 'default',
  published: 'success',
  archived: 'default',
};

// 用户提交状态
type SubmissionStatus = 'null' | 'in_progress' | 'submitted' | 'graded' | 'auto_submitted';

const submissionStatusLabels: Record<SubmissionStatus, string> = {
  null: '未参加',
  in_progress: '进行中',
  submitted: '已提交',
  graded: '已评分',
  auto_submitted: '自动提交',
};

const submissionStatusColors: Record<SubmissionStatus, ChipProps['color']> = {
  null: 'default',
  in_progress: 'warning',
  submitted: 'info',
  graded: 'success',
  auto_submitted: 'error',
};

// 获取提交状态标签的辅助函数
const getSubmissionStatusKey = (status: string | null): SubmissionStatus => {
  return (status === null ? 'null' : status) as SubmissionStatus;
};

export default function ExamsPage({ loaderData, params }: Route.ComponentProps) {
  const exams = loaderData.exams.results;
  const course = loaderData.course;
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate(`/courses/${params.courseId}`);
  };

  const handleTakeExam = (examId: number) => {
    navigate(`/courses/${params.courseId}/exams/${examId}/`);
  };

  // 检查测验是否可以开始
  const canStartExam = (exam: Exam) => {
    if (exam.status !== 'published') return false;
    if (!exam.is_active) return false;
    if (exam.user_submission_status) {
      return exam.user_submission_status.status === null || exam.user_submission_status.status === 'in_progress';
    }
    return true;
  };

  // 检查是否可以查看结果
  const canViewResults = (exam: Exam) => {
    const status = exam.user_submission_status?.status;
    // console.log(exam.show_results_after_submit)
    return status === 'graded' || (status === 'auto_submitted' && exam.show_results_after_submit) || (status === 'submitted' && exam.show_results_after_submit);
  };

  if (!exams || exams.length === 0) {
    return (
      <PageContainer maxWidth="sm">
        <SectionContainer spacing="md" variant="card">
          <Typography variant="h6" color="text.secondary" align="center" sx={{ py: spacing.lg }}>
            暂无测验
          </Typography>
          <Typography variant="body2" color="text.disabled" align="center">
            该课程还没有发布测验。
          </Typography>
          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
            <Button onClick={handleGoBack}>
              返回课程主页
            </Button>
          </Box>
        </SectionContainer>
      </PageContainer>
    );
  }

  return (
    <PageContainer maxWidth="lg">
      <PageHeader
        title="测验列表"
        subtitle={`课程: ${course.title}`}
      />
      <SectionContainer spacing="md" variant="card">
        <Box sx={{ p: { xs: 2, sm: 3 }, borderBottom: 1, borderColor: 'divider' }}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid>
              <Button
                variant="outlined"
                onClick={handleGoBack}
                sx={{
                  color: 'text.primary',
                  borderColor: 'divider',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                返回课程主页
              </Button>
            </Grid>
          </Grid>
        </Box>

        <List sx={{ bgcolor: 'background.paper' }}>
          {exams.map((exam) => (
            <ListItem
              key={exam.id}
              disablePadding
              sx={{
                '&:not(:last-child)': {
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                },
              }}
            >
              <ListItemButton
                sx={{
                  '&:hover': {
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6" component="span" sx={{ fontWeight: 600 }}>
                        {exam.title}
                      </Typography>
                      <Chip
                        label={statusLabels[exam.status]}
                        size="small"
                        color={statusColors[exam.status]}
                        variant="outlined"
                      />
                      {exam.user_submission_status && (
                        <Chip
                          label={submissionStatusLabels[getSubmissionStatusKey(exam.user_submission_status.status)]}
                          size="small"
                          color={submissionStatusColors[getSubmissionStatusKey(exam.user_submission_status.status)]}
                          variant="filled"
                        />
                      )}
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 1 }}>
                      {exam.description && (
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {exam.description}
                        </Typography>
                      )}
                      <Grid container spacing={2}>
                        <Grid size={12}>
                          <Typography variant="caption" color="text.secondary">
                            题目数量：{exam.question_count} 题
                          </Typography>
                        </Grid>
                        <Grid size={12}>
                          <Typography variant="caption" color="text.secondary">
                            总分：{exam.total_score} 分，及格分：{exam.passing_score} 分
                          </Typography>
                        </Grid>
                        <Grid size={12}>
                          <Typography variant="caption" color="text.secondary">
                            开放时间：{exam.start_time} 至 {exam.end_time}
                          </Typography>
                        </Grid>
                        <Grid size={12}>
                            <Typography variant="caption" color="text.secondary">
                              答题时长：{exam.duration_minutes>0?`${exam.duration_minutes} 分钟`:'不限时'}
                            </Typography>
                          </Grid>
                      </Grid>
                      {exam.user_submission_status && exam.user_submission_status.status === 'graded' && (
                        <Box sx={{ mt: 1 }}>
                          <Typography
                            variant="caption"
                            color={exam.user_submission_status.is_passed ? 'success.main' : 'error.main'}
                            sx={{ fontWeight: 500 }}
                          >
                            得分：{exam.user_submission_status.total_score} 分，{exam.user_submission_status.is_passed ? '已通过' : '未通过'}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  }
                />
                <Box sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', pl: 2 }}>
                  {exam.is_active ? (
                    <Badge
                      badgeContent={
                        exam.user_submission_status && exam.user_submission_status.status === 'in_progress'
                          ? '进行中'
                          : exam.user_submission_status
                            ? '已参加'
                            : '可参加'
                      }
                      color="primary"
                    >
                      <Card sx={{ width: 200 }}>
                        <CardContent sx={{ p: 2 }}>
                          {exam.user_submission_status?.status === 'in_progress' ? (
                            <>
                              <Typography variant="caption" color="text.secondary">
                                剩余时间
                              </Typography>
                              <Typography variant="body2" color="error" sx={{ fontWeight: 600 }}>
                                {exam.remaining_time?.remaining_seconds && exam.remaining_time.remaining_seconds > 0
                                  ? `${Math.floor(exam.remaining_time.remaining_seconds / 60)}:${(exam.remaining_time.remaining_seconds % 60).toString().padStart(2, '0')}`
                                  : '已超时'
                                }
                              </Typography>
                            </>
                          ) : (
                            <Typography variant="caption" color="text.secondary">
                              {exam.question_count} 题
                            </Typography>
                          )}
                        </CardContent>
                        <CardActions sx={{ p: '4px 8px' }}>
                          {canStartExam(exam) ? (
                            <Button
                              size="small"
                              variant="contained"
                              onClick={(e) => {
                                e.preventDefault();
                                handleTakeExam(exam.id);
                              }}
                              disabled={!exam.is_active}
                              fullWidth
                            >
                              {exam.user_submission_status?.status === 'in_progress' ? '继续测验' : '开始测验'}
                            </Button>
                          ) : canViewResults(exam) ? (
                            <Button
                              size="small"
                              variant="outlined"
                              onClick={(e) => {
                                e.preventDefault();
                                navigate(`/courses/${params.courseId}/exams/${exam.id}/results`);
                              }}
                              fullWidth
                            >
                              查看结果
                            </Button>
                          ) : (
                            <Button
                              size="small"
                              variant="outlined"
                              disabled
                              fullWidth
                            >
                              {exam.status === 'draft' ? '未发布' : '暂不可参加'}
                            </Button>
                          )}
                        </CardActions>
                      </Card>
                    </Badge>
                  ) : (
                    <Alert severity="info">
                      测验未开放
                    </Alert>
                  )}
                </Box>
              </ListItemButton>
            </ListItem>
          ))}
        </List>
      </SectionContainer>
    </PageContainer>
  );
}