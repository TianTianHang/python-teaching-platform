
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
  Alert
} from '@mui/material';
import { useNavigate, useSubmit } from 'react-router';
import type { Page } from "~/types/page";


export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.course.title || "课程主页" },
  ];
}
export async function action({request,params}:Route.ActionArgs) {
   const http = createHttp(request);
  
  try {
    // Get course details
    const enrollment = await http.post<Enrollment>(`/courses/${params.courseId}/enroll/`);
    
    
    
    return createResponse(request, {enrollment});
  } catch (error) {
    console.error('Error loading course data:', error);
    throw error;
  }
  
}
export async function loader({ request, params }: Route.LoaderArgs) {
  const http = createHttp(request);
  
  try {
    // Get course details
    const course = await http.get<Course>(`/courses/${params.courseId}`);
    
    // Check if user is enrolled in the course
    let enrollment = null;
    try {
      // Get all enrollments for the user
      const userEnrollments = await http.get<Page<Enrollment>>('/enrollments/');
      enrollment = userEnrollments.results.find(e => e.course === parseInt(params.courseId));
    } catch (error) {
      console.error('Error checking enrollment:', error);
    }
    
    return createResponse(request, { course, enrollment });
  } catch (error) {
    console.error('Error loading course data:', error);
    throw error;
  }
}

export default function CourseDetailPage({ params, loaderData, actionData }: Route.ComponentProps) {
  const course= loaderData.course;
  const enrollment = loaderData?.enrollment ||  actionData?.enrollment;
  const navigate = useNavigate();
  const submit = useSubmit();
  
  const handleJoinCourse = () => {
    // Make a POST request to enroll the user in the course
    submit({}, {
      method: 'POST',
      action: `/courses/${params.courseId}`
    });
  };

  const handleGoToChapters = () => {
    navigate(`/${params.lang}/courses/${params.courseId}/chapters`);
  };

  if (!course) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">课程信息加载失败</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Card sx={{ boxShadow: 3 }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold' }}>
            {course.title}
          </Typography>
          
          <Typography variant="body1" sx={{ mt: 2, mb: 3, whiteSpace: 'pre-line' }}>
            {course.description || '暂无课程描述'}
          </Typography>
          
          <Grid container spacing={3} sx={{ mt: 1 }}>
            <Grid  size={{xs:12,md:6}}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>课程信息</Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2">创建时间：{course.created_at ? new Date(course.created_at).toLocaleString() : 'N/A'}</Typography>
                <Typography variant="body2">更新时间：{course.updated_at ? new Date(course.updated_at).toLocaleString() : 'N/A'}</Typography>
              </Box>
            </Grid>
            
            <Grid size={{xs:12,md:6}}>
              <Typography variant="h6" sx={{ fontWeight: 'bold' }}>学习进度</Typography>
              {enrollment ? (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2">已加入课程</Typography>
                  <Typography variant="body2">加入时间：{new Date(enrollment.enrolled_at).toLocaleString()}</Typography>
                  {enrollment.last_accessed_at && (
                    <Typography variant="body2">最后访问：{new Date(enrollment.last_accessed_at).toLocaleString()}</Typography>
                  )}
                </Box>
              ) : (
                <Typography variant="body2" color="text.secondary">尚未加入课程</Typography>
              )}
            </Grid>
          </Grid>
          
          <Box sx={{ mt: 4, display: 'flex', gap: 2 }}>
            {!enrollment ? (
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleJoinCourse}
                sx={{ px: 4, py: 1.5 }}
              >
                加入课程
              </Button>
            ) : (
              <Button 
                variant="contained" 
                color="primary"
                onClick={handleGoToChapters}
                sx={{ px: 4, py: 1.5 }}
              >
                开始学习
              </Button>
            )}
            <Button 
              variant="outlined" 
              onClick={() => navigate(`/${params.lang}/courses`)}
            >
              返回课程列表
            </Button>
          </Box>
        </CardContent>
      </Card>
    </Container>
  );
}