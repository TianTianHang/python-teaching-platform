import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  AlertTitle,
  Chip,
  TextField,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  Checkbox,
  Divider,
} from '@mui/material';
import { ArrowBack, Timer, Save, ArrowForward, Quiz, AccessTime } from '@mui/icons-material';
import type { Exam, ExamProblem, ExamSubmission } from "~/types/course";
import type { Route } from "./+types/_layout.courses_.$courseId_.exams_.$examId";
import { createHttp } from "~/utils/http/index.server";
import { useNavigate } from 'react-router';
import { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import useFetcherAction from '~/hooks/useFetcherAction';
import MarkdownRenderer from '~/components/MarkdownRenderer';
import { formatTitle, PAGE_TITLES } from '~/config/meta';

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
  const exam = loaderData?.exam;
  const pageTitle = exam?.title ? PAGE_TITLES.exam(exam.title) : '测验';

  // Validate path parameters to prevent injection
  const courseId = Number(params.courseId);
  const examId = Number(params.examId);
  if (isNaN(courseId) || isNaN(examId) || courseId <= 0 || examId <= 0) {
    return (
      <>
        <title>{formatTitle('错误')}</title>
        <PageContainer maxWidth="md">
          <SectionContainer spacing="lg" variant="card">
          <Alert severity="error">
            无效的课程或测验ID。
          </Alert>
        </SectionContainer>
      </PageContainer>
      </>
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
    <>
      <title>{formatTitle(pageTitle)}</title>
      <PageContainer maxWidth="md">
        <PageHeader
          title="测验"
          subtitle={exam.title}
        />

      <SectionContainer spacing="md" variant="card">
        {/* Exam Header with Enhanced Timer */}
        <Card sx={{
          position: 'relative',
          overflow: 'hidden',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: 4,
            background: timeRemaining !== null && timeRemaining < 300
              ? 'linear-gradient(90deg, error.main 0%, error.light 100%)'
              : 'linear-gradient(90deg, primary.main 0%, primary.light 100%)',
            animation: timeRemaining !== null && timeRemaining < 300 ? 'pulse 2s ease-in-out infinite' : 'none',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.7 },
            },
          },
        }}>
          <CardContent sx={{ pb: 2 }}>
            {/* Title Row with Timer */}
            <Box sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 2,
              flexWrap: 'wrap',
              gap: 2,
            }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  color: 'text.primary',
                  flex: 1,
                  minWidth: 200,
                }}
              >
                {exam.title}
              </Typography>

              {timeRemaining !== null && (
                <Card
                  sx={{
                    backgroundColor: timeRemaining < 300 ? 'error.main' : 'primary.main',
                    color: 'primary.contrastText',
                    borderRadius: 2,
                    px: 3,
                    py: 1.5,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1.5,
                    boxShadow: timeRemaining < 300 ? 4 : 2,
                    animation: timeRemaining < 300 ? 'pulse 1s ease-in-out infinite' : 'none',
                    '@keyframes pulse': {
                      '0%, 100%': { opacity: 1 },
                      '50%': { opacity: 0.7 },
                    },
                  }}
                >
                  <Timer sx={{ fontSize: 24 }} />
                  <Box>
                    <Typography variant="caption" sx={{ opacity: 0.9, display: 'block', lineHeight: 1 }}>
                      剩余时间
                    </Typography>
                    <Typography
                      variant="h4"
                      sx={{
                        fontWeight: 700,
                        lineHeight: 1.2,
                        fontFamily: 'monospace',
                      }}
                    >
                      {formattedTime}
                    </Typography>
                  </Box>
                </Card>
              )}
            </Box>

            {/* Description */}
            {exam.description && (
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, lineHeight: 1.6 }}>
                {exam.description}
              </Typography>
            )}

            {/* Exam Info Chips */}
            <Box sx={{ display: 'flex', gap: 1.5, mb: 2, flexWrap: 'wrap' }}>
              <Chip
                label={`${exam.question_count} 题`}
                size="small"
                icon={<Quiz fontSize="small" />}
              />
              <Chip
                label={`总分 ${exam.total_score}`}
                size="small"
                color="primary"
                variant="outlined"
              />
              <Chip
                label={`及格 ${exam.passing_score}`}
                size="small"
                color={exam.passing_score / exam.total_score > 0.6 ? 'success' : 'warning'}
                variant="outlined"
              />
              {exam.duration_minutes > 0 && (
                <Chip
                  label={`${exam.duration_minutes} 分钟`}
                  size="small"
                  icon={<AccessTime fontSize="small" />}
                />
              )}
            </Box>

            {/* Error Alert */}
            {submitError && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {submitError}
              </Alert>
            )}
          </CardContent>
        </Card>

        {/* Enhanced Progress Bar */}
        {exam.exam_problems && exam.exam_problems.length > 0 && (
          <Card sx={{ mb: 3, overflow: 'hidden' }}>
            <CardContent sx={{ pb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle2" color="text.secondary">
                  答题进度
                </Typography>
                <Typography variant="subtitle2" color="text.secondary" sx={{ fontWeight: 600 }}>
                  {Object.keys(answers).length} / {exam.exam_problems.length}
                </Typography>
              </Box>
              <Box sx={{ position: 'relative', height: 12, backgroundColor: 'action.hover', borderRadius: 6, overflow: 'hidden' }}>
                <Box
                  sx={{
                    position: 'absolute',
                    left: 0,
                    top: 0,
                    height: '100%',
                    width: `${Object.keys(answers).length / exam.exam_problems.length * 100}%`,
                    background: 'linear-gradient(90deg, primary.main 0%, primary.light 100%)',
                    transition: 'width 0.5s ease-in-out',
                    borderRadius: 6,
                  }}
                />
              </Box>
              <Typography variant="caption" color="text.disabled" sx={{ mt: 1, display: 'block' }}>
                已完成 {Math.round(Object.keys(answers).length / exam.exam_problems.length * 100)}%
              </Typography>
            </CardContent>
          </Card>
        )}

        {/* Question Navigation Grid */}
        {exam.exam_problems && exam.exam_problems.length > 0 && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 2 }}>
                题目导航
              </Typography>
              <Box sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(48px, 1fr))',
                gap: 1.5,
              }}>
                {exam.exam_problems.map((problem: ExamProblem, index: number) => {
                  const isAnswered = Object.prototype.hasOwnProperty.call(answers, problem.problem_id);
                  const isCurrent = currentStep === index;

                  return (
                    <Button
                      key={problem.problem_id}
                      variant={isCurrent ? "contained" : isAnswered ? "outlined" : "text"}
                      onClick={() => setCurrentStep(index)}
                      sx={{
                        minWidth: 48,
                        height: 48,
                        p: 0,
                        fontSize: '1rem',
                        fontWeight: 600,
                        borderRadius: 2,
                        backgroundColor: isCurrent ? 'primary.main' : isAnswered ? 'primary.light' : 'action.hover',
                        color: isCurrent ? 'primary.contrastText' : isAnswered ? 'primary.contrastText' : 'text.primary',
                        border: isAnswered && !isCurrent ? `2px solid` : 'none',
                        borderColor: isAnswered && !isCurrent ? 'primary.main' : 'transparent',
                        '&:hover': {
                          backgroundColor: isCurrent ? 'primary.dark' : 'primary.light',
                          transform: 'scale(1.02)',
                        },
                        transition: 'all 0.2s ease-in-out',
                      }}
                    >
                      {index + 1}
                    </Button>
                  );
                })}
              </Box>

              {/* Legend */}
              <Box sx={{ display: 'flex', gap: 2, mt: 2, flexWrap: 'wrap' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: 1, backgroundColor: 'primary.main' }} />
                  <Typography variant="caption" color="text.secondary">当前</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: 1, border: '2px solid', borderColor: 'primary.main' }} />
                  <Typography variant="caption" color="text.secondary">已答</Typography>
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                  <Box sx={{ width: 16, height: 16, borderRadius: 1, backgroundColor: 'action.hover' }} />
                  <Typography variant="caption" color="text.secondary">未答</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}

        {/* 题目内容 */}
        {exam.exam_problems[currentStep] && (
          <Card
            sx={{
              position: 'relative',
              overflow: 'visible',
              '&::before': {
                content: '""',
                position: 'absolute',
                top: 0,
                left: 0,
                right: 0,
                height: 4,
                background: 'linear-gradient(90deg, primary.main 0%, primary.light 100%)',
              },
            }}
          >
            <CardContent sx={{ pt: 4 }}>
              {/* Question Header with Number Badge */}
              <Box sx={{ display: 'flex', alignItems: 'flex-start', gap: 2, mb: 3 }}>
                <Box sx={{
                  flexShrink: 0,
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  typography: 'h5',
                  fontWeight: 700,
                  boxShadow: 2,
                }}>
                  {currentStep + 1}
                </Box>

                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 600,
                      color: 'text.primary',
                      mb: 1
                    }}
                  >
                    {exam.exam_problems[currentStep].title}
                  </Typography>

                  {/* Question Metadata */}
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip
                      label={`${exam.exam_problems[currentStep].score} 分`}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                    <Chip
                      label={exam.exam_problems[currentStep].type === 'choice'
                        ? (exam.exam_problems[currentStep].is_multiple_choice ? '多选题' : '单选题')
                        : '填空题'
                      }
                      size="small"
                    />
                    {exam.exam_problems[currentStep].difficulty > 0 && (
                      <Chip
                        label={`难度: ${'★'.repeat(exam.exam_problems[currentStep].difficulty)}`}
                        size="small"
                        color={exam.exam_problems[currentStep].difficulty >= 3 ? 'error' : 'default'}
                      />
                    )}
                  </Box>
                </Box>
              </Box>

              {/* Markdown Question Content */}
              <Box sx={{
                backgroundColor: 'background.paper',
                borderRadius: 2,
                p: 3,
                borderLeft: `4px solid`,
                borderColor: 'primary.main',
                boxShadow: 1,
                mb: 3,
              }}>
                <MarkdownRenderer
                  markdownContent={exam.exam_problems[currentStep].content}
                />
              </Box>

              <Divider sx={{ my: 3 }} />

              {/* Answer Input Section */}
              {exam.exam_problems[currentStep].type === 'choice' && (
                <FormControl fullWidth>
                  <Typography
                    variant="subtitle1"
                    sx={{
                      fontWeight: 600,
                      mb: 2,
                      color: 'text.primary'
                    }}
                  >
                    请选择答案
                    {exam.exam_problems[currentStep].is_multiple_choice && (
                      <Typography
                        component="span"
                        variant="caption"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        (可多选)
                      </Typography>
                    )}
                  </Typography>

                  <RadioGroup
                    value={(answers[exam.exam_problems[currentStep].problem_id] as string | string[]) || (exam.exam_problems[currentStep].is_multiple_choice ? [] : '')}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                      const problemId = exam.exam_problems[currentStep].problem_id;
                      const value = e.target.value;
                      const isMultiple = exam.exam_problems[currentStep].is_multiple_choice;

                      if (isMultiple) {
                        const currentAnswers = (answers[problemId] as string[]) || [];
                        const newAnswers = currentAnswers.includes(value)
                          ? currentAnswers.filter(a => a !== value)
                          : [...currentAnswers, value];
                        handleChoiceAnswer(problemId, newAnswers);
                      } else {
                        handleChoiceAnswer(problemId, value);
                      }
                    }}
                  >
                    {Object.entries((exam.exam_problems[currentStep]).options || {}).map(([key, value]) => {
                      const isSelected = exam.exam_problems[currentStep].is_multiple_choice
                        ? (answers[exam.exam_problems[currentStep].problem_id] as string[] || []).includes(key)
                        : answers[exam.exam_problems[currentStep].problem_id] === key;

                      return (
                        <Card
                          key={key}
                          sx={{
                            mb: 1.5,
                            border: `2px solid`,
                            borderColor: isSelected ? 'primary.main' : 'divider',
                            borderRadius: 2,
                            transition: 'all 0.2s ease-in-out',
                            cursor: 'pointer',
                            '&:hover': {
                              borderColor: 'primary.light',
                              transform: 'translateX(4px)',
                            },
                          }}
                          onClick={() => {
                            const input = document.getElementById(`choice-${key}`) as HTMLInputElement;
                            if (input) input.click();
                          }}
                        >
                          <CardContent sx={{ py: 2, px: 2.5 }}>
                            <FormControlLabel
                              value={key}
                              control={
                                exam.exam_problems[currentStep].is_multiple_choice ? (
                                  <Checkbox
                                    id={`choice-${key}`}
                                    checked={isSelected}
                                  />
                                ) : (
                                  <Radio
                                    id={`choice-${key}`}
                                    checked={isSelected}
                                  />
                                )
                              }
                              label={
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <Typography
                                    sx={{
                                      fontWeight: 600,
                                      color: 'primary.main',
                                      minWidth: 24,
                                    }}
                                  >
                                    {key}.
                                  </Typography>
                                  <Typography variant="body1">
                                    {String(value)}
                                  </Typography>
                                </Box>
                              }
                              sx={{ margin: 0, width: '100%' }}
                            />
                          </CardContent>
                        </Card>
                      );
                    })}
                  </RadioGroup>
                </FormControl>
              )}

              {exam.exam_problems[currentStep].type === 'fillblank' && (
                <Box>
                  <Typography
                    variant="subtitle1"
                    sx={{
                      fontWeight: 600,
                      mb: 3,
                      color: 'text.primary'
                    }}
                  >
                    请填写答案
                  </Typography>

                  {Object.entries(answers[exam.exam_problems[currentStep].problem_id] || {}).map(([blankId, value]: [string, string], index: number) => (
                    <Box
                      key={blankId}
                      sx={{
                        mb: 3,
                        p: 2,
                        backgroundColor: 'action.hover',
                        borderRadius: 2,
                        borderLeft: `4px solid`,
                        borderColor: 'primary.main',
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        sx={{
                          mb: 2,
                          fontWeight: 600,
                          color: 'text.secondary',
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1
                        }}
                      >
                        <Box sx={{
                          width: 24,
                          height: 24,
                          borderRadius: '50%',
                          backgroundColor: 'primary.main',
                          color: 'primary.contrastText',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                        }}>
                          {index + 1}
                        </Box>
                        {blankId}
                      </Typography>
                      <TextField
                        fullWidth
                        label={`请输入 ${blankId} 的答案`}
                        value={value || ''}
                        onChange={(e) => handleFillBlankAnswer(
                          exam.exam_problems[currentStep].problem_id,
                          blankId,
                          e.target.value
                        )}
                        variant="outlined"
                        sx={{
                          '& .MuiOutlinedInput-root': {
                            '&.Mui-focused fieldset': {
                              borderColor: 'primary.main',
                              borderWidth: 2,
                            },
                          },
                        }}
                      />
                    </Box>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        )}

        {/* Enhanced Navigation Buttons */}
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mt: 4,
          pt: 3,
          borderTop: 1,
          borderColor: 'divider',
          flexWrap: 'wrap',
          gap: 2,
        }}>
          {/* Back Button */}
          <Button
            startIcon={<ArrowBack />}
            onClick={handleGoBack}
            variant="outlined"
            sx={{
              minWidth: 120,
              borderRadius: 2,
            }}
          >
            退出测验
          </Button>

          {/* Navigation Actions */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="outlined"
              onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
              disabled={currentStep === 0}
              sx={{
                minWidth: 100,
                borderRadius: 2,
              }}
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
              sx={{
                minWidth: 120,
                borderRadius: 2,
                fontWeight: 600,
                background: 'linear-gradient(135deg, primary.main 0%, primary.dark 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, primary.dark 0%, primary.main 100%)',
                },
                '&:disabled': {
                  background: 'action.disabledBackground',
                },
              }}
            >
              {fetcherSubmit.isSubmitting ? '提交中...' : (exam.exam_problems && currentStep === exam.exam_problems.length - 1 ? '提交测验' : '下一题')}
            </Button>
          </Box>
        </Box>
      </SectionContainer>
    </PageContainer>
    </>
  );
}