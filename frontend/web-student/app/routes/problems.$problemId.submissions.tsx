import { Typography, Stack, Pagination, Box, CircularProgress } from "@mui/material";
import { useNavigate, useParams, useSearchParams } from "react-router";
import SubmissionItem from "~/components/SubmissionTtem";
import type { Submission } from "~/types/submission";
import type { Problem } from "~/types/course";
import { clientHttp } from "~/utils/http/client";
import type { Page } from "~/types/page";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import { useState, useEffect } from "react";

export default function ProblemSubmissions() {
    const { problemId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    
    const page = parseInt(searchParams.get("page") || "1", 10);
    const pageSize = parseInt(searchParams.get("page_size") || "10", 10);
    
    const [loading, setLoading] = useState(true);
    const [submissions, setSubmissions] = useState<Submission[]>([]);
    const [totalItems, setTotalItems] = useState(0);
    const [actualPageSize, setActualPageSize] = useState(10);
    const [problem, setProblem] = useState<Problem | null>(null);
    
    const totalPages = Math.ceil(totalItems / actualPageSize);
    
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const [submissionsData, problemData] = await Promise.all([
                    clientHttp.get<Page<Submission>>(`/submissions/?page=${page}&page_size=${pageSize}&problemId=${problemId}&exclude=code`),
                    clientHttp.get<Problem>(`/problems/${problemId}`)
                ]);
                setSubmissions(submissionsData.results);
                setTotalItems(submissionsData.count);
                setActualPageSize(submissionsData.page_size || pageSize);
                setProblem(problemData);
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [problemId, page, pageSize]);

    const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("page", value.toString());
        newSearchParams.set("page_size", actualPageSize.toString());
        navigate(`/problems/${problemId}/submissions?${newSearchParams.toString()}`);
    };

    if (loading) {
        return (
            <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="200px">
                <CircularProgress />
            </Box>
        );
    }

    return (
        <>
            {problem && <title>{formatTitle(PAGE_TITLES.problem(problem.title))}</title>}
            <Box sx={{ mt: 2 }}>
                <Typography variant="h6">提交记录</Typography>
                {submissions && submissions.length > 0 ? (
                    <Stack spacing={2} sx={{ mt: 1 }}>
                        {submissions.map((submission, index) => (
                            <SubmissionItem
                                key={submission.id || index}
                                submission={submission}
                            />
                        ))}
                        {totalPages > 1 && (
                            <Stack spacing={2} sx={{ mt: 3, mb: 2, alignItems: 'center' }}>
                                <Pagination
                                    count={totalPages}
                                    page={page}
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
        </>
    );
}