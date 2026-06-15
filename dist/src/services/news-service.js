async function request(path) {
  const response = await fetch(path, {
    method: "GET",
    credentials: "same-origin",
    headers: { Accept: "application/json" },
  });
  const payload = await response.json().catch(() => ({
    success: false,
    message: "Respons news tidak dapat dibaca.",
  }));
  if (!response.ok) {
    const error = new Error(payload.message || "News tidak dapat dimuat.");
    error.status = response.status;
    throw error;
  }
  return payload.data || {};
}

export async function getNewsArticles(filters = {}) {
  const query = new URLSearchParams();
  if (filters.search) query.set("search", filters.search);
  if (filters.category) query.set("category", filters.category);
  if (filters.featured) query.set("featured", "1");
  if (filters.trending) query.set("trending", "1");
  const data = await request(`/api/v1/news?${query}`);
  return data.articles || [];
}

export async function getNewsCategories() {
  const data = await request("/api/v1/news/categories");
  return data.categories || [];
}

export async function getNewsArticle(slug) {
  const data = await request(`/api/v1/news/${encodeURIComponent(slug)}`);
  return data.article;
}
