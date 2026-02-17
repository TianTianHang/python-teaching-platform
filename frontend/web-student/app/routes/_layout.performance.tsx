/**
 * 性能测试页面
 * 用于测试 API 接口的响应时间
 */

import * as React from "react";
import { Box, Button, Card, CardContent, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, Typography, useTheme } from "@mui/material";
import { formatTitle, PAGE_TITLES } from '~/config/meta';
import { Speed as SpeedIcon, PlayArrow as PlayArrowIcon } from "@mui/icons-material";
import { data, redirect, useSubmit, useNavigation, useActionData } from "react-router";
import { getSession, commitSession } from "~/sessions.server";
import type { PerformanceMetrics } from "~/utils/performance.server";
import { testLogin, testProblems, testChapters, testCourses } from "~/utils/apiTester.server";
import { PageContainer } from "~/components/Layout";
import { spacing } from "~/design-system/tokens";

// 本地存储的键名
const STORAGE_KEY = 'performance-test-results';

// 类型定义
interface LoaderData {
  user: { username: string } | null;
  previousResults: PerformanceMetrics[];
}

/**
 * 从 local storage 获取存储的测试结果（仅在客户端执行）
 */
function getStoredResults(): PerformanceMetrics[] {
  if (typeof window === 'undefined') {
    return [];
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      const results = JSON.parse(stored);
      return Array.isArray(results) ? results : [];
    }
  } catch (error) {
    console.error('Error loading stored results:', error);
  }
  return [];
}

/**
 * 安全地存储到 local storage（仅在客户端执行）
 */
function safelySetStorage(key: string, value: string): void {
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem(key, value);
    } catch (error) {
      console.error('Error storing to localStorage:', error);
    }
  }
}

/**
 * 存储测试结果到 local storage
 */
function storeResult(result: PerformanceMetrics): void {
  try {
    const previousResults = getStoredResults();
    const updatedResults = [result, ...previousResults].slice(0, 10);
    safelySetStorage(STORAGE_KEY, JSON.stringify(updatedResults));
  } catch (error) {
    console.error('Error storing result:', error);
  }
}

/**
 * Loader - 检查用户认证状态
 */
export async function loader({ request }: { request: Request }) {
  const session = await getSession(request.headers.get('Cookie'));

  // 检查认证状态
  if (!session.get('isAuthenticated')) {
    return redirect('/auth/login');
  }

  // 从 session 中获取用户信息，测试结果在客户端获取
  const user = session.get('user');
  const previousResults = []; // 空数组，客户端会重新加载

  return data(
    {
      user,
      previousResults: [],
    },
    {
      headers: {
        'Set-Cookie': await commitSession(session),
      },
    }
  );
}

/**
 * Action - 处理测试请求
 */
export async function action({ request }: { request: Request }) {
  // 获取 session（仅用于认证检查）
  // const session = await getSession(request.headers.get('Cookie'));
  const formData = await request.formData();
  const testType = String(formData.get("testType"));
  const username = String(formData.get("username") || "");
  const password = String(formData.get("password") || "");
  const courseId = String(formData.get("courseId") || "1");

  let result: PerformanceMetrics;

  // 根据测试类型执行相应的测试
  switch (testType) {
    case "login":
      result = await testLogin(request, username, password);
      break;
    case "problems":
      result = await testProblems(request);
      break;
    case "chapters":
      result = await testChapters(request, courseId);
      break;
    case "courses":
      result = await testCourses(request);
      break;
    default:
      return new Response("Invalid test type", { status: 400 });
  }

  return data({ result });
}

/**
 * 性能测试页面组件 - 纯客户端组件
 */
