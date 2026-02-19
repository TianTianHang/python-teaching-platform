import { Box, Skeleton, Grid, List, ListItem, ListItemIcon, ListItemText, Divider } from "@mui/material";
import { spacing } from "~/design-system/tokens";

export default function SkeletonHome() {
    return (
        <Box>
            {/* Page Header */}
            <Box sx={{ mb: spacing.lg }}>
                <Skeleton variant="text" width={200} height={32} />
                <Skeleton variant="text" width="60%" height={24} sx={{ mt: spacing.sm }} />
            </Box>

            {/* My Courses Section */}
            <Box sx={{ mb: spacing.xl }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <Skeleton variant="circular" width={24} height={24} />
                    <Skeleton variant="text" width={120} height={28} />
                </Box>
                <Grid container spacing={2}>
                    <CourseCardSkeleton />
                    <CourseCardSkeleton />
                </Grid>
            </Box>

            {/* Unfinished Problems Section */}
            <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
                    <Skeleton variant="circular" width={24} height={24} />
                    <Skeleton variant="text" width={150} height={28} />
                </Box>
                <List sx={{ py: 0 }}>
                    <ProblemListItemSkeleton />
                    <ProblemListItemSkeleton />
                    <ProblemListItemSkeleton />
                </List>
            </Box>
        </Box>
    );
}

function CourseCardSkeleton() {
    return (
        <Grid size={{ xs: 12, md: 6 }}>
            <Box
                sx={{
                    p: spacing.lg,
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    bgcolor: 'background.paper',
                }}
            >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: spacing.md }}>
                    <Box sx={{ flex: 1 }}>
                        <Skeleton variant="text" width="70%" height={28} />
                        <Skeleton variant="text" width="50%" height={20} sx={{ mt: spacing.sm }} />
                    </Box>
                    <Skeleton variant="rounded" width={80} height={32} />
                </Box>
                <Skeleton variant="text" width="100%" height={20} sx={{ mb: spacing.sm }} />
                <Skeleton variant="text" width="60%" height={18} />
            </Box>
        </Grid>
    );
}

function ProblemListItemSkeleton() {
    return (
        <>
            <ListItem>
                <ListItemIcon>
                    <Skeleton variant="circular" width={24} height={24} />
                </ListItemIcon>
                <ListItemText
                    primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                            <Skeleton variant="text" width="40%" height={20} />
                            <Skeleton variant="rounded" width={40} height={20} />
                            <Skeleton variant="rounded" width={60} height={20} />
                        </Box>
                    }
                    secondary={<Skeleton variant="text" width="30%" height={16} />}
                />
                <Skeleton variant="rounded" width={60} height={32} />
            </ListItem>
            <Divider variant="inset" component="li" />
        </>
    );
}
