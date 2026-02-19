// RegisterPage.tsx
import * as React from 'react';
import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Alert,
  useTheme,
} from '@mui/material';
import { useSubmit, redirect } from 'react-router';
import type { Route } from './+types/auth.register';
import createHttp from '~/utils/http/index.server';
import { commitSession, getSession } from '~/sessions.server';
import type { User } from '~/types/user';
import { AuthContainer, AuthButton, AuthLink } from '~/components/Auth';
import { FormTextField } from '~/components/Form';
import { formatTitle, PAGE_TITLES } from '~/config/meta';


export async function action({
  request,
}: Route.ActionArgs) {
  const formData = await request.formData();
  const username = String(formData.get('username'));
  const password = String(formData.get('password'));
  const stNumber = String(formData.get('stNumber'));
  
  try {
    const http = createHttp(request);
    const response = await http.post<{
      user: User;
      access: string;
      refresh: string;
    }>('auth/register', {
      username,
      password,
      st_number: stNumber,
    });

   
    const session = await getSession(
      request.headers.get('Cookie')
    );
    session.set('accessToken', response.access);
    session.set('refreshToken', response.refresh);
    session.set('user', response.user);
    session.set('isAuthenticated', true);

    return redirect(`/home`, {
      headers: {
        'Set-Cookie': await commitSession(session),
      },
    });
  } catch (error) {
    // 你可以根据实际 API 错误细化 message
    return { error: (error as Error ).message };
  }
}

export default function RegisterPage({ actionData }: Route.ComponentProps) {
  const theme = useTheme();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [stNumber, setStNumber] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [clientError, setClientError] = useState<string | null>(null);

  const submit = useSubmit();

  // 当 action 执行完毕（无论成功失败），actionData 会更新，此时关闭 loading
  useEffect(() => {
    if (actionData !== undefined) {
      setLoading(false);
    }
  }, [actionData]);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    setClientError(null);

    // 客户端验证
    if (password !== confirmPassword) {
      setClientError('密码和确认密码不匹配');
      return;
    }

    if (password.length < 6) {
      setClientError('密码长度至少为6位');
      return;
    }

    if (stNumber.length !== 12) {
      setClientError('学号长度必须为12位!');
      return;
    }

    setLoading(true);
    // 提交到 action（服务端）
    submit(
      { username, password, stNumber },
      { method: 'post' }
    );
    // 注意：submit 是同步导航行为，不会返回 Promise
  };

  // 优先显示客户端错误，否则显示服务端错误
  const error = clientError || actionData?.error || null;

  return (
    <>
      <title>{formatTitle(PAGE_TITLES.register)}</title>
      <AuthContainer title="注册" subtitle="创建您的账号信息">
      <Box component="form" onSubmit={handleSubmit} noValidate>
        <FormTextField
          margin="normal"
          required
          fullWidth
          id="username"
          label="用户名"
          name="username"
          autoComplete="username"
          autoFocus
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <FormTextField
          margin="normal"
          required
          fullWidth
          id="stNumber"
          label="学号"
          name="stNumber"
          autoComplete="stNumber"
          value={stNumber}
          onChange={(e) => setStNumber(e.target.value)}
        />
        <FormTextField
          margin="normal"
          required
          fullWidth
          name="password"
          label="密码"
          type="password"
          id="password"
          autoComplete="new-password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <FormTextField
          margin="normal"
          required
          fullWidth
          name="confirmPassword"
          label="确认密码"
          type="password"
          id="confirmPassword"
          autoComplete="new-password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
        />
        {error && (
          <Alert
            severity="error"
            sx={{
              mt: 2,
              backgroundColor: theme.palette.error.light,
              borderLeft: `4px solid ${theme.palette.error.main}`,
            }}
          >
            {error}
          </Alert>
        )}
        <AuthButton
          type="submit"
          loading={loading}
          loadingText="注册中..."
        >
          注册
        </AuthButton>
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            textAlign: 'center',
            mt: 2,
          }}
        >
          <AuthLink
            to="/auth/login"
            text="已经有账号了？"
            linkText="去登录"
          />
        </Typography>
      </Box>
    </AuthContainer>
    </>
  );
}