/* eslint-disable @typescript-eslint/no-explicit-any */
// src/utils/loaderWrapper.ts

import { redirect } from "react-router";
import { AxiosError } from "axios";



export function withAuth<T extends (...args: any[]) => any>(fn: T): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      if (error instanceof AxiosError && error.response?.status === 401 ) {
        const url = new URL(args[0].request.url);
        return redirect(`/refresh?back=${encodeURIComponent(url.pathname)}`);
      }
     throw error;
    }
  }) as T;
}