import { Box, Typography, Container, Paper, List, ListItem } from '@mui/material';
import type { Chapter, ChoiceProblem, Problem } from '~/types/course'; // 确保路径正确
import { formatDateTime } from '~/utils/time';
import type { Route } from "./+types/route"
import http from '~/utils/http';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ProblemRenderer from '~/components/Problem'; // 确保 ProblemRenderer 的导入路径正确
import type { Page } from '~/types/page';
import ChoiceProblemPage from '~/routes/$lang.problems.$problemId/ChoiceProblemPage';
import ChoiceProblemCmp from '~/components/Problem/ChoiceProblemCmp';
export function meta({ loaderData }: Route.MetaArgs) {
    return [
        { title: loaderData?.chapter.title || "Error" },
    ];
}
export async function clientLoader({ params }: Route.ClientLoaderArgs) {
    const chapter = await http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
    const problems = await http.get<Page<Problem>>(`/courses/${params.courseId}/chapters/${params.chapterId}/problems`)
    return { chapter, problems };
}

export default function ChapterDetail({ loaderData }: Route.ComponentProps) {

    const { chapter, problems } = loaderData;
    const markdownStyle = {
        // 可选：添加一些基本样式，以便更好地显示 Markdown 内容
        '& h1, & h2, & h3, & h4, & h5, & h6': {
            mt: 3,
            mb: 1,
        },
        '& p': {
            mb: 2,
        },
        '& ul, & ol': {
            ml: 4,
            mb: 2,
        },
        '& a': {
            color: 'primary.main',
            textDecoration: 'none',
            '&:hover': {
                textDecoration: 'underline',
            }
        },
        '& code': {
            backgroundColor: '#f2f2f2', // 浅灰色背景
            padding: '2px 4px',
            borderRadius: '4px',
            fontFamily: 'monospace',
        },
        // 代码块样式
        '& pre': {
            backgroundColor: '#2d2d2d', // 深色背景
            color: '#f8f8f2', // 文本颜色
            padding: '16px',
            borderRadius: '8px',
            overflowX: 'auto',
            margin: '24px 0',
        },
        '& pre code': {
            backgroundColor: 'transparent', // 代码块内部的代码背景透明
            padding: 0,
            borderRadius: 0,
            whiteSpace: 'pre-wrap', // 允许代码换行
            wordBreak: 'break-word',
        }
    };
    return (
        <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
            <Paper elevation={3} sx={{ p: 4 }}>
                <Typography variant="h4" component="h1" gutterBottom>
                    {chapter.title}
                </Typography>
                <Typography variant="h6" color="text.secondary" gutterBottom>
                    课程: {chapter.course_title}
                </Typography>
                {/* 使用 ReactMarkdown 渲染 chapter.content */}
                <Box sx={markdownStyle}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {chapter.content}
                    </ReactMarkdown>
                </Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 4 }}>
                    <Typography variant="caption" color="text.disabled">
                        创建于: {formatDateTime(chapter.created_at)}
                    </Typography>
                    <Typography variant="caption" color="text.disabled">
                        最后更新: {formatDateTime(chapter.updated_at)}
                    </Typography>
                </Box>
            </Paper>

            {/* 这里渲染题目列表，不使用 ProblemListRenderer */}
            <Box sx={{ mt: 4 }}>
                <Typography variant="h5" component="h2" gutterBottom sx={{ mb: 2 }}>
                    相关题目
                </Typography>
                {problems && problems.results.length > 0 ? (
                    <Box> {/* 使用 Box 而不是 List 来包含多个 ProblemRenderer */}
                        {problems.results.map((problem) => {
                            if (problem.type == 'choice') {
                                return (
                                    <ChoiceProblemCmp problem={problem as ChoiceProblem} />
                                )
                            } else {
                                return (
                                    <Box key={problem.id} sx={{ mb: 3 }}> {/* 为每个 ProblemRenderer 添加一个外层 Box 并设置底部边距 */}
                                        <ProblemRenderer problem={problem} />
                                    </Box>
                                )
                            }
                        })}
                    </Box>
                ) : (
                    <Paper elevation={1} sx={{ p: 2, textAlign: 'center' }}>
                        <Typography variant="body1" color="text.secondary">
                            本章节暂无相关题目。
                        </Typography>
                    </Paper>
                )}
            </Box>
        </Container>
    );
}
