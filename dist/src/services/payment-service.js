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
    message: "Respons payment tidak dapat dibaca.",
  }));
  if (!response.ok) {
    const error = new Error(payload.message || "Request payment gagal.");
    error.status = response.status;
    error.errors = payload.errors || {};
    throw error;
  }
  return payload.data || {};
}

export async function createPayment(orderId, method, bank, csrfToken) {
  return request("/api/v1/payment/create", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify({ orderId, method, bank }),
  });
}

export async function getOrderPayments(orderId) {
  const data = await request(
    `/api/v1/payments?orderId=${encodeURIComponent(orderId)}`,
    { method: "GET", headers: {} },
  );
  return data.payments || [];
}
