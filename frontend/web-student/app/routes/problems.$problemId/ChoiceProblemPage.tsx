import { Box, Typography, Container } from "@mui/material";
import ChoiceProblemCmp from "~/components/Problem/ChoiceProblemCmp";
import ProblemNavigation from "~/components/ProblemNavigation";
import type { ChoiceProblem } from "~/types/course";

export default function ChoiceProblemPage({ problem, onNext, hasNext, onPrevious, hasPrevious, onBackToList, loading }: {
  problem: ChoiceProblem,
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
            选择题练习
          </Typography>
        </Box>

        {/* 题目卡片容器 */}
        <ChoiceProblemCmp problem={problem} />
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
