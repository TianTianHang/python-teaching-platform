import { Box, Typography, Button, Stack } from "@mui/material";
import {
    Book as BookIcon,
    Quiz as QuizIcon,
    Refresh as RefreshIcon,
    Home as HomeIcon,
    Warning as WarningIcon,
} from '@mui/icons-material';
import type { Page } from "~/types/page";
import type { Enrollment, ProblemProgress } from "~/types/course";

/**
 * Error information structure for individual data sections
 */
interface ErrorInfo {
    status: number;
    message: string;
}

/**
 * Structured data type for section-specific loading results
 */
type SectionResult<T> = {
    data: T | null;
    error: ErrorInfo | null;
};

import { useLoaderData } from "react-router";
import { redirect } from "react-router";
import { clientHttp } from "~/utils/http/client";
import { PageContainer, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { SkeletonHome } from "~/components/HydrateFallback";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import { useUser } from "~/hooks/userUser";
import type { Route } from "./+types/_layout.home";
import { CoursesSection } from "~/components/CoursesSection";
import { ProblemsSection } from "~/components/ProblemsSection";

/**
 * Route headers for HTTP caching
 * Home dashboard has user-specific content, using private cache
 */
export function headers(): Headers | HeadersInit {
    return {
        "Cache-Control": "private, max-age=120, must-revalidate",
    };
}

/**
 * Client loader with hydration enabled
 * Fetches enrolled courses and unfinished problems independently using Promise.allSettled
 * Each section's success or failure is handled independently
 */
export async function clientLoader({ request }: Route.ClientLoaderArgs) {
    // Handle 401 errors globally by redirecting to login
    try {
        // Use Promise.allSettled to handle each request independently
        const results = await Promise.allSettled([
            clientHttp.get<Page<Enrollment>>('enrollments/'),
            clientHttp.get<Page<ProblemProgress>>('problem-progress/?status_not=solved')
        ]);

        // Process enrollments result
        let enrolledCoursesResult: SectionResult<Page<Enrollment>>;
        if (results[0].status === 'fulfilled') {
            enrolledCoursesResult = {
                data: results[0].value,
                error: null
            };
        } else {
            const error = results[0].reason;
            // Check for 401 and redirect globally
            if (error.response?.status === 401) {
                throw redirect('/auth/login');
            }
            enrolledCoursesResult = {
                data: null,
                error: {
                    status: error.response?.status || 500,
                    message: error.message || '加载课程失败'
                }
            };
        }

        // Process problems result
        let unfinishedProblemsResult: SectionResult<Page<ProblemProgress>>;
        if (results[1].status === 'fulfilled') {
            unfinishedProblemsResult = {
                data: results[1].value,
                error: null
            };
        } else {
            const error = results[1].reason;
            // Check for 401 and redirect globally
            if (error.response?.status === 401) {
                throw redirect('/auth/login');
            }
            unfinishedProblemsResult = {
                data: null,
                error: {
                    status: error.response?.status || 500,
                    message: error.message || '加载题目失败'
                }
            };
        }

        return {
            enrolledCourses: enrolledCoursesResult,
            unfinishedProblems: unfinishedProblemsResult
        };
    } catch (error: any) {
        // Handle any unexpected errors (like 401 redirect)
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw error;
    }
}
clientLoader.hydrate = true as const;

/**
 * Hydrate fallback component
 * Shows while the client loader is hydrating
 */
export function HydrateFallback() {
    return <SkeletonHome />;
}

/**
 * Error boundary for client loader errors
 * Enhanced with friendly UI and retry functionality
 */
/**
 * Enhanced ErrorBoundary with better UI and retry functionality
 */
export function ErrorBoundary({ error }: { error: Error }) {
    // Extract status code from error message if available
    const getStatusFromError = (errorMessage: string): number => {
        const match = errorMessage.match(/\((\d{3})\)/);
        return match ? parseInt(match[1]) : 500;
    };

    const statusCode = getStatusFromError(error.message || '');
    const isRetriable = statusCode >= 500 || statusCode === 503 || statusCode === 504;

    return (
        <PageContainer maxWidth="lg">
            <Box sx={{ py: spacing.xl }}>
                {/* Error Icon */}
                <Box
                    sx={{
                        width: 80,
                        height: 80,
                        borderRadius: '50%',
                        bgcolor: 'error.main',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto ' + spacing.md,
                    }}
                >
                    <WarningIcon sx={{ fontSize: 48, color: 'error.contrastText' }} />
                </Box>

                <Typography color="error" variant="h6" gutterBottom align="center">
                    {statusCode === 401 ? '需要登录' : '页面加载失败'}
                </Typography>
                <Typography color="text.secondary" align="center" sx={{ mb: spacing.md }}>
                    {statusCode === 401
                        ? '您需要登录才能访问此页面'
                        : error.message || '无法加载页面数据，请稍后重试'
                    }
                </Typography>

                {/* Action Buttons */}
                <Stack
                    direction="row"
                    spacing={spacing.sm}
                    sx={{ mt: spacing.md, justifyContent: 'center' }}
                >
                    {isRetriable && (
                        <Button
                            variant="contained"
                            startIcon={<RefreshIcon />}
                            component="a"
                            href="."
                            sx={{
                                background: 'linear-gradient(135deg, primary.main 0%, primary.dark 100%)',
                                color: 'common.white',
                                borderRadius: 2,
                                boxShadow: 'shadows[2]',
                                fontWeight: 600,
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    boxShadow: 'shadows[3]',
                                    background: 'linear-gradient(135deg, primary.dark 0%, primary.main 100%)',
                                    transform: 'scale(1.05)',
                                },
                            }}
                        >
                            重新加载
                        </Button>
                    )}

                    <Button
                        variant="outlined"
                        startIcon={<HomeIcon />}
                        href="/home"
                        sx={{
                            borderRadius: 2,
                            fontWeight: 500,
                            transition: 'all 0.2s ease',
                            '&:hover': {
                                backgroundColor: 'primary.main',
                                borderColor: 'primary.main',
                                color: 'common.white',
                            },
                        }}
                    >
                        返回首页
                    </Button>
                </Stack>
            </Box>
        </PageContainer>
    );
}

export default function Home() {
    const {user}=useUser()
    const loaderData = useLoaderData<typeof clientLoader>();
    const enrolledCourses = loaderData.enrolledCourses;
    const unfinishedProblems = loaderData.unfinishedProblems;

    return (
        <>
            <title>{formatTitle(PAGE_TITLES.home(user?.username))}</title>
            <PageContainer maxWidth="lg">
                {/* 页面标题 */}
                <SectionContainer spacing="lg">
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                        <BookIcon sx={{ color: 'text.primary' }} />
                        <Typography variant="h3" component="h1" color="text.primary">
                            学习中心
                        </Typography>
                    </Box>
                    <Typography variant="subtitle1" color="text.secondary">
                        继续您的学习之旅
                    </Typography>
                </SectionContainer>

                {/* 我的课程区块 */}
                <CoursesSection initialData={enrolledCourses?.data} initialError={enrolledCourses?.error} />

                {/* 待解决问题区块 */}
                <ProblemsSection initialData={unfinishedProblems?.data} initialError={unfinishedProblems?.error} />
            </PageContainer>
        </>
    );
}

