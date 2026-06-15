async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: "same-origin",
    ...options,
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({
    success: false,
    message: "Respons admin tidak dapat dibaca.",
  }));
  if (!response.ok) {
    const error = new Error(payload.message || "Request admin gagal.");
    error.status = response.status;
    error.errors = payload.errors || {};
    throw error;
  }
  return payload.data || {};
}

export async function getAdminKpis() {
  const data = await request("/api/v1/admin/kpis");
  return data.kpis;
}

export async function getAdminConsultations(status = "") {
  const query = new URLSearchParams();
  if (status) query.set("status", status);
  const data = await request(`/api/v1/admin/consultation${query.size ? `?${query}` : ""}`);
  return data.tickets || [];
}

export async function replyAdminConsultation(ticketId, message, csrfToken) {
  const data = await request(
    `/api/v1/admin/consultation/${encodeURIComponent(ticketId)}/replies`,
    {
      method: "POST",
      headers: { "X-CSRF-Token": csrfToken },
      body: JSON.stringify({ message }),
    },
  );
  return data.ticket;
}

export async function updateAdminConsultationStatus(ticketId, status, csrfToken) {
  const data = await request(
    `/api/v1/admin/consultation/${encodeURIComponent(ticketId)}/status`,
    {
      method: "PUT",
      headers: { "X-CSRF-Token": csrfToken },
      body: JSON.stringify({ status }),
    },
  );
  return data.ticket;
}

export async function getAdminOrders(filters = {}) {
  const query = new URLSearchParams();
  if (filters.paymentStatus) query.set("paymentStatus", filters.paymentStatus);
  if (filters.orderStatus) query.set("orderStatus", filters.orderStatus);
  const data = await request(`/api/v1/admin/orders${query.size ? `?${query}` : ""}`);
  return data.orders || [];
}

export async function getAdminOrder(orderId) {
  const data = await request(`/api/v1/admin/orders/${encodeURIComponent(orderId)}`);
  return data.order;
}

export async function updateAdminOrderFulfillment(orderId, status, csrfToken) {
  const data = await request(
    `/api/v1/admin/orders/${encodeURIComponent(orderId)}/fulfillment`,
    {
      method: "PUT",
      headers: { "X-CSRF-Token": csrfToken },
      body: JSON.stringify({ status }),
    },
  );
  return data.order;
}

export async function getAdminProducts() {
  const data = await request("/api/v1/admin/products");
  return data.products || [];
}

export async function saveAdminProduct(product, csrfToken, productId = "") {
  const data = await request(
    productId
      ? `/api/v1/admin/products/${encodeURIComponent(productId)}`
      : "/api/v1/admin/products",
    {
      method: productId ? "PUT" : "POST",
      headers: { "X-CSRF-Token": csrfToken },
      body: JSON.stringify(product),
    },
  );
  return data.product;
}

export async function archiveAdminProduct(productId, csrfToken) {
  const data = await request(`/api/v1/admin/products/${encodeURIComponent(productId)}`, {
    method: "DELETE",
    headers: { "X-CSRF-Token": csrfToken },
  });
  return data.product;
}

export async function uploadAdminProductImage(file, csrfToken) {
  const dataUrl = await new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.addEventListener("load", () => resolve(reader.result));
    reader.addEventListener("error", () => reject(new Error("Gambar tidak dapat dibaca.")));
    reader.readAsDataURL(file);
  });
  const data = await request("/api/v1/admin/products/upload", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify({ data: dataUrl }),
  });
  return data.url;
}
