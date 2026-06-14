import { renderProductBadge } from "../ui/ProductBadge.js";
import { renderPriceTag } from "../ui/PriceTag.js";
import { renderPrimaryButton } from "../ui/PrimaryButton.js";

export function renderProductCard(product) {
  return `
    <article class="mf-product-card mf-card">
      <a class="mf-product-card__media" href="/marketplace/product/${product.slug}" tabindex="-1" aria-hidden="true">
        <img src="${product.image}" alt="" loading="lazy" width="640" height="420">
      </a>
      <div class="mf-product-card__body">
        ${renderProductBadge(product.badge)}
        <div class="mf-stack">
          <h3>${product.name}</h3>
          <p>${product.shortDescription}</p>
        </div>
        ${renderPriceTag(product.price)}
        ${renderPrimaryButton({ label: "Lihat detail", href: `/marketplace/product/${product.slug}` })}
      </div>
    </article>
  `;
}
