
import type { Route } from "./+types/submission";
import createHttp from "~/utils/http/index.server";
import type { Submission, SubmissionFreelyRes, SubmissionRes } from "~/types/submission";
import type { Page } from "~/types/page";
import { withAuth } from "~/utils/loaderWrapper";
export interface SubmissionReq {
    code: string;
    language: string;
    problem_id?: number;
}
export const action = withAuth(async ({
    request
}: Route.ActionArgs) => {
    const formData = await request.formData();
    const code = String(formData.get("code"));
    const language = String(formData.get("language"));
    const problem_id = Number(formData.get("problem_id"));
    const http = createHttp(request);
    const result = await http.post<SubmissionFreelyRes | SubmissionRes>(
        "/submissions/",
        { code, language, problem_id }
    );
    return Response.json(result);
})
export const loader = withAuth(async ({
    request, params
}: Route.LoaderArgs) => {
    const url = new URL(request.url);

    const searchParams = url.searchParams;
    const problemId = searchParams.get("problemId")
    // 将 page 参数解析为数字，如果不存在则默认为 1
    const page = parseInt(searchParams.get("page") || "1", 10);
    const pageSize = parseInt(searchParams.get("page_size") || "10", 10); // 可以添加 page_size 参数，默认为10
    // 构建查询参数对象
    const queryParams = new URLSearchParams();
    queryParams.set("page", page.toString());
    queryParams.set("page_size", pageSize.toString()); // 添加 pageSize 到查询参数
    const http = createHttp(request);
    const data = await http.get<Page<Submission>>(`/problems/${problemId}/submissions/?${queryParams.toString()}`);
    // 返回 currentPage, totalItems 和 actualPageSize
    return Response.json({
        data: data.results,
        currentPage: page,
        totalItems: data.count,
        // 从后端数据中获取 page_size，如果不存在则使用默认值
        actualPageSize: data.page_size || pageSize,
    })
})

