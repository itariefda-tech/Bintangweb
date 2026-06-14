const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const mobileLinks = document.querySelectorAll(".mobile-nav a, .mobile-menu .button");
const siteHeader = document.querySelector("[data-site-header]");

const defaultPublicSettings = {
  processAudioAutoplay: true,
  workVideo: "",
  clients: [],
  backgrounds: {},
  testimonials: {},
};

function setManagedBackground(selector, url, overlay) {
  const element = document.querySelector(selector);
  if (!element || !url) return;
  element.style.backgroundImage = `${overlay}, url("${url}")`;
  element.style.backgroundPosition = "center";
  element.style.backgroundRepeat = "no-repeat";
  element.style.backgroundSize = "cover";
}

function initialsFromName(name) {
  const words = name.trim().split(/\s+/).filter(Boolean);
  if (!words.length) return "BCF";
  return words.slice(0, 2).map((word) => word[0]).join("").toUpperCase();
}

function applyClientList(clients) {
  const list = document.querySelector("[data-client-list]");
  if (!list) return;

  const normalizedClients = Array.isArray(clients)
    ? clients.filter((client) => typeof client === "string" && client.trim())
    : [];

  if (!normalizedClients.length) {
    const empty = document.createElement("p");
    empty.className = "client-panel-empty";
    empty.textContent = "Client list is being prepared.";
    list.replaceChildren(empty);
    return;
  }

  const createGroup = (isDuplicate = false) => {
    const group = document.createElement("div");
    group.className = "client-panel-group";
    if (isDuplicate) group.setAttribute("aria-hidden", "true");

    normalizedClients.forEach((client, index) => {
      const item = document.createElement("div");
      item.className = "client-panel-name";
      const number = document.createElement("small");
      const name = document.createElement("strong");
      number.textContent = String(index + 1).padStart(2, "0");
      name.textContent = client.trim();
      item.append(number, name);
      group.append(item);
    });

    return group;
  };

  const track = document.createElement("div");
  track.className = "client-panel-track";
  track.style.setProperty("--client-roll-duration", `${Math.max(14, normalizedClients.length * 3.5)}s`);
  track.append(createGroup(), createGroup(true));
  list.replaceChildren(track);
}

function applyPublicSettings(settings) {
  const backgrounds = settings.backgrounds || {};
  setManagedBackground(
    ".site-header",
    backgrounds.header,
    "linear-gradient(90deg, rgba(231, 241, 246, 0.9), rgba(231, 241, 246, 0.72))"
  );
  setManagedBackground(
    ".hero-section",
    backgrounds.hero,
    "linear-gradient(90deg, rgba(255, 252, 246, 0.86), rgba(255, 252, 246, 0.18))"
  );
  setManagedBackground(
    ".about-section",
    backgrounds.about,
    "linear-gradient(110deg, rgba(255, 252, 246, 0.9), rgba(220, 239, 247, 0.42))"
  );
  setManagedBackground(
    ".why-section",
    backgrounds.solutions,
    "linear-gradient(110deg, rgba(255, 252, 246, 0.9), rgba(220, 239, 247, 0.3))"
  );
  setManagedBackground(
    ".process-section",
    backgrounds.process,
    "linear-gradient(180deg, rgba(4, 10, 18, 0.32), rgba(4, 10, 18, 0.68))"
  );
  setManagedBackground(
    ".cta-section",
    backgrounds.contact,
    "linear-gradient(180deg, rgba(15, 52, 81, 0.28), rgba(15, 52, 81, 0.5))"
  );
  setManagedBackground(
    ".site-footer",
    backgrounds.footer,
    "linear-gradient(180deg, rgba(4, 15, 27, 0.34), rgba(3, 13, 24, 0.72))"
  );

  Object.entries(settings.testimonials || {}).forEach(([caseId, testimonial]) => {
    const proofCase = document.querySelector(`[data-proof-case="${caseId}"]`);
    if (!proofCase || !testimonial?.quote) return;

    const name = testimonial.name || "Verified Client";
    const normalizedMeta = [testimonial.role, testimonial.company]
      .filter(Boolean)
      .join(" / ");
    proofCase.querySelector("[data-testimonial-quote]").textContent = testimonial.quote;
    proofCase.querySelector("[data-testimonial-name]").textContent = name;
    proofCase.querySelector("[data-testimonial-meta]").textContent =
      normalizedMeta || "Verified project feedback";
    proofCase.querySelector("[data-testimonial-monogram]").textContent =
      initialsFromName(name);
  });

  const projectFilm = document.querySelector("[data-project-film]");
  if (projectFilm && settings.workVideo) {
    projectFilm.dataset.videoSrc = settings.workVideo;
    const filmLabel = projectFilm.querySelector(".project-film-meta span:last-child");
    if (filmLabel) filmLabel.textContent = "Ready to play";
  }

  applyClientList(settings.clients);
}

