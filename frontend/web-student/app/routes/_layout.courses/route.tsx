import type { Page } from "~/types/page";
import type { Course } from "~/types/course";
import CourseList, { CourseListkeleton } from "./components/CourseList";
import { useNavigate, useSearchParams } from "react-router";
import React, { useState, useEffect } from "react";
import { Box, ListItem, ListItemText, Typography } from "@mui/material";
import ResolveError from "~/components/ResolveError";
import { PageContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { School as SchoolIcon } from "@mui/icons-material";
import { clientHttp } from "~/utils/http/client";
import { DEFAULT_META, formatTitle, PAGE_TITLES } from "~/config/meta";

export default function CoursePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10);

  const [courses, setCourses] = useState<Page<Course> | { status: number; message: string } | null>(null);
  const [loading, setLoading] = useState(true);

  const navigate = useNavigate();

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const queryParams = new URLSearchParams();
        queryParams.set("page", page.toString());
        queryParams.set("page_size", pageSize.toString());
        const data = await clientHttp.get<Page<Course>>(`/courses/?${queryParams.toString()}`);
        setCourses(data);
      } catch (error: any) {
        if (error.response?.status === 401) {
          navigate('/auth/login');
          return;
        }
        setCourses({
          status: error.response?.status || 500,
          message: error.message || '请求失败'
        });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [page, pageSize, navigate]);

  const onPageChange = (newPage: number, newPageSize: number) => {
    const newSearchParams = new URLSearchParams();
    newSearchParams.set("page", newPage.toString());
    newSearchParams.set("page_size", newPageSize.toString());
    navigate(`/courses/?${newSearchParams.toString()}`);
  };

  if (loading) {
    return (
      <>
        <title>{formatTitle(PAGE_TITLES.courses)}</title>
        <PageContainer maxWidth="lg">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
            <SchoolIcon sx={{ color: 'text.primary' }} />
            <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
              课程列表
            </Typography>
          </Box>
          <Typography variant="body1" color="text.secondary" sx={{ mb: spacing.md }}>
            探索我们的课程
          </Typography>
          <CourseListkeleton />
        </PageContainer>
      </>
    );
  }

  return (
    <>
      <title>{formatTitle(PAGE_TITLES.courses)}</title>
      <PageContainer maxWidth="lg">
      <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
        <SchoolIcon sx={{ color: 'text.primary' }} />
        <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
          课程列表
        </Typography>
      </Box>
      <Typography variant="body1" color="text.secondary" sx={{ mb: spacing.md }}>
        探索我们的课程
      </Typography>
      {courses && 'status' in courses ? (
        <ResolveError status={courses.status} message={courses.message}>
          <ListItem>
            <ListItemText>
              加载失败
            </ListItemText>
          </ListItem>
        </ResolveError>
      ) : (
        <CourseList
          courses={courses?.results || []}
          page={{ 
            currentPage: page, 
            totalItems: courses?.count || 0, 
            totalPages: Math.ceil((courses?.count || 0) / pageSize) 
          }}
          onPageChange={(newPage) => onPageChange(newPage, pageSize)}
        />
      )}
    </PageContainer>
    </>
  );
}
