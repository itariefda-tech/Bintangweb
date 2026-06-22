# Feira Marketplace

## Component System Guide

> Component system Feira Marketplace dirancang agar UI konsisten, reusable, premium, mobile-first, dan scalable.

---

# COMPONENT PHILOSOPHY

Semua component harus:

* reusable
* responsive
* modular
* clean
* lightweight
* elegant
* easy maintenance

---

# DESIGN PRINCIPLE

UI harus terasa:

* premium
* modern
* soft futuristic
* startup ecosystem
* elegant technology platform

---

# COMPONENT CATEGORY

# 1. LAYOUT COMPONENTS

## Main Components

* Container
* Section Wrapper
* Grid System
* Stack Layout
* Responsive Flex

---

# 2. NAVIGATION COMPONENTS

## Components

* Floating Navbar
* Mobile Drawer
* Search Bar
* Breadcrumb
* Bottom Mobile Nav (future)

---

# NAVBAR RULES

Navbar harus:

* floating
* blur background
* rounded
* premium shadow
* mobile-safe

---

# 3. BUTTON COMPONENTS

## Button Variants

### Primary Button

Gold gradient CTA.

### Secondary Button

Soft cream transparent.

### Ghost Button

Minimal outline button.

### Danger Button

Delete/cancel action.

---

# BUTTON RULES

```css id="9km4ua"
.button {
  min-height: 48px;
  border-radius: 999px;
}
```

Mobile:

* mudah ditekan
* tidak terlalu kecil

---

# 4. CARD COMPONENTS

## Main Card Types

* Product Card
* News Card
* Consultation Card
* Dashboard Card
* Feature Card
* Process Card

---

# PRODUCT CARD

## Structure

```text id="mf5kmh"
Image
Badge
Title
Short Spec
Price
CTA
```

---

# CARD STYLE

```css id="ncbn02"
.card {
  border-radius: 28px;
  overflow: hidden;
  background: rgba(255,249,239,0.82);
  border: 1px solid rgba(201,154,58,0.22);
  box-shadow: 0 24px 60px rgba(75,46,22,0.08);
}
```

---

# 5. FORM COMPONENTS

## Components

* Input
* Select
* Textarea
* Upload Area
* Search Input
* Password Field

---

# FORM RULES

Form harus:

* clean
* readable
* mobile friendly
* spacing lega

---

# 6. MARKETPLACE COMPONENTS

## Components

* Product Gallery
* Product Badge
* Price Tag
* Stock Indicator
* Wishlist Button
* Cart Button
* Quantity Counter

---

# 7. DASHBOARD COMPONENTS

## Components

* KPI Card
* Activity Timeline
* Recent Order
* Notification List
* Consultation Status
* Quick Action

---

# 8. CONSULTATION COMPONENTS

## Components

* Ticket Card
* Chat Bubble
* Status Badge
* Attachment Preview
* Consultation Timeline

---

# CONSULTATION STYLE

Harus terasa:

* modern support system
* clean
* organized
* readable

---

# 9. NEWS COMPONENTS

## Components

* Article Card
* Featured Article
* Category Badge
* Reading Time
* Related Article

---

# 10. FEEDBACK COMPONENTS

## Components

* Toast Notification
* Alert Banner
* Modal
* Confirmation Dialog
* Loading Skeleton

---

# MODAL RULES

Modal harus:

* centered
* mobile-safe
* blur overlay
* easy close
* not oversized

---

# 11. MOBILE COMPONENTS

## Critical Mobile Components

* Mobile Navbar
* Floating CTA
* Sticky Cart
* Swipe Product Gallery
* Mobile Drawer

---

# MOBILE UX RULES

Wajib:

* no overlap
* no horizontal scroll
* one hand friendly
* thumb reachable CTA
* spacing nyaman

---

# 12. DECORATION COMPONENTS

## Decorative Elements

* Soft Glow
* Circuit Line
* Gradient Orb
* Particle Layer
* Abstract Geometry

---

# DECORATION RULES

Decor hanya kosmetik:

* pointer-events: none
* opacity rendah
* tidak menutup content

---

# COMPONENT NAMING RULE

## Example

```text id="7is54h"
market-card
market-card__image
market-card__content
market-card__title
market-card__price
```

Gunakan naming konsisten.

---

# RESPONSIVE RULES

## Desktop

* cinematic
* spacious
* elegant

## Mobile

* compact
* clean
* easy interaction

---

# ANIMATION RULES

Allowed:

* fade
* soft translate
* hover lift
* subtle glow

Forbidden:

* shake
* bounce berlebihan
* blinking chaos

---

# PERFORMANCE RULES

Component harus:

* reusable
* lightweight
* lazy render friendly
* animation optimized

---

# FINAL COMPONENT GOAL

Membangun component ecosystem yang:

* konsisten
* premium
* mudah dikembangkan
* modern
* scalable
* nyaman digunakan di mobile maupun desktop
