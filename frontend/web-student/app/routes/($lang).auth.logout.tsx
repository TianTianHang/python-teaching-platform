import { redirect } from "react-router";
import {
  getSession,
  destroySession,
} from "../sessions.server";
import type { Route } from "./+types/($lang).auth.logout";
import createHttp from "~/utils/http/index.server";

export async function action({
  request,params
}: Route.ActionArgs) {
  const session = await getSession(
    request.headers.get("Cookie"),
  );
  const http = createHttp(request);
  const refresh = session.get("refreshToken")
  http.post('auth/logout',{refresh})
  return redirect(`/${params.lang||"zh"}/auth/login`, {
    headers: {
      "Set-Cookie": await destroySession(session),
    },
  });
}
