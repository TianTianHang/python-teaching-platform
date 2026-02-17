import { Box, Skeleton, List, ListItem, ListItemIcon, ListItemText } from "@mui/material";
import { spacing } from "~/design-system/tokens";

export default function SkeletonProblems() {
    return (
        <Box>
            {/* Page Header */}
            <Box sx={{ mb: spacing.lg }}>
                <Skeleton variant="text" width={200} height={36} />
                <Skeleton variant="text" width="50%" height={20} sx={{ mt: spacing.sm }} />
            </Box>

            {/* Filters Section */}
            <Box sx={{ mb: spacing.md, p: spacing.md, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', gap: spacing.sm, mb: spacing.sm }}>
                    <Skeleton variant="rounded" width={100} height={36} />
                    <Skeleton variant="rounded" width={100} height={36} />
                    <Skeleton variant="rounded" width={100} height={36} />
                </Box>
                <Skeleton variant="rounded" width={120} height={36} />
            </Box>

            {/* Problems List */}
            <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
                <List sx={{ py: 0 }}>
                    {[...Array(10)].map((_, i) => (
                        <ProblemListItemSkeleton key={i} />
                    ))}
                </List>
            </Box>

            {/* Pagination */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: spacing.lg }}>
                <Box sx={{ display: 'flex', gap: spacing.sm }}>
                    <Skeleton variant="rounded" width={40} height={36} />
                    <Skeleton variant="rounded" width={40} height={36} />
                    <Skeleton variant="rounded" width={40} height={36} />
                    <Skeleton variant="rounded" width={40} height={36} />
                    <Skeleton variant="rounded" width={40} height={36} />
                </Box>
            </Box>
        </Box>
    );
}

function ProblemListItemSkeleton() {
    return (
        <>
            <ListItem
                sx={{
                    px: 2,
                    py: 1.5,
                    borderTop: '1px solid',
                    borderColor: 'divider',
                }}
            >
                <ListItemIcon sx={{ minWidth: 100 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                        <Skeleton variant="circular" width={20} height={20} />
                        <Skeleton variant="text" width={50} height={16} />
                    </Box>
                </ListItemIcon>
                <ListItemText
                    primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                            <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                                <Skeleton variant="text" width="60%" height={20} />
                                <Skeleton variant="text" width="40%" height={16} sx={{ mt: spacing.sm }} />
                            </Box>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
                                <Skeleton variant="rounded" width={40} height={20} />
                                <Skeleton variant="rounded" width={50} height={20} />
                            </Box>
                        </Box>
                    }
                />
            </ListItem>
        </>
    );
}
