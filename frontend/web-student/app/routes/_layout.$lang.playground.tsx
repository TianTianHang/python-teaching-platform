import { Container, Box, Button, Typography, Paper, Alert, CircularProgress } from "@mui/material";
import type { Route } from "./+types/_layout.$lang.playground";
import { useState } from "react";
import http from "~/utils/http";
import CodeEditor from "~/components/CodeEditor";



export default function PlaygroundPage({ params }: Route.ComponentProps) {
  const [code, setCode] = useState<string>("print('Hello, World!')");
  const [output, setOutput] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const executeCode = async () => {
    setIsLoading(true);
    setError(null);
    setOutput(null);

    try {
      // Directly call the http utility which will handle authentication automatically
      const data = await http.post('/submissions/', {
        code: code,
        language: 'python'
      });

      // Handle both run_freely and submission results
      if (data.stdout !== undefined) {
        // Result from run_freely
        setOutput(`Status: ${data.status || 'completed'}\n${data.execution_time_ms ? `Execution Time: ${data.execution_time_ms}ms\n` : ''}${data.memory_used_kb ? `Memory Used: ${data.memory_used_kb}KB\n` : ''}Output:\n${data.stdout}${data.stderr ? `\n\nErrors:\n${data.stderr}` : ''}`);
      } else if (data.status) {
        // Result from submission
        setOutput(`Status: ${data.status}\nExecution Time: ${data.execution_time}ms\nMemory Usage: ${data.memory_usage}KB\n${data.stdout ? `\nOutput:\n${data.stdout}` : ''}${data.stderr ? `\nErrors:\n${data.stderr}` : ''}`);
      }
    } catch (err: any) {
      setError(err?.response?.data?.error || err?.message || 'An error occurred while executing code');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom align="center">
        Python Playground
      </Typography>
      
      <Paper elevation={3} sx={{ p: 2, mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6">Code Editor</Typography>
          <Button
            variant="contained"
            color="primary"
            onClick={executeCode}
            disabled={isLoading}
            startIcon={isLoading ? <CircularProgress size={20} /> : null}
          >
            {isLoading ? 'Executing...' : 'Run Code'}
          </Button>
        </Box>
        <CodeEditor code={code} onChange={setCode} />
      </Paper>

      {(output || error) && (
        <Paper elevation={3} sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>Execution Result</Typography>
          {error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
            <Box
              component="pre"
              sx={{
                backgroundColor: '#f5f5f5',
                p: 2,
                borderRadius: 1,
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                maxHeight: '300px',
                overflowY: 'auto'
              }}
            >
              {output}
            </Box>
          )}
        </Paper>
      )}
    </Container>
  );
}