import { Box, Skeleton, Grid } from "@mui/material";
import { spacing } from "~/design-system/tokens";

export default function SkeletonProfile() {
    return (
        <Box>
            {/* Page Header */}
            <Box sx={{ mb: spacing.lg }}>
                <Skeleton variant="text" width={150} height={36} />
                <Skeleton variant="text" width="60%" height={20} sx={{ mt: spacing.sm }} />
            </Box>

            {/* Profile Section */}
            <Box sx={{ mb: spacing.xl, p: spacing.lg, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Grid container spacing={4}>
                    <Grid size={{ xs: 6, sm: 4 }}>
                        <Skeleton variant="circular" width={120} height={120} sx={{ margin: '0 auto' }} />
                    </Grid>
                    <Grid size="grow">
                        <Skeleton variant="rectangular" width="100%" height={56} sx={{ mb: spacing.md }} />
                        <Skeleton variant="rectangular" width="100%" height={56} sx={{ mb: spacing.md }} />
                        <Skeleton variant="rectangular" width={120} height={36} />
                    </Grid>
                </Grid>
            </Box>

            {/* Password Section */}
            <Box sx={{ p: spacing.lg, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Box sx={{ mb: spacing.md }}>
                    <Skeleton variant="text" width={150} height={24} sx={{ mb: spacing.sm }} />
                    <Skeleton variant="text" width="80%" height={16} />
                </Box>

                <Grid container spacing={3}>
                    <Grid size={12}>
                        <Skeleton variant="rectangular" width="100%" height={56} />
                    </Grid>
                    <Grid size={12}>
                        <Skeleton variant="rectangular" width="100%" height={56} />
                    </Grid>
                    <Grid size={12}>
                        <Skeleton variant="rectangular" width="100%" height={56} />
                    </Grid>
                </Grid>

                <Box sx={{ mt: spacing.lg }}>
                    <Skeleton variant="rectangular" width={150} height={36} />
                </Box>
            </Box>
        </Box>
    );
}
