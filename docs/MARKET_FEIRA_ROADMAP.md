# Feira Marketplace

## Master Development Roadmap

> Roadmap pembangunan mini marketplace modern yang terintegrasi di dalam ecosystem website feira.my.id.

---

# PROJECT STATUS

## Current Position

Phase 8 - Admin Ecosystem active. Dashboard, order, product, consultation, and owner-credential news management are complete.

## Main Objective

Membangun:

* mini marketplace
* member ecosystem
* consultation platform
* IT news portal
* digital payment system

Dengan pengalaman:

* premium
* mobile-first
* scalable
* modern
* artistic technology ecosystem

---

# DEVELOPMENT PHILOSOPHY

Project dibangun:

* bertahap
* modular
* scalable
* tidak chaos
* tidak terburu-buru

Prioritas utama:

1. pondasi stabil
2. mobile UX aman
3. architecture clean
4. reusable component
5. scalable ecosystem

---

# MASTER ROADMAP

# PHASE 1 — FOUNDATION & CORE SYSTEM

## Objective

Membangun pondasi architecture, UI system, dan ecosystem structure.

## Tasks

* [x] README ecosystem
* [x] Architecture planning
* [x] UI/UX guide
* [x] Database architecture
* [x] API structure
* [x] Component system
* [x] Security guide
* [x] Folder structure
* [x] QA checklist
* [x] Project vision
* [x] Business rules
* [x] Role matrix

---

## Frontend Foundation

* [x] Setup frontend framework
* [x] Setup routing system
* [x] Setup layout system
* [x] Setup theme variables
* [x] Setup typography
* [x] Setup responsive utilities
* [x] Setup animation utilities
* [x] Setup reusable component base

## Output / Result - Frontend Foundation (2026-06-14)

* Existing vanilla HTML/CSS/JS + Python static server stack dipertahankan dan diadaptasikan secara modular.
* Struktur `src/` tersedia untuk app, modules, components, layouts, pages, services, styles, utils, dan config.
* Module placeholder auth, marketplace, member, consultation, payment, news, dan dashboard sudah tersedia.
* Shared `MarketplaceLayout` dan shell page digunakan oleh seluruh route placeholder Phase 1.
* Route `/marketplace`, dynamic product slug, `/login`, `/register`, `/member`, `/member/orders`, `/member/consultation`, `/news`, dan `/checkout` sudah dapat diakses.
* Theme variables, typography, responsive container, button, card, badge, form, animation, dan mobile-first utilities sudah tersedia.
* Reusable component awal tersedia: ProductCard, ProductBadge, PriceTag, FloatingCartButton, MemberDashboardCard, ConsultationTicketCard, NewsCard, PrimaryButton, dan SectionHeader.
* Mock catalog/content diberi label Phase 1 dan belum terhubung ke database atau transaksi.
* Production build dan HTTP route smoke test berhasil.

---

## Backend Foundation

* [x] Setup backend architecture
* [x] Setup environment config
* [x] Setup database connection
* [x] Setup auth middleware
* [x] Setup API response standard
* [ ] Setup upload system
* [ ] Setup logging system

## Output / Result - Auth Backend Foundation (2026-06-14)

* Persistence user dan member session menggunakan SQLite private pada `DATA_ROOT`.
* Password disimpan sebagai hash `scrypt`; email dinormalisasi dan unique case-insensitive.
* Opaque session token hanya disimpan sebagai SHA-256 hash di database.
* Session memiliki idle timeout dan absolute timeout yang dapat dikonfigurasi melalui environment.
* Cookie member menggunakan `HttpOnly`, `SameSite=Lax`, path root, dan `Secure` saat HTTPS.
* API versioned tersedia pada `/api/v1/auth/register`, `/login`, `/logout`, dan `/me`.
* Response API memakai format konsisten `success`, `message`, `data`, dan `errors`.
* Route member dan checkout dilindungi server-side dengan redirect aman menuju login.
* Logout memakai CSRF token; register/login memiliki same-origin guard dan rate limit dasar.
* Session dan user tetap tersedia setelah server restart.

---

# PHASE 2 — AUTH & MEMBER SYSTEM

## Objective

Membangun ecosystem login dan member area.

## Tasks

* [x] Register page
* [x] Login page
* [x] Forgot password
* [x] Session management
* [x] Role management
* [x] Member dashboard
* [x] Profile settings
* [x] Avatar upload
* [x] Notification center

---

## UX Priority

* [x] Mobile login nyaman
* [x] Fast auth flow
* [x] Clean member dashboard
* [x] One-hand mobile interaction

