import type { Page } from "~/types/page";
import type { Route } from "./+types/route";
import type { Course } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import CourseList from "./components/CourseList";
import { Box, Container, Typography, CircularProgress } from '@mui/material';
import { withAuth } from "~/utils/loaderWrapper";
import { useNavigate } from "react-router";

// export  async function loader({ params,request }: Route.LoaderArgs) {
  
//   const courses = await http.get<Page<Course>>("courses");
//   return courses;
// }
export const loader = withAuth(async ({ request }:Route.LoaderArgs) => {
  const url = new URL(request.url);
  const searchParams = url.searchParams;
   // 将 page 参数解析为数字，如果不存在则默认为 1
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10); // 可以添加 page_size 参数，默认为10
  // 构建查询参数对象
  const queryParams = new URLSearchParams();
  queryParams.set("page", page.toString());
  queryParams.set("page_size", pageSize.toString()); // 添加 pageSize 到查询参数

  const http = createHttp(request);
  const courses = await http.get<Page<Course>>(`/courses/?${queryParams.toString()}`); // 如果 401，自动 redirect
  return {
    data: courses.results,
    currentPage: page,
    totalItems: courses.count,
    // 从后端数据中获取 page_size，如果不存在则使用默认值
    actualPageSize: courses.page_size || pageSize,
  };
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
  const data = loaderData.data
  const currentPage = loaderData.currentPage;
  const totalItems = loaderData.totalItems;
  const actualPageSize = loaderData.actualPageSize;
  const totalPages = Math.ceil(totalItems / actualPageSize)
  const navigate = useNavigate();
  const onPageChange = (page: number) => {
    // 构建新的 URL
    const newSearchParams = new URLSearchParams();
    newSearchParams.set("page", page.toString());
    newSearchParams.set("page_size", actualPageSize.toString()); // 保持 pageSize
    
    navigate(`/courses/?${newSearchParams.toString()}`);
  };
  return <>
    <CourseList courses={data} page={{currentPage,totalItems,totalPages}} onPageChange={onPageChange}/>
  </>
}