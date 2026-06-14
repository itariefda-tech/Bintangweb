export function renderConsultationTicketCard(ticket) {
  return `
    <article class="mf-ticket-card mf-card">
      <div class="mf-ticket-card__top">
        <span class="mf-badge mf-badge--blue">${ticket.status}</span>
        <small>${ticket.number}</small>
      </div>
      <h3>${ticket.subject}</h3>
      <p>${ticket.summary}</p>
      <div class="mf-ticket-card__meta"><span>${ticket.category}</span><span>${ticket.updatedAt}</span></div>
    </article>
  `;
}
