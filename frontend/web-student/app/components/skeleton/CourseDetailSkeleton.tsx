import { Skeleton, Box, Grid } from '@mui/material';
import { spacing } from '~/design-system/tokens';

/**
 * Skeleton for course detail page
 * Matches the layout of course information and progress sections
 */
export default function CourseDetailSkeleton() {
  return (
    <Box sx={{ mb: spacing.lg }}>
      {/* Page title */}
      <Skeleton variant="text" width="50%" height={40} sx={{ mb: spacing.md }} />

      {/* Description */}
      <Skeleton variant="text" width="100%" height={20} />
      <Skeleton variant="text" width="95%" height={20} sx={{ mt: spacing.xs }} />
      <Skeleton variant="text" width="80%" height={20} sx={{ mt: spacing.xs }} />

      {/* Course info grid */}
      <Grid container spacing={3} sx={{ mt: spacing.md }}>
        <Grid size={{ xs: 12, md: 6 }}>
          <Skeleton variant="text" width={100} height={24} sx={{ mb: spacing.sm }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: spacing.xs }}>
            <Skeleton variant="text" width="60%" height={18} />
            <Skeleton variant="text" width="60%" height={18} />
          </Box>
        </Grid>

        <Grid size={{ xs: 12, md: 6 }}>
          <Skeleton variant="text" width={100} height={24} sx={{ mb: spacing.sm }} />
          <Skeleton variant="rounded" width="100%" height={100} />
        </Grid>
      </Grid>

      {/* Action buttons */}
      <Box sx={{ mt: spacing.lg, display: 'flex', gap: spacing.md, justifyContent: 'center' }}>
        <Skeleton variant="rounded" width={160} height={48} />
        <Skeleton variant="rounded" width={140} height={48} />
      </Box>
    </Box>
  );
}