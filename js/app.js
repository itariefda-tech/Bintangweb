const menuToggle = document.querySelector("[data-menu-toggle]");
const mobileMenu = document.querySelector("[data-mobile-menu]");
const mobileLinks = document.querySelectorAll(".mobile-nav a, .mobile-menu .button");
const siteHeader = document.querySelector("[data-site-header]");

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

window.addEventListener("resize", () => {
  if (window.matchMedia("(min-width: 1024px)").matches) {
    setMenuState(false);
  }
});

function updateHeaderState() {
  siteHeader?.classList.toggle("is-scrolled", window.scrollY > 10);
}

updateHeaderState();
window.addEventListener("scroll", updateHeaderState, { passive: true });

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
document.fonts?.ready.then(fitDesktopSections);
window.addEventListener("load", fitDesktopSections);
window.addEventListener("resize", fitDesktopSections);

if (siteHeader && "ResizeObserver" in window) {
  new ResizeObserver(fitDesktopSections).observe(siteHeader);
}

const revealItems = document.querySelectorAll(
  ".section-header, .problem-card, .problem-closing, .about-copy, .about-card, .about-quote, .service-card, .detail-card, .why-intro, .reason-list article, .why-path, .highlight-card, .process-audio, .process-step, .cta-panel"
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

const processAudioPanel = document.querySelector("[data-process-audio]");

if (processAudioPanel) {
  const audio = processAudioPanel.querySelector("[data-process-audio-source]");
  const toggle = processAudioPanel.querySelector("[data-process-audio-toggle]");
  const status = processAudioPanel.querySelector("[data-process-audio-status]");
  const time = processAudioPanel.querySelector("[data-process-audio-time]");
  const progress = processAudioPanel.querySelector("[data-process-audio-progress]");
  const progressFill = processAudioPanel.querySelector(
    "[data-process-audio-progress-fill]"
  );
  const processSection = processAudioPanel.closest(".process-section");
  const previewDuration = 60;

  function formatAudioTime(seconds) {
    const safeSeconds = Math.max(0, Math.min(previewDuration, seconds));
    const minutes = Math.floor(safeSeconds / 60);
    const remainingSeconds = Math.floor(safeSeconds % 60);
    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  }

  function updateProcessAudio() {
    if (!audio) return;

    const currentTime = Math.min(audio.currentTime, previewDuration);
    const percentage = (currentTime / previewDuration) * 100;
    const isPlaying = !audio.paused && currentTime < previewDuration;

    processAudioPanel.classList.toggle("is-playing", isPlaying);
    toggle?.setAttribute("aria-pressed", String(isPlaying));
    toggle?.setAttribute(
      "aria-label",
      isPlaying ? "Jeda soundtrack Process" : "Putar soundtrack Process"
    );

    if (status) {
      status.textContent = isPlaying
        ? "Now playing: 60-second Process soundscape"
        : currentTime >= previewDuration
          ? "Preview finished - play again"
          : "Play the first 60 seconds";
    }

    if (time) {
      time.textContent = `${formatAudioTime(currentTime)} / 01:00`;
    }

    if (progressFill) {
      progressFill.style.width = `${percentage}%`;
    }

    progress?.setAttribute("aria-valuenow", String(Math.floor(currentTime)));
  }

  function stopAtPreviewEnd() {
    if (!audio || audio.currentTime < previewDuration) return;
    audio.pause();
    audio.currentTime = previewDuration;
    updateProcessAudio();
  }

  toggle?.addEventListener("click", async () => {
    if (!audio) return;

    if (!audio.paused) {
      audio.pause();
      return;
    }

    if (audio.currentTime >= previewDuration - 0.05) {
      audio.currentTime = 0;
    }

    try {
      await audio.play();
    } catch {
      if (status) status.textContent = "Audio could not be played";
    }
  });

  audio?.addEventListener("play", updateProcessAudio);
  audio?.addEventListener("pause", updateProcessAudio);
  audio?.addEventListener("timeupdate", () => {
    stopAtPreviewEnd();
    updateProcessAudio();
  });

  if (processSection && "IntersectionObserver" in window) {
    const processAudioObserver = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting && audio && !audio.paused) {
          audio.pause();
        }
      },
      { threshold: 0.08 }
    );

    processAudioObserver.observe(processSection);
  }

  updateProcessAudio();
}

const serviceCarousels = document.querySelectorAll("[data-service-carousel]");
const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

serviceCarousels.forEach((carousel) => {
  const track = carousel.querySelector("[data-service-carousel-track]");
  const cards = Array.from(track?.querySelectorAll(".detail-card") ?? []);
  const previousButton = carousel.querySelector("[data-service-carousel-prev]");
  const nextButton = carousel.querySelector("[data-service-carousel-next]");
  const currentLabel = carousel.querySelector("[data-service-carousel-current]");

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

  function goToCard(index, behavior = "smooth") {
    currentIndex = (index + cards.length) % cards.length;
    track.scrollTo({
      left: cards[currentIndex].offsetLeft - cards[0].offsetLeft,
      behavior,
    });
    updateCurrentLabel();
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

    currentIndex = closestIndex;
    updateCurrentLabel();
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
  track.addEventListener("scroll", syncIndexFromScroll, { passive: true });

  document.addEventListener("visibilitychange", startAutoSlide);
  prefersReducedMotion.addEventListener?.("change", startAutoSlide);
  window.addEventListener("resize", () => goToCard(currentIndex, "auto"));

  updateCurrentLabel();
  startAutoSlide();
});
