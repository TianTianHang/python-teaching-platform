
import type { Route } from "./+types/submission";
import createHttp, { createResponse } from "~/utils/http/index.server";
import type { Submission, SubmissionFreelyRes, SubmissionRes } from "~/types/submission";
import type { Page } from "~/types/page";
export interface SubmissionReq {
    code: string;
    language: string;
    problem_id?: number;
}
export async function action({
    request
}: Route.ActionArgs) {
    const formData = await request.formData();
    const code = String(formData.get("code"));
    const language = String(formData.get("language"));
    const problem_id = Number(formData.get("problem_id"));
    try {
        const http = createHttp(request);
        const result = await http.post<SubmissionFreelyRes | SubmissionRes>(
            "/submissions/",
            { code, language, problem_id }
        );
        return createResponse(request,result);
    } catch (error) {
        return { error: (error as any).message };
    }
}

export async function loader({
    request
}: Route.LoaderArgs) {
    const url = new URL(request.url);
    const id = url.searchParams.get("id") ?? "1";
    try {
        const http = createHttp(request);
        const data = await http.get<Page<Submission>>(`/problems/${id}/submissions`);
        return createResponse(request,data);
    } catch (error) {
        return { error: (error as any).message };
    }
}
