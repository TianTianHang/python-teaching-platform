import { useEffect, type ReactNode } from "react";
import { useAsyncError, useNavigate } from "react-router";
import { showNotification } from "./Notification";
import { AxiosError } from "axios";



export default function ResolveError({ children }: { children: ReactNode }) {
    const error = useAsyncError() as Error;
    const navagate = useNavigate();

    useEffect(() => {
        if (error instanceof AxiosError && error.response?.status === 401 ) {
            showNotification("warning","refresh","token过期，尝试刷新")
            const url = new URL(error.request.url);
            navagate(`/refresh?back=${encodeURIComponent(location.pathname)}`)
        }
    }),[]

    return children;
}