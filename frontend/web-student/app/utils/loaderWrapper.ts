// src/utils/loaderWrapper.ts

import { redirect, type ActionFunction, type ActionFunctionArgs, type LoaderFunction, type LoaderFunctionArgs } from "react-router";
import { UnauthorizedRedirectError } from "./http/error";
import { AxiosError } from "axios";


type AsyncHandler<T extends LoaderFunctionArgs | ActionFunctionArgs> = (
  args: T
) => Promise<Response | any>;

export function withAuth<T extends (...args: any[]) => any>(fn: T): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      if (error instanceof AxiosError && error.response?.status === 401 ) {
        const url = new URL(error.request.url);
        return redirect(`/refresh?back=${encodeURIComponent(url.pathname)}`);

      }
     return {"error":error};
    }
  }) as T;
}