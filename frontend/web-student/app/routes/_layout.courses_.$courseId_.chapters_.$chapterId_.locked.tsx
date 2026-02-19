import { createHttp } from '~/utils/http/index.server';
import { withAuth } from '~/utils/loaderWrapper';
import { ChapterLockScreen } from '~/components/Chapter/ChapterLockScreen';
import type { Chapter, ChapterUnlockStatus } from '~/types/course';
import type { Route } from './+types/_layout.courses_.$courseId_.chapters_.$chapterId_.locked';
import { formatTitle, PAGE_TITLES } from '~/config/meta';

export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);
  const chapter = await http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
  const unlockStatus = await http.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`);
  return { chapter, unlockStatus };
});

export default function LockedChapter({ loaderData, params }: Route.ComponentProps) {
  const { chapter, unlockStatus } = loaderData;
  const title = chapter.title || "章节已锁定";
  return (
    <>
      <title>{formatTitle(`${title} (已锁定)`)}</title>
      <ChapterLockScreen
        chapter={chapter}
        unlockStatus={unlockStatus}
        courseId={params.courseId}
      />
    </>
  );
}
