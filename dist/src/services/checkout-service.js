async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({
    success: false,
    message: "Respons checkout tidak dapat dibaca.",
  }));
  if (!response.ok) {
    const error = new Error(payload.message || "Request checkout gagal.");
    error.status = response.status;
    error.errors = payload.errors || {};
    throw error;
  }
  return payload.data || {};
}

export async function getCart() {
  const data = await request("/api/v1/cart", { method: "GET", headers: {} });
  return data.cart;
}

export async function addCartItem(productSlug, qty, csrfToken) {
  const data = await request("/api/v1/cart/add", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify({ productSlug, qty }),
  });
  return data.cart;
}

export async function updateCartItem(itemId, qty, csrfToken) {
  const data = await request(`/api/v1/cart/items/${encodeURIComponent(itemId)}`, {
    method: "PUT",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify({ qty }),
  });
  return data.cart;
}

export async function removeCartItem(itemId, csrfToken) {
  const data = await request(`/api/v1/cart/items/${encodeURIComponent(itemId)}`, {
    method: "DELETE",
    headers: { "X-CSRF-Token": csrfToken },
  });
  return data.cart;
}

export async function getAddresses() {
  const data = await request("/api/v1/member/addresses", {
    method: "GET",
    headers: {},
  });
  return data.addresses || [];
}

export async function saveAddress(address, csrfToken) {
  const data = await request("/api/v1/member/addresses", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify(address),
  });
  return data.address;
}

export async function createOrder(checkout, csrfToken) {
  const data = await request("/api/v1/checkout", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify(checkout),
  });
  return data.order;
}

export async function getOrders() {
  const data = await request("/api/v1/member/orders", {
    method: "GET",
    headers: {},
  });
  return data.orders || [];
}
