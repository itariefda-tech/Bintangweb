# Auth Module

Phase 2 limited foundation:

- register/login/logout/me melalui `/api/v1/auth`
- SQLite persistence pada private `DATA_ROOT`
- password hash `scrypt`
- opaque HttpOnly session cookie
- session token disimpan sebagai SHA-256 hash
- role awal `member`
- CSRF validation untuk logout

Forgot password, profile settings, avatar, dan advanced hardening belum termasuk stage ini.
