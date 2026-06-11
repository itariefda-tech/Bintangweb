# Roadmap Bintang Computer Feira

Website dibangun bertahap dengan prioritas mobile-first, visual premium, dan struktur yang tetap scalable.

---

# Phase 1 - Foundation Setup

## Status

Completed

## Objective

Membangun pondasi visual dan responsive system.

## Tasks

* [x] Setup folder structure
* [x] Setup typography
* [x] Setup color system
* [x] Setup responsive container
* [x] Setup spacing system
* [x] Setup global button style
* [x] Setup card component
* [x] Setup mobile navigation
* [x] Setup responsive utility
* [x] Setup asset folders
* [x] Setup z-index layer system
* [x] Prevent initial horizontal scroll
* [~] Setup Tailwind CSS

## Output

* `index.html` foundation shell
* `css/style.css`
* `css/components.css`
* `css/responsive.css`
* `js/app.js`
* `assets/images/`
* `assets/icons/`
* `assets/branding/`
* `assets/decorations/`

## Notes

Tailwind CSS tidak dipasang sebagai build dependency. Project menggunakan custom CSS modular agar ringan, cepat, dan mudah dikontrol untuk mobile-first.

---

# Phase 2 - Homepage Build

## Status

Completed

## Objective

Membangun landing page utama.

## Tasks

* [x] Hero section
* [x] Problems We Solve section
* [x] Services section
* [x] Why choose us
* [x] Featured solutions
* [x] Process section
* [x] CTA section
* [x] Footer
* [x] Floating WhatsApp
* [x] Python dev server
* [x] NPM dev script

## Output

* Homepage single-page company profile
* Hero visual CSS-based tech illustration
* Problems We Solve section after hero
* Core services snapshot
* Trust / why choose us section
* Featured solutions
* Process flow
* Closing CTA
* Footer
* Floating WhatsApp foundation
* `app.py`
* `package.json` with `npm run dev`

---

# Phase 3 - Core Services Detail

## Status

Completed

## Objective

Membangun section detail layanan.

## Tasks

* [x] IT Procurement section
* [x] Network Solution section
* [x] CCTV section
* [x] PABX section
* [x] Custom App section
* [x] Website section

## Output

* Detailed Services section
* Six detailed service cards
* Feature lists for each service
* Marketing copy per service
* Responsive detail layout: 1 column mobile, 2 columns desktop

---

# Phase 4 - Responsive Hardening

## Status

Completed

## Objective

Memastikan mobile view benar-benar aman.

## Critical Checks

* [x] No overlap
* [x] No horizontal scroll
* [x] No broken grid
* [x] No oversized image
* [x] CTA clickable
* [x] Navbar stable
* [x] Hero safe on mobile
* [x] Spacing comfortable
* [x] Sticky navbar anchor offset
* [x] Drawer scroll-safe on small screens
* [x] Touch target minimum 48px

## Output

* Hardened mobile drawer
* `scroll-margin-top` for section anchors
* Safer card/list wrapping
* Defensive `min-width: 0`
* Safer mobile padding
* Clean process grid borders
* Responsive audit passed at 360, 390, 430, 768, 1024, and 1366px

---

# Phase 5 - UI Polish

## Status

Completed

## Objective

Menambahkan nuansa premium modern.

## Tasks

* [x] Glassmorphism layer
* [x] Gradient enhancement
* [x] Soft shadow refinement
* [x] Hover animation
* [x] Scroll animation
* [x] Icon consistency
* [x] Decorative SVG
* [x] Mobile interaction polish
* [x] Focus visible polish
* [x] Reduced-motion support

## Output

* Premium header scroll state
* Button arrow micro-interaction
* Card hover and shadow refinement
* CSS-based circuit grid background
* `assets/decorations/circuit-line.svg`
* Hero visual polish
* Motion-only reveal behavior
* Safer `prefers-reduced-motion` handling

---

# Phase 6 - Optimization

## Status

Completed

## Objective

Website ringan dan cepat.

## Tasks

* [x] Image/SVG optimization
* [x] Lazy/decode strategy for decorative asset
* [x] Minify CSS
* [x] Minify JS
* [x] Build output generation
* [x] Mobile performance test
* [x] Responsive optimization audit

## Output

* Decorative SVG dimensions added
* `decoding="async"` and `fetchpriority="low"` for decorative image
* `theme-color` meta added
* Below-the-fold sections kept fully renderable for safer visual QA and crawlers
* `scripts/build.js`
* `npm run build`
* `dist/index.html`
* `dist/css/main.min.css`
* `dist/js/app.min.js`
* `dist/assets/`

## Validation

* Dev server response: 200
* Build script runs successfully
* No horizontal scroll at 360, 390, 430, 768, 1024, and 1366px
* CTA remains clickable
* Decorative asset loads and does not block pointer events

---

# Phase 7 - Production Ready

## Status

Technical Completed - Deployment target still required

## Objective

Website siap publish.

## Final Checklist

* [x] Mobile view premium
* [x] Desktop view elegant
* [x] No responsive issue
* [x] SEO meta complete
* [x] OpenGraph image ready
* [x] Contact CTA active
* [x] Real WhatsApp number added
* [x] Real email/contact added
* [x] Final QA completed
* [ ] Deployment target selected

## Expected Output

* Final SEO metadata
* OpenGraph image: `assets/branding/og-image.jpg`
* Favicon: `assets/branding/favicon.svg`
* Web manifest: `site.webmanifest`
* Robots file: `robots.txt`
* Sitemap: `sitemap.xml`
* Production-ready `dist/`
* Final QA report: `docs/production-qa.md`
* Build command: `npm run build`

## Production Blockers

* Select deployment target

---

# Phase 8 - Proof Room

## Status

Implemented foundation - Real customer assets pending

## Objective

Menambahkan bukti kerja yang menghubungkan portofolio, pengalaman customer, dan video proyek sebelum CTA contact.

## Tasks

* [x] Portfolio and testimonial layout
* [x] Three selectable solution showcases
* [x] Keyboard-accessible tab interaction
* [x] Cinematic project film player shell
* [x] Honest empty state for unavailable video
* [x] Pause Process audio when project video plays
* [x] Responsive layout and overflow validation
* [ ] Add approved customer identities and logos
* [ ] Add verified customer comments
* [ ] Add real project photos and video
* [ ] Add video captions

## Output

* `#portfolio` Proof Room between Process and Contact
* Desktop asymmetric portfolio/video layout
* Mobile horizontal project selector
* Future-ready video player behavior
* Detailed specification: `docs/portfolio-testimonial-video-design.md`

---

# Phase 9 - Private Owner Builder

## Status

Completed

## Objective

Memberi owner control room tersembunyi untuk mengelola konten dinamis tanpa mengekspos credential ke frontend.

## Tasks

* [x] Five-second logo hold access
* [x] Environment-based owner credential
* [x] HttpOnly owner session
* [x] Hidden authenticated builder route
* [x] Work video upload
* [x] Work testimonial editor
* [x] Section background upload
* [x] Process audio autoplay toggle
* [x] Persistent server settings and media
* [x] Docker data volume support

## Output

* `owner-builder.html`
* `css/owner-builder.css`
* `js/owner-builder.js`
* Owner API and static runtime in `app.py`
* `.env.example`

---

# Final Vision

Website harus terasa:

* modern
* premium
* trusted
* visually memorable
* not generic
* comfortable on mobile
* scalable for future development
