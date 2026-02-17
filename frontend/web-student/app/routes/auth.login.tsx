// LoginPage.tsx
import * as React from 'react';
import { useEffect, useState } from 'react';
import {
    Box,
    Typography,
    Alert,
    useTheme,
} from '@mui/material';
import { useSubmit, redirect } from 'react-router';
import type { Route } from './+types/auth.login';
import type { Token, User } from '~/types/user';
import { commitSession, getSession } from '~/sessions.server';
import createHttp from '~/utils/http/index.server';
import { AuthContainer, AuthButton, AuthLink } from '~/components/Auth';
import { FormTextField } from '~/components/Form';
import { DEFAULT_META, formatTitle, PAGE_TITLES } from '~/config/meta';



export async function action({
    request }: Route.ActionArgs) {
    const formData = await request.formData();
    const username = String(formData.get("username"));
    const password = String(formData.get("password"));

    try {
        const http = createHttp(request);
        const token = await http.post<Token>("auth/login", { username, password })
        // 创建 session
        const session = await getSession(request.headers.get('Cookie'));
        session.set('accessToken', token.access);
        //console.log(`access: ${token.access}`)
        session.set('refreshToken', token.refresh);
        session.set('isAuthenticated', true);
        const user = await http.get<User>("auth/me", {}, { headers: { Authorization: `Bearer ${token.access}` } });
        session.set('user', user);
        return redirect(`/home`, {
            headers: {
                'Set-Cookie': await commitSession(session),
            },
        });
    } catch (error) {
        return { error: (error as Error).message };
    }
}

export default function LoginPage({ actionData }: Route.ComponentProps) {
    const theme = useTheme();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const [loading, setLoading] = useState(false);
    const submit = useSubmit()
    const [error, setError] = useState<string | null>(null);

    // 当 actionData 更新时，表示提交完成
    useEffect(() => {
        if (actionData !== undefined) {
            if (actionData?.error !== undefined) {
                setError(actionData.error)
            }

            setLoading(false);
        }
    }, [actionData]);

    const handleSubmit = (event: React.FormEvent) => {
        event.preventDefault();
        setLoading(true);
        setError(null);
        submit({ username, password }, { method: 'post' });
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
