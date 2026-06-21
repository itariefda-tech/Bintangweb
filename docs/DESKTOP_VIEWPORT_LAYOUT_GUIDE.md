# Desktop Viewport Layout Guide

Dokumen ini menjadi acuan default untuk membenahi layout section khusus desktop. Fokusnya bukan mobile viewport. Mobile tetap mengikuti pola carousel/stack yang sudah ada, sedangkan desktop harus terasa seperti komposisi satu layar yang rapi, penuh, dan terkontrol.

Section yang menjadi bukti keberhasilan:

- `about-section`
- `why-section` / Solutions
- `process-section`
- `proof-section` / Work

## Tujuan

Setiap section desktop harus terlihat seperti satu scene presentasi, bukan sekadar konten panjang yang kebetulan masuk layar.

Target utama:

- Section memenuhi tinggi viewport desktop dengan aman.
- Konten utama tidak kepotong.
- Dekorasi terlihat intentional, bukan menabrak konten.
- Header, copy, cards, dan visual punya area masing-masing.
- Semua card di desktop terasa sejajar dan balanced.
- Tidak memakai pola mobile carousel untuk desktop.

## Breakpoint Acuan

Gunakan desktop behavior mulai dari:

```css
@media (min-width: 900px) {
  /* desktop viewport layout */
}
```

Untuk desktop besar, gunakan refinement:

```css
@media (min-width: 1200px) {
  /* wide desktop composition */
}
```

## Default Section Shell

Pola default section desktop:

```css
@media (min-width: 900px) {
  .target-section {
    display: grid;
    height: var(--desktop-section-height, calc(100svh - 73px));
    min-height: 0;
    padding-block: clamp(1rem, 3svh, 2rem);
    align-items: center;
    overflow: hidden;
  }

  .target-section > .container {
    width: min(100% - (var(--container-gutter) * 2), var(--container-max));
    max-width: 100%;
    min-height: 0;
  }
}
```

Catatan:

- Pakai `height`, bukan hanya `min-height`, jika section memang harus pas viewport.
- Selalu tambahkan `min-height: 0` pada section, container, grid, dan child besar.
- `overflow: hidden` dipakai untuk dekorasi, tetapi jangan sampai menyembunyikan konten utama.
- Jika section berisi konten dinamis yang bisa tinggi, gunakan internal scroll pada area kecil, bukan membiarkan seluruh section pecah.

## Pola About Section Yang Berhasil

About berhasil karena desktop besar dibagi menjadi tiga zona:

1. Copy kiri.
2. Grid card tengah.
3. Quote kanan.

Pola penting:

```css
@media (min-width: 1200px) {
  .about-section > .container {
    width: min(calc(100% - 2rem), 1600px);
    max-width: none;
  }

  .about-grid {
    display: grid;
    height: 100%;
    grid-template-columns:
      minmax(280px, 0.72fr)
      minmax(650px, 1.55fr)
      minmax(240px, 0.63fr);
    grid-template-areas: "copy cards quote";
    gap: clamp(1rem, 1.8vw, 2rem);
    align-items: stretch;
  }
}
```

Pelajaran dari About:

- Gunakan `grid-template-areas` agar struktur desktop jelas.
- Copy tidak perlu memenuhi lebar besar; heading dibuat kuat secara vertikal.
- Card utama dibuat `height: 100%` agar visual rata.
- Quote menjadi panel vertikal untuk mengunci komposisi.
- Decorative image/circuit berada di belakang dengan opacity rendah.

Checklist About-style layout:

- Ada copy column.
- Ada content grid yang menjadi fokus.
- Ada supporting panel atau quote.
- Semua kolom stretch setinggi section.
- Tidak ada card yang ukurannya liar.

## Pola Solution Section

Solution cocok memakai turunan pola About:

1. Intro kiri.
2. Reason grid 2x2 sebagai fokus utama.
3. Path panel kanan pada desktop besar.

Pola desktop sedang:

```css
@media (min-width: 900px) {
  .why-layout {
    height: 100%;
    grid-template-columns: minmax(260px, 0.72fr) minmax(0, 1.28fr);
    grid-template-areas:
      "intro story"
      "path path";
    align-items: stretch;
  }
}
```

Pola desktop besar:

