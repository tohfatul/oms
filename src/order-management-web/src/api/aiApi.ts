import type {
  AccountInfo,
  IPublicClientApplication,
} from "@azure/msal-browser";

import { getAccessToken } from "./authApi";

export type AiChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type PendingOrderItem = {
  product_id: string;
  sku: string;
  name: string;
  quantity: number;
  unit_price: number;
};

export type PendingOrder = {
  customer_id: string;
  items: PendingOrderItem[];
  total_amount: number;
};

export type AiChatResponse = {
  message: string;
  pending_order: PendingOrder | null;
  sources: string[];
};

export async function sendAiMessage(
  instance: IPublicClientApplication,
  account: AccountInfo,
  message: string,
  history: AiChatMessage[],
  pendingOrder: PendingOrder | null,
): Promise<AiChatResponse> {
  const token = await getAccessToken(instance, account);

  const response = await fetch(`${import.meta.env.VITE_AI_BASE_URL}/ai/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      message,
      history,
      pending_order: pendingOrder,
    }),
  });

  if (!response.ok) {
    let detail = `AI request failed: ${response.status} ${response.statusText}`;

    try {
      const body = await response.json();

      if (body?.detail) {
        detail = body.detail;
      }
    } catch {
      // Keep default error message.
    }

    throw new Error(detail);
  }

  return response.json();
}
