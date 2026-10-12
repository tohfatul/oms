import type {
  AccountInfo,
  IPublicClientApplication,
} from "@azure/msal-browser";
import type { CartItem } from "../types/cart";
import type { CreateOrderResponse } from "../types/order";
import { getAccessToken } from "./authApi";

export async function createOrder(
  instance: IPublicClientApplication,
  account: AccountInfo,
  customerId: string,
  cart: CartItem[],
): Promise<CreateOrderResponse> {
  const token = await getAccessToken(instance, account);

  const response = await fetch(
    `${import.meta.env.VITE_API_BASE_URL}/api/orders`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        customerId,
        items: cart.map((item) => ({
          productId: item.productId,
          quantity: item.quantity,
        })),
      }),
    },
  );

  if (!response.ok) {
    throw new Error(
      `Order creation failed: ${response.status} ${response.statusText}`,
    );
  }

  return response.json();
}
