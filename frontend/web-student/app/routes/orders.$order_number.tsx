import createHttp from "~/utils/http/index.server";
import type { Route } from "./+types/orders.$order_number";
import type { Order } from "~/types/order";
import { data } from "react-router";
import { withAuth } from "~/utils/loaderWrapper";

export const loader = withAuth(async ({ params, request }: Route.LoaderArgs) => {
    const { order_number } = params;
    const http = createHttp(request);
    const order = await http.get<Order>(`orders/${order_number}`);

    if (!order) throw data('Not found', { status: 404 });
    return order;
});