import JupyterLiteEmbed from "~/components/JupyterLiteEmbed";
import { getSession } from "~/sessions.server";
import { withAuth } from "~/utils/loaderWrapper";
import { formatTitle, PAGE_TITLES } from "~/config/meta";
import type { Route } from "./+types/_layout.jupyter";





export const loader = withAuth(async ({ request }: Route.LoaderArgs) => {
    const session = await getSession(request.headers.get('Cookie'));
    return session.get('accessToken');
})
export default function JupyterLite({loaderData}:Route.ComponentProps) {
    const access= loaderData||"";
    return (
        <>
            <title>{formatTitle(PAGE_TITLES.jupyter)}</title>
            <JupyterLiteEmbed url={"/jupyterlite/lab/index.html"} access={access} />
        </>
    );
}