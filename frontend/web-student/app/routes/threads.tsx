
import type { Route } from "./+types/threads";
import createHttp from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { withAuth } from "~/utils/loaderWrapper";
import type { Thread } from "~/types/thread";
import { getSession } from "~/sessions.server";
export interface SubmissionReq {
    code: string;
    language: string;
    problem_id?: number;
}
export const action = withAuth(async ({
    request
}: Route.ActionArgs) => {
     const session = await getSession(
        request.headers.get("Cookie"),
      );
    const formData = await request.formData();
    const title = String(formData.get("title"));
    const content = String(formData.get("content"));
    const problemId = formData.get("problemId");
    const chapterId = formData.get("chapterId");
    const courseId = formData.get("courseId");
    const body = {
        title,
        content,
        author:session.get("user"),
        ...(problemId && { problem: problemId }),
        ...(chapterId && { chapter: chapterId }),
        ...(courseId && { course: courseId })
    };
    const http = createHttp(request);
    const result = await http.post<Thread>(
        "/threads/",
        body
    );
    return Response.json(result);
})
export const loader = withAuth(async ({
    request
}: Route.LoaderArgs) => {
    const url = new URL(request.url);
    if (url.pathname !== "/threads") {
        return
    }
    const searchParams = url.searchParams;
    const problemId = searchParams.get("problemId");
    const chapterId = searchParams.get("chapterId");
    const courseId = searchParams.get("courseId");
    // 将 page 参数解析为数字，如果不存在则默认为 1
    const page = parseInt(searchParams.get("page") || "1", 10);
    const pageSize = parseInt(searchParams.get("page_size") || "10", 10); // 可以添加 page_size 参数，默认为10
    // 构建查询参数对象
    const queryParams = new URLSearchParams();
    queryParams.set("page", page.toString());
    queryParams.set("page_size", pageSize.toString()); // 添加 pageSize 到查询参数
    if (problemId) {
        queryParams.set("problem", problemId);
    }
    if (chapterId) {
        queryParams.set("chapter", chapterId);
    }
    if (courseId) {
        queryParams.set("course", courseId);
    }

    const http = createHttp(request);
    const data = await http.get<Page<Thread>>(`/threads/?${queryParams.toString()}`);
    // 返回 currentPage, totalItems 和 actualPageSize
    return Response.json({
        data: data.results,
        currentPage: page,
        totalItems: data.count,
        // 从后端数据中获取 page_size，如果不存在则使用默认值
        actualPageSize: data.page_size || pageSize,
    })
})



