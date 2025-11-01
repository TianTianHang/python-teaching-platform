
import type { AlgorithmProblem, ChoiceProblem, Problem } from '~/types/course';
import AlgorithmProblemPage from './AlgorithmProblemPage';
import ChoiceProblemPage from './ChoiceProblemPage';
import type { Route } from './+types/route';
import createHttp from '~/utils/http/index.server';
import { withAuth } from '~/utils/loaderWrapper';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.title||"" },
  ];
}

export const loader = withAuth(async ({ params, request }) => {
  const http = createHttp(request);

  const problem = await http.get<Problem>(`/problems/${params.problemId}`);
  
  if (problem.type === "algorithm") {
    // 可以在这里补充 submissions 逻辑
    // const submissions = await http.get<Page<Submission>>(`/problems/${params.problemId}/submissions`);
  }

  return problem;
});

export default function ProblemPage({ loaderData, params }: Route.ComponentProps) {
  const problem = loaderData;
  
  if (problem.type === 'algorithm') {
    return <AlgorithmProblemPage problem={problem as AlgorithmProblem} />;
  }

  if (problem.type === 'choice') {
    return <ChoiceProblemPage problem={problem as ChoiceProblem} />;
  }

  return <div>未知题型</div>;

}