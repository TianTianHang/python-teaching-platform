import { Box, Button, Typography, Alert, CircularProgress } from "@mui/material";
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import { PageContainer, PageHeader, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { useEffect, useState } from "react";
import CodeEditor from "~/components/CodeEditor";
import useSubmission from "~/hooks/useSubmission";
import SubmissionOutputViewer from "~/components/SubmissionOutputViewer";
import { Code as CodeIcon, PlayArrow as PlayArrowIcon } from "@mui/icons-material";




export default function PlaygroundPage() {
  const [code, setCode] = useState<string>("print('Hello, World!')");
  const [disablePaste, setDisablePaste] = useState<boolean>(true);
  const { output, isLoading, error, executeCode } = useSubmission();
  // useEffect(()=>{
  //   console.log("Current code:", code);
  // },[code]);
  return (
    <>
      <title>{formatTitle(PAGE_TITLES.playground)}</title>
      <PageContainer maxWidth="md">
      <PageHeader
        title="Python Playground"
        subtitle="在线编写和运行 Python 代码"
      />
      
      <SectionContainer spacing="md" variant="card" height={'50vh'}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: spacing.md }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm }}>
            <CodeIcon sx={{ color: 'text.primary' }} />
            <Typography variant="h6" color="text.primary">Code Editor</Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: spacing.sm }}>
            {/* <Button
              variant={disablePaste ? "contained" : "outlined"}
              color={disablePaste ? "warning" : "primary"}
              onClick={() => setDisablePaste(!disablePaste)}
              size="small"
            >
              {disablePaste ? '粘贴已禁用' : '粘贴已启用'}
            </Button> */}
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
        </Box>
        <CodeEditor code={code} onChange={setCode} disablePaste={disablePaste} />
      </SectionContainer>

      {(output || error) && (
        <SectionContainer spacing="md" variant="card">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: spacing.sm, mb: spacing.md }}>
            <PlayArrowIcon sx={{ color: 'text.primary' }} />
            <Typography variant="h6" color="text.primary">Execution Result</Typography>
          </Box>
          {error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
              <SubmissionOutputViewer output={output} isLoading={isLoading}/>
          )}
        </SectionContainer>
      )}
      {/* <Box>
        <JupyterLiteEmbed/>
      </Box> */}
    </PageContainer>
    </>
  );
}