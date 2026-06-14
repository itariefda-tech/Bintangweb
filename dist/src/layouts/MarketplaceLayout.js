import { renderFloatingCartButton } from "../components/navigation/FloatingCartButton.js";

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

export function renderMarketplaceLayout({ content, activeRoute, session, unreadCount = 0, cartCount = 0 }) {
  const isActive = (route) => activeRoute === route ? ' aria-current="page"' : "";
  const isMemberActive = ["member", "profile", "notifications", "orders", "consultation"].includes(activeRoute)
    ? ' aria-current="page"'
    : "";
  const accountAction = session
    ? `
      <div class="mf-account">
        <a href="/member" title="${escapeHtml(session.user.email)}">${escapeHtml(session.user.name)}</a>
        <a class="mf-notification-link" href="/member/notifications" aria-label="Notifikasi, ${unreadCount} belum dibaca">
          Notifikasi${unreadCount ? `<strong>${unreadCount}</strong>` : ""}
        </a>
        <button type="button" data-logout>Logout</button>
      </div>
    `
    : '<a class="mf-header__login" href="/login">Login</a>';
  return `
    <a class="mf-skip-link" href="#mf-main">Lewati ke konten utama</a>
    <header class="mf-header">
      <div class="mf-container mf-header__inner">
        <a class="mf-brand" href="/marketplace" aria-label="Feira Marketplace">
          <img src="/assets/images/logo_bcf.webp" width="54" height="54" alt="">
          <span><strong>Feira</strong><small>Technology ecosystem</small></span>
        </a>
        <nav class="mf-nav" aria-label="Navigasi marketplace">
          <a href="/marketplace"${isActive("marketplace")}>Marketplace</a>
          <a href="/news"${isActive("news")}>IT News</a>
          <a href="/member/consultation"${isActive("consultation")}>Consultation</a>
          <a href="/member"${isMemberActive}>Member</a>
        </nav>
        ${accountAction}
      </div>
    </header>
    <main id="mf-main">${content}</main>
    <nav class="mf-mobile-nav" aria-label="Navigasi marketplace mobile">
        <a href="/marketplace"${isActive("marketplace")}><span>Market</span></a>
        <a href="/news"${isActive("news")}><span>IT News</span></a>
        ${session ? `
          <a href="/member/notifications"${isActive("notifications")}><span>Notifikasi${unreadCount ? ` (${unreadCount})` : ""}</span></a>
          <a href="/member"${isMemberActive}><span>Member</span></a>
        ` : `
          <a href="/member/consultation"${isActive("consultation")}><span>Konsultasi</span></a>
          <a href="/login"${isActive("login")}><span>Login</span></a>
        `}
      </nav>
    <footer class="mf-footer">
      <div class="mf-container mf-footer__inner">
        <div><strong>Feira Technology Ecosystem</strong><p>Marketplace, consultation, member, dan insight dalam satu pondasi modular.</p></div>
        <a href="/">Kembali ke website utama</a>
      </div>
    </footer>
    ${activeRoute === "checkout" ? "" : renderFloatingCartButton(cartCount, session)}
  `;
}
