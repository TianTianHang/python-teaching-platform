import type { AlgorithmProblem, ChoiceProblem, FillBlankProblem, Problem } from '~/types/course';
import AlgorithmProblemPage from './AlgorithmProblemPage';
import ChoiceProblemPage from './ChoiceProblemPage';
import FillBlankProblemPage from './FillBlankProblemPage';
import { clientHttp } from '~/utils/http/client';
import { useNavigate, useParams, useSearchParams, useLoaderData } from 'react-router';
import { redirect } from 'react-router';
import { Box, Typography, Button, CircularProgress } from '@mui/material';
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import type { Route } from "./+types/route";

export async function clientLoader({ params, request }: Route.ClientLoaderArgs) {
    const { problemId } = params;
    const url = new URL(request.url);
    const next_type = url.searchParams.get('type');
    const next_id = url.searchParams.get('id');

    try {
        let result: { problem: Problem; has_next: boolean };
        if (next_id && next_type) {
            const search = new URLSearchParams();
            search.append('type', next_type);
            search.append('id', next_id);
            result = await clientHttp.get<{ problem: Problem; has_next: boolean }>(`/problems/next/?${search.toString()}`);
        } else {
            const data = await clientHttp.get<Problem>(`/problems/${problemId}`);
            result = { problem: data, has_next: false };
        }

        // 尝试获取上一题信息
        try {
            const previousResult = await clientHttp.get<{ problem: Problem; has_previous: boolean }>(`/problems/previous?type=${result.problem.type}&id=${result.problem.id}`);
            return {
                ...result,
                has_previous: previousResult.has_previous
            };
        } catch (error) {
            // 如果获取上一题失败，默认为没有上一题
            return {
                ...result,
                has_previous: false
            };
        }
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

export function shouldRevalidate() {
    return true;
}

export function HydrateFallback() {
    return (
        <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="200px">
            <CircularProgress />
        </Box>
    );
}

export function ErrorBoundary({ error }: { error: Error }) {
    const navigate = useNavigate();
    return (
        <Box p={4}>
            <Typography variant="h6" color="error">
                {error.message || '题目加载失败，请重试。'}
            </Typography>
            <Box mt={2}>
                <Button variant="outlined" onClick={() => navigate(-1)}>
                    返回
                </Button>
            </Box>
        </Box>
    );
}

export default function ProblemPage() {
    const { problemId } = useParams();
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const loaderData = useLoaderData<typeof clientLoader>();

    const resolvedProblem = loaderData.problem;
    const hasNext = loaderData.has_next;
    const hasPrevious = loaderData.has_previous;
    const title = resolvedProblem?.title || "题目详情";

  const next = () => {
    navigate(`/problems/next?type=${resolvedProblem.type}&id=${resolvedProblem.id}`);
  }

  const previous = () => {
    navigate(`/problems/previous?type=${resolvedProblem.type}&id=${resolvedProblem.id}`);
  }

  const backToList = () => {
    navigate('/problems');
  }

  if (resolvedProblem.type === 'algorithm') {
    return <>
      <title>{formatTitle(PAGE_TITLES.problem(title))}</title>
      <AlgorithmProblemPage problem={resolvedProblem as AlgorithmProblem} />;
    </>;
  }

  if (resolvedProblem.type === 'choice') {
    return <>
      <title>{formatTitle(PAGE_TITLES.problem(title))}</title>
      <ChoiceProblemPage
        problem={resolvedProblem as ChoiceProblem}
        onNext={next}
        hasNext={hasNext}
        onPrevious={hasPrevious ? previous : undefined}
        hasPrevious={hasPrevious}
        onBackToList={backToList}
      />;
    </>;
  }

  if (resolvedProblem.type === 'fillblank') {
    return <>
      <title>{formatTitle(PAGE_TITLES.problem(title))}</title>
      <FillBlankProblemPage
        problem={resolvedProblem as FillBlankProblem}
        onNext={next}
        hasNext={hasNext}
        onPrevious={hasPrevious ? previous : undefined}
        hasPrevious={hasPrevious}
        onBackToList={backToList}
      />;
    </>;
  }

  return <>
    <title>{formatTitle(PAGE_TITLES.problem(title))}</title>
    <div>未知题型</div>
  </>;
}