const publicSettingsPromise = fetch("/api/public-settings", {
  credentials: "same-origin",
})
  .then((response) => (response.ok ? response.json() : defaultPublicSettings))
  .catch(() => defaultPublicSettings)
  .then((settings) => {
    applyPublicSettings(settings);
    return settings;
  });

function frameThrottle(callback) {
  let frameId = 0;

  return (...args) => {
    if (frameId) return;

    frameId = window.requestAnimationFrame(() => {
      frameId = 0;
      callback(...args);
    });
  };
}

function setMenuState(isOpen) {
  if (!menuToggle || !mobileMenu) return;

  menuToggle.setAttribute("aria-expanded", String(isOpen));
  menuToggle.setAttribute("aria-label", isOpen ? "Tutup menu" : "Buka menu");
  mobileMenu.hidden = !isOpen;
  document.body.classList.toggle("menu-open", isOpen);
}

menuToggle?.addEventListener("click", () => {
  const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
  setMenuState(!isOpen);
});

mobileLinks.forEach((link) => {
  link.addEventListener("click", () => setMenuState(false));
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape") {
    setMenuState(false);
  }
});

const updateResponsiveMenu = frameThrottle(() => {
  if (window.matchMedia("(min-width: 1024px)").matches) {
    setMenuState(false);
  }
});
window.addEventListener("resize", updateResponsiveMenu, { passive: true });

function updateHeaderState() {
  siteHeader?.classList.toggle("is-scrolled", window.scrollY > 10);
}

updateHeaderState();
window.addEventListener("scroll", frameThrottle(updateHeaderState), {
  passive: true,
});

const viewportSections = document.querySelectorAll(
  ".why-section, .process-section"
);

function fitDesktopSections() {
  const isDesktop = window.innerWidth >= 900;
  const headerHeight = siteHeader?.getBoundingClientRect().height ?? 0;
  const sectionHeight = Math.max(0, window.innerHeight - headerHeight);

  document.documentElement.style.setProperty(
    "--sticky-offset",
    `${headerHeight}px`
  );
  document.documentElement.style.setProperty(
    "--desktop-section-height",
    `${sectionHeight}px`
  );

  viewportSections.forEach((section) => {
    const content = section.querySelector(":scope > .container");
    section.classList.toggle("desktop-viewport-section", isDesktop);

    if (!content || !isDesktop) {
      section.style.removeProperty("--section-content-scale");
      return;
    }

    section.style.setProperty("--section-content-scale", "1");

    const styles = getComputedStyle(section);
    const availableHeight =
      section.clientHeight -
      parseFloat(styles.paddingTop) -
      parseFloat(styles.paddingBottom);
    const availableWidth = section.clientWidth;
    const contentHeight = content.scrollHeight;
    const contentWidth = section.classList.contains("service-detail-section")
      ? availableWidth
      : content.scrollWidth;
    const scale = Math.min(
      1,
      availableHeight / contentHeight,
      availableWidth / contentWidth
    );

    section.style.setProperty(
      "--section-content-scale",
      String(Math.max(0.25, scale))
    );
  });
}

