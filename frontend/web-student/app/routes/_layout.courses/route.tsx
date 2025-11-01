import type { Page } from "~/types/page";
import type { Route } from "./+types/route";
import type { Course } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import CourseList from "./components/CourseList";
import { Box, Container, Typography, CircularProgress } from '@mui/material';
import { withAuth } from "~/utils/loaderWrapper";

// export  async function loader({ params,request }: Route.LoaderArgs) {
  
//   const courses = await http.get<Page<Course>>("courses");
//   return courses;
// }
export const loader = withAuth(async ({ request }:Route.LoaderArgs) => {
  const http = createHttp(request);

  const courses = await http.get<Page<Course>>('/courses'); // 如果 401，自动 redirect
  return courses;
});

export function HydrateFallback() {
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
        <Typography variant="body1" sx={{ ml: 2 }}>加载课程中...</Typography>
      </Box>
    </Container>
  );
}

export default function CoursePage({params, loaderData}:Route.ComponentProps) {
  return <>
    <CourseList courses={loaderData.results}/>
  </>
}