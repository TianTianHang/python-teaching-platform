import { Skeleton, Box } from '@mui/material';

const ProblemsSkeleton = () => {
  return (
    <Box sx={{ mt: 4 }}>
      <Skeleton variant="text" width={120} height={32} sx={{ mb: 2 }} /> {/* “相关题目”标题 */}
      <Box>
        {[...Array(3)].map((_, i) => (
          <Box key={i} sx={{ mb: 3 }}>
            <Skeleton variant="text" width="60%" height={28} /> {/* 题目标题 */}
            <Skeleton variant="text" width="40%" height={20} sx={{ mt: 0.5 }} /> {/* 标签 */}
            <Skeleton variant="text" width="100%" height={20} sx={{ mt: 0.5 }} /> {/* 描述 */}
            <Skeleton variant="text" width="80%" height={20} sx={{ mt: 0.5 }} /> {/* 可选：多行描述或留空 */}
          </Box>
        ))}
      </Box>
    </Box>
  );
};
export default ProblemsSkeleton;