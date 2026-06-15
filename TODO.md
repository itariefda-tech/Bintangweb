# TODO.md
## Mini Marketplace Feira Development Tracker

### Active Phase
PHASE 8 - ADMIN ECOSYSTEM

### Current Focus
Membangun control center Phase 8 secara bertahap. Dashboard, consultation, order, product, dan owner-credential News Management sudah aktif.

### Last Progress
- Route `/admin` dan `/admin/consultation` dilindungi untuk role `admin` dan `super_admin`.
- Dashboard admin menampilkan KPI nyata dari SQLite.
- Consultation queue menampilkan member, thread, attachment, prioritas, dan status.
- Admin dapat reply dan update status ticket melalui API dengan CSRF.
- Order monitoring menyediakan filter payment/order status dan detail invoice snapshot.
- Fulfillment berjalan berurutan dari paid, processing, shipped, hingga completed.
- Member menerima notifikasi setiap status fulfillment berubah.
- Product management role-based menyediakan create, edit, upload gambar, featured, stock/status, preview, dan archive.
- Owner builder tidak lagi diperlukan untuk operasi katalog harian.
- News Management tersedia sebagai section khusus `09 / Feira IT News` pada Owner Tool Builder.
- Owner dapat mengelola kategori, draft/publish/archive, featured, trending score, reading time, cover, dan preview artikel.
- Navigation admin tersedia pada desktop dan mobile sesuai role.
- Source dan production build memakai service admin modular.
- Seluruh test suite lulus 48 test.

### Active Files
- `app.py`
- `marketplace_admin.py`
- `marketplace_consultation.py`
- `src/app/marketplace-app.js`
- `src/layouts/MarketplaceLayout.js`
- `src/services/admin-service.js`
- `src/styles/components.css`
- `src/styles/responsive.css`
- `tests/test_marketplace_admin.py`
- `tests/test_marketplace_consultation.py`
- `docs/MARKET_FEIRA_ROADMAP.md`

### Issues / Notes
- Endpoint product owner lama masih tersedia sebagai compatibility path sementara.
- News management sengaja memakai credential owner, bukan role admin.
- Member management belum memiliki UI admin baru.
- Logging system foundation masih terbuka dari Phase 1.
- Security hardening menyeluruh tetap menjadi scope Phase 10.

### Next Step
- Lanjutkan member management.

### Checklist
- [x] Buat protected admin routes.
- [x] Buat admin dashboard shell.
- [x] Buat KPI API dan cards.
- [x] Buat consultation queue UI.
- [x] Sambungkan admin reply dan status update.
- [x] Tambahkan test permission dan KPI.
- [x] Sinkronkan roadmap dan tracker.
- [x] Buat order monitoring.
- [x] Buat filter payment dan order status.
- [x] Tampilkan detail snapshot invoice.
- [x] Buat state machine fulfillment.
- [x] Kirim notifikasi fulfillment ke member.
- [x] Buat product management.
- [x] Buat product create dan edit.
- [x] Buat upload media produk berbasis role admin.
- [x] Buat stock, status, featured, preview, dan archive.
- [x] Buat News Management pada Owner Tool Builder.
- [x] Buat category create dan edit.
- [x] Buat article draft, publish, edit, preview, dan archive.
- [x] Buat cover upload dengan file signature validation.
- [ ] Buat member management.
