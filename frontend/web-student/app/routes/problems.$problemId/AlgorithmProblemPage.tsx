import { Box, AppBar, Toolbar, Typography, Card, CardContent, Tabs, Tab, Alert, IconButton, ButtonGroup, CardActions, Accordion, AccordionSummary, AccordionDetails } from "@mui/material";
import { PageContainer, SectionContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";
import { useState } from "react";
import { Outlet, useNavigate } from "react-router";
import CodeEditor from "~/components/CodeEditor";
import SubmissionOutputViewer from "~/components/SubmissionOutputViewer";
import { a11yProps, TabPanel } from "~/components/TabUtils";
import useSubmission from "~/hooks/useSubmission";
import { useCodeDraft } from "~/hooks/useCodeDraft";
import { useEditorLayout } from "~/hooks/useEditorLayout";
import type { AlgorithmProblem } from "~/types/course";
import ArrowBackIosIcon from '@mui/icons-material/ArrowBackIos';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import HistoryIcon from '@mui/icons-material/History';
import DescriptionIcon from '@mui/icons-material/Description';
import CodeIcon from '@mui/icons-material/Code';
import SaveIcon from '@mui/icons-material/Save';
import { useMount, useUpdateEffect } from 'ahooks';
import { CaseDetail } from "~/components/Problem/CaseDetail";
import ForumIcon from '@mui/icons-material/Forum';
import ArrowDropDownIcon from '@mui/icons-material/ArrowDropDown';
import DiscussionForum from "~/components/Thread/DiscussionForum";
import SaveStatusIndicator from '~/components/SaveStatusIndicator';
import { Group, Panel, Separator } from 'react-resizable-panels';
import "~/routes/problems.$problemId/AlgorithmProblemPage.module.css";
export default function AlgorithmProblemPage({ problem }: { problem: AlgorithmProblem }) {
    // console.log(problem.recent_threads)
    const [t1, setT1] = useState(0);
    const onTab1Change = (_: React.SyntheticEvent, newValue: number) => {
        setT1(newValue);
    };

    const [t2, setT2] = useState(0);
    const onTab2Change = (_: React.SyntheticEvent, newValue: number) => {
        setT2(newValue);
    };

    // Code draft with enhanced save tracking
    const { code, setCode, saveDraft, isLoading: isDraftSaving, lastSavedAt, saveType } = useCodeDraft({
        problemId: Number(problem.id),
        initialCode: problem.code_template.python,
        language: 'python'
    });

    // Editor layout management
    const { layout } = useEditorLayout();

    const navigate = useNavigate();
    const [t3, setT3] = useState("description");
    const onTab3Change = (_: React.SyntheticEvent, value: string) => {
        setT3(value)
        if (value === 'description') {
            navigate('description', { replace: true });
        } else if (value === 'submissions') {
            navigate('submissions', { replace: true });
        }
    };

    // 包装 saveDraft 函数以匹配 useSubmission 的期望类型
    const saveDraftForSubmission = (codeToSave: string) => saveDraft('submission');
    const { output, isLoading, error, executeCode } = useSubmission();

    // useUpdateEffect(() => {
    //     if (!isLoading && t3 === "description") {
    //         setT3("submissions")
    //         navigate("submissions")
    //     }
    // }, [isLoading, t3]);

    useMount(() => {
        navigate("description", { replace: true });
    });

    // Handle manual save from SaveStatusIndicator
    const handleManualSave = () => {
        saveDraft('manual_save');
    };

    return (
        <PageContainer sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }} maxWidth={false}>
            {/* Enhanced AppBar with SaveStatusIndicator */}
            <AppBar position="static">
                <Toolbar>
                    {/* Back button */}
                    <IconButton
                        onClick={() => navigate(-1)}
                        size="large"
                        edge="start"
                        color="inherit"
                        aria-label="menu"
                        sx={{ mr: 2 }}
                    >
                        <ArrowBackIosIcon />
                    </IconButton>

                    {/* Title */}
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        算法题
                    </Typography>

                    {/* Save status indicator */}
                    <SaveStatusIndicator
                        lastSavedAt={lastSavedAt}
                        saveType={saveType}
                        isLoading={isDraftSaving}
                        onManualSave={handleManualSave}
                    />

                    {/* Save button with enhanced animation classes */}
                    <IconButton
                        size="large"
                        color="inherit"
                        edge="start"
                        loading={isDraftSaving}
                        onClick={() => saveDraft('manual_save')}
                        title="Save code"
                        className={isDraftSaving ? 'saveButton saving' : 'saveButton'}
                    >
                        <SaveIcon />
                    </IconButton>

                    {/* Run button */}
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
                                    setT1(1);
                                },
                                onError: (err) => {
                                    setT1(1);
                                    console.error("Submission failed:", err);
                                },
                                onSaveDraft: saveDraftForSubmission
                            })
                        }
                        title="Run code"
                    >
                        <PlayArrowIcon />
                    </IconButton>

                    {/* Right padding to match back button */}
                    <Box sx={{ width: 100 }} />
                </Toolbar>
            </AppBar>

            {/* Main content area - using Group for resizable layout */}
            <Box sx={{ flex: 1, overflow: 'hidden' }}>
                <Group
                    orientation="horizontal"
                    className="panel-group"
                >
                    {/* Left: Problem description panel */}
                    <Panel
                        defaultSize={`${layout.horizontalSplit}%`}
                        minSize={"20%"}
                        maxSize={"80%"}
                        className="panel"
                    >
                        <SectionContainer
                            spacing="md"
                            variant="card"
                            sx={{
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                overflow: 'auto',
                            }}
                            disableTopSpacing
                        >
                            <Box sx={{ flex: '0 0 auto'}}>
                                <CardActions>
                                    <Tabs
                                        value={t3} // Not auto-selecting any tab for navigation
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
                            {/* Comments accordion */}
                            <Box sx={{ flex: 1, p: 2, pt: 1, borderTop: 1, borderColor: 'divider' }}>
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
                                        <DiscussionForum threads={problem.recent_threads} problemId={problem.id} />
                                    </AccordionDetails>
                                </Accordion>
                            </Box>
                        </SectionContainer>
                    </Panel>

                    {/* Horizontal resize handle */}
                    <Separator className="horizontalResizeHandle" />

                    {/* Right: Editor + Test results (vertical split) */}
                    <Panel minSize={"40%"}>
                        <Group orientation="vertical">
                            {/* Code editor panel */}
                            <Panel
                                defaultSize={`${layout.editorSize}%`}
                                minSize={"30%"}
                                maxSize={"70%"}
                                className="panel"
                            >
                                <SectionContainer
                                    spacing="md"
                                    variant="card"
                                    sx={{
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                    }}
                                    disableTopSpacing
                                >
                                    <Box sx={{ p: spacing.lg, pb: spacing.md,height: '100%'}}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', mb: spacing.md }}>
                                            <CodeIcon fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />
                                            <Typography variant="subtitle1" sx={{ color: 'text.secondary', fontWeight: 'medium' }}>
                                                代码
                                            </Typography>
                                        </Box>
                                        <Box sx={{ borderRadius: 1, overflow: 'hidden', border: '1px solid', borderColor: 'divider' }}>
                                            <CodeEditor code={code} onChange={setCode} />
                                        </Box>
                                    </Box>
                                </SectionContainer>
                            </Panel>

                            {/* Vertical resize handle */}
                            <Separator className="verticalResizeHandle" style={{height:"6px"}}/>

                            {/* Test results panel */}
                            <Panel minSize={"30%"} className="panel">
                                <SectionContainer
                                    spacing="md"
                                    variant="card"
                                    sx={{
                                        height: '100%',
                                        display: 'flex',
                                        flexDirection: 'column',
                                        overflow:"auto"
                                    }}
                                    disableTopSpacing
                                >
                                    <Box sx={{ p: spacing.lg, pt: spacing.sm, borderTop: 1, borderColor: 'divider', flex: 1, display: 'flex', flexDirection: 'column' }}>
                                        <Typography variant="subtitle1" color="text.secondary" sx={{ fontWeight: 'medium', mb: spacing.md }}>
                                            测试结果
                                        </Typography>
                                        <Box sx={{ flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                                            <Tabs value={t1} onChange={onTab1Change} sx={{ mb: spacing.md }}>
                                                <Tab label="测试用例" {...a11yProps(0)} />
                                                <Tab label="Output" {...a11yProps(1)} />
                                            </Tabs>

                                            <Box sx={{ flex: 1, minHeight: 0, overflow: 'auto' }}>
                                                <TabPanel index={0} value={t1} sx={{ p: 0 }}>
                                                    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: spacing.md }}>
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
                                                            <TabPanel key={index} index={index} value={t2} sx={{ p: 0, pt: spacing.sm }}>
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
                                </SectionContainer>
                            </Panel>
                        </Group>
                    </Panel>
                </Group>
            </Box>
        </PageContainer>
    );
}