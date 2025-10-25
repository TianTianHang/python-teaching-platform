
import type { AlgorithmProblem, ChoiceProblem, Problem } from '~/types/course';
import AlgorithmProblemPage from './AlgorithmProblemPage';
import ChoiceProblemPage from './ChoiceProblemPage';
import type { Route } from './+types/route';
import createHttp from '~/utils/http/index.server';

export function meta({ loaderData }: Route.MetaArgs) {
  return [
    { title: loaderData?.title||"" },
  ];
}

export async function loader({ params,request }: Route.LoaderArgs) {
  const http = createHttp(request);
  const problem = await http.get<Problem>(`/problems/${params.problemId}`);
  if(problem.type=="algorithm"){
    //const submisstions = await http.get<Page<Submission>>()
  }
  return problem;
}

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