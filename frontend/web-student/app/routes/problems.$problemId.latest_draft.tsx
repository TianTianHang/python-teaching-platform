import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/problems.$problemId.latest_draft";
import { withAuth } from "~/utils/loaderWrapper";

export const loader = withAuth(async ({ request, params }: Route.LoaderArgs) => {
    const http = createHttp(request);
    const problemId = params.problemId;

    const result = await http.get(`/drafts/latest/`, {
         problem_id: parseInt(problemId) 
    });

    return result;
})