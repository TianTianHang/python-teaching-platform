// src/utils/loaderWrapper.ts

import { redirect } from "react-router";
import { isApiError } from "./typeGuards";



export function withAuth<T extends (...args: any[]) => any>(fn: T): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error: unknown) {
      if (isApiError(error) && error.response?.status === 401) {
        const url = new URL((args[0] as { request: { url: string } }).request.url);
        return redirect(`/refresh?back=${encodeURIComponent(url.pathname)}`);
      }
      if (isApiError(error)) {
        throw new Response(JSON.stringify(error.response?.data), {
          headers: {
            'Content-Type': 'application/json',
          },
          status: error.response?.status || 500,
        });
      }

      throw error;
    }
  }) as T;
}