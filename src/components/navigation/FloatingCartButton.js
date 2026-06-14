export function renderFloatingCartButton(count = 0, session = null) {
  const href = session ? "/checkout" : "/login?next=/checkout";
  return `
    <a class="mf-floating-cart" href="${href}" aria-label="Buka cart, ${count} item">
      <span aria-hidden="true">Cart</span>
      <strong data-cart-count>${count}</strong>
    </a>
  `;
}
