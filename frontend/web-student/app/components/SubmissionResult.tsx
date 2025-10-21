import { Alert, Box, CircularProgress, Paper, Stack, Typography } from "@mui/material";
import type { SubmissionResponse } from "~/utils/judge/type";

interface SubmissionResultProps {
  result: SubmissionResponse | null;
  isPolling: boolean;
  error: string | null;
}

const SubmissionResult: React.FC<SubmissionResultProps> = ({ result, isPolling, error }) => {
  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        <Typography variant="body1">❌ {error}</Typography>
      </Alert>
    );
  }

  if (isPolling || !result) {
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
        <CircularProgress size={20} sx={{ mr: 1 }} />
        <Typography variant="body2" color="text.secondary">
          评测中...
        </Typography>
      </Box>
    );
  }

  // 判断是否为终态（status_id >= 4）
  const isFinished = result.status_id >= 4;

  // 状态描述（可扩展）
  const getStatusText = (statusId: number): string => {
    const map: Record<number, string> = {
      1: 'In Queue',
      2: 'Compiling',
      3: 'Running',
      4: '✅ Accepted',
      5: '❌ Wrong Answer',
      6: '⚠️ Compilation Error',
      7: '💥 Runtime Error',
      8: '⏱️ Time Limit Exceeded',
      9: 'MemoryWarning Memory Limit Exceeded',
    };
    return map[statusId] || `Status ${statusId}`;
  };

  const statusColor = result.status.id === 4 ? 'success.main' : 'error.main';

  return (
    <Box sx={{ mt: 2 }}>
      {/* 状态标签 */}
      <Typography variant="subtitle2" color={statusColor} gutterBottom>
        {getStatusText(result.status.id)}
      </Typography>

      {/* 编译错误（优先级最高） */}
      {result.compile_output && (
        <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'error.light', mt: 1 }}>
          <Typography variant="body2" fontWeight="bold" color="error.dark">
            编译错误:
          </Typography>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
            {result.compile_output}
          </pre>
        </Paper>
      )}

      {/* 标准错误（stderr） */}
      {result.stderr && !result.compile_output && (
        <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'warning.light', mt: 1 }}>
          <Typography variant="body2" fontWeight="bold" color="warning.dark">
            运行时错误:
          </Typography>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
            {result.stderr}
          </pre>
        </Paper>
      )}

      {/* 标准输出（stdout） */}
      {result.stdout && (
        <Paper variant="outlined" sx={{ p: 1.5, mt: 1 }}>
          <Typography variant="body2" fontWeight="bold" color="text.primary">
            输出:
          </Typography>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap', fontSize: '0.875rem' }}>
            {result.stdout}
          </pre>
        </Paper>
      )}

      {/* 耗时 & 内存（仅终态显示） */}
      {isFinished && (
        <Stack direction="row" spacing={2} sx={{ mt: 1, flexWrap: 'wrap' }}>
          {result.time && (
            <Typography variant="body2" color="text.secondary">
              ⏱️ 耗时: {parseFloat(result.time).toFixed(3)}s
            </Typography>
          )}
          {result.memory && (
            <Typography variant="body2" color="text.secondary">
              🧠 内存: {result.memory} KB
            </Typography>
          )}
        </Stack>
      )}
    </Box>
  );
};
export default SubmissionResult;