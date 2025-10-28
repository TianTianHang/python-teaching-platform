import createHttp, { createResponse } from "~/utils/http/index.server";
import type { Route } from "./+types/problems.$problemId.mark_as_solved";
import type { ProblemProgress } from "~/types/course";



export async function action({ request,params }: Route.ActionArgs) {
    try {
        const http = createHttp(request);
        const formData = await request.formData();
        const solvedStr = formData.get('solved');
        const solved = solvedStr === null ? true : solvedStr === 'true';
        const result = await http.post<ProblemProgress>(`/problems/${params.problemId}/mark_as_solved/`,{solved});
        return createResponse(request, result);
    } catch (error) {
        return { error: (error as any).message };
    }
}