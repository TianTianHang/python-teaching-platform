import {
  Box,
  Typography,
  Button,
  Alert,
  CircularProgress,
  Divider,
  Card,
  CardContent,
  Chip,
  useTheme,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Cancel,
  Quiz,
  EmojiEvents,
  AccessTime,
} from '@mui/icons-material';
import type { ExamSubmission, ExamAnswer } from "~/types/course";
import type { Route } from "./+types/_layout.courses_.$courseId_.exams_.$examId_.results";
import { createHttp } from "~/utils/http/index.server";
import { Link } from 'react-router';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, SectionContainer } from '~/components/Layout';
import ScoreRing from '~/components/ExamReport/ScoreRing';
import SummaryCard from '~/components/ExamReport/SummaryCard';
import AnswerReviewCard from '~/components/ExamReport/AnswerReviewCard';
import MarkdownRenderer from '~/components/MarkdownRenderer';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: `${loaderData?.submission.exam_title} - 测验结果` },
  ];
}

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
  const submission = await http.get<ExamSubmission>(`/exams/${params.examId}/results/`);
  return { submission };
});

// Status configurations
const getStatusConfig = (status: string) => {
  const configs: Record<string, { color: 'success' | 'error' | 'warning' | 'default'; label: string }> = {
    graded: { color: 'success', label: '已评分' },
    submitted: { color: 'success', label: '已提交' },
    auto_submitted: { color: 'warning', label: '自动提交(超时)' },
    in_progress: { color: 'default', label: '进行中' },
  };
  return configs[status] || configs.in_progress;
};

