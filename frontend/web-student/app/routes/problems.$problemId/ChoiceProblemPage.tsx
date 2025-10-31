import { Box } from "@mui/material";
import ChoiceProblemCmp from "~/components/Problem/ChoiceProblemCmp";
import type { ChoiceProblem } from "~/types/course";

export default function ChoiceProblemPage({ problem }: { problem: ChoiceProblem }) {

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        bgcolor: '#f5f5f5',
        p: 2,
      }}
    >
      <ChoiceProblemCmp problem={problem}/>
    </Box>
  );
}