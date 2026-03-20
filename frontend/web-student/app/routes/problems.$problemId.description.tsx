import { Typography, Divider, Box, CircularProgress } from "@mui/material";
import MarkdownRenderer from "~/components/MarkdownRenderer";
import { useLoaderData } from "react-router";
import { redirect } from "react-router";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import { clientHttp } from "~/utils/http/client";
import type { Problem } from "~/types/course";
import type { Route } from "./+types/problems.$problemId.description";
import { isApiError } from "~/utils/typeGuards";

export async function clientLoader({ params }: Route.ClientLoaderArgs) {
    const { problemId } = params;
    try {
        const data = await clientHttp.get<Problem>(`/problems/${problemId}`);
        return data;
    } catch (error: unknown) {
        if (isApiError(error) && error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        const message = error instanceof Error ? error.message : '无法加载题目';
        const status = isApiError(error) ? error.response?.status || 500 : 500;
        throw new Response(JSON.stringify({ message }), {
            status,
            statusText: message
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