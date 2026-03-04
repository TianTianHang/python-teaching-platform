// LoginPage.tsx
import * as React from 'react';
import { useEffect, useState } from 'react';
import {
    Box,
    Typography,
    Alert,
    useTheme,
} from '@mui/material';
import { useNavigate } from 'react-router';
import { clientAuth } from '~/utils/http/client';
import { AuthContainer, AuthButton, AuthLink } from '~/components/Auth';
import { FormTextField } from '~/components/Form';
import { formatTitle, PAGE_TITLES } from '~/config/meta';


export default function LoginPage() {
    const theme = useTheme();
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const { token, user } = await clientAuth.login(username, password);
            
            // 设置服务端 session（用于 SSR）
            const formData = new FormData();
            formData.append('accessToken', token.access);
            formData.append('refreshToken', token.refresh);
            formData.append('user', JSON.stringify(user));
            
            await fetch('/auth/set-session', {
                method: 'POST',
                body: formData,
                credentials: 'include',
            });
            
            navigate('/home');
        } catch (err: any) {
            const message = err.response?.data?.detail 
                || err.response?.data?.non_field_errors?.[0]
                || '登录失败，请检查用户名和密码';
            setError(message);
        } finally {
            setLoading(false);
        }
    };


    return (
        <>
            <title>{formatTitle(PAGE_TITLES.login)}</title>
            <AuthContainer title="登录" subtitle="请输入您的账号信息">
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
                    name="password"
                    label="密码"
                    type="password"
                    id="password"
                    autoComplete="current-password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
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
                    loadingText="登录中..."
                >
                    登录
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
                        to="/auth/register"
                        text="还没有账号？"
                        linkText="去注册"
                    />
                </Typography>
            </Box>
        </AuthContainer></>
    );
}
