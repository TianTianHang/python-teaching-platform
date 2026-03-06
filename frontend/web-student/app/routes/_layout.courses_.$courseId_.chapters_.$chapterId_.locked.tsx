import { clientHttp } from '~/utils/http/client';
import { ChapterLockScreen } from '~/components/Chapter/ChapterLockScreen';
import type { ChapterUnlockStatus } from '~/types/course';
import type { Route } from './+types/_layout.courses_.$courseId_.chapters_.$chapterId_.locked';
import { formatTitle } from '~/config/meta';
import { redirect, Link } from 'react-router';
import { Box, Typography, Button } from '@mui/material';
import { spacing } from '~/design-system/tokens';
import { useLoaderData } from 'react-router';

/**
 * Client loader with hydration enabled
 * Fetches chapter unlock status on client-side
 */
export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  try {
    const unlockStatus = await clientHttp.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`);
    return { unlockStatus };
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
      <title>{formatTitle('章节已锁定')}</title>
      <Box sx={{ p: spacing.xl, display: 'flex', justifyContent: 'center' }}>
        <Typography>加载中...</Typography>
      </Box>
    </>
  );
}

/**
 * Error boundary for client loader errors
 */
export function ErrorBoundary({ error }: { error: Error }) {
  return (
    <Box sx={{ p: spacing.xl }}>
      <Typography color="error" variant="h6" gutterBottom>
        加载失败
      </Typography>
      <Typography color="text.secondary">
        {error.message || '无法加载章节信息'}
      </Typography>
      <Box sx={{ mt: 2 }}>
        <Button variant="outlined" component={Link} to=".">
          重试
        </Button>
      </Box>
    </Box>
  );
}

export default function LockedChapter({ params }: Route.ComponentProps) {
  const loaderData = useLoaderData<typeof clientLoader>();
  const { unlockStatus } = loaderData;
  //console.log(unlockStatus)
  const chapter = unlockStatus.chapter;
  const title = chapter?.title || "章节已锁定";
  return (
    <>
      <title>{formatTitle(`${title} (已锁定)`)}</title>
      <ChapterLockScreen
        chapter={chapter || { id: 0, title: "章节已锁定", course_title: "" }}
        unlockStatus={unlockStatus}
        courseId={params.courseId}
      />
    </>
  );
}
