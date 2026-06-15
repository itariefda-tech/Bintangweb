import { renderMarketplaceLayout } from "../layouts/MarketplaceLayout.js";
import { bindSiteHeader } from "../components/navigation/SiteHeader.js";
import { renderProductCard } from "../components/cards/ProductCard.js";
import { renderMemberDashboardCard } from "../components/cards/MemberDashboardCard.js";
import { renderConsultationTicketCard } from "../components/cards/ConsultationTicketCard.js";
import { renderNewsCard } from "../components/cards/NewsCard.js";
import { renderPrimaryButton } from "../components/ui/PrimaryButton.js";
import { renderPriceTag } from "../components/ui/PriceTag.js";
import { renderProductBadge } from "../components/ui/ProductBadge.js";
import { renderSectionHeader } from "../components/sections/SectionHeader.js";
import { marketplaceConfig } from "../config/marketplace.js";
import {
  getCurrentSession,
  getMemberNotifications,
  getMemberProfile,
  loginMember,
  logoutMember,
  markMemberNotificationsRead,
  registerMember,
  requestPasswordReset,
  resetMemberPassword,
  updateMemberProfile,
  uploadMemberAvatar,
} from "../services/auth-service.js";
import {
  mockDashboardItems,
} from "../modules/marketplace/data/mock-marketplace.js";
import {
  getCategories,
  getProduct,
  getProducts,
} from "../services/marketplace-service.js";
import {
  addCartItem,
  createOrder,
  getAddresses,
  getCart,
  getOrders,
  removeCartItem,
  saveAddress,
  updateCartItem,
} from "../services/checkout-service.js";
import {
  createPayment,
  getOrderPayments,
} from "../services/payment-service.js";
import {
  createConsultationTicket,
  getConsultationTickets,
  replyConsultationTicket,
} from "../services/consultation-service.js";
import {
  getNewsArticle,
  getNewsArticles,
  getNewsCategories,
} from "../services/news-service.js";
import {
  archiveAdminProduct,
  getAdminConsultations,
  getAdminKpis,
  getAdminOrder,
  getAdminOrders,
  getAdminProducts,
  replyAdminConsultation,
  saveAdminProduct,
  updateAdminOrderFulfillment,
  updateAdminConsultationStatus,
  uploadAdminProductImage,
} from "../services/admin-service.js";

let adminProductCache = [];

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const formatIdr = (value) =>
  new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(Number(value) || 0);

function getRoute() {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  if (path.startsWith("/marketplace/product/")) return "product";
  if (path.startsWith("/news/")) return "article";
  return marketplaceConfig.routes[path] || "not-found";
}

function currentCatalogFilters() {
  const query = new URLSearchParams(window.location.search);
  return {
    search: query.get("search") || "",
    category: query.get("category") || "",
    featured: query.get("featured") === "1",
    sort: query.get("sort") || "featured",
  };
}

function currentNewsFilters() {
  const query = new URLSearchParams(window.location.search);
  return {
    search: query.get("search") || "",
    category: query.get("category") || "",
    featured: query.get("featured") === "1",
    trending: query.get("trending") === "1",
  };
}

function currentAdminConsultationStatus() {
  return new URLSearchParams(window.location.search).get("status") || "";
}

function currentAdminOrderFilters() {
  const query = new URLSearchParams(window.location.search);
  return {
    paymentStatus: query.get("paymentStatus") || "",
    orderStatus: query.get("orderStatus") || "",
  };
}

function renderMarketplace(_session, catalog) {
  const { products = [], categories = [], filters = {} } = catalog || {};
  const featuredProduct = products.find((product) => product.featured) || products[0];
  return `
    <section class="mf-hero mf-section">
      <div class="mf-container mf-hero__grid">
        <div class="mf-stack mf-stack--lg">
          <p class="mf-eyebrow">Feira Mini Marketplace</p>
          <h1>Perangkat IT pilihan, dengan arahan yang lebih manusiawi.</h1>
          <p class="mf-lead">Katalog teknologi terkurasi untuk kebutuhan kerja, bisnis, jaringan, keamanan, dan solusi digital.</p>
          <div class="mf-action-row">
            ${renderPrimaryButton({ label: "Jelajahi produk", href: "#produk" })}
            ${renderPrimaryButton({ label: "Konsultasi kebutuhan", href: "/member/consultation", variant: "secondary" })}
          </div>
          <p class="mf-demo-note">${products.length} produk aktif dari ${categories.length} kategori.</p>
        </div>
        <div class="mf-hero__visual" aria-hidden="true">
          <span class="mf-hero__orb"></span>
          <div class="mf-hero__panel">
            <span>Curated technology</span>
            <strong>Built around your workflow.</strong>
          </div>
        </div>
      </div>
    </section>
    ${featuredProduct ? `
      <section class="mf-market-banner">
        <div class="mf-container mf-market-banner__inner">
          <div>
            <p class="mf-eyebrow">Featured solution</p>
            <h2>${escapeHtml(featuredProduct.name)}</h2>
            <p>${escapeHtml(featuredProduct.shortDescription)}</p>
          </div>
          ${renderPrimaryButton({ label: "Lihat pilihan featured", href: "/marketplace?featured=1#produk", variant: "secondary" })}
        </div>
      </section>
    ` : ""}
    <section class="mf-section" id="produk">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Katalog awal",
          title: "Pilihan teknologi untuk fondasi kerja yang solid.",
          description: "Cari berdasarkan kebutuhan, pilih kategori, dan urutkan katalog dengan cepat.",
        })}
        <form class="mf-catalog-tools mf-card" data-catalog-filter>
          <label class="mf-field">Cari produk
            <input type="search" name="search" value="${escapeHtml(filters.search)}" placeholder="Laptop, network, CCTV...">
          </label>
          <label class="mf-field">Kategori
            <select name="category">
              <option value="">Semua kategori</option>
              ${categories.map((category) => `<option value="${escapeHtml(category.slug)}"${filters.category === category.slug ? " selected" : ""}>${escapeHtml(category.name)} (${category.productCount})</option>`).join("")}
            </select>
          </label>
          <label class="mf-field">Urutkan
            <select name="sort">
              <option value="featured"${filters.sort === "featured" ? " selected" : ""}>Featured</option>
              <option value="newest"${filters.sort === "newest" ? " selected" : ""}>Terbaru</option>
              <option value="price_asc"${filters.sort === "price_asc" ? " selected" : ""}>Harga terendah</option>
              <option value="price_desc"${filters.sort === "price_desc" ? " selected" : ""}>Harga tertinggi</option>
              <option value="name"${filters.sort === "name" ? " selected" : ""}>Nama A-Z</option>
            </select>
          </label>
          <label class="mf-featured-toggle">
            <input type="checkbox" name="featured" value="1"${filters.featured ? " checked" : ""}>
            Featured saja
          </label>
          <button class="mf-button mf-button--primary" type="submit">Terapkan filter</button>
          <a class="mf-button mf-button--secondary" href="/marketplace#produk">Reset</a>
        </form>
        <p class="mf-catalog-count">${products.length} produk ditemukan.</p>
        ${products.length ? `<div class="mf-grid mf-grid--products">${products.map(renderProductCard).join("")}</div>` : `
          <div class="mf-empty-state mf-card">
            <h3>Produk belum ditemukan.</h3>
            <p>Coba kata kunci atau kategori lain.</p>
          </div>
        `}
      </div>
    </section>
  `;
}

function renderProductDetail(session, product) {
  if (!product) {
    return renderEmptyState("404", "Produk tidak ditemukan.", "Produk mungkin sudah tidak aktif.", "/marketplace", "Kembali ke katalog");
  }
  const stockLabels = {
    in_stock: `${product.stock} unit tersedia`,
    low_stock: `Stok terbatas, tersisa ${product.stock}`,
    out_of_stock: "Stok sedang habis",
  };
  return `
    <section class="mf-section">
      <div class="mf-container mf-product-detail">
        <div class="mf-product-gallery" data-product-gallery>
          <div class="mf-product-detail__media">
            <img src="${escapeHtml(product.images[0])}" alt="${escapeHtml(product.name)}" data-gallery-main>
          </div>
          <div class="mf-product-gallery__thumbs" aria-label="Galeri produk">
            ${product.images.map((image, index) => `
              <button type="button" data-gallery-image="${escapeHtml(image)}"${index === 0 ? ' aria-current="true"' : ""}>
                <img src="${escapeHtml(image)}" alt="Tampilan ${index + 1} ${escapeHtml(product.name)}">
              </button>
            `).join("")}
          </div>
        </div>
        <div class="mf-stack mf-stack--lg">
          <p class="mf-eyebrow">${escapeHtml(product.category.name)}</p>
          <h1>${escapeHtml(product.name)}</h1>
          <p class="mf-lead">${escapeHtml(product.description)}</p>
          <div class="mf-action-row">
            ${renderProductBadge(escapeHtml(product.badge))}
            ${product.featured ? '<span class="mf-badge mf-badge--blue">Featured</span>' : ""}
          </div>
          ${renderPriceTag(product.price)}
          <div class="mf-notice">${escapeHtml(stockLabels[product.stockStatus])}</div>
          ${product.stockStatus === "out_of_stock" ? "" : session ? `
            <form class="mf-add-cart" data-add-cart="${escapeHtml(product.slug)}">
              <label class="mf-field">Jumlah
                <input type="number" name="qty" min="1" max="${product.stock}" value="1" required>
              </label>
              <button class="mf-button mf-button--primary" type="submit">Tambah ke cart</button>
              <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
            </form>
          ` : renderPrimaryButton({ label: "Login untuk membeli", href: `/login?next=/marketplace/product/${escapeHtml(product.slug)}` })}
          ${renderPrimaryButton({ label: "Kembali ke marketplace", href: "/marketplace" })}
        </div>
      </div>
    </section>
    <section class="mf-section mf-related-products">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Related product",
          title: "Pilihan lain dalam kategori yang sama.",
          description: product.related.length ? "Bandingkan solusi sebelum menentukan kebutuhan." : "Belum ada produk terkait lain pada kategori ini.",
        })}
        ${product.related.length ? `<div class="mf-grid mf-grid--products">${product.related.map(renderProductCard).join("")}</div>` : ""}
      </div>
    </section>
  `;
}

