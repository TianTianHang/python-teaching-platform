import { Button, Box, Typography } from '@mui/material';
import { useRouteError, useNavigate, useRevalidator } from 'react-router';
import LoadingState from '~/components/Layout/LoadingState';
import { spacing } from '~/design-system/tokens';
import { ArrowBack as ArrowBackIcon, Refresh as RefreshIcon } from '@mui/icons-material';

/**
 * ProblemLoadError - Problem 加载错误组件
 *
 * 当 problem 数据加载失败时显示的错误页面。
 * 使用 LoadingState 作为基础，提供重试和返回按钮。
 *
 * @example
 * // 在路由中使用 errorElement
 * <Route path="problems/:problemId" element={<ProblemPage />} errorElement={<ProblemLoadError />} />
 */
export default function ProblemLoadError() {
  const error = useRouteError() as Response;
  const navigate = useNavigate();
  const revalidator = useRevalidator();

  // 解析错误数据
  let errorData: { message?: string } | null = null;
  try {
    errorData = error.json ? await error.clone().json() : null;
  } catch {
    // 如果解析失败，忽略
  }

  // 根据错误状态码确定错误消息
  const getErrorMessage = (): string => {
    const status = error?.status;

    if (status === 404) {
      return '题目未找到';
    }
    if (status === 500) {
      return '服务器错误，请稍后重试';
    }
    if (status === 403) {
      return '无权访问此题目';
    }
    if (status === 401) {
      return '请先登录';
    }
    // 网络错误或其他错误
    return '题目加载失败，请检查网络连接';
  };

  const getErrorDetail = (): string => {
    if (error?.data?.message) {
      return error.data.message;
    }
    return `错误代码: ${error?.status || '未知'}`;
  };

  const handleRetry = () => {
    revalidator.revalidate();
  };

  const handleBack = () => {
    navigate('/problems');
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        minHeight: '50vh',
        py: spacing.xl,
      }}
    >
      <LoadingState
        variant="error"
        message={getErrorMessage()}
        sx={{ width: '100%', maxWidth: 600 }}
      >
        <Typography variant="body2" color="text.secondary">
          {getErrorDetail()}
        </Typography>
      </LoadingState>

      <Box
        sx={{
          display: 'flex',
          gap: spacing.md,
          mt: spacing.lg,
        }}
      >
        <Button
          variant="outlined"
          startIcon={<ArrowBackIcon />}
          onClick={handleBack}
          size="large"
        >
          返回题目列表
        </Button>
        <Button
          variant="contained"
          startIcon={<RefreshIcon />}
          onClick={handleRetry}
          disabled={revalidator.state === 'loading'}
          size="large"
        >
          {revalidator.state === 'loading' ? '重试中...' : '重试'}
        </Button>
      </Box>
    </Box>
  );
}
