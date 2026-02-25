import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/_layout.threads_.$threadId";
import createHttp from "~/utils/http/index.server";
import type { Thread } from "~/types/thread";
import MainThread from "~/components/Thread/MainThread";
import { formatTitle } from "~/config/meta";

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
    const http = createHttp(request);

    const thread = await http.get<Thread>(`/threads/${params.threadId}`);
    return thread;
})



export default function ThreadMainPage({loaderData}: Route.ComponentProps) {
    const thread = loaderData;
    return (
        <>
          <title>{formatTitle('讨论帖')}</title>
          <MainThread thread={thread}/>
        </>
    )
}
