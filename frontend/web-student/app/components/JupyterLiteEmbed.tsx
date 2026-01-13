import { Box, IconButton, Paper, useTheme } from '@mui/material';
import { Fullscreen, FullscreenExit } from '@mui/icons-material';
import { useEffect, useRef } from 'react';
import { showNotification } from './Notification';
import { useFullscreen } from 'ahooks';

interface JupyterLiteEmbedProps {
    url: string;
    access: string | undefined;
}

const JupyterLiteEmbed = ({ url, access }: JupyterLiteEmbedProps) => {
    const theme = useTheme();
    const iframeRef = useRef<HTMLIFrameElement>(null);
    const ref = useRef<HTMLDivElement>(null);
    const [isFullscreen, { toggleFullscreen }] = useFullscreen(ref, {
        pageFullscreen: true,
    });
    useEffect(() => {

        const handleMessage = (event: MessageEvent) => {

            if (event.data?.type === 'JUPYTER_READY') {
                console.log('✅ JupyterLite is ready. Sending config...');
                handleIframeLoad();
            }
        };
        window.addEventListener('message', handleMessage);
        return () => window.removeEventListener('message', handleMessage);
    }, []);

    const handleIframeLoad = () => {
        const iframe = iframeRef.current;
        if (!iframe || !iframe.contentWindow) return;
        if (access === undefined) {
            console.warn('⚠️ Access token is undefined. Cannot use file service.');
            showNotification('warning', 'Access Token Missing', 'Cannot use file service without a valid access token.');
        }
        // 发送 Jupyter 配置
        iframe.contentWindow.postMessage(
            {
                type: 'SET_JUPYTER_CONFIG',
                config: {
                    baseUrl: import.meta.env.VITE_JUPYTER_BASE_URL,
                    token: access,
                },
            },
            "*" // 注意：生产环境应替换为具体的 origin（如 'http://localhost:8000'）
        );
    };
    return (
        <Box sx={{ width: '100%', height: '800px', my: 2, position: 'relative' }}>
            <Paper
                ref={ref}
                elevation={3}
                sx={{
                    width: '100%',
                    height: '100%',
                    overflow: 'hidden',
                    borderRadius: theme.shape.borderRadius,
                    border: 'none',

                }}
            >
                <iframe
                    ref={iframeRef}
                    id="jupyter-iframe"
                    src={url}
                    title="JupyterLite"
                    width="100%"
                    height="100%"
                    style={{ border: 'none' }}
                    allowFullScreen
                    onLoad={handleIframeLoad}
                />
                <IconButton
                    onClick={toggleFullscreen}
                    sx={{
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        zIndex: 10,
                        bgcolor: 'background.paper',
                        boxShadow: 2,
                        '&:hover': {
                            bgcolor: 'background.default',
                        },
                    }}
                >
                    {isFullscreen ? <FullscreenExit /> : <Fullscreen />}
                </IconButton>
            </Paper>

        </Box>
    );
};

export default JupyterLiteEmbed;