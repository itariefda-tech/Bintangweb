export function renderMemberDashboardCard(item) {
  return `
    <a class="mf-dashboard-card mf-card" href="${item.href}">
      <span class="mf-dashboard-card__index">${item.index}</span>
      <div><h3>${item.title}</h3><p>${item.description}</p></div>
      <span aria-hidden="true">Open</span>
    </a>
  `;
}