function renderAuth(type) {
  const isLogin = type === "login";
  const approvalNotice = isLogin
    && new URLSearchParams(window.location.search).get("registered") === "1"
    ? "Registrasi berhasil. Silakan tunggu persetujuan owner sebelum login."
    : "";
  return `
    <section class="mf-section">
      <div class="mf-container mf-auth-wrap">
        <div class="mf-auth-card mf-card">
          ${renderSectionHeader({
            eyebrow: "Member foundation",
            title: isLogin ? "Selamat datang kembali." : "Mulai ekosistem Feira.",
            description: isLogin
              ? "Masuk dengan session aman untuk membuka area member."
              : "Buat akun member untuk mengakses order dan consultation foundation.",
          })}
          <form class="mf-form" data-auth-form="${type}" novalidate>
            ${isLogin ? "" : '<label class="mf-field">Nama lengkap<input type="text" name="name" autocomplete="name" minlength="2" maxlength="120" required placeholder="Nama Anda"><small data-field-error="name"></small></label>'}
            <label class="mf-field">Email<input type="email" name="email" autocomplete="email" maxlength="254" required placeholder="nama@perusahaan.com"><small data-field-error="email"></small></label>
            <label class="mf-field">Password<input type="password" name="password" autocomplete="${isLogin ? "current-password" : "new-password"}" minlength="8" maxlength="128" required placeholder="Minimum 8 karakter"><small data-field-error="password"></small></label>
            <button class="mf-button mf-button--primary" type="submit">${isLogin ? "Masuk ke member area" : "Buat akun member"}</button>
            <p class="mf-form-status" data-form-status role="status" aria-live="polite"${approvalNotice ? ' data-state="success"' : ""}>${approvalNotice}</p>
          </form>
          <p class="mf-form-help">${isLogin ? 'Belum punya akun? <a href="/register">Daftar member</a>. <a href="/forgot-password">Lupa password?</a>' : 'Sudah terdaftar? <a href="/login">Masuk di sini</a>.'}</p>
        </div>
      </div>
    </section>
  `;
}

function renderPasswordRecovery(type) {
  const isReset = type === "reset";
  const hasToken = new URLSearchParams(window.location.search).has("token");
  return `
    <section class="mf-section">
      <div class="mf-container mf-auth-wrap">
        <div class="mf-auth-card mf-card">
          ${renderSectionHeader({
            eyebrow: "Account recovery",
            title: isReset ? "Buat password baru." : "Pulihkan akses akun.",
            description: isReset
              ? "Password baru akan menghentikan seluruh sesi lama."
              : "Masukkan email akun. Instruksi akan dikirim jika email terdaftar.",
          })}
          ${isReset && !hasToken ? '<div class="mf-notice">Link reset password tidak memiliki token.</div>' : `
            <form class="mf-form" data-recovery-form="${type}" novalidate>
              ${isReset
                ? '<label class="mf-field">Password baru<input type="password" name="password" autocomplete="new-password" minlength="8" maxlength="128" required placeholder="Minimum 8 karakter"><small data-field-error="password"></small></label>'
                : '<label class="mf-field">Email<input type="email" name="email" autocomplete="email" maxlength="254" required placeholder="nama@perusahaan.com"><small data-field-error="email"></small></label>'}
              <button class="mf-button mf-button--primary" type="submit">${isReset ? "Perbarui password" : "Kirim instruksi reset"}</button>
              <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
            </form>
          `}
          <p class="mf-form-help"><a href="/login">Kembali ke login</a>.</p>
        </div>
      </div>
    </section>
  `;
}

function renderMember(session, _profile, notifications) {
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Member area",
          title: `Halo, ${escapeHtml(session.user.name)}.`,
          description: `Session member aktif dengan role ${escapeHtml(session.user.role)}. Anda memiliki ${notifications?.unreadCount || 0} notifikasi belum dibaca.`,
        })}
        <div class="mf-grid mf-grid--dashboard">
          ${mockDashboardItems.map(renderMemberDashboardCard).join("")}
        </div>
      </div>
    </section>
  `;
}

function renderProfile(profile) {
  const avatar = profile.avatarUrl
    ? `<img src="${escapeHtml(profile.avatarUrl)}" alt="Avatar ${escapeHtml(profile.name)}">`
    : escapeHtml(profile.name.slice(0, 1).toUpperCase());
  return `
    <section class="mf-section">
      <div class="mf-container mf-profile-layout">
        <aside class="mf-profile-summary mf-card">
          <span class="mf-profile-summary__avatar">${avatar}</span>
          <div>
            <p class="mf-eyebrow">Member profile</p>
            <h2>${escapeHtml(profile.name)}</h2>
            <p>${escapeHtml(profile.email)}</p>
            <span class="mf-badge">${escapeHtml(profile.role)}</span>
          </div>
          <form class="mf-avatar-form" data-avatar-form>
            <label class="mf-field">Avatar JPG, PNG, atau WebP
              <input type="file" name="avatar" accept="image/jpeg,image/png,image/webp" required>
              <small>Maksimal 2MB.</small>
            </label>
            <button class="mf-button mf-button--secondary" type="submit">Upload avatar</button>
            <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
          </form>
        </aside>
        <div class="mf-profile-panel mf-card">
          ${renderSectionHeader({
            eyebrow: "Profile settings",
            title: "Lengkapi konteks kerja Anda.",
            description: "Informasi ini disimpan privat dan akan membantu flow konsultasi serta checkout pada phase berikutnya.",
          })}
          <form class="mf-form" data-profile-form novalidate>
            <div class="mf-form-grid">
              <label class="mf-field">Nama lengkap<input type="text" name="name" autocomplete="name" minlength="2" maxlength="120" required value="${escapeHtml(profile.name)}"><small data-field-error="name"></small></label>
              <label class="mf-field">Email<input type="email" autocomplete="email" readonly value="${escapeHtml(profile.email)}"><small>Email tidak dapat diubah pada stage ini.</small></label>
              <label class="mf-field">Nomor telepon<input type="tel" name="phone" autocomplete="tel" maxlength="24" value="${escapeHtml(profile.phone)}" placeholder="+62 812 3456 7890"><small data-field-error="phone"></small></label>
              <label class="mf-field">Perusahaan<input type="text" name="companyName" autocomplete="organization" maxlength="120" value="${escapeHtml(profile.companyName)}" placeholder="Nama perusahaan"><small data-field-error="companyName"></small></label>
              <label class="mf-field">Jabatan<input type="text" name="jobTitle" autocomplete="organization-title" maxlength="120" value="${escapeHtml(profile.jobTitle)}" placeholder="Jabatan atau peran"><small data-field-error="jobTitle"></small></label>
              <label class="mf-field">Kota<input type="text" name="city" autocomplete="address-level2" maxlength="100" value="${escapeHtml(profile.city)}" placeholder="Kota"><small data-field-error="city"></small></label>
              <label class="mf-field">Provinsi<input type="text" name="province" autocomplete="address-level1" maxlength="100" value="${escapeHtml(profile.province)}" placeholder="Provinsi"><small data-field-error="province"></small></label>
              <label class="mf-field">Kode pos<input type="text" name="postalCode" autocomplete="postal-code" maxlength="12" value="${escapeHtml(profile.postalCode)}" placeholder="Kode pos"><small data-field-error="postalCode"></small></label>
              <label class="mf-field mf-field--wide">Alamat<textarea name="address" autocomplete="street-address" maxlength="300" rows="3" placeholder="Alamat untuk kebutuhan layanan mendatang">${escapeHtml(profile.address)}</textarea><small data-field-error="address"></small></label>
              <label class="mf-field mf-field--wide">Bio singkat<textarea name="bio" maxlength="600" rows="4" placeholder="Ceritakan kebutuhan atau konteks teknologi Anda">${escapeHtml(profile.bio)}</textarea><small data-field-error="bio"></small></label>
            </div>
            <div class="mf-profile-actions">
              <button class="mf-button mf-button--primary" type="submit">Simpan profile</button>
              <a class="mf-button mf-button--secondary" href="/member">Kembali ke dashboard</a>
            </div>
            <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
          </form>
        </div>
      </div>
    </section>
  `;
}

function renderNotifications(_session, _profile, notifications) {
  const items = notifications?.items || [];
  return `
    <section class="mf-section">
      <div class="mf-container">
        <div class="mf-notification-heading">
          ${renderSectionHeader({
            eyebrow: "Notification center",
            title: "Update akun dalam satu tempat.",
            description: `${notifications?.unreadCount || 0} notifikasi belum dibaca.`,
          })}
          ${items.length ? '<button class="mf-button mf-button--secondary" type="button" data-read-all>Tandai semua dibaca</button>' : ""}
        </div>
        <div class="mf-notification-list">
          ${items.length ? items.map((item) => `
            <article class="mf-notification-item mf-card${item.read ? "" : " is-unread"}">
              <div>
                <span class="mf-badge">${escapeHtml(item.kind)}</span>
                <h3>${escapeHtml(item.title)}</h3>
                <p>${escapeHtml(item.message)}</p>
              </div>
              <div class="mf-notification-actions">
                ${item.actionUrl ? `<a class="mf-text-link" href="${escapeHtml(item.actionUrl)}">Buka</a>` : ""}
                ${item.read ? "" : `<button type="button" data-read-notification="${escapeHtml(item.id)}">Tandai dibaca</button>`}
              </div>
            </article>
          `).join("") : '<div class="mf-empty-state mf-card"><p>Belum ada notifikasi.</p></div>'}
        </div>
      </div>
    </section>
  `;
}

function renderOrders(_session, orders) {
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Order history",
          title: "Invoice dan perjalanan order Anda.",
          description: `${orders?.length || 0} order tercatat.`,
        })}
        <div class="mf-order-list">
          ${(orders || []).length ? orders.map((order) => {
            const payment = order.payments?.[0];
            return `
            <article class="mf-order-card mf-card">
              <div class="mf-order-card__heading"><span class="mf-badge">${escapeHtml(order.orderStatus)}</span><h3>${escapeHtml(order.invoiceNumber)}</h3><strong>${formatIdr(order.grandTotal)}</strong></div>
              ${payment ? `
                <div class="mf-payment-instruction">
                  <div><span>Metode</span><strong>${escapeHtml(payment.method === "qris" ? "QRIS" : `${payment.bank.toUpperCase()} Virtual Account`)}</strong></div>
                  <div><span>Status</span><strong>${escapeHtml(payment.status)}</strong></div>
                  ${payment.qrUrl ? `<img src="${escapeHtml(payment.qrUrl)}" alt="QR pembayaran ${escapeHtml(order.invoiceNumber)}">` : ""}
                  ${payment.vaNumber ? `<div class="mf-va-number"><span>Nomor Virtual Account</span><strong>${escapeHtml(payment.vaNumber)}</strong></div>` : ""}
                  ${payment.status === "pending" ? '<p>Instruksi aktif. Status akan diperbarui otomatis melalui callback Midtrans.</p>' : ""}
                </div>
              ` : order.paymentStatus === "paid" ? "" : `
                <form class="mf-payment-form" data-payment-form="${escapeHtml(order.id)}">
                  <label class="mf-field">Metode pembayaran
                    <select name="method" data-payment-method>
                      <option value="qris">QRIS</option>
                      <option value="bank_transfer">Bank transfer / VA</option>
                    </select>
                  </label>
                  <label class="mf-field" data-payment-bank hidden>Bank
                    <select name="bank" disabled>
                      <option value="bca">BCA</option>
                      <option value="bni">BNI</option>
                      <option value="bri">BRI</option>
                      <option value="permata">Permata</option>
                    </select>
                  </label>
                  <button class="mf-button mf-button--primary" type="submit">Buat instruksi pembayaran</button>
                  <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
                </form>
              `}
            </article>
          `}).join("") : '<div class="mf-empty-state mf-card"><p>Belum ada order.</p><a class="mf-text-link" href="/marketplace">Mulai dari katalog</a></div>'}
        </div>
      </div>
    </section>
  `;
}

