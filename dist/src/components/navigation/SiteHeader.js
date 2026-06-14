const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

function renderNavigation(className, label, items) {
  return `
    <nav class="${className}" aria-label="${label}">
      ${items.map(({ name, href, active }) =>
        `<a href="${href}"${active ? ' aria-current="page"' : ""}>${name}</a>`
      ).join("")}
    </nav>
  `;
}

export function renderSiteHeader({
  navigationItems,
  action,
  navigationLabel = "Navigasi utama",
} = {}) {
  const items = navigationItems || [
    { name: "Home", href: "/#home" },
    { name: "About", href: "/#about" },
    { name: "Services", href: "/#services" },
    { name: "Solutions", href: "/#solutions" },
    { name: "Process", href: "/#process" },
    { name: "Work", href: "/#portfolio" },
    { name: "Contact", href: "/#contact" },
  ];
  const headerAction = action || {
    label: "Product",
    href: "/marketplace",
    active: true,
  };
  const actionLabel = escapeHtml(headerAction.label);
  const actionTitle = headerAction.title ? ` title="${escapeHtml(headerAction.title)}"` : "";
  const actionCurrent = headerAction.active ? ' aria-current="page"' : "";

  return `
    <header class="site-header" data-site-header>
      <div class="mf-container nav-shell">
        <a class="brand" href="/#home" aria-label="Bintang Computer Feira">
          <span class="brand-mark" aria-hidden="true">
            <img src="/assets/images/logo_bcf.webp" width="1536" height="1024" alt="">
          </span>
          <span class="brand-copy">
            <span class="brand-name">Bintang Computer Feira</span>
            <span class="brand-label">Consultan IT</span>
          </span>
        </a>
        ${renderNavigation("desktop-nav", navigationLabel, items)}
        <a class="button button-small button-primary nav-cta" href="${headerAction.href}"${actionTitle}${actionCurrent}>${actionLabel}</a>
        <button
          class="menu-toggle"
          type="button"
          aria-label="Buka menu"
          aria-expanded="false"
          aria-controls="marketplace-mobile-menu"
          data-menu-toggle
        >
          <span></span>
          <span></span>
        </button>
      </div>
      <div class="mobile-menu" id="marketplace-mobile-menu" data-mobile-menu hidden>
        <div class="mf-container mobile-menu-panel">
          ${renderNavigation("mobile-nav", `${navigationLabel} mobile`, items)}
          <a class="button button-primary" href="${headerAction.href}"${actionTitle}${actionCurrent}>${actionLabel}</a>
        </div>
      </div>
    </header>
  `;
}

export function bindSiteHeader() {
  const header = document.querySelector("[data-site-header]");
  const toggle = header?.querySelector("[data-menu-toggle]");
  const menu = header?.querySelector("[data-mobile-menu]");
  if (!header || !toggle || !menu) return;

  const closeMenu = () => {
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Buka menu");
    menu.hidden = true;
    document.body.classList.remove("menu-open");
  };

  toggle.addEventListener("click", () => {
    const isOpen = toggle.getAttribute("aria-expanded") === "true";
    if (isOpen) {
      closeMenu();
      return;
    }
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Tutup menu");
    menu.hidden = false;
    document.body.classList.add("menu-open");
  });
  menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
  window.addEventListener("resize", () => {
    if (window.innerWidth >= 1024) closeMenu();
  }, { passive: true });

  const updateHeaderState = () => header.classList.toggle("is-scrolled", window.scrollY > 10);
  updateHeaderState();
  window.addEventListener("scroll", updateHeaderState, { passive: true });

  fetch("/api/public-settings", { credentials: "same-origin" })
    .then((response) => response.ok ? response.json() : null)
    .then((settings) => {
      const background = settings?.backgrounds?.header;
      if (!background) return;
      header.style.backgroundImage =
        `linear-gradient(90deg, rgba(231, 241, 246, 0.9), rgba(231, 241, 246, 0.72)), url("${background}")`;
      header.style.backgroundPosition = "center";
      header.style.backgroundRepeat = "no-repeat";
      header.style.backgroundSize = "cover";
    })
    .catch(() => {});
}
