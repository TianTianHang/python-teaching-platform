import { Box, AppBar, Toolbar, Grid, Paper, Typography, Button, Card, CardContent, Tabs, Tab, Alert, Stack, IconButton, ButtonGroup, CardActions, CardHeader, Accordion, AccordionSummary, AccordionDetails } from "@mui/material";
import { useState } from "react";
import { Outlet, useNavigate } from "react-router";
import CodeEditor from "~/components/CodeEditor";
import SubmissionOutputViewer from "~/components/SubmissionOutputViewer";
import { a11yProps, TabPanel } from "~/components/TabUtils";
import useSubmission from "~/hooks/useSubmission";
import type { AlgorithmProblem, TestCase } from "~/types/course";
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import HistoryIcon from '@mui/icons-material/History';
import DescriptionIcon from '@mui/icons-material/Description';
import CodeIcon from '@mui/icons-material/Code';
import { useMount, useUpdateEffect } from 'ahooks';
import { CaseDetail } from "~/components/Problem/CaseDetail";
import ForumIcon from '@mui/icons-material/Forum';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
export default function AlgorithmProblemPage({ problem }: { problem: AlgorithmProblem }) {


    const [t1, setT1] = useState(0);
    const onTab1Change = (_: React.SyntheticEvent, newValue: number) => {
        setT1(newValue);
    };

    const [t2, setT2] = useState(0);
    const onTab2Change = (_: React.SyntheticEvent, newValue: number) => {
        setT2(newValue);
    };
    const [code, setCode] = useState<string>(problem.code_template.python);
    const { output, isLoading, error, executeCode } = useSubmission();
    useUpdateEffect(() => {
        if (!isLoading) {
            setT3("submissions")
            navigate("submissions")
        }
    }, [isLoading]);
    useMount(() => {
        navigate("description", { replace: true });
    })
    const navigate = useNavigate();
    const [t3, setT3] = useState("description");
    const onTab3Change = (event: React.SyntheticEvent, value: string) => {
        setT3(value)
        if (value === 'description') {
            navigate('description', { replace: true });
        } else if (value === 'submissions') {
            navigate('submissions', { replace: true });
        }
    };
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
                                        setT1(1)
                                    },
                                    onError: (err) => {
                                        setT1(1)
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
                        <Card elevation={3} sx={{ p: 3, height: '100%', overflow: 'auto' }}>
                            <Box sx={{ flex: '0 0 auto', height: '100vh' }}>
                                <CardActions>
                                    <Tabs
                                        value={t3} // 不自动选中任何 tab，因为是导航用途
                                        onChange={onTab3Change}
                                        textColor="primary"
                                        indicatorColor="primary"
                                        variant="fullWidth"
                                        sx={{ minHeight: 40 }}
                                    >
                                        <Tab
                                            value="description"
                                            label="题目描述"
                                            icon={<DescriptionIcon />}
                                            iconPosition="start"
                                            sx={{ textTransform: 'none', minHeight: 40 }}
                                        />
                                        <Tab
                                            value="submissions"
                                            label="提交记录"
                                            icon={<HistoryIcon />}
                                            iconPosition="start"
                                            sx={{ textTransform: 'none', minHeight: 40 }}
                                        />
                                    </Tabs>
                                </CardActions>
                                <CardContent>
                                    <Outlet />
                                </CardContent>
                            </Box>
                            {/* 下半部分：评论 Accordion 列表 */}
                            <Box sx={{ flex: 1, overflow: 'auto', p: 2, pt: 1, borderTop: 1, borderColor: 'divider' }}>
                                <Accordion>
                                    <AccordionSummary
                                        expandIcon={<ArrowDropDownIcon />}
                                    >
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                            <ForumIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                            <Typography variant="subtitle1" sx={{ color: 'text.secondary', fontWeight: 'medium' }}>
                                                评论
                                            </Typography>
                                        </Box>
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        
                                    </AccordionDetails>
                                </Accordion>
                            </Box>
                        </Card>
                    </Grid>

                    {/* 右侧：编辑器 + 测试 */}
                    <Grid size={{ xs: 12, md: 5 }} sx={{ height: { xs: 'auto', md: '100%', } }}>

                        <Card
                            elevation={3}
                            sx={{
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                            }}
                        >
                            {/* 代码编辑器区域 */}
                            <Box sx={{ p: 3, pb: 2 }}>
                                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                    <CodeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                    <Typography variant="subtitle1" sx={{ color: 'text.secondary', fontWeight: 'medium' }}>
                                        代码
                                    </Typography>
                                </Box>
                                <Box
                                    sx={{
                                        height: { xs: '250px', sm: '300px', md: '280px' },
                                        maxHeight: '60vh',
                                        minHeight: '250px',
                                        borderRadius: 1,
                                        overflow: 'hidden',
                                        border: '1px solid',
                                        borderColor: 'divider',
                                    }}
                                >
                                    <CodeEditor code={code} onChange={setCode} />
                                </Box>
                            </Box>

                            {/* 测试结果区域 */}
                            <Box sx={{ p: 3, pt: 1, borderTop: 1, borderColor: 'divider', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                <Typography variant="subtitle1" sx={{ color: 'text.secondary', fontWeight: 'medium', mb: 2 }}>
                                    测试结果
                                </Typography>
                                <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                                    <Tabs value={t1} onChange={onTab1Change} sx={{ mb: 2 }}>
                                        <Tab label="测试用例" {...a11yProps(0)} />
                                        <Tab label="Output" {...a11yProps(1)} />
                                    </Tabs>

                                    <Box sx={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
                                        <TabPanel index={0} value={t1} sx={{ p: 0 }}>
                                            <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
                                                <Tabs value={t2} onChange={onTab2Change} variant="scrollable">
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
                                                    <TabPanel key={index} index={index} value={t2} sx={{ p: 0, pt: 1 }}>
                                                        <CaseDetail testcase={tc} />
                                                    </TabPanel>
                                                ))}
                                        </TabPanel>

                                        <TabPanel index={1} value={t1} sx={{ p: 0 }}>
                                            {error ? (
                                                <Alert severity="error">{error}</Alert>
                                            ) : (
                                                <SubmissionOutputViewer output={output} isLoading={isLoading} />
                                            )}
                                        </TabPanel>
                                    </Box>
                                </Box>
                            </Box>
                        </Card>
                    </Grid>
                </Grid>
            </Box>
        </Box>
    );
}