function formatTimestamp(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("id-ID", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(Number(value) * 1000));
}

function renderConsultation(_session, tickets = []) {
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "IT consultation",
          title: "Percakapan teknis yang tetap terstruktur.",
          description: `${tickets.length} ticket konsultasi tersimpan. Buat ticket baru, pantau status, dan balas follow-up dari tim Feira.`,
        })}
        <div class="mf-consultation-layout">
          <section class="mf-card mf-consultation-form-card">
            <h2>Buat ticket konsultasi</h2>
            <form class="mf-form" data-consultation-form novalidate>
              <div class="mf-form-grid">
                <label class="mf-field mf-field--wide">Subject
                  <input name="subject" minlength="5" maxlength="160" required placeholder="Contoh: Audit jaringan kantor cabang">
                  <small data-field-error="subject"></small>
                </label>
                <label class="mf-field">Kategori
                  <select name="category">
                    <option value="Network">Network</option>
                    <option value="CCTV">CCTV</option>
                    <option value="Website">Website</option>
                    <option value="Custom Application">Custom Application</option>
                    <option value="Procurement">Procurement</option>
                  </select>
                  <small data-field-error="category"></small>
                </label>
                <label class="mf-field">Prioritas
                  <select name="priority">
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="urgent">Urgent</option>
                    <option value="low">Low</option>
                  </select>
                  <small data-field-error="priority"></small>
                </label>
                <label class="mf-field mf-field--wide">Kebutuhan
                  <textarea name="message" minlength="12" maxlength="4000" rows="5" required placeholder="Ceritakan kondisi saat ini, target, lokasi, dan kendala utama."></textarea>
                  <small data-field-error="message"></small>
                </label>
                <label class="mf-field mf-field--wide">Attachment pendukung
                  <input type="file" name="attachmentFile" accept="image/jpeg,image/png,application/pdf">
                  <small data-field-error="attachment">Opsional. JPG, PNG, atau PDF maksimal 5MB.</small>
                </label>
              </div>
              <button class="mf-button mf-button--primary" type="submit">Kirim ticket</button>
              <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
            </form>
          </section>
          <section class="mf-consultation-list">
            ${tickets.length ? tickets.map((ticket) => `
              <article class="mf-ticket-detail mf-card">
                ${renderConsultationTicketCard({
                  ...ticket,
                  updatedAt: formatTimestamp(ticket.updatedAt),
                })}
                <div class="mf-ticket-thread">
                  ${(ticket.replies || []).map((reply) => `
                    <div class="mf-ticket-reply" data-role="${escapeHtml(reply.authorRole)}">
                      <strong>${escapeHtml(reply.authorRole)}</strong>
                      <p>${escapeHtml(reply.message)}</p>
                      <small>${formatTimestamp(reply.createdAt)}</small>
                    </div>
                  `).join("")}
                </div>
                ${(ticket.attachments || []).length ? `
                  <div class="mf-ticket-attachments">
                    ${(ticket.attachments || []).map((attachment) => `
                      <a href="${escapeHtml(attachment.downloadUrl)}">${escapeHtml(attachment.filename)}</a>
                    `).join("")}
                  </div>
                ` : ""}
                ${ticket.status === "closed" ? "" : `
                  <form class="mf-ticket-reply-form" data-consultation-reply="${escapeHtml(ticket.id)}">
                    <label class="mf-field">Reply
                      <textarea name="message" minlength="2" maxlength="3000" rows="3" required placeholder="Tambahkan informasi atau jawab pertanyaan tim."></textarea>
                    </label>
                    <button class="mf-button mf-button--secondary" type="submit">Kirim reply</button>
                    <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
                  </form>
                `}
              </article>
            `).join("") : `
              <div class="mf-empty-state mf-card">
                <h3>Belum ada ticket konsultasi.</h3>
                <p>Mulai dari kebutuhan yang paling terasa hari ini. Tim akan menata konteksnya bersama Anda.</p>
              </div>
            `}
          </section>
        </div>
      </div>
    </section>
  `;
}

function renderNews(_session, newsData = {}) {
  const { articles = [], categories = [], filters = {} } = newsData || {};
  const featured = articles.find((article) => article.featured) || articles[0];
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Feira IT News",
          title: "Insight ringkas untuk keputusan teknologi yang lebih jernih.",
          description: `${articles.length} artikel tersedia dari ${categories.length} kategori.`,
        })}
        ${featured ? `
          <article class="mf-news-featured mf-card">
            <img src="${escapeHtml(featured.image)}" alt="" loading="lazy" width="960" height="540">
            <div>
              <span class="mf-badge mf-badge--blue">${escapeHtml(featured.category.name)}</span>
              <h2>${escapeHtml(featured.title)}</h2>
              <p>${escapeHtml(featured.excerpt)}</p>
              <a class="mf-button mf-button--primary" href="/news/${encodeURIComponent(featured.slug)}">Baca featured</a>
            </div>
          </article>
        ` : ""}
        <form class="mf-catalog-tools mf-card" data-news-filter>
          <label class="mf-field">Cari artikel
            <input type="search" name="search" value="${escapeHtml(filters.search)}" placeholder="Network, CCTV, website...">
          </label>
          <label class="mf-field">Kategori
            <select name="category">
              <option value="">Semua kategori</option>
              ${categories.map((category) => `<option value="${escapeHtml(category.slug)}"${filters.category === category.slug ? " selected" : ""}>${escapeHtml(category.name)} (${category.articleCount})</option>`).join("")}
            </select>
          </label>
          <label class="mf-featured-toggle">
            <input type="checkbox" name="featured" value="1"${filters.featured ? " checked" : ""}>
            Featured
          </label>
          <label class="mf-featured-toggle">
            <input type="checkbox" name="trending" value="1"${filters.trending ? " checked" : ""}>
            Trending
          </label>
          <button class="mf-button mf-button--primary" type="submit">Terapkan</button>
          <a class="mf-button mf-button--secondary" href="/news">Reset</a>
        </form>
        ${articles.length ? `<div class="mf-grid mf-grid--news">${articles.map(renderNewsCard).join("")}</div>` : `
          <div class="mf-empty-state mf-card"><h3>Artikel belum ditemukan.</h3><p>Coba kata kunci atau kategori lain.</p></div>
        `}
      </div>
    </section>
  `;
}

function renderArticle(_session, article) {
  if (!article) {
    return renderEmptyState("404", "Artikel tidak ditemukan.", "Artikel mungkin belum dipublikasikan.", "/news", "Kembali ke News");
  }
  return `
    <article class="mf-section">
      <div class="mf-container mf-article-layout">
        <header class="mf-article-header">
          <p class="mf-eyebrow">${escapeHtml(article.category.name)} / ${escapeHtml(article.readingTime)}</p>
          <h1>${escapeHtml(article.title)}</h1>
          <p class="mf-lead">${escapeHtml(article.excerpt)}</p>
        </header>
        <img class="mf-article-image" src="${escapeHtml(article.image)}" alt="" loading="lazy" width="1120" height="630">
        <div class="mf-article-body mf-card">
          <p>${escapeHtml(article.body)}</p>
        </div>
        ${(article.related || []).length ? `
          <section>
            ${renderSectionHeader({
              eyebrow: "Related article",
              title: "Baca juga dari kategori yang sama.",
              description: "Insight terkait untuk memperluas konteks keputusan IT.",
            })}
            <div class="mf-grid mf-grid--news">${article.related.map(renderNewsCard).join("")}</div>
          </section>
        ` : ""}
      </div>
    </article>
  `;
}

