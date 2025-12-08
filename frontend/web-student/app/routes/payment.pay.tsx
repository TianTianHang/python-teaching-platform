import { withAuth } from "~/utils/loaderWrapper";
import type { Route } from "./+types/payment.pay";
import createHttp from "~/utils/http/index.server";


export const action = withAuth(async ({ request }: Route.ActionArgs) => {
  const formData = await request.formData();
  const order_id = formData.get('order_id');
  const payment_method = formData.get('payment_method');
  if (order_id && payment_method) {
    const http = createHttp(request);
    const res = await http.post<{
      method: string;
      pay_url: string;
      gateway: string;
    }>(`/orders/${order_id}/pay/`, { payment_method })
    return res;
  } else {
    return {}
  }

})