import {
  Box,
  Typography,
  Button,
  Chip,
  Divider,
  Alert,
  CircularProgress,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ArrowBack,
  CheckCircle,
  Cancel,
  Schedule,
  ExpandMore,
  Check,
  Close,
} from '@mui/icons-material';
import type { ExamSubmission, ExamAnswer } from "~/types/course";
import type { Route } from "./+types/_layout.courses_.$courseId_.exams_.$examId_.results";
import { createHttp } from "~/utils/http/index.server";
import { Link } from 'react-router';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';

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

// Status chip configurations
const STATUS_CONFIG: Record<string, { color: 'success' | 'error' | 'warning' | 'default'; label: string }> = {
  graded: { color: 'success', label: '已评分' },
  submitted: { color: 'warning', label: '已提交' },
  auto_submitted: { color: 'warning', label: '自动提交(超时)' },
  in_progress: { color: 'default', label: '进行中' },
};

// Format time duration
function formatTime(seconds?: number): string {
  if (!seconds) return '--';
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secs = seconds % 60;

  if (hours > 0) {
    return `${hours}小时${minutes}分钟${secs}秒`;
  }
  if (minutes > 0) {
    return `${minutes}分钟${secs}秒`;
  }
  return `${secs}秒`;
}

// Component for displaying choice problem answer
function ChoiceAnswerDisplay({
  userAnswer,
  correctAnswer,
  allOptions,
}: {
  userAnswer: string | string[];
  correctAnswer: string | string[];
  allOptions?: Record<string, string>;
}) {
  const userAnswers = Array.isArray(userAnswer) ? userAnswer : [userAnswer];
  const correctAnswers = Array.isArray(correctAnswer) ? correctAnswer : [correctAnswer];

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        选项:
      </Typography>
      {allOptions && Object.entries(allOptions).map(([key, value]) => {
        const isSelected = userAnswers.includes(key);
        const isCorrect = correctAnswers.includes(key);
        const boxColor = isSelected && isCorrect ? 'success.main' :
                         isSelected && !isCorrect ? 'error.main' :
                         !isSelected && isCorrect ? 'warning.main' : 'transparent';

        return (
          <Box
            key={key}
            sx={{
              display: 'flex',
              alignItems: 'center',
              py: 0.5,
              px: 1,
              my: 0.5,
              border: 1,
              borderColor: boxColor === 'transparent' ? 'divider' : boxColor,
              borderRadius: 1,
              bgcolor: boxColor === 'transparent' ? 'transparent' : `${boxColor}.08`,
            }}
          >
            <Typography variant="body2" sx={{ flex: 1 }}>
              <strong>{key}.</strong> {value}
            </Typography>
            {isSelected && isCorrect && <Check color="success" fontSize="small" />}
            {isSelected && !isCorrect && <Close color="error" fontSize="small" />}
            {!isSelected && isCorrect && <Check color="warning" fontSize="small" />}
          </Box>
        );
      })}
    </Box>
  );
}

// Component for displaying fill-in-blank problem answer
function FillblankAnswerDisplay({
  userAnswer,
  blanksList,
  score,
  correctPercentage,
}: {
  userAnswer: Record<string, string>;
  blanksList: Array<{ answers: string[]; case_sensitive?: boolean }>;
  score?: number;
  correctPercentage?: number;
}) {
  const blankKeys = Object.keys(userAnswer).sort();

  return (
    <Box>
      <Typography variant="body2" color="text.secondary" gutterBottom>
        填空详情:
      </Typography>
      {blankKeys.map((key, index) => {
        const userVal = userAnswer[key];
        const blankInfo = blanksList[index];
        const correctVals = blankInfo?.answers || [];
        const caseSensitive = blankInfo?.case_sensitive || false;

        const isCorrect = caseSensitive
          ? correctVals.includes(userVal)
          : correctVals.some(v => v.toLowerCase() === userVal.toLowerCase());

        return (
          <Box
            key={key}
            sx={{
              display: 'flex',
              alignItems: 'center',
              py: 0.5,
              px: 1,
              my: 0.5,
              border: 1,
              borderColor: isCorrect ? 'success.main' : 'error.main',
              borderRadius: 1,
              bgcolor: isCorrect ? 'success.08' : 'error.08',
            }}
          >
            <Typography variant="body2" sx={{ minWidth: 80 }}>
              <strong>{key}:</strong>
            </Typography>
            <Typography variant="body2" sx={{ flex: 1 }}>
              你的答案: {userVal || '(未填)'}
            </Typography>
            {isCorrect ? (
              <Check color="success" fontSize="small" />
            ) : (
              <>
                <Close color="error" fontSize="small" />
                <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                  正确答案: {correctVals.join(' 或 ')}
                </Typography>
              </>
            )}
          </Box>
        );
      })}
      {correctPercentage !== undefined && correctPercentage < 100 && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          得分率: {correctPercentage.toFixed(1)}%
        </Typography>
      )}
    </Box>
  );
}