fitDesktopSections();
const scheduleDesktopSectionFit = frameThrottle(fitDesktopSections);
document.fonts?.ready.then(scheduleDesktopSectionFit);
window.addEventListener("load", scheduleDesktopSectionFit);
window.addEventListener("resize", scheduleDesktopSectionFit, { passive: true });

if (siteHeader && "ResizeObserver" in window) {
  new ResizeObserver(scheduleDesktopSectionFit).observe(siteHeader);
}

const revealItems = document.querySelectorAll(
  ".section-header, .problem-card, .problem-closing, .about-copy, .about-card, .about-quote, .service-card, .detail-card, .why-intro, .reason-list article, .why-path, .highlight-card, .process-step, .proof-dossier, .project-film, .client-panel, .cta-panel"
);

if (revealItems.length && "IntersectionObserver" in window) {
  document.body.classList.add("reveal-ready");
  revealItems.forEach((item) => item.classList.add("reveal-item"));

  const revealObserver = new IntersectionObserver(
    (entries, observer) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
  );

  revealItems.forEach((item) => revealObserver.observe(item));
}

const processAudio = document.querySelector("[data-process-audio]");

publicSettingsPromise.then((settings) => {
if (processAudio && settings.processAudioAutoplay) {
  const processSection = processAudio.closest(".process-section");
  const previewDuration = 60;
  let processIsVisible = false;

  async function startProcessAudio() {
    if (
      !processIsVisible ||
      processAudio.currentTime >= previewDuration ||
      !processAudio.paused
    ) {
      return;
    }

    try {
      await processAudio.play();
    } catch {
      // Browsers may require a user gesture before allowing sound.
    }
  }

  processAudio.addEventListener("timeupdate", () => {
    if (processAudio.currentTime >= previewDuration) {
      processAudio.pause();
      processAudio.currentTime = previewDuration;
    }
  });

  if (processSection && "IntersectionObserver" in window) {
    const processAudioObserver = new IntersectionObserver(
      ([entry]) => {
        processIsVisible = entry.isIntersecting;

        if (processIsVisible) {
          startProcessAudio();
        } else if (!processAudio.paused) {
          processAudio.pause();
        }
      },
      { threshold: 0.35 }
    );

    processAudioObserver.observe(processSection);
  } else {
    processIsVisible = true;
    startProcessAudio();
  }

  ["pointerdown", "touchstart", "keydown"].forEach((eventName) => {
    document.addEventListener(eventName, startProcessAudio, {
      passive: true,
    });
  });
}
});

const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
const proofRooms = document.querySelectorAll("[data-proof-room]");

proofRooms.forEach((proofRoom) => {
  const tabs = Array.from(proofRoom.querySelectorAll("[data-proof-tab]"));
  const cases = Array.from(proofRoom.querySelectorAll("[data-proof-case]"));

  if (!tabs.length || tabs.length !== cases.length) return;

  proofRoom.classList.add("proof-enhanced");

  function activateCase(caseId, focusTab = false) {
    const activeIndex = tabs.findIndex((tab) => tab.dataset.proofTab === caseId);
    if (activeIndex < 0) return;

    tabs.forEach((tab, index) => {
      const isActive = index === activeIndex;
      tab.classList.toggle("is-active", isActive);
      tab.setAttribute("aria-selected", String(isActive));
      tab.tabIndex = isActive ? 0 : -1;
      if (isActive && focusTab) tab.focus();
    });

    cases.forEach((proofCase) => {
      const isActive = proofCase.dataset.proofCase === caseId;
      proofCase.classList.toggle("is-active", isActive);
      proofCase.hidden = !isActive;
    });

    const tabList = tabs[activeIndex].parentElement;
    tabList?.scrollTo({
      left: Math.max(0, tabs[activeIndex].offsetLeft - tabList.offsetLeft),
      behavior: prefersReducedMotion.matches ? "auto" : "smooth",
    });
    scheduleDesktopSectionFit();
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => activateCase(tab.dataset.proofTab));
    tab.addEventListener("keydown", (event) => {
      if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) {
        return;
      }

      event.preventDefault();
      let nextIndex = index;

      if (event.key === "ArrowLeft") nextIndex = (index - 1 + tabs.length) % tabs.length;
      if (event.key === "ArrowRight") nextIndex = (index + 1) % tabs.length;
      if (event.key === "Home") nextIndex = 0;
      if (event.key === "End") nextIndex = tabs.length - 1;

      activateCase(tabs[nextIndex].dataset.proofTab, true);
    });
  });

  activateCase(tabs.find((tab) => tab.classList.contains("is-active"))?.dataset.proofTab ?? tabs[0].dataset.proofTab);
});

