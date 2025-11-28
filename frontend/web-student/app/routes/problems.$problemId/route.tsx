
import type { AlgorithmProblem, ChoiceProblem, Problem } from '~/types/course';
import AlgorithmProblemPage from './AlgorithmProblemPage';
import ChoiceProblemPage from './ChoiceProblemPage';
import type { Route } from './+types/route';
import createHttp from '~/utils/http/index.server';
import { withAuth } from '~/utils/loaderWrapper';
import { useNavigate } from 'react-router';
import { Box, Button, Typography } from '@mui/material';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.problem?.title || "" },
  ];
}

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
  const http = createHttp(request);
  const searchParams = new URL(request.url).searchParams;
  const next_type = searchParams.get('type');
  const next_id = searchParams.get('id');
  let problem: Problem;
  let hasNext = true;
  if (next_id && next_type) {
    const search = new URLSearchParams();
    search.append('type', next_type);
    search.append('id', next_id);
    const result= await http.get<{problem:Problem,has_next:boolean}>(`/problems/next/?${search.toString()}`);
    problem = result.problem;
    hasNext = result.has_next;
  } else {
    problem = await http.get<Problem>(`/problems/${params.problemId}`);
  }
  if (problem.type === "algorithm") {
    // 可以在这里补充 submissions 逻辑
    // const submissions = await http.get<Page<Submission>>(`/problems/${params.problemId}/submissions`);
  }

  return {problem:problem,hasNext:hasNext};
});

export default function ProblemPage({ loaderData, params }: Route.ComponentProps) {
  const navigate = useNavigate();
  //错误处理：当 loader 返回 error 字段时

  const problem = loaderData.problem;
  // if(problem===undefined){
  //   return <Box p={4}>
  //     <Typography variant="h6" color="error">题目加载失败，请重试。</Typography>
  //   </Box>
  // }
  const hasNext = loaderData.hasNext;
  console.log("hasNext",hasNext);
  const next = () => {
    navigate(`/problems/next?type=${problem.type}&id=${problem.id}`);
  }
  if (problem.type === 'algorithm') {
    return <AlgorithmProblemPage problem={problem as AlgorithmProblem} />;
  }

  if (problem.type === 'choice') {
    return <ChoiceProblemPage problem={problem as ChoiceProblem} onNext={next} hasNext={hasNext} />;
  }

  return <div>未知题型</div>;

}