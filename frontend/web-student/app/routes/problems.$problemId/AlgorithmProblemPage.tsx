import { Box, AppBar, Toolbar, Grid, Paper, Typography, Divider, Button, Card, CardContent, Tabs, Tab, Alert, Stack, IconButton, ButtonGroup, Pagination } from "@mui/material";
import { useState, useEffect } from "react";
import { useFetcher, useNavigate } from "react-router";
import CodeEditor from "~/components/CodeEditor";
import SubmissionOutputViewer from "~/components/SubmissionOutputViewer";
import { a11yProps, TabPanel } from "~/components/TabUtils";
import useSubmission from "~/hooks/useSubmission";
import type { AlgorithmProblem, TestCase } from "~/types/course";
import type { Submission } from "~/types/submission";
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import SubmissionItem from "~/components/SubmissionTtem";
import MarkdownRenderer from "~/components/MarkdownRenderer";
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
   

    const [t1, setT1] = useState(0);
    const onTab1Change = (_: React.SyntheticEvent, newValue: number) => {
        setT1(newValue);
    };

    const [t2, setT2] = useState(0);
    const onTab2Change = (_: React.SyntheticEvent, newValue: number) => {
        setT2(newValue);
    };
    const [t3, setT3] = useState(0);
    const onTab3Change = (_: React.SyntheticEvent, newValue: number) => {
        setT3(newValue);
    };
    const [code, setCode] = useState<string>(problem.code_template.python);
    const { output, isLoading, error, executeCode } = useSubmission();
    const [submissions, setSubmissions] = useState<Submission[]>();
    const [submissionsLoading, setSubmissionsLoading] = useState(true);
    const [pageState, setPageState] = useState<{
        currentPage: number;
        totalItems: number;
        actualPageSize: number;
    }>();
    const [totalPages, setTotalPages] = useState<number>(0);
    const [refreshKey, setRefreshKey] = useState(0);
    const [init,setInit] = useState(true);
    const fetcher = useFetcher<{
        data: Submission[],
        currentPage: number,
        totalItems: number,
        actualPageSize: number,
    }>()


    // 加载提交的代码到编辑器
    const loadSubmission = (submissionCode: string) => {
        setCode(submissionCode);
    };

    useEffect(() => {
        if (!isLoading) {
            setT1(1)
        }
    }, [isLoading])
    useEffect(()=>{
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("problemId",String(problem.id));
        if (pageState?.currentPage && pageState.currentPage > 1) {
            newSearchParams.set('page', pageState.currentPage.toString());
        }
        fetcher.load(`/submission/?${newSearchParams.toString()}`);
        setSubmissionsLoading(true);
        setInit(false)
    },[])
    // 修改 useEffect 中的 fetcher.load 调用
    useEffect(() => {
        if(init){
            return
        }
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("problemId",String(problem.id));
        if (pageState?.currentPage && pageState.currentPage > 1) {
            newSearchParams.set('page', pageState.currentPage.toString());
        }
        fetcher.load(`/submission/?${newSearchParams.toString()}`);
        setSubmissionsLoading(true);

    }, [problem.id, pageState?.currentPage,refreshKey]); // 注意：只监听 currentPage，避免无限循环

    useEffect(()=>{
        if(pageState){
            setTotalPages(Math.ceil(pageState.totalItems / pageState.actualPageSize))
        }
    },[pageState?.totalItems,pageState?.actualPageSize])

    useEffect(() => {   
        if (fetcher.state == "idle") {
            const data = fetcher.data;
            if (data) {
                setSubmissions(data.data);
                setPageState({
                    currentPage: data.currentPage,
                    totalItems: data.totalItems,
                    actualPageSize: data.actualPageSize,
                
                });
                setSubmissionsLoading(false);
            }
            return;
        }
        if (fetcher.state == "loading" || fetcher.state == "submitting") {

        }
    }, [fetcher.state])

    const handlePageChange = (_: React.ChangeEvent<unknown>, page: number) => {
        setPageState((prev) => prev ? { ...prev, currentPage: page } : undefined);
    };
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
                                }, {
                                    onSuccess: () => {
                                        setRefreshKey(prev => prev + 1);
                                        // ✅ 提交成功，刷新提交记录（回到第一页）
                                        setPageState((prev) => prev ? { ...prev, currentPage: 1 } : undefined);
                                    },
                                    onError: (err) => {
                                        console.error("Submission failed:", err);
                                    },
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
                                <MarkdownRenderer markdownContent={problem.content}/>
                            </TabPanel>
                            <TabPanel index={1} value={t3}>

                                <Typography variant="h4">SUBMISSION</Typography>

                                <Box sx={{ mt: 2 }}>
                                    <Typography variant="h6">提交记录</Typography>
                                    {submissionsLoading ? (
                                        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                                            加载中...
                                        </Typography>
                                    ) : submissions && submissions.length > 0 ? (
                                        <Stack spacing={2} sx={{ mt: 1 }}>
                                            {submissions.map((submission, index) => (
                                                <SubmissionItem submission={submission} reUseCode={loadSubmission} key={index} />
                                            ))}
                                            {/* 添加分页组件 */}
                                            {pageState && totalPages > 1 && ( // 只有当总页数大于1时才显示分页
                                                <Stack spacing={2} sx={{ mt: 3, mb: 2, alignItems: 'center' }}>
                                                    <Pagination
                                                        count={totalPages}
                                                        page={pageState.currentPage}
                                                        onChange={handlePageChange}
                                                        color="primary"
                                                        showFirstButton
                                                        showLastButton
                                                    />
                                                </Stack>
                                            )}
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
                    <Grid size={{ xs: 12, md: 5 }} sx={{ height: { xs: 'auto', md: '100%', overflow: 'hidden', } }}>

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
                            <Card
                                sx={{
                                    flex: 1,
                                    minHeight: '300px',        // 提高最小高度保证可见
                                    maxHeight: '60vh',     // 最大不超过 60% 视口高度
                                    mb: 2,
                                    overflow: 'hidden',      // 启用滚动以处理内容超出
                                }}
                            >
                                <CodeEditor code={code} onChange={setCode} />
                            </Card>

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