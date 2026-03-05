import { redirect } from "react-router";
import type { Route } from "./+types/problems.$problemId.save_draft";
import { clientHttp } from "~/utils/http/client";
import type { SaveType } from "~/types/codeDraft";

export async function clientAction({ request, params }: Route.ClientActionArgs) {
    try {
        const body = await request.json();
        const problemId = params.problemId;
        const { code, language = 'python', save_type = 'manual_save' } = body;

        const result = await clientHttp.post(`/drafts/save_draft/`, {
            problem_id: parseInt(problemId),
            code,
            language,
            save_type: save_type as SaveType
        });

        return result;
    } catch (error: any) {
        if (error.response?.status === 401) {
            throw redirect('/auth/login');
        }
        throw error;
    }
}