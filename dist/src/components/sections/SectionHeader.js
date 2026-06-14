export function renderSectionHeader({ eyebrow, title, description = "" }) {
  return `
    <header class="mf-section-header">
      <p class="mf-eyebrow">${eyebrow}</p>
      <h2>${title}</h2>
      ${description ? `<p>${description}</p>` : ""}
    </header>
  `;
}
