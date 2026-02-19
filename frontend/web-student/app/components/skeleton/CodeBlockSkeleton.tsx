import { Skeleton, Box } from '@mui/material';

interface CodeBlockSkeletonProps {
  height?: number | string;
}

/**
 * Skeleton placeholder for lazy-loaded code blocks.
 * Matches JupyterLite iframe dimensions to prevent layout shift.
 */
const CodeBlockSkeleton = ({ height = 200 }: CodeBlockSkeletonProps) => {

  return (
    <Box
      sx={{
        width: '100%',
        height: typeof height === 'number' ? `${height}px` : height,
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 1,
        overflow: 'hidden',
        bgcolor: 'background.paper',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Toolbar area */}
      <Box
        sx={{
          height: 40,
          borderBottom: '1px solid',
          borderColor: 'divider',
          bgcolor: 'action.hover',
          display: 'flex',
          alignItems: 'center',
          px: 1,
        }}
      >
        <Skeleton variant="circular" width={20} height={20} />
        <Skeleton variant="rectangular" width={100} height={20} sx={{ ml: 1 }} />
      </Box>
      {/* Code area */}
      <Box sx={{ flex: 1, p: 2 }}>
        <Skeleton variant="text" width="100%" sx={{ mb: 1 }} />
        <Skeleton variant="text" width="90%" sx={{ mb: 1 }} />
        <Skeleton variant="text" width="95%" sx={{ mb: 1 }} />
        <Skeleton variant="text" width="85%" sx={{ mb: 1 }} />
        <Skeleton variant="text" width="92%" sx={{ mb: 1 }} />
      </Box>
    </Box>
  );
};

export default CodeBlockSkeleton;
