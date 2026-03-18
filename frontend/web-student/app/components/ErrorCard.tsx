import { Paper, Stack, Typography, Button, Box } from "@mui/material";
import { Refresh, Home, Warning } from "@mui/icons-material";
import { spacing } from "~/design-system/tokens";

/**
 * Props for the ErrorCard component
 */
interface ErrorCardProps {
    /** HTTP status code or error type */
    status?: number | string;
    /** Error message to display */
    message?: string;
    /** Section title for context */
    title?: string;
    /** Callback when retry is clicked */
    onRetry?: () => void;
    /** Whether a retry is in progress */
    isLoading?: boolean;
}

/**
 * Maps HTTP status codes and error types to friendly Chinese messages
 */
function getFriendlyErrorMessage(status?: number | string, message?: string): string {
    // Handle network-related errors
    if (message?.includes('timeout') || message?.includes('超时')) {
        return "网络连接超时，请检查您的网络设置";
    }
    if (message?.includes('Network') || message?.includes('fetch')) {
        return "网络连接失败，请检查网络后重试";
    }

    // Handle HTTP status codes
    const statusCode = typeof status === 'number' ? status : parseInt(String(status));

    switch (statusCode) {
        case 400:
            return "请求参数不正确，请刷新页面重试";
        case 403:
            return "您没有权限查看此内容";
        case 404:
            return "请求的内容不存在";
        case 429:
            return "请求过于频繁，请稍后再试";
        case 500:
            return "服务器出错了，我们正在努力修复";
        case 502:
            return "网关错误，请稍后重试";
        case 503:
            return "服务暂时不可用，请稍后重试";
        case 504:
            return "请求超时，请检查网络连接";
        default:
            return message || "加载失败，请稍后重试";
    }
}

/**
 * Determines if an error is retriable based on status code
 */
function isRetriableError(status?: number | string): boolean {
    const statusCode = typeof status === 'number' ? status : parseInt(String(status));

    // 5xx errors are retriable
    if (statusCode >= 500 && statusCode < 600) {
        return true;
    }

    // 429 Too Many Requests is retriable
    if (statusCode === 429) {
        return true;
    }

    // Network errors (no status code) are retriable
    if (!status) {
        return true;
    }

    // 4xx errors are not retriable (except 429)
    return false;
}

/**
 * ErrorCard component - Displays a friendly error UI with optional retry
 *
 * Features:
 * - Error icon and friendly Chinese messages
 * - Conditional retry button (only for retriable errors)
 * - Back to home button
 * - Loading state during retry
 */
export function ErrorCard({
    status,
    message,
    title = "加载失败",
    onRetry,
    isLoading = false
}: ErrorCardProps) {
    const friendlyMessage = getFriendlyErrorMessage(status, message);
    const canRetry = isRetriableError(status);

    return (
        <Paper
            elevation={0}
            sx={{
                p: spacing.xl,
                border: '1px solid',
                borderColor: 'warning.main',
                borderRadius: 2,
                bgcolor: 'warning.50',
            }}
        >
            <Stack
                direction="column"
                alignItems="center"
                spacing={spacing.md}
                textAlign="center"
            >
                {/* Error Icon */}
                <Box
                    sx={{
                        width: 64,
                        height: 64,
                        borderRadius: '50%',
                        bgcolor: 'warning.main',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}
                >
                    <Warning
                        sx={{
                            fontSize: 40,
                            color: 'warning.contrastText',
                        }}
                    />
                </Box>

                {/* Error Title */}
                <Typography variant="h6" color="text.primary">
                    {title}
                </Typography>

                {/* Error Message */}
                <Typography variant="body2" color="text.secondary">
                    {friendlyMessage}
                </Typography>

                {/* Action Buttons */}
                <Stack
                    direction="row"
                    spacing={spacing.sm}
                    sx={{ mt: spacing.sm }}
                >
                    {canRetry && onRetry && (
                        <Button
                            variant="contained"
                            startIcon={<Refresh />}
                            onClick={onRetry}
                            disabled={isLoading}
                            color="primary"
                        >
                            {isLoading ? "重新加载中..." : "重新加载"}
                        </Button>
                    )}

                    <Button
                        variant="outlined"
                        startIcon={<Home />}
                        href="/home"
                        disabled={isLoading}
                    >
                        返回首页
                    </Button>
                </Stack>
            </Stack>
        </Paper>
    );
}
