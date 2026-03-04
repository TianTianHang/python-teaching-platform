import type { Page } from "~/types/page";
import type { Course } from "~/types/course";
import type { Route } from "./+types/route";
import CourseList, { CourseListkeleton } from "./components/CourseList";
import { useNavigate, useLoaderData } from "react-router";
import { redirect } from "react-router";
import React from "react";
import { Box, ListItem, ListItemText, Typography } from "@mui/material";
import { PageContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { School as SchoolIcon } from "@mui/icons-material";
import { clientHttp } from "~/utils/http/client";
import { formatTitle, PAGE_TITLES } from "~/config/meta";

/**
 * Client loader with hydration enabled
 * Fetches courses list with pagination support
 */
export async function clientLoader({ request }: Route.ClientLoaderArgs) {
    const url = new URL(request.url);
    const page = parseInt(url.searchParams.get("page") || "1", 10);
    const pageSize = parseInt(url.searchParams.get("page_size") || "10", 10);

    try {
        const queryParams = new URLSearchParams();
        queryParams.set("page", page.toString());
        queryParams.set("page_size", pageSize.toString());
        const data = await clientHttp.get<Page<Course>>(`/courses/?${queryParams.toString()}`);
        return { courses: data, page, pageSize };
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw new Response(JSON.stringify({ message: error.message || '请求失败' }), {
            status: error.response?.status || 500,
            statusText: error.message || '请求失败'
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

/**
 * Error boundary for client loader errors
 */
export function ErrorBoundary({ error }: { error: Error }) {
    return (
        <PageContainer maxWidth="lg">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                <SchoolIcon sx={{ color: 'text.primary' }} />
                <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
                    课程列表
                </Typography>
            </Box>
            <Typography color="error" variant="h6" gutterBottom>
                加载失败
            </Typography>
            <Typography color="text.secondary">
                {error.message || '无法加载课程列表'}
            </Typography>
        </PageContainer>
    );
}

export default function CoursePage() {
    const navigate = useNavigate();
    const loaderData = useLoaderData<typeof clientLoader>();
    const { courses, page, pageSize } = loaderData;

    const onPageChange = (newPage: number, newPageSize: number) => {
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("page", newPage.toString());
        newSearchParams.set("page_size", newPageSize.toString());
        navigate(`/courses/?${newSearchParams.toString()}`);
    };

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
            <CourseList
                courses={courses.results || []}
                page={{
                    currentPage: page,
                    totalItems: courses.count || 0,
                    totalPages: Math.ceil((courses.count || 0) / pageSize)
                }}
                onPageChange={(newPage) => onPageChange(newPage, pageSize)}
            />
        </PageContainer>
        </>
    );
}
