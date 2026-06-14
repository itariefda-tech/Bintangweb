export function renderPriceTag(value, suffix = "") {
  return `<p class="mf-price"><span>Mulai</span><strong>${new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value)}</strong>${suffix ? `<small>${suffix}</small>` : ""}</p>`;
}