const projectFilms = document.querySelectorAll("[data-project-film]");

projectFilms.forEach((film) => {
  const video = film.querySelector("[data-project-video]");
  const playButton = film.querySelector("[data-project-play]");
  const status = film.querySelector("[data-project-status]");
  let statusTimer;

  if (!video || !playButton || !status) return;

  function showStatus(message) {
    window.clearTimeout(statusTimer);
    status.textContent = message;
    status.classList.add("is-visible");
    statusTimer = window.setTimeout(() => {
      status.classList.remove("is-visible");
    }, 5200);
  }

  playButton.addEventListener("click", async () => {
    const videoSource = film.dataset.videoSrc?.trim();
    if (!videoSource) {
      showStatus("Project film sedang disiapkan. Player akan aktif setelah video proyek asli tersedia.");
      return;
    }

    if (!video.src) {
      video.src = videoSource;
      video.load();
    }

    processAudio?.pause();
    video.hidden = false;
    playButton.hidden = true;

    try {
      await video.play();
    } catch {
      playButton.hidden = false;
      video.hidden = true;
      showStatus("Video belum dapat diputar. Silakan coba kembali.");
    }
  });

  video.addEventListener("play", () => processAudio?.pause());

  video.addEventListener("ended", () => {
    playButton.hidden = false;
    video.hidden = true;
    showStatus("Film selesai. Putar kembali atau diskusikan sistem berikutnya bersama kami.");
  });

  if ("IntersectionObserver" in window) {
    new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting && !video.paused) video.pause();
      },
      { threshold: 0.15 }
    ).observe(film);
  }
});

const ownerTrigger = document.querySelector("[data-owner-trigger]");
const ownerDialog = document.querySelector("[data-owner-dialog]");
const ownerLoginForm = document.querySelector("[data-owner-login-form]");
const ownerPassword = document.querySelector("[data-owner-password]");
const ownerError = document.querySelector("[data-owner-error]");
let ownerHoldTimer;
let ownerHoldStartedAt = 0;

function cancelOwnerHold() {
  window.clearTimeout(ownerHoldTimer);
  ownerHoldTimer = undefined;
  ownerHoldStartedAt = 0;
  ownerTrigger?.classList.remove("is-owner-holding");
}

function openOwnerAccess() {
  cancelOwnerHold();
  if (!ownerDialog?.open) ownerDialog?.showModal();
  ownerPassword?.focus();
}

ownerTrigger?.addEventListener("pointerdown", (event) => {
  if (event.button !== 0) return;
  ownerHoldStartedAt = Date.now();
  ownerTrigger.classList.add("is-owner-holding");
  ownerHoldTimer = window.setTimeout(openOwnerAccess, 5000);
});

["pointerup", "pointercancel", "pointerleave"].forEach((eventName) => {
  ownerTrigger?.addEventListener(eventName, () => {
    if (ownerHoldStartedAt && Date.now() - ownerHoldStartedAt < 5000) {
      cancelOwnerHold();
    }
  });
});

ownerTrigger?.addEventListener("contextmenu", (event) => event.preventDefault());
document.querySelector("[data-owner-close]")?.addEventListener("click", () => {
  ownerDialog?.close();
});

ownerDialog?.addEventListener("click", (event) => {
  if (event.target === ownerDialog) ownerDialog.close();
});

ownerLoginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  ownerError.textContent = "";
  const submitButton = ownerLoginForm.querySelector("[type='submit']");
  submitButton.disabled = true;

  try {
    const response = await fetch("/api/owner/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ password: ownerPassword.value }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "Akses owner gagal.");
    window.location.assign("/owner-builder");
  } catch (error) {
    ownerError.textContent = error.message;
    ownerPassword.select();
  } finally {
    submitButton.disabled = false;
  }
});

const serviceCarousels = document.querySelectorAll("[data-service-carousel]");

serviceCarousels.forEach((carousel) => {
  const track = carousel.querySelector("[data-service-carousel-track]");
  const cards = Array.from(track?.querySelectorAll(".detail-card") ?? []);
  const previousButton = carousel.querySelector("[data-service-carousel-prev]");
  const nextButton = carousel.querySelector("[data-service-carousel-next]");
  const currentLabel = carousel.querySelector("[data-service-carousel-current]");
  const serviceDetailSection = carousel.closest(".service-detail-section");
  const orb = serviceDetailSection?.querySelector("[data-service-detail-orb]");

  if (!track || cards.length < 2) return;

  let currentIndex = 0;
  let autoSlideTimer;
  let resumeTimer;
  let isPaused = false;
  let isTouchStopped = false;

  function updateCurrentLabel() {
    if (currentLabel) {
      currentLabel.textContent = String(currentIndex + 1).padStart(2, "0");
    }
  }

  function randomBetween(min, max) {
    return Math.random() * (max - min) + min;
  }

  function moveDecorativeOrb() {
    if (!orb) return;

    orb.style.setProperty(
      "--orb-x",
      `${randomBetween(3, 97).toFixed(2)}%`
    );
    orb.style.setProperty(
      "--orb-y",
      `${randomBetween(6, 94).toFixed(2)}%`
    );
    orb.style.setProperty(
      "--orb-drift-x",
      `${randomBetween(-12, 12).toFixed(2)}px`
    );
    orb.style.setProperty(
      "--orb-drift-y",
      `${randomBetween(-11, 11).toFixed(2)}px`
    );
    orb.style.setProperty("--orb-scale", randomBetween(0.88, 1.12).toFixed(2));
    orb.style.setProperty(
      "--orb-duration",
      `${randomBetween(3.8, 6.2).toFixed(2)}s`
    );
  }

  function goToCard(index, behavior = "smooth") {
    currentIndex = (index + cards.length) % cards.length;
    track.scrollTo({
      left: cards[currentIndex].offsetLeft - cards[0].offsetLeft,
      behavior,
    });
    updateCurrentLabel();
    moveDecorativeOrb();
  }

  function stopAutoSlide() {
    window.clearInterval(autoSlideTimer);
  }

  function startAutoSlide() {
    stopAutoSlide();
    if (
      isPaused ||
      isTouchStopped ||
      prefersReducedMotion.matches ||
      document.hidden
    ) return;
    autoSlideTimer = window.setInterval(() => {
      goToCard(currentIndex + 1);
    }, 8000);
  }

  function pauseAutoSlide() {
    isPaused = true;
    window.clearTimeout(resumeTimer);
    stopAutoSlide();
  }

  function resumeAutoSlide(delay = 0) {
    if (isTouchStopped) return;
    window.clearTimeout(resumeTimer);
    resumeTimer = window.setTimeout(() => {
      isPaused = false;
      startAutoSlide();
    }, delay);
  }

  function syncIndexFromScroll() {
    const trackLeft = track.getBoundingClientRect().left;
    let closestIndex = 0;
    let closestDistance = Number.POSITIVE_INFINITY;

    cards.forEach((card, index) => {
      const distance = Math.abs(card.getBoundingClientRect().left - trackLeft);
      if (distance < closestDistance) {
        closestDistance = distance;
        closestIndex = index;
      }
    });

    if (closestIndex !== currentIndex) {
      currentIndex = closestIndex;
      updateCurrentLabel();
      moveDecorativeOrb();
    }
  }

  previousButton?.addEventListener("click", () => {
    goToCard(currentIndex - 1);
    resumeAutoSlide(6000);
  });

  nextButton?.addEventListener("click", () => {
    goToCard(currentIndex + 1);
    resumeAutoSlide(6000);
  });

  carousel.addEventListener("mouseenter", pauseAutoSlide);
  carousel.addEventListener("mouseleave", () => resumeAutoSlide(1500));
  carousel.addEventListener("focusin", pauseAutoSlide);
  carousel.addEventListener("focusout", () => resumeAutoSlide(1500));
  track.addEventListener("pointerdown", (event) => {
    if (event.pointerType === "touch") isTouchStopped = true;
    pauseAutoSlide();
  });
  track.addEventListener("pointerup", () => {
    if (!isTouchStopped) resumeAutoSlide(5000);
  });
  track.addEventListener("scroll", frameThrottle(syncIndexFromScroll), {
    passive: true,
  });

  document.addEventListener("visibilitychange", startAutoSlide);
  prefersReducedMotion.addEventListener?.("change", startAutoSlide);
  window.addEventListener(
    "resize",
    frameThrottle(() => goToCard(currentIndex, "auto")),
    { passive: true }
  );

  updateCurrentLabel();
  moveDecorativeOrb();
  startAutoSlide();
});

