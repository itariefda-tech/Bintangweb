const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const mobileLinks = document.querySelectorAll(".mobile-nav a, .mobile-menu .button");
const siteHeader = document.querySelector("[data-site-header]");

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
  "main > .section:not(.hero-section):not(.cta-section)"
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
  ".section-header, .problem-card, .problem-closing, .about-copy, .about-card, .about-quote, .service-card, .detail-card, .why-intro, .reason-list article, .why-path, .highlight-card, .process-step, .cta-panel"
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

if (processAudio) {
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

const serviceCarousels = document.querySelectorAll("[data-service-carousel]");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

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
    if (isPaused || prefersReducedMotion.matches || document.hidden) return;
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
  track.addEventListener("pointerdown", pauseAutoSlide);
  track.addEventListener("pointerup", () => resumeAutoSlide(5000));
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
