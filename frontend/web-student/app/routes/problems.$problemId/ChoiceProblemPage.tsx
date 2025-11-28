import { useTheme, Box, Paper, Typography, Container, Button } from "@mui/material";
import { useMount } from "ahooks";
import { useEffect, useState } from "react";
import { useFetcher } from "react-router";
import ChoiceProblemCmp from "~/components/Problem/ChoiceProblemCmp";
import type { ChoiceProblem } from "~/types/course";
import type { Page } from "~/types/page";

export default function ChoiceProblemPage({ problem,onNext,hasNext }: { problem: ChoiceProblem,onNext: () => void,hasNext: boolean }) {
  const theme = useTheme();
  // const [problems, setProblems] = useState<Page<ChoiceProblem>>();
  // const fetcher = useFetcher();
  // useMount(() => {
  //   fetcher.load(`/problems?type=choice&page_size=10?page=1`);
  // })
  // useEffect(() => {
  //   if (fetcher.state === "idle" && fetcher.data) {
  //     setProblems(fetcher.data);
  //   }
  // }, [fetcher.state]);
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* 可选：页面标题 */}
      <Box mb={3}>
        <Typography variant="h5" color="text.secondary">
          选择题练习
        </Typography>
      </Box>

      {/* 题目卡片容器 */}

      <ChoiceProblemCmp problem={problem} />


      {/* 可选：底部提示或操作区（如“下一题”按钮） */}
      <Box mt={3} display="flex" justifyContent="flex-end">
        <Button  disabled={!hasNext} variant="contained" onClick={onNext}>下一题</Button>
      </Box>
    </Container>
  );
}