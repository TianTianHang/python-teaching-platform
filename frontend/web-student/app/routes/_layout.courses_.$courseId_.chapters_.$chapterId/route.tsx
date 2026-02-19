import {
  Box,
  Typography,
  Drawer,
  Toolbar,
  Divider,
  useTheme,
  useMediaQuery,
  Button,
  CircularProgress,
} from '@mui/material';
import type { Chapter, ChapterUnlockStatus, ChoiceProblem, FillBlankProblem, Problem } from '~/types/course'; // 确保路径正确
import { formatDateTime } from '~/utils/time';
import type { Route } from "./+types/route"
import { createHttp } from '~/utils/http/index.server';
import ProblemRenderer from '~/components/Problem'; // 确保 ProblemRenderer 的导入路径正确
import type { Page } from '~/types/page';
import ChoiceProblemCmp from '~/components/Problem/ChoiceProblemCmp';
import FillBlankProblemCmp from '~/components/Problem/FillBlankProblemCmp';
import { Await, redirect, useFetcher, useNavigate } from 'react-router';
import { ChapterSidebar } from '~/components/ChapterSidebar';
import { showNotification } from '~/components/Notification';
import { withAuth } from '~/utils/loaderWrapper';
import MarkdownRenderer from '~/components/MarkdownRenderer';
import React from 'react';
import ProblemsSkeleton from '~/components/skeleton/ProblemsSkeleton';
import ResolveError from '~/components/ResolveError';
import { PageContainer, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import type { AxiosError } from 'axios';
import { formatTitle, PAGE_TITLES } from '~/config/meta';

export const action = withAuth(async ({ request, params }) => {
  const http = createHttp(request);
  await http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: true });
  return { message: "已完成" };
});

export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);
  // Fetch unlock status for the chapter
  const unlockStatus = await http.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`)
  if (unlockStatus.is_locked) {
    return redirect(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`)
  }
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

  // Fetch course chapters directly (not as a promise) for infinite scroll
  let courseChapters: Page<Chapter> | { status: number; message: string };
  try {
    courseChapters = await http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters`);
  } catch (e: unknown) {
    const error = e as AxiosError;
    courseChapters = {
      status: error.status || 500,
      message: error.message,
    };
  }

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

  // Render sidebar content with infinite scroll
  const renderSidebarContent = () => {
    if ('status' in courseChapters) {
      return (
        <>
          <Toolbar />
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" component="h2" gutterBottom>
              课程章节
            </Typography>
            <Divider sx={{ mb: 2 }} />
          </Box>
          <ResolveError status={courseChapters.status} message={courseChapters.message}>
            <Typography variant="inherit">Could not load chapters 😬</Typography>
          </ResolveError>
        </>
      );
    }

    return (
      <ChapterSidebar
        initialData={courseChapters}
        courseId={params.courseId}
        currentChapterId={chapter.id}
        onChapterSelect={handleChapterSelect}
      />
    );
  };

  return (
    <>
      <title>{formatTitle(PAGE_TITLES.chapter(chapter.title, chapter.course_title))}</title>
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
            {renderSidebarContent()}
          </Drawer>
        ) : (
          <Drawer
            variant="permanent"
            sx={{
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280, pt: 8, borderRight: '1px solid rgba(0, 0, 0, 0.12)' },
            }}
          >
            {renderSidebarContent()}
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
                          } else if (problem.type === 'fillblank') {
                            return (
                              <FillBlankProblemCmp
                                problem={problem as FillBlankProblem}
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
    </>
  );
}
