import { useState } from "react";
import { Box, Card, Grid, Typography, Button, useTheme } from "@mui/material";
import { PlayArrow as PlayArrowIcon, Book as BookIcon } from "@mui/icons-material";
import { useNavigate } from "react-router";
import type { Page } from "~/types/page";
import type { Enrollment } from "~/types/course";
import { SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { ErrorCard } from "~/components/ErrorCard";
import { SkeletonHome } from "~/components/HydrateFallback";

interface ErrorInfo {
    status: number;
    message: string;
}

interface CoursesSectionProps {
    initialData: Page<Enrollment> | null;
    initialError: ErrorInfo | null;
}

/**
 * CoursesSection component - Displays enrolled courses with independent error handling
 *
 * Features:
 * - Independent loading, error, and data states
 * - Retry functionality for failed requests
 * - Empty state handling
 * - Reuses existing course card styling
 */
export function CoursesSection({ initialData, initialError }: CoursesSectionProps) {
    const theme = useTheme();
    const navigate = useNavigate();
    const [data, setData] = useState<Page<Enrollment> | null>(initialData);
    const [error, setError] = useState<ErrorInfo | null>(initialError);
    const [isLoading, setIsLoading] = useState(false);

    /**
     * Retry loading courses data
     */
    async function handleRetry() {
        setIsLoading(true);
        setError(null);

        try {
            // Dynamic import to avoid circular dependency
            const { clientHttp } = await import("~/utils/http/client");
            const result = await clientHttp.get<Page<Enrollment>>('enrollments/');
            setData(result);
            setError(null);
        } catch (err: any) {
            setError({
                status: err.response?.status || 500,
                message: err.message || '加载课程失败'
            });
        } finally {
            setIsLoading(false);
        }
    }

    // Show loading state
    if (isLoading) {
        return (
            <SectionContainer spacing="lg" variant="card">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <BookIcon sx={{ color: "text.primary" }} />
                    <Typography variant="h6" color="text.primary">我的课程</Typography>
                </Box>
                <CourseCardsSkeleton />
            </SectionContainer>
        );
    }

    // Show error state
    if (error) {
        return (
            <SectionContainer spacing="lg" variant="card">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <BookIcon sx={{ color: "text.primary" }} />
                    <Typography variant="h6" color="text.primary">我的课程</Typography>
                </Box>
                <ErrorCard
                    status={error.status}
                    message={error.message}
                    title="课程列表加载失败"
                    onRetry={handleRetry}
                    isLoading={isLoading}
                />
            </SectionContainer>
        );
    }

    // Show empty state
    if (!data || data.results.length === 0) {
        return (
            <SectionContainer spacing="lg" variant="card">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <BookIcon sx={{ color: "text.primary" }} />
                    <Typography variant="h6" color="text.primary">我的课程</Typography>
                </Box>
                <Grid container spacing={2}>
                    <Grid size={12}>
                        <Typography color="text.secondary" align="center" sx={{ py: spacing.xl }}>
                            暂无已报名课程
                        </Typography>
                    </Grid>
                </Grid>
            </SectionContainer>
        );
    }

    // Show normal state
    return (
        <SectionContainer spacing="lg" variant="card">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                <BookIcon sx={{ color: "text.primary" }} />
                <Typography variant="h6" color="text.primary">我的课程</Typography>
            </Box>

            <Grid container spacing={2}>
                {data.results.map((course) => (
                    <Grid size={{ xs: 12, md: 6 }} key={course.id}>
                        <Card
                            elevation={2}
                            sx={{
                                p: spacing.lg,
                                transition: 'background-color 0.3s ease, box-shadow 0.3s ease',
                                position: 'relative',
                                overflow: 'hidden',
                                cursor: 'pointer',
                                '&:hover': {
                                    elevation: 8,
                                    transform: 'translateY(-4px)',
                                },
                                '&:hover::before': {
                                    content: '""',
                                    position: 'absolute',
                                    top: 0,
                                    left: 0,
                                    right: 0,
                                    height: '3px',
                                    background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                                },
                            }}
                        >
                            {/* Progress indicator */}
                            <Box sx={{ mb: spacing.md }}>
                                <Typography
                                    variant="h6"
                                    component="div"
                                    sx={{
                                        fontWeight: 600,
                                        color: 'text.primary',
                                        fontSize: '1.125rem',
                                    }}
                                >
                                    {course.course_title}
                                </Typography>
                                <Typography
                                    variant="body2"
                                    sx={{ color: 'text.secondary' }}
                                >
                                    课程进度
                                </Typography>
                            </Box>

                            {/* Progress bar */}
                            <Box sx={{ mb: spacing.md }}>
                                <Box
                                    sx={{
                                        display: 'flex',
                                        justifyContent: 'space-between',
                                        alignItems: 'center',
                                        mb: spacing.sm,
                                    }}
                                >
                                    <Typography
                                        variant="body2"
                                        sx={{
                                            color: 'text.secondary',
                                        }}
                                    >
                                        {course.progress_percentage}%
                                    </Typography>
                                    <Typography
                                        variant="caption"
                                        sx={{
                                            color: 'text.disabled',
                                        }}
                                    >
                                        完成进度
                                    </Typography>
                                </Box>
                                <Box
                                    sx={{
                                        height: 8,
                                        borderRadius: 4,
                                        backgroundColor: theme.palette.mode === 'dark'
                                            ? theme.palette.grey[800]
                                            : theme.palette.grey[200],
                                        overflow: 'hidden',
                                    }}
                                >
                                    <Box
                                        sx={{
                                            height: '100%',
                                            width: `${course.progress_percentage}%`,
                                            background: `linear-gradient(90deg, ${theme.palette.primary.main}, ${theme.palette.primary.dark})`,
                                            transition: 'width 0.6s ease',
                                            borderRadius: 4,
                                        }}
                                    />
                                </Box>
                            </Box>

                            {/* Next chapter and button */}
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <Box>
                                    <Typography
                                        variant="body2"
                                        sx={{
                                            color: 'text.secondary',
                                            mt: spacing.sm,
                                        }}
                                    >
                                        下一章：{course.next_chapter?.title || '暂无'}
                                    </Typography>
                                </Box>
                                <Button
                                    variant="contained"
                                    size="small"
                                    startIcon={<PlayArrowIcon sx={{ color: "text.primary" }} />}
                                    onClick={() =>
                                        navigate(`/courses/${course.course}/chapters/${course.next_chapter?.id}`)
                                    }
                                    disabled={!course.next_chapter}
                                    sx={{
                                        background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
                                        color: 'common.white',
                                        borderRadius: 2,
                                        boxShadow: theme.shadows[2],
                                        fontWeight: 600,
                                        transition: 'all 0.2s ease',
                                        '&:hover': {
                                            transform: 'scale(1.05)',
                                            boxShadow: theme.shadows[3],
                                            background: `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.primary.main} 100%)`,
                                        },
                                    }}
                                >
                                    继续学习
                                </Button>
                            </Box>
                        </Card>
                    </Grid>
                ))}
            </Grid>
        </SectionContainer>
    );
}

/**
 * Skeleton loader for courses section
 * Reuses the skeleton component from SkeletonHome
 */
function CourseCardsSkeleton() {
    // Extract the skeleton part from SkeletonHome
    return (
        <Grid container spacing={2}>
            <CourseCardSkeleton />
            <CourseCardSkeleton />
        </Grid>
    );
}

function CourseCardSkeleton() {
    return (
        <Grid size={{ xs: 12, md: 6 }}>
            <Box
                sx={{
                    p: spacing.lg,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    bgcolor: 'background.paper',
                }}
            >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: spacing.md }}>
                    <Box sx={{ flex: 1 }}>
                        <Box sx={{ width: '70%', height: 28, mb: spacing.sm }}>
                            <Box sx={{ height: '100%', bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                        </Box>
                        <Box sx={{ width: '50%', height: 20 }}>
                            <Box sx={{ height: '100%', bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                        </Box>
                    </Box>
                    <Box sx={{ width: 80, height: 32, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                </Box>
                <Box sx={{ width: '100%', height: 20, mb: spacing.sm, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                <Box sx={{ width: '60%', height: 18, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
            </Box>
        </Grid>
    );
}
