import { Container, Box, Button, Typography, Paper, Alert, CircularProgress } from "@mui/material";

import { useState } from "react";
import CodeEditor from "~/components/CodeEditor";
import useSubmission from "~/hooks/useSubmission";
import SubmissionOutputViewer from "~/components/SubmissionOutputViewer";



export default function PlaygroundPage() {
  const [code, setCode] = useState<string>("print('Hello, World!')");
  const { output, isLoading, error, executeCode } = useSubmission();
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
            onClick={()=>executeCode({code:code,language:'python'})}
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
              <SubmissionOutputViewer output={output} isLoading={isLoading}/>
          )}
        </Paper>
      )}
      {/* <Box>
        <JupyterLiteEmbed/>
      </Box> */}
    </Container>
  );
}