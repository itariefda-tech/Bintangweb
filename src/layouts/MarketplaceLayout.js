import { renderFloatingCartButton } from "../components/navigation/FloatingCartButton.js";
import { renderSiteHeader } from "../components/navigation/SiteHeader.js";

export function renderMarketplaceLayout({ content, activeRoute, session, unreadCount = 0, cartCount = 0 }) {
  const isActive = (route) => activeRoute === route ? ' aria-current="page"' : "";
  const memberRoutes = ["member", "profile", "notifications", "orders"];
  const isMemberActive = memberRoutes.includes(activeRoute)
    ? ' aria-current="page"'
    : "";
  const siteHeader = renderSiteHeader({
    navigationLabel: "Navigasi marketplace",
    navigationItems: [
      { name: "Marketplace", href: "/marketplace", active: activeRoute === "marketplace" || activeRoute === "product" },
      { name: "IT News", href: "/news", active: activeRoute === "news" },
      { name: "Consultation", href: "/member/consultation", active: activeRoute === "consultation" },
      { name: "Member", href: "/member", active: memberRoutes.includes(activeRoute) },
    ],
    action: session
      ? {
          label: session.user.name,
          href: "/member",
          title: session.user.email,
          active: memberRoutes.includes(activeRoute),
        }
      : {
          label: "Login",
          href: "/login",
          active: activeRoute === "login",
        },
  });
  return `
    <a class="mf-skip-link" href="#mf-main">Lewati ke konten utama</a>
    ${siteHeader}
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
        <div class="mf-footer__actions">
          <a href="/">Kembali ke website utama</a>
          ${session ? '<button type="button" data-logout>Logout</button>' : '<a href="/login">Login member</a>'}
        </div>
      </div>
    </footer>
    ${activeRoute === "checkout" ? "" : renderFloatingCartButton(cartCount, session)}
  `;
}
