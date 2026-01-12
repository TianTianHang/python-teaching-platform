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
import type { Exam, ExamSubmission } from "~/types/course";
import type { Route } from "./+types/route";
import { createHttp } from "~/utils/http/index.server";
import { useNavigate, useSubmit } from 'react-router';
import { useState, useEffect, useRef } from 'react';
import { withAuth } from '~/utils/loaderWrapper';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: `${loaderData?.exam.title} - 测验` },
  ];
}

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
  const exam = await http.get<Exam>(`/exams/${params.examId}`);
  const submission = await http.get<{ submission_id: string; remaining_time: { remaining_seconds: number; deadline: string } } | null>(
    `/exams/${params.examId}/start/`,
    { method: 'POST' }
  );
  return { exam, submission };
});

export const action = withAuth(async ({ params, request }: Route.ActionArgs) => {
  const http = createHttp(request);
  const formData = await request.json();

  const submission = await http.post<ExamSubmission>(
    `/exams/${params.examId}/submit/`,
    formData
  );

  return { submission };
});

export default function ExamTakingPage({ loaderData, params }: Route.ComponentProps) {
  const navigate = useNavigate();
  const submit = useSubmit();
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<number, any>>({});
  const [timeRemaining, setTimeRemaining] = useState<number | null>(null);
  const timerRef = useRef<NodeJS.Timeout>();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const exam = loaderData.exam;
  const submission = loaderData.submission;

  // Initialize answers
  useEffect(() => {
    if (exam && exam.exam_problems) {
      const initialAnswers: Record<number, any> = {};
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

  // Set up timer if there's an active submission
  useEffect(() => {
    if (submission?.remaining_time?.remaining_seconds) {
      setTimeRemaining(submission.remaining_time.remaining_seconds);

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
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [submission, answers]);

  const handleGoBack = () => {
    if (confirm('确定要退出测验吗？未保存的进度将丢失。')) {
      navigate(`/courses/${params.courseId}/exams`);
    }
  };

  const handleChoiceAnswer = (problemId: number, value: string | string[]) => {
    setAnswers(prev => ({
      ...prev,
      [problemId]: value
    }));
  };

  const handleFillBlankAnswer = (problemId: number, blankId: string, value: string) => {
    setAnswers(prev => ({
      ...prev,
      [problemId]: {
        ...prev[problemId],
        [blankId]: value
      }
    }));
  };

  const handleSubmit = async () => {
    if (isSubmitted) return;

    try {
      const answersArray = exam?.exam_problems.map((problem: any) => ({
        problem_id: problem.problem_id,
        problem_type: problem.type,
        ...(problem.type === 'choice' ? {
          choice_answers: answers[problem.problem_id] || []
        } : {
          fillblank_answers: answers[problem.problem_id] || {}
        })
      })) || [];

      const formData = { answers: answersArray };

      submit(formData, {
        method: 'post',
        action: `/courses/${params.courseId}/exams/${params.examId}`,
      });

      setIsSubmitted(true);
      setSubmitError(null);

      // Redirect to results after a short delay
      setTimeout(() => {
        navigate(`/courses/${params.courseId}/exams/${params.examId}/results`);
      }, 1500);

    } catch (error: any) {
      setSubmitError(error.response?.data?.detail || '提交失败，请重试');
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

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
                    {formatTime(timeRemaining)}
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
            {exam.exam_problems.map((problem: any, index: number) => (
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
                      value={answers[exam.exam_problems[currentStep].problem_id] || (exam.exam_problems[currentStep].is_multiple_choice ? [] : '')}
                      multiple={exam.exam_problems[currentStep].is_multiple_choice}
                      onChange={(e: any) => handleChoiceAnswer(
                        exam.exam_problems[currentStep].problem_id,
                        e.target.value
                      )}
                      sx={{ mt: 2 }}
                    >
                      {Object.entries((exam.exam_problems[currentStep] as any).options || {}).map(([key, value]) => (
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
                    {Object.entries(answers[exam.exam_problems[currentStep].problem_id] || {}).map(([blankId, value]: [string, any]) => (
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
              disabled={!Object.keys(answers).includes(String(exam.exam_problems?.[currentStep]?.problem_id))}
            >
              {exam.exam_problems && currentStep === exam.exam_problems.length - 1 ? '提交测验' : '下一题'}
            </Button>
          </Box>
        </Box>
      </SectionContainer>
    </PageContainer>
  );
}