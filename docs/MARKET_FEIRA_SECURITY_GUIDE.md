# Feira Marketplace

## Security Guide & Protection Rules

> Security bukan fitur tambahan. Security adalah pondasi utama ecosystem Feira Marketplace.

---

# SECURITY PHILOSOPHY

Sistem harus:

* aman
* scalable
* tidak mudah disalahgunakan
* tahan spam dasar
* aman untuk transaksi
* aman untuk member

---

# CORE SECURITY LAYERS

# 1. AUTHENTICATION SECURITY

## Password Rules

Password wajib:

* hash bcrypt/argon2
* minimum length
* tidak disimpan plain text

---

## Login Protection

Gunakan:

* rate limit
* brute force protection
* session expiration
* suspicious login detection

---

# SESSION RULES

## Session Expiration

* auto logout inactivity
* refresh token future-ready
* secure cookie

---

# 2. ROLE SECURITY

## Role Hierarchy

```text id="mf5h9z"
Guest
Member
Admin
Super Admin
```

---

## Rules

Member:

* hanya akses data sendiri

Admin:

* hanya akses module tertentu

Super Admin:

* full system access

---

# 3. PAYMENT SECURITY

## Payment Callback

Wajib:

* verify signature
* validate invoice
* validate nominal
* validate payment status

Current implementation:

* Midtrans SHA-512 signature verification
* invoice/provider order lookup
* exact gross amount comparison
* status code, fraud status, dan transaction status validation
* idempotent event key untuk duplicate webhook

---

# PAYMENT RULES

Jangan:

* percaya frontend
* percaya nominal dari client
* percaya callback tanpa validation

---

# 4. FILE UPLOAD SECURITY

## Allowed File

```text id="p84vcs"
jpg
jpeg
png
webp
pdf
```

---

## Upload Rules

* validate mime type
* validate extension
* validate size
* randomize filename
* block executable file

---

# MAX FILE SIZE

| Type                    | Max  |
| ----------------------- | ---- |
| Avatar                  | 2MB  |
| Product Image           | 5MB  |
| Consultation Attachment | 10MB |

---

# 5. API SECURITY

## Required

* CSRF protection
* auth middleware
* role middleware
* request validation
* rate limit

---

# API RATE LIMIT

Example:

* login
* register
* consultation submit
* payment callback

---

# 6. DATABASE SECURITY

## Rules

* prepared statement
* ORM safe query
* avoid raw query
* sanitize input

---

# 7. CONSULTATION SECURITY

## Consultation Protection

* member hanya melihat ticket sendiri
* upload validation
* anti spam submit
* admin logging

---

# 8. ADMIN SECURITY

## Admin Protection

Admin area wajib:

* auth protected
* role protected
* session monitored

---

# ADMIN ACTION LOG

Log:

* delete product
* update order
* payment verification
* article publish

---

# 9. FRONTEND SECURITY

## Frontend Rules

Jangan:

* expose secret key
* expose payment secret
* expose admin endpoint

---

# 10. FUTURE SECURITY

Future:

* 2FA
* device tracking
* suspicious activity monitoring
* audit log
* anti fraud

---

# MOBILE SECURITY

Mobile wajib:

* secure auth
* safe session
* protected upload
* safe checkout flow

---

# FINAL SECURITY GOAL

Membangun platform yang:

* aman digunakan
* aman untuk transaksi
* aman untuk member
* scalable untuk future ecosystem
