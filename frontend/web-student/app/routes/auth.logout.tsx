import { redirect } from "react-router";
import {
  getSession,
  destroySession,
} from "../sessions.server";
import type { Route } from "./+types/auth.logout";
import createHttp from "~/utils/http/index.server";
import {withAuth} from "~/utils/loaderWrapper";
export const action = withAuth(async ({
  request, params
}: Route.ActionArgs) => {
  const session = await getSession(
    request.headers.get("Cookie"),
  );
  const http = createHttp(request);
  const refresh = session.get("refreshToken")
  try {
    http.post('auth/logout', { refresh })
  }
  catch (error) {
    console.log(error)
  }
  return redirect(`/auth/login`, {
    headers: {
      "Set-Cookie": await destroySession(session),
    },
  });
})

