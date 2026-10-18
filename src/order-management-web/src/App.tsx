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
import AppFooter from "./components/AppFooter";
import AboutProject from "./pages/AboutProject";

import type { Product } from "./types/product";
import type { CartItem } from "./types/cart";
import type { CreateOrderResponse } from "./types/order";

type View = "oms" | "about";

function App() {
  const { instance, accounts, inProgress } = useMsal();

  const [view, setView] = useState<View>("oms");

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
    <div className="d-flex flex-column min-vh-100">
      <header className="border-bottom bg-white">
        <div className="container py-3">
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
            <div>
              <h1 className="h3 mb-0">Order Management System</h1>
              <small className="text-secondary">
                Full-Stack • Cloud • Event-Driven Architecture • AI
              </small>
            </div>

            <nav className="d-flex gap-2">
              <button
                type="button"
                className={`btn ${
                  view === "oms" ? "btn-primary" : "btn-outline-primary"
                }`}
                onClick={() => setView("oms")}
              >
                OMS
              </button>

              <button
                type="button"
                className={`btn ${
                  view === "about" ? "btn-primary" : "btn-outline-primary"
                }`}
                onClick={() => setView("about")}
              >
                About Project
              </button>
            </nav>
          </div>
        </div>
      </header>

      <main className="flex-grow-1">
        {view === "about" ? (
          <AboutProject />
        ) : (
          <div className="container py-4">
            <UnauthenticatedTemplate>
              <div className="card shadow-sm">
                <div className="card-body p-4">
                  <h2 className="h4">Welcome to the OMS</h2>

                  <p className="text-secondary mb-3">
                    Sign in with Microsoft to access products, create orders,
                    and use the authenticated Order Management System.
                  </p>

                  <button
                    className="btn btn-primary"
                    onClick={login}
                    disabled={inProgress !== InteractionStatus.None}
                  >
                    {inProgress === InteractionStatus.None
                      ? "Sign in with Microsoft"
                      : "Signing in..."}
                  </button>

                  <p className="small text-secondary mt-3 mb-0">
                    You can also explore the architecture, technologies, and
                    project features from the{" "}
                    <span
                      role="link"
                      tabIndex={0}
                      className="text-primary fw-semibold text-decoration-underline"
                      style={{ cursor: "pointer" }}
                      onClick={() => setView("about")}
                      onKeyDown={(event) => {
                        if (event.key === "Enter" || event.key === " ") {
                          setView("about");
                        }
                      }}
                    >
                      About Project
                    </span>{" "}
                    section without signing in.
                  </p>
                </div>
              </div>
            </UnauthenticatedTemplate>

            <AuthenticatedTemplate>
              <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3 mb-4">
                <div>
                  <h2 className="h4 mb-1">Order Workspace</h2>

                  <p className="mb-0 text-secondary">
                    Signed in as <strong>{accounts[0]?.username}</strong>
                  </p>
                </div>

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
          </div>
        )}
      </main>

      <AppFooter />
    </div>
  );
}

export default App;
