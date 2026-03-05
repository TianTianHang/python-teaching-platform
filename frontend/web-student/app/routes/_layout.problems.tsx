import type { Problem } from "~/types/course";
import { clientHttp } from "~/utils/http/client";
import type { Page } from "~/types/page";
import { Box, Button, List, ListItem, ListItemIcon, Pagination, Stack, Typography } from "@mui/material";
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import { Code, Quiz, Edit, Lock as LockIcon } from "@mui/icons-material";
import { PageContainer, PageHeader, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { formatDateTime } from "~/utils/time";
import { useNavigate, useSearchParams, useLoaderData } from "react-router";
import { redirect } from "react-router";
import React from "react";
import ProblemFilters, { type FilterState } from "~/components/Problem/ProblemFilters";
import { SkeletonProblems } from "~/components/HydrateFallback";
import type { Route } from "./+types/_layout.problems";

export function headers(): Headers | HeadersInit {
    return {
        "Cache-Control": "public, max-age=300, s-maxage=600, stale-while-revalidate=3600",
        "Vary": "Accept-Encoding",
    };
}

export async function clientLoader({ request }: Route.ClientLoaderArgs) {
    const url = new URL(request.url);
    const page = url.searchParams.get("page") || "1";
    const type = url.searchParams.get("type");
    const difficulty = url.searchParams.get("difficulty");
    const ordering = url.searchParams.get("ordering");
    const pageSize = "10";
    
    const queryParams = new URLSearchParams();
    queryParams.set("page", page);
    queryParams.set("page_size", pageSize);
    queryParams.set("exclude", "content,recent_threads,status,chapter_title,updated_at");
    if (type) queryParams.set("type", type);
    if (difficulty) queryParams.set("difficulty", difficulty);
    if (ordering) queryParams.set("ordering", ordering);
    
    try {
        const data = await clientHttp.get<Page<Problem>>(`/problems/?${queryParams.toString()}`);
        return data;
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

export function HydrateFallback() {
    return (
        <>
            <title>{formatTitle(PAGE_TITLES.problems)}</title>
            <PageContainer maxWidth="md">
                <PageHeader title="Problem Set" subtitle="浏览和解决编程题目" />
                <SectionContainer spacing="md" variant="card">
                    <ProblemFilters currentType={null} currentDifficulty={null} currentOrdering={null} onFilterChange={() => {}} />
                </SectionContainer>
                <SectionContainer spacing="md" variant="card">
                    <SkeletonProblems />
                </SectionContainer>
            </PageContainer>
        </>
    );
}

export function ErrorBoundary({ error }: { error: Error }) {
    return (
        <PageContainer maxWidth="md">
            <Box sx={{ py: spacing.xl }}>
                <Typography color="error" variant="h6" gutterBottom>
                    加载失败
                </Typography>
                <Typography color="text.secondary">
                    {error.message || '无法加载题目列表'}
                </Typography>
                <Box sx={{ mt: 2 }}>
                    <Button variant="outlined" onClick={() => window.location.reload()}>
                        重试
                    </Button>
                </Box>
            </Box>
        </PageContainer>
    );
}

export default function ProblemListPage() {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const pageData = useLoaderData<typeof clientLoader>();

    const currentPage = parseInt(searchParams.get("page") || "1", 10);
    const currentType = searchParams.get("type");
    const currentDifficulty = searchParams.get("difficulty");
    const currentOrdering = searchParams.get("ordering") || "";
    const actualPageSize = pageData.page_size || 10;
    const totalItems = pageData.count ?? 0;
    const totalPages = Math.ceil(totalItems / actualPageSize);

    const getTypeLabel = (type: string) => {
        switch (type) {
            case 'algorithm': return '算法题';
            case 'choice': return '选择题';
            case 'fillblank': return '填空题';
            default: return '未知';
        }
    };

    const getIcon = (type: string) => {
        switch (type) {
            case 'algorithm': return <Code sx={{ color: 'text.primary' }} />;
            case 'choice': return <Quiz sx={{ color: 'text.primary' }} />;
            case 'fillblank': return <Edit sx={{ color: 'text.primary' }} />;
            default: return <Code sx={{ color: 'text.primary' }} />;
        }
    };
    const onClick = (id: number) => {
        navigate(`/problems/${id}`)
    }
    // 处理筛选变化的函数
    const handleFilterChange = (filters: FilterState) => {
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("page", "1"); // 重置到第一页
        newSearchParams.set("page_size", actualPageSize.toString());
        if (filters.type) newSearchParams.set("type", filters.type);
        if (filters.difficulty) newSearchParams.set("difficulty", filters.difficulty);
        if (filters.ordering) newSearchParams.set("ordering", filters.ordering);
        navigate(`/problems/?${newSearchParams.toString()}`);
    };
    // 处理页码变化的函数
    const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
        // 构建新的 URL
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("page", value.toString());
        newSearchParams.set("page_size", actualPageSize.toString()); // 保持 pageSize
        if (currentType) {
            newSearchParams.set("type", currentType); // 保持 type 参数
        }
        if (currentDifficulty) {
            newSearchParams.set("difficulty", currentDifficulty); // 保持 difficulty 参数
        }
        if (currentOrdering) {
            newSearchParams.set("ordering", currentOrdering); // 保持 ordering 参数
        }
        navigate(`/problems/?${newSearchParams.toString()}`);
    };

    return (
        <>
            <title>{formatTitle(PAGE_TITLES.problems)}</title>
            <PageContainer maxWidth="md">
                <PageHeader
                    title="Problem Set"
                    subtitle="浏览和解决编程题目"
                />
                <SectionContainer spacing="md" variant="card">
                    <ProblemFilters
                        currentType={currentType}
                        currentDifficulty={currentDifficulty}
                        currentOrdering={currentOrdering}
                        onFilterChange={handleFilterChange}
                    />
                </SectionContainer>
                <SectionContainer spacing="md" variant="card">
                    <List sx={{ py: 0 }}>
                        {pageData.results.map((problem) => (
                            <ListItem
                                onClick={() => {
                                    if (problem.is_unlocked) {
                                        onClick(problem.id);
                                    }
                                }}
                                key={problem.id}
                                sx={{
                                    px: 2,
                                    py: 1.5,
                                    borderTop: '1px solid',
                                    borderColor: 'divider',
                                    transition: 'background-color 0.2s',
                                    '&:hover': {
                                        bgcolor: problem.is_unlocked ? 'action.hover' : 'action.disabledBackground'
                                    },
                                    opacity: problem.is_unlocked ? 1 : 0.6,
                                    cursor: problem.is_unlocked ? 'pointer' : 'not-allowed',
                                }}
                                title={problem.is_unlocked ? undefined :
                                    (problem.unlock_condition_description.is_prerequisite_required
                                        ? `需要完成的前置题目: ${problem.unlock_condition_description.prerequisite_problems.map(p => p.title).join(', ')}`
                                        : undefined)
                                }
                            >
                                <ListItemIcon sx={{ minWidth: 100, color: problem.is_unlocked ? 'text.primary' : 'action.disabled' }}>
                                    {problem.is_unlocked ? (
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                            {getIcon(problem.type)}
                                            <Typography variant="caption" sx={{ color: 'text.secondary', fontSize: '0.75rem' }}>
                                                {getTypeLabel(problem.type)}
                                            </Typography>
                                        </Box>
                                    ) : (
                                        <LockIcon sx={{ color: 'action.disabled' }} fontSize="small" />
                                    )}
                                </ListItemIcon>

                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                                    <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                                        <Typography
                                            variant="subtitle1"
                                            fontWeight={500}
                                            noWrap
                                            sx={{
                                                color: problem.is_unlocked ? 'text.primary' : 'text.disabled',
                                                textDecoration: problem.is_unlocked ? 'none' : 'line-through'
                                            }}
                                        >
                                            {problem.title}
                                        </Typography>
                                        {!problem.is_unlocked && problem.unlock_condition_description && (
                                            <Typography
                                                variant="caption"
                                                color="text.secondary"
                                                sx={{ mt: 0.5 }}
                                            >
                                                {problem.unlock_condition_description.type_display}:
                                                {problem.unlock_condition_description.is_prerequisite_required &&
                                                    ` 需要完成 ${problem.unlock_condition_description.prerequisite_count || 0} 个前置题目`}
                                                {problem.unlock_condition_description.is_date_required &&
                                                    ` 解锁日期: ${problem.unlock_condition_description.unlock_date ? new Date(problem.unlock_condition_description.unlock_date).toLocaleString() : ''}`}
                                            </Typography>
                                        )}
                                    </Box>
                                    <Typography variant="caption" color={problem.is_unlocked ? "text.disabled" : "text.secondary"}>
                                        {formatDateTime(problem.created_at)}
                                    </Typography>
                                </Box>
                            </ListItem>
                        ))}
                    </List>
                </SectionContainer>

                {totalPages > 1 && (
                    <Stack spacing={spacing.sm} sx={{ mt: spacing.lg, mb: spacing.md, alignItems: 'center' }}>
                        <Pagination
                            count={totalPages}
                            page={currentPage}
                            onChange={handlePageChange}
                            color="primary"
                            showFirstButton
                            showLastButton
                        />
                    </Stack>
                )}
            </PageContainer>
        </>
    );
}

