import { Box, Paper, useTheme } from '@mui/material';
import type { ICommandBridgeRemote } from 'jupyter-iframe-commands';
import { createBridge } from 'jupyter-iframe-commands-host';
import { useEffect, useRef } from 'react';
const JupyterLiteEmbed = () => {
    const theme = useTheme();
    // Create a bridge to the JupyterLite instance
    const commandBridge:ICommandBridgeRemote = createBridge({ iframeId: 'jupyter-iframe' });
    
    // List all available JupyterLab commands
      async function listCommands() {
        const commands = await commandBridge.listCommands();
        console.log(commands);
      }

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
                    src="/jupyterlite/lab/index.html"
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