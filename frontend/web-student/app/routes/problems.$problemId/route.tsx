import type { AlgorithmProblem, ChoiceProblem, FillBlankProblem, Problem } from '~/types/course';
import AlgorithmProblemPage from './AlgorithmProblemPage';
import ChoiceProblemPage from './ChoiceProblemPage';
import FillBlankProblemPage from './FillBlankProblemPage';
import { clientHttp } from '~/utils/http/client';
import { useNavigate, useParams, useSearchParams } from 'react-router';
import { Box, Typography, Button, CircularProgress } from '@mui/material';
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import { useState, useEffect } from 'react';

export default function ProblemPage() {
  const { problemId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [problem, setProblem] = useState<Problem | { status: number; message: string } | null>(null);
  const [hasNext, setHasNext] = useState(true);

  const next_type = searchParams.get('type');
  const next_id = searchParams.get('id');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
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
        setProblem(result.problem);
        setHasNext(result.has_next);
      } catch (e: any) {
        setProblem({
          status: e.response?.status || 500,
          message: e.message || '无法加载题目',
        });
        setHasNext(false);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [problemId, next_type, next_id]);

  if (loading) {
    return (
      <Box p={4} display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  const rawProblem = problem;
  const isError = rawProblem && 'message' in rawProblem;
  const resolvedProblem = isError ? null : rawProblem as Problem | null;
  const errorMessage = isError && rawProblem ? (rawProblem as { status: number; message: string }).message : null;
  const title = resolvedProblem?.title || "题目详情";

  if (!resolvedProblem) {
    return (
      <Box p={4}>
        <title>{formatTitle(PAGE_TITLES.problem("题目加载失败"))}</title>
        <Typography variant="h6" color="error">
          {errorMessage || '题目加载失败，请重试。'}
        </Typography>
        <Box mt={2}>
          <Button variant="outlined" onClick={() => navigate(-1)}>
            返回
          </Button>
        </Box>
      </Box>
    );
  }

  const next = () => {
    navigate(`/problems/next?type=${resolvedProblem.type}&id=${resolvedProblem.id}`);
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
      <ChoiceProblemPage problem={resolvedProblem as ChoiceProblem} onNext={next} hasNext={hasNext} />;
    </>;
  }

  if (resolvedProblem.type === 'fillblank') {
    return <>
      <title>{formatTitle(PAGE_TITLES.problem(title))}</title>
      <FillBlankProblemPage problem={resolvedProblem as FillBlankProblem} onNext={next} hasNext={hasNext} />;
    </>;
  }

  return <>
    <title>{formatTitle(PAGE_TITLES.problem(title))}</title>
    <div>未知题型</div>
  </>;
}