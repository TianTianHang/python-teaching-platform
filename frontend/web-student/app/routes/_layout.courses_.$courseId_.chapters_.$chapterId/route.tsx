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
import { clientHttp } from '~/utils/http/client';
import ProblemRenderer from '~/components/Problem';
import type { Page } from '~/types/page';
import ChoiceProblemCmp from '~/components/Problem/ChoiceProblemCmp';
import FillBlankProblemCmp from '~/components/Problem/FillBlankProblemCmp';
import { Await, redirect, useFetcher, useNavigate, useLoaderData, Link } from 'react-router';
import { ChapterSidebar } from '~/components/ChapterSidebar';
import { showNotification } from '~/components/Notification';
import MarkdownRenderer from '~/components/MarkdownRenderer';
import React, { useEffect } from 'react';
import ProblemsSkeleton from '~/components/skeleton/ProblemsSkeleton';
import ResolveError from '~/components/ResolveError';
import { PageContainer, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import type { AxiosError } from 'axios';
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import ChapterTitleSkeleton from '~/components/skeleton/ChapterTitleSkeleton';
import ChapterContentSkeleton from '~/components/skeleton/ChapterContentSkeleton';
import SidebarSkeleton from '~/components/skeleton/SidebarSkeleton';
import SkeletonChapterDetail from '~/components/skeleton/SkeletonChapterDetail';

export async function clientAction({ request, params }: Route.ClientActionArgs) {
  try {
    await clientHttp.post(`/courses/${params.courseId}/chapters/${params.chapterId}/mark_as_completed/`, { completed: true });
    return { message: "已完成" };
  } catch (error: any) {
    if (error.response?.status === 401) {
      throw redirect('/auth/login');
    }
    throw error;
  }
};

/**
 * Client loader with hydration enabled
 * Fetches chapter unlock status, content, and related data on client-side
 */
export async function clientLoader({ params, request }: Route.ClientLoaderArgs) {
  try {
    // Check unlock status first
    const unlockStatus = await clientHttp.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`)
      .catch((e: AxiosError) => {
        // Treat errors as locked
        return {
          is_locked: true,
          chapter: null,
          reason: e.message || '无法检查章节状态',
        };
      });

    // Return unlock status along with other data
    // Don't redirect here - let component handle it
    return {
      isLocked: unlockStatus.is_locked || false,
      unlockStatus,
      chapter: clientHttp.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`),
      problems: clientHttp.get<Page<Problem>>(`/courses/${params.courseId}/chapters/${params.chapterId}/problems?exclude=recent_threads`)
        .catch((e: AxiosError) => ({
          status: e.status,
          message: e.message,
        })),
      courseChapters: clientHttp.get<Page<Chapter>>(`/courses/${params.courseId}/chapters?exclude=content`)
        .catch((e: AxiosError) => ({
          status: e.status || 500,
          message: e.message,
        })),
    };
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
      <title>{formatTitle('章节详情')}</title>
      <SkeletonChapterDetail />
    </>
  );
}

/**
 * Error boundary for client loader errors
 */
export function ErrorBoundary({ error }: { error: Error }) {
  return (
    <PageContainer disableTopSpacing>
      <Box sx={{ p: spacing.xl }}>
        <Typography color="error" variant="h6" gutterBottom>
          加载失败
        </Typography>
        <Typography color="text.secondary">
          {error.message || '无法加载章节内容'}
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button variant="outlined" component={Link} to=".">
            重试
          </Button>
        </Box>
      </Box>
    </PageContainer>
  );
}

export default function ChapterDetail({ params, actionData }: Route.ComponentProps) {
  const loaderData = useLoaderData<typeof clientLoader>();
  const { isLocked, chapter, problems, courseChapters } = loaderData;
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const fetcher = useFetcher()

  // Client-side redirect based on lock status
  useEffect(() => {
    if (isLocked) {
      navigate(`/courses/${params.courseId}/chapters/${params.chapterId}/locked`, { replace: true });
    }
  }, [isLocked, navigate, params.courseId, params.chapterId]);

  // Don't render anything if locked (redirecting)
  if (isLocked) {
    return null;
  }

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
                      <ChapterSidebar
                        initialData={resolved}
                        courseId={params.courseId}
                        currentChapterId={Number(params.chapterId)}
                        onChapterSelect={handleChapterSelect}
                      />
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
                      <ChapterSidebar
                        initialData={resolved}
                        courseId={params.courseId}
                        currentChapterId={Number(params.chapterId)}
                        onChapterSelect={handleChapterSelect}
                      />
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
                            //console.log(problem)
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
