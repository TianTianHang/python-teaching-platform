import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLocation,
  useNavigate,
} from "react-router";
import { ThemeProvider, createTheme, useTheme } from '@mui/material/styles';
import type { Route } from "./+types/root";
import "./app.css";
import { NotificationProvider } from "./components/Notification";
import { Alert, AlertTitle, Box, Container, Paper, Stack, Typography } from "@mui/material";
import { useEffect } from "react";
import type { AxiosError } from "axios";

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
  },
];

export function Layout({ children }: { children: React.ReactNode }) {

  const theme = createTheme();
  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="emotion-insertion-point" content="" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <ThemeProvider theme={theme}>
          <NotificationProvider>
            {children}
          </NotificationProvider>
        </ThemeProvider>

        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  return <Outlet />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "Oops!";
  let details = "An unexpected error occurred.";
  let stack: string | undefined;
  const theme = useTheme();
  
  if (isRouteErrorResponse(error)) {

    message = error.status === 404 ? "404" : "Error";
    details =
      error.status === 404
        ? "The requested page could not be found."
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <Container
      maxWidth="md"
      sx={{
        pt: { xs: 8, sm: 10 }, // 相当于 pt-16（16 = 4rem，MUI 默认 spacing=8px，所以 16*0.25=4 → pt=4）
        pb: 4,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          borderRadius: 2,
          backgroundColor: theme.palette.mode === 'dark'
            ? 'background.paper'
            : '#fff',
        }}
      >
        <Stack spacing={2}>
          <Typography variant="h4" color="error" fontWeight="bold">
            {message || '发生错误'}
          </Typography>

          {details && (
            <Typography variant="body1" color="text.secondary">
              {details}
            </Typography>
          )}

          {stack && (
            <Alert severity="error" variant="outlined">
              <AlertTitle>错误堆栈</AlertTitle>
              <Box
                component="pre"
                sx={{
                  mt: 1,
                  p: 1.5,
                  overflowX: 'auto',
                  fontSize: '0.875rem',
                  fontFamily: 'monospace',
                  backgroundColor: theme.palette.mode === 'dark'
                    ? 'grey.900'
                    : 'grey.100',
                  borderRadius: 1,
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                <code>{stack}</code>
              </Box>
            </Alert>
          )}
        </Stack>
      </Paper>
    </Container>
  );
}
