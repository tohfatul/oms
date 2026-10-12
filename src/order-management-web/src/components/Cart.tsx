import type { CartItem } from "../types/cart";

type Props = {
  cart: CartItem[];
  customerId: string;
  onCustomerIdChange: (value: string) => void;
  onSubmit: () => void;
};

export function Cart({
  cart,
  customerId,
  onCustomerIdChange,
  onSubmit,
}: Props) {
  if (cart.length === 0) {
    return null;
  }

  const total = cart.reduce((sum, item) => sum + item.price * item.quantity, 0);

  return (
    <section className="card mt-4">
      <div className="card-body">
        <h2 className="card-title mb-3">Cart</h2>

        <ul className="list-group mb-3">
          {cart.map((item) => (
            <li
              key={item.productId}
              className="list-group-item d-flex justify-content-between"
            >
              <span>
                {item.name} × {item.quantity}
              </span>

              <strong>${(item.price * item.quantity).toFixed(2)}</strong>
            </li>
          ))}
        </ul>

        <div className="text-end mb-3">
          <strong>Total: ${total.toFixed(2)}</strong>
        </div>

        <div className="row g-2">
          <div className="col-md-8">
            <input
              className="form-control"
              value={customerId}
              onChange={(e) => onCustomerIdChange(e.target.value)}
              placeholder="Customer ID"
            />
          </div>

          <div className="col-md-4">
            <button
              className="btn btn-primary w-100"
              onClick={onSubmit}
              disabled={!customerId || cart.length === 0}
            >
              Submit Order
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
