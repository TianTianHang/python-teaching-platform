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
import type { Chapter, ChapterUnlockStatus, ChoiceProblem, FillBlankProblem, Problem } from '~/types/course';
import { formatDateTime } from '~/utils/time';
import type { Route } from "./+types/route"
import { createHttp } from '~/utils/http/index.server';
import ProblemRenderer from '~/components/Problem';
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
import ChapterTitleSkeleton from '~/components/skeleton/ChapterTitleSkeleton';
import ChapterContentSkeleton from '~/components/skeleton/ChapterContentSkeleton';
import SidebarSkeleton from '~/components/skeleton/SidebarSkeleton';

export const action = withAuth(async ({ request, params }) => {
  const http = createHttp(request);
  await http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: true });
  return { message: "已完成" };
});

export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);

  // Check unlock status first (must wait - required for redirect decision)
  const unlockStatus = await http.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`)
  if (unlockStatus.is_locked) {
    return redirect(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`)
  }

  // Return Promises without awaiting - enables streaming
  // Priority: chapter (P1) > problems (P2) > courseChapters (P3)
  const chapter = http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
  const problems = http.get<Page<Problem>>(`/courses/${params.courseId}/chapters/${params.chapterId}/problems?exclude=content,recent_threads,status`)
    .catch((e: AxiosError) => ({
      status: e.status,
      message: e.message,
    }));
  const courseChapters = http.get<Page<Chapter>>(`/courses/${params.courseId}/chapters?exclude=content`)
    .catch((e: AxiosError) => ({
      status: e.status || 500,
      message: e.message,
    }));

  // Fire-and-forget: mark chapter as started (doesn't block response)
  chapter.then(ch => {
    if (ch.status === "not_started") {
      http.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: false })
        .catch(() => {
          // Silently handle error - this doesn't affect user experience
        });
    }
  });

  return { chapter, problems, courseChapters };
});

export default function ChapterDetail({ loaderData, params, actionData }: Route.ComponentProps) {
  const { chapter, problems, courseChapters } = loaderData;
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const fetcher = useFetcher()

  if (actionData?.message) {
    showNotification("success", "", actionData.message)
  }

  const handleChapterSelect = (chapterId: number) => {
    navigate(`/courses/${params.courseId}/chapters/${chapterId}`);
  };

  return (
    <>
      <React.Suspense fallback={<title>{formatTitle('章节详情')}</title>}>
        <Await resolve={chapter}>
          {(resolved) => (
            <title>{formatTitle(PAGE_TITLES.chapter(resolved.title, resolved.course_title))}</title>
          )}
        </Await>
      </React.Suspense>

      <PageContainer disableTopSpacing>
        <Box sx={{ display: 'flex', height: '100%' }}>
          {/* Sidebar with streaming */}
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
              <React.Suspense fallback={<SidebarSkeleton />}>
                <Await resolve={courseChapters}>
                  {(resolved) => {
                    if ('status' in resolved) {
                      return (
                        <>
                          <Toolbar />
                          <Box sx={{ p: 2 }}>
                            <Typography variant="h6" component="h2" gutterBottom>
                              课程章节
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                          </Box>
                          <ResolveError status={resolved.status} message={resolved.message}>
                            <Typography variant="inherit">无法加载章节列表 😬</Typography>
                          </ResolveError>
                        </>
                      );
                    }
                    return (
                      <Await resolve={chapter}>
                        {(resolvedChapter) => (
                          <ChapterSidebar
                            initialData={resolved}
                            courseId={params.courseId}
                            currentChapterId={resolvedChapter.id}
                            onChapterSelect={handleChapterSelect}
                          />
                        )}
                      </Await>
                    );
                  }}
                </Await>
              </React.Suspense>
            </Drawer>
          ) : (
            <Drawer
              variant="permanent"
              sx={{
                '& .MuiDrawer-paper': { boxSizing: 'border-box', width: 280, pt: 8, borderRight: '1px solid rgba(0, 0, 0, 0.12)' },
              }}
            >
              <React.Suspense fallback={<SidebarSkeleton />}>
                <Await resolve={courseChapters}>
                  {(resolved) => {
                    if ('status' in resolved) {
                      return (
                        <>
                          <Toolbar />
                          <Box sx={{ p: 2 }}>
                            <Typography variant="h6" component="h2" gutterBottom>
                              课程章节
                            </Typography>
                            <Divider sx={{ mb: 2 }} />
                          </Box>
                          <ResolveError status={resolved.status} message={resolved.message}>
                            <Typography variant="inherit">无法加载章节列表 😬</Typography>
                          </ResolveError>
                        </>
                      );
                    }
                    return (
                      <Await resolve={chapter}>
                        {(resolvedChapter) => (
                          <ChapterSidebar
                            initialData={resolved}
                            courseId={params.courseId}
                            currentChapterId={resolvedChapter.id}
                            onChapterSelect={handleChapterSelect}
                          />
                        )}
                      </Await>
                    );
                  }}
                </Await>
              </React.Suspense>
            </Drawer>
          )}

          {/* Main content area with streaming */}
          <Box component="main" sx={{ flexGrow: 1, ml: isMobile ? 0 : 35, p: spacing.md }}>
            {/* Chapter title with independent Suspense boundary */}
            <React.Suspense fallback={<ChapterTitleSkeleton />}>
              <Await resolve={chapter}>
                {(resolved) => (
                  <Box sx={{ mb: spacing.md }}>
                    <Typography variant="h4" component="h1" color="text.primary" gutterBottom>
                      {resolved.title}
                    </Typography>
                    <Typography variant="h6" color="text.secondary" gutterBottom>
                      课程: {resolved.course_title}
                    </Typography>
                  </Box>
                )}
              </Await>
            </React.Suspense>

            {/* Chapter content with independent Suspense boundary */}
            <React.Suspense fallback={<ChapterContentSkeleton />}>
              <Await resolve={chapter}>
                {(resolved) => (
                  <SectionContainer spacing="lg" variant="card">
                    <MarkdownRenderer markdownContent={resolved.content} />
                    {resolved.status !== 'completed' && (
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
                        创建于: {formatDateTime(resolved.created_at)}
                      </Typography>
                      <Typography variant="caption" color="text.disabled">
                        最后更新: {formatDateTime(resolved.updated_at)}
                      </Typography>
                    </Box>
                  </SectionContainer>
                )}
              </Await>
            </React.Suspense>

            {/* Problems list with independent Suspense boundary */}
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
