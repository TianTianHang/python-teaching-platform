import { withAuth } from "~/utils/loaderWrapper";

import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/orders.create";
import type { Order } from "~/types/order";


export const action = withAuth(async ({ request }: Route.ActionArgs) => {
    const formData = await request.formData();
    const membership_type = formData.get('membershipType');
    if(!membership_type){
        return {"detail":"请选择会员类型"}
    }
    const http = createHttp(request);
    const order = await http.post<Order>(`/orders/`, { membership_type })
    return order;

})