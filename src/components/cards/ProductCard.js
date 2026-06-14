import { renderProductBadge } from "../ui/ProductBadge.js";
import { renderPriceTag } from "../ui/PriceTag.js";
import { renderPrimaryButton } from "../ui/PrimaryButton.js";

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

export function renderProductCard(product) {
  const stockLabels = {
    in_stock: "Tersedia",
    low_stock: `Stok terbatas: ${product.stock}`,
    out_of_stock: "Stok habis",
  };
  return `
    <article class="mf-product-card mf-card">
      <a class="mf-product-card__media" href="/marketplace/product/${escapeHtml(product.slug)}" tabindex="-1" aria-hidden="true">
        <img src="${escapeHtml(product.image)}" alt="" loading="lazy" width="640" height="420">
      </a>
      <div class="mf-product-card__body">
        <div class="mf-product-card__badges">
          ${renderProductBadge(escapeHtml(product.badge))}
          ${product.featured ? '<span class="mf-badge mf-badge--blue">Featured</span>' : ""}
        </div>
        <div class="mf-stack">
          <p class="mf-product-card__category">${escapeHtml(product.category.name)}</p>
          <h3>${escapeHtml(product.name)}</h3>
          <p>${escapeHtml(product.shortDescription)}</p>
        </div>
        <span class="mf-stock mf-stock--${escapeHtml(product.stockStatus)}">${escapeHtml(stockLabels[product.stockStatus] || "Cek stok")}</span>
        ${renderPriceTag(product.price)}
        ${renderPrimaryButton({ label: "Lihat detail", href: `/marketplace/product/${escapeHtml(product.slug)}` })}
      </div>
    </article>
  `;
}
