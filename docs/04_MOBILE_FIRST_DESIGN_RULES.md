# Mobile First Design Rules

## Bintang Computer Feira Website

## Prioritas Utama

Website harus dirancang dengan pendekatan **mobile-first**.

Artinya:

* Desain dimulai dari layar HP terlebih dahulu.
* Desktop adalah pengembangan dari mobile, bukan sebaliknya.
* Tidak boleh membuat layout desktop dulu lalu “dipaksa mengecil” ke mobile.

## Target Viewport Utama

Prioritas testing:

* 360px — Android kecil
* 390px — iPhone normal
* 430px — Android besar
* 768px — tablet
* 1024px ke atas — desktop

## Aturan Wajib Mobile

### 1. Tidak boleh ada elemen saling tindih

Semua section wajib punya jarak aman.

Gunakan:

```css
section {
  padding: 64px 20px;
}
```

Untuk mobile:

```css
@media (max-width: 640px) {
  section {
    padding: 48px 18px;
  }
}
```

### 2. Hero tidak boleh terlalu tinggi

Hero mobile maksimal terasa nyaman dalam 1 layar.

```css
.hero {
  min-height: auto;
  padding-top: 96px;
  padding-bottom: 56px;
}
```

### 3. Text harus turun dulu, image setelahnya

Pada mobile:

* Headline
* Subheadline
* CTA
* Visual / image

Bukan image besar dulu yang menutup teks.

### 4. Grid harus berubah jadi 1 kolom

Desktop boleh 2–3 kolom.
Mobile wajib 1 kolom.

```css
.service-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

@media (max-width: 768px) {
  .service-grid {
    grid-template-columns: 1fr;
  }
}
```

### 5. Card tidak boleh fixed height

Hindari:

```css
height: 400px;
```

Gunakan:

```css
min-height: fit-content;
height: auto;
```

### 6. Dekor tidak boleh mengganggu konten

Semua dekor seperti circuit line, glow, orb, star, pattern harus:

```css
pointer-events: none;
z-index: 0;
```

Konten utama:

```css
.content {
  position: relative;
  z-index: 2;
}
```

### 7. Gambar harus responsive

```css
img {
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
```

### 8. Font mobile jangan terlalu besar

Headline mobile:

```css
font-size: clamp(2.2rem, 9vw, 4.5rem);
line-height: 1.05;
```

Body:

```css
font-size: 1rem;
line-height: 1.7;
```

## Prinsip Final

Mobile harus terasa:

* lega
* premium
* tidak sesak
* tidak saling dorong
* tidak ada layer menutup tombol
* CTA mudah ditekan
* konten mudah dibaca

Website ini harus terlihat seperti **IT consultant modern**, bukan brosur PDF yang dipaksa masuk HP.