function renderAdminDashboard(session, data = {}) {
  const kpis = data.kpis || {};
  const recentTickets = data.tickets || [];
  const cards = [
    ["Akun aktif", kpis.activeMembers || 0, `${kpis.totalMembers || 0} total akun`],
    ["Total order", kpis.totalOrders || 0, `${kpis.pendingPayments || 0} menunggu pembayaran`],
    ["Omzet paid", formatIdr(kpis.paidRevenue), "Akumulasi order berstatus paid"],
    ["Ticket aktif", kpis.activeTickets || 0, `${kpis.urgentTickets || 0} prioritas urgent`],
  ];
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Admin ecosystem",
          title: `Operational overview, ${escapeHtml(session.user.name)}.`,
          description: "Ringkasan data marketplace dan konsultasi yang dihitung langsung dari persistence aktif.",
        })}
        <div class="mf-admin-kpi-grid">
          ${cards.map(([label, value, note]) => `
            <article class="mf-admin-kpi mf-card">
              <span>${escapeHtml(label)}</span>
              <strong>${escapeHtml(value)}</strong>
              <small>${escapeHtml(note)}</small>
            </article>
          `).join("")}
        </div>
        <div class="mf-admin-dashboard-grid">
          <section class="mf-card mf-admin-panel">
            <div class="mf-admin-panel__heading">
              <div><p class="mf-eyebrow">Consultation queue</p><h2>Ticket terbaru</h2></div>
              <a class="mf-text-link" href="/admin/consultation">Buka semua</a>
            </div>
            ${recentTickets.length ? `
              <div class="mf-admin-ticket-summary">
                ${recentTickets.slice(0, 5).map((ticket) => `
                  <a href="/admin/consultation#ticket-${escapeHtml(ticket.id)}">
                    <span class="mf-badge">${escapeHtml(ticket.priority)}</span>
                    <div><strong>${escapeHtml(ticket.subject)}</strong><small>${escapeHtml(ticket.member?.name || "-")} / ${escapeHtml(ticket.status)}</small></div>
                    <time>${formatTimestamp(ticket.updatedAt)}</time>
                  </a>
                `).join("")}
              </div>
            ` : '<div class="mf-empty-state"><p>Queue konsultasi masih kosong.</p></div>'}
          </section>
          <aside class="mf-card mf-admin-panel">
            <p class="mf-eyebrow">Phase 8 scope</p>
            <h2>Operational control center.</h2>
            <p>KPI, consultation management, order monitoring, dan product management sudah aktif. News dan member management menjadi tahap lanjutan Phase 8.</p>
            <div class="mf-action-row">
              <a class="mf-button mf-button--primary" href="/admin/orders">Monitor order</a>
              <a class="mf-button mf-button--secondary" href="/admin/products">Kelola produk</a>
              <a class="mf-button mf-button--secondary" href="/admin/consultation">Kelola konsultasi</a>
            </div>
          </aside>
        </div>
      </div>
    </section>
  `;
}

function renderAdminProducts(_session, data = {}) {
  const products = data.products || [];
  const categories = data.categories || [];
  adminProductCache = products;
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Admin products",
          title: "Kelola katalog tanpa bergantung pada owner builder.",
          description: `${products.length} produk tersimpan. Create, edit, media, stok, featured, dan archive tersedia untuk role admin.`,
        })}
        <div class="mf-admin-product-layout">
          <section class="mf-card mf-admin-product-form-card">
            <div class="mf-admin-panel__heading">
              <div><p class="mf-eyebrow">Product editor</p><h2 data-product-form-title>Produk baru</h2></div>
              <button class="mf-button mf-button--secondary" type="button" data-admin-product-reset>Reset</button>
            </div>
            <form class="mf-form" data-admin-product-form novalidate>
              <input type="hidden" name="id">
              <div class="mf-form-grid">
                <label class="mf-field">Nama produk
                  <input name="name" minlength="3" maxlength="160" required>
                  <small data-field-error="name"></small>
                </label>
                <label class="mf-field">Slug
                  <input name="slug" maxlength="160" pattern="[a-z0-9]+(?:-[a-z0-9]+)*" placeholder="otomatis-jika-kosong">
                  <small data-field-error="slug"></small>
                </label>
                <label class="mf-field">Kategori
                  <select name="category" required>
                    ${categories.map((category) => `<option value="${escapeHtml(category.slug)}">${escapeHtml(category.name)}</option>`).join("")}
                  </select>
                  <small data-field-error="category"></small>
                </label>
                <label class="mf-field">Badge
                  <input name="badge" maxlength="80">
                  <small data-field-error="badge"></small>
                </label>
                <label class="mf-field">Harga
                  <input type="number" name="price" min="0" step="1" required>
                  <small data-field-error="price"></small>
                </label>
                <label class="mf-field">Stok
                  <input type="number" name="stock" min="0" step="1" required>
                  <small data-field-error="stock"></small>
                </label>
                <label class="mf-field">Status
                  <select name="status">
                    <option value="active">active</option>
                    <option value="inactive">inactive</option>
                    <option value="out_of_stock">out_of_stock</option>
                    <option value="archived">archived</option>
                  </select>
                  <small data-field-error="status"></small>
                </label>
                <label class="mf-featured-toggle">
                  <input type="checkbox" name="featured">
                  Featured product
                </label>
                <label class="mf-field mf-field--wide">Ringkasan
                  <textarea name="shortDescription" maxlength="280" rows="3" required></textarea>
                  <small data-field-error="shortDescription"></small>
                </label>
                <label class="mf-field mf-field--wide">Deskripsi
                  <textarea name="description" maxlength="5000" rows="6" required></textarea>
                  <small data-field-error="description"></small>
                </label>
                <label class="mf-field mf-field--wide">Gambar utama
                  <input name="thumbnail" maxlength="500" required placeholder="/owner-media/product-....webp">
                  <small data-field-error="thumbnail"></small>
                </label>
                <label class="mf-field">Upload gambar
                  <input type="file" name="imageFile" accept="image/jpeg,image/png,image/webp,image/gif">
                  <small>JPG, PNG, WebP, atau GIF maksimal 10MB.</small>
                </label>
                <div class="mf-admin-product-upload">
                  <button class="mf-button mf-button--secondary" type="button" data-admin-product-upload>Upload dan gunakan</button>
                  <p class="mf-form-status" data-upload-status role="status" aria-live="polite"></p>
                </div>
                <label class="mf-field mf-field--wide">Gallery URL
                  <textarea name="images" rows="5" placeholder="Satu URL per baris"></textarea>
                  <small>Maksimal 10 gambar. Gambar utama otomatis masuk gallery.</small>
                </label>
              </div>
              <button class="mf-button mf-button--primary" type="submit">Simpan produk</button>
              <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
            </form>
          </section>
          <section class="mf-admin-product-list">
            ${products.map((product) => `
              <article class="mf-card mf-admin-product-card">
                <img src="${escapeHtml(product.image)}" alt="" loading="lazy" width="320" height="200">
                <div>
                  <div class="mf-action-row">
                    <span class="mf-badge">${escapeHtml(product.status)}</span>
                    ${product.featured ? '<span class="mf-badge mf-badge--blue">featured</span>' : ""}
                  </div>
                  <h3>${escapeHtml(product.name)}</h3>
                  <p>${escapeHtml(product.category.name)} / stok ${product.stock}</p>
                  <strong>${formatIdr(product.price)}</strong>
                  <div class="mf-action-row">
                    <button class="mf-button mf-button--secondary" type="button" data-admin-product-edit="${escapeHtml(product.id)}">Edit</button>
                    ${product.status === "archived" ? "" : `<button class="mf-button mf-button--secondary" type="button" data-admin-product-archive="${escapeHtml(product.id)}">Arsipkan</button>`}
                    ${product.status === "active" || product.status === "out_of_stock" ? `<a class="mf-text-link" href="/marketplace/product/${encodeURIComponent(product.slug)}" target="_blank" rel="noreferrer">Preview</a>` : ""}
                  </div>
                </div>
              </article>
            `).join("")}
          </section>
        </div>
      </div>
    </section>
  `;
}

