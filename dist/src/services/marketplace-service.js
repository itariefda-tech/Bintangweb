async function request(path) {
  const response = await fetch(path, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  const payload = await response.json().catch(() => ({
    success: false,
    message: "Respons katalog tidak dapat dibaca.",
  }));
  if (!response.ok) {
    const error = new Error(payload.message || "Katalog tidak dapat dimuat.");
    error.status = response.status;
    throw error;
  }
  return payload.data || {};
}

export async function getCategories() {
  const data = await request("/api/v1/categories");
  return data.categories || [];
}

export async function getProducts(filters = {}) {
  const query = new URLSearchParams();
  if (filters.search) query.set("search", filters.search);
  if (filters.category) query.set("category", filters.category);
  if (filters.featured) query.set("featured", "1");
  if (filters.sort) query.set("sort", filters.sort);
  const data = await request(`/api/v1/products?${query}`);
  return data.products || [];
}

export async function getProduct(slug) {
  const data = await request(`/api/v1/products/${encodeURIComponent(slug)}`);
  return data.product;
}
