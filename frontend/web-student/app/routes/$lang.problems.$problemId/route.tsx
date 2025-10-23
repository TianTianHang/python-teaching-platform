import React, { useEffect, useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Tabs,
  Tab,
  Divider,
  Card,
  CardContent,
  Grid,
  Avatar,
  Container,
  Stack,
  AppBar,
  Toolbar,
  IconButton,
  Alert,
} from '@mui/material';
import type { Route } from './+types/route';
import http from '~/utils/http';
import type { AlgorithmProblem, Problem } from '~/types/course';
import { useRouteError } from 'react-router';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { a11yProps, TabPanel } from '~/components/TabUtils';
import { CaseDetail } from '~/components/Problem/AlgorithmProblemDetail';
import CodeEditor from '~/components/CodeEditor';
import useSubmission from '~/hooks/useSubmission';
import SubmissionOutputViewer from '~/components/SubmissionOutputViewer';

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
  const problem = await http.get<Problem>(`/problems/${params.problemId}`);
  if (problem.type !== 'algorithm') {
    throw new Error('Not an algorithm problem!');
  }
  return problem as AlgorithmProblem;
}

export default function ProblemPage({ loaderData, params }: Route.ComponentProps) {
  const problem = loaderData;

  const markdownStyle = {
    '& h1, & h2, & h3, & h4, & h5, & h6': { mt: 3, mb: 1 },
    '& p': { mb: 2 },
    '& ul, & ol': { ml: 4, mb: 2 },
    '& a': {
      color: 'primary.main',
      textDecoration: 'none',
      '&:hover': { textDecoration: 'underline' },
    },
    '& code': {
      backgroundColor: '#f2f2f2',
      padding: '2px 4px',
      borderRadius: '4px',
      fontFamily: 'monospace',
    },
    '& pre': {
      backgroundColor: '#2d2d2d',
      color: '#f8f8f2',
      padding: '16px',
      borderRadius: '8px',
      overflowX: 'auto',
      margin: '24px 0',
    },
    '& pre code': {
      backgroundColor: 'transparent',
      padding: 0,
      borderRadius: 0,
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-word',
    },
  };

  const [t1, setT1] = useState(0);
  const onTab1Change = (_: React.SyntheticEvent, newValue: number) => {
    setT1(newValue);
  };

  const [t2, setT2] = useState(0);
  const onTab2Change = (_: React.SyntheticEvent, newValue: number) => {
    setT2(newValue); // ✅ 修复：原来是 setT1
  };

  const [code, setCode] = useState<string>(problem.code_template.python);
  const { output, isLoading, error, executeCode } = useSubmission();
  useEffect(()=>{
    if(!isLoading){
      setT1(1)
    }
  },[isLoading])
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* 顶部 AppBar */}
      <AppBar position="static">
        <Toolbar>

        </Toolbar>
      </AppBar>

      {/* 主内容区 - 使用 Grid 响应式布局 */}
      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <Grid container spacing={3} sx={{ height: '100%' }}>
          {/* 左侧：题目 */}
          <Grid size={{ xs: 12, md: 7 }} sx={{ height: { xs: 'auto', md: '100%' } }}>
            <Paper elevation={3} sx={{ p: 3, height: '100%', overflow: 'auto' }}>
              <Typography variant="h4">{`${problem.id}.${problem.title}`}</Typography>
              <Divider />
              <Typography variant="h5" gutterBottom>题目描述</Typography>
              <Box sx={markdownStyle}>
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {problem.content}
                </ReactMarkdown>
              </Box>
            </Paper>
          </Grid>

          {/* 右侧：编辑器 + 测试 */}
          <Grid size={{ xs: 12, md: 5 }} sx={{ height: { xs: 'auto', md: '100%' } }}>

            <Paper
              elevation={3}
              sx={{
                p: 2,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
              }}
            >
              {/* 代码编辑器区域：限制最大高度，可滚动 */}
              <Box
                sx={{
                  flex: 1,
                  minHeight: 120,        // 最小高度保证可见
                  maxHeight: '60vh',     // 最大不超过 60% 视口高度
                  mb: 2,
                  overflow: 'hidden',    // 或 'auto' 如果 CodeEditor 内部不滚动
                }}
              >
                <CodeEditor code={code} onChange={setCode} />
              </Box>

              {/* 提交按钮：固定高度 */}
              <Button variant="contained" color="primary" fullWidth sx={{ mb: 2 }} 
              loading={isLoading}
              onClick={
                () => executeCode({ code: code, language: 'python', problem_id: Number(params.problemId) })
              }>
                提交代码
              </Button>

              {/* 测试结果：占据剩余空间，可滚动 */}
              <Card sx={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
                <CardContent>
                  {/* Tabs + TabPanel 内容放这里 */}
                  <Tabs value={t1} onChange={onTab1Change}>
                    <Tab label="测试用例" {...a11yProps(0)} />
                    <Tab label="Output" {...a11yProps(1)} />
                  </Tabs>

                  <TabPanel index={0} value={t1}>
                    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                      <Tabs value={t2} onChange={onTab2Change}>
                        {problem.sample_cases
                          .filter((tc) => tc.is_sample)
                          .map((_, index) => (
                            <Tab key={index} label={`Case ${index + 1}`} {...a11yProps(index)} />
                          ))}
                      </Tabs>
                    </Box>
                    {problem.sample_cases
                      .filter((tc) => tc.is_sample)
                      .map((tc, index) => (
                        <TabPanel key={index} index={index} value={t2}>
                          <CaseDetail testcase={tc} />
                        </TabPanel>
                      ))}
                  </TabPanel>

                  <TabPanel index={1} value={t1}>
                    <Typography variant="body2" color="text.secondary">
                      {error ? (
                        <Alert severity="error">{error}</Alert>
                      ) : (
                          <SubmissionOutputViewer output={output} isLoading={isLoading} />
                      )}
                    </Typography>
                  </TabPanel>
                </CardContent>
              </Card>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Box>
  );
}