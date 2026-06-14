# Feira Marketplace

## Database Architecture

---

# DATABASE PHILOSOPHY

Database Feira Marketplace harus:

* scalable
* modular
* mudah dikembangkan
* aman
* clean relation
* future-ready

Database dirancang bukan hanya untuk mini marketplace saat ini, tetapi juga pondasi:

* konsultasi digital
* ecosystem member
* payment gateway
* subscription system
* AI integration
* future mobile apps

---

# CORE DATABASE MODULES

# 1. USER MODULE

## users

```text
id
name
email
password_hash
phone
role
status
created_at
updated_at
```

## member_profiles

```text
id
user_id
avatar
address
city
province
postal_code
company_name
job_title
bio
created_at
updated_at
```

---

# 2. MARKETPLACE MODULE

## product_categories

```text
id
name
slug
icon
description
status
```

## products

```text
id
category_id
name
slug
short_description
description
price
stock
thumbnail
status
featured
created_at
updated_at
```

## product_images

```text
id
product_id
image_path
sort_order
```

---

# 3. CART SYSTEM

## carts

```text
id
user_id
status
created_at
updated_at
```

## cart_items

```text
id
cart_id
product_id
qty
price
subtotal
```

---

# 4. ORDER SYSTEM

## orders

```text
id
user_id
invoice_number
subtotal
shipping_cost
grand_total
payment_status
order_status
created_at
```

## order_items

```text
id
order_id
product_id
qty
price
subtotal
```

---

# 5. PAYMENT MODULE

## payments

```text
id
order_id
payment_method
payment_reference
payment_status
paid_at
created_at
```

---

# 6. CONSULTATION MODULE

## consultations

```text
id
user_id
ticket_number
category
subject
status
priority
created_at
updated_at
```

## consultation_messages

```text
id
consultation_id
sender_type
message
attachment
created_at
```

---

# 7. NEWS MODULE

## news_categories

```text
id
name
slug
```

## news_articles

```text
id
category_id
title
slug
excerpt
content
thumbnail
featured
published_at
```

---

# 8. NOTIFICATION MODULE

## notifications

```text
id
user_id
title
message
type
is_read
created_at
```

---

# RELATIONSHIP FLOW

```text
users
 ├── member_profiles
 ├── carts
 ├── orders
 ├── consultations
 └── notifications

products
 ├── product_images
 ├── cart_items
 └── order_items

orders
 ├── order_items
 └── payments

consultations
 └── consultation_messages
```

---

# FUTURE DATABASE EXPANSION

Future-ready table:

* subscriptions
* maintenance_contracts
* ai_chat_logs
* support_tickets
* affiliate_system
* service_booking
* multi_vendor

---

# DATABASE RULES

## Rules

* gunakan UUID atau bigint scalable
* soft delete untuk data penting
* index untuk query berat
* foreign key wajib konsisten
* audit log future-ready
* jangan campur business logic di database

---

# PERFORMANCE TARGET

Database harus:

* ringan
* scalable
* mudah di-maintain
* aman untuk transaksi
* siap untuk growth
