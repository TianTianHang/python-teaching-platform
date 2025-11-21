import { createHttp } from "~/utils/http/index.server";
import type { Route } from "./+types/route";
import type { Course } from "~/types/course";
import type { Enrollment } from "~/types/course";
import {
  Box,
  Container,
  Typography,
  Button,
  Card,
  CardContent,
  Grid,
  CircularProgress,
  Alert,
  LinearProgress,
  Divider,
  Skeleton
} from '@mui/material';
import { useNavigate, useSubmit, useNavigation, Await } from 'react-router';
import type { Page } from "~/types/page";
import { formatDateTime } from "~/utils/time";
import { withAuth } from "~/utils/loaderWrapper";
import DiscussionForum from "~/components/Thread/DiscussionForum";
import React, { useEffect, useState } from "react";
import ResolveError from "~/components/ResolveError";

export function meta({ loaderData }: Route.MetaArgs) {
  const [title, setTitle] = useState("课程主页");
  useEffect(() => {
    loaderData?.course.then((c) => {
      setTitle(c.title);
    }).catch(e => {
      setTitle('error')
    })
  });
  return [
    { title: title },
  ];
}

export const action = withAuth(async ({ request, params }: Route.ActionArgs) => {
  const http = createHttp(request);

  const enrollment = await http.post<Enrollment>(`/courses/${params.courseId}/enroll/`);
  return { enrollment };
});
export const loader = withAuth(async ({ request, params }: Route.LoaderArgs) => {
  const http = createHttp(request);

  const course = http.get<Course>(`/courses/${params.courseId}`);
  let enrollment: Enrollment | null = null;

  const userEnrollments = await http.get<Page<Enrollment>>(`/enrollments/?course=${params.courseId}`);
  enrollment = userEnrollments.results.length > 0 ? userEnrollments.results[0] : null;
  return { course, enrollment };
})


export default function CourseDetailPage({ loaderData, actionData, params }: Route.ComponentProps) {
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



  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
      <Card elevation={2}>
        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
          <React.Suspense fallback={<CourseDetailSkeleton/>}>
            <Await
              resolve={course}
              errorElement={
                <ResolveError>
                  <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
                  <Alert severity="error">课程不存在或加载失败，请稍后重试。</Alert>
                  <Box sx={{ mt: 2 }}>
                    <Button variant="outlined" onClick={() => navigate(`/courses`)}>
                      返回课程列表
                    </Button>
                  </Box>
                </Container>
                </ResolveError>
                
              }
              children={(resolved) => {

                const description = resolved.description?.trim() || "暂无课程描述";
                return (
                  <>
                    <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
                      {resolved.title}
                    </Typography>

                    <Typography
                      variant="body1"
                      sx={{
                        mt: 2,
                        mb: 3,
                        whiteSpace: 'pre-line',
                        color: description === "暂无课程描述" ? 'text.secondary' : 'text.primary'
                      }}
                    >
                      {description}
                    </Typography>

                    <Grid container spacing={3} sx={{ mt: 1 }}>
                      <Grid size={{ xs: 12, md: 6 }}>
                        <Typography variant="h6" fontWeight="bold" gutterBottom>
                          课程信息
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                          <Typography variant="body2">
                            创建时间：{resolved.created_at ? formatDateTime(resolved.created_at) : '—'}
                          </Typography>
                          <Typography variant="body2">
                            更新时间：{resolved.updated_at ? formatDateTime(resolved.updated_at) : '—'}
                          </Typography>
                        </Box>
                      </Grid>

                      <Grid size={{ xs: 12, md: 6 }}>
                        <Typography variant="h6" fontWeight="bold" gutterBottom>
                          学习进度
                        </Typography>
                        {enrollment ? (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="body2" color="success.main" fontWeight="medium">
                              ✅ 已加入课程
                            </Typography>
                            <Box sx={{ mt: 1, mb: 0.5 }}>
                              <Typography variant="body2">
                                进度：{enrollment.progress_percentage}%
                              </Typography>
                              <LinearProgress
                                variant="determinate"
                                value={enrollment.progress_percentage}
                                sx={{ mt: 0.5, height: 6, borderRadius: 3 }}
                              />
                            </Box>
                            <Typography variant="body2" sx={{ mt: 1 }}>
                              加入时间：{formatDateTime(enrollment.enrolled_at)}
                            </Typography>
                            {enrollment.last_accessed_at && (
                              <Typography variant="body2">
                                最后学习：{formatDateTime(enrollment.last_accessed_at)}
                              </Typography>
                            )}
                          </Box>
                        ) : (
                          <Typography variant="body2" color="text.secondary">
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
          <Box sx={{ mt: 4, mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
            {enrollment ? (
              <Button
                variant="contained"
                color="primary"
                onClick={handleGoToChapters}
                size="large"
                sx={{ minWidth: 140 }}
              >
                开始学习
              </Button>
            ) : (
              <Button
                variant="contained"
                color="primary"
                onClick={handleJoinCourse}
                disabled={isSubmitting}
                size="large"
                sx={{ minWidth: 140 }}
                startIcon={isSubmitting ? <CircularProgress size={20} color="inherit" /> : null}
              >
                {isSubmitting ? "加入中…" : "加入课程"}
              </Button>
            )}
            <Button
              variant="outlined"
              onClick={() => navigate(`/courses`)}
              size="large"
            >
              返回课程列表
            </Button>
          </Box>
          <Divider />
          <React.Suspense >
            <Await
              resolve={course}
              children={(resolved) => (
                <Box sx={{ mt: 4 }}>
                  <DiscussionForum threads={resolved.recent_threads} courseId={resolved.id} />
                </Box>)
              } />
          </React.Suspense>

        </CardContent>

      </Card>
    </Container>
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
      <Grid  size={{ xs: 12, md: 6 }}>
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