import React from 'react';
import { Box, Typography } from '@mui/material';
import type { AlgorithmProblem } from '~/types/course';



interface AlgorithmProblemDetailProps {
  algorithmProblem: AlgorithmProblem;
}

const AlgorithmProblemDetail: React.FC<AlgorithmProblemDetailProps> = ({ algorithmProblem }) => {
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
        {algorithmProblem.sample_cases
          .filter((tc) => tc.is_sample)
          .map((tc, index) => (
            <Box
              key={index}
              sx={{
                mb: 2,
                whiteSpace: 'pre-wrap',
                fontFamily: 'monospace',
                fontSize: '0.875rem',
              }}
            >
              <strong>Sample {index + 1}:</strong>
              {'\n'}
              <strong>Input:</strong>
              {'\n'}
              {tc.input_data}
              {'\n'}
              <strong>Output:</strong>
              {'\n'}
              {tc.expected_output}
            </Box>
          ))}
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
          <code>{algorithmProblem.code_template}</code>
        </pre>
      </Box>
    </Box>
  );
};

export default AlgorithmProblemDetail;