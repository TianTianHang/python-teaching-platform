import { useEffect, type ReactNode } from "react";
import { useAsyncError, useLocation, useNavigate } from "react-router";
import { showNotification } from "./Notification";



export default function ResolveError({ children }: { children: ReactNode }) {
    const error = useAsyncError() as Error;
    const navagate = useNavigate();
    const location = useLocation()

    useEffect(() => {
        if (error.message === 'Unauthorized: redirect required') {
            showNotification("warning","refresh","token过期，尝试刷新")
            navagate(`/refresh?back=${encodeURIComponent(location.pathname)}`)
        }
    })

    return children;
}