# Production QA Report

Date: 2026-06-08

## Scope

Final QA for Bintang Computer Feira single-page company profile before deployment.

## Technical Checks

* [x] Dev server responds with HTTP 200
* [x] Production build runs with `npm run build`
* [x] `dist/index.html` generated
* [x] `dist/css/main.min.css` generated
* [x] `dist/js/app.min.js` generated
* [x] Assets copied to `dist/assets/`
* [x] `robots.txt` copied to `dist/`
* [x] `sitemap.xml` copied to `dist/`
* [x] `site.webmanifest` copied to `dist/`

## Responsive Checks

* [x] 360px
* [x] 390px
* [x] 430px
* [x] 768px
* [x] 1024px
* [x] 1366px

## Layout Checks

* [x] No horizontal scroll
* [x] No non-decorative element overflowing viewport
* [x] Mobile drawer opens and locks body scroll
* [x] CTA buttons remain clickable
* [x] Minimum visible touch target is 48px
* [x] Decorative SVG uses `pointer-events: none`
* [x] Service grid responds correctly
* [x] Detail service layout responds correctly

## SEO Checks

* [x] Page title
* [x] Meta description
* [x] Canonical URL
* [x] Robots meta
* [x] OpenGraph metadata
* [x] Twitter card metadata
* [x] JSON-LD structured data
* [x] Sitemap
* [x] Robots file
* [x] Web manifest
* [x] Favicon
* [x] OpenGraph image
* [x] OpenGraph image optimized to JPEG

## Production Risks

* [x] WhatsApp number configured: `08170725258`
* [x] Email configured: `it.ariefda@gmail.com`
* [x] Production domain confirmed: `https://feira.my.id/`
* [ ] Choose deployment target

## Deployment Candidate

Use the `dist/` folder as the static deployment output after contact/domain data is confirmed.
