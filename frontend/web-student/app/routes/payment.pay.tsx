import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/payment.pay";
import createHttp from "~/utils/http/index.server";
import { useNavigate } from "react-router";
import type { Order } from "~/types/order";
import { Alert, Box, Button, CircularProgress, Container, Paper, Typography } from "@mui/material";
import React from "react";
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
export const action = withAuth(async ({ request }: Route.ActionArgs) => {
  const formData = await request.formData();
  const order_number = formData.get('order_number');
  const payment_method = formData.get('payment_method');
  if (order_number && payment_method) {
    const http = createHttp(request);
    const res = await http.post<{
      method: string;
      pay_url: string;
      gateway: string;
    }>(`/orders/${order_number}/pay/`, { payment_method })
    return res;
  } else {
    return {}
  }

})



export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  const url = new URL(request.url);
  const searchParams = url.searchParams;
  // 只返回 order_number，轮询交给前端
  return { order_number:searchParams.get("out_trade_no") };
});


export default function PaymentCallbackPage({ loaderData }: Route.ComponentProps) {
  const { order_number } = loaderData;
  const navigate = useNavigate();
  const [status, setStatus] = React.useState<'idle' | 'checking' | 'paid' | 'failed'>('checking');
  const [error, setError] = React.useState<string | null>(null);
  React.useEffect(() => {
    let active = true;
    const maxDuration = 60_000; // 60 seconds
    const interval = 2000; // 2 seconds
    const startTime = Date.now();

    const poll = async () => {
      try {
        const res = await fetch(`/orders/${order_number}`);
        if (!res.ok) {
          throw new Error('网络错误');
        }
        const order: Order = await res.json();
        if (!active) return;
        if (order?.status === 'paid') {
          setStatus('paid');
          // 可选：触发登录或刷新用户状态
          // 例如：window.location.reload(); 或调用 /auth/me
          return;
        }
        if (['cancelled', 'failed'].includes(order?.status || "")) {
          setStatus('failed');
          setError('订单已取消或支付失败');
          return;
        }
        // 继续轮询
        if (Date.now() - startTime < maxDuration) {
          setTimeout(poll, interval);
        } else {
          setStatus('failed');
          setError('支付超时，请检查支付结果或重新下单');
        }
      } catch (err) {
        if (!active) return;
        console.error('Polling error:', err);
        if (Date.now() - startTime < maxDuration) {
          setTimeout(poll, interval);
        } else {
          setStatus('failed');
          setError('无法获取订单状态，请稍后重试');
        }
      }
    };
    poll();
    return () => {
      active = false;
    };
  }, [order_number]);


  const handleGoToDashboard = () => {
    navigate('/profile');
  };

  const handleRetry = () => {
    navigate('/profile');
  };


  const handleBackHome = () => {
    navigate('/home');
  };


  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        {status === 'checking' && (
          <>
            <CircularProgress size={60} sx={{ mb: 3 }} />
            <Typography variant="h6" color="text.secondary">
              正在查询支付结果...
            </Typography>
            <Typography variant="body2" color="text.disabled" sx={{ mt: 1 }}>
              最多需要 60 秒，请不要关闭页面
            </Typography>
          </>
        )}
        {status === 'paid' && (
          <>
            <CheckCircleIcon
              sx={{ fontSize: 80, color: 'success.main', mb: 3 }}
            />
            <Typography variant="h5" color="success.main" gutterBottom>
              支付成功！
            </Typography>
            <Typography variant="body1" sx={{ mb: 3 }}>
              您的会员激活，感谢您的支持！
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={handleGoToDashboard}
              fullWidth
            >
              进入会员中心
            </Button>
          </>
        )}
        {status === 'failed' && (
          <>
            <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
            <Typography variant="h5" color="error.main" gutterBottom>
              支付未完成
            </Typography>
            <Alert severity="error" sx={{ mb: 3 }}>
              {error || '未知错误'}
            </Alert>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center' }}>
              <Button variant="outlined" onClick={handleRetry}>
                重新购买
              </Button>
              <Button variant="contained" onClick={handleBackHome}>
                返回首页
              </Button>
            </Box>
          </>
        )}
      </Paper>
    </Container>
  );
}


// Fallback for initial hydration

export function HydrateFallback() {
  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={60} sx={{ mb: 3 }} />
        <Typography>加载中...</Typography>
      </Paper>
    </Container>
  );
}


// 错误边界（处理 loader 报错，如无 order_number）
export function ErrorBoundary() {
  const navigate = useNavigate();
  return (
    <Container maxWidth="sm" sx={{ py: 6 }}>
      <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
        <ErrorIcon sx={{ fontSize: 80, color: 'error.main', mb: 3 }} />
        <Typography variant="h6" color="error" gutterBottom>
          页面初始化失败
        </Typography>
        <Typography variant="body2" sx={{ mb: 3 }}>
          未找到订单信息，请勿直接访问此页面。
        </Typography>
        <Button variant="contained" onClick={() => navigate('/home')}>
          返回首页
        </Button>
      </Paper>
    </Container>
  );
}