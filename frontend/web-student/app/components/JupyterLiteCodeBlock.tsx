import { Box, useTheme, keyframes } from '@mui/material';
import { useMemo, useState, useEffect, useRef } from 'react';

interface JupyterLiteCodeBlockProps {
    code?: string;
    height?: number | string;
}

const fadeIn = keyframes`
    from {
        opacity: 0;
    }
    to {
        opacity: 1;
    }
`;

const JupyterLiteCodeBlock = ({ code, height = 400 }: JupyterLiteCodeBlockProps) => {
    const theme = useTheme();
    const [pendingSrc, setPendingSrc] = useState<string | null>(null);
    const [currentSrc, setCurrentSrc] = useState<string>('');
    const [showTransition, setShowTransition] = useState(false);
    const iframeRef = useRef<HTMLIFrameElement>(null);

    const iframeSrc = useMemo(() => {
        const jupyterTheme = theme.palette.mode === 'dark' ? 'JupyterLab Dark' : 'JupyterLab Light';
        const encodedCode = code ? code : '';
        const baseUrl = 'https://tiantianhang.github.io/python-teaching-platform/repl/index.html';

        const params = new URLSearchParams({
            toolbar: '1',
            kernel: 'xpython',
            theme: jupyterTheme,
            promptCellPosition: 'left',
            clearCellsOnExecute: '1',
            hideCodeInput: '1',
            clearCodeContentOnExecute: '0',
            showBanner: '0',
            code: encodedCode,
            execute: '0',
        });

        return `${baseUrl}?${params.toString()}`;
    }, [code, theme.palette.mode]);

    // 初始化或主题变化时，准备新的iframe
    useEffect(() => {
        if (!currentSrc) {
            // 首次加载
            setCurrentSrc(iframeSrc);
        } else if (currentSrc !== iframeSrc) {
            // 主题切换，在后台加载新的
            setPendingSrc(iframeSrc);
        }
    }, [iframeSrc]);

    // 处理新iframe加载完成
    const handlePendingIframeLoad = () => {
        setShowTransition(true);
        // 等待淡出动画完成
        setTimeout(() => {
            setCurrentSrc(pendingSrc!);
            setPendingSrc(null);
            setShowTransition(false);
        }, 300);
    };

    return (
        <Box
            sx={{
                width: '100%',
                height: typeof height === 'number' ? `${height}px` : height,
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1,
                overflow: 'hidden',
                position: 'relative',
                bgcolor: 'background.paper',
            }}
        >
            {/* 当前显示的iframe */}
            <iframe
                ref={iframeRef}
                src={currentSrc}
                style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    opacity: showTransition ? 0 : 1,
                    transition: 'opacity 0.3s ease-in-out',
                    animation: !showTransition ? `${fadeIn} 0.3s ease-in-out` : 'none',
                }}
                sandbox="allow-scripts allow-same-origin allow-forms"
                title="JupyterLite Code Block - Current"
            />

            {/* 后台加载的新iframe */}
            {pendingSrc && (
                <iframe
                    src={pendingSrc}
                    onLoad={handlePendingIframeLoad}
                    style={{
                        width: '100%',
                        height: '100%',
                        border: 'none',
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        opacity: 0,
                        pointerEvents: 'none',
                    }}
                    sandbox="allow-scripts allow-same-origin allow-forms"
                    title="JupyterLite Code Block - Pending"
                />
            )}
        </Box>
    );
};

export default JupyterLiteCodeBlock;