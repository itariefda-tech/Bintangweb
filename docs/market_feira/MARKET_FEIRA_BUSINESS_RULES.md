# Feira Marketplace

## Business Rules

---

# CORE BUSINESS RULES

# 1. USER RULES

## Guest

Guest hanya dapat:

* melihat produk
* membaca artikel
* melihat layanan

Guest tidak dapat:

* checkout
* konsultasi
* wishlist
* order tracking

---

## Member

Member dapat:

* checkout produk
* konsultasi IT
* menyimpan wishlist
* melihat histori order
* menerima notifikasi

---

# 2. PRODUCT RULES

## Product Status

Status produk:

* active
* inactive
* out_of_stock
* archived

Produk inactive tidak tampil publik.

---

# 3. ORDER RULES

## Checkout

Checkout hanya dapat dilakukan:

* oleh member login
* cart tidak kosong
* stock tersedia

---

## Order Status

Status:

* pending
* waiting_payment
* paid
* processing
* shipped
* completed
* cancelled

---

# 4. PAYMENT RULES

## Payment Validation

Order dianggap valid jika:

* payment verified
* nominal sesuai
* callback/payment confirmation sukses

---

# 5. CONSULTATION RULES

## Consultation Access

Hanya member login yang dapat membuat consultation ticket.

---

## Consultation Priority

Priority:

* normal
* urgent
* premium future

---

# 6. NEWS RULES

## Article Visibility

Article dapat:

* public
* member only (future)

---

# 7. SECURITY RULES

## Authentication

* password wajib hash
* session timeout
* rate limit login
* upload validation

---

# 8. MOBILE UX RULES

Semua flow wajib:

* mobile-first
* mudah dipahami
* CTA terlihat jelas
* tidak overlap
* tidak horizontal scroll

---

# 9. ADMIN RULES

Admin dapat:

* manage product
* manage order
* manage consultation
* manage news

Super Admin:

* full configuration access

---

# 10. FUTURE BUSINESS RULES

Future:

* subscription member
* maintenance package
* service booking
* AI consultation
* loyalty point
* affiliate system
