# Feira Marketplace

## UI / UX Guide System

> UI/UX Feira Marketplace harus terasa seperti perpaduan modern IT ecosystem, premium startup, dan mini marketplace futuristik yang tetap ringan serta nyaman digunakan di mobile.

---

# UI/UX PHILOSOPHY

## Core Experience

User harus merasa:

* modern
* premium
* profesional
* ringan
* nyaman
* tidak ribet
* cepat dipahami
* trusted
* tech consultant vibes

Marketplace tidak boleh terasa seperti:

* toko online murah
* dashboard admin jadul
* template bootstrap lama
* marketplace penuh spam visual

---

# VISUAL PERSONALITY

## Main Identity

Feira Marketplace harus terasa seperti:

* modern IT consultant
* premium technology ecosystem
* startup digital platform
* intelligent business system

---

# DESIGN STYLE

## Visual Direction

Gunakan:

* soft glassmorphism
* rounded modern card
* subtle gradient
* elegant spacing
* premium shadow
* thin border
* modern typography
* cinematic section background
* soft glow
* layered depth

Hindari:

* border tebal
* shadow kasar
* warna terlalu neon
* terlalu banyak icon
* layout sempit
* dashboard terlalu padat

---

# COLOR SYSTEM

## Primary Palette

```css
--cream-bg: #F8F1E4;
--soft-cream: #FFF9EF;
--gold: #C99A3A;
--deep-gold: #A67420;
--light-blue: #DCEFF7;
--sky-blue-soft: #BFDDEB;
--brown: #4B2E16;
--dark-brown: #2A1608;
--charcoal: #202124;
--white-soft: #FFFCF6;
```

---

# SECTION COLOR STRATEGY

| Section          | Theme              |
| ---------------- | ------------------ |
| Hero             | Cream + light blue |
| Marketplace      | Soft cream         |
| Process          | Dark cinematic     |
| Member dashboard | Charcoal + cream   |
| Footer           | Dark premium       |
| CTA              | Gold accent        |
| Consultation     | Soft blue          |
| IT News          | Clean light        |

---

# TYPOGRAPHY SYSTEM

# Heading

Gunakan:

* Playfair Display
* Cormorant Garamond
* DM Serif Display

Style:

* elegant
* premium
* cinematic

---

# Body Text

Gunakan:

* Inter
* Plus Jakarta Sans
* Manrope

Style:

* clean
* readable
* modern

---

# FONT SCALE

## Mobile

```css
h1 {
  font-size: clamp(2.2rem, 8vw, 4rem);
}

h2 {
  font-size: clamp(1.8rem, 6vw, 3rem);
}

body {
  font-size: 1rem;
  line-height: 1.7;
}
```

---

# LAYOUT PHILOSOPHY

## Mobile First

Desain harus dimulai dari:

* 360px
* 390px
* 430px

Baru berkembang ke:

* tablet
* desktop

---

# RULES

## Wajib:

* no overlap
* no horizontal scroll
* no fixed height
* spacing lega
* CTA mudah ditekan
* card turun jadi 1 kolom di mobile

---

# CONTAINER SYSTEM

```css
.container {
  width: min(100% - 40px, 1280px);
  margin-inline: auto;
}
```

---

# GRID SYSTEM

## Desktop

* 2–4 kolom

## Tablet

* 2 kolom

## Mobile

* 1 kolom

---

# CARD DESIGN SYSTEM

## Product Card

Card harus:

* premium
* ringan
* tidak penuh teks

Isi:

* image
* product title
* short spec
* price
* badge
* CTA

---

# CARD STYLE

```css
.product-card {
  border-radius: 28px;
  overflow: hidden;
  background: rgba(255,249,239,0.82);
  border: 1px solid rgba(201,154,58,0.22);
  box-shadow: 0 24px 60px rgba(75,46,22,0.08);
}
```

---

# BUTTON SYSTEM

## Primary Button

Style:

* gold gradient
* rounded pill
* soft shadow

CTA harus terlihat jelas.

---

# BUTTON SIZE

```css
.button {
  min-height: 48px;
  padding: 14px 22px;
}
```

---

# NAVBAR SYSTEM

## Navbar Style

Navbar harus:

* floating
* glass effect
* premium
* blur background

---

# MOBILE NAVIGATION

Mobile navbar wajib:

* sticky
* mudah dijangkau
* drawer clean
* tidak fullscreen chaos

---

# MARKETPLACE UI

# Product Card Layout

## Desktop

* image atas
* content bawah

## Mobile

* image compact
* CTA langsung terlihat

---

# PRODUCT DETAIL PAGE

## Layout

Desktop:

* gallery kiri
* detail kanan

Mobile:

* gallery atas
* detail bawah

---

# MEMBER DASHBOARD

## Dashboard Feel

Dashboard harus terasa:

* clean
* futuristic
* organized
* not overwhelming

---

# DASHBOARD COMPONENTS

* KPI card
* recent order
* consultation status
* wishlist
* news update
* quick action

---

# CONSULTATION UI

## Consultation Card

Harus terasa:

* modern ticket system
* ringan
* mudah dibaca

Gunakan:

* bubble response
* status badge
* timeline

---

# NEWS UI

## Article Card

Gunakan:

* featured image
* category badge
* title
* short excerpt

Jangan terlalu panjang.

---

# PROCESS SECTION STYLE

Gunakan background cinematic dark industrial fantasy yang sudah dibuat.

Process cards harus:

* terang
* readable
* kontras cukup
* premium glass card

---

# IMAGE RULES

## Images

Semua image:

* responsive
* max-width: 100%
* object-fit: cover/contain

---

# DECORATION RULES

Gunakan:

* thin circuit line
* soft glow
* abstract geometry
* subtle particles

Hindari:

* dekor terlalu ramai
* floating UI berlebihan
* cyberpunk overload

---

# ANIMATION SYSTEM

## Allowed

* fade in
* soft translate
* hover lift
* smooth transition
* subtle glow

## Forbidden

* shake
* bounce berlebihan
* blinking
* chaotic motion

---

# UX RULES

## Marketplace UX

User harus bisa:

* browse cepat
* checkout cepat
* menemukan produk mudah
* konsultasi tanpa bingung

---

# MOBILE UX PRIORITY

Critical:

* cart access
* CTA visibility
* checkout flow
* navigation
* consultation button

---

# ACCESSIBILITY

Wajib:

* contrast aman
* button cukup besar
* text readable
* spacing nyaman

---

# PERFORMANCE RULES

Target:

* lightweight
* fast rendering
* lazy image
* optimized asset

---

# FINAL EXPERIENCE TARGET

Feira Marketplace harus terasa seperti:

“Marketplace dan portal teknologi modern yang premium, artistik, dan nyaman digunakan, tetapi tetap fokus pada efisiensi bisnis dan kemudahan user.”

Bukan sekadar toko online biasa.