// Format time duration
function formatTime(seconds?: number): string {
  if (!seconds) return '--';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}小时${minutes}分钟`;
  }
  if (minutes > 0) {
    return `${minutes}分钟`;
  }
  return `${secs}秒`;
}

// Get color for score percentage
const getScoreGrade = (percentage: number) => {
  if (percentage >= 90) return { color: 'success', label: '优秀', icon: '🏆' }; // Amber
  if (percentage >= 75) return { color: 'primary', label: '良好', icon: '⭐' }; // Blue
  if (percentage >= 60) return { color: 'primary', label: '及格', icon: '✓' }; // Green
  if (percentage >= 50) return { color: 'warning', label: '边缘', icon: '⚠️' }; // Amber
  return { color: 'error', label: '不及格', icon: '✗' }; // Red
};

export default function ExamResultsPage({ loaderData, params }: Route.ComponentProps) {
  const theme = useTheme();
  const courseId = Number(params.courseId);
  const examId = Number(params.examId);

  // Validate path parameters
  if (isNaN(courseId) || isNaN(examId) || courseId <= 0 || examId <= 0) {
    return (
      <PageContainer maxWidth="md">
        <SectionContainer spacing="lg" variant="card">
          <Alert severity="error">无效的课程或测验ID。</Alert>
        </SectionContainer>
      </PageContainer>
    );
  }

  const { submission } = loaderData;

  if (!submission) {
    return (
      <PageContainer maxWidth="md">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </PageContainer>
    );
  }

  const statusConfig = getStatusConfig(submission.status);
  const scorePercentage = submission.exam_total_score
    ? ((parseFloat(submission.total_score || '0') / submission.exam_total_score) * 100)
    : 0;
  
  const gradeInfo = getScoreGrade(scorePercentage);

  return (
    <PageContainer maxWidth="lg">
      {/* Enhanced Page Header */}
      <Box
        sx={{
          position: 'relative',
          mb: 4,
          pb: 4,
          borderBottom: `1px solid ${theme.palette.divider}`,
        }}
      >
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: 2,
          }}
        >
          <Box>
            <Typography
              variant="overline"
              sx={{
                color: theme.palette.text.secondary,
                letterSpacing: 2,
                textTransform: 'uppercase',
                fontWeight: 600,
              }}
            >
              测验报告
            </Typography>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                mt: 1,
                fontFamily: '"Playfair Display", serif',
              }}
            >
              {submission.exam_title}
            </Typography>
          </Box>

          <Button
            startIcon={<ArrowBack />}
            component={Link}
            to={`/courses/${courseId}/exams`}
            variant="outlined"
            sx={{
              borderRadius: 2,
              px: 3,
              py: 1.5,
            }}
          >
            返回测验列表
          </Button>
        </Box>

        {/* Decorative gradient line */}
        <Box
          sx={{
            position: 'absolute',
            bottom: -1,
            left: 0,
            width: 120,
            height: 3,
            background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.light} 100%)`,
          }}
        />
      </Box>

      {/* Summary Section - Two Column Layout */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '300px 1fr' },
          gap: 3,
          mb: 4,
        }}
      >
        {/* Left Column - Score Ring */}
        <Card
          sx={{
            height: 'fit-content',
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: 4,
              background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.light} 100%)`,
            },
          }}
        >
          <CardContent sx={{ textAlign: 'center', py: 4 }}>
            <ScoreRing
              score={parseFloat(submission.total_score ?? '0')}
              maxScore={submission.exam_total_score ?? 100}
              size={160}
              strokeWidth={14}
            />

            <Divider sx={{ my: 3 }} />

            {/* Pass/Fail Status */}
            {submission.is_passed !== null && submission.is_passed !== undefined && (
              <Box
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 1,
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  backgroundColor: submission.is_passed
                    ? `${theme.palette.success.main}08`
                    : `${theme.palette.error.main}08`,
                  border: `1px solid ${submission.is_passed
                    ? theme.palette.success.main
                    : theme.palette.error.main
                  }`,
                }}
              >
                {submission.is_passed ? (
                  <CheckCircle sx={{ color: theme.palette.success.main }} />
                ) : (
                  <Cancel sx={{ color: theme.palette.error.main }} />
                )}
                <Typography
                  variant="subtitle1"
                  sx={{
                    fontWeight: 600,
                    color: submission.is_passed
                      ? theme.palette.success.main
                      : theme.palette.error.main,
                  }}
                >
                  {submission.is_passed ? '通过' : '未通过'}
                </Typography>
              </Box>
            )}

            {submission.exam_passing_score !== undefined && (
              <Typography
                variant="caption"
                sx={{
                  color: theme.palette.text.secondary,
                  mt: 2,
                  display: 'block',
                }}
              >
                及格分: {submission.exam_passing_score} / {submission.exam_total_score}
              </Typography>
            )}
          </CardContent>
        </Card>

        {/* Right Column - Metrics Grid */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)' },
            gap: 2,
          }}
        >
          {/* Score Summary */}
          <SummaryCard
            title="总分"
            value={`${submission.total_score ?? '--'} / ${submission.exam_total_score ?? '--'}`}
            icon={<EmojiEvents />}
            color={gradeInfo.color as 'success' | 'warning' | 'error' | 'primary'}
            subtitle={`${scorePercentage.toFixed(1)}%`}
          />

          {/* Status */}
          <SummaryCard
            title="状态"
            value={statusConfig.label}
            icon={<Quiz />}
            color={statusConfig.color === 'default' ? 'neutral' : statusConfig.color}
          />

          {/* Time Spent */}
          <SummaryCard
            title="用时"
            value={formatTime(submission.time_spent_seconds)}
            icon={<AccessTime />}
            color="primary"
          />

          {/* Grade */}
          <SummaryCard
            title="等级"
            value={gradeInfo.label}
            icon={<Typography sx={{ fontSize: 20 }}>{gradeInfo.icon}</Typography>}
            color={gradeInfo.color as 'success' | 'warning' | 'error' | 'primary'}
          />

          {/* Auto-submit Warning */}
          {submission.status === 'auto_submitted' && (
            <Alert
              severity="warning"
              sx={{
                gridColumn: '1 / -1',
                mt: 1,
              }}
            >
              您的测验因超时被自动提交
            </Alert>
          )}
        </Box>
      </Box>

      {/* Questions Timeline */}
      <SectionContainer spacing="lg" variant="card">
        <Box sx={{ mb: 4 }}>
          <Typography
            variant="h5"
            sx={{
              fontWeight: 600,
              mb: 1,
              fontFamily: '"Playfair Display", serif',
            }}
          >
            题目回顾
          </Typography>
          <Typography
            variant="body2"
            sx={{ color: theme.palette.text.secondary }}
          >
            共 {submission.answers.length} 道题目 · 正确率 {Math.round(scorePercentage)}%
          </Typography>
        </Box>

        <Divider sx={{ mb: 4 }} />

        {/* Question Timeline */}
        <Box
          sx={{
            position: 'relative',
          }}
        >
          {/* Timeline Line */}
          <Box
            sx={{
              position: 'absolute',
              left: 19,
              top: 0,
              bottom: 0,
              width: 2,
              background: `linear-gradient(to bottom, ${theme.palette.primary.main}, ${theme.palette.divider})`,
            }}
          />

          {/* Question Cards */}
          {submission.answers.map((answer: ExamAnswer, index: number) => {
            const isCorrect = answer.is_correct === true;
            const isWrong = answer.is_correct === false;

            return (
              <Box
                key={answer.id}
                sx={{
                  position: 'relative',
                  pl: 7,
                  pb: 5,
                  animation: 'slideUpFade 0.5s ease-out forwards',
                  opacity: 0,
                  animationDelay: `${index * 0.1}s`,
                  '@keyframes slideUpFade': {
                    from: { opacity: 0, transform: 'translateY(20px)' },
                    to: { opacity: 1, transform: 'translateY(0)' },
                  },
                }}
              >
                {/* Timeline Node */}
                <Box
                  sx={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    backgroundColor: isCorrect
                      ? theme.palette.success.main
                      : isWrong
                        ? theme.palette.error.main
                        : theme.palette.grey[500],
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '1rem',
                    boxShadow: 2,
                    zIndex: 1,
                  }}
                >
                  {index + 1}
                </Box>

                {/* Question Card */}
                <Card
                  sx={{
                    border: `1px solid ${isCorrect
                      ? theme.palette.success.main
                      : isWrong
                        ? theme.palette.error.main
                        : theme.palette.divider
                    }`,
                    borderRadius: 2,
                    overflow: 'hidden',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      boxShadow: 4,
                      transform: 'translateX(4px)',
                    },
                  }}
                >
                  {/* Card Header */}
                  <Box
                    sx={{
                      p: 2,
                      backgroundColor: isCorrect
                        ? `${theme.palette.success.main}08`
                        : isWrong
                          ? `${theme.palette.error.main}08`
                          : 'action.hover',
                      borderBottom: `1px solid ${isCorrect
                        ? theme.palette.success.main
                        : isWrong
                          ? theme.palette.error.main
                          : theme.palette.divider
                      }`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      flexWrap: 'wrap',
                      gap: 1,
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Typography
                        variant="h6"
                        sx={{ fontWeight: 600 }}
                      >
                        {answer.problem_title}
                      </Typography>
                      <Chip
                        label={answer.problem_type === 'choice' ? '选择题' : '填空题'}
                        size="small"
                        variant="outlined"
                      />
                    </Box>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {answer.is_correct !== null && answer.is_correct !== undefined && (
                        <Chip
                          icon={answer.is_correct ? <CheckCircle /> : <Cancel />}
                          label={answer.is_correct ? '正确' : '错误'}
                          color={answer.is_correct ? 'success' : 'error'}
                          size="small"
                        />
                      )}
                      {answer.score !== undefined && answer.score !== null && (
                        <Typography
                          variant="body2"
                          sx={{
                                fontWeight: 600,
                                color: isCorrect
                                  ? theme.palette.success.main
                                  : isWrong
                                    ? theme.palette.error.main
                                    : theme.palette.text.secondary,
                              }}
                        >
                          {answer.score} 分
                        </Typography>
                      )}
                    </Box>
                  </Box>

                  {/* Card Content */}
                  <CardContent sx={{ pt: 3 }}>
                    {/* Question Content with MarkdownRenderer */}
                    {answer.problem_data?.content && (
                      <Box sx={{ mb: 3 }}>
                        <Typography
                          variant="subtitle2"
                          sx={{
                            color: theme.palette.text.secondary,
                            mb: 2,
                            fontWeight: 600,
                            display: 'flex',
                            alignItems: 'center',
                            gap: 1,
                          }}
                        >
                          <Quiz fontSize="small" />
                          题目内容
                        </Typography>
                        <Box
                          sx={{
                            p: 2,
                            borderRadius: 2,
                            backgroundColor: 'background.paper',
                            border: `1px solid ${theme.palette.divider}`,
                          }}
                        >
                          <MarkdownRenderer
                            markdownContent={answer.problem_data.content}
                          />
                        </Box>
                      </Box>
                    )}

                    <Divider sx={{ my: 3 }} />

                    {/* Answer Review */}
                    <Typography
                      variant="subtitle2"
                      sx={{
                        color: theme.palette.text.secondary,
                        mb: 2,
                        fontWeight: 600,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                      }}
                    >
                      答案解析
                    </Typography>

                    <AnswerReviewCard
                      problemType={answer.problem_type as 'choice' | 'fillblank'}
                      userAnswer={answer.choice_answers || answer.fillblank_answers}
                      correctAnswer={answer.correct_answer || { all_options: {}, correct_answer: [], blanks_list: [] }}
                      score={answer.score !== undefined ? parseFloat(answer.score) : undefined}
                      correctPercentage={answer.correct_percentage}
                      maxScore={answer?.problem_data?.score}
                    />
                  </CardContent>
                </Card>
              </Box>
            );
          })}

          {submission.answers.length === 0 && (
            <Alert severity="info">暂无题目详情。</Alert>
          )}
        </Box>
      </SectionContainer>
    </PageContainer>
  );
}
