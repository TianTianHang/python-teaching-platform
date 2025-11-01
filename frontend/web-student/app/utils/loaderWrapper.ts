// src/utils/loaderWrapper.ts

import type { ActionFunction, ActionFunctionArgs, LoaderFunction, LoaderFunctionArgs } from "react-router";
import { UnauthorizedRedirectError } from "./http/error";


type AsyncHandler<T extends LoaderFunctionArgs | ActionFunctionArgs> = (
  args: T
) => Promise<Response | any>;

export function withAuth<T extends (...args: any[]) => any>(fn: T): T {
  return (async (...args: Parameters<T>) => {
    try {
      return await fn(...args);
    } catch (error) {
      if (error instanceof UnauthorizedRedirectError) {
        return error.redirectResponse;
      }
      throw error;
    }
  }) as T;
}