import type { Problem } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { Box, List, ListItem, ListItemIcon, Pagination, Stack, Typography } from "@mui/material";
import { Code, Quiz, Edit, Lock as LockIcon } from "@mui/icons-material";
import { PageContainer, PageHeader, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { formatDateTime } from "~/utils/time";
import { Await, useNavigate } from "react-router";
import type { Route } from "./+types/_layout.problems";
import { withAuth } from "~/utils/loaderWrapper";
import React, { useState } from "react";
import ResolveError from "~/components/ResolveError";
import type { AxiosError } from "axios";
import ProblemFilters, { type FilterState } from "~/components/Problem/ProblemFilters";
export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  const url = new URL(request.url);
  const searchParams = url.searchParams;
  const type = searchParams.get("type");
  const difficulty = searchParams.get("difficulty");
  const ordering = searchParams.get("ordering") || "";
  // 将 page 参数解析为数字，如果不存在则默认为 1
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10); // 可以添加 page_size 参数，默认为10
  // 构建查询参数对象
  const queryParams = new URLSearchParams();
  queryParams.set("page", page.toString());
  queryParams.set("page_size", pageSize.toString()); // 添加 pageSize 到查询参数
  if (type !== null) queryParams.set("type", type);
  if (difficulty !== null) queryParams.set("difficulty", difficulty);
  if (ordering !== "") queryParams.set("ordering", ordering);
  const http = createHttp(request);
  const problems = http.get<Page<Problem>>(`/problems/?${queryParams.toString()}`)
    .catch((e: AxiosError) => {
      return {
        status: e.status,
        message: e.message,
      }
    });;
  // 返回 currentPage, totalItems 和 actualPageSize
  return {
    pageData: problems,
    currentPage: page,
    currentType: type,
    currentDifficulty: difficulty,
    currentOrdering: ordering,
  };
})

export default function ProblemListPage({ loaderData }: Route.ComponentProps) {
  const currentPage = loaderData.currentPage;
  const currentType = loaderData.currentType;
  const currentDifficulty = loaderData.currentDifficulty;
  const currentOrdering = loaderData.currentOrdering;
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [totalItems, setTotalItems] = useState<number>(0);
  const [actualPageSize, setActualPageSize] = useState<number>(10)
  const [totalPages, setTotalPages] = useState<number>(1)
  const navigate = useNavigate();
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
          <React.Suspense >
            <Await
              resolve={loaderData.pageData}

              children={(resolved) => {
                if ('status' in resolved) {
                  return (
                    <ResolveError status={resolved.status} message={resolved.message}>
                      <Typography>出错了</Typography>
                    </ResolveError>)
                }
                const data = resolved.results
                const newTotalItems = resolved.count ?? 0;
                const newActualPageSize = resolved.page_size || 10;
                const newTotalPages = Math.ceil(newTotalItems / newActualPageSize);
                queueMicrotask(() => {
                  setTotalItems(newTotalItems);
                  setActualPageSize(newActualPageSize);
                  setTotalPages(newTotalPages);

                });
                return (
                  <>{
                    data.map((problem) => (
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
                          // 上下都加 divider（用 ::before 伪元素或直接 border）
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

                        {/* 主内容区域：标题在左，时间在右 */}
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
                    ))
                  }
                  </>
                )
              }}


            />
          </React.Suspense>

        </List>
      </SectionContainer>

      {/* 添加分页组件 */}
      {totalPages > 1 && ( // 只有当总页数大于1时才显示分页
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

  )
}