## Output / Result - Auth & Member System (2026-06-14)

* Form register/login sudah terhubung ke API dengan validation feedback per field.
* Login berhasil mengarahkan user ke tujuan member yang diizinkan.
* Header menampilkan identitas member dan action logout saat session aktif.
* Dashboard member dipersonalisasi dan hanya dapat dibuka oleh session valid.
* Forgot/reset password memakai token acak yang disimpan sebagai SHA-256 hash, berlaku 30 menit, sekali pakai, dan mencabut seluruh session lama.
* Pengiriman link reset mendukung SMTP; debug URL hanya tersedia saat `PASSWORD_RESET_DEBUG=1`.
* Role `member`, `admin`, dan `super_admin` memiliki hierarchy enforcement; perubahan role hanya dapat dilakukan super admin melalui API terlindungi.
* Profile settings menyimpan identitas, kontak, perusahaan, alamat, dan bio.
* Avatar JPG/PNG/WebP maksimal 2MB divalidasi berdasarkan file signature dan disimpan di private data volume.
* Notification center persisten menyediakan unread count, mark-one, dan mark-all.
* Bottom navigation member menyediakan target sentuh minimum 44px untuk interaksi satu tangan di mobile.
* Unit test auth store mencakup password hash, session, profile, reset password, avatar, notification isolation, role authorization, dan migration idempotency.

---

# PHASE 3 — MARKETPLACE CORE

## Objective

Membangun sistem marketplace utama.

## Product System

* [x] Product category
* [x] Product listing
* [x] Product detail
* [x] Product gallery
* [x] Featured product
* [x] Related product
* [x] Product badge
* [x] Stock status

---

## Search & Filtering

* [x] Product search
* [x] Category filter
* [x] Sort system
* [x] Featured filter

---

## Marketplace UI

* [x] Product card system
* [x] Marketplace hero
* [x] Marketplace banner
* [x] Marketplace mobile navigation
* [x] Floating cart

## Output / Result - Marketplace Core (2026-06-14)

* Kategori, produk, dan gallery tersimpan pada SQLite melalui migration schema versi 4.
* Seed katalog awal idempotent menyediakan lima produk pada empat kategori tanpa menduplikasi data saat restart.
* API publik versioned tersedia untuk kategori, listing, detail slug, featured, category listing, dan search.
* Listing mendukung pencarian, filter kategori, featured-only, serta sort featured, terbaru, nama, dan harga.
* Filter disimpan pada query URL sehingga hasil dapat dibagikan dan kompatibel dengan browser navigation.
* Detail produk menampilkan gallery, badge, kategori, harga, status stok, dan related products.
* Product card reusable menggunakan data API dan membedakan in-stock, low-stock, serta out-of-stock.
* Hero marketplace, featured campaign banner, mobile bottom navigation, dan floating cart sudah aktif.
* Cart masih menampilkan jumlah nol dan menjadi titik integrasi Phase 4.
* Unit test katalog mencakup seed idempotent, filter, sort, gallery, related product, stock, dan public visibility.

---

# PHASE 4 — CART & CHECKOUT

## Objective

Membangun shopping flow modern.

## Cart System

* [x] Add to cart
* [x] Remove cart item
* [x] Qty update
* [x] Cart persistence

---

## Checkout System

* [x] Checkout page
* [x] Shipping form
* [x] Address management
* [x] Invoice generation
* [x] Order summary

---

## Mobile UX

* [x] Sticky checkout CTA
* [x] Mobile-safe cart
* [x] Fast checkout flow

## Output / Result - Cart & Checkout (2026-06-14)

* Schema versi 5 menyediakan `carts`, `cart_items`, `member_addresses`, `orders`, dan `order_items`.
* Cart hanya dapat diakses member dan persisten di SQLite berdasarkan user aktif.
* Add-to-cart, quantity update, dan remove item memakai same-origin, session, CSRF, serta validasi stok server-side.
* Floating cart menampilkan total quantity aktual dari server pada seluruh halaman.
* Checkout menampilkan cart editor, alamat tersimpan atau alamat baru, metode pengiriman, subtotal, shipping cost, dan grand total.
* Alamat dapat disimpan sebagai default dan digunakan kembali pada checkout berikutnya.
* Invoice unik dibuat bersama snapshot item order, alamat pengiriman, harga, dan status awal `unpaid` / `pending`.
* Checkout menggunakan transaksi `BEGIN IMMEDIATE`, validasi ulang stok/harga, conditional stock decrement, pembuatan order, dan konversi cart secara atomik.
* Jika stok berubah saat checkout, seluruh transaksi di-rollback sehingga tidak ada order parsial atau pengurangan stok ganda.
* Order history member menampilkan invoice, total, payment status, dan order status.
* Mobile cart memakai target sentuh minimum 44px dan order summary sticky pada desktop.
* Integration test mencakup cart persistence, add/update/remove, alamat, invoice, stock decrement, serta rollback overselling dua member.

---

# PHASE 5 — PAYMENT GATEWAY

## Objective

Integrasi transaksi digital modern.

## Tasks

* [x] Payment architecture
* [x] Midtrans/Xendit integration
* [x] QRIS support
* [x] Bank transfer
* [x] Payment callback validation
* [x] Payment status automation
* [x] Payment notification

---

## Security

* [x] Signature validation
* [x] Callback verification
* [x] Duplicate callback protection

## Output / Result - Payment Gateway (2026-06-14)

* Midtrans Core API dipilih untuk mempertahankan checkout UI custom Feira dengan dukungan QRIS dan Virtual Account.
* Schema versi 6 menyediakan payment attempt dan immutable callback event ledger.
* QRIS serta bank transfer BCA, BNI, BRI, dan Permata dapat dibuat dari order member.
* Mode sandbox/production dikendalikan environment; mode mock lokal aktif saat server key belum tersedia.
* Credential Midtrans hanya digunakan server-side melalui Basic Authentication dan tidak pernah dikirim ke frontend.
* Callback Midtrans tersedia pada `POST /api/v1/payment/callback/midtrans`.
* Signature diverifikasi menggunakan SHA-512 `order_id + status_code + gross_amount + server_key`.
* Callback juga memverifikasi invoice provider, nominal order, status code `200`, fraud status `accept`, dan transaction status.
* Event key transaction/status mencegah callback duplikat memproses perubahan yang sama lebih dari sekali.
* Status payment/order otomatis dipetakan untuk pending, paid, failed, expired, dan cancelled.
* Member menerima notifikasi persisten setiap perubahan status payment.
* Order history menampilkan pilihan metode, QR instruction, Virtual Account, dan status pembayaran.
* Integration test mencakup QRIS, Virtual Account, signature formula, amount mismatch, status automation, notification, dan duplicate callback.

---

# PHASE 6 — CONSULTATION SYSTEM

## Objective

Membangun layanan konsultasi IT.

## Consultation Features

* [x] Consultation ticket
* [x] Consultation dashboard
* [x] Ticket status
* [x] Reply system
* [x] File attachment
* [x] Consultation history

---

## Admin Features

* [x] Consultation queue
* [x] Ticket monitoring
* [x] Ticket status update

## Output / Result - Consultation System (2026-06-15)

* Schema versi 7 menyediakan consultation ticket, reply thread, dan attachment metadata/file storage.
* Member dapat membuat ticket konsultasi dari `/member/consultation`, melihat history, status, prioritas, kategori, reply, dan attachment.
* Reply member mengubah status menjadi `in_review`; reply admin mengubah status menjadi `waiting_member`.
* Attachment JPG, PNG, dan PDF divalidasi dari file signature, dibatasi 5MB, dan disimpan pada private data volume.
* Attachment hanya dapat diunduh oleh pemilik ticket atau admin melalui endpoint terautentikasi.
* Admin API tersedia untuk queue konsultasi, reply, dan update status ticket.
* Status ticket mendukung `open`, `in_review`, `waiting_member`, `resolved`, dan `closed`.
* Notifikasi member otomatis dibuat saat ticket dibuat, dibalas, atau status berubah.
* Unit test mencakup create ticket, reply, admin queue/status, permission, dan validation.

---

# PHASE 7 — FEIRA IT NEWS

## Objective

Membangun koran teknologi modern.

## Features

* [x] Article system
* [x] Featured article
* [x] Trending article
* [x] Article category
* [x] Related article
* [x] Search article

## Output / Result - Feira IT News (2026-06-15)

* Schema versi 8 menyediakan kategori dan artikel news terpublikasi.
* Seed artikel teknologi awal idempotent tersedia untuk infrastructure, security, dan digital workflow.
* API publik tersedia untuk listing artikel, kategori, featured, trending, search, dan detail slug.
* Halaman `/news` memakai data API nyata dengan filter kategori, search, featured, dan trending.
* Route `/news/{slug}` menampilkan detail artikel dan related article.
* Card news tidak lagi memakai mock content Phase 1.
* Unit test mencakup seed idempotent, kategori count, search, featured, trending, related article, dan visibility artikel archived.

---

## Future

* [ ] Newsletter
* [ ] AI article summary
* [ ] Video content

