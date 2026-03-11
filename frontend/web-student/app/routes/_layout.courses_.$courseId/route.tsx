import type { Course } from "~/types/course";
import type { Enrollment } from "~/types/course";
import type { Route } from "./+types/route";
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  CircularProgress,
  Alert,
  LinearProgress,
  Divider,
  useTheme,
  } from '@mui/material';
import { useNavigate, useParams, useLoaderData, Link, useRevalidator } from 'react-router';
import { redirect } from 'react-router';
import type { Page } from "~/types/page";
import { formatDateTime } from "~/utils/time";
import DiscussionForum from "~/components/Thread/DiscussionForum";
import React, { useState } from "react";
import { PageContainer, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { clientHttp } from "~/utils/http/client";
import QuizIcon from '@mui/icons-material/Quiz';
import { DEFAULT_META, formatTitle, truncateDescription } from "~/config/meta";
import CourseDetailSkeleton from "~/components/skeleton/CourseDetailSkeleton";
import { ErrorCard } from "~/components/ErrorCard";

/**
 * Helper function to parse error from Error or Response object
 */
function parseError(error: any): { status: number; message: string } {
    if (error.response?.status) {
        return {
            status: parseInt(error.response.status),
            message: error.response?.data?.detail || error.message || '请求失败'
        };
    }
    return {
        status: 500,
        message: error.message || '请求失败'
    };
}

/**
 * Type for section result with error handling
 */
interface SectionResult<T> {
    data: T | null;
    error: { status: number; message: string } | null;
}

/**
 * Client loader with hydration enabled
 * Fetches course details and enrollment info with independent error handling
 */
export async function clientLoader({ params, request }: Route.ClientLoaderArgs) {
    const { courseId } = params;

    try {
        const results = await Promise.allSettled([
            clientHttp.get<Course>(`/courses/${courseId}`),
            clientHttp.get<Page<Enrollment>>(`/enrollments/?course=${courseId}`)
                .then(result => result.results.length > 0 ? result.results[0] : null)
        ]);

        const courseResult = results[0];
        const enrollmentResult = results[1];

        const course: SectionResult<Course> = {
            data: courseResult.status === 'fulfilled' ? courseResult.value : null,
            error: courseResult.status === 'rejected' ? parseError(courseResult.reason) : null
        };

        const enrollment: SectionResult<Enrollment> = {
            data: enrollmentResult.status === 'fulfilled' ? enrollmentResult.value : null,
            error: enrollmentResult.status === 'rejected' ? parseError(enrollmentResult.reason) : null
        };

        return { course, enrollment };
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw new Response(JSON.stringify({ message: error.message || '加载失败' }), {
            status: error.response?.status || 500,
            statusText: error.message || '加载失败'
        });
    }
}
clientLoader.hydrate = true as const;

/**
 * Hydrate fallback component
 */
export function HydrateFallback() {
    return (
        <>
            <title>{formatTitle('课程详情')}</title>
            <PageContainer maxWidth="lg">
                <SectionContainer spacing="lg" variant="card">
                    <CourseDetailSkeleton />
                </SectionContainer>
            </PageContainer>
        </>
    );
}

/**
 * Error boundary for client loader errors
 */
export function ErrorBoundary({ error }: { error: Error }) {
    // Parse error from Response
    const errorResponse = error as any;
    const status = errorResponse.status ? parseInt(errorResponse.status) : 500;
    const message = errorResponse.message || '课程加载失败';

    return (
        <PageContainer maxWidth="lg">
            <Box sx={{ py: spacing.xl }}>
                <ErrorCard
                    status={status}
                    message={message}
                    title="课程详情加载失败"
                    onRetry={() => window.location.reload()}
                />
            </Box>
        </PageContainer>
    );
}

export default function CourseDetailPage() {
  const { courseId } = useParams();
  const theme = useTheme();
  const navigate = useNavigate();
  const revalidator = useRevalidator();
  const loaderData = useLoaderData<typeof clientLoader>();
  const { course, enrollment } = loaderData;

  const [enrolling, setEnrolling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleJoinCourse = async () => {
    setEnrolling(true);
    setError(null);
    try {
      const result = await clientHttp.post<Enrollment>(`/courses/${courseId}/enroll/`);
      revalidator.revalidate();
    } catch (err: any) {
      if (err.response?.status === 401) {
        navigate('/auth/login');
        return;
      }
      setError(err.message || '报名失败');
    } finally {
      setEnrolling(false);
    }
  };

  const handleGoToChapters = () => {
    navigate(`/courses/${courseId}/chapters`);
  };

  const handleGoToExams = () => {
    navigate(`/courses/${courseId}/exams`);
  };

  // Handle course loading error
  if (course?.error) {
    return (
      <PageContainer maxWidth="lg">
        <Box sx={{ py: spacing.xl }}>
          <ErrorCard
            status={course.error.status}
            message={course.error.message}
            title="课程信息加载失败"
            onRetry={() => window.location.reload()}
          />
        </Box>
      </PageContainer>
    );
  }

  // Handle enrollment loading error but show course content
  if (enrollment?.error) {
    return (
      <PageContainer maxWidth="lg">
        <SectionContainer spacing="lg" variant="card">
          <Box sx={{ mb: spacing.md }}>
            <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
              课程详情
            </Typography>
          </Box>

          {course?.data && (
            <>
              <title>{formatTitle(course.data.title)}</title>
              <meta name="description" content={truncateDescription(course.data.description) || `查看《${course.data.title}》课程详情`} />
              <meta property="og:title" content={formatTitle(course.data.title)} />
              <meta property="og:description" content={truncateDescription(course.data.description) || `查看《${course.data.title}》课程详情`} />
              <meta property="og:type" content="course" />

              {/* Course content - display normally */}
              <Box sx={{ mb: spacing.xl }}>
                {/* Course title and description */}
                <Typography variant="h6" color="text.primary" gutterBottom>
                  {course.data.title}
                </Typography>
                <Typography variant="body1" color="text.secondary" paragraph>
                  {course.data.description}
                </Typography>
                {/* Other course content */}
              </Box>

              {/* Enrollment status with error */}
              <Box sx={{ p: 3, border: 1, borderColor: 'error.light', borderRadius: 2, bgcolor: 'error.50' }}>
                <Typography variant="body2" color="error" gutterBottom>
                  报名信息加载失败：{enrollment.error.message}
                </Typography>
                <Button
                  variant="outlined"
                  onClick={() => window.location.reload()}
                  sx={{ mt: 1 }}
                >
                  重新加载报名信息
                </Button>
              </Box>
            </>
          )}
        </SectionContainer>
      </PageContainer>
    );
  }

  const description = course?.data?.description?.trim() || "暂无课程描述";
  const title = course?.data?.title || "课程详情";
  const metaDescription = truncateDescription(description);

  return (
    <>
      <title>{formatTitle('课程详情')}</title>
      <meta name="description" content={`查看课程详情和学习进度 - ${DEFAULT_META.description}`} />
      <meta property="og:title" content={`课程详情 - ${DEFAULT_META.siteName}`} />
      <meta property="og:description" content={`查看课程详情和学习进度 - ${DEFAULT_META.description}`} />
      <meta property="og:type" content={DEFAULT_META.ogType} />

      <PageContainer maxWidth="lg">
        <SectionContainer spacing="lg" variant="card">
          <Box sx={{ mb: spacing.md }}>
            <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
              课程详情
            </Typography>
          </Box>

          {course?.data && (
            <>
              <title>{formatTitle(title)}</title>
              <meta name="description" content={metaDescription || `查看《${title}》课程详情和学习进度`} />
              <meta property="og:title" content={formatTitle(title)} />
              <meta property="og:description" content={metaDescription || `查看《${title}》课程详情和学习进度`} />
              <meta property="og:type" content="course" />

              <Typography
                variant="h4"
                component="h1"
                gutterBottom
                sx={{
                  fontWeight: 700,
                  color: theme.palette.text.primary,
                  lineHeight: 1.3,
                  fontSize: '2rem',
                }}
              >
                {course.data.title}
              </Typography>

              <Typography
                variant="body1"
                sx={{
                  mt: 3,
                  mb: 4,
                  whiteSpace: 'pre-line',
                  color: description === "暂无课程描述" ? theme.palette.text.secondary : theme.palette.text.primary,
                  lineHeight: 1.6,
                  fontSize: '1.125rem',
                }}
              >
                {description}
              </Typography>

              <Grid container spacing={3} sx={{ mt: 1 }}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography variant="h6" fontWeight="bold" gutterBottom color={theme?.palette.text.primary || 'text.primary'}>
                    课程信息
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                    <Typography variant="body2" color={theme?.palette.text.primary || 'text.primary'}>
                      创建时间：{course.data.created_at ? formatDateTime(course.data.created_at) : '—'}
                    </Typography>
                    <Typography variant="body2" color={theme?.palette.text.primary || 'text.primary'}>
                      更新时间：{course.data.updated_at ? formatDateTime(course.data.updated_at) : '—'}
                    </Typography>
                  </Box>
                </Grid>

                <Grid size={{ xs: 12, md: 6 }}>
                  <Typography
                    variant="h6"
                    fontWeight={600}
                    gutterBottom
                    sx={{
                      color: theme.palette.text.primary,
                      fontSize: '1.25rem',
                    }}
                  >
                    学习进度
                  </Typography>

                  {enrollment?.error ? (
                    <Alert severity="warning" sx={{ mt: 2 }}>
                      加载报名信息失败，请刷新页面重试
                    </Alert>
                  ) : !enrollment?.data ? (
                    <Typography
                      variant="body2"
                      sx={{ color: theme.palette.text.secondary }}
                    >
                      尚未加入课程
                    </Typography>
                  ) : (
                    <Box sx={{ mt: 2 }}>
                      <Box
                        sx={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: 1,
                          mb: 2,
                          p: 1.5,
                          borderRadius: 1,
                          bgcolor: theme.palette.mode === 'dark' ? theme.palette.success.dark : theme.palette.success.light,
                        }}
                      >
                        <Typography
                          variant="body1"
                          fontWeight={600}
                          sx={{
                            color: theme.palette.success.contrastText || 'white',
                          }}
                        >
                          已加入课程
                        </Typography>
                      </Box>
                      <Box sx={{ mb: 2 }}>
                        <Typography
                          variant="body2"
                          sx={{
                            color: theme.palette.text.secondary,
                            fontWeight: 500,
                            mb: 0.5,
                            display: 'flex',
                            justifyContent: 'space-between',
                          }}
                        >
                          <span>进度：{enrollment?.data?.progress_percentage}%</span>
                          <span>完成率</span>
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={enrollment?.data?.progress_percentage}
                          sx={{
                            mt: 0.5,
                            height: 8,
                            borderRadius: 4,
                            backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[800] : theme.palette.grey[200],
                          }}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                        <Typography
                          variant="body2"
                          sx={{ color: theme.palette.text.secondary }}
                        >
                          加入时间：{enrollment?.data?.enrolled_at ? formatDateTime(enrollment.data.enrolled_at) : '—'}
                        </Typography>
                        {enrollment?.data?.last_accessed_at && (
                          <Typography
                            variant="body2"
                            sx={{ color: theme.palette.text.secondary }}
                          >
                            最后学习：{formatDateTime(enrollment.data.last_accessed_at)}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  )}
                </Grid>
              </Grid>
            </>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Box sx={{ mt: 6, mb: 4, display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center' }}>
            {enrollment && !('status' in enrollment) ? (
              <Button
                variant="contained"
                onClick={handleGoToChapters}
                size="large"
                sx={{
                  minWidth: 160,
                  padding: '12px 24px',
                  borderRadius: 2,
                  background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                  color: 'common.white',
                  fontWeight: 600,
                  textTransform: 'none',
                  boxShadow: theme.shadows[4],
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: theme.shadows[6],
                    background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                  },
                }}
              >
                开始学习
              </Button>
            ) : (
              <Button
                variant="contained"
                onClick={handleJoinCourse}
                disabled={enrolling}
                size="large"
                sx={{
                  minWidth: 140,
                  background: `linear-gradient(135deg, ${theme.palette.success.main} 0%, ${theme.palette.success.dark} 100%)`,
                  color: 'common.white',
                  fontWeight: 600,
                  textTransform: 'none',
                  boxShadow: theme.shadows[4],
                  '&:hover': {
                    transform: 'translateY(-2px)',
                    boxShadow: theme.shadows[6],
                    background: `linear-gradient(135deg, ${theme.palette.success.dark} 0%, ${theme.palette.success.main} 100%)`,
                  },
                  '&:disabled': {
                    background: theme.palette.action.disabled,
                    color: theme.palette.action.disabled,
                    boxShadow: 'none',
                    transform: 'none',
                  },
                }}
                startIcon={enrolling ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {enrolling ? "加入中…" : "加入课程"}
              </Button>
            )}
            {/* <Button
              variant="contained"
              onClick={handleGoToExams}
              size="large"
              startIcon={<QuizIcon />}
              sx={{
                minWidth: 140,
                padding: '12px 24px',
                borderRadius: 2,
                background: `linear-gradient(135deg, ${theme.palette.warning.main} 0%, ${theme.palette.warning.dark} 100%)`,
                color: 'common.white',
                fontWeight: 600,
                textTransform: 'none',
                boxShadow: theme.shadows[4],
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                '&:hover': {
                  transform: 'translateY(-2px) scale(1.02)',
                  boxShadow: theme.shadows[6],
                  background: `linear-gradient(135deg, ${theme.palette.warning.dark} 0%, #DC2626 100%)`,
                  '& .MuiSvgIcon-root': {
                    transform: 'scale(1.15) rotate(-5deg)',
                  },
                },
                '&:active': {
                  transform: 'translateY(0) scale(0.98)',
                },
                '& .MuiSvgIcon-root': {
                  transition: 'transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)',
                  transformOrigin: 'center',
                },
                '@media (prefers-reduced-motion: reduce)': {
                  transition: 'none',
                  '&:hover': {
                    transform: 'none',
                  },
                },
              }}
              aria-label="前往课程测验页面"
            >
              测验
            </Button> */}
            <Button
              variant="outlined"
              onClick={() => navigate(`/courses`)}
              size="large"
              sx={{
                fontWeight: 600,
                borderRadius: 2,
                borderColor: theme.palette.divider,
                '&:hover': {
                  borderColor: theme.palette.primary.main,
                  backgroundColor: theme.palette.action.hover,
                },
              }}
            >
              返回课程列表
            </Button>
          </Box>

          <Divider />

          {false && course?.data && (
            <Box sx={{ mt: 4 }}>
              <DiscussionForum
                threads={course.data?.recent_threads || []}
                courseId={course.data?.id || Number(courseId)}
              />
            </Box>
          )}
        </SectionContainer>
      </PageContainer>
    </>
  );
}