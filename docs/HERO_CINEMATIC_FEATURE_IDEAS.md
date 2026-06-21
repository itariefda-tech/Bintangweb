# Hero Cinematic Feature Ideas

Dokumen ini berisi ide pengembangan hero section Bintang Computer Feira agar terasa lebih cinematic, modern, premium, dan tetap relevan dengan brand "Light Premium Tech Consultant".

## Tujuan Visual

Hero perlu terasa seperti "control room modern" untuk bisnis: rapi, meyakinkan, teknologis, tetapi tetap hangat dan mudah dipahami. Efek cinematic sebaiknya mendukung pesan utama, bukan sekadar ramai.

Prinsip utama:

- Premium, clean, tidak terlalu gelap.
- Tetap memakai cream, gold, brown, dan light blue.
- Animasi terasa halus, bukan agresif.
- Visual langsung menunjukkan dunia IT: network, CCTV, cloud, support, server, dashboard.
- Mobile tetap ringan dan tidak penuh efek berat.

## Ide Feature Cinematic

### 1. 3D Floating IT Object

Tambahkan objek visual 3D di dalam atau di belakang cinematic card, misalnya:

- Mini server rack 3D.
- CCTV camera 3D.
- Cloud node 3D.
- Router/network cube 3D.
- Shield security 3D.

Konsep terbaik: objek 3D berupa "tech core" yang melayang di sisi kanan card, berputar pelan 6-10 derajat, dengan soft gold rim light.

Implementasi ringan:

- Gunakan PNG/WebP transparent 3D render.
- Tambahkan CSS `transform: rotateY(...) translateY(...)`.
- Tidak perlu Three.js dulu jika hanya butuh efek premium ringan.

Implementasi advanced:

- Three.js scene kecil untuk model server/CCTV.
- Mouse parallax halus.
- Auto rotate pelan.
- Matikan di mobile atau reduced-motion.

Prioritas: High.

#### Prompt ChatGPT Untuk Merancang Detail Visual

Gunakan prompt ini ke ChatGPT untuk meminta bantuan merancang konsep visual, bukan meminta langsung dibuatkan asset final:

```text
Saya sedang merancang hero section website untuk brand Bintang Computer Feira, sebuah konsultan IT dan penyedia solusi teknologi bisnis. Brand direction-nya adalah Light Premium Tech Consultant: modern, clean, premium, friendly, tech-savvy, tidak terlalu gelap, dengan warna cream, soft white, gold, brown, dan light blue.

Saya ingin membuat elemen "3D Floating IT Object" untuk hero section. Objek utamanya adalah:
1. komputer AIO modern,
2. rack server premium.

Tolong bantu saya merancang konsep detail visual untuk asset ini sebagai arahan desain, bukan langsung membuat kode. Saya ingin hasilnya bisa dipakai sebagai brief untuk Figma, Midjourney, atau designer 3D.

Kebutuhan visual:
- Objek komputer AIO dan rack server terlihat premium, modern, dan corporate.
- Komputer AIO berada sedikit di depan, rack server berada di belakang atau samping sebagai depth layer.
- Style 3D semi-realistic, glossy soft, bukan kartun lucu dan bukan cyberpunk gelap.
- Warna utama mengikuti brand: cream/soft white body, dark brown/charcoal detail, gold accent tipis, light blue glow.
- Ada soft rim light gold di pinggir objek.
- Ada glow light blue halus dari screen AIO atau indikator server.
- Objek harus cocok ditempatkan di hero website berlatar cream-light blue.
- Komposisi harus punya transparent background jika nanti dibuat asset PNG/WebP.
- Mood: premium IT control room, modern business technology, clean cinematic.

Tolong bantu pecah output menjadi:
1. Konsep visual utama.
2. Komposisi layout objek untuk hero website desktop.
3. Komposisi versi mobile.
4. Detail bentuk komputer AIO.
5. Detail bentuk rack server.
6. Lighting dan material.
7. Palet warna rekomendasi.
8. Prompt Midjourney untuk membuat asset 3D transparent background.
9. Prompt alternatif untuk DALL-E/image generator lain.
10. Arahan layer di Figma: layer mana di depan, belakang, glow, shadow, dan highlight.
11. Catatan agar asset tetap ringan untuk website.
12. Negative prompt agar hasil tidak menjadi terlalu gaming, neon berlebihan, dark cyberpunk, atau terlalu ramai.

Berikan hasil yang detail, praktis, dan siap dipakai sebagai creative brief.
```

#### Prompt Midjourney Awal

Prompt ini bisa dipakai setelah brief ChatGPT dirapikan:

```text
premium 3D floating IT hardware object, modern all-in-one computer in front with a clean glowing dashboard screen, elegant rack server behind it, semi realistic 3D render, soft glossy material, cream white body, charcoal details, subtle gold accents, light blue indicator lights, warm gold rim light, soft shadow, transparent background, clean corporate technology aesthetic, premium IT consultant website hero asset, minimal cinematic composition, high detail, no text, no logo --ar 1:1 --v 6 --style raw
```

#### Negative Prompt Midjourney

```text
dark cyberpunk, gaming pc, RGB overload, messy cables, aggressive neon, cartoon style, low quality, blurry, distorted monitor, unreadable text, brand logo, watermark, human character, cluttered background, heavy black background
```

#### Arahan Figma Untuk Asset

- Buat frame asset rasio `1:1` atau `4:3`.
- Tempatkan rack server di belakang kanan dengan opacity/shadow yang memberi depth.
- Tempatkan komputer AIO di depan kiri atau center-front.
- Tambahkan glow light blue dari layar AIO.
- Tambahkan rim light gold tipis di sisi kanan objek.
- Tambahkan soft ellipse shadow di bawah objek.
- Export sebagai transparent WebP/PNG ukuran sekitar `900-1200px`.
- Siapkan versi desktop dan mobile crop.

### 2. Hero Title Sequential Fade In

Judul "Complete IT Solutions for Smarter Business" bisa dibuat muncul per baris atau per kata.

Contoh ritme:

- Eyebrow muncul dulu dari atas.
- Kata "Complete IT" fade in.
- Kata "Solutions" muncul dengan slight shimmer gold.
- Baris "for Smarter Business" naik pelan dari bawah.
- Subtitle menyusul 200-300ms setelah title selesai.

Efek ini membuat first impression lebih cinematic tanpa mengubah layout.

Prioritas: High.

### 3. Gold Shimmer Sweep Pada Title

Tambahkan shimmer tipis pada kata penting, misalnya "Smarter Business" atau "IT Solutions".

Gaya:

- Gradient gold tipis berjalan dari kiri ke kanan.
- Durasi 3-5 detik.
- Loop pelan, tidak terus menyala.
- Bisa aktif hanya setelah title fade-in selesai.

Catatan desain:

- Jangan shimmer seluruh judul, cukup 1 frasa agar tidak terlihat berlebihan.
- Warna shimmer gunakan `rgba(201, 154, 58, 0.85)` dan highlight `#fff4c7`.

Prioritas: High.

### 4. Cinematic Card Scene Rotation

Card hero saat ini sudah berisi status `Network`, `Security`, `Backup`, `Support`. Bisa dibuat seperti mini scene yang berganti state.

Loop scene:

1. Infrastructure Live
2. CCTV Monitoring
3. Cloud Backup
4. Direct Support

Setiap scene mengganti:

- Label header.
- 4 metric cards.
- Signal pattern.
- Accent glow.

Contoh copy:

- `CCTV Monitoring` / `Camera Online`, `Motion Check`, `Report Ready`, `Alert Active`
- `Cloud Backup` / `Auto Sync`, `Encrypted`, `Restore Ready`, `Daily Check`
- `Direct Support` / `Ticket Open`, `Remote Assist`, `Field Team`, `Resolved`

Implementasi:

- CSS-only jika scene dibuat sebagai beberapa layer.
- JS kecil jika ingin text berubah dinamis.

Prioritas: Medium.

### 5. Data Stream Lines

Tambahkan garis data tipis yang mengalir dari kiri hero menuju card cinematic.

Gaya:

- Line gold/blue 1px.
- Ada dot kecil bergerak mengikuti garis.
- Mengarah dari trust row/CTA ke dashboard card.
- Opacity rendah agar tidak mengganggu teks.

Efek ini memberi rasa "system connected" antara pesan brand dan visual card.

Prioritas: Medium.

### 6. Parallax Layer Saat Mouse Bergerak

Hero bisa diberi interaksi halus:

- Decor circuit bergerak 4-8px.
- Cinematic card bergerak 8-14px.
- Orbit/glow bergerak sedikit berlawanan arah.
- 3D object bergerak paling besar, sekitar 16-24px.

Catatan:

- Aktif hanya desktop.
- Gunakan `requestAnimationFrame`.
- Respect `prefers-reduced-motion`.
- Jangan mengubah posisi text terlalu banyak.

Prioritas: Medium.

### 7. Scanline dan HUD Pulse

Tambahkan efek scanline tipis di dalam cinematic dashboard.

Detail:

- Horizontal scanline bergerak turun setiap 4-6 detik.
- Saat scanline lewat, grid card sedikit glow.
- Signal bar menyala mengikuti scanline.

Efek ini cocok untuk kesan monitoring/control room.

Prioritas: Medium.

### 8. CTA Button Magnetic Glow

CTA utama "Konsultasi Sekarang" bisa diberi efek premium:

- Glow gold lembut saat hover.
- Shine sweep diagonal.
- Icon panah kecil muncul saat hover.
- Button sedikit naik 2px.

Efek ini membuat action terasa lebih hidup tanpa mengganggu hero.

Prioritas: Medium.

### 9. Metric Counter Reveal

Angka `20+`, `6`, dan `1` bisa muncul dengan counter animation saat hero masuk viewport.

Detail:

- Counter dari 0 ke nilai akhir selama 900-1200ms.
- Setelah selesai, card metric pulse sekali.
- Jangan loop terus menerus.

Catatan:

- Untuk angka `1`, cukup fade/scale, tidak perlu counter.

Prioritas: Low-Medium.

### 10. Background Cinematic Light Sweep

Tambahkan light sweep besar yang bergerak sangat pelan di belakang hero.

Gaya:

- Cream-to-blue translucent beam.
- Gerak diagonal dari kanan atas ke kiri bawah.
- Durasi 14-20 detik.
- Opacity rendah.

Efek ini membuat area hero terasa seperti scene, bukan hanya layout statis.

Prioritas: Low-Medium.

### 11. Floating Service Chips

Tambahkan chip kecil yang muncul/hilang di sekitar card:

- CCTV
- Network
- Cloud
- PABX
- Apps
- Procurement

Ritme:

- Muncul satu per satu.
- Drift ringan.
- Fade out saat cinematic card keluar.

Catatan:

- Batasi maksimal 3 chip tampil bersamaan.
- Di mobile sebaiknya hidden.

Prioritas: Medium.

### 12. Cinematic Intro Timeline

Saat halaman pertama kali dibuka:

1. Background glow masuk.
2. Eyebrow muncul.
3. Title muncul per baris.
4. Subtitle dan CTA muncul.
5. Metrics masuk.
6. Cinematic card muncul dari atas.
7. Shimmer title aktif.
8. Card mulai loop 15 detik.

Ini memberi pengalaman hero yang lebih terarah.

Prioritas: High.

## Rekomendasi Paket Implementasi

### Paket 1: Quick Cinematic Upgrade

Paling aman untuk dikerjakan cepat.

- Title sequential fade-in.
- Gold shimmer pada frasa penting.
- CTA shine hover.
- Scanline dashboard.
- Background light sweep.

Estimasi kompleksitas: rendah.

### Paket 2: Premium Dashboard Hero

Membuat hero terasa jauh lebih hidup.

- Cinematic card scene rotation.
- Floating service chips.
- Data stream lines.
- Metric counter reveal.
- Parallax desktop.

Estimasi kompleksitas: sedang.

### Paket 3: Signature 3D Hero

Versi paling kuat secara visual.

- 3D floating object berupa server/CCTV/cloud node.
- Mouse parallax multi-layer.
- Hero intro timeline.
- Dashboard scene rotation.
- Shimmer title yang sinkron dengan card.

Estimasi kompleksitas: tinggi.

## Prioritas Yang Saya Sarankan

Untuk tahap berikutnya, mulai dari kombinasi ini:

1. Hero title sequential fade-in.
2. Gold shimmer pada "Smarter Business".
3. Scanline dalam cinematic dashboard.
4. Floating 3D PNG/WebP object, bukan Three.js dulu.
5. Data stream lines tipis dari kiri ke card.

Alasannya: dampak visual tinggi, risiko layout kecil, performa lebih aman, dan tetap cocok dengan style brand sekarang.

## Catatan Teknis

- Simpan animasi utama di `css/responsive.css` atau `css/components.css` sesuai area yang sudah ada.
- Gunakan class khusus seperti `.hero-title-line`, `.hero-shimmer-text`, `.hero-data-stream`, dan `.cinematic-3d-object`.
- Jangan memakai animasi berat di mobile.
- Tambahkan rule `@media (prefers-reduced-motion: reduce)`.
- Pastikan tidak ada text yang bergeser setelah load.
- Gunakan `will-change` hanya pada elemen yang benar-benar bergerak.
- Jika memakai gambar 3D, gunakan WebP transparent dan preload jika tampil di first viewport.

## Contoh Struktur Hero Tambahan

```html
<h1 class="hero-title">
  <span class="hero-title-line">Complete IT</span>
  <span class="hero-title-line hero-shimmer-text">Solutions</span>
  <span class="hero-title-line">for Smarter Business</span>
</h1>

<div class="hero-data-stream" aria-hidden="true">
  <span></span>
  <span></span>
  <span></span>
</div>

<img
  class="cinematic-3d-object"
  src="./assets/images/hero-server-3d.webp"
  width="420"
  height="420"
  alt=""
  aria-hidden="true"
>
```

## Mood Reference Internal

Hero yang ideal terasa seperti:

- Company profile IT premium.
- Dashboard control room.
- Subtle sci-fi, tetapi tetap corporate.
- Ada motion yang elegan, bukan gaming.
- Ada kedalaman visual melalui layer, glow, dan objek 3D.
