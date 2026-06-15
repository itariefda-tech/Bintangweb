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
    message: "Respons konsultasi tidak dapat dibaca.",
  }));
  if (!response.ok) {
    const error = new Error(payload.message || "Request konsultasi gagal.");
    error.status = response.status;
    error.errors = payload.errors || {};
    throw error;
  }
  return payload.data || {};
}

export async function getConsultationTickets() {
  const data = await request("/api/v1/member/consultation", {
    method: "GET",
    headers: {},
  });
  return data.tickets || [];
}

export async function createConsultationTicket(ticket, csrfToken) {
  const data = await request("/api/v1/member/consultation", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify(ticket),
  });
  return data.ticket;
}

export async function replyConsultationTicket(ticketId, message, csrfToken) {
  const data = await request(`/api/v1/member/consultation/${encodeURIComponent(ticketId)}/replies`, {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify({ message }),
  });
  return data.ticket;
}
