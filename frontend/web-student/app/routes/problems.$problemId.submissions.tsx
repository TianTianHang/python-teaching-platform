import { Typography, Stack, Pagination, Box } from "@mui/material";
import { useNavigate, useRouteLoaderData } from "react-router";
import SubmissionItem from "~/components/SubmissionTtem";
import type { Submission } from "~/types/submission";
import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/problems.$problemId.submissions";
import createHttp from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { DEFAULT_META, formatTitle, PAGE_TITLES } from "~/config/meta";

export const loader = withAuth(async ({ request, params }: Route.LoaderArgs) => {
    const url = new URL(request.url);
    const searchParams = url.searchParams;
    // 将 page 参数解析为数字，如果不存在则默认为 1
    const page = parseInt(searchParams.get("page") || "1", 10);
    const pageSize = parseInt(searchParams.get("page_size") || "10", 10); // 可以添加 page_size 参数，默认为10
    // 构建查询参数对象
    const queryParams = new URLSearchParams();
    queryParams.set("page", page.toString());
    queryParams.set("page_size", pageSize.toString()); // 添加 pageSize 到查询参数q\
    queryParams.set("problemId", String(params.problemId));
    const http = createHttp(request);
    const submissions = await http.get<Page<Submission>>(`/submissions/?${queryParams.toString()}`);
    // 返回 currentPage, totalItems 和 actualPageSize
    return {
        data: submissions.results,
        currentPage: page,
        totalItems: submissions.count,
        // 从后端数据中获取 page_size，如果不存在则使用默认值
        actualPageSize: submissions.page_size || pageSize,

    };
})
export default function ProblemSubmissions({ loaderData }: Route.ComponentProps) {
    const { data, currentPage, totalItems, actualPageSize } = loaderData
    const totalPages = Math.ceil(totalItems / actualPageSize);
    const navigate = useNavigate();
    // 处理页码变化的函数
    const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
        // 构建新的 URL
        const newSearchParams = new URLSearchParams();
        newSearchParams.set("page", value.toString());
        newSearchParams.set("page_size", actualPageSize.toString()); // 保持 pageSize

        navigate(`/problems/?${newSearchParams.toString()}`);
    };
    const pdata = useRouteLoaderData("routes/problems.$problemId");
    const problem = pdata.problem;
    return (
        <>
          <title>{formatTitle(PAGE_TITLES.problem(problem.title))}</title>
          <Box sx={{ mt: 2 }}>
            <Typography variant="h6">提交记录</Typography>
            {data && data.length > 0 ? (
                <Stack spacing={2} sx={{ mt: 1 }}>
                    {data.map((submission, index) => (
                        <SubmissionItem
                            key={submission.id || index}
                            submission={submission}
                        // reUseCode={null}
                        />
                    ))}
                    {totalPages > 1 && (
                        <Stack spacing={2} sx={{ mt: 3, mb: 2, alignItems: 'center' }}>
                            <Pagination
                                count={totalPages}
                                page={currentPage}
                                onChange={handlePageChange}
                                color="primary"
                                showFirstButton
                                showLastButton
                            />
                        </Stack>
                    )}
                </Stack>
            ) : (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    暂无提交记录
                </Typography>
            )}
        </Box>
        </>
    );
}
