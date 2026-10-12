import { useState } from "react";
import {
  AuthenticatedTemplate,
  UnauthenticatedTemplate,
  useMsal,
} from "@azure/msal-react";
import { InteractionStatus } from "@azure/msal-browser";

import { loginRequest } from "./authConfig";
import { getProducts } from "./api/productApi";
import { createOrder } from "./api/orderApi";

import { ProductList } from "./components/ProductList";
import { Cart } from "./components/Cart";
import { OrderConfirmation } from "./components/OrderConfirmation";

import type { Product } from "./types/product";
import type { CartItem } from "./types/cart";
import type { CreateOrderResponse } from "./types/order";

function App() {
  const { instance, accounts, inProgress } = useMsal();

  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [createdOrder, setCreatedOrder] = useState<CreateOrderResponse | null>(
    null,
  );

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const login = async () => {
    if (inProgress !== InteractionStatus.None) {
      return;
    }

    try {
      await instance.loginPopup(loginRequest);
    } catch (error) {
      console.error("Login failed:", error);
    }
  };

  const logout = async () => {
    await instance.logoutPopup();
  };

  const loadProducts = async () => {
    if (!accounts[0]) {
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await getProducts(instance, accounts[0]);
      setProducts(data);
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Unable to load products.",
      );
    } finally {
      setLoading(false);
    }
  };

  const addToCart = (product: Product) => {
    setCart((current) => {
      const existing = current.find((item) => item.productId === product.id);

      if (existing) {
        return current.map((item) =>
          item.productId === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item,
        );
      }

      return [
        ...current,
        {
          productId: product.id,
          sku: product.sku,
          name: product.name,
          price: product.price,
          quantity: 1,
        },
      ];
    });
  };

  const submitOrder = async () => {
    if (!accounts[0] || cart.length === 0) {
      return;
    }

    try {
      setError(null);

      const result = await createOrder(instance, accounts[0], customerId, cart);

      setCreatedOrder(result);
      setCart([]);
      setCustomerId("");
    } catch (error) {
      setError(
        error instanceof Error ? error.message : "Unable to create order.",
      );
    }
  };

  return (
    <main className="container py-4">
      <h1 className="mb-4">Order Management System</h1>

      <UnauthenticatedTemplate>
        <p>Please sign in to access the OMS.</p>

        <button
          onClick={login}
          disabled={inProgress !== InteractionStatus.None}
        >
          {inProgress === InteractionStatus.None
            ? "Sign in with Microsoft"
            : "Signing in..."}
        </button>
      </UnauthenticatedTemplate>

      <AuthenticatedTemplate>
        <div className="d-flex justify-content-between align-items-center mb-4">
          <p className="mb-0">
            Signed in as <strong>{accounts[0]?.username}</strong>
          </p>

          <button className="btn btn-outline-secondary" onClick={logout}>
            Sign out
          </button>
        </div>

        <button
          className="btn btn-primary"
          onClick={loadProducts}
          disabled={loading}
        >
          {loading ? "Loading..." : "Load Products"}
        </button>

        {error && <div className="alert alert-danger mt-3">{error}</div>}

        <ProductList products={products} onAdd={addToCart} />

        <Cart
          cart={cart}
          customerId={customerId}
          onCustomerIdChange={setCustomerId}
          onSubmit={submitOrder}
        />

        <OrderConfirmation order={createdOrder} />
      </AuthenticatedTemplate>
    </main>
  );
}

export default App;
