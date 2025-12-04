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
       console.error("error message:", error);
    });

    return children;
}