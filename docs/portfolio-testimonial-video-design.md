# Portfolio, Testimonial & Video Section

## Status

Implemented foundation.

Markup, visual responsive, portfolio selector, testimonial placeholder, dan video empty state sudah tersedia. Publikasi identitas customer, komentar asli, foto proyek, serta video final masih menunggu aset dan izin yang terverifikasi.

## Placement

Section baru ditempatkan tepat di antara:

1. `Process`
2. `Proof Room` (section baru)
3. `Contact`

Pada desktop, area portofolio/testimoni dan pemutar video tampil berdampingan. Pada mobile, keduanya menjadi satu alur vertikal yang tetap terasa terhubung.

---

## 1. Creative Direction

### Nama Section

**Proof Room**

### Eyebrow

**Selected Work / Client Stories**

### Headline

**Bukan sekadar selesai dipasang. Harus terasa lebih siap dipakai.**

### Supporting Copy

Beberapa sistem yang kami rancang bersama customer, dari kebutuhan operasional sehari-hari hingga fondasi teknologi untuk pertumbuhan berikutnya.

### Tujuan Naratif

Section ini adalah bukti setelah pengunjung memahami proses kerja Bintang Computer Feira:

* Portofolio menunjukkan apa yang dikerjakan.
* Testimoni menunjukkan bagaimana pengalaman customer.
* Video menunjukkan kualitas kerja secara visual.
* Contact menjadi langkah natural setelah kepercayaan terbentuk.

Hasil akhirnya harus terasa seperti mini case-study gallery, bukan kumpulan logo dan quote generik.

---

## 2. Master Layout

Gunakan satu section induk, bukan tiga section yang terputus.

```text
+------------------------------------------------------------------+
| SELECTED WORK / CLIENT STORIES                                   |
| Bukan sekadar selesai dipasang. Harus terasa lebih siap dipakai. |
+--------------------------------------+---------------------------+
|                                      |                           |
|  PORTFOLIO + TESTIMONIAL              |  CINEMATIC VIDEO PLAYER   |
|  7 columns                            |  5 columns                |
|                                      |                           |
|  Customer selector                    |  Project poster           |
|  Active case visual                   |  Play control             |
|  Scope + result                       |  Duration + chapter       |
|  Customer comment                     |  Short video description  |
|                                      |                           |
+--------------------------------------+---------------------------+
```

### Desktop

* Grid utama: `minmax(0, 7fr) minmax(340px, 5fr)`.
* Gap: `24px` sampai `32px`.
* Kedua panel memiliki tinggi visual yang seimbang.
* Section boleh mendekati satu viewport, tetapi tidak menggunakan fixed height.
* Komposisi dibuat asimetris agar terlihat editorial dan tidak seperti template kartu biasa.

### Tablet

* Tetap berdampingan selama masing-masing panel masih memiliki ruang yang layak.
* Pada lebar sempit, grid berubah menjadi satu kolom.
* Video diletakkan setelah active case agar alur bukti tetap logis.

### Mobile

Urutan konten:

1. Eyebrow dan headline
2. Customer selector horizontal
3. Active portfolio case
4. Testimonial
5. Video player
6. CTA menuju Contact

Customer selector menggunakan horizontal scroll dengan scroll-snap. Tidak memakai carousel otomatis.

---

## 3. Portfolio Panel

### Konsep Visual

Panel portofolio dibuat seperti **project dossier** modern: perpaduan antara visual proyek, informasi sistem, dan hasil yang diperoleh. Logo customer hanya menjadi identitas pendukung, bukan isi utama.

### Customer Selector

Tampilkan 4 sampai 6 customer. Setiap item berisi:

* Logo atau monogram customer
* Nama customer
* Jenis industri
* Status kecil seperti `Completed`, `Ongoing`, atau `Support`

Contoh struktur:

```text
[ Customer A ] [ Customer B ] [ Customer C ] [ Customer D ]
  Retail          Office        Hospitality    Professional Service
```

Customer aktif memiliki:

* Garis gold tipis
* Background cream-glass
* Titik status light blue
* Nomor editorial seperti `01 / 04`

### Active Case Card

#### Bagian Visual

Gunakan satu gambar proyek yang kuat:

* Foto rack/network yang rapi
* CCTV command view
* Website atau dashboard pada device mockup
* Teknisi saat testing

Tambahkan overlay informasi, bukan dekor berlebihan:

```text
PROJECT 01
Integrated Office System
Jakarta / 2026
```

#### Bagian Informasi

Setiap case berisi:

* **Customer**: nama customer
* **Challenge**: masalah utama dalam satu kalimat
* **Solution**: maksimal tiga scope pekerjaan
* **Outcome**: satu hasil terverifikasi
* **Service tags**: contoh `Network`, `CCTV`, `Procurement`

### Draft Content Pattern

Gunakan pola berikut saat data customer asli sudah tersedia:

#### Case 01 - Office Infrastructure

**Title:** Satu fondasi untuk perangkat, jaringan, dan kontrol operasional.

**Challenge:** Perangkat berkembang tanpa struktur jaringan dan dokumentasi yang konsisten.