export default function PerformanceTestPage({ loaderData }: { loaderData: LoaderData }) {
  const theme = useTheme();
  const navigation = useNavigation();
  const actionData = useActionData<typeof action>();
  const { user } = loaderData;
  const [isTesting, setIsTesting] = React.useState(false);
  const [loginUsername, setLoginUsername] = React.useState("");
  const [loginPassword, setLoginPassword] = React.useState("");
  const [courseId, setCourseId] = React.useState("1");
  const [previousResults, setPreviousResults] = React.useState<PerformanceMetrics[]>([]);
  const submit = useSubmit();

  // 客户端加载历史记录
  React.useEffect(() => {
    setPreviousResults(getStoredResults());
  }, []);

  // 当导航结束时重置测试状态
  React.useEffect(() => {
    if (navigation.state !== "submitting" && navigation.state !== "loading") {
      setIsTesting(false);
    }
  }, [navigation.state]);

  // 当 action 返回新结果时，存储到 localStorage 并更新显示
  React.useEffect(() => {
    if (actionData?.result) {
      storeResult(actionData.result);
      setPreviousResults(getStoredResults());
    }
  }, [actionData]);

  /**
   * 执行测试
   */
  const runTest = (testType: string) => {
    setIsTesting(true);
    const formData = new FormData();
    formData.set("testType", testType);

    if (testType === "login") {
      formData.set("username", loginUsername);
      formData.set("password", loginPassword);
    } else if (testType === "chapters") {
      formData.set("courseId", courseId);
    }

    submit(formData, { method: "POST", action: "/performance" });
  };

  /**
   * 检查是否正在测试中
   */
  const isNavigationState = navigation.state === "submitting" || navigation.state === "loading";
  const isSubmitting = isTesting || isNavigationState;

  /**
   * 格式化时间（毫秒）
   */
  const formatTime = (ms: number | undefined) => {
    if (ms === undefined || ms === null) {
      return '0.00';
    }
    return ms.toFixed(2);
  };

  /**
   * 获取状态颜色
   */
  const getStatusColor = (success: boolean) => {
    return success ? "success.main" : "error.main";
  };

  /**
   * 获取状态文本
   */
  const getStatusText = (success: boolean) => {
    return success ? "成功" : "失败";
  };

  /**
   * 清空测试结果历史
   */
  const clearResults = () => {
    try {
      if (typeof window !== 'undefined') {
        localStorage.removeItem(STORAGE_KEY);
        setPreviousResults([]); // 清空本地状态
      }
    } catch (error) {
      console.error('Error clearing results:', error);
    }
  };

  return (
    <>
      <title>{formatTitle(PAGE_TITLES.performance)}</title>
      <PageContainer maxWidth="lg">
      {/* 页面标题 */}
      <Box sx={{ mb: spacing.xl }}>
        <Stack direction="row" spacing={spacing.sm} alignItems="center" sx={{ mb: spacing.sm }}>
          <SpeedIcon sx={{ color: "text.primary" }} />
          <Typography variant="h3" component="h1" color="text.primary">
            API 性能测试
          </Typography>
        </Stack>
        <Typography variant="subtitle1" color="text.secondary">
          测试从前端服务器到后端的请求响应时间
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mt: spacing.sm }}>
          当前用户：{user?.username || "未知"}
        </Typography>
      </Box>

      {/* 测试控制面板 */}
      <Stack spacing={spacing.lg}>
        {/* Login 测试卡片 */}
        <Card elevation={2}>
          <CardContent>
            <Typography variant="h6" gutterBottom color="text.primary">
              Login 测试 (POST /auth/login)
            </Typography>
            <Stack direction={{ xs: "column", md: "row" }} spacing={spacing.md} alignItems="flex-end">
              <TextField
                label="用户名"
                value={loginUsername}
                onChange={(e) => setLoginUsername(e.target.value)}
                disabled={isSubmitting}
                fullWidth
                size="small"
              />
              <TextField
                label="密码"
                type="password"
                value={loginPassword}
                onChange={(e) => setLoginPassword(e.target.value)}
                disabled={isSubmitting}
                fullWidth
                size="small"
              />
              <Button
                variant="contained"
                startIcon={<PlayArrowIcon />}
                onClick={() => runTest("login")}
                disabled={isSubmitting || !loginUsername || !loginPassword}
              >
                {isSubmitting ? "测试中..." : "测试"}
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* Problems 测试卡片 */}
        <Card elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h6" color="text.primary">
                  Problems 测试 (GET /problems/)
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  获取题目列表（分页：1，页大小：10）
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<PlayArrowIcon />}
                onClick={() => runTest("problems")}
                disabled={isSubmitting}
              >
                {isSubmitting ? "测试中..." : "测试"}
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* Chapters 测试卡片 */}
        <Card elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h6" color="text.primary">
                  Chapters 测试 (GET /courses/{courseId}/chapters)
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  获取指定课程的章节列表
                </Typography>
              </Box>
              <Stack direction="row" spacing={spacing.md} alignItems="center">
                <TextField
                  label="课程 ID"
                  type="number"
                  value={courseId}
                  onChange={(e) => setCourseId(e.target.value)}
                  disabled={isSubmitting}
                  size="small"
                  sx={{ width: 120 }}
                />
                <Button
                  variant="contained"
                  startIcon={<PlayArrowIcon />}
                  onClick={() => runTest("chapters")}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "测试中..." : "测试"}
                </Button>
              </Stack>
            </Stack>
          </CardContent>
        </Card>

        {/* Courses 测试卡片 */}
        <Card elevation={2}>
          <CardContent>
            <Stack direction="row" justifyContent="space-between" alignItems="center">
              <Box>
                <Typography variant="h6" color="text.primary">
                  Courses 测试 (GET /courses/)
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  获取课程列表（分页：1，页大小：10）
                </Typography>
              </Box>
              <Button
                variant="contained"
                startIcon={<PlayArrowIcon />}
                onClick={() => runTest("courses")}
                disabled={isSubmitting}
              >
                {isSubmitting ? "测试中..." : "测试"}
              </Button>
            </Stack>
          </CardContent>
        </Card>

        {/* 测试结果表格 */}
        {previousResults.length > 0 && (
          <Card elevation={2}>
            <CardContent>
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: spacing.md }}>
                <Typography variant="h6" color="text.primary">
                  测试结果历史
                </Typography>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={clearResults}
                  disabled={previousResults.length === 0}
                >
                  清空记录
                </Button>
              </Stack>
              <TableContainer component={Paper} elevation={0}>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>端点</TableCell>
                      <TableCell>状态</TableCell>
                      <TableCell align="right">总时间 (ms)</TableCell>
                      <TableCell align="right">前端处理 (ms)</TableCell>
                      <TableCell align="right">后端请求 (ms)</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {previousResults.map((result: PerformanceMetrics, index: number) => (
                      <TableRow
                        key={index}
                        sx={{
                          "&:last-child td, &:last-child th": { border: 0 },
                          backgroundColor: index === 0 ? theme.palette.action.hover : "inherit",
                        }}
                      >
                        <TableCell component="th" scope="row">
                          <Typography variant="body2" sx={{ fontFamily: "monospace" }}>
                            {result.endpoint}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography
                            variant="body2"
                            sx={{ color: getStatusColor(result.success), fontWeight: 500 }}
                          >
                            {getStatusText(result.success)}
                            {result.error && ` (${result.error})`}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2">
                            {formatTime(result.totalTime)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="text.secondary">
                            {formatTime(result.frontendProcessing)}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color="text.secondary">
                            {formatTime(result.backendRequest)}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        )}
      </Stack>
    </PageContainer>
    </>
  );
}