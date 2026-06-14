export function renderNewsCard(article) {
  return `
    <article class="mf-news-card mf-card">
      <img src="${article.image}" alt="" loading="lazy" width="640" height="400">
      <div class="mf-news-card__body">
        <div class="mf-news-card__meta"><span class="mf-badge mf-badge--blue">${article.category}</span><span>${article.readingTime}</span></div>
        <h3>${article.title}</h3>
        <p>${article.excerpt}</p>
        <span class="mf-text-link">Article placeholder</span>
      </div>
    </article>
  `;
}