const mobileAutoSliders = document.querySelectorAll("[data-mobile-auto-slider]");
const mobileSliderMedia = window.matchMedia("(max-width: 767.98px)");

mobileAutoSliders.forEach((track) => {
  const cards = Array.from(
    track.querySelectorAll(
      ".about-card, .about-quote, .service-card, .reason-card, .why-path, " +
        ".highlight-card, .process-step, .proof-dossier, .project-film"
    )
  );

  if (cards.length < 2) return;

  let currentIndex = 0;
  let autoSlideTimer;
  let isInteracting = false;
  let isVisible = false;

  function stopAutoSlide() {
    window.clearTimeout(autoSlideTimer);
  }

  function canAutoSlide() {
    return (
      mobileSliderMedia.matches &&
      !prefersReducedMotion.matches &&
      !document.hidden &&
      !isInteracting &&
      isVisible
    );
  }

  function scheduleAutoSlide(delay = 4500) {
    stopAutoSlide();
    if (!canAutoSlide()) return;

    autoSlideTimer = window.setTimeout(() => {
      currentIndex = (currentIndex + 1) % cards.length;
      track.scrollTo({
        left: cards[currentIndex].offsetLeft - cards[0].offsetLeft,
        behavior: "smooth",
      });
      scheduleAutoSlide();
    }, delay);
  }

  function syncIndexFromScroll() {
    const trackLeft = track.getBoundingClientRect().left;
    let closestIndex = 0;
    let closestDistance = Number.POSITIVE_INFINITY;

    cards.forEach((card, index) => {
      const distance = Math.abs(card.getBoundingClientRect().left - trackLeft);
      if (distance < closestDistance) {
        closestDistance = distance;
        closestIndex = index;
      }
    });

    currentIndex = closestIndex;
  }

  function pauseForInteraction() {
    if (!mobileSliderMedia.matches) return;
    isInteracting = true;
    stopAutoSlide();
  }

  track.addEventListener("pointerdown", pauseForInteraction);
  track.addEventListener("scroll", frameThrottle(syncIndexFromScroll), {
    passive: true,
  });

  const visibilityObserver = new IntersectionObserver(
    ([entry]) => {
      isVisible = entry.isIntersecting && entry.intersectionRatio >= 0.35;
      if (isVisible) {
        syncIndexFromScroll();
        scheduleAutoSlide(2500);
      } else {
        stopAutoSlide();
      }
    },
    { threshold: [0, 0.35] }
  );

  visibilityObserver.observe(track);

  document.addEventListener("visibilitychange", () => scheduleAutoSlide());
  mobileSliderMedia.addEventListener?.("change", () => scheduleAutoSlide());
  prefersReducedMotion.addEventListener?.("change", () => scheduleAutoSlide());
});
