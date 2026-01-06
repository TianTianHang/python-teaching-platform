import JupyterLiteEmbed from "~/components/JupyterLiteEmbed";

import { redirect, useLocation } from "react-router";
import { getSession } from "~/sessions.server";
import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "../+types/root";

export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
  const session = await getSession(request.headers.get('Cookie'));
  if (!session.get('isAuthenticated')) {
    return redirect(`/auth/login`);
  }
  const access = session.get('accessToken'); ;
  return access;
})

export default function JupyterLite({loaderData}:Route.ComponentProps) {
    const  location = useLocation()
    return (
        <JupyterLiteEmbed url={location.pathname} access={loaderData}/>
    );
}