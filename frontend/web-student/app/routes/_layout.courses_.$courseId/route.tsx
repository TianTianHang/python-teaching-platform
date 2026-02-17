import { createHttp } from "~/utils/http/index.server";
import type { Route } from "./+types/route";
import type { Course } from "~/types/course";
import type { Enrollment } from "~/types/course";
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
  Skeleton,
  useTheme,
  } from '@mui/material';
import { useNavigate, useSubmit, useNavigation, Await } from 'react-router';
import type { Page } from "~/types/page";
import { formatDateTime } from "~/utils/time";
import { withAuth } from "~/utils/loaderWrapper";
import DiscussionForum from "~/components/Thread/DiscussionForum";
import React from "react";
import ResolveError from "~/components/ResolveError";
import { PageContainer, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import type { AxiosError } from "axios";
import QuizIcon from '@mui/icons-material/Quiz';
import { DEFAULT_META, formatTitle, truncateDescription } from "~/config/meta";

export const action = withAuth(async ({ request, params }: Route.ActionArgs) => {
  const http = createHttp(request);

  const enrollment = await http.post<Enrollment>(`/courses/${params.courseId}/enroll/`);
  return { enrollment };
});
export const loader = withAuth(async ({ request, params }: Route.LoaderArgs) => {
  const http = createHttp(request);

  const course = http.get<Course>(`/courses/${params.courseId}`)
    .catch((e: AxiosError) => {
      return {
        status: e.status,
        message: e.message,
      }
    });;
  let enrollment: Enrollment | null = null;

  const userEnrollments = await http.get<Page<Enrollment>>(`/enrollments/?course=${params.courseId}`);
  enrollment = userEnrollments.results.length > 0 ? userEnrollments.results[0] : null;
  return { course, enrollment };
})


export default function CourseDetailPage({ loaderData, actionData, params }: Route.ComponentProps) {
  const theme = useTheme();
  const course = loaderData.course;
  const enrollment = loaderData?.enrollment || actionData?.enrollment;
  const navigate = useNavigate();
  const submit = useSubmit();
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";

  const handleJoinCourse = () => {
    submit({}, { method: 'POST', action: `/courses/${params.courseId}` });
  };

  const handleGoToChapters = () => {
    navigate(`/courses/${params.courseId}/chapters`);
  };

  const handleGoToExams = () => {
    navigate(`/courses/${params.courseId}/exams`);
  };



  return (
    <>
      <title>课程详情 - {DEFAULT_META.siteName}</title>
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
          <React.Suspense fallback={<CourseDetailSkeleton />}>
            <Await
              resolve={course}
              children={(resolved) => {
                if ('status' in resolved) {
                  return (
                    <ResolveError status={resolved.status} message={resolved.message}>
                      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                        <Alert severity="error">课程不存在或加载失败，请稍后重试。</Alert>
                        <Box sx={{ mt: 2 }}>
                          <Button variant="outlined" onClick={() => navigate(`/courses`)}>
                            返回课程列表
                          </Button>
                        </Box>
                      </Container>
                    </ResolveError>)
                }
                const description = resolved.description?.trim() || "暂无课程描述";
                const title = resolved.title || "课程详情";
                const metaDescription = truncateDescription(description);
                return (
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
                      {resolved.title}
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
                            创建时间：{resolved.created_at ? formatDateTime(resolved.created_at) : '—'}
                          </Typography>
                          <Typography variant="body2" color={theme?.palette.text.primary || 'text.primary'}>
                            更新时间：{resolved.updated_at ? formatDateTime(resolved.updated_at) : '—'}
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
                        {enrollment ? (
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
                                <span>进度：{enrollment.progress_percentage}%</span>
                                <span>完成率</span>
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={enrollment.progress_percentage}
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
                                加入时间：{formatDateTime(enrollment.enrolled_at)}
                              </Typography>
                              {enrollment.last_accessed_at && (
                                <Typography
                                  variant="body2"
                                  sx={{ color: theme.palette.text.secondary }}
                                >
                                  最后学习：{formatDateTime(enrollment.last_accessed_at)}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        ) : (
                          <Typography
                            variant="body2"
                            sx={{ color: theme.palette.text.secondary }}
                          >
                            尚未加入课程
                          </Typography>
                        )}
                      </Grid>
                    </Grid>
                  </>
                )
              }}
            />
          </React.Suspense>
          <Box sx={{ mt: 6, mb: 4, display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center' }}>
            {enrollment ? (
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
                disabled={isSubmitting}
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
                startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {isSubmitting ? "加入中…" : "加入课程"}
              </Button>
            )}
            <Button
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
            </Button>
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
          <React.Suspense >
            <Await
              resolve={course}
              children={(resolved) => {
                if ('status' in resolved) {
                  return (
                    <ResolveError status={resolved.status} message={resolved.message}>
                      <></>
                    </ResolveError>)
                }
                return (
                  <Box sx={{ mt: 4 }}>
                    <DiscussionForum threads={resolved.recent_threads} courseId={resolved.id} />
                  </Box>)
              }
              } />
          </React.Suspense>
      </SectionContainer>
    </PageContainer>
    </>
  );
}



const CourseDetailSkeleton = () => (
  <>
    {/* 标题骨架 */}
    <Skeleton variant="text" width="60%" height={40} />

    {/* 描述骨架 */}
    <Skeleton
      variant="text"
      width="100%"
      height={60}
      sx={{ mt: 2, mb: 3 }}
    />

    <Grid container spacing={3} sx={{ mt: 1 }}>
      {/* 课程信息 */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          课程信息
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
          <Skeleton variant="text" width="80%" height={24} />
          <Skeleton variant="text" width="70%" height={24} />
        </Box>
      </Grid>

      {/* 学习进度 */}
      <Grid size={{ xs: 12, md: 6 }}>
        <Typography variant="h6" fontWeight="bold" gutterBottom>
          学习进度
        </Typography>
        <Skeleton
          variant="rounded"
          height={40}
          sx={{ borderRadius: 1 }}
        />
      </Grid>
    </Grid>
  </>
)