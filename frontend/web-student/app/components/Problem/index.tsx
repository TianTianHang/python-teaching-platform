import React from 'react';
import { Card, CardContent, Typography, Box, Chip, Divider, CardActionArea } from '@mui/material';
import type { Problem } from '~/types/course';

import { useNavigate, useParams } from 'react-router';
import ProblemStatusChip from './ProblemStatusChip';
import MarkdownRenderer from '../MarkdownRenderer';

// Define a type for the props of the ProblemRenderer component
interface ProblemRendererProps {
    problem: Problem;
}

const ProblemRenderer: React.FC<ProblemRendererProps> = ({ problem }) => {
    const navigate = useNavigate()
    const params = useParams()
    return (
        <Card raised sx={{ maxWidth: 800, margin: '20px auto', p: 2 }}>
            <CardActionArea onClick={() => { navigate(`/${params.lang}/problems/${problem.id}`) }}>
                <CardContent>

                    <Typography variant="h4" component="h1" gutterBottom>
                        {problem.title}
                    </Typography>



                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                        <ProblemStatusChip status={problem.status} />
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
                     <MarkdownRenderer markdownContent={problem.content}/>

                </CardContent>
            </CardActionArea>
        </Card>
    );
};

export default ProblemRenderer;
