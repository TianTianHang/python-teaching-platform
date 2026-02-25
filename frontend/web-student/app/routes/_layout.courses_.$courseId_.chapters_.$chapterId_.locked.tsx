import { createHttp } from '~/utils/http/index.server';
import { withAuth } from '~/utils/loaderWrapper';
import { ChapterLockScreen } from '~/components/Chapter/ChapterLockScreen';
import type { ChapterUnlockStatus } from '~/types/course';
import type { Route } from './+types/_layout.courses_.$courseId_.chapters_.$chapterId_.locked';
import { formatTitle } from '~/config/meta';

export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);
  const unlockStatus = await http.get<ChapterUnlockStatus>(`/courses/${params.courseId}/chapters/${params.chapterId}/unlock_status`);
  return { unlockStatus };
});

export default function LockedChapter({ loaderData, params }: Route.ComponentProps) {
  const { unlockStatus } = loaderData;
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
