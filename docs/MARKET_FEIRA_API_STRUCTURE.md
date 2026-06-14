# Feira Marketplace

## API Structure Architecture

> API Feira Marketplace dirancang modular, scalable, mobile-app ready, dan future-ready untuk ecosystem digital Bintang Computer Feira.

---

# API PHILOSOPHY

API harus:

* clean
* modular
* scalable
* RESTful
* secure
* easy maintenance
* frontend independent
* future mobile-app ready

---

# API BASE STRUCTURE

```text id="s56g0e"
/api/v1/
```

Versi API wajib dipisah:

* `/api/v1`
* `/api/v2`
* dst

Agar future update tidak merusak sistem lama.

---

# MAIN API MODULES

# 1. AUTH MODULE

## Endpoint

```http id="v6hn2g"
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
POST   /api/v1/auth/forgot-password
POST   /api/v1/auth/reset-password
GET    /api/v1/auth/me
```

---

# AUTH RESPONSE FORMAT

```json id="vjqj7k"
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {},
    "token": ""
  }
}
```

---

# 2. PRODUCT MODULE

## Product Endpoint

```http id="5m5k3u"
GET    /api/v1/products
GET    /api/v1/products/{slug}
GET    /api/v1/products/featured
GET    /api/v1/products/category/{slug}
GET    /api/v1/products/search
```

---

# Product Admin Endpoint

```http id="95d4xd"
POST   /api/v1/admin/products
PUT    /api/v1/admin/products/{id}
DELETE /api/v1/admin/products/{id}
```

---

# 3. CATEGORY MODULE

```http id="mx9zlo"
GET    /api/v1/categories
GET    /api/v1/categories/{slug}
```

---

# 4. CART MODULE

```http id="v4lgk7"
GET    /api/v1/cart
POST   /api/v1/cart/add
PUT    /api/v1/cart/items/{id}
DELETE /api/v1/cart/items/{id}
```

---

# 5. CHECKOUT MODULE

```http id="sqqw8u"
POST   /api/v1/checkout
GET    /api/v1/member/orders

Implemented member endpoints:

```http
GET    /api/v1/member/addresses
POST   /api/v1/member/addresses
```
```

---

# 6. PAYMENT MODULE

```http id="gu1b9n"
POST   /api/v1/payment/create
POST   /api/v1/payment/callback
GET    /api/v1/payment/status/{invoice}
```

Implemented Phase 5 endpoints:

```http
POST   /api/v1/payment/create
GET    /api/v1/payments?orderId={id}
POST   /api/v1/payment/callback/midtrans
```

---

# PAYMENT FLOW

```text id="77m20x"
User Checkout
   │
   ▼
Create Invoice
   │
   ▼
Payment Gateway
   │
   ▼
Payment Callback
   │
   ▼
Order Status Updated
```

---

# 7. CONSULTATION MODULE

```http id="k0ozsq"
GET    /api/v1/consultations
POST   /api/v1/consultations
GET    /api/v1/consultations/{ticket}
POST   /api/v1/consultations/{ticket}/reply
```

---

# 8. NEWS MODULE

```http id="m0n7lm"
GET    /api/v1/news
GET    /api/v1/news/{slug}
GET    /api/v1/news/featured
```

---

# 9. MEMBER MODULE

```http id="1j1d09"
GET    /api/v1/member/profile
PUT    /api/v1/member/profile
GET    /api/v1/member/orders
GET    /api/v1/member/wishlist
```

---

# 10. NOTIFICATION MODULE

```http id="5cd1rp"
GET    /api/v1/notifications
POST   /api/v1/notifications/read
```

---

# RESPONSE STANDARD

## Success Response

```json id="68c49y"
{
  "success": true,
  "message": "Success",
  "data": {}
}
```

---

## Error Response

```json id="r87u6m"
{
  "success": false,
  "message": "Validation error",
  "errors": {}
}
```

---

# SECURITY RULES

## Required

* JWT/session validation
* CSRF protection
* upload validation
* rate limit
* role middleware
* payment callback validation

---

# FILE UPLOAD RULES

## Allowed

* jpg
* png
* webp
* pdf

## Max Upload

* consultation attachment
* product image
* avatar image

---

# API STRUCTURE RULES

## Rules

* gunakan plural naming
* gunakan slug untuk public URL
* jangan expose internal ID sembarangan
* consistent response format
* versioning wajib

---

# FUTURE API READY

Future:

* mobile apps
* AI assistant
* real-time notification
* websocket consultation
* vendor system
* cloud sync

---

# PERFORMANCE TARGET

API harus:

* cepat
* scalable
* cache-friendly
* future microservice ready
* mobile optimized

---

# FINAL API GOAL

Membangun API ecosystem yang:

* modular
* aman
* scalable
* modern
* siap berkembang menjadi platform digital besar
