import { Box } from '@mui/material';
import { spacing } from '~/design-system/tokens';
import ChapterTitleSkeleton from './ChapterTitleSkeleton';
import ChapterContentSkeleton from './ChapterContentSkeleton';
import SidebarSkeleton from './SidebarSkeleton';

/**
 * Skeleton for chapter detail page
 * Combines title, content, and sidebar skeletons
 */
export default function SkeletonChapterDetail() {
  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Main content area */}
      <Box sx={{ flex: 1, overflow: 'auto', p: spacing.md }}>
        <ChapterTitleSkeleton />
        <ChapterContentSkeleton />
      </Box>

      {/* Sidebar */}
      <Box
        sx={{
          width: 280,
          borderLeft: '1px solid',
          borderColor: 'divider',
          overflow: 'auto',
        }}
      >
        <SidebarSkeleton />
      </Box>
    </Box>
  );
}
