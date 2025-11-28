import { Box, Paper, useTheme } from '@mui/material';

const JupyterLiteEmbed = ({url}:{url:string}) => {
    const theme = useTheme();
  

    return (
        <Box sx={{ width: '100%', height: '800px', my: 2 }}>
            <Paper
                elevation={3}
                sx={{
                    width: '100%',
                    height: '100%',
                    overflow: 'hidden',
                    borderRadius: theme.shape.borderRadius,
                    border: 'none', // 移除 iframe 默认边框，由 Paper 提供阴影/边框感
                }}
            >
                <iframe
                    id='jupyter-iframe'
                    src={url}
                    title="JupyterLite"
                    width="100%"
                    height="100%"
                    style={{ border: 'none' }}
                    allowFullScreen
                  
                />
            </Paper>
        </Box>
    );
};

export default JupyterLiteEmbed;