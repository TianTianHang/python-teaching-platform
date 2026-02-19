import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/_layout.threads_.$threadId";
import createHttp from "~/utils/http/index.server";
import type { Thread } from "~/types/thread";
import MainThread from "~/components/Thread/MainThread";
import { DEFAULT_META } from "~/config/meta";

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
    const http = createHttp(request);

    const thread = await http.get<Thread>(`/threads/${params.threadId}`);
    return thread;
})



export default function ThreadMainPage({loaderData}: Route.ComponentProps) {
    const thread = loaderData;
    return (
        <>
          <title>讨论帖 - {DEFAULT_META.siteName}</title>
          <MainThread thread={thread}/>
        </>
    )
}
