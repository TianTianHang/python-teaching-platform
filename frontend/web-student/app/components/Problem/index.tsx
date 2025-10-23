import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Divider } from '@mui/material';
import type { AlgorithmProblem, Problem } from '~/types/course';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import AlgorithmProblemDetail from './AlgorithmProblemDetail'

// Define a type for the props of the ProblemRenderer component
interface ProblemRendererProps {
    problem: Problem;
}

const ProblemRenderer: React.FC<ProblemRendererProps> = ({ problem }) => {
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
        <Card raised sx={{ maxWidth: 800, margin: '20px auto', p: 2 }}>
            <CardContent>
                <Typography variant="h4" component="h1" gutterBottom>
                    {problem.title}
                </Typography>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <Chip label={problem.type.charAt(0).toUpperCase() + problem.type.slice(1)} color="primary" size="small" />
                    <Chip label={`Difficulty: ${problem.difficulty}`} color="secondary" size="small" />
                    {problem.chapter_title && (
                        <Chip label={`Chapter: ${problem.chapter_title}`} variant="outlined" size="small" />
                    )}
                </Box>

                <Typography variant="body2" color="text.secondary" gutterBottom>
                    Created: {new Date(problem.created_at).toLocaleDateString()} | Last Updated: {new Date(problem.updated_at).toLocaleDateString()}
                </Typography>

                <Divider sx={{ my: 2 }} />

                <Box sx={markdownStyle}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                        {problem.content}
                    </ReactMarkdown>
                </Box>
            </CardContent>
        </Card>
    );
};

export const renderProblemDetails = (problem: Problem) => {
    switch (problem.type) {
        case 'algorithm':
            const algorithmProblem = problem as AlgorithmProblem;
            return (
                <AlgorithmProblemDetail algorithmProblem={algorithmProblem} />
            );
        // Add more cases here for future problem types
        // case 'anotherType':
        //   const anotherProblem = problem as AnotherProblem;
        //   return (
        //     <Box sx={{ mt: 2 }}>
        //       <Typography variant="body2">
        //         Specific detail for another type: {anotherProblem.someProperty}
        //       </Typography>
        //     </Box>
        //   );
        default:
            return (
                <Typography variant="body2" color="error" sx={{ mt: 2 }}>
                    Unknown problem type: {problem.type}
                </Typography>
            );
    }
};

export default ProblemRenderer;
