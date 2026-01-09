import {
  Box,
  Typography,
  Container,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Drawer,
  Toolbar,
  Divider,
  useTheme,
  useMediaQuery,
  Button,
  CircularProgress,
  } from '@mui/material';
import type { Chapter, ChoiceProblem, Problem } from '~/types/course'; // 确保路径正确
import { formatDateTime } from '~/utils/time';
import type { Route } from "./+types/route"
import { createHttp } from '~/utils/http/index.server';
import ProblemRenderer from '~/components/Problem'; // 确保 ProblemRenderer 的导入路径正确
import type { Page } from '~/types/page';
import ChoiceProblemCmp from '~/components/Problem/ChoiceProblemCmp';
import { Await, useFetcher, useNavigate } from 'react-router';
import { showNotification } from '~/components/Notification';
import { withAuth } from '~/utils/loaderWrapper';
import MarkdownRenderer from '~/components/MarkdownRenderer';
import React from 'react';
import ProblemsSkeleton from '~/components/skeleton/ProblemsSkeleton';
import ResolveError from '~/components/ResolveError';
import { PageContainer, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import type { AxiosError } from 'axios';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.chapter.title || "Error" },
  ];
}
export const action = withAuth(async ({ request, params }) => {
  const http = createHttp(request);
  await http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: true });
  return { message: "已完成" };
});

export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);
  const chapter = await http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
  if (chapter.status == "not_started") {
    await http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: false });
  }
  const problems = http.get<Page<Problem>>(`/courses/${params.courseId}/chapters/${params.chapterId}/problems`)
    .catch((e: AxiosError) => {
      return {
        status: e.status,
        message: e.message,
      }
    });;
  const courseChapters = http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters`)
    .catch((e: AxiosError) => {
      return {
        status: e.status,
        message: e.message,
      }
    });;
  return { chapter, problems, courseChapters };
});

export default function ChapterDetail({ loaderData, params, actionData }: Route.ComponentProps) {
  const { chapter, problems, courseChapters } = loaderData;
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  if (actionData?.message) {
    showNotification("success", "", actionData.message)
  }
  const handleChapterSelect = (chapterId: number) => {
    navigate(`/courses/${params.courseId}/chapters/${chapterId}`);
  };

  const fetcher = useFetcher()
  const sidebarContent = (
    <>
      <Toolbar />
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" component="h2" gutterBottom>
          课程章节
        </Typography>
        <Divider sx={{ mb: 2 }} />
      </Box>
      <React.Suspense fallback={<CircularProgress />}>
        <Await
          resolve={courseChapters}

          children={(resolvedCourseChapters) => {
            if ('status' in resolvedCourseChapters) {
              return (
                <ResolveError status={resolvedCourseChapters.status} message={resolvedCourseChapters.message}>
                  <Typography variant="inherit">Could not load chapters 😬</Typography>
                </ResolveError>)
            }
            return (
              <List>
                {resolvedCourseChapters.results.map((ch) => (
                  <ListItem
                    key={ch.id}
                    disablePadding
                    sx={{
                      backgroundColor: ch.id === chapter.id ? 'action.selected' : 'transparent',
                      '&:hover': { backgroundColor: 'action.hover' }
                    }}
                  >
                    <ListItemButton
                      onClick={() => handleChapterSelect(ch.id)}
                      selected={ch.id === chapter.id}
                    >
                      <ListItemText
                        primary={ch.title}
                        slotProps={{
                          primary: {
                            noWrap: true,
                            sx: {
                              fontWeight: ch.id === chapter.id ? 'bold' : 'normal',
                            }
                          }
                        }}
                      />
                    </ListItemButton>
                  </ListItem>
                ))}
              </List>
            )
          }}
        />
      </React.Suspense>
    </>
  );

  return (
    <PageContainer disableTopSpacing>
      <Box sx={{ display: 'flex', height: '100%' }}>
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={true}
            onClose={() => { }}
            ModalProps={{ keepMounted: true }}
            sx={{
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280, pt: 8 },
            }}
          >
            {sidebarContent}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            sx={{
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280, pt: 8, borderRight: '1px solid rgba(0, 0, 0, 0.12)' },
            }}
          >
            {sidebarContent}
          </Drawer>
        )}

      {/* 主内容区 */}
      <Box component="main" sx={{ flexGrow: 1, ml: isMobile ? 0 : 35, p: spacing.md }}>
        {/* 页面标题 */}
        <Box sx={{ mb: spacing.md }}>
          <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
            {chapter.title}
          </Typography>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            课程: {chapter.course_title}
          </Typography>
        </Box>

        <SectionContainer spacing="lg" variant="card">
          <MarkdownRenderer markdownContent={chapter.content} />
          {chapter.status !== 'completed' && (
            <Box sx={{ mt: spacing.md }}>
              <fetcher.Form method="post" action={`/courses/${params.courseId}/chapters/${params.chapterId}/`}>
                <input type="hidden" name="completed" value="true" />
                <Button
                  type="submit"
                  variant="contained"
                  color="success"
                  disabled={fetcher.state !== 'idle'}
                  startIcon={fetcher.state !== 'idle' ? <CircularProgress size={20} /> : null}
                >
                  {fetcher.state !== 'idle' ? '提交中...' : '标记为已完成'}
                </Button>
              </fetcher.Form>
            </Box>
          )}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: spacing.lg }}>
            <Typography variant="caption" color="text.disabled">
              创建于: {formatDateTime(chapter.created_at)}
            </Typography>
            <Typography variant="caption" color="text.disabled">
              最后更新: {formatDateTime(chapter.updated_at)}
            </Typography>
          </Box>
        </SectionContainer>

        {/* 这里渲染题目列表，不使用 ProblemListRenderer */}
        <SectionContainer spacing="md" variant="card" sx={{ mt: spacing.md }}>
          <Box sx={{ mb: spacing.md }}>
            <Typography variant="h5" component="h2" color="text.primary" gutterBottom>
              相关题目
            </Typography>
          </Box>
          <React.Suspense fallback={<ProblemsSkeleton />}>
            <Await
              resolve={problems}
              children={(resolvedProblems) => {
                if ('status' in resolvedProblems) {
                  return (
                    <ResolveError status={resolvedProblems.status} message={resolvedProblems.message}>
                      <Typography variant="inherit">无法加载相关题目 😬</Typography>
                    </ResolveError>)
                }
                return (
                  resolvedProblems.results.length > 0 ? (
                    <Box>
                      {resolvedProblems.results.map((problem) => {
                        if (problem.type === 'choice') {
                          return (
                            <ChoiceProblemCmp
                              problem={problem as ChoiceProblem}
                              key={problem.id}
                            />
                          );
                        } else {
                          return (
                            <SectionContainer spacing="sm" variant="plain" key={problem.id} sx={{ mb: spacing.sm }}>
                              <ProblemRenderer problem={problem} />
                            </SectionContainer>
                          );
                        }
                      })}
                    </Box>
                  ) : (
                    <Typography color="text.secondary" align="center" sx={{ py: spacing.lg }}>
                      暂无相关题目
                    </Typography>
                  )
                )
              }}
            />
          </React.Suspense>
        </SectionContainer>
        </Box>
      </Box>
    </PageContainer>
  );
}
