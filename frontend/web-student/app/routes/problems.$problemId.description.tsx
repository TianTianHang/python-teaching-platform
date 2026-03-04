import { Typography, Divider, Box, CircularProgress } from "@mui/material";
import MarkdownRenderer from "~/components/MarkdownRenderer";
import { useParams } from "react-router";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import { clientHttp } from "~/utils/http/client";
import type { Problem } from "~/types/course";
import { useState, useEffect } from "react";

export default function ProblemDescription() {
    const { problemId } = useParams();
    const [loading, setLoading] = useState(true);
    const [problem, setProblem] = useState<Problem | null>(null);
    
    useEffect(() => {
        const fetchData = async () => {
            try {
                const data = await clientHttp.get<Problem>(`/problems/${problemId}`);
                setProblem(data);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [problemId]);
    
    if (loading) {
        return (
            <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }
    
    if (!problem) {
        return <Typography color="error">无法加载题目</Typography>;
    }
    
    return (
        <>
            <title>{formatTitle(PAGE_TITLES.problem(problem.title))}</title>
            <Typography variant="h4">{`${problem.id}. ${problem.title}`}</Typography>
            <Divider sx={{ my: 2 }} />
            <Typography variant="h5" gutterBottom>题目描述</Typography>
            <MarkdownRenderer markdownContent={problem.content} />
        </>
    );
}