import { Skeleton, Box } from '@mui/material';
import { spacing } from '~/design-system/tokens';

/**
 * Skeleton for chapter title section
 * Matches the layout of chapter title and course title
 */
export default function ChapterTitleSkeleton() {
  return (
    <Box sx={{ mb: spacing.md }}>
      <Skeleton
        variant="text"
        width="60%"
        height={40}
        sx={{ mb: spacing.xs }}
      />
      <Skeleton
        variant="text"
        width="40%"
        height={24}
      />
    </Box>
  );
}