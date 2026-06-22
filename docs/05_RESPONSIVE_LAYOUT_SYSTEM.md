# Layout Philosophy

Gunakan sistem layout yang aman, fleksibel, dan tidak mudah pecah.

Prioritas:

1. Mobile view rapi
2. Tablet tetap nyaman
3. Desktop terlihat premium dan luas

## Container System

Gunakan container utama:

```css
.container {
  width: min(100% - 40px, 1180px);
  margin-inline: auto;
}
```

Mobile:

```css
@media (max-width: 640px) {
  .container {
    width: min(100% - 32px, 100%);
  }
}
```

## Section Pattern

Setiap section minimal punya struktur:

```html
<section class="section">
  <div class="container">
    <div class="section-header"></div>
    <div class="section-content"></div>
  </div>
</section>
```

Jangan membuat elemen langsung menempel tanpa container.

## Hero Layout

Desktop:

```css
.hero-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  align-items: center;
  gap: 56px;
}
```

Mobile:

```css
@media (max-width: 768px) {
  .hero-grid {
    grid-template-columns: 1fr;
    gap: 36px;
    text-align: center;
  }
}
```

## Services Layout

Desktop:

```css
.services-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}
```

Tablet:

```css
@media (max-width: 1024px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

Mobile:

```css
@media (max-width: 640px) {
  .services-grid {
    grid-template-columns: 1fr;
  }
}
```

## Card Design

Card style:

```css
.service-card {
  position: relative;
  border-radius: 28px;
  padding: 28px;
  background: rgba(255, 249, 239, 0.82);
  border: 1px solid rgba(201, 154, 58, 0.24);
  box-shadow: 0 24px 60px rgba(75, 46, 22, 0.08);
  overflow: hidden;
}
```

Mobile card:

```css
@media (max-width: 640px) {
  .service-card {
    padding: 24px;
    border-radius: 24px;
  }
}
```

## Z-Index Rules

Gunakan aturan ini:

```css
.background-decor {
  z-index: 0;
}

.section-content {
  z-index: 2;
}

.navbar {
  z-index: 50;
}

.mobile-menu {
  z-index: 80;
}

.floating-whatsapp {
  z-index: 90;
}
```

Jangan asal pakai:

```css
z-index: 9999;
```

Itu tanda layout mulai barbar.

## Mobile Navigation

Mobile navbar harus:

* sticky / fixed di atas
* logo kiri
* tombol menu kanan
* menu muncul full-screen atau drawer
* tidak menutup hero text secara permanen

## CTA Button

Minimal tinggi tombol:

```css
.button {
  min-height: 48px;
  padding: 14px 22px;
  border-radius: 999px;
}
```

Mobile button:

```css
@media (max-width: 640px) {
  .button-group {
    flex-direction: column;
    width: 100%;
  }

  .button {
    width: 100%;
  }
}
```

## Testing Checklist

Sebelum selesai, wajib cek:

* [ ] Tidak ada horizontal scroll
* [ ] Tidak ada text ketutup gambar
* [ ] Tidak ada tombol ketutup dekor
* [ ] Navbar mobile normal
* [ ] Semua card turun menjadi 1 kolom
* [ ] Hero mobile tetap elegan
* [ ] Gambar tidak keluar layar
* [ ] CTA mudah ditekan
* [ ] Spacing antar section lega
* [ ] Desktop tetap terlihat premium