---

# PHASE 8 — ADMIN ECOSYSTEM

## Objective

Membangun admin dashboard ecosystem.

## Admin Dashboard

* [x] KPI dashboard
* [x] Order monitoring
* [x] Product management
* [x] Consultation management
* [x] News management
* [ ] Member management

## Output / Result - Admin Foundation (2026-06-15)

* Route `/admin` dan `/admin/consultation` memakai shared marketplace shell dan dilindungi server-side untuk role `admin` serta `super_admin`.
* Guest diarahkan ke login dengan safe next path; member biasa menerima HTTP 403.
* KPI dashboard dihitung dari SQLite untuk member aktif, total order, omzet paid, payment pending, ticket aktif, dan ticket urgent.
* Consultation queue admin menampilkan identitas member, prioritas, status, thread lengkap, dan attachment private.
* Admin dapat memfilter queue berdasarkan status, mengirim reply, serta memperbarui status ticket dengan session, same-origin, dan CSRF validation.
* Route `/admin/orders` menyediakan filter payment status dan order status dengan detail snapshot invoice, customer, shipping, item, dan total.
* Fulfillment memakai transisi tervalidasi `paid` ke `processing`, `shipped`, lalu `completed`; order unpaid dan lompatan status ditolak.
* Setiap perubahan fulfillment membuat notifikasi persisten untuk member.
* Route `/admin/products` menyediakan listing seluruh produk, create, edit, featured flag, stock/status management, preview, dan archive.
* Upload gambar produk memakai session admin, same-origin, CSRF, format image yang diizinkan, serta private server credential boundary.
* Operasi katalog sekarang tersedia melalui API `/api/v1/admin/products*`; owner builder lama hanya dipertahankan sebagai compatibility path sementara.
* News Management ditempatkan sebagai section `09 / Feira IT News` pada Owner Tool Builder sesuai keputusan credential boundary owner.
* Editor news menyediakan category create/edit, article create/edit, draft/published/archived, featured, trending score, reading time, cover upload, preview, dan archive.
* API `/api/owner/news*` hanya tersedia untuk sesi owner dan mutasi dilindungi same-origin.
* Cover JPG, PNG, WebP, atau GIF dibatasi 10MB dan divalidasi berdasarkan MIME serta file signature.
* Navigasi desktop dan mobile menampilkan entry admin hanya untuk role yang diizinkan.
* Unit test mencakup KPI, permission, consultation, order fulfillment, product CRUD, serta category/article news lifecycle.

---

# PHASE 9 — VISUAL POLISH & CINEMATIC EXPERIENCE

## Objective

Menjadikan platform terasa premium dan berbeda.

## Tasks

* [ ] Cinematic hero
* [ ] Process background implementation
* [ ] Floating navbar
* [ ] Premium footer
* [ ] Soft animation
* [ ] Glassmorphism polish
* [ ] Decorative system

---

## UX Enhancement

* [ ] Hover interaction
* [ ] Skeleton loading
* [ ] Smooth transition
* [ ] Premium scrolling experience

---

# PHASE 10 — SECURITY & HARDENING

## Objective

Menjadikan platform production ready.

## Tasks

* [ ] Auth hardening
* [ ] Upload validation
* [ ] Rate limiting
* [ ] Session security
* [ ] Admin protection
* [ ] API protection
* [ ] Error handling

---

# PHASE 11 — QA & OPTIMIZATION

## Objective

Audit keseluruhan ecosystem.

## QA Checklist

* [ ] Responsive audit
* [ ] Mobile audit
* [ ] Performance audit
* [ ] Security audit
* [ ] Component consistency
* [ ] Lighthouse testing
* [ ] Asset optimization

---

# PHASE 12 — DEPLOYMENT & PRODUCTION

## Objective

Launch production ecosystem.

## Tasks

* [ ] Production build
* [ ] Environment setup
* [ ] Database migration
* [ ] Backup system
* [ ] SSL setup
* [ ] CDN optimization
* [ ] Monitoring setup

---

# FUTURE EXPANSION

## Future Ecosystem

* [ ] Mobile apps
* [ ] AI consultation assistant
* [ ] Subscription member
* [ ] Maintenance contract
* [ ] Vendor marketplace
* [ ] Cloud dashboard
* [ ] Affiliate system
* [ ] Service booking

---

# FINAL TARGET

Feira Marketplace harus menjadi:

“Premium IT digital ecosystem yang menggabungkan marketplace, consultation, technology news, dan member platform dalam pengalaman modern, artistik, scalable, dan mobile-first.”

Bukan sekadar toko online IT biasa.
