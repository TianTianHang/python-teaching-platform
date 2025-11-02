import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/problems.$problemId.mark_as_solved";
import type { ProblemProgress } from "~/types/course";
import { withAuth } from "~/utils/loaderWrapper";


export const action = withAuth(async ({ request, params }: Route.ActionArgs) => {
    const http = createHttp(request);
    const formData = await request.formData();
    const solvedStr = formData.get('solved');
    const solved = solvedStr === null ? true : solvedStr === 'true';
    const result = await http.post<ProblemProgress>(`/problems/${params.problemId}/mark_as_solved/`, { solved });
    return result;
})
