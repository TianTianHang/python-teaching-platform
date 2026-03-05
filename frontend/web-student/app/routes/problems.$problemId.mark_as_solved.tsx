import { redirect } from "react-router";
import type { Route } from "./+types/problems.$problemId.mark_as_solved";
import type { ProblemProgress } from "~/types/course";
import { clientHttp } from "~/utils/http/client";


export async function clientAction({ request, params }: Route.ClientActionArgs) {
    try {
        const formData = await request.formData();
        const solvedStr = formData.get('solved');
        const solved = solvedStr === null ? true : solvedStr === 'true';
        const result = await clientHttp.post<ProblemProgress>(`/problems/${params.problemId}/mark_as_solved/`, { solved });
        return result;
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw error;
    }
}