**Solution:**

* Penataan network dan segmentasi perangkat
* Pengadaan perangkat sesuai kapasitas kerja
* Dokumentasi titik, akses, dan konfigurasi utama

**Outcome:** Tim memiliki sistem yang lebih mudah dipantau, dirawat, dan dikembangkan.

#### Case 02 - Security & Monitoring

**Title:** Area penting terlihat jelas, akses monitoring tetap sederhana.

**Challenge:** Titik pengawasan belum mencakup area prioritas dan proses pengecekan rekaman memakan waktu.

**Solution:**

* Audit titik kamera
* Instalasi CCTV dan recording
* Remote monitoring untuk personel berwenang

**Outcome:** Monitoring harian menjadi lebih cepat dengan cakupan yang lebih relevan.

#### Case 03 - Business Website

**Title:** Identitas bisnis yang lebih meyakinkan sejak kunjungan pertama.

**Challenge:** Informasi layanan tersebar dan belum memiliki presentasi digital yang konsisten.

**Solution:**

* Penyusunan arsitektur konten
* UI responsive dan premium
* Integrasi jalur inquiry ke WhatsApp

**Outcome:** Customer mendapatkan jalur yang lebih jelas dari mengenal layanan menuju konsultasi.

> Catatan: Nama, foto, tahun, ruang lingkup, dan outcome di atas adalah pola editorial. Jangan dipublikasikan sebagai proyek nyata sebelum mendapat konfirmasi.

---

## 4. Testimonial Module

### Posisi

Testimoni berada di dalam panel portofolio, tepat di bawah informasi active case. Komentar berubah mengikuti customer yang dipilih sehingga portofolio dan testimoni selalu memiliki konteks yang sama.

### Visual

* Quote mark besar tetapi transparan sebagai elemen latar.
* Komentar maksimal 2 sampai 4 baris pada desktop.
* Avatar atau monogram kecil.
* Nama, jabatan, dan perusahaan.
* Label verifikasi seperti `Verified project feedback` hanya digunakan jika benar-benar dapat dibuktikan.

### Copy Direction

Komentar harus terdengar spesifik dan manusiawi. Hindari:

* "Pelayanannya sangat memuaskan."
* "Recommended banget."
* "Cepat, ramah, dan profesional."

Format yang lebih kuat:

> "Tim Bintang membantu kami memahami mana yang perlu dibenahi lebih dulu. Implementasinya rapi, dan saat ada penyesuaian kami tidak perlu menjelaskan semuanya dari awal."

Alternatif untuk proyek digital:

> "Yang paling terasa bukan hanya tampilan barunya, tetapi alur informasi yang sekarang jauh lebih mudah dipahami customer kami."

### Aturan Integritas Konten

* Jangan membuat nama, jabatan, komentar, atau angka performa fiktif.
* Quote boleh dirapikan untuk keterbacaan tanpa mengubah makna.
* Minta persetujuan customer sebelum menampilkan identitas dan foto.
* Jika customer meminta privasi, gunakan format seperti `Operations Manager, Retail Company`.
* Jangan memakai rating bintang jika tidak berasal dari sistem review yang nyata.

---

## 5. Cinematic Video Player

### Tujuan

Video bukan dekorasi. Isinya harus menjadi bukti kerja singkat yang dapat dipahami walau tanpa suara.

### Poster Frame

Poster menggunakan frame proyek paling kuat, dengan:

* Gradient navy transparan
* Garis framing gold yang sangat tipis
* Tombol play besar di area focal point
* Label `Field Notes 01`
* Durasi, contoh `01:18`
* Caption: `From planning room to final testing`

### Video Content

Durasi ideal: **60 sampai 90 detik**.

Struktur cerita:

1. `0-05 detik` - Masalah atau kondisi awal
2. `05-18 detik` - Survey dan planning
3. `18-45 detik` - Instalasi atau development
4. `45-65 detik` - Testing dan quality check
5. `65-80 detik` - Sistem digunakan
6. `80-90 detik` - Closing line dan brand

### Suggested On-Screen Copy

```text
Understand the operation.
Design what matters.
Build with precision.
Test before handover.
Stay after launch.
```

### Closing Frame

**Technology should feel ready before the business depends on it.**

Logo Bintang Computer Feira dan CTA kecil:

**Discuss your next system**

### Player Behavior

* Tidak autoplay.
* Video mulai hanya setelah tombol play ditekan.
* Sound mengikuti kontrol user dan tidak dipaksa aktif.
* Native controls tetap tersedia.
* `playsinline` wajib untuk mobile.
* Poster dimuat lebih dulu; file video tidak boleh menghambat initial page load.
* Saat video dimainkan, audio pada section `Process` harus pause.
* Saat panel keluar viewport, video pause otomatis.
* Setelah selesai, tampilkan replay dan CTA menuju `#contact`.
* Sediakan caption/subtitle WebVTT.

### Empty State

Jika video asli belum tersedia, tampilkan poster dan label:

**Project film is being prepared**

