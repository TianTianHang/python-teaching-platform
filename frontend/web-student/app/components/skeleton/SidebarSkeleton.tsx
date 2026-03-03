import { Skeleton, Box, Typography, Divider, Toolbar } from '@mui/material';
import { spacing } from '~/design-system/tokens';

/**
 * Skeleton for chapter sidebar
 * Matches the width and layout of ChapterSidebar component
 */
export default function SidebarSkeleton() {
  return (
    <>
      <Toolbar />
      <Box sx={{ p: spacing.md }}>
        <Typography variant="h6" component="h2" gutterBottom>
          课程章节
        </Typography>
        <Divider sx={{ mb: spacing.md }} />

        {/* Chapter list items */}
        {[...Array(8)].map((_, i) => (
          <Box
            key={i}
            sx={{
              display: 'flex',
              alignItems: 'center',
              py: spacing.xs,
              px: spacing.xs,
              mb: spacing.xs,
            }}
          >
            <Skeleton variant="text" width="80%" height={20} />
          </Box>
        ))}
      </Box>
    </>
  );
}