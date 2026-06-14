# Auth Module

Phase 2:

- register/login/logout/me melalui `/api/v1/auth`
- forgot/reset password dengan token hash sekali pakai dan expiry 30 menit
- pengiriman reset melalui SMTP, dengan debug URL opt-in untuk development
- SQLite persistence pada private `DATA_ROOT`
- password hash `scrypt`
- opaque HttpOnly session cookie
- session token disimpan sebagai SHA-256 hash
- role `member`, `admin`, dan `super_admin` dengan hierarchy enforcement
- super admin bootstrap melalui `MARKETPLACE_SUPER_ADMIN_EMAILS`
- CSRF validation untuk logout
- seluruh session lama dicabut setelah password reset
