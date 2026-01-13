import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  LinearProgress,
  Alert,
  AlertTitle,
  Chip,
  Stepper,
  Step,
  StepLabel,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { ArrowBack, Timer, Save, ArrowForward } from '@mui/icons-material';
import type { Exam, ExamProblem, ExamSubmission } from "~/types/course";
import type { Route } from "./+types/_layout.courses_.$courseId_.exams_.$examId";
import type { SelectChangeEvent } from "@mui/material";
import { createHttp } from "~/utils/http/index.server";
import { useNavigate } from 'react-router';
import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import useFetcherAction from '~/hooks/useFetcherAction';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: `${loaderData?.exam.title} - 测验` },
  ];
}

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
 
  const exam = await http.get<Exam>(`/exams/${params.examId}`);

  const submission = await http.post<{ submission_id: string; remaining_time: { remaining_seconds: number; deadline: string } } | null>(
    `/exams/${params.examId}/start/`
  );
  return { exam, submission };

});

export const action = withAuth(async ({ params, request }: Route.ActionArgs) => {
  const http = createHttp(request);
  const formData = await request.json();

  const TIMEOUT = 25000; // Server-side timeout (less than client timeout)

  const result = await Promise.race([
    http.post<ExamSubmission>(`/exams/${params.examId}/submit/`, formData),
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error('TIMEOUT')), TIMEOUT)
    )
  ]);

  return { submission: result };
});

// Type for user's working answers (different from server-side ExamAnswer type)
type UserExamAnswer = string | string[] | Record<string, string>;

// Type for submission answers
interface ExamAnswerForSubmission {
  problem_id: number;
  problem_type: string;
  choice_answers?: string[];
  fillblank_answers?: Record<string, string>;
  [key: string]: unknown; // Index signature for JSON serialization
}

// Constants
const EXAM_CONFIG = {
  TIME_FORMAT: 'HH:MM:SS',
  SUBMIT_TIMEOUT: 30000,
  SYNC_INTERVAL: 60000,
  AUTO_REDIRECT_DELAY: 1500,
} as const;

const ERROR_MESSAGES = {
  NETWORK_DISCONNECTED: '网络连接已断开，请检查您的网络连接',
  SESSION_EXPIRED: '会话已过期，请重新登录',
  NO_PERMISSION: '没有权限执行此操作',
  EXAM_NOT_FOUND: '测验不存在或已被删除',
  SUBMIT_TOO_FREQUENT: '提交过于频繁，请稍后再试',
  DATA_INCOMPLETE: '测验数据不完整',
  ANSWERS_REQUIRED: '请完成所有题目后再提交',
  SUBMIT_FAILED: '提交失败，请重试',
  TIMEOUT: '请求超时，请重试',
} as const;