```css
@media (min-width: 1200px) {
  .why-layout {
    grid-template-columns:
      minmax(280px, 0.72fr)
      minmax(560px, 1.45fr)
      minmax(220px, 0.56fr);
    grid-template-areas: "intro story path";
  }
}
```

Pelajaran dari Solution:

- Jika section punya prinsip/benefit, gunakan grid 2x2 sebagai fokus utama.
- Panel proses ringkas bisa menjadi kolom kanan pada desktop besar.
- Desktop sedang boleh membuat panel proses turun sebagai row penuh.
- Intro tetap menjadi anchor kiri, bukan header full-width.
- Background/dekorasi boleh luas karena konten sudah punya area kuat.

## Pola Process Section Yang Berhasil

Process berhasil karena kontennya sederhana dan dijadikan panel horizontal satu baris.

Pola penting:

```css
@media (min-width: 900px) {
  .process-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }

  .process-step {
    border-bottom: 0;
  }

  .process-step,
  .process-step:nth-child(2n) {
    border-right: 1px solid rgba(240, 179, 67, 0.22);
  }

  .process-step:last-child {
    border-right: 0;
  }
}
```

Pelajaran dari Process:

- Jika jumlah item tetap dan pendek, gunakan satu baris horizontal.
- Parent panel boleh punya border, radius, background glass, dan shadow.
- Tiap item cukup padat, tidak perlu card mengambang sendiri-sendiri.
- Background boleh cinematic, tetapi overlay gelap/terang harus menjaga kontras text.

Checklist Process-style layout:

- Header pendek.
- Grid item satu baris.
- Semua item punya ukuran sama.
- Visual rhythm dibentuk dari divider, bukan jarak besar.
- Section background menjadi scene.

## Pola Detailed Services

Detailed Services cocok memakai pola carousel-as-viewport:

1. Header pendek di row atas.
2. Active detail card mengisi sisa viewport.
3. Controls berada di row bawah.
4. Card lain tetap off-canvas agar JS carousel tetap bekerja.

Pola penting:

```css
@media (min-width: 900px) {
  .service-detail-section > .container {
    display: grid;
    height: 100%;
    min-height: 0;
    grid-template-rows: auto minmax(0, 1fr);
  }

  .service-detail-carousel {
    height: 100%;
    min-height: 0;
    grid-template-rows: minmax(0, 1fr) auto;
  }

  .service-detail-list .detail-card {
    height: 100%;
    flex: 0 0 100%;
    min-height: 0;
  }
}
```

Pelajaran dari Detailed Services:

- Carousel desktop tidak harus menampilkan banyak card sekaligus.
- Satu card yang kuat dan penuh viewport lebih mudah dibaca.
- Feature list boleh scroll internal jika jumlah item panjang.
- Controls harus tetap terlihat tanpa mengambil terlalu banyak tinggi.
- Terapkan readability guard karena detail layanan berisi banyak teks.

## Pola Work / Proof Section Yang Berhasil

Work berhasil karena memiliki struktur dashboard desktop:

1. Header pendek.
2. Dossier utama.
3. Project film panel.
4. Client panel.

Pola penting:

```css
@media (min-width: 900px) {
  .proof-section {
    display: grid;
    height: var(--desktop-section-height, calc(100svh - 73px));
    min-height: 0;
    padding-block: clamp(0.75rem, 2svh, 1.25rem);
    align-items: stretch;
  }

  .proof-section > .container {
    display: grid;
    height: 100%;
    min-height: 0;
    grid-template-rows: auto minmax(0, 1fr);
    gap: clamp(0.55rem, 1.5svh, 0.9rem);
  }

  .proof-layout {
    align-items: stretch;
  }
}
```

Wide desktop refinement:

```css
@media (min-width: 1200px) {
  .proof-section > .container {
    width: min(calc(100% - 2rem), 1600px);
    max-width: none;
  }

  .proof-layout {
    grid-template-columns:
      minmax(620px, 1.55fr)
      minmax(260px, 0.67fr)
      minmax(220px, 0.48fr);
    gap: clamp(0.75rem, 1.2vw, 1.15rem);
  }
}
```

Pelajaran dari Work:

- Section yang kompleks perlu `container` dengan `grid-template-rows: auto minmax(0, 1fr)`.
- Header tidak boleh mengambil terlalu banyak tinggi.
- Area utama harus stretch.
- Panel samping boleh lebih sempit, tetapi tetap setinggi area utama.
- Jika ada tab/content dinamis, area aktif harus tetap menjaga tinggi.

Checklist Work-style layout:

- Header ringkas.
- Main layout stretch.
- Panel utama lebih besar dari panel pendukung.
- Panel pendukung tidak jatuh ke bawah pada desktop besar.
- Decorative grid lines berada di background, bukan di atas konten.

## Default Grid Ratio

Gunakan rasio berikut sebagai awal:

### Two Column

Untuk section copy + visual:

```css
grid-template-columns: minmax(300px, 0.8fr) minmax(520px, 1.2fr);
```

### Three Column

Untuk section dashboard seperti About/Work:

```css
grid-template-columns:
  minmax(260px, 0.7fr)
  minmax(600px, 1.5fr)
  minmax(220px, 0.55fr);
```

### Equal Cards

Untuk section proses atau fitur pendek:

```css
grid-template-columns: repeat(var(--item-count, 4), minmax(0, 1fr));
```

## Spacing Default

Gunakan spacing yang mengikuti tinggi viewport:

```css
gap: clamp(0.75rem, 1.6svh, 1.25rem);
padding-block: clamp(1rem, 3svh, 2rem);
```

Untuk desktop besar:

```css
gap: clamp(1rem, 1.8vw, 2rem);
```

Hindari gap besar berbasis `vw` saja karena tinggi viewport bisa pendek.

## Typography Default

Viewport berhasil hanya sah jika text tetap terbaca. Jangan mengecilkan font sampai section tampak muat tetapi kehilangan readability.

Heading desktop section:

```css
font-size: clamp(2rem, min(3.8vw, 5.8svh), 3.35rem);
line-height: 1.05;
```

Heading wide desktop yang sangat penting:

```css
font-size: clamp(2.8rem, min(4vw, 6.2svh), 4.4rem);
line-height: 1.02;
```

Body copy:

```css
font-size: clamp(0.9rem, 1.05vw, 1.08rem);
line-height: 1.6;
```

Card body:

```css
font-size: clamp(0.78rem, 0.9vw, 0.94rem);
line-height: 1.5;
```

## Minimum Font Rules

Ambil About section sebagai batas bawah readability. Untuk text penjelasan utama pada card, ukuran normal terkecil adalah sekitar `0.78rem`. Pada desktop pendek boleh dibuat lebih compact, tetapi jangan turun terlalu jauh.

Aturan minimum:

- Section intro/body paragraph: minimal `0.8rem`.
- Card detail paragraph: ideal minimal `0.78rem`.
- Card detail paragraph pada desktop pendek: emergency minimal `0.74rem`.
- Card title: minimal `0.96rem`.
- Micro-label/kicker/badge: minimal `0.62rem`.
- Jangan gunakan `0.58rem` untuk label penting yang perlu dibaca.
- Footer/ornamental label boleh lebih kecil hanya jika bukan informasi utama.

Template desktop pendek:

```css
@media (min-width: 900px) and (max-height: 700px) {
  .section-intro > p:not(.eyebrow) {
    font-size: clamp(0.8rem, 0.94vw, 0.9rem);
    line-height: 1.48;
  }

  .section-card h3 {
    font-size: clamp(0.96rem, 1.1vw, 1.08rem);
  }

  .section-card > p {
    font-size: clamp(0.74rem, 0.84vw, 0.82rem);
    line-height: 1.45;
  }

  .section-kicker,
  .section-label {
    font-size: 0.62rem;
  }
}
```

Jika section tidak muat setelah batas minimum ini dipakai, solusinya bukan mengecilkan text lagi. Kurangi copy, ubah layout, tambah internal scroll kecil, atau pecah konten menjadi panel yang lebih jelas.

Jika ada rule compact seperti `@media (min-width: 900px) and (max-height: 700px)`, tambahkan readability guard di bawah seluruh rule desktop agar batas minimum tidak kalah cascade:

