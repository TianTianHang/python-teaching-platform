import { type ReactNode } from "react";
import { useLocation, useNavigate } from "react-router";
import { showNotification } from "./Notification";
import { useMount } from "ahooks";




export default function ResolveError({ children, status, message }: { children: ReactNode,status?:number, message?:string }) {
    const navigate = useNavigate();
    const location = useLocation();
    useMount(() => {
       if(status && message){
        if(status === 401){
          const currentPath = location.pathname + location.search;
          navigate(`/refresh?back=${encodeURIComponent(currentPath)}`);
          showNotification("warning","","登录已过期，尝试刷新token")
        }
       }
    });

    return children;
}