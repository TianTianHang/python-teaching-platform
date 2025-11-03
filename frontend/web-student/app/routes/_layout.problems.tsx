import type { Problem } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { Box, List, ListItem, ListItemIcon, ListItemText, Pagination, Paper, Stack, Typography } from "@mui/material";
import { Alarm, Check } from "@mui/icons-material"
import { formatDateTime } from "~/utils/time";
import { useNavigate } from "react-router";
import type { Route } from "./+types/_layout.problems";
import { withAuth } from "~/utils/loaderWrapper";
export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  const url = new URL(request.url);
  const searchParams = url.searchParams;
  const type = searchParams.get("type");
  // 将 page 参数解析为数字，如果不存在则默认为 1
  const page = parseInt(searchParams.get("page") || "1", 10);
  const pageSize = parseInt(searchParams.get("page_size") || "10", 10); // 可以添加 page_size 参数，默认为10
  // 构建查询参数对象
  const queryParams = new URLSearchParams();
  queryParams.set("page", page.toString());
  queryParams.set("page_size", pageSize.toString()); // 添加 pageSize 到查询参数
  if (type !== null) queryParams.set("type", type);
  const http = createHttp(request);
  const problems = await http.get<Page<Problem>>(`/problems/?${queryParams.toString()}`);
  // 返回 currentPage, totalItems 和 actualPageSize
  return {
    data: problems.results,
    currentPage: page,
    totalItems: problems.count,
    // 从后端数据中获取 page_size，如果不存在则使用默认值
    actualPageSize: problems.page_size || pageSize,
    currentType: type
  };
})

export default function ProblemListPage({ loaderData, params }: Route.ComponentProps) {
  const problems = loaderData.data;
  const currentPage = loaderData.currentPage;
  const currentType = loaderData.currentType;
  const totalItems = loaderData.totalItems;
  const actualPageSize = loaderData.actualPageSize;
  const totalPages = Math.ceil(totalItems / actualPageSize);
  const navigate = useNavigate();
  const getIcon = (type: string) => {
    switch (type) {
      case 'algorithm': return <Alarm />;
      case 'choice': return <Check />
      default: return <Alarm />;
    }
  };
  const onClick = (id: number) => {
    navigate(`/problems/${id}`)
  }
  // 处理页码变化的函数
  const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
    // 构建新的 URL
    const newSearchParams = new URLSearchParams();
    newSearchParams.set("page", value.toString());
    newSearchParams.set("page_size", actualPageSize.toString()); // 保持 pageSize
    if (currentType) {
      newSearchParams.set("type", currentType); // 保持 type 参数
    }
    navigate(`/problems/?${newSearchParams.toString()}`);
  };
  return (
    <Box>
      <Typography variant="h5" fontWeight={500} noWrap sx={{ width: '100%', maxWidth: 600, mx: 'auto', mt: 2 }}>
        Problem Set
      </Typography>
      <Paper sx={{ width: '100%', maxWidth: 600, mx: 'auto', mt: 2 }}>

        <List sx={{ py: 0 }}>
          {problems.map((problem) => (
            <ListItem
              onClick={() => onClick(problem.id)}
              key={problem.id}
              sx={{
                px: 2,
                py: 1.5,
                // 上下都加 divider（用 ::before 伪元素或直接 border）
                borderTop: '1px solid',
                borderColor: 'divider',
                transition: 'background-color 0.2s',
                '&:hover': { bgcolor: 'action.hover' },
              }}
            >
              <ListItemIcon sx={{ minWidth: 48, color: 'inherit' }}>
                {getIcon(problem.type)}
              </ListItemIcon>

              {/* 主内容区域：标题在左，时间在右 */}
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                <Typography variant="subtitle1" fontWeight={500} noWrap>
                  {problem.title}
                </Typography>
                <Typography variant="caption" color="text.disabled">
                  {formatDateTime(problem.created_at)}
                </Typography>
              </Box>
            </ListItem>
          ))}
        </List>
      </Paper>
      {/* 添加分页组件 */}
      {totalPages > 1 && ( // 只有当总页数大于1时才显示分页
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
    </Box>

  )
}