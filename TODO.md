# TODO.md
## Mini Marketplace Feira Development Tracker

### Active Phase
PHASE 2 - AUTH & MEMBER SYSTEM (LIMITED FOUNDATION)

### Current Focus
Membangun member profile persistence dan profile settings dengan migration versioning, API terproteksi, serta form mobile-first. Avatar upload dan notification center tetap di luar scope stage ini.

### Last Progress
- Seluruh dokumen `docs/MARKET_FEIRA*.md` sudah dibaca.
- Stack existing sudah dipetakan: static frontend, Node build script, dan Python `SimpleHTTPRequestHandler`.
- Struktur modular `src/`, UI foundation, reusable component, dan shared marketplace shell sudah dibuat.
- Semua route placeholder Phase 1 berhasil diakses dari source dan production build.
- Audit visual menemukan risiko min-content overflow pada 360px dan sudah diperbaiki.
- `npm run build`, Python compile check, JavaScript syntax check, dan HTTP smoke test berhasil.
- Keputusan Phase 2: SQLite pada `DATA_ROOT`, password hash `scrypt`, opaque session token yang disimpan sebagai hash, cookie HttpOnly/SameSite, API `/api/v1/auth/*`, dan role awal `member`.
- API register/login/logout/me, protected route, dan UI auth sudah aktif.
- Session terbukti tetap valid setelah restart server dengan `DATA_ROOT` yang sama.
- Unit test menemukan file handle SQLite belum tertutup; connection lifecycle sudah diperbaiki dan test ulang lulus.
- Build production, raw guest redirect, CSRF logout, origin guard, dan login validation lulus.
- Ruang drive C sudah kembali sekitar 3,37 GB; blocker `ENOSPC` selesai.

### Files Created / Modified
- `TODO.md`
- `src/app/marketplace-app.js`
- `src/components/**`
- `src/config/marketplace.js`
- `src/layouts/MarketplaceLayout.js`
- `src/modules/**`
- `src/pages/marketplace-shell.html`
- `src/services/README.md`
- `src/styles/**`
- `src/utils/README.md`
- `app.py`
- `scripts/build.js`
- `Dockerfile`
- `index.html`
- `sitemap.xml`
- `docs/MARKET_FEIRA_ROADMAP.md`
- `marketplace_auth.py`
- `tests/test_marketplace_auth.py`
- `.env.example`
- `src/services/auth-service.js`

### Issues / Notes
- Repo tidak memakai frontend framework; struktur guideline diadaptasikan ke ES modules dan static page shell.
- Dokumen Feira masih untracked dan tidak boleh tertimpa.
- Data demo yang digunakan pada Phase 1 harus diberi label mock/seed sementara.
- Order content, consultation workflow, checkout transaction, dan product detail masih UI placeholder.
- Database, session member, auth middleware, dan auth API foundation sudah diimplementasikan.
- Cart persistence, payment, upload system, logging system, dan API module lain belum diimplementasikan.
- Register/login akan memakai rate limit in-memory dasar; hardening terdistribusi tetap menjadi scope Phase 10.
- Forgot password, profile settings, avatar, dan notification center tidak termasuk stage terbatas ini.
- Role schema sudah future-ready, tetapi role management/admin assignment belum tersedia.
- Session database memakai schema bootstrap idempotent; migration versioning formal belum tersedia.
- Audit screenshot final Edge headless mengalami timeout setelah cache-buster update; source responsive fix, route, dan build test tetap berhasil.
- Drive C hanya menyisakan sekitar 24 MB setelah audit; build/test sempat gagal `ENOSPC` dan berhasil setelah folder audit sementara dibersihkan. Ruang disk perlu ditambah sebelum stage berikutnya.

### Next Step
- Tambahkan schema migration tracker dan tabel `member_profiles`.
- Buat API GET/PUT profile dengan session, same-origin, CSRF, dan validation.
- Buat route `/member/profile` serta form settings mobile-first.
- Verifikasi upgrade database existing, persistence, build, dan responsive behavior.

### Checklist
- [x] Baca roadmap dan seluruh foundation docs.
- [x] Identifikasi stack serta batas implementasi Phase 1.
- [x] Buat struktur folder `src`.
- [x] Buat module placeholder.
- [x] Buat UI foundation mobile-first.
- [x] Buat reusable component awal.
- [x] Buat route/page placeholder.
- [x] Verifikasi build dan route.
- [x] Update roadmap dan tracker akhir.
- [x] Buat persistence user SQLite.
- [x] Buat password hashing dan verification.
- [x] Buat persistent member session.
- [x] Buat API register/login/logout/me.
- [x] Proteksi route member dan checkout.
- [x] Sambungkan form auth dan header member.
- [x] Verifikasi restart persistence dan security behavior.
- [x] Update roadmap dan tracker Phase 2.
- [ ] Tambahkan schema migration versioning.
- [ ] Buat persistence dan validation member profile.
- [ ] Buat API GET/PUT member profile.
- [ ] Buat route dan UI profile settings.
- [ ] Verifikasi migration, persistence, security, dan responsive behavior.
- [ ] Update roadmap dan tracker profile stage.
