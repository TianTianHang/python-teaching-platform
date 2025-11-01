import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/refresh";
import { commitSession, destroySession, getSession } from "~/sessions.server";
import { redirect } from "react-router";

export async function loader({
    request
}: Route.LoaderArgs) {
    const url = new URL(request.url);

    const searchParams = url.searchParams;
    const back = searchParams.get("back");
    const http = createHttp(request);
    const session = await getSession(request.headers.get('Cookie'));
    const refresh = session.get('refreshToken');
    try {
        const newToken = await http.post<{ access: string, refresh: string }>("/auth/refresh", {
            refresh: refresh,
        });
        session.set('accessToken', newToken.access);
        session.set('refreshToken', newToken.refresh);
        return redirect(back || "/home", {
            headers: {
                'Set-Cookie': await commitSession(session),
            },
        });
    } catch (error) {
        await destroySession(session)
        redirect("/auth/login", {
            headers: {
                'Set-Cookie': await commitSession(session),
            },
        });
    }
}