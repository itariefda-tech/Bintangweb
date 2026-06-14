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
    message: "Respons server tidak dapat dibaca.",
  }));

  if (!response.ok) {
    const error = new Error(payload.message || "Request autentikasi gagal.");
    error.status = response.status;
    error.errors = payload.errors || {};
    throw error;
  }
  return payload.data || {};
}

export async function getCurrentSession() {
  try {
    return await request("/api/v1/auth/me", { method: "GET", headers: {} });
  } catch (error) {
    if (error.status === 401) return null;
    throw error;
  }
}

export function registerMember({ name, email, password }) {
  return request("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

export function loginMember({ email, password }) {
  return request("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function logoutMember(csrfToken) {
  return request("/api/v1/auth/logout", {
    method: "POST",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify({}),
  });
}

export async function getMemberProfile() {
  const data = await request("/api/v1/member/profile", {
    method: "GET",
    headers: {},
  });
  return data.profile;
}

export async function updateMemberProfile(profile, csrfToken) {
  const data = await request("/api/v1/member/profile", {
    method: "PUT",
    headers: { "X-CSRF-Token": csrfToken },
    body: JSON.stringify(profile),
  });
  return data.profile;
}