```css
@media (min-width: 900px) {
  .target-section .section-card > p {
    font-size: clamp(0.86rem, 0.92vw, 0.96rem);
    line-height: 1.55;
  }

  .target-section .section-kicker,
  .target-section .section-label {
    font-size: clamp(0.66rem, 0.72vw, 0.76rem);
  }
}
```

Gunakan guard ini khusus pada section yang terbukti masih terlihat micro setelah layout viewport berhasil.

## Card Rules

Desktop cards harus:

- Punya `min-width: 0`.
- Punya tinggi yang terkunci oleh grid, bukan oleh konten random.
- Menggunakan `height: 100%` jika berada dalam area stretch.
- Punya padding yang lebih kecil daripada mobile besar.
- Menggunakan image/silhouette dengan `object-fit: contain`.
- Tidak membuat nested card kecuali memang panel utama.

Template:

```css
.section-card {
  display: grid;
  min-width: 0;
  min-height: 0;
  height: 100%;
  overflow: hidden;
  padding: clamp(0.9rem, 1.35vw, 1.35rem);
}
```

## Decoration Rules

Dekorasi desktop harus mengikuti aturan:

- Letakkan di background layer.
- Gunakan `position: absolute`.
- Gunakan `z-index: 0`.
- Konten utama harus `position: relative; z-index: 1`.
- Opacity rendah: sekitar `0.08` sampai `0.34`.
- Dekorasi boleh keluar section, tetapi section harus `overflow: hidden`.
- Dekorasi tidak boleh menjadi alasan text/card kepotong.

Template:

```css
.target-section {
  position: relative;
  isolation: isolate;
  overflow: hidden;
}

.target-section::before {
  content: "";
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.target-section > .container {
  position: relative;
  z-index: 1;
}
```

## Kapan Pakai `.desktop-viewport-section`

Class `.desktop-viewport-section` bisa dipakai untuk section yang sederhana dan ingin dipusatkan dalam viewport.

Pola yang sudah ada:

```css
.desktop-viewport-section {
  display: grid;
  height: var(--desktop-section-height, calc(100svh - 73px));
  min-height: 0;
  padding-block: clamp(1rem, 3svh, 2rem);
  place-items: center;
  overflow: hidden;
}
```

Gunakan untuk:

- Section dengan satu header dan satu grid.
- Section yang tidak punya panel kompleks.
- Section yang kontennya bisa diskalakan aman.

Jangan gunakan apa adanya untuk:

- Section dengan banyak panel interaktif.
- Section yang butuh 3 kolom seperti About.
- Section dengan media/video besar seperti Work.

## Audit Sebelum Membenahi Section Lain

Sebelum edit section lain, jawab ini dulu:

1. Section ini harus mengikuti pola About, Process, Work, atau pola baru?
2. Apakah section harus pas 1 viewport desktop?
3. Berapa area utama yang dibutuhkan: 1, 2, atau 3 kolom?
4. Apakah header perlu masuk row sendiri?
5. Apakah ada panel yang harus stretch full-height?
6. Apakah card terlalu banyak untuk 1 viewport?
7. Apakah perlu internal scroll atau ringkas copy?
8. Apakah dekorasi berada di layer background?
9. Apakah mobile tetap memakai pola lama?
10. Apakah `min-height: 0` sudah dipasang di semua grid parent penting?

## Default Decision

Jika ragu:

- Untuk section storytelling, tiru About.
- Untuk section step pendek, tiru Process.
- Untuk section showcase/proof/media, tiru Work.
- Untuk section sederhana, pakai `.desktop-viewport-section`.

## Do Not

- Jangan paksa desktop memakai mobile horizontal scroll.
- Jangan biarkan heading besar membuat card turun keluar viewport.
- Jangan memakai `min-height: 100vh` tanpa memperhitungkan sticky header.
- Jangan memberi padding terlalu besar di desktop viewport pendek.
- Jangan membuat dekorasi berada di atas konten.
- Jangan memperbaiki desktop dengan mengorbankan mobile.

## Target Akhir

Setiap section desktop harus terasa seperti slide premium dalam company profile:

- Ada hierarchy jelas.
- Ada visual anchor.
- Ada breathing room.
- Semua elemen masuk viewport.
- Dekorasi mendukung mood.
- Layout tetap stabil di desktop pendek dan desktop lebar.
