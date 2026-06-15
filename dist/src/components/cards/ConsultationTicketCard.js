const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

export function renderConsultationTicketCard(ticket) {
  return `
    <article class="mf-ticket-card mf-card">
      <div class="mf-ticket-card__top">
        <span class="mf-badge mf-badge--blue">${escapeHtml(ticket.status)}</span>
        <small>${escapeHtml(ticket.number)}</small>
      </div>
      <h3>${escapeHtml(ticket.subject)}</h3>
      <p>${escapeHtml(ticket.summary)}</p>
      <div class="mf-ticket-card__meta"><span>${escapeHtml(ticket.category)}</span><span>${escapeHtml(ticket.updatedAt)}</span></div>
    </article>
  `;
}