export default function ExamResultsPage({ loaderData, params }: Route.ComponentProps) {
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

  const statusConfig = STATUS_CONFIG[submission.status] || STATUS_CONFIG.in_progress;
  const scorePercentage = submission.exam_total_score
    ? ((submission.total_score || 0) / submission.exam_total_score) * 100
    : 0;

  return (
    <PageContainer maxWidth="lg">
      <PageHeader
        title={submission.exam_title}
        subtitle="测验结果"
        action={
          <Button
            startIcon={<ArrowBack />}
            component={Link}
            to={`/courses/${courseId}/exams`}
            variant="outlined"
          >
            返回测验列表
          </Button>
        }
      />

      {/* Summary Card */}
      <SectionContainer spacing="lg" variant="card">
        <Typography variant="h6" gutterBottom>
          测验概览
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3, mb: 2 }}>
          {/* Score */}
          <Box sx={{ minWidth: 200, flex: 1 }}>
            <Typography variant="body2" color="text.secondary">
              得分
            </Typography>
            <Typography variant="h4" color="primary">
              {submission.total_score ?? '--'} / {submission.exam_total_score ?? '--'}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              ({scorePercentage.toFixed(1)}%)
            </Typography>
          </Box>

          {/* Pass/Fail */}
          <Box sx={{ minWidth: 200, flex: 1 }}>
            <Typography variant="body2" color="text.secondary">
              结果
            </Typography>
            {submission.is_passed !== null && submission.is_passed !== undefined ? (
              <Chip
                icon={submission.is_passed ? <CheckCircle /> : <Cancel />}
                label={submission.is_passed ? '通过' : '未通过'}
                color={submission.is_passed ? 'success' : 'error'}
                sx={{ mt: 0.5 }}
              />
            ) : (
              <Typography variant="body1">--</Typography>
            )}
            {submission.exam_passing_score !== undefined && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                及格分: {submission.exam_passing_score}
              </Typography>
            )}
          </Box>

          {/* Status */}
          <Box sx={{ minWidth: 200, flex: 1 }}>
            <Typography variant="body2" color="text.secondary">
              状态
            </Typography>
            <Chip
              label={statusConfig.label}
              color={statusConfig.color}
              sx={{ mt: 0.5 }}
            />
          </Box>

          {/* Time Spent */}
          <Box sx={{ minWidth: 200, flex: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              用时
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Schedule color="action" fontSize="small" />
              <Typography variant="body1">
                {formatTime(submission.time_spent_seconds)}
              </Typography>
            </Box>
          </Box>
        </Box>

        {submission.status === 'auto_submitted' && (
          <Alert severity="warning" sx={{ mt: 2 }}>
            您的测验因超时被自动提交。
          </Alert>
        )}
      </SectionContainer>

      {/* Questions List */}
      <SectionContainer spacing="lg" variant="card">
        <Typography variant="h6" gutterBottom>
          题目详情
        </Typography>
        <Divider sx={{ mb: 3 }} />

        {submission.answers.map((answer: ExamAnswer, index: number) => (
          <Accordion key={answer.id} defaultExpanded={index === 0}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 2 }}>
                <Typography variant="body1" sx={{ minWidth: 40 }}>
                  {index + 1}.
                </Typography>
                <Typography variant="subtitle1" sx={{ flex: 1 }}>
                  {answer.problem_title}
                </Typography>
                <Chip
                  label={answer.problem_type === 'choice' ? '选择题' : '填空题'}
                  size="small"
                  variant="outlined"
                />
                {answer.is_correct !== null && answer.is_correct !== undefined && (
                  <Chip
                    icon={answer.is_correct ? <CheckCircle /> : <Cancel />}
                    label={answer.is_correct ? '正确' : '错误'}
                    color={answer.is_correct ? 'success' : 'error'}
                    size="small"
                  />
                )}
                {answer.score !== undefined && answer.score !== null && (
                  <Typography variant="body2" color="text.secondary" sx={{ minWidth: 80, textAlign: 'right' }}>
                    {answer.score} 分
                  </Typography>
                )}
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Box sx={{ pl: 5 }}>
                {/* Problem Content */}
                {answer.problem_data?.content && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      题目内容:
                    </Typography>
                    <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                      {answer.problem_data.content}
                    </Typography>
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Answer Display by Type */}
                {answer.problem_type === 'choice' && answer.correct_answer?.all_options && (
                  <ChoiceAnswerDisplay
                    userAnswer={answer.choice_answers || []}
                    correctAnswer={answer.correct_answer.correct_answer || []}
                    allOptions={answer.correct_answer.all_options}
                  />
                )}

                {answer.problem_type === 'fillblank' && answer.fillblank_answers && answer.correct_answer?.blanks_list && (
                  <FillblankAnswerDisplay
                    userAnswer={answer.fillblank_answers}
                    blanksList={answer.correct_answer.blanks_list}
                    score={answer.score}
                    correctPercentage={answer.correct_percentage}
                  />
                )}
              </Box>
            </AccordionDetails>
          </Accordion>
        ))}

        {submission.answers.length === 0 && (
          <Alert severity="info">暂无题目详情。</Alert>
        )}
      </SectionContainer>
    </PageContainer>
  );
}