function renderAdminOrders(_session, data = {}) {
  const orders = data.orders || [];
  const filters = data.filters || {};
  const paymentStatuses = ["unpaid", "pending", "paid", "failed", "expired", "cancelled"];
  const orderStatuses = ["pending", "waiting_payment", "paid", "processing", "shipped", "completed", "cancelled"];
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Admin orders",
          title: "Invoice, pembayaran, dan fulfillment dalam satu monitor.",
          description: `${orders.length} order ditampilkan berdasarkan filter aktif.`,
        })}
        <form class="mf-admin-filter mf-admin-order-filter mf-card" data-admin-order-filter>
          <label class="mf-field">Payment status
            <select name="paymentStatus">
              <option value="">Semua payment</option>
              ${paymentStatuses.map((status) => `<option value="${status}"${filters.paymentStatus === status ? " selected" : ""}>${status}</option>`).join("")}
            </select>
          </label>
          <label class="mf-field">Order status
            <select name="orderStatus">
              <option value="">Semua order</option>
              ${orderStatuses.map((status) => `<option value="${status}"${filters.orderStatus === status ? " selected" : ""}>${status}</option>`).join("")}
            </select>
          </label>
          <button class="mf-button mf-button--primary" type="submit">Terapkan</button>
          <a class="mf-button mf-button--secondary" href="/admin/orders">Reset</a>
        </form>
        <div class="mf-admin-order-list">
          ${orders.length ? orders.map((order) => `
            <article class="mf-card mf-admin-order" id="order-${escapeHtml(order.id)}">
              <header class="mf-admin-order__header">
                <div>
                  <div class="mf-action-row">
                    <span class="mf-badge mf-badge--blue">payment: ${escapeHtml(order.paymentStatus)}</span>
                    <span class="mf-badge">order: ${escapeHtml(order.orderStatus)}</span>
                  </div>
                  <h2>${escapeHtml(order.invoiceNumber)}</h2>
                  <p>Dibuat ${formatTimestamp(order.createdAt)}</p>
                </div>
                <strong class="mf-admin-order__total">${formatIdr(order.grandTotal)}</strong>
              </header>
              <div class="mf-admin-order__grid">
                <section>
                  <p class="mf-eyebrow">Customer</p>
                  <h3>${escapeHtml(order.customer.name)}</h3>
                  <p>${escapeHtml(order.customer.email)}</p>
                  <p>${escapeHtml(order.customer.recipientName)} / ${escapeHtml(order.customer.phone)}</p>
                </section>
                <section>
                  <p class="mf-eyebrow">Shipping</p>
                  <p>${escapeHtml(order.shipping.address)}</p>
                  <p>${escapeHtml(order.shipping.city)}, ${escapeHtml(order.shipping.province)} ${escapeHtml(order.shipping.postalCode)}</p>
                  <p>Metode: ${escapeHtml(order.shipping.method)}</p>
                </section>
              </div>
              <div class="mf-admin-order-items">
                ${(order.items || []).map((item) => `
                  <div>
                    <span><strong>${escapeHtml(item.name)}</strong><small>${item.qty} x ${formatIdr(item.price)}</small></span>
                    <strong>${formatIdr(item.subtotal)}</strong>
                  </div>
                `).join("")}
                <div><span>Subtotal</span><strong>${formatIdr(order.subtotal)}</strong></div>
                <div><span>Shipping</span><strong>${formatIdr(order.shippingCost)}</strong></div>
                <div class="mf-admin-order-items__grand"><span>Grand total</span><strong>${formatIdr(order.grandTotal)}</strong></div>
              </div>
              ${order.nextFulfillmentStatus ? `
                <form class="mf-admin-fulfillment" data-admin-fulfillment="${escapeHtml(order.id)}">
                  <input type="hidden" name="status" value="${escapeHtml(order.nextFulfillmentStatus)}">
                  <div>
                    <strong>Langkah fulfillment berikutnya</strong>
                    <p>${escapeHtml(order.orderStatus)} → ${escapeHtml(order.nextFulfillmentStatus)}</p>
                  </div>
                  <button class="mf-button mf-button--primary" type="submit">Set ${escapeHtml(order.nextFulfillmentStatus)}</button>
                  <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
                </form>
              ` : `
                <div class="mf-notice">
                  ${order.paymentStatus !== "paid"
                    ? "Fulfillment terkunci sampai pembayaran berstatus paid."
                    : "Fulfillment order ini sudah selesai atau tidak memiliki transisi berikutnya."}
                </div>
              `}
            </article>
          `).join("") : '<div class="mf-empty-state mf-card"><h3>Order tidak ditemukan.</h3><p>Coba kombinasi filter lain.</p></div>'}
        </div>
      </div>
    </section>
  `;
}

function renderAdminConsultation(_session, data = {}) {
  const tickets = data.tickets || [];
  const activeStatus = data.status || "";
  const statuses = ["open", "in_review", "waiting_member", "resolved", "closed"];
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Admin consultation",
          title: "Queue konsultasi dalam satu ruang kerja.",
          description: `${tickets.length} ticket ditampilkan${activeStatus ? ` untuk status ${activeStatus}` : ""}.`,
        })}
        <form class="mf-admin-filter mf-card" data-admin-consultation-filter>
          <label class="mf-field">Filter status
            <select name="status">
              <option value="">Semua status</option>
              ${statuses.map((status) => `<option value="${status}"${activeStatus === status ? " selected" : ""}>${status}</option>`).join("")}
            </select>
          </label>
          <button class="mf-button mf-button--primary" type="submit">Terapkan</button>
          <a class="mf-button mf-button--secondary" href="/admin/consultation">Reset</a>
        </form>
        <div class="mf-admin-queue">
          ${tickets.length ? tickets.map((ticket) => `
            <article class="mf-card mf-admin-ticket" id="ticket-${escapeHtml(ticket.id)}">
              <header class="mf-admin-ticket__header">
                <div>
                  <div class="mf-action-row">
                    <span class="mf-badge">${escapeHtml(ticket.priority)}</span>
                    <span class="mf-badge mf-badge--blue">${escapeHtml(ticket.status)}</span>
                  </div>
                  <h2>${escapeHtml(ticket.subject)}</h2>
                  <p>${escapeHtml(ticket.number)} / ${escapeHtml(ticket.category)}</p>
                </div>
                <div class="mf-admin-member">
                  <strong>${escapeHtml(ticket.member?.name || "-")}</strong>
                  <a href="mailto:${escapeHtml(ticket.member?.email || "")}">${escapeHtml(ticket.member?.email || "-")}</a>
                  <small>Update ${formatTimestamp(ticket.updatedAt)}</small>
                </div>
              </header>
              <div class="mf-ticket-thread">
                ${(ticket.replies || []).map((reply) => `
                  <div class="mf-ticket-reply" data-role="${escapeHtml(reply.authorRole)}">
                    <strong>${escapeHtml(reply.authorRole)}</strong>
                    <p>${escapeHtml(reply.message)}</p>
                    <small>${formatTimestamp(reply.createdAt)}</small>
                  </div>
                `).join("")}
              </div>
              ${(ticket.attachments || []).length ? `
                <div class="mf-ticket-attachments">
                  ${(ticket.attachments || []).map((attachment) => `<a href="${escapeHtml(attachment.downloadUrl)}">${escapeHtml(attachment.filename)}</a>`).join("")}
                </div>
              ` : ""}
              <div class="mf-admin-ticket__actions">
                <form class="mf-form" data-admin-reply="${escapeHtml(ticket.id)}">
                  <label class="mf-field">Balasan admin
                    <textarea name="message" minlength="2" maxlength="3000" rows="3" required placeholder="Berikan update teknis atau pertanyaan lanjutan."></textarea>
                  </label>
                  <button class="mf-button mf-button--primary" type="submit">Kirim balasan</button>
                  <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
                </form>
                <form class="mf-form" data-admin-status="${escapeHtml(ticket.id)}">
                  <label class="mf-field">Status ticket
                    <select name="status">
                      ${statuses.map((status) => `<option value="${status}"${ticket.status === status ? " selected" : ""}>${status}</option>`).join("")}
                    </select>
                  </label>
                  <button class="mf-button mf-button--secondary" type="submit">Update status</button>
                  <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
                </form>
              </div>
            </article>
          `).join("") : '<div class="mf-empty-state mf-card"><h3>Queue kosong.</h3><p>Tidak ada ticket untuk filter ini.</p></div>'}
        </div>
      </div>
    </section>
  `;
}

function renderCheckout(_session, checkout) {
  const { cart, addresses, profile } = checkout || {};
  if (!cart?.items?.length) {
    return renderEmptyState(
      "Cart",
      "Cart Anda masih kosong.",
      "Tambahkan produk yang sesuai sebelum melanjutkan checkout.",
      "/marketplace",
      "Lihat katalog",
    );
  }
  const defaultAddress = addresses.find((address) => address.isDefault) || addresses[0];
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Secure checkout",
          title: "Periksa cart dan tujuan pengiriman.",
          description: "Harga dan stok akan divalidasi ulang secara atomik saat order dibuat.",
        })}
        <div class="mf-checkout-layout">
          <div class="mf-checkout-main">
            <section class="mf-card mf-checkout-card">
              <h2>Cart</h2>
              <div class="mf-cart-list">
                ${cart.items.map((item) => `
                  <article class="mf-cart-item">
                    <img src="${escapeHtml(item.image)}" alt="">
                    <div><h3>${escapeHtml(item.name)}</h3><p>${formatIdr(item.price)}</p><small>Stok ${item.stock}</small></div>
                    <form data-cart-qty="${escapeHtml(item.id)}">
                      <input type="number" name="qty" min="1" max="${item.stock}" value="${item.qty}" aria-label="Jumlah ${escapeHtml(item.name)}">
                      <button type="submit">Update</button>
                    </form>
                    <strong>${formatIdr(item.subtotal)}</strong>
                    <button class="mf-cart-remove" type="button" data-cart-remove="${escapeHtml(item.id)}">Hapus</button>
                  </article>
                `).join("")}
              </div>
              <p class="mf-form-status" data-cart-status role="status" aria-live="polite"></p>
            </section>
            <section class="mf-card mf-checkout-card">
              <h2>Alamat pengiriman</h2>
              <form class="mf-form" data-checkout-form novalidate>
                ${addresses.length ? `
                  <label class="mf-field">Alamat tersimpan
                    <select name="addressId" data-address-select>
                      <option value="">Gunakan alamat baru</option>
                      ${addresses.map((address) => `<option value="${escapeHtml(address.id)}"${defaultAddress?.id === address.id ? " selected" : ""}>${escapeHtml(address.label)} - ${escapeHtml(address.city)}</option>`).join("")}
                    </select>
                  </label>
                ` : ""}
                <div class="mf-form-grid" data-new-address${defaultAddress ? " hidden" : ""}>
                  <label class="mf-field">Label<input name="label" maxlength="50" value="Alamat utama"></label>
                  <label class="mf-field">Nama penerima<input name="recipientName" autocomplete="name" minlength="2" maxlength="120" required value="${escapeHtml(profile?.name || "")}"><small data-field-error="recipientName"></small></label>
                  <label class="mf-field">Telepon<input name="phone" autocomplete="tel" maxlength="24" required value="${escapeHtml(profile?.phone || "")}"><small data-field-error="phone"></small></label>
                  <label class="mf-field">Kota<input name="city" autocomplete="address-level2" maxlength="100" required value="${escapeHtml(profile?.city || "")}"><small data-field-error="city"></small></label>
                  <label class="mf-field">Provinsi<input name="province" autocomplete="address-level1" maxlength="100" required value="${escapeHtml(profile?.province || "")}"><small data-field-error="province"></small></label>
                  <label class="mf-field">Kode pos<input name="postalCode" autocomplete="postal-code" maxlength="12" required value="${escapeHtml(profile?.postalCode || "")}"><small data-field-error="postalCode"></small></label>
                  <label class="mf-field mf-field--wide">Alamat<textarea name="address" autocomplete="street-address" minlength="8" maxlength="300" required>${escapeHtml(profile?.address || "")}</textarea><small data-field-error="address"></small></label>
                  <label class="mf-featured-toggle mf-field--wide"><input type="checkbox" name="saveAddress" value="1" checked>Simpan sebagai alamat default</label>
                </div>
                <label class="mf-field">Pengiriman
                  <select name="shippingMethod" data-shipping-method>
                    <option value="standard">Standard - ${formatIdr(25000)}</option>
                    <option value="priority">Priority - ${formatIdr(75000)}</option>
                    <option value="digital">Digital/service - ${formatIdr(0)}</option>
                  </select>
                </label>
                <button class="mf-button mf-button--primary mf-checkout-submit" type="submit">Buat order</button>
                <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
              </form>
            </section>
          </div>
          <aside class="mf-card mf-order-summary">
            <h2>Order summary</h2>
            <div><span>${cart.itemCount} item</span><strong>${formatIdr(cart.subtotal)}</strong></div>
            <div><span>Pengiriman</span><strong data-shipping-cost>${formatIdr(25000)}</strong></div>
            <div class="mf-order-summary__total"><span>Total</span><strong data-grand-total data-subtotal="${cart.subtotal}">${formatIdr(cart.subtotal + 25000)}</strong></div>
            <p>Payment diproses pada Phase 5. Order dibuat dengan status unpaid.</p>
          </aside>
        </div>
      </div>
    </section>
  `;
}

function renderEmptyState(eyebrow, title, description, href, label) {
  return `
    <section class="mf-section">
      <div class="mf-container mf-empty-state mf-card">
        ${renderSectionHeader({ eyebrow, title, description })}
        ${renderPrimaryButton({ label, href })}
      </div>
    </section>
  `;
}

const pages = {
  marketplace: renderMarketplace,
  product: renderProductDetail,
  login: () => renderAuth("login"),
  register: () => renderAuth("register"),
  forgot: () => renderPasswordRecovery("forgot"),
  reset: () => renderPasswordRecovery("reset"),
  member: renderMember,
  profile: (_session, profile) => renderProfile(profile),
  notifications: renderNotifications,
  orders: renderOrders,
  consultation: renderConsultation,
  news: renderNews,
  article: renderArticle,
  admin: renderAdminDashboard,
  "admin-consultation": renderAdminConsultation,
  "admin-orders": renderAdminOrders,
  "admin-products": renderAdminProducts,
  checkout: renderCheckout,
  "not-found": () =>
    renderEmptyState("404", "Halaman belum tersedia.", "Route ini belum menjadi bagian dari foundation Feira.", "/marketplace", "Ke marketplace"),
};

function safeNextPath() {
  const next = new URLSearchParams(window.location.search).get("next");
  const allowed = new Set([
    "/member",
    "/member/profile",
    "/member/orders",
    "/member/consultation",
    "/admin",
    "/admin/consultation",
    "/admin/orders",
    "/admin/products",
    "/checkout",
  ]);
  if (allowed.has(next) || next?.startsWith("/marketplace/product/")) return next;
  return "/member";
}

function clearFormErrors(form) {
  form.querySelectorAll("[data-field-error]").forEach((element) => {
    element.textContent = "";
  });
}

function bindAuthForm() {
  const form = document.querySelector("[data-auth-form]");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormErrors(form);
    const status = form.querySelector("[data-form-status]");
    const button = form.querySelector('button[type="submit"]');

    if (!form.reportValidity()) return;
    button.disabled = true;
    status.textContent = "Memproses...";
    status.dataset.state = "pending";

    const values = Object.fromEntries(new FormData(form));
    try {
      if (form.dataset.authForm === "register") {
        await registerMember(values);
        status.textContent = "Registrasi berhasil. Tunggu persetujuan owner sebelum login.";
        status.dataset.state = "success";
        form.reset();
        window.setTimeout(() => window.location.assign("/login?registered=1"), 1400);
        return;
      } else {
        await loginMember(values);
      }
      status.textContent = "Berhasil. Membuka member area...";
      status.dataset.state = "success";
      window.location.assign(safeNextPath());
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
      Object.entries(error.errors || {}).forEach(([field, message]) => {
        const target = form.querySelector(`[data-field-error="${field}"]`);
        if (target) target.textContent = message;
      });
      button.disabled = false;
    }
  });
}

function bindRecoveryForm() {
  const form = document.querySelector("[data-recovery-form]");
  if (!form) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormErrors(form);
    const status = form.querySelector("[data-form-status]");
    const button = form.querySelector('button[type="submit"]');
    if (!form.reportValidity()) return;
    button.disabled = true;
    status.textContent = "Memproses...";
    status.dataset.state = "pending";
    try {
      if (form.dataset.recoveryForm === "forgot") {
        const result = await requestPasswordReset(Object.fromEntries(new FormData(form)));
        status.textContent = "Jika email terdaftar, instruksi reset telah dikirim.";
        if (result.resetUrl) {
          const link = document.createElement("a");
          link.href = result.resetUrl;
          link.className = "mf-text-link";
          link.textContent = " Buka link reset development.";
          status.append(link);
        }
      } else {
        const token = new URLSearchParams(window.location.search).get("token") || "";
        await resetMemberPassword({
          token,
          password: new FormData(form).get("password"),
        });
        status.textContent = "Password berhasil diperbarui. Membuka halaman login...";
        window.setTimeout(() => window.location.assign("/login"), 900);
      }
      status.dataset.state = "success";
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
      Object.entries(error.errors || {}).forEach(([field, message]) => {
        const target = form.querySelector(`[data-field-error="${field}"]`);
        if (target) target.textContent = message;
      });
      button.disabled = false;
    }
  });
}

function bindLogout(session) {
  const button = document.querySelector("[data-logout]");
  if (!button || !session) return;
  button.addEventListener("click", async () => {
    button.disabled = true;
    try {
      await logoutMember(session.csrfToken);
      window.location.assign("/marketplace");
    } catch {
      button.disabled = false;
    }
  });
}

function bindProfileForm(session) {
  const form = document.querySelector("[data-profile-form]");
  if (!form || !session) return;

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormErrors(form);
    const status = form.querySelector("[data-form-status]");
    const button = form.querySelector('button[type="submit"]');
    if (!form.reportValidity()) return;

    button.disabled = true;
    status.textContent = "Menyimpan profile...";
    status.dataset.state = "pending";
    try {
      const profile = await updateMemberProfile(
        Object.fromEntries(new FormData(form)),
        session.csrfToken,
      );
      status.textContent = "Profile berhasil disimpan.";
      status.dataset.state = "success";
      const accountName = document.querySelector(".mf-account a");
      if (accountName) accountName.textContent = profile.name;
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
      Object.entries(error.errors || {}).forEach(([field, message]) => {
        const target = form.querySelector(`[data-field-error="${field}"]`);
        if (target) target.textContent = message;
      });
    } finally {
      button.disabled = false;
    }
  });
}

function bindAvatarForm(session) {
  const form = document.querySelector("[data-avatar-form]");
  if (!form || !session) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const input = form.querySelector('input[type="file"]');
    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector("[data-form-status]");
    const file = input.files?.[0];
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      status.textContent = "Ukuran avatar maksimal 2MB.";
      status.dataset.state = "error";
      return;
    }
    button.disabled = true;
    status.textContent = "Mengupload avatar...";
    status.dataset.state = "pending";
    try {
      const data = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.addEventListener("load", () => resolve(reader.result));
        reader.addEventListener("error", () => reject(new Error("File avatar tidak dapat dibaca.")));
        reader.readAsDataURL(file);
      });
      await uploadMemberAvatar(data, session.csrfToken);
      status.textContent = "Avatar berhasil diperbarui.";
      status.dataset.state = "success";
      window.setTimeout(() => window.location.reload(), 500);
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
      button.disabled = false;
    }
  });
}

function bindNotifications(session) {
  if (!session) return;
  const buttons = document.querySelectorAll("[data-read-notification], [data-read-all]");
  buttons.forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        await markMemberNotificationsRead(
          button.dataset.readNotification || "",
          session.csrfToken,
        );
        window.location.reload();
      } catch {
        button.disabled = false;
      }
    });
  });
}

function bindCatalogFilter() {
  const form = document.querySelector("[data-catalog-filter]");
  if (!form) return;
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const values = new FormData(form);
    const query = new URLSearchParams();
    const search = String(values.get("search") || "").trim();
    const category = String(values.get("category") || "").trim();
    const sort = String(values.get("sort") || "").trim();
    if (search) query.set("search", search);
    if (category) query.set("category", category);
    if (sort && sort !== "featured") query.set("sort", sort);
    if (values.get("featured")) query.set("featured", "1");
    const suffix = query.size ? `?${query}` : "";
    window.location.assign(`/marketplace${suffix}#produk`);
  });
}

function bindNewsFilter() {
  const form = document.querySelector("[data-news-filter]");
  if (!form) return;
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const values = new FormData(form);
    const query = new URLSearchParams();
    const search = String(values.get("search") || "").trim();
    const category = String(values.get("category") || "").trim();
    if (search) query.set("search", search);
    if (category) query.set("category", category);
    if (values.get("featured")) query.set("featured", "1");
    if (values.get("trending")) query.set("trending", "1");
    window.location.assign(`/news${query.size ? `?${query}` : ""}`);
  });
}

function bindConsultationForms(session) {
  if (!session) return;
  const form = document.querySelector("[data-consultation-form]");
  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      clearFormErrors(form);
      const button = form.querySelector('button[type="submit"]');
      const status = form.querySelector("[data-form-status]");
      if (!form.reportValidity()) return;
      button.disabled = true;
      status.textContent = "Mengirim ticket konsultasi...";
      status.dataset.state = "pending";
      try {
        const values = Object.fromEntries(new FormData(form));
        const file = form.querySelector('input[name="attachmentFile"]')?.files?.[0];
        delete values.attachmentFile;
        if (file) {
          if (file.size > 5 * 1024 * 1024) {
            throw Object.assign(new Error("Attachment maksimal 5MB."), {
              errors: { attachment: "Attachment maksimal 5MB." },
            });
          }
          values.attachment = {
            filename: file.name,
            data: await new Promise((resolve, reject) => {
              const reader = new FileReader();
              reader.addEventListener("load", () => resolve(reader.result));
              reader.addEventListener("error", () => reject(new Error("Attachment tidak dapat dibaca.")));
              reader.readAsDataURL(file);
            }),
          };
        }
        await createConsultationTicket(values, session.csrfToken);
        status.textContent = "Ticket berhasil dibuat.";
        status.dataset.state = "success";
        window.setTimeout(() => window.location.reload(), 600);
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        Object.entries(error.errors || {}).forEach(([field, message]) => {
          const target = form.querySelector(`[data-field-error="${field}"]`);
          if (target) target.textContent = message;
        });
        button.disabled = false;
      }
    });
  }

  document.querySelectorAll("[data-consultation-reply]").forEach((replyForm) => {
    replyForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = replyForm.querySelector('button[type="submit"]');
      const status = replyForm.querySelector("[data-form-status]");
      if (!replyForm.reportValidity()) return;
      button.disabled = true;
      status.textContent = "Mengirim reply...";
      status.dataset.state = "pending";
      try {
        await replyConsultationTicket(
          replyForm.dataset.consultationReply,
          new FormData(replyForm).get("message"),
          session.csrfToken,
        );
        status.textContent = "Reply berhasil dikirim.";
        status.dataset.state = "success";
        window.setTimeout(() => window.location.reload(), 600);
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });
}

function bindAdminConsultation(session) {
  const filter = document.querySelector("[data-admin-consultation-filter]");
  filter?.addEventListener("submit", (event) => {
    event.preventDefault();
    const status = String(new FormData(filter).get("status") || "");
    window.location.assign(`/admin/consultation${status ? `?status=${encodeURIComponent(status)}` : ""}`);
  });

  document.querySelectorAll("[data-admin-reply]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const status = form.querySelector("[data-form-status]");
      if (!form.reportValidity()) return;
      button.disabled = true;
      status.textContent = "Mengirim balasan...";
      status.dataset.state = "pending";
      try {
        await replyAdminConsultation(
          form.dataset.adminReply,
          new FormData(form).get("message"),
          session.csrfToken,
        );
        status.textContent = "Balasan admin terkirim.";
        status.dataset.state = "success";
        window.setTimeout(() => window.location.reload(), 500);
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });

  document.querySelectorAll("[data-admin-status]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const status = form.querySelector("[data-form-status]");
      button.disabled = true;
      status.textContent = "Memperbarui status...";
      status.dataset.state = "pending";
      try {
        await updateAdminConsultationStatus(
          form.dataset.adminStatus,
          new FormData(form).get("status"),
          session.csrfToken,
        );
        status.textContent = "Status berhasil diperbarui.";
        status.dataset.state = "success";
        window.setTimeout(() => window.location.reload(), 500);
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });
}

function bindAdminOrders(session) {
  const filter = document.querySelector("[data-admin-order-filter]");
  filter?.addEventListener("submit", (event) => {
    event.preventDefault();
    const values = new FormData(filter);
    const query = new URLSearchParams();
    const paymentStatus = String(values.get("paymentStatus") || "");
    const orderStatus = String(values.get("orderStatus") || "");
    if (paymentStatus) query.set("paymentStatus", paymentStatus);
    if (orderStatus) query.set("orderStatus", orderStatus);
    window.location.assign(`/admin/orders${query.size ? `?${query}` : ""}`);
  });

  document.querySelectorAll("[data-admin-fulfillment]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const status = form.querySelector("[data-form-status]");
      button.disabled = true;
      status.textContent = "Memperbarui fulfillment...";
      status.dataset.state = "pending";
      try {
        await updateAdminOrderFulfillment(
          form.dataset.adminFulfillment,
          new FormData(form).get("status"),
          session.csrfToken,
        );
        status.textContent = "Fulfillment berhasil diperbarui.";
        status.dataset.state = "success";
        window.setTimeout(() => window.location.reload(), 500);
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });
}

function bindAdminProducts(session) {
  const form = document.querySelector("[data-admin-product-form]");
  if (!form) return;
  const title = document.querySelector("[data-product-form-title]");
  const reset = () => {
    form.reset();
    form.elements.id.value = "";
    form.elements.status.value = "active";
    title.textContent = "Produk baru";
    clearFormErrors(form);
    form.querySelector("[data-form-status]").textContent = "";
  };
  document.querySelector("[data-admin-product-reset]")?.addEventListener("click", reset);

  document.querySelector("[data-admin-product-upload]")?.addEventListener("click", async () => {
    const file = form.elements.imageFile.files?.[0];
    const status = form.querySelector("[data-upload-status]");
    if (!file) {
      status.textContent = "Pilih gambar terlebih dahulu.";
      status.dataset.state = "error";
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      status.textContent = "Ukuran gambar maksimal 10MB.";
      status.dataset.state = "error";
      return;
    }
    status.textContent = "Mengupload gambar...";
    status.dataset.state = "pending";
    try {
      const url = await uploadAdminProductImage(file, session.csrfToken);
      form.elements.thumbnail.value = url;
      const gallery = form.elements.images.value.split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
      if (!gallery.includes(url)) gallery.unshift(url);
      form.elements.images.value = gallery.join("\n");
      status.textContent = "Gambar berhasil diupload.";
      status.dataset.state = "success";
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
    }
  });

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormErrors(form);
    if (!form.reportValidity()) return;
    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector("[data-form-status]");
    const values = Object.fromEntries(new FormData(form));
    const productId = String(values.id || "");
    delete values.id;
    delete values.imageFile;
    values.featured = form.elements.featured.checked;
    values.images = String(values.images || "").split(/\r?\n/).map((item) => item.trim()).filter(Boolean);
    button.disabled = true;
    status.textContent = "Menyimpan produk...";
    status.dataset.state = "pending";
    try {
      await saveAdminProduct(values, session.csrfToken, productId);
      status.textContent = productId ? "Produk berhasil diperbarui." : "Produk berhasil ditambahkan.";
      status.dataset.state = "success";
      window.setTimeout(() => window.location.reload(), 500);
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
      Object.entries(error.errors || {}).forEach(([field, message]) => {
        const target = form.querySelector(`[data-field-error="${field}"]`);
        if (target) target.textContent = message;
      });
      button.disabled = false;
    }
  });

  document.querySelectorAll("[data-admin-product-edit]").forEach((button) => {
    button.addEventListener("click", () => {
      const product = adminProductCache.find((item) => item.id === button.dataset.adminProductEdit);
      if (!product) return;
      form.elements.id.value = product.id;
      form.elements.name.value = product.name;
      form.elements.slug.value = product.slug;
      form.elements.category.value = product.category.slug;
      form.elements.badge.value = product.badge || "";
      form.elements.price.value = product.price;
      form.elements.stock.value = product.stock;
      form.elements.status.value = product.status;
      form.elements.featured.checked = product.featured;
      form.elements.shortDescription.value = product.shortDescription;
      form.elements.description.value = product.description;
      form.elements.thumbnail.value = product.image;
      form.elements.images.value = (product.images || []).join("\n");
      title.textContent = `Edit ${product.name}`;
      form.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  });

  document.querySelectorAll("[data-admin-product-archive]").forEach((button) => {
    button.addEventListener("click", async () => {
      const product = adminProductCache.find((item) => item.id === button.dataset.adminProductArchive);
      if (!product || !window.confirm(`Arsipkan ${product.name}?`)) return;
      button.disabled = true;
      try {
        await archiveAdminProduct(product.id, session.csrfToken);
        window.location.reload();
      } catch (error) {
        window.alert(error.message);
        button.disabled = false;
      }
    });
  });
}

function bindProductGallery() {
  const gallery = document.querySelector("[data-product-gallery]");
  if (!gallery) return;
  const mainImage = gallery.querySelector("[data-gallery-main]");
  gallery.querySelectorAll("[data-gallery-image]").forEach((button) => {
    button.addEventListener("click", () => {
      mainImage.src = button.dataset.galleryImage;
      gallery.querySelectorAll("[data-gallery-image]").forEach((item) => {
        item.removeAttribute("aria-current");
      });
      button.setAttribute("aria-current", "true");
    });
  });
}

function updateCartCount(cart) {
  const count = document.querySelector("[data-cart-count]");
  if (count) count.textContent = cart.itemCount;
}

function bindAddCart(session) {
  const form = document.querySelector("[data-add-cart]");
  if (!form || !session) return;
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector("[data-form-status]");
    if (!form.reportValidity()) return;
    button.disabled = true;
    status.textContent = "Menambahkan ke cart...";
    status.dataset.state = "pending";
    try {
      const cart = await addCartItem(
        form.dataset.addCart,
        new FormData(form).get("qty"),
        session.csrfToken,
      );
      updateCartCount(cart);
      status.textContent = "Produk berhasil ditambahkan ke cart.";
      status.dataset.state = "success";
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
    } finally {
      button.disabled = false;
    }
  });
}

function bindCartEditor(session) {
  if (!session) return;
  const status = document.querySelector("[data-cart-status]");
  document.querySelectorAll("[data-cart-qty]").forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector("button");
      button.disabled = true;
      try {
        const cart = await updateCartItem(
          form.dataset.cartQty,
          new FormData(form).get("qty"),
          session.csrfToken,
        );
        updateCartCount(cart);
        window.location.reload();
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });
  document.querySelectorAll("[data-cart-remove]").forEach((button) => {
    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        const cart = await removeCartItem(button.dataset.cartRemove, session.csrfToken);
        updateCartCount(cart);
        window.location.reload();
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });
}

function setAddressFieldsEnabled(container, enabled) {
  if (!container) return;
  container.hidden = !enabled;
  container.querySelectorAll("input, textarea").forEach((field) => {
    field.disabled = !enabled;
  });
}

function bindCheckout(session) {
  const form = document.querySelector("[data-checkout-form]");
  if (!form || !session) return;
  const addressSelect = form.querySelector("[data-address-select]");
  const newAddress = form.querySelector("[data-new-address]");
  const shipping = form.querySelector("[data-shipping-method]");
  const shippingCost = document.querySelector("[data-shipping-cost]");
  const total = document.querySelector("[data-grand-total]");
  const costs = { standard: 25000, priority: 75000, digital: 0 };

  const syncAddress = () => setAddressFieldsEnabled(newAddress, !addressSelect?.value);
  const syncSummary = () => {
    const cost = costs[shipping.value] ?? 0;
    shippingCost.textContent = formatIdr(cost);
    total.textContent = formatIdr(Number(total.dataset.subtotal) + cost);
  };
  addressSelect?.addEventListener("change", syncAddress);
  shipping.addEventListener("change", syncSummary);
  syncAddress();
  syncSummary();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearFormErrors(form);
    const button = form.querySelector('button[type="submit"]');
    const status = form.querySelector("[data-form-status]");
    if (!form.reportValidity()) return;
    button.disabled = true;
    status.textContent = "Memvalidasi stok dan membuat invoice...";
    status.dataset.state = "pending";
    try {
      const values = Object.fromEntries(new FormData(form));
      let addressId = values.addressId || "";
      const address = {
        label: values.label,
        recipientName: values.recipientName,
        phone: values.phone,
        address: values.address,
        city: values.city,
        province: values.province,
        postalCode: values.postalCode,
        isDefault: Boolean(values.saveAddress),
      };
      if (!addressId && values.saveAddress) {
        const saved = await saveAddress(address, session.csrfToken);
        addressId = saved.id;
      }
      const order = await createOrder(
        {
          addressId,
          address: addressId ? undefined : address,
          shippingMethod: values.shippingMethod,
        },
        session.csrfToken,
      );
      updateCartCount({ itemCount: 0 });
      status.textContent = `Invoice ${order.invoiceNumber} berhasil dibuat.`;
      status.dataset.state = "success";
      window.setTimeout(() => window.location.assign("/member/orders"), 900);
    } catch (error) {
      status.textContent = error.message;
      status.dataset.state = "error";
      Object.entries(error.errors || {}).forEach(([field, message]) => {
        const target = form.querySelector(`[data-field-error="${field}"]`);
        if (target) target.textContent = message;
      });
      button.disabled = false;
    }
  });
}

function bindPaymentForms(session) {
  if (!session) return;
  document.querySelectorAll("[data-payment-form]").forEach((form) => {
    const method = form.querySelector("[data-payment-method]");
    const bankField = form.querySelector("[data-payment-bank]");
    const bank = bankField.querySelector("select");
    const syncMethod = () => {
      const usesBank = method.value === "bank_transfer";
      bankField.hidden = !usesBank;
      bank.disabled = !usesBank;
    };
    method.addEventListener("change", syncMethod);
    syncMethod();
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const button = form.querySelector('button[type="submit"]');
      const status = form.querySelector("[data-form-status]");
      button.disabled = true;
      status.textContent = "Menghubungkan ke payment gateway...";
      status.dataset.state = "pending";
      try {
        const values = Object.fromEntries(new FormData(form));
        const result = await createPayment(
          form.dataset.paymentForm,
          values.method,
          values.bank || "",
          session.csrfToken,
        );
        status.textContent = result.mock
          ? "Instruksi mock berhasil dibuat."
          : "Instruksi pembayaran berhasil dibuat.";
        status.dataset.state = "success";
        window.setTimeout(() => window.location.reload(), 600);
      } catch (error) {
        status.textContent = error.message;
        status.dataset.state = "error";
        button.disabled = false;
      }
    });
  });
}

async function bootstrap() {
  const route = getRoute();
  const root = document.querySelector("[data-marketplace-root]");
  let session = null;
  let profile = null;
  let notifications = null;
  let pageData = null;
  let cart = { items: [], itemCount: 0, subtotal: 0 };

  try {
    session = await getCurrentSession();
  } catch {
    root.innerHTML = renderEmptyState(
      "Connection issue",
      "Session belum dapat diperiksa.",
      "Coba muat ulang halaman. Tidak ada credential yang disimpan di browser.",
      window.location.pathname,
      "Muat ulang",
    );
    return;
  }

  if (session && (route === "login" || route === "register")) {
    window.location.replace("/member");
    return;
  }

  if (session) {
    try {
      [notifications, cart] = await Promise.all([
        getMemberNotifications(),
        getCart(),
      ]);
    } catch {
      notifications = { items: [], unreadCount: 0 };
    }
  }

  if (route === "profile") {
    try {
      profile = await getMemberProfile();
    } catch {
      root.innerHTML = renderEmptyState(
        "Profile unavailable",
        "Profile belum dapat dimuat.",
        "Coba muat ulang halaman untuk mengambil data member.",
        "/member/profile",
        "Muat ulang",
      );
      return;
    }
  }

  try {
    if (route === "marketplace") {
      const filters = currentCatalogFilters();
      const [products, categories] = await Promise.all([
        getProducts(filters),
        getCategories(),
      ]);
      pageData = { products, categories, filters };
    } else if (route === "product") {
      const slug = window.location.pathname.split("/").filter(Boolean).at(-1);
      pageData = await getProduct(slug);
    } else if (route === "checkout") {
      const [addresses, checkoutProfile] = await Promise.all([
        getAddresses(),
        getMemberProfile(),
      ]);
      pageData = { cart, addresses, profile: checkoutProfile };
    } else if (route === "orders") {
      const orders = await getOrders();
      pageData = await Promise.all(
        orders.map(async (order) => ({
          ...order,
          payments: await getOrderPayments(order.id),
        })),
      );
    } else if (route === "consultation") {
      pageData = await getConsultationTickets();
    } else if (route === "news") {
      const filters = currentNewsFilters();
      const [articles, categories] = await Promise.all([
        getNewsArticles(filters),
        getNewsCategories(),
      ]);
      pageData = { articles, categories, filters };
    } else if (route === "article") {
      const slug = window.location.pathname.split("/").filter(Boolean).at(-1);
      pageData = await getNewsArticle(slug);
    } else if (route === "admin") {
      const [kpis, tickets] = await Promise.all([
        getAdminKpis(),
        getAdminConsultations(),
      ]);
      pageData = { kpis, tickets };
    } else if (route === "admin-consultation") {
      const status = currentAdminConsultationStatus();
      pageData = {
        tickets: await getAdminConsultations(status),
        status,
      };
    } else if (route === "admin-orders") {
      const filters = currentAdminOrderFilters();
      const summaries = await getAdminOrders(filters);
      pageData = {
        orders: await Promise.all(
          summaries.map((order) => getAdminOrder(order.id)),
        ),
        filters,
      };
    } else if (route === "admin-products") {
      const [products, categories] = await Promise.all([
        getAdminProducts(),
        getCategories(),
      ]);
      pageData = { products, categories };
    }
  } catch (error) {
    if ((route === "product" || route === "article") && error.status === 404) {
      pageData = null;
    } else {
      root.innerHTML = renderEmptyState(
        "Catalog unavailable",
        "Katalog belum dapat dimuat.",
        "Coba muat ulang halaman untuk mengambil data produk.",
        window.location.pathname,
        "Muat ulang",
      );
      return;
    }
  }

  const data = route === "profile"
    ? profile
    : route === "notifications" || route === "member"
      ? notifications
      : pageData;
  const content = pages[route](session, data, notifications);
  root.innerHTML = renderMarketplaceLayout({
    content,
    activeRoute: route,
    session,
    unreadCount: notifications?.unreadCount || 0,
    cartCount: cart.itemCount || 0,
  });
  document.title = `${marketplaceConfig.titles[route] || "Marketplace"} | Feira`;
  bindSiteHeader();
  bindAuthForm();
  bindRecoveryForm();
  bindLogout(session);
  bindProfileForm(session);
  bindAvatarForm(session);
  bindNotifications(session);
  bindCatalogFilter();
  bindNewsFilter();
  bindConsultationForms(session);
  bindAdminConsultation(session);
  bindAdminOrders(session);
  bindAdminProducts(session);
  bindProductGallery();
  bindAddCart(session);
  bindCartEditor(session);
  bindCheckout(session);
  bindPaymentForms(session);
}

bootstrap();
