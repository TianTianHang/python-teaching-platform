import { Box, Paper, Stack, Typography } from "@mui/material"
import type { TestCase } from "~/types/course"



export const CaseDetail = ({ testcase }: { testcase: TestCase }) => {
  return (
    <Stack spacing={2}>
      <Box>
        <Typography variant="body2" gutterBottom>
          Input:
        </Typography>
        <Paper
          elevation={0}
          sx={{
            p: 1.5,
            bgcolor: 'background.paper',
            borderRadius: 1,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontSize: '0.875rem',
          }}
        >
          {testcase.input_data}
        </Paper>
      </Box>

      <Box>
        <Typography variant="body2" gutterBottom>
          Output:
        </Typography>
        <Paper
          elevation={0}
          sx={{
            p: 1.5,
            bgcolor: 'background.paper',
            borderRadius: 1,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word',
            fontSize: '0.875rem',
          }}
        >
          {testcase.expected_output}
        </Paper>
      </Box>
    </Stack>
  );
};