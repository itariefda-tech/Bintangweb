# Payment Module

Phase 5 Midtrans Core API:

- QRIS dan bank transfer VA BCA, BNI, BRI, serta Permata
- sandbox/production configuration melalui environment
- mock gateway lokal saat credential belum tersedia
- payment attempt dan callback event persistence
- SHA-512 callback signature validation
- invoice, amount, status code, fraud status, dan transaction status verification
- idempotent duplicate callback protection
- automatic order/payment status dan member notification

Endpoint callback:

`POST /api/v1/payment/callback/midtrans`
