import type {
  AccountInfo,
  IPublicClientApplication,
} from "@azure/msal-browser";
import type { Product } from "../types/product";
import { getAccessToken } from "./authApi";

export async function getProducts(
  instance: IPublicClientApplication,
  account: AccountInfo,
): Promise<Product[]> {
  const token = await getAccessToken(instance, account);

  const response = await fetch(
    `${import.meta.env.VITE_API_BASE_URL}/api/products`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    },
  );

  if (!response.ok) {
    throw new Error(
      `Unable to load products: ${response.status} ${response.statusText}`,
    );
  }

  return response.json();
}
