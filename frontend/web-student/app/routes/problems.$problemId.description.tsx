import { Typography, Divider, Box, CircularProgress } from "@mui/material";
import MarkdownRenderer from "~/components/MarkdownRenderer";
import { useLoaderData } from "react-router";
import { redirect } from "react-router";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import { clientHttp } from "~/utils/http/client";
import type { Problem } from "~/types/course";
import type { Route } from "./+types/problems.$problemId.description";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
    const { problemId } = params;
    try {
        const data = await clientHttp.get<Problem>(`/problems/${problemId}`);
        return data;
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw new Response(JSON.stringify({ message: error.message || '无法加载题目' }), {
            status: error.response?.status || 500,
            statusText: error.message || '无法加载题目'
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
                {error.message || '无法加载题目'}
            </Typography>
        </Box>
    );
}

export default function ProblemDescription() {
    const problem = useLoaderData<typeof clientLoader>();
    
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