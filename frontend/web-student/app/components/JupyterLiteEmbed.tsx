import { Box, Paper, useTheme } from '@mui/material';
import { useEffect, useRef } from 'react';

interface JupyterLiteEmbedProps {
    url: string;
    access: string;
}

const JupyterLiteEmbed = ({ url, access }: JupyterLiteEmbedProps) => {
    const theme = useTheme();
    const iframeRef = useRef<HTMLIFrameElement>(null);

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
        <Box sx={{ width: '100%', height: '800px', my: 2 }}>
            <Paper
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
            </Paper>
        </Box>
    );
};

export default JupyterLiteEmbed;