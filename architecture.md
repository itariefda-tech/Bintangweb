# Architecture Philosophy

Arsitektur website harus:

* Modular
* Clean
* Reusable
* Mobile-first
* Easy maintenance
* Scalable
* Fast rendering

---

# High Level Architecture

```text
User
 │
 ▼
Frontend UI Layer
 │
 ├── Navbar
 ├── Hero
 ├── Service Section
 ├── CTA Section
 ├── Contact Section
 └── Footer
 │
 ▼
Component Layer
 │
 ├── Card Component
 ├── Button Component
 ├── Grid System
 ├── Mobile Menu
 ├── Animation Layer
 └── Responsive Utility
 │
 ▼
Styling Layer
 │
 ├── Tailwind Utility
 ├── Custom CSS
 ├── Theme Variables
 └── Responsive Rules
 │
 ▼
Asset Layer
 │
 ├── Images
 ├── Icons
 ├── SVG Decoration
 └── Branding Assets
```

---

# Frontend Architecture

## UI Layer

Semua section dibuat modular:

* reusable
* independent
* tidak saling menempel

---

# Layout System

## Container Rules

```css
.container {
  width: min(100% - 40px, 1180px);
  margin-inline: auto;
}
```

---

# Responsive Architecture

## Mobile First

```css
base style = mobile
tablet = enhancement
desktop = expansion
```

---

# Z-Index Hierarchy

```css
background decor = 0
content = 2
navbar = 50
mobile menu = 80
floating button = 90
```

Jangan gunakan:

```css
z-index: 99999;
```

Karena itu tanda architecture mulai kacau.

---

# Performance Architecture

## Target:

* Fast load
* Lightweight animation
* Lazy load image
* Minimized JS
* Optimized image

---

# Component Structure

## Components:

* HeroCard
* ServiceCard
* CTAButton
* FloatingContact
* SectionHeader
* TrustBadge
* MobileDrawer
* FooterGrid

---

# Animation Philosophy

Gunakan:

* soft fade
* subtle motion
* smooth hover
* elegant transition

Hindari:

* animasi berlebihan
* blinking
* cyberpunk chaos
* motion berlebihan

---

# Mobile Experience Priority

Website harus:

* nyaman dibuka satu tangan
* CTA mudah dijangkau
* text mudah dibaca
* spacing lega
* tidak sumpek

---

# Desktop Experience

Desktop tetap harus:

* premium
* cinematic
* modern
* luas
* elegant

Bukan layout kosong besar tanpa arah.

---

# Final Architecture Goal

Website harus terasa seperti:

* modern IT consultant
* premium startup
* trusted technology partner
* scalable digital business
