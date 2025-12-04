import type { Page } from "~/types/page";
import type { Route } from "./+types/route";
import type { Course } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import CourseList, { CourseListkeleton } from "./components/CourseList";
import { withAuth } from "~/utils/loaderWrapper";
import { Await, useNavigate } from "react-router";
import React from "react";
import { Container, ListItem, ListItemText, Typography } from "@mui/material";
import ResolveError from "~/components/ResolveError";
import type { AxiosError } from "axios";

// export  async function loader({ params,request }: Route.LoaderArgs) {

//   const courses = await http.get<Page<Course>>("courses");
//   return courses;
// }
export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
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
  const courses = http.get<Page<Course>>(`/courses/?${queryParams.toString()}`)
    .catch((e: AxiosError) => {
      return {
        status: e.status,
        message: e.message,
      }
    });
  return {
    currentPage: page,
    pageData: courses
  }
  // return {
  //   data: courses.results,
  //   currentPage: page,
  //   totalItems: courses.count,
  //   // 从后端数据中获取 page_size，如果不存在则使用默认值
  //   actualPageSize: courses.page_size || pageSize,
  // };
});

export default function CoursePage({ params, loaderData }: Route.ComponentProps) {

  const navigate = useNavigate();
  const onPageChange = (page: number, page_size: number) => {
    // 构建新的 URL
    const newSearchParams = new URLSearchParams();
    newSearchParams.set("page", page.toString());
    newSearchParams.set("page_size", page_size.toString()); // 保持 pageSize

    navigate(`/courses/?${newSearchParams.toString()}`);
  };
  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        课程列表
      </Typography>
      <React.Suspense fallback={<CourseListkeleton />}>
        <Await
          resolve={loaderData.pageData}
          children={(resolved) => {
            if ('status' in resolved) {
              return (
                <ResolveError status={resolved.status} message={resolved.message}>
                  <ListItem>
                    <ListItemText>
                      加载失败
                    </ListItemText>
                  </ListItem>
                </ResolveError>)
            }
            const data = resolved.results
            const currentPage = loaderData.currentPage;
            const totalItems = resolved.count;
            const actualPageSize = resolved.page_size || 10;
            const totalPages = Math.ceil(totalItems / actualPageSize)

            return (
              <CourseList
                courses={data}
                page={{ currentPage, totalItems, totalPages }}
                onPageChange={(page) => onPageChange(page, actualPageSize)}
              />
            )
          }}
        />
      </React.Suspense>
    </Container>)
}


