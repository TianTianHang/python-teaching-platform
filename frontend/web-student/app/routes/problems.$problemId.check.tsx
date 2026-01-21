import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/problems.$problemId.mark_as_solved";
import type { CheckFillBlankResponse } from "~/types/course";
import { withAuth } from "~/utils/loaderWrapper";

const backend = {
    fill_blank: 'check_fillblank',
} as const;


type BackendType = keyof typeof backend;
interface ResponseMap {
    fill_blank: CheckFillBlankResponse;

}
type GetResponseType<T extends BackendType> = ResponseMap[T];
export const action = withAuth(async ({ request, params }: Route.ActionArgs) => {
    const http = createHttp(request);
    const formData = await request.formData();
    const url = new URL(request.url);
    const searchParams = url.searchParams;
    const type = (searchParams.get("type") || 'fill_blank') as BackendType;
    const payload: Record<string, string> = {};

    for (const [key, value] of formData.entries()) {
        if (typeof value === 'string') {
        payload[key] = JSON.parse(value);
        }

    }
   
    // 确保 type 是合法值
    if (!Object.keys(backend).includes(type)) {
        throw new Response('Invalid type', { status: 400 });
    }

    const endpoint = `/problems/${params.problemId}/${backend[type]}/`;

    // 使用类型断言，因为我们知道 type 对应的响应结构
    const result = await http.post<GetResponseType<typeof type>>(endpoint,payload);

    return result;
});
