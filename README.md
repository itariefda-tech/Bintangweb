# BINTANG COMPUTER FEIRA

## Modern IT Consultant & Technology Solution

![Bintang Computer Feira](./assets/banner-cover.jpg)

> Technology Simplified, Business Amplified.

---

# Overview

Bintang Computer Feira adalah website company profile modern untuk layanan konsultasi IT, pengadaan perangkat teknologi, infrastruktur jaringan, CCTV, PABX, pengembangan aplikasi custom, dan website development.

Project ini dirancang dengan pendekatan:

* Mobile-first
* Premium modern UI
* Clean technology branding
* Responsive layout system
* Scalable architecture
* Gen-Z modern designer aesthetic

---

# Core Services

## 1. IT Procurement

Penyediaan komputer, laptop, printer, scanner, monitor, UPS, dan perangkat IT lainnya.

## 2. Network Solution

Setup jaringan kantor, server, NAS, firewall, VPN, backup system, dan private cloud.

## 3. CCTV System

Pemasangan CCTV, monitoring realtime, DVR/NVR, remote smartphone monitoring.

## 4. PABX System

Setup telepon internal kantor, extension, IP PBX, voicemail, dan komunikasi internal.

## 5. Custom Application & Refactor

Pembuatan aplikasi custom, dashboard bisnis, reporting system, HRIS, attendance system.

## 6. Website Development & Refactor

Website company profile, landing page, redesign website lama, responsive modern web.

---

# Design Philosophy

Website harus terasa:

* Modern
* Premium
* Clean
* Elegant
* Semi futuristic
* Mobile friendly
* Technology consultant vibes

Bukan template corporate lawas.

---

# Technology Stack

## Frontend

* HTML5
* Tailwind CSS
* Vanilla JS / Alpine JS
* GSAP Animation (optional)

## Design System

* Mobile-first responsive
* Glassmorphism soft style
* Gold + cream + light blue palette
* Large rounded card
* Soft shadow layering

---

# Responsive Rules

## Priority:

1. Mobile
2. Tablet
3. Desktop

## Must Avoid:

* Horizontal scroll
* Overlapping layer
* Fixed card height
* Hero overflow
* Broken grid
* Unclickable button

---

# Folder Structure

```bash
project/
│
├── index.html
├── assets/
│   ├── images/
│   ├── icons/
│   └── branding/
│
├── css/
│   ├── style.css
│   ├── components.css
│   └── responsive.css
│
├── js/
│   ├── app.js
│   └── animation.js
│
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── roadmap.md
│   ├── uiuxguide.md
│   └── erd.md
```

---

# Brand Palette

```css
--cream-bg: #F8F1E4;
--soft-cream: #FFF9EF;
--gold: #C99A3A;
--deep-gold: #A67420;
--light-blue: #DCEFF7;
--brown: #4B2E16;
--charcoal: #202124;
```

---

# Target Experience

User harus merasa:

* “wah ini modern”
* “ini bukan jasa IT biasa”
* “visualnya premium”
* “terlihat profesional dan dipercaya”
* “nyaman dibuka di HP”

---

# Final Objective

Membangun website company profile yang:

* Modern
* Responsive
* High trust
* Visually memorable
* Business oriented
* Ready for scaling

---

# Private Owner Builder

Owner builder tidak memiliki link publik. Dari halaman utama:

1. Tahan logo pada header selama 5 detik.
2. Masukkan password owner dari `.env`.
3. Builder dibuka melalui route `/owner-builder`.

Fitur:

* Mock theme preview
* Upload video untuk section Work
* Editor testimoni Work
* Upload background header, hero, about, solutions, process, contact, dan footer
* Toggle autoplay audio Process

Credential wajib disimpan di `.env` dan tidak boleh di-commit:

```env
OWNER_PASSWORD=change-this-owner-password
```

Setting dan upload disimpan di folder `data/`. Pada Docker, gunakan persistent volume ke `/app/data` dan jalankan container dengan `--env-file`.
