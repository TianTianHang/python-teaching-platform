import { useState } from "react";
import React from "react";
import { Box, List, ListItem, ListItemIcon, ListItemText, Divider, Stack, Chip, Button, Typography } from "@mui/material";
import {
    CheckCircle as CheckCircleIcon,
    HourglassEmpty as HourglassEmptyIcon,
    Cancel as CancelIcon,
    RadioButtonUnchecked as RadioButtonUncheckedIcon,
    Code as CodeIcon,
    Quiz as QuizIcon
} from "@mui/icons-material";
import { useNavigate } from "react-router";
import type { Page } from "~/types/page";
import type { ProblemProgress } from "~/types/course";
import { SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { ErrorCard } from "~/components/ErrorCard";
import { getDifficultyLabel } from "~/utils/chips";

interface ErrorInfo {
    status: number;
    message: string;
}

interface ProblemsSectionProps {
    initialData: Page<ProblemProgress> | null;
    initialError: ErrorInfo | null;
}

/**
 * ProblemsSection component - Displays unfinished problems with independent error handling
 *
 * Features:
 * - Independent loading, error, and data states
 * - Retry functionality for failed requests
 * - Empty state handling
 * - Reuses existing problem list styling
 */
export function ProblemsSection({ initialData, initialError }: ProblemsSectionProps) {
    const navigate = useNavigate();
    const [data, setData] = useState<Page<ProblemProgress> | null>(initialData);
    const [error, setError] = useState<ErrorInfo | null>(initialError);
    const [isLoading, setIsLoading] = useState(false);

    /**
     * Retry loading problems data
     */
    async function handleRetry() {
        setIsLoading(true);
        setError(null);

        try {
            // Dynamic import to avoid circular dependency
            const { clientHttp } = await import("~/utils/http/client");
            const result = await clientHttp.get<Page<ProblemProgress>>('problem-progress/?status_not=solved');
            setData(result);
            setError(null);
        } catch (err: any) {
            setError({
                status: err.response?.status || 500,
                message: err.message || '加载题目失败'
            });
        } finally {
            setIsLoading(false);
        }
    }

    /**
     * Get status icon for problem
     */
    const getProblemStatusIcon = (status: string) => {
        switch (status) {
            case 'solved':
                return <CheckCircleIcon color="success" fontSize="small" sx={{ color: "text.primary" }} />;
            case 'in_progress':
                return <HourglassEmptyIcon color="warning" fontSize="small" sx={{ color: "text.primary" }} />;
            case 'failed':
                return <CancelIcon color="error" fontSize="small" sx={{ color: "text.primary" }} />;
            case 'not_started':
            default:
                return <RadioButtonUncheckedIcon color="disabled" fontSize="small" sx={{ color: "text.primary" }} />;
        }
    };

    /**
     * Get status chip for problem
     */
    const getProblemStatusChip = (status: string) => {
        const statusMap = {
            'solved': { label: '已解决', color: 'success' as const },
            'in_progress': { label: '进行中', color: 'warning' as const },
            'failed': { label: '未通过', color: 'error' as const },
            'not_started': { label: '未开始', color: 'default' as const },
        };
        const statusConfig = statusMap[status as keyof typeof statusMap] || statusMap['not_started'];

        return (
            <Chip
                label={statusConfig.label}
                color={statusConfig.color}
                size="small"
                variant="outlined"
                sx={{
                    fontWeight: 500,
                }}
            />
        );
    };

    // Show loading state
    if (isLoading) {
        return (
            <SectionContainer spacing="md">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <QuizIcon sx={{ color: "text.primary" }} />
                    <Typography variant="h6" color="text.primary">待解决问题</Typography>
                </Box>
                <ProblemsListSkeleton />
            </SectionContainer>
        );
    }

    // Show error state
    if (error) {
        return (
            <SectionContainer spacing="md">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <QuizIcon sx={{ color: "text.primary" }} />
                    <Typography variant="h6" color="text.primary">待解决问题</Typography>
                </Box>
                <ErrorCard
                    status={error.status}
                    message={error.message}
                    title="题目列表加载失败"
                    onRetry={handleRetry}
                    isLoading={isLoading}
                />
            </SectionContainer>
        );
    }

    // Show empty state
    if (!data || data.results.length === 0) {
        return (
            <SectionContainer spacing="md">
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <QuizIcon sx={{ color: "text.primary" }} />
                    <Typography variant="h6" color="text.primary">待解决问题</Typography>
                </Box>
                <List dense>
                    <ListItem>
                        <ListItemText
                            primary="暂无未完成题目"
                            slotProps={{ primary: { color: "text.secondary" } }}
                        />
                    </ListItem>
                </List>
            </SectionContainer>
        );
    }

    // Show normal state
    return (
        <SectionContainer spacing="md">
            <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                <QuizIcon sx={{ color: "text.primary" }} />
                <Typography variant="h6" color="text.primary">待解决问题</Typography>
            </Box>

            <List dense>
                {data.results.map((prob) => (
                    <React.Fragment key={prob.id}>
                        <ListItem
                            sx={{
                                padding: '0',
                                '& .MuiListItemAvatar-root': {
                                    minWidth: 40,
                                },
                                transition: 'all 0.2s ease',
                                '&:hover': {
                                    backgroundColor: 'action.hover',
                                },
                            }}
                        >
                            <ListItemIcon>
                                {getProblemStatusIcon(prob.status)}
                            </ListItemIcon>
                            <ListItemText
                                primary={
                                    <Stack direction="row" spacing={1} alignItems="center">
                                        <Typography
                                            variant="subtitle2"
                                            sx={{
                                                fontWeight: 600,
                                                color: 'text.primary',
                                                mr: spacing.sm,
                                            }}
                                        >
                                            {prob.problem_title}
                                        </Typography>
                                        {getDifficultyLabel(prob.problem_difficulty)}
                                        {getProblemStatusChip(prob.status)}
                                        <Chip
                                            label={prob.problem_type === 'algorithm' ? '算法题' : '选择题'}
                                            size="small"
                                            variant="outlined"
                                            color="info"
                                        />
                                    </Stack>
                                }
                                secondary={
                                    <Typography
                                        variant="body2"
                                        sx={{
                                            color: 'text.secondary',
                                            fontSize: '0.875rem',
                                        }}
                                    >
                                        {prob.problem_type === 'algorithm' ? '点击提交代码' : '点击作答'}
                                    </Typography>
                                }
                            />
                            <Button
                                size="small"
                                variant="outlined"
                                color="primary"
                                startIcon={prob.problem_type === 'algorithm' ? <CodeIcon sx={{ color: "text.primary" }} /> : <QuizIcon sx={{ color: "text.primary" }} />}
                                onClick={() => navigate(`/problems/${prob.problem}`)}
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
                                {prob.status === 'solved' ? '查看' : '开始'}
                            </Button>
                        </ListItem>
                        <Divider variant="inset" component="li" sx={{ margin: 0 }} />
                    </React.Fragment>
                ))}
            </List>
        </SectionContainer>
    );
}

/**
 * Skeleton loader for problems list
 */
function ProblemsListSkeleton() {
    return (
        <List sx={{ py: 0 }}>
            <ProblemListItemSkeleton />
            <ProblemListItemSkeleton />
            <ProblemListItemSkeleton />
        </List>
    );
}

function ProblemListItemSkeleton() {
    return (
        <>
            <ListItem>
                <ListItemIcon>
                    <Box sx={{ width: 24, height: 24, borderRadius: '50%', bgcolor: 'text.disabled', opacity: 0.1 }} />
                </ListItemIcon>
                <ListItemText
                    primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                            <Box sx={{ width: '40%', height: 20, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                            <Box sx={{ width: 40, height: 20, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                            <Box sx={{ width: 60, height: 20, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
                        </Box>
                    }
                    secondary={<Box sx={{ width: '30%', height: 16, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />}
                />
                <Box sx={{ width: 60, height: 32, bgcolor: 'text.disabled', opacity: 0.1, borderRadius: 1 }} />
            </ListItem>
            <Divider variant="inset" component="li" />
        </>
    );
}
