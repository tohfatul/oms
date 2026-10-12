import type { CreateOrderResponse } from "../types/order";

type Props = {
  order: CreateOrderResponse | null;
};

export function OrderConfirmation({ order }: Props) {
  if (!order) {
    return null;
  }

  return (
    <div className="alert alert-success mt-4">
      <h4 className="alert-heading">Order Submitted Successfully</h4>

      <p>
        Order Number: <strong>{order.orderNumber}</strong>
      </p>

      <p>
        Status: <strong>{order.status}</strong>
      </p>

      <hr />

      <small>Order ID: {order.orderId}</small>
    </div>
  );
}