export default function ExamTakingPage({ loaderData, params }: Route.ComponentProps) {
  const navigate = useNavigate();

  // Validate path parameters to prevent injection
  const courseId = Number(params.courseId);
  const examId = Number(params.examId);
  if (isNaN(courseId) || isNaN(examId) || courseId <= 0 || examId <= 0) {
    return (
      <PageContainer maxWidth="md">
        <SectionContainer spacing="lg" variant="card">
          <Alert severity="error">
            无效的课程或测验ID。
          </Alert>
        </SectionContainer>
      </PageContainer>
    );
  }

  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<number, UserExamAnswer>>({});
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Initialize the fetcher hook for exam submission
  const fetcherSubmit = useFetcherAction<{ submission: ExamSubmission }, string>({
    action: `/courses/${courseId}/exams/${examId}`,
    method: 'POST',
    timeout: EXAM_CONFIG.SUBMIT_TIMEOUT,
    onSuccess: () => {
      setIsSubmitted(true);
      setSubmitError(null);
      // Redirect to results after a short delay
      setTimeout(() => {
        navigate(`/courses/${courseId}/exams`);
      }, EXAM_CONFIG.AUTO_REDIRECT_DELAY);
    },
    onError: (errorMsg) => {
      setSubmitError(errorMsg);
    },
    errorMessages: ERROR_MESSAGES,
    // Check if response contains error (for HTTP errors from backend)
    isErrorResponse: (data) => {
      return typeof data === 'object' && data !== null && 'detail' in data && data.detail !== null;
    },
    getErrorMessage: (data) => {
      return (data as { detail?: string })?.detail || ERROR_MESSAGES.SUBMIT_FAILED;
    },
  });

  const exam = loaderData.exam;
  const submission = loaderData.submission;

  // Utility function to format time as HH:MM:SS
  const formatTime = useCallback((seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  // Memoized formatted time display
  const formattedTime = useMemo(() => {
    return timeRemaining !== null ? formatTime(timeRemaining) : '';
  }, [timeRemaining, formatTime]);

  // Utility function to map answers for submission
  const mapAnswersForSubmission = useCallback((
    examProblems: ExamProblem[],
    answersData: Record<number, UserExamAnswer>
  ): ExamAnswerForSubmission[] => {
    return examProblems.map((problem: ExamProblem) => ({
      problem_id: problem.problem_id,
      problem_type: problem.type,
      ...(problem.type === 'choice' ? {
        choice_answers: (answersData[problem.problem_id] || []) as string[]
      } : {
        fillblank_answers: (answersData[problem.problem_id] || {}) as Record<string, string>
      })
    }));
  }, []);

  // Initialize answers
  useEffect(() => {
    if (exam && exam.exam_problems) {
      const initialAnswers: Record<number, UserExamAnswer> = {};
      console.log('Initializing answers for exam problems:', exam);
      exam.exam_problems.forEach(problem => {
        if (problem.type === 'choice') {
          initialAnswers[problem.problem_id] = [];
        } else if (problem.type === 'fillblank') {
          initialAnswers[problem.problem_id] = {};
        }
      });
      setAnswers(initialAnswers);
    }
  }, [exam]);

  // Handle connection errors and network issues
  useEffect(() => {
    const handleOnline = () => {
      setSubmitError(null);
    };

    const handleOffline = () => {
      setSubmitError(ERROR_MESSAGES.NETWORK_DISCONNECTED);
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  const handleSubmit = useCallback(() => {
    if (isSubmitted) return;

    // Check network connectivity
    if (!navigator.onLine) {
      setSubmitError(ERROR_MESSAGES.NETWORK_DISCONNECTED);
      return;
    }

    if (!exam?.exam_problems) {
      setSubmitError(ERROR_MESSAGES.DATA_INCOMPLETE);
      return;
    }

    // Validate all answers are provided
    const hasAllAnswers = exam.exam_problems.every(problem =>
      Object.prototype.hasOwnProperty.call(answers, problem.problem_id)
    );
    if (!hasAllAnswers) {
      setSubmitError(ERROR_MESSAGES.ANSWERS_REQUIRED);
      return;
    }

    // Submit using fetcher hook
    const answersArray = mapAnswersForSubmission(exam.exam_problems, answers);
    fetcherSubmit.submit({ answers: answersArray });
  }, [isSubmitted, exam, answers, fetcherSubmit, mapAnswersForSubmission]);

  // Set up timer if there's an active submission
  useEffect(() => {
    if (!submission?.remaining_time?.remaining_seconds) return;

    const initialTime = submission.remaining_time.remaining_seconds;
    setTimeRemaining(initialTime);

    // Check if exam has already expired
    if (initialTime <= 0) {
      handleSubmit();
      return;
    }

    timerRef.current = setInterval(() => {
      setTimeRemaining(prev => {
        if (!prev) return 0;
        const newTime = prev - 1;

        // Auto-submit when time runs out
        if (newTime <= 0 && Object.keys(answers).length > 0) {
          handleSubmit();
          return 0;
        }

        return newTime;
      });
    }, 1000);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [submission, answers, handleSubmit]);

  // Sync time with server periodically to prevent client-side manipulation
  useEffect(() => {
    if (!submission?.remaining_time?.remaining_seconds || isSubmitted) return;

    const syncInterval = setInterval(() => {
      // This would ideally make an API call to get the remaining time
      // For now, we'll just continue with the client-side timer
      // but with a more stable approach
    }, EXAM_CONFIG.SYNC_INTERVAL);

    return () => {
      clearInterval(syncInterval);
    };
  }, [submission?.remaining_time?.remaining_seconds, isSubmitted]);

  const handleGoBack = useCallback(() => {
    if (confirm('确定要退出测验吗？未保存的进度将丢失。')) {
      navigate(`/courses/${courseId}/exams`);
    }
  }, [courseId, navigate]);

  const handleChoiceAnswer = useCallback((problemId: number, value: string | string[]) => {
    setAnswers(prev => ({
      ...prev,
      [problemId]: value
    }));
  }, []);

  const handleFillBlankAnswer = useCallback((problemId: number, blankId: string, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [problemId]: {
        ...(prev[problemId] as Record<string, string>),
        [blankId]: value
      }
    }));
  }, []);

  if (isSubmitted) {
    return (
      <PageContainer maxWidth="md">
        <SectionContainer spacing="lg" variant="card">
          <Box sx={{ textAlign: 'center', py: spacing.xl }}>
            <Alert severity="success" sx={{ mb: 3 }}>
              <AlertTitle>测验已提交</AlertTitle>
              正在跳转到结果页面...
            </Alert>
          </Box>
        </SectionContainer>
      </PageContainer>
    );
  }

  if (!exam) {
    return (
      <PageContainer maxWidth="md">
        <SectionContainer spacing="lg" variant="card">
          <Alert severity="error">
            测验不存在或加载失败。
          </Alert>
        </SectionContainer>
      </PageContainer>
    );
  }

  return (
    <PageContainer maxWidth="md">
      <PageHeader
        title="测验"
        subtitle={exam.title}
      />

      <SectionContainer spacing="md" variant="card">
        {/* 测验头部信息 */}
        <Card>
          <CardContent sx={{ pb: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {exam.title}
              </Typography>
              {timeRemaining !== null && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Timer color={timeRemaining < 300 ? 'error' : 'primary'} />
                  <Typography
                    variant="body2"
                    sx={{
                      color: timeRemaining < 300 ? 'error.main' : 'text.primary',
                      fontWeight: 500
                    }}
                  >
                    {formattedTime}
                  </Typography>
                </Box>
              )}
            </Box>

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              {exam.description}
            </Typography>

            <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
              <Chip label={`题目数：${exam.question_count}`} size="small" />
              <Chip label={`总分：${exam.total_score}`} size="small" />
              <Chip label={`及格分：${exam.passing_score}`} size="small" />
              {exam.duration_minutes > 0 && (
                <Chip label={`时限：${exam.duration_minutes}分钟`} size="small" />
              )}
            </Box>

            {submitError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {submitError}
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* 进度条 */}
        {exam.exam_problems && exam.exam_problems.length > 0 && (
          <LinearProgress
            variant="determinate"
            value={Object.keys(answers).length / exam.exam_problems.length * 100}
            sx={{ mb: 3, height: 8 }}
          />
        )}

        {/* 题目导航 */}
        {exam.exam_problems && exam.exam_problems.length > 0 && (
          <Stepper
            activeStep={currentStep}
            sx={{ mb: 3 }}
            orientation="horizontal"
            alternativeLabel
          >
            {exam.exam_problems.map((problem: ExamProblem, index: number) => (
              <Step key={problem.problem_id}>
                <StepLabel optional={
                  <Typography variant="caption" color="text.secondary">
                    {problem.score}分
                  </Typography>
                }>
                  <Button
                    variant={currentStep === index ? "contained" : "outlined"}
                    size="small"
                    onClick={() => setCurrentStep(index)}
                    sx={{ minWidth: 40 }}
                  >
                    {index + 1}
                  </Button>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        )}

        {/* 题目内容 */}
        {exam.exam_problems[currentStep] && (
          <Card>
            <CardContent>
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  {exam.exam_problems[currentStep].title}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-line',
                    lineHeight: 1.6,
                    mb: 3,
                    color: 'text.primary'
                  }}
                >
                  {exam.exam_problems[currentStep].content}
                </Typography>

                {exam.exam_problems[currentStep].type === 'choice' && (
                  <FormControl fullWidth>
                    <InputLabel id={`choice-${exam.exam_problems[currentStep].problem_id}-label`}>
                      选择答案
                    </InputLabel>
                    <Select
                      labelId={`choice-${exam.exam_problems[currentStep].problem_id}-label`}
                      value={(answers[exam.exam_problems[currentStep].problem_id] as string | string[]) || (exam.exam_problems[currentStep].is_multiple_choice ? [] : '')}
                      multiple={exam.exam_problems[currentStep].is_multiple_choice}
                      onChange={(e: SelectChangeEvent<string | string[]>) => handleChoiceAnswer(
                        exam.exam_problems[currentStep].problem_id,
                        e.target.value
                      )}
                      sx={{ mt: 2 }}
                    >
                      {Object.entries((exam.exam_problems[currentStep]).options || {}).map(([key, value]) => (
                        <MenuItem key={key} value={key}>
                          {key}. {String(value)}
                        </MenuItem>
                      ))}
                    </Select>
                    {exam.exam_problems[currentStep].is_multiple_choice && (
                      <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
                        多选题，可选择多个答案
                      </Typography>
                    )}
                  </FormControl>
                )}

                {exam.exam_problems[currentStep].type === 'fillblank' && (
                  <Box sx={{ mt: 2 }}>
                    {Object.entries(answers[exam.exam_problems[currentStep].problem_id] || {}).map(([blankId, value]: [string, string]) => (
                      <Box key={blankId} sx={{ mb: 2 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                          {blankId}
                        </Typography>
                        <TextField
                          fullWidth
                          label={`请输入${blankId}的答案`}
                          value={value || ''}
                          onChange={(e) => handleFillBlankAnswer(
                            exam.exam_problems[currentStep].problem_id,
                            blankId,
                            e.target.value
                          )}
                        />
                      </Box>
                    ))}
                  </Box>
                )}
              </Box>
            </CardContent>
          </Card>
        )}

        {/* 导航按钮 */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
          <Button
            startIcon={<ArrowBack />}
            onClick={handleGoBack}
            variant="outlined"
          >
            退出测验
          </Button>

          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
              disabled={currentStep === 0}
            >
              上一题
            </Button>

            <Button
              variant="contained"
              onClick={() => {
                if (exam.exam_problems && currentStep < exam.exam_problems.length - 1) {
                  setCurrentStep(prev => prev + 1);
                } else {
                  handleSubmit();
                }
              }}
              endIcon={exam.exam_problems && currentStep === exam.exam_problems.length - 1 ? <Save /> : <ArrowForward />}
              disabled={exam.exam_problems?.[currentStep]?.problem_id === undefined || Object.prototype.hasOwnProperty.call(answers, exam.exam_problems[currentStep].problem_id) === false}
            >
              {fetcherSubmit.isSubmitting ? '提交中...' : (exam.exam_problems && currentStep === exam.exam_problems.length - 1 ? '提交测验' : '下一题')}
            </Button>
          </Box>
        </Box>
      </SectionContainer>
    </PageContainer>
  );
}