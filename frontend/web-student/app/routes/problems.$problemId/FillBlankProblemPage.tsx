import { Box, Typography, Container } from "@mui/material";
import FillBlankProblemCmp from "~/components/Problem/FillBlankProblemCmp";
import ProblemNavigation from "~/components/ProblemNavigation";
import type { FillBlankProblem } from "~/types/course";

export default function FillBlankProblemPage({ problem, onNext, hasNext, onPrevious, hasPrevious, onBackToList, loading }: {
  problem: FillBlankProblem,
  onNext: () => void,
  hasNext: boolean,
  onPrevious?: () => void,
  hasPrevious?: boolean,
  onBackToList?: () => void,
  loading?: boolean
}) {
  return (
    <>
      <Container maxWidth="md" sx={{ py: 4, pb: 8 }}>
        {/* 可选：页面标题 */}
        <Box mb={3}>
          <Typography variant="h5" color="text.secondary">
            填空题练习
          </Typography>
        </Box>

        {/* 题目卡片容器 */}
        <FillBlankProblemCmp problem={problem} />
      </Container>

      {/* 底部导航栏 */}
      <ProblemNavigation
        problemTitle={problem.title}
        hasNext={hasNext}
        hasPrevious={hasPrevious || false}
        onPrevious={onPrevious}
        onNext={onNext}
        onBackToList={onBackToList}
        loading={loading}
      />
    </>
  );
}
