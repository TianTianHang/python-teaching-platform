import {
  Typography,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Grid,
  Button,
  Chip,
  IconButton,
  Tooltip,
  CircularProgress,
  Box,
  type ChipProps,
} from '@mui/material';
import type { Chapter, Course } from "~/types/course";
import type { Route } from "./+types/route"
import { clientHttp } from '~/utils/http/client';
import type { Page } from "~/types/page";
import { useNavigate, useLoaderData, Link, redirect } from 'react-router';
import { PageContainer, PageHeader, SectionContainer } from '~/components/Layout';
import { spacing } from '~/design-system/tokens';
import { Lock as LockIcon, Info as InfoIcon } from '@mui/icons-material';
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import { useInfiniteScroll } from '~/hooks/useInfiniteScroll';
import SkeletonChapterList from '~/components/skeleton/SkeletonChapterList';

/**
 * Route headers for HTTP caching
 */
export function headers(): Headers | HeadersInit {
  return {
    "Cache-Control": "private, max-age=120, must-revalidate",
  };
}

/**
 * Client loader with hydration enabled
 * Fetches course and chapters list on client-side
 */
export async function clientLoader({ params, request }: Route.ClientLoaderArgs) {
  const url = new URL(request.url);
  const searchParams = url.searchParams;
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10);

  const queryParams = new URLSearchParams();
  queryParams.set("page", page.toString());
  queryParams.set("page_size", pageSize.toString());
  queryParams.set("exclude", "content"); // 排除富文本内容字段，减少 60-70% 数据传输

  try {
    // Parallelize independent API requests to reduce total latency
    const results = await Promise.allSettled([
      clientHttp.get<Course>(`/courses/${params.courseId}`),
      clientHttp.get<Page<Chapter>>(`/courses/${params.courseId}/chapters/?${queryParams.toString()}`),
    ]);

    const course = results[0].status === 'fulfilled'
      ? results[0].value
      : { id: params.courseId, title: '', description: '', status: 'not_started', is_locked: true };

    const chapters = results[1].status === 'fulfilled'
      ? results[1].value
      : { results: [], count: 0, next: null, previous: null, page_size: pageSize };

    return { chapters, course };
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
      <title>{formatTitle('章节列表')}</title>
      <PageContainer maxWidth="lg">
        <SkeletonChapterList />
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
      <Box sx={{ py: spacing.xl }}>
        <Typography color="error" variant="h6" gutterBottom>
          加载失败
        </Typography>
        <Typography color="text.secondary">
          {error.message || '无法加载章节列表'}
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

// 状态映射（可选：美化显示文本）
const statusLabels = {
  not_started: '未开始',
  in_progress: '进行中',
  completed: '已完成',
};

// 状态颜色：显式指定类型，确保值是合法的 color 值
const statusColors: Record<string, ChipProps['color']> = {
  not_started: 'default',
  in_progress: 'warning',
  completed: 'success',
};

export default function ChapterPage({ params }: Route.ComponentProps) {
  const { courseId } = params;
  const navigate = useNavigate();
  const loaderData = useLoaderData<typeof clientLoader>();
  const title = loaderData.course.title;
  const pageTitle = title ? PAGE_TITLES.chapters(title) : '章节列表';

  // Initialize infinite scroll
  const infiniteScroll = useInfiniteScroll<Chapter>({
    initialData: loaderData.chapters,
    extractData: (data) => data.chapters,
    getNextPageUrl: (page, pageSize) =>
      `/courses/${courseId}/chapters?page=${page}&page_size=${pageSize}`,
  });

  const handleClick = (id: number, isLocked: boolean) => {
    if (isLocked) {
      navigate(`/courses/${courseId}/chapters/${id}/locked`);
    } else {
      navigate(`/courses/${courseId}/chapters/${id}`);
    }
  };

  // Filter unlocked and locked chapters from accumulated items
  const unlockedChapters = infiniteScroll.items.filter(chapter => !chapter.is_locked);
  const lockedChapters = infiniteScroll.items.filter(chapter => chapter.is_locked);

  if (infiniteScroll.items.length === 0) {
    return (
      <>
        <title>{formatTitle(pageTitle)}</title>
        <PageContainer maxWidth="sm">
          <SectionContainer spacing="md" variant="card">
            <Typography variant="h6" color="text.secondary" align="center" sx={{ py: spacing.lg }}>
              暂无章节
            </Typography>
            <Typography variant="body2" color="text.disabled" align="center">
              请稍后回来查看，或联系管理员。
            </Typography>
          </SectionContainer>
        </PageContainer>
      </>
    );
  }

  return (
    <>
      <title>{formatTitle(pageTitle)}</title>
      <PageContainer maxWidth="lg">
        <PageHeader
          title="章节列表"
          subtitle={`课程: ${title}`}
        />
      <SectionContainer spacing="md" variant="card">
        <Box sx={{ p: { xs: 2, sm: 3 }, borderBottom: 1, borderColor: 'divider' }}>
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid>
              <Button
                variant="outlined"
                onClick={() => navigate(`/courses/${courseId}`)}
                                sx={{
                  color: 'text.primary',
                  borderColor: 'divider',
                  '&:hover': {
                    borderColor: 'primary.main',
                    backgroundColor: 'action.hover',
                  },
                }}
              >
                返回课程主页
              </Button>
            </Grid>
          </Grid>
        </Box>
        <List>
          {/* Unlocked chapters */}
          {unlockedChapters.map((chapter) => (
            <ListItem
              key={chapter.id}
              disablePadding
              onClick={() => handleClick(chapter.id, chapter.is_locked)}
              sx={{
                '&:not(:last-child)': {
                  borderBottom: '1px solid',
                  borderColor: 'divider',
                },
              }}
            >
              <ListItemButton>
                <ListItemText
                  primary={chapter.title}
                  secondary={chapter.course_title}
                />
                <Box sx={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
                  <Chip
                    label={statusLabels[chapter.status]}
                    size="small"
                    color={statusColors[chapter.status]}
                    variant="outlined"
                  />
                </Box>
              </ListItemButton>
            </ListItem>
          ))}

          {/* Locked chapters */}
          {lockedChapters.map((chapter) => {
            const prerequisiteCount = chapter.prerequisite_progress?.total || 0;
            return (
              <ListItem
                key={`locked-${chapter.id}`}
                disablePadding
                sx={{
                  '&:not(:last-child)': {
                    borderBottom: '1px solid',
                    borderColor: 'divider',
                  },
                  opacity: 0.7,
                  cursor: 'default',
                  py: 1,
                  px: 2,
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flex: 1 }}>
                  <LockIcon
                    color="disabled"
                    fontSize="small"
                  />
                  <ListItemText
                    primary={
                      <Typography variant="body1" color="text.secondary">
                        {chapter.title}
                      </Typography>
                    }
                    secondary={
                      <>
                        <Typography variant="body2" component="span" color="text.disabled">
                          {chapter.course_title}
                        </Typography>
                        {prerequisiteCount > 0 && (
                          <Chip
                            component="span"
                            label={`完成 ${prerequisiteCount} 个前置章节`}
                            size="small"
                            color="default"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem', ml: 1 }}
                          />
                        )}
                      </>
                    }
                  />
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, opacity: 1 }}>
                  <Chip
                    label="已锁定"
                    size="small"
                    color="default"
                    variant="outlined"
                  />
                  <Tooltip title="查看解锁条件">
                    <IconButton
                      size="small"
                      color="info"
                      sx={{ p: 0.5 }}
                      edge="end"
                      onClick={() => handleClick(chapter.id, chapter.is_locked)}
                    >
                      <InfoIcon fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
              </ListItem>
            );
          })}
        </List>

        {/* Infinite scroll states */}
        <Box ref={infiniteScroll.sentinelRef} />

        {infiniteScroll.loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}

        {infiniteScroll.error && (
          <Box sx={{ textAlign: 'center', my: 2 }}>
            <Typography color="error" sx={{ mb: 1 }}>
              {infiniteScroll.error}
            </Typography>
            <Button variant="outlined" onClick={infiniteScroll.retry}>
              重试
            </Button>
          </Box>
        )}

        {!infiniteScroll.hasMore && infiniteScroll.items.length > 0 && (
          <Typography color="text.secondary" sx={{ textAlign: 'center', my: 2 }}>
            已加载全部 {infiniteScroll.items.length} 个章节
          </Typography>
        )}
      </SectionContainer>
    </PageContainer>
    </>
  );
}
