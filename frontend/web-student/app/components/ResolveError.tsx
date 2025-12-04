import { useEffect, type ReactNode } from "react";
import { useAsyncError, useLocation, useNavigate } from "react-router";
import { showNotification } from "./Notification";
import { useMount } from "ahooks";
import { AxiosError } from "axios";



export default function ResolveError({ children }: { children: ReactNode }) {
    const error = useAsyncError();
    const navigate = useNavigate();
    const location = useLocation();
    useMount(() => {
        try {
            const parsedError = JSON.parse((error as Error).message);
            if (parsedError && parsedError.isAxiosError) {
                if (parsedError.status === 401) {
                    console.log("Detected 401 error, redirecting to refresh token");
                    showNotification("warning", "refresh", "token过期，尝试刷新");
                    navigate(`/refresh?back=${encodeURIComponent(location.pathname)}`);
                    return;
                }

            }
        } catch (e) {
            console.error("error message:", e);
        }
    });

    return children;
}