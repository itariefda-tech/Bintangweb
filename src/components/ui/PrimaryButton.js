export function renderPrimaryButton({ label, href = "#", variant = "primary" }) {
  return `<a class="mf-button mf-button--${variant}" href="${href}">${label}</a>`;
}
