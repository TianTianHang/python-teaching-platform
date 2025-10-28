import { createHttp, createResponse } from "~/utils/http/index.server";
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
  LinearProgress
} from '@mui/material';
import { useNavigate, useSubmit, useNavigation } from 'react-router';
import type { Page } from "~/types/page";
import { formatDateTime } from "~/utils/time";

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.course?.title || "课程主页" },
  ];
}

export async function action({ request, params }: Route.ActionArgs) {
  const http = createHttp(request);
  try {
    const enrollment = await http.post<Enrollment>(`/courses/${params.courseId}/enroll/`);
    return createResponse(request, { enrollment });
  } catch (error) {
    console.error('Enrollment error:', error);
    throw error;
  }
}

export async function loader({ request, params }: Route.LoaderArgs) {
  const http = createHttp(request);
  try {
    const course = await http.get<Course>(`/courses/${params.courseId}`);
    let enrollment: Enrollment | null = null;
    try {
      const userEnrollments = await http.get<Page<Enrollment>>('/enrollments/');
      enrollment = userEnrollments.results.find(e => e.course === parseInt(params.courseId))||null;
    } catch (err) {
      // Silently fail enrollment check (non-critical)
    }
    return createResponse(request, { course, enrollment });
  } catch (error) {
    console.error('Course load error:', error);
    throw error;
  }
}

export default function CourseDetailPage({ loaderData, actionData, params }: Route.ComponentProps) {
  const course = loaderData?.course;
  const enrollment = loaderData?.enrollment || actionData?.enrollment;
  const navigate = useNavigate();
  const submit = useSubmit();
  const navigation = useNavigation();
  const isSubmitting = navigation.state === "submitting";

  // Handle missing course (e.g., 404)
  if (!course) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">课程不存在或加载失败，请稍后重试。</Alert>
        <Box sx={{ mt: 2 }}>
          <Button variant="outlined" onClick={() => navigate(`/${params.lang}/courses`)}>
            返回课程列表
          </Button>
        </Box>
      </Container>
    );
  }

  const handleJoinCourse = () => {
    submit({}, { method: 'POST', action: `/courses/${params.courseId}` });
  };

  const handleGoToChapters = () => {
    navigate(`/${params.lang}/courses/${params.courseId}/chapters`);
  };

  const description = course.description?.trim() || "暂无课程描述";

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 6 }}>
      <Card elevation={2}>
        <CardContent sx={{ p: { xs: 2, sm: 3 } }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
            {course.title}
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
            <Grid size={{xs:12,md:6}}>
              <Typography variant="h6" fontWeight="bold" gutterBottom>
                课程信息
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Typography variant="body2">
                  创建时间：{course.created_at ? formatDateTime(course.created_at) : '—'}
                </Typography>
                <Typography variant="body2">
                  更新时间：{course.updated_at ? formatDateTime(course.updated_at) : '—'}
                </Typography>
              </Box>
            </Grid>

            <Grid size={{xs:12,md:6}}>
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

          <Box sx={{ mt: 4, display: 'flex', flexWrap: 'wrap', gap: 1.5 }}>
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
              onClick={() => navigate(`/${params.lang}/courses`)}
              size="large"
            >
              返回课程列表
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}