import { renderMarketplaceLayout } from "../layouts/MarketplaceLayout.js";
import { renderProductCard } from "../components/cards/ProductCard.js";
import { renderMemberDashboardCard } from "../components/cards/MemberDashboardCard.js";
import { renderConsultationTicketCard } from "../components/cards/ConsultationTicketCard.js";
import { renderNewsCard } from "../components/cards/NewsCard.js";
import { renderPrimaryButton } from "../components/ui/PrimaryButton.js";
import { renderPriceTag } from "../components/ui/PriceTag.js";
import { renderSectionHeader } from "../components/sections/SectionHeader.js";
import { marketplaceConfig } from "../config/marketplace.js";
import {
  getCurrentSession,
  getMemberProfile,
  loginMember,
  logoutMember,
  registerMember,
  updateMemberProfile,
} from "../services/auth-service.js";
import {
  mockConsultations,
  mockDashboardItems,
  mockNews,
  mockProducts,
} from "../modules/marketplace/data/mock-marketplace.js";

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

function getRoute() {
  const path = window.location.pathname.replace(/\/+$/, "") || "/";
  if (path.startsWith("/marketplace/product/")) return "product";
  return marketplaceConfig.routes[path] || "not-found";
}

function renderMarketplace() {
  return `
    <section class="mf-hero mf-section">
      <div class="mf-container mf-hero__grid">
        <div class="mf-stack mf-stack--lg">
          <p class="mf-eyebrow">Feira Mini Marketplace</p>
          <h1>Perangkat IT pilihan, dengan arahan yang lebih manusiawi.</h1>
          <p class="mf-lead">Pondasi katalog premium untuk kebutuhan kerja, bisnis, jaringan, dan solusi digital. Transaksi belum aktif pada Phase 1.</p>
          <div class="mf-action-row">
            ${renderPrimaryButton({ label: "Jelajahi produk", href: "#produk" })}
            ${renderPrimaryButton({ label: "Konsultasi kebutuhan", href: "/member/consultation", variant: "secondary" })}
          </div>
          <p class="mf-demo-note">Mock catalog Phase 1 - harga dan stok belum terhubung ke database.</p>
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
    <section class="mf-section" id="produk">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Katalog awal",
          title: "Pilihan teknologi untuk fondasi kerja yang solid.",
          description: "Komponen card sudah reusable; filter, cart, dan data live masuk pada phase lanjutan.",
        })}
        <div class="mf-grid mf-grid--products">
          ${mockProducts.map(renderProductCard).join("")}
        </div>
      </div>
    </section>
  `;
}

function renderProductDetail() {
  const slug = window.location.pathname.split("/").filter(Boolean).at(-1);
  const product = mockProducts.find((item) => item.slug === slug) || mockProducts[0];
  return `
    <section class="mf-section">
      <div class="mf-container mf-product-detail">
        <div class="mf-product-detail__media">
          <img src="${escapeHtml(product.image)}" alt="${escapeHtml(product.name)}">
        </div>
        <div class="mf-stack mf-stack--lg">
          <p class="mf-eyebrow">Product placeholder</p>
          <h1>${escapeHtml(product.name)}</h1>
          <p class="mf-lead">${escapeHtml(product.description)}</p>
          ${renderPriceTag(product.price)}
          <div class="mf-notice">Detail spesifikasi, gallery, stock validation, wishlist, dan add-to-cart akan diaktifkan pada Phase 3.</div>
          ${renderPrimaryButton({ label: "Kembali ke marketplace", href: "/marketplace" })}
        </div>
      </div>
    </section>
  `;
}

function renderAuth(type) {
  const isLogin = type === "login";
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
            <p class="mf-form-status" data-form-status role="status" aria-live="polite"></p>
          </form>
          <p class="mf-form-help">${isLogin ? 'Belum punya akun? <a href="/register">Daftar member</a>.' : 'Sudah terdaftar? <a href="/login">Masuk di sini</a>.'}</p>
        </div>
      </div>
    </section>
  `;
}

function renderMember(session) {
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Member area",
          title: `Halo, ${escapeHtml(session.user.name)}.`,
          description: "Session member aktif. Order dan consultation masih berupa foundation untuk phase berikutnya.",
        })}
        <div class="mf-grid mf-grid--dashboard">
          ${mockDashboardItems.map(renderMemberDashboardCard).join("")}
        </div>
      </div>
    </section>
  `;
}

function renderProfile(profile) {
  return `
    <section class="mf-section">
      <div class="mf-container mf-profile-layout">
        <aside class="mf-profile-summary mf-card">
          <span class="mf-profile-summary__avatar" aria-hidden="true">${escapeHtml(profile.name.slice(0, 1).toUpperCase())}</span>
          <div>
            <p class="mf-eyebrow">Member profile</p>
            <h2>${escapeHtml(profile.name)}</h2>
            <p>${escapeHtml(profile.email)}</p>
          </div>
          <div class="mf-notice">Avatar upload belum aktif pada stage ini.</div>
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

function renderOrders() {
  return renderEmptyState(
    "Order history",
    "Pesanan Anda akan tampil di sini.",
    "Order service, invoice, dan status tracking baru diaktifkan setelah auth dan marketplace core stabil.",
    "/marketplace",
    "Lihat katalog",
  );
}

function renderConsultation() {
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "IT consultation",
          title: "Percakapan teknis yang tetap terstruktur.",
          description: "Ticket card berikut adalah mock UI. Submit, upload, reply, dan permission belum aktif.",
        })}
        <div class="mf-grid mf-grid--tickets">
          ${mockConsultations.map(renderConsultationTicketCard).join("")}
        </div>
      </div>
    </section>
  `;
}

function renderNews() {
  return `
    <section class="mf-section">
      <div class="mf-container">
        ${renderSectionHeader({
          eyebrow: "Feira IT News",
          title: "Insight ringkas untuk keputusan teknologi yang lebih jernih.",
          description: "Artikel berikut adalah mock content Phase 1, bukan publikasi final.",
        })}
        <div class="mf-grid mf-grid--news">
          ${mockNews.map(renderNewsCard).join("")}
        </div>
      </div>
    </section>
  `;
}

function renderCheckout() {
  return renderEmptyState(
    "Checkout foundation",
    "Checkout belum diaktifkan.",
    "Halaman ini mengunci ekspektasi route dan layout. Cart persistence, alamat, invoice, stock validation, dan payment akan dibangun bertahap.",
    "/marketplace",
    "Kembali ke marketplace",
  );
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
  member: renderMember,
  profile: (_session, profile) => renderProfile(profile),
  orders: renderOrders,
  consultation: renderConsultation,
  news: renderNews,
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
    "/checkout",
  ]);
  return allowed.has(next) ? next : "/member";
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

async function bootstrap() {
  const route = getRoute();
  const root = document.querySelector("[data-marketplace-root]");
  let session = null;
  let profile = null;

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

  const content = pages[route](session, profile);
  root.innerHTML = renderMarketplaceLayout({ content, activeRoute: route, session });
  document.title = `${marketplaceConfig.titles[route] || "Marketplace"} | Feira`;
  bindAuthForm();
  bindLogout(session);
  bindProfileForm(session);
}

bootstrap();
