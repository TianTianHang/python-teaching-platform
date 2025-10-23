import React, { useState } from 'react';
import { Box, Divider, Stack, Tab, Tabs, Typography } from '@mui/material';
import type { AlgorithmProblem, TestCase } from '~/types/course';
import { a11yProps, TabPanel } from '~/components/TabUtils'


interface AlgorithmProblemDetailProps {
  algorithmProblem: AlgorithmProblem;
}
export const CaseDetail = ({ testcase }: { testcase: TestCase }) => {
  return <Stack>
    <Box>
      <Typography variant="body2">Input:</Typography>
      {testcase.input_data}
    </Box>

    <Box>
      <Typography variant="body2">Output:</Typography>
      {testcase.expected_output}
    </Box>

  </Stack>
}
const AlgorithmProblemDetail: React.FC<AlgorithmProblemDetailProps> = ({ algorithmProblem }) => {
  const [tabValue, setTabValue] = useState(0);
  const onTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue)
  }
  return (
    <Box sx={{ mt: 2 }}>
      <Typography variant="body2" color="text.secondary">
        Time Limit: {algorithmProblem.time_limit} ms
      </Typography>
      <Typography variant="body2" color="text.secondary">
        Memory Limit: {algorithmProblem.memory_limit} MB
      </Typography>

      <Typography variant="h6" component="h3" sx={{ mt: 2 }}>
        Sample Inputs/Outputs
      </Typography>
      <Box
        sx={{
          backgroundColor: '#f5f5f5',
          padding: '10px',
          borderRadius: '4px',
          overflowX: 'auto',
        }}
      >
        <Box>
          <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
            <Tabs value={tabValue} onChange={onTabChange}>
              {algorithmProblem.sample_cases
                .filter((tc) => tc.is_sample)
                .map((tc, index) => (
                  <Tab label={`case ${index + 1}`} {...a11yProps(index)} />
                ))}
            </Tabs>
          </Box>
          {algorithmProblem.sample_cases
            .filter((tc) => tc.is_sample)
            .map((tc, index) => (
              <TabPanel index={index} value={tabValue}>
                <CaseDetail testcase={tc} />
              </TabPanel>
            ))}
        </Box>



      </Box>

      <Typography variant="h6" component="h3" sx={{ mt: 2 }}>
        Code Template
      </Typography>
      <Box
        sx={{
          backgroundColor: '#f5f5f5',
          padding: '10px',
          borderRadius: '4px',
          overflowX: 'auto',
        }}
      >
        <pre style={{ margin: 0, fontFamily: 'monospace', fontSize: '0.875rem' }}>
          <code>{algorithmProblem.code_template.python}</code>
        </pre>
      </Box>
    </Box>
  );
};

export default AlgorithmProblemDetail;