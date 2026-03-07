import { Skeleton, Box, List, ListItem, ListItemText, Chip } from '@mui/material';
import { spacing } from '~/design-system/tokens';

/**
 * Skeleton for chapter list page
 * Matches the layout of chapter list with pagination
 */
export default function SkeletonChapterList() {
  return (
    <Box sx={{ py: spacing.xl }}>
      {/* Page header */}
      <Skeleton variant="text" width="40%" height={40} sx={{ mb: spacing.sm }} />
      <Skeleton variant="text" width="60%" height={20} sx={{ mb: spacing.md }} />

      {/* Chapter list items */}
      <Box sx={{ bgcolor: 'background.paper', borderRadius: 2, boxShadow: 1 }}>
        {[...Array(8)].map((_, i) => (
          <Box
            key={i}
            sx={{
              borderBottom: i < 7 ? '1px solid' : 'none',
              borderColor: 'divider',
            }}
          >
            <ListItem>
              <ListItemText
                primary={
                  <Skeleton
                    variant="text"
                    width={`${60 + Math.random() * 20}%`}
                    height={24}
                  />
                }
                secondary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.xs, mt: spacing.xs }}>
                    <Skeleton variant="text" width={80} height={20} />
                    <Skeleton variant="text" width={60} height={20} />
                  </Box>
                }
              />
              <Box sx={{ display: 'flex', gap: spacing.xs }}>
                <Skeleton variant="rounded" width={60} height={32} />
              </Box>
            </ListItem>
          </Box>
        ))}
      </Box>

      {/* Pagination skeleton */}
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: spacing.lg }}>
        <Skeleton variant="rounded" width={300} height={40} />
      </Box>
    </Box>
  );
}
