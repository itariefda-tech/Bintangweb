const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

export function renderNewsCard(article) {
  const category = article.category?.name || article.category || "News";
  return `
    <article class="mf-news-card mf-card">
      <img src="${escapeHtml(article.image)}" alt="" loading="lazy" width="640" height="400">
      <div class="mf-news-card__body">
        <div class="mf-news-card__meta"><span class="mf-badge mf-badge--blue">${escapeHtml(category)}</span><span>${escapeHtml(article.readingTime)}</span></div>
        <h3>${escapeHtml(article.title)}</h3>
        <p>${escapeHtml(article.excerpt)}</p>
        <a class="mf-text-link" href="/news/${encodeURIComponent(article.slug)}">Baca artikel</a>
      </div>
    </article>
  `;
}