Jangan memakai stock video teknologi generik karena akan menurunkan kredibilitas portofolio.

---

## 6. Visual Language

### Background

Gunakan transisi visual dari dark `Process` menuju `Contact`:

* Dasar deep navy menuju warm cream.
* Glow light blue lembut di belakang video.
* Garis circuit gold hanya sebagai pengikat visual.
* Tidak memakai background image ramai di seluruh section.

### Portfolio Panel

* Warm cream glass
* Border gold dengan opacity rendah
* Shadow brown lembut
* Radius besar mengikuti sistem visual saat ini

### Video Panel

* Deep navy atau charcoal
* Poster dengan rasio `4:5` pada desktop agar terasa editorial
* Rasio `16:9` pada mobile agar tidak terlalu tinggi
* Control accent menggunakan gold, focus state menggunakan light blue

### Signature Detail

Tambahkan garis tipis yang bergerak dari nomor active case menuju label video `Field Notes`. Gerakan cukup sekali saat section masuk viewport. Pada `prefers-reduced-motion`, garis tampil tanpa animasi.

Hindari:

* Logo wall tanpa konteks
* Carousel yang bergerak sendiri
* Quote cards yang semuanya tampil sekaligus
* Efek 3D berlebihan
* Counter atau angka hasil yang tidak dapat diverifikasi

---

## 7. Interaction Model

Saat customer dipilih:

1. Active indicator berpindah.
2. Visual case berganti dengan crossfade singkat.
3. Scope, outcome, tags, dan testimonial ikut berubah.
4. Nomor proyek diperbarui melalui `aria-live="polite"`.
5. Fokus keyboard tidak dipindahkan secara paksa.

Navigasi:

* Customer selector menggunakan button, bukan link kosong.
* Arrow key dapat berpindah antar customer tab.
* Swipe didukung pada mobile.
* Tidak ada auto-rotation agar pengunjung sempat membaca.

Motion:

* Crossfade `220-320ms`.
* Tidak memakai parallax pada mobile.
* Semua informasi tetap tersedia tanpa JavaScript sebagai daftar statis.

---

## 8. Responsive & Accessibility Requirements

* Tidak ada fixed height pada card atau section.
* Touch target minimal `48px`.
* Kontras teks memenuhi WCAG AA.
* Tombol play memiliki label spesifik, contoh `Putar video proyek Office Infrastructure`.
* Gambar proyek memiliki alt text berdasarkan aktivitas, bukan nama file.
* Logo dekoratif memakai alt kosong; nama customer tetap tersedia sebagai teks.
* Subtitle video wajib tersedia.
* Player dapat dioperasikan dengan keyboard.
* Layout aman pada viewport `360`, `390`, `430`, `768`, `1024`, dan `1366px`.
* Tidak ada horizontal overflow selain customer selector yang memang dapat digeser.

---

## 9. Content Assets Required

Sebelum implementasi final, siapkan:

* 4 sampai 6 nama customer yang mendapat izin publikasi
* Logo customer dalam SVG, PNG, atau WebP transparan
* Minimal 1 foto landscape per proyek
* Jenis industri dan lokasi
* Challenge, scope, dan outcome setiap proyek
* Komentar asli customer
* Nama dan jabatan pemberi komentar atau format anonim yang disetujui
* Video MP4 Web-optimized
* Poster WebP
* Subtitle `.vtt`

Fallback awal yang masih layak:

* 3 customer
* 3 foto proyek
* 3 komentar
* 1 video kompilasi

---

## 10. Proposed Content Labels

Gunakan label berikut agar tone konsisten:

* `Selected Work`
* `Client Stories`
* `Project 01`
* `The Challenge`
* `What We Built`
* `The Outcome`
* `Client Note`
* `Field Notes`
* `Watch Project Film`
* `Discuss a Similar Project`

Bahasa Indonesia tetap dominan pada penjelasan. Label Inggris dipakai sebagai aksen editorial, sesuai karakter visual website saat ini.

---

## 11. CTA Bridge to Contact

Di bawah kedua panel, gunakan satu kalimat penghubung pendek:

**Punya kebutuhan yang mirip, atau justru belum tahu harus mulai dari mana?**

CTA:

* Primary: `Diskusikan Kebutuhan Anda`
* Secondary: `Lihat Semua Layanan`

Primary menuju `#contact`. Secondary menuju `#services`.

---

## 12. Implementation Acceptance Criteria

* Section berada tepat antara `Process` dan `Contact`.
* Portofolio/testimoni dan video tampil berdampingan pada desktop.
* Minimal tiga customer dapat dipilih.
* Testimoni selalu sesuai dengan active customer.
* Tidak ada konten customer fiktif yang tampil sebagai fakta.
* Video tidak autoplay dan tidak memutar suara tanpa izin.
* Audio `Process` berhenti saat video mulai.
* Semua interaksi dapat digunakan dengan keyboard dan touch.
* Fallback tanpa JavaScript tetap memperlihatkan seluruh case.
* Mobile tetap lega dan tidak mengalami horizontal page scroll.
* Build production dan responsive QA harus lulus setelah implementasi.
