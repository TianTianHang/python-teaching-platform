import type { Problem } from "~/types/course";
import { createHttp } from "~/utils/http/index.server";
import type { Page } from "~/types/page";
import { Box, List, ListItem, ListItemIcon, ListItemText, Paper, Typography } from "@mui/material";
import { Alarm, Check } from "@mui/icons-material"
import { formatDateTime } from "~/utils/time";
import { useNavigate } from "react-router";
import type { Route } from "./+types/($lang)._layout.problems";

export async function loader({ request }: Route.LoaderArgs) {
  const http = createHttp(request);
  const problems = await http.get<Page<Problem>>(`/problems`);

  return problems;
}
export default function ProblemListPage({ loaderData, params }: Route.ComponentProps) {
  const problems = loaderData.results;
  const navigate = useNavigate();
  const getIcon = (type: string) => {
    switch (type) {
      case 'algorithm': return <Alarm />;
      case 'choice': return <Check/>
      default: return <Alarm />;
    }
  };
  const onClick = (id: number) => {
    navigate(`/${params.lang}/problems/${id}`)
  }
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
    </Box>

  )
}