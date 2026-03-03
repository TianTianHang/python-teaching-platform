import { Skeleton, Box } from '@mui/material';
import { spacing } from '~/design-system/tokens';

/**
 * Skeleton for chapter content section
 * Matches the layout of Markdown content and action buttons
 */
export default function ChapterContentSkeleton() {
  return (
    <Box sx={{ minHeight: 400, p: spacing.md }}>
      {/* Markdown content lines */}
      <Skeleton variant="text" width="100%" height={20} />
      <Skeleton variant="text" width="95%" height={20} sx={{ mt: spacing.xs }} />
      <Skeleton variant="text" width="90%" height={20} sx={{ mt: spacing.xs }} />
      <Skeleton variant="text" width="85%" height={20} sx={{ mt: spacing.xs }} />

      {/* Paragraph break */}
      <Box sx={{ mt: spacing.md }}>
        <Skeleton variant="text" width="100%" height={20} />
        <Skeleton variant="text" width="75%" height={20} sx={{ mt: spacing.xs }} />
      </Box>

      {/* Code block placeholder */}
      <Skeleton
        variant="rectangular"
        width="100%"
        height={150}
        sx={{ mt: spacing.md, borderRadius: 1 }}
      />

      {/* Button skeleton */}
      <Box sx={{ mt: spacing.md }}>
        <Skeleton variant="rounded" width={140} height={36} />
      </Box>

      {/* Timestamps */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: spacing.lg }}>
        <Skeleton variant="text" width={150} height={14} />
        <Skeleton variant="text" width={150} height={14} />
      </Box>
    </Box>
  );
}