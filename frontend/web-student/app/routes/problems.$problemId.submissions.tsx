import { Typography, Stack, Pagination, Box, CircularProgress } from "@mui/material";
import { useNavigate, useParams, useSearchParams, useLoaderData } from "react-router";
import { redirect } from "react-router";
import SubmissionItem from "~/components/SubmissionTtem";
import type { Submission } from "~/types/submission";
import type { Problem } from "~/types/course";
import { clientHttp } from "~/utils/http/client";
import type { Page } from "~/types/page";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import type { Route } from "./+types/problems.$problemId.submissions";

export async function clientLoader({ params, request }: Route.ClientLoaderArgs) {
    const { problemId } = params;
    const url = new URL(request.url);
    const page = url.searchParams.get("page") || "1";
    const pageSize = url.searchParams.get("page_size") || "10";
    
    try {
        const [submissionsData, problemData] = await Promise.all([
            clientHttp.get<Page<Submission>>(`/problems/${problemId}/submissions/?page=${page}&page_size=${pageSize}`),
            clientHttp.get<Problem>(`/problems/${problemId}`)
        ]);
        return { submissions: submissionsData, problem: problemData };
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw new Response(JSON.stringify({ message: error.message || '请求失败' }), {
            status: error.response?.status || 500,
            statusText: error.message || '请求失败'
        });
    }
}
clientLoader.hydrate = true as const;


export function HydrateFallback() {
    return (
        <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
        </Box>
    );
}

export function ErrorBoundary({ error }: { error: Error }) {
    return (
        <Box p={4}>
            <Typography color="error" variant="h6" gutterBottom>
                {error.message || '无法加载提交记录'}
            </Typography>
        </Box>
    );
}

export default function ProblemSubmissions() {
    const { problemId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const loaderData = useLoaderData<typeof clientLoader>();
    
    const submissions = loaderData.submissions.results;
    const totalItems = loaderData.submissions.count ?? 0;
    const actualPageSize = loaderData.submissions.page_size || 10;
    const problem = loaderData.problem;
    
    const page = parseInt(searchParams.get("page") || "1", 10);
    const totalPages = Math.ceil(totalItems / actualPageSize);

    const handlePageChange = (_event: React.ChangeEvent<unknown>, value: number) => {
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("page", value.toString());
        newSearchParams.set("page_size", actualPageSize.toString());
        navigate(`/problems/${problemId}/submissions?${newSearchParams.toString()}`);
    };

    return (
        <>
            <title>{formatTitle(PAGE_TITLES.problem(problem.title))}</title>
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