import { Box, AppBar, Toolbar, Grid, Paper, Typography, Divider, Button, Card, CardContent, Tabs, Tab, Alert, Stack, IconButton, ButtonGroup } from "@mui/material";
import { useState, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import { useFetcher, useNavigate } from "react-router";
import remarkGfm from "remark-gfm";
import CodeEditor from "~/components/CodeEditor";
import SubmissionOutputViewer from "~/components/SubmissionOutputViewer";
import { a11yProps, TabPanel } from "~/components/TabUtils";
import useSubmission from "~/hooks/useSubmission";
import type { AlgorithmProblem, TestCase } from "~/types/course";
import type { Submission, SubmissionRes } from "~/types/submission";
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import type { Page } from "~/types/page";
export const CaseDetail = ({ testcase }: { testcase: TestCase }) => {
    return <Stack>
        <Box>
            <Typography variant="body2">Input:</Typography>
            {testcase.input_data}
        </Box>

        <Box>
            <Typography variant="body2">Output:</Typography>
            {testcase.expected_output}
        </Box>

    </Stack>
}

export default function AlgorithmProblemPage({ problem }: { problem: AlgorithmProblem }) {
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
    const [t3, setT3] = useState(0);
    const onTab3Change = (_: React.SyntheticEvent, newValue: number) => {
        setT3(newValue); // ✅ 修复：原来是 setT1
    };
    const [code, setCode] = useState<string>(problem.code_template.python);
    const { output, isLoading, error, executeCode } = useSubmission();
    const [submissions, setSubmissions] = useState<Page<Submission>>();
    const [submissionsLoading, setSubmissionsLoading] = useState(true);
    const fetcher = useFetcher()
    // 获取状态颜色
    const getStatusColor = (status: string) => {
        switch(status) {
            case 'accepted': return '#4caf50';
            case 'wrong_answer': return '#f44336';
            case 'time_limit_exceeded': return '#ff9800';
            case 'memory_limit_exceeded': return '#ff9800';
            case 'runtime_error': return '#f44336';
            case 'compilation_error': return '#f44336';
            case 'pending': return '#9e9e9e';
            case 'judging': return '#2196f3';
            default: return '#9e9e9e';
        }
    };
    
    // 加载提交的代码到编辑器
    const loadSubmission = (submissionCode: string) => {
        setCode(submissionCode);
    };
    
    // 获取提交历史
    const fetchSubmissions = async () => {
        try {
            await fetcher.load(`/submission?id=${problem.id}`);
            const data = fetcher.data as Page<Submission>;
            console.log(data)
            setSubmissions(data);
        } catch (err) {
            console.error('获取提交记录失败:', err);
        } finally {
            setSubmissionsLoading(false);
        }
    };
    
    useEffect(() => {
        if (!isLoading) {
            setT1(1)
        }
    }, [isLoading])
    
    useEffect(() => {
        if (!isLoading) {
            fetchSubmissions();
        }
    }, [problem.id,isLoading]);
    
    const navigate = useNavigate()
    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
            {/* 顶部 AppBar */}
            <AppBar position="static">
                <Toolbar>
                    <IconButton onClick={() => navigate(-1)}
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{ mr: 2 }}>
                        <ArrowBackIosIcon />
                    </IconButton>
                    <ButtonGroup sx={{ marginLeft: 'auto', marginRight: 'auto', }}>
                        <IconButton
                            size="large"
                            color="inherit"
                            edge="start"
                            loading={isLoading}
                            onClick={() =>
                                executeCode({
                                    code: code,
                                    language: 'python',
                                    problem_id: Number(problem.id),
                                })
                            }
                        >
                            <PlayArrowIcon />
                        </IconButton>
                    </ButtonGroup>
                    {/* 右侧占位，宽度等于左侧 IconButton 的宽度（约 40px） */}
                    <Box sx={{ width: 40 }} />
                </Toolbar>
            </AppBar>

            {/* 主内容区 - 使用 Grid 响应式布局 */}
            <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
                <Grid container spacing={3} sx={{ height: '100%' }}>
                    {/* 左侧：题目 */}
                    <Grid size={{ xs: 12, md: 7 }} sx={{ height: { xs: 'auto', md: '100%' } }}>
                        <Paper elevation={3} sx={{ p: 3, height: '100%', overflow: 'auto' }}>
                            <Tabs value={t3} onChange={onTab3Change}>
                                <Tab label={"描述"} {...a11yProps(0)}></Tab>
                                <Tab label={"submisstion"} {...a11yProps(1)}></Tab>
                            </Tabs>
                            <TabPanel index={0} value={t3}>

                                <Typography variant="h4">{`${problem.id}.${problem.title}`}</Typography>
                                <Divider />
                                <Typography variant="h5" gutterBottom>题目描述</Typography>
                                <Box sx={markdownStyle}>
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                        {problem.content}
                                    </ReactMarkdown>
                                </Box>

                            </TabPanel>
                            <TabPanel index={1} value={t3}>

                                <Typography variant="h4">SUBMISSION</Typography>
                                
                                <Box sx={{ mt: 2 }}>
                                    <Typography variant="h6">提交记录</Typography>
                                    {submissionsLoading ? (
                                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                                            加载中...
                                        </Typography>
                                    ) : submissions && submissions.results.length > 0 ? (
                                        <Stack spacing={2} sx={{ mt: 1 }}>
                                            {submissions.results.map((submission, index) => (
                                                <Card key={submission.id} variant="outlined" sx={{ p: 2 }}>
                                                    <Grid container justifyContent="space-between" alignItems="center">
                                                        <Grid >
                                                            <Typography variant="body1" sx={{ fontWeight: 'bold' }}>
                                                                提交 #{submissions.results.length - index}
                                                            </Typography>
                                                            <Typography variant="body2" color="text.secondary">
                                                                状态: <span style={{ color: getStatusColor(submission.status) }}>{submission.status}</span> |
                                                                时间: {submission.execution_time ? `${submission.execution_time}ms` : 'N/A'} |
                                                                内存: {submission.memory_used ? `${submission.memory_used}KB` : 'N/A'}
                                                            </Typography>
                                                        </Grid>
                                                        <Grid>
                                                            <Button size="small" onClick={() => loadSubmission(submission.code)}>
                                                                重新使用
                                                            </Button>
                                                        </Grid>
                                                    </Grid>
                                                    {submission.output && (
                                                        <Box sx={{ mt: 1 }}>
                                                            <Typography variant="body2" sx={{ wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
                                                                输出: {submission.output}
                                                            </Typography>
                                                        </Box>
                                                    )}
                                                    {submission.error && (
                                                        <Box sx={{ mt: 1 }}>
                                                            <Typography variant="body2" color="error" sx={{ wordBreak: 'break-word', whiteSpace: 'pre-wrap' }}>
                                                                错误: {submission.error}
                                                            </Typography>
                                                        </Box>
                                                    )}
                                                </Card>
                                            ))}
                                        </Stack>
                                    ) : (
                                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                                            暂无提交记录
                                        </Typography>
                                    )}
                                </Box>


                            </TabPanel>
                        </Paper>
                    </Grid>

                    {/* 右侧：编辑器 + 测试 */}
                    <Grid size={{ xs: 12, md: 5 }} sx={{ height: { xs: 'auto', md: '100%',overflow: 'hidden',  } }}>

                        <Paper
                            elevation={3}
                            sx={{
                                p: 2,
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                            }}
                        >
                            {/* 代码编辑器区域：设置固定高度，允许内部滚动 */}
                            <Box
                                sx={{
                                    flex: 1,
                                    minHeight: 300,        // 提高最小高度保证可见
                                    maxHeight: '60vh',     // 最大不超过 60% 视口高度
                                    mb: 2,
                                    overflow: 'hidden',      // 启用滚动以处理内容超出
                                    '& .cm-editor': {
                                        height: '100%',
                                    },
                                    '& .cm-scroller': {
                                        overflow: 'auto',
                                    }
                                }}
                            >
                                <CodeEditor code={code} onChange={setCode} />
                            </Box>

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