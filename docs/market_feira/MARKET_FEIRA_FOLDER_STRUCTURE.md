# Feira Marketplace

## Folder Structure Guide

> Struktur folder harus clean, scalable, modular, dan future-ready.

---

# STRUCTURE PHILOSOPHY

Project structure harus:

* mudah dipahami
* modular
* scalable
* tidak chaos
* mudah maintenance
* future mobile-app ready

---

# ROOT STRUCTURE

```bash
feira-marketplace/
│
├── docs/
├── public/
├── src/
├── assets/
├── database/
├── tests/
├── scripts/
├── .env
├── package.json
└── README.md
```

---

# DOCS STRUCTURE

```bash
docs/
│
└── market_feira/
    ├── MARKET_FEIRA_README.md
    ├── MARKET_FEIRA_ARCHITECTURE.md
    ├── MARKET_FEIRA_UIUX_GUIDE.md
    ├── MARKET_FEIRA_DATABASE_ARCHITECTURE.md
    ├── MARKET_FEIRA_API_STRUCTURE.md
    ├── MARKET_FEIRA_COMPONENT_SYSTEM.md
    ├── MARKET_FEIRA_SECURITY_GUIDE.md
    ├── MARKET_FEIRA_MATRIX.md
    ├── MARKET_FEIRA_PROJECT_VISION.md
    └── MARKET_FEIRA_ROADMAP.md
```

---

# SRC STRUCTURE

```bash
src/
│
├── app/
├── modules/
├── components/
├── layouts/
├── pages/
├── services/
├── stores/
├── hooks/
├── utils/
├── styles/
└── config/
```

---

# MODULE STRUCTURE

Setiap module wajib terpisah.

Example:

```bash
modules/
│
├── auth/
├── marketplace/
├── consultation/
├── payment/
├── news/
├── member/
└── dashboard/
```

---

# MODULE INTERNAL STRUCTURE

Example:

```bash
marketplace/
│
├── components/
├── pages/
├── services/
├── store/
├── hooks/
├── types/
└── utils/
```

---

# COMPONENT STRUCTURE

```bash
components/
│
├── ui/
├── cards/
├── forms/
├── navigation/
├── modal/
├── feedback/
└── sections/
```

---

# UI COMPONENTS

```bash
ui/
│
├── button/
├── badge/
├── input/
├── textarea/
├── select/
├── avatar/
└── skeleton/
```

---

# PAGE STRUCTURE

```bash
pages/
│
├── home/
├── marketplace/
├── product/
├── consultation/
├── member/
├── auth/
└── dashboard/
```

---

# ASSET STRUCTURE

```bash
assets/
│
├── images/
├── icons/
├── illustrations/
├── logos/
├── backgrounds/
└── decorations/
```

---

# IMAGE STRUCTURE

```bash
images/
│
├── hero/
├── products/
├── banners/
├── consultation/
└── backgrounds/
```

---

# BACKGROUND STRUCTURE

```bash
backgrounds/
│
├── hero/
├── process/
├── navbar/
├── footer/
└── dashboard/
```

---

# STYLES STRUCTURE

```bash
styles/
│
├── globals.css
├── variables.css
├── typography.css
├── animations.css
├── utilities.css
└── responsive.css
```

---

# DATABASE STRUCTURE

```bash
database/
│
├── migrations/
├── seeders/
├── schema/
└── backups/
```

---

# TEST STRUCTURE

```bash
tests/
│
├── unit/
├── integration/
├── ui/
└── mobile/
```

---

# CONFIG STRUCTURE

```bash
config/
│
├── api.ts
├── auth.ts
├── payment.ts
├── constants.ts
└── environment.ts
```

---

# FUTURE STRUCTURE

Future-ready:

* mobile-app
* websocket
* AI service
* multi vendor
* cloud integration

---

# FOLDER RULES

## Rules

* jangan campur business logic
* jangan taruh semua component di satu folder
* hindari file monster ribuan baris
* pisahkan module dengan jelas
* reusable component wajib diprioritaskan

---

# FILE NAMING RULE

## Components

```text id="kcc74s"
ProductCard.tsx
ConsultationCard.tsx
FloatingNavbar.tsx
```

---

## Styles

```text id="8tgho0"
product-card.css
dashboard-layout.css
```

---

# FINAL STRUCTURE GOAL

Membangun struktur project yang:

* profesional
* scalable
* modular
* mudah maintenance
* siap berkembang menjadi ecosystem digital besar
