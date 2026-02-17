import { Box, useTheme, CircularProgress } from '@mui/material';
import { useMemo, useState, useEffect } from 'react';

interface JupyterLiteCodeBlockProps {
    code?: string;
    height?: number | string;
}

const JupyterLiteCodeBlock = ({ code, height = 400 }: JupyterLiteCodeBlockProps) => {
    const theme = useTheme();
    const [pendingSrc, setPendingSrc] = useState<string | null>(null);
    const [currentSrc, setCurrentSrc] = useState<string>('');
    const [isLoading, setIsLoading] = useState(true);

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

    // Handle initial load and theme switching
    useEffect(() => {
        if (!currentSrc) {
            // Initial load
            setCurrentSrc(iframeSrc);
        } else if (currentSrc !== iframeSrc) {
            // Theme switching - show loading mask and prepare new src
            setIsLoading(true);
            setPendingSrc(iframeSrc);
        }
    }, [iframeSrc]);

    // Handle iframe load complete with minimum loading time
    const handleIframeLoad = () => {
        // Set minimum loading time to ensure JupyterLite is fully ready
        setTimeout(() => {
            if (pendingSrc) {
                setCurrentSrc(pendingSrc);
                setPendingSrc(null);
            }
            // Small additional delay after content switch
            setTimeout(() => setIsLoading(false), 50);
        }, 500);
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
            {/* Loading mask - covers entire container during loading */}
            {isLoading && (
                <Box
                    sx={{
                        position: 'absolute',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: '100%',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        bgcolor: 'background.paper',
                        zIndex: 100,
                    }}
                >
                    <CircularProgress />
                </Box>
            )}

            {/* Current iframe */}
            <iframe
                key={currentSrc}
                src={currentSrc}
                onLoad={handleIframeLoad}
                style={{
                    width: '100%',
                    height: '100%',
                    border: 'none',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                }}
                sandbox="allow-scripts allow-same-origin allow-forms"
                title="JupyterLite Code Block"
            />

            {/* Preload new iframe for theme switching */}
            {pendingSrc && (
                <iframe
                    src={pendingSrc}
                    onLoad={handleIframeLoad}
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
