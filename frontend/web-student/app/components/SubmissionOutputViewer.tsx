// SubmissionOutputViewer.tsx
import React from 'react';
import { Paper, Typography, Box, Chip, Divider } from '@mui/material';
import { green, red, grey } from '@mui/material/colors';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import CodeIcon from '@mui/icons-material/Code';
import type { UnifiedOutput } from '~/types/submission';

interface SubmissionOutputViewerProps {
  output: UnifiedOutput | null;
  isLoading?: boolean;
}

const getStatusColor = (status: string) => {
  if (status === 'accepted') return green[500];
  if (['wrong_answer', 'runtime_error', 'compilation_error', 'time_limit_exceeded'].includes(status))
    return red[500];
  return grey[600];
};

const getStatusIcon = (status: string) => {
  console.log(status)
  if (status === 'accepted') return <CheckCircleIcon sx={{ color: green[500] }} />;
  return <ErrorIcon sx={{ color: red[500] }} />;
};

const SubmissionOutputViewer: React.FC<SubmissionOutputViewerProps> = ({ output, isLoading }) => {
  if (isLoading) {
    return (
     
        <Typography variant="body2" color="text.secondary">
          Running code...
        </Typography>
    
    );
  }

  if (!output) return null;

  return (
    <Box>
      {/* 状态与性能指标 */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        {getStatusIcon(output.status)}
        <Typography variant="subtitle2" fontWeight="bold" color={getStatusColor(output.status)}>
          {output.status.replace('_', ' ').toUpperCase()}
        </Typography>
        {output.executionTime !== null && (
          <Chip
            size="small"
            label={`${output.executionTime} ms`}
            variant="outlined"
            sx={{ height: 24, fontSize: '0.75rem' }}
          />
        )}
        {output.memoryUsed !== null && (
          <Chip
            size="small"
            label={`${output.memoryUsed} MB`}
            variant="outlined"
            sx={{ height: 24, fontSize: '0.75rem' }}
          />
        )}
      </Box>

      <Divider sx={{ my: 1.5 }} />

      {/* 标准输出 */}
      {output.stdout && (
        <Box sx={{ mb: output.stderr ? 2 : 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            <CodeIcon sx={{ fontSize: 16, mr: 0.5, color: grey[600] }} />
            <Typography variant="caption" fontWeight="bold" color="text.secondary">
              Output
            </Typography>
          </Box>
          <Paper
            variant="outlined"
            sx={{
              p: 1.5,
              backgroundColor: '#fff',
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              whiteSpace: 'pre-wrap',
              borderRadius: 1,
              maxHeight: 200,
              overflow: 'auto',
            }}
          >
            {output.stdout}
          </Paper>
        </Box>
      )}

      {/* 错误输出 */}
      {output.stderr && (
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
            <ErrorIcon sx={{ fontSize: 16, mr: 0.5, color: red[500] }} />
            <Typography variant="caption" fontWeight="bold" color="error">
              Errors
            </Typography>
          </Box>
          <Paper
            variant="outlined"
            sx={{
              p: 1.5,
              backgroundColor: '#fff8f8',
              borderColor: red[200],
              fontFamily: 'monospace',
              fontSize: '0.9rem',
              whiteSpace: 'pre-wrap',
              borderRadius: 1,
              maxHeight: 200,
              overflow: 'auto',
            }}
          >
            {output.stderr}
          </Paper>
        </Box>
      )}

      {/* 如果都没有输出，显示空状态 */}
      {!output.stdout && !output.stderr && (
        <Typography variant="body2" color="text.secondary" fontStyle="italic">
          No output generated.
        </Typography>
      )}
    </Box>
  );
};

export default SubmissionOutputViewer;