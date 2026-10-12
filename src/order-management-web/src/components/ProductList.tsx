import type { Product } from "../types/product";

type Props = {
  products: Product[];
  onAdd: (product: Product) => void;
};

export function ProductList({ products, onAdd }: Props) {
  if (products.length === 0) {
    return null;
  }

  return (
    <section className="mt-4">
      <h2 className="mb-3">Products</h2>

      <div className="table-responsive">
        <table className="table table-striped table-hover align-middle">
          <thead className="table-light">
            <tr>
              <th>SKU</th>
              <th>Name</th>
              <th>Description</th>
              <th>Price</th>
              <th></th>
            </tr>
          </thead>

          <tbody>
            {products.map((product) => (
              <tr key={product.id}>
                <td>{product.sku}</td>

                <td>
                  <strong>{product.name}</strong>
                </td>

                <td>{product.description ?? "-"}</td>

                <td>${product.price.toFixed(2)}</td>

                <td className="text-end">
                  <button
                    className="btn btn-sm btn-success"
                    onClick={() => onAdd(product)}
                  >
                    Add to Cart
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
