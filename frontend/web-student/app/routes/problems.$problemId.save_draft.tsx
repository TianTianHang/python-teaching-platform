import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/problems.$problemId.save_draft";
import { withAuth } from "~/utils/loaderWrapper";
import type { SaveType } from "~/types/codeDraft";

export const action = withAuth(async ({ request, params }: Route.ActionArgs) => {
    const http = createHttp(request);
    const body = await request.json();
    const problemId = params.problemId;
    const { code, language = 'python', save_type = 'manual_save' } = body;

    const result = await http.post(`/drafts/save_draft/`, {
        problem_id: parseInt(problemId),
        code,
        language,
        save_type: save_type as SaveType
    });

    return result;
})