import { Box, Typography, Container, Paper } from '@mui/material';
import type { Chapter } from '~/types/course'; // 确保路径正确
import { formatDateTime } from '~/utils/time';
import type { Route } from "./+types/route"
import http from '~/utils/http';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
    const chapter = await http.get<Chapter>(`/courses/${params.courseId}/chapters/${params.chapterId}`);
    return chapter;
}

export default function ChapterDetail({ loaderData }: Route.ComponentProps) {
   
    const chapter = loaderData;
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
            
        </Container>
    );
}
