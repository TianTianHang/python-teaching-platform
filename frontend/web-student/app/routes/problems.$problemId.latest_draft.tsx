import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/problems.$problemId.latest_draft";
import { withAuth } from "~/utils/loaderWrapper";
import { AxiosError } from "axios";

export const loader = withAuth(async ({ request, params }: Route.LoaderArgs) => {
    const http = createHttp(request);
    const problemId = params.problemId;

    try {
        const result = await http.get(`/drafts/latest/`, {
            problem_id: parseInt(problemId)
        });
        return result;
    } catch (error) {
        if (error instanceof AxiosError && error.response?.status === 404) {
            return null;
        }
        throw error;
    }
})
