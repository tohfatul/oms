import { useState } from "react";
import type { FormEvent } from "react";
import type {
  AccountInfo,
  IPublicClientApplication,
} from "@azure/msal-browser";

import {
  sendAiMessage,
  type AiChatMessage,
  type PendingOrder,
} from "../api/aiApi";

type AiAssistantProps = {
  instance: IPublicClientApplication;
  account: AccountInfo;
};

type Message = {
  role: "user" | "assistant";
  text: string;
  sources?: string[];
};

export function AiAssistant({ instance, account }: AiAssistantProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pendingOrder, setPendingOrder] = useState<PendingOrder | null>(null);

  const submit = async (event: FormEvent) => {
    event.preventDefault();

    const message = input.trim();

    if (!message || loading) {
      return;
    }

    // const history: AiChatMessage[] = messages.map((item) => ({
    //   role: item.role,
    //   content: item.text,
    // }));

    setMessages((current) => [
      ...current,
      {
        role: "user",
        text: message,
      },
    ]);

    setInput("");
    setLoading(true);
    setError(null);

    try {
      const history: AiChatMessage[] = messages.map((item) => ({
        role: item.role,
        content: item.text,
      }));

      const result = await sendAiMessage(
        instance,
        account,
        message,
        history,
        pendingOrder,
      );

      setPendingOrder(result.pending_order);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: result.message,
          sources: result.sources,
        },
      ]);
    } catch (error) {
      setError(
        error instanceof Error
          ? error.message
          : "Unable to contact the AI assistant.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card shadow-sm mt-4">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-center mb-3">
          <div>
            <h2 className="h5 mb-1">OrderFlow AI Assistant</h2>
            <p className="small text-secondary mb-0">
              Ask about products, orders, or the OrderFlow system.
            </p>
          </div>

          <span className="badge text-bg-primary">AI</span>
        </div>

        <div className="alert alert-light border text-start">
          <div className="fw-semibold mb-2">You can ask OrderFlow AI to:</div>

          <ul className="mb-0 ps-3">
            <li>How does OrderFlow process orders asynchronously?</li>
            <li>Show all available products</li>
            <li>Search products by name, SKU, or product ID</li>
            <li>Find products even with minor typing mistakes</li>
            <li>Show details for an existing order using its order ID</li>
            <li>Explain how to create an order</li>
            <li>
              Prepare an order, for example:
              <br />
              <span className="text-secondary">
                Create an order for customer CUST-100 with 2 Business Laptop
              </span>
            </li>
            <li>
              Create an order with multiple products, for example:
              <br />
              <span className="text-secondary">
                Create an order for customer CUST-100 with 2 Business Laptop and
                1 Wireless Mouse
              </span>
            </li>
            <li>Ask follow-up questions about products or orders</li>
            <li>Ask general questions about OrderFlow or order management</li>
          </ul>

          <div className="small text-secondary mt-3">
            Order creation requires explicit confirmation before the order is
            submitted.
          </div>
        </div>

        {messages.length > 0 && (
          <div
            className="border rounded p-3 mb-3 bg-light"
            style={{
              maxHeight: "360px",
              overflowY: "auto",
            }}
          >
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-3 ${
                  message.role === "user" ? "text-end" : "text-start"
                }`}
              >
                <div
                  className={`d-inline-block rounded px-3 py-2 ${
                    message.role === "user"
                      ? "bg-primary text-white"
                      : "bg-white border"
                  }`}
                  style={{
                    maxWidth: "85%",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  <div>{message.text}</div>

                  {message.role === "assistant" &&
                    message.sources &&
                    message.sources.length > 0 && (
                      <div className="small text-secondary mt-2 pt-2 border-top">
                        <span className="fw-semibold">Sources:</span>{" "}
                        {message.sources.join(", ")}
                      </div>
                    )}
                </div>
              </div>
            ))}
          </div>
        )}

        {error && <div className="alert alert-danger">{error}</div>}

        {pendingOrder && (
          <div className="alert alert-warning">
            <div className="fw-semibold mb-2">
              Pending Order — Not Submitted
            </div>

            <div>Customer: {pendingOrder.customer_id}</div>

            <ul className="mb-2 mt-2">
              {pendingOrder.items.map((item) => (
                <li key={item.product_id}>
                  {item.name} × {item.quantity}
                  {" — "}${(item.unit_price * item.quantity).toFixed(2)}
                </li>
              ))}
            </ul>

            <div className="fw-semibold">
              Total: ${pendingOrder.total_amount.toFixed(2)}
            </div>

            <div className="small mt-2">
              Type <strong>confirm</strong> to place this order.
            </div>
          </div>
        )}

        <form onSubmit={submit}>
          <div className="input-group">
            <input
              type="text"
              className="form-control"
              placeholder="Ask OrderFlow AI..."
              value={input}
              onChange={(event) => setInput(event.target.value)}
              disabled={loading}
            />

            <button
              type="submit"
              className="btn btn-primary"
              disabled={loading || !input.trim()}
            >
              {loading ? "Thinking..." : "Send"}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}
