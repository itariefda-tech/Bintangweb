# AI-NEWSROOM_README.md

## 1. Nama Modul

**Feira AI Newsroom Builder**

Modul ini adalah bagian dari website `feira.my.id`, khususnya pada area **Tool Builder**, yang berfungsi sebagai sistem ruang redaksi virtual untuk membuat, mengelola, menulis, memeriksa, menyunting, dan menyiapkan artikel berita seputar teknologi dan IT.

Modul ini bukan sekadar fitur “AI tulis artikel otomatis”.

Modul ini dirancang sebagai **mini newsroom system** dengan alur kerja yang tertib, status yang jelas, agent penulis yang berbeda karakter, dan kontrol editorial oleh manusia.

---

## 2. Prinsip Utama

Feira AI Newsroom Builder dibangun dengan prinsip:

> **Gratis dulu, rapi dulu, stabil dulu, baru scalable.**

Pada tahap awal, sistem **tidak wajib memakai API AI berbayar**.

Fokus awal bukan mengejar otomatisasi penuh, tetapi memastikan:

1. alur produksi artikel jelas,
2. topik tidak menumpuk tanpa arah,
3. draft tidak bercampur-campur,
4. setiap artikel punya status,
5. setiap artikel punya sumber atau catatan keterbatasan,
6. setiap agent punya karakter dan batasan,
7. artikel tidak langsung publish otomatis,
8. manusia tetap menjadi editor final,
9. sistem bisa dikembangkan ke AI API atau local LLM di masa depan.

---

## 3. Latar Belakang

`feira.my.id` adalah website brand **Bintang Computer Feira**, sebuah konsultan IT dan penyedia solusi teknologi bisnis.

Pemilik proyek memiliki latar belakang:

* pengalaman di dunia IT,
* pengalaman majalah/redaksi,
* pengalaman desain media,
* pengalaman web dan konten,
* pengalaman komputer, jaringan, server, NAS, CCTV, aplikasi, dan konsultasi teknologi.

Karena itu, modul ini harus terasa seperti **ruang redaksi teknologi**, bukan sekadar generator artikel instan.

AI boleh membantu menulis, tetapi arah berpikir, kualitas, dan tanggung jawab editorial tetap dikendalikan oleh pemilik website.

---

## 4. Tujuan Modul

Tujuan utama modul ini adalah membuat sistem produksi konten teknologi dan IT yang:

1. membantu membangun otoritas brand Feira,
2. menghasilkan artikel teknologi yang rapi dan konsisten,
3. membantu edukasi calon klien,
4. menjadi mesin konten untuk SEO,
5. menjadi portofolio pemikiran IT Bintang Computer Feira,
6. membantu membuat berita, insight, opini, panduan, dan artikel edukasi,
7. menjadi pondasi menuju organisasi virtual berbasis AI.

---

## 5. Batasan Tahap Awal

Pada tahap awal, modul ini **tidak boleh bergantung pada platform berbayar**.

Artinya:

* tidak wajib OpenAI API,
* tidak wajib Gemini API,
* tidak wajib Claude API,
* tidak wajib automation platform berbayar,
* tidak wajib SaaS eksternal,
* tidak wajib CMS premium,
* tidak wajib publish otomatis.

Tahap awal harus bisa berjalan dengan salah satu mode berikut:

### 5.1 Manual Prompt Mode

Mode paling sederhana.

Sistem menyiapkan:

* prompt agent,
* form topik,
* struktur artikel,
* tempat menyimpan draft,
* status artikel,
* review manual.

Pengguna dapat menyalin prompt ke AI apa pun yang tersedia, lalu menempelkan hasilnya kembali ke Draft Studio.

Mode ini cocok untuk membuktikan workflow.

### 5.2 Local/Free LLM Adapter Mode

Mode lanjutan tanpa biaya API berbayar.

Sistem disiapkan agar kelak bisa terhubung ke LLM lokal atau model gratis/self-hosted.

Contoh konsep:

```text
Website Feira
→ Backend AI Newsroom
→ AI Adapter
→ Local/Free LLM
→ Draft Result
→ Review Manual
```

Catatan penting:

* pilihan model dapat berubah,
* jangan kunci sistem ke satu provider,
* sistem harus memakai adapter agar mudah diganti,
* lisensi model harus dicek sebelum dipakai untuk produksi komersial.

### 5.3 Future Paid API Mode

Mode ini **belum diaktifkan pada tahap awal**.

Sistem hanya disiapkan agar kelak bisa memakai API berbayar jika workflow sudah terbukti bagus.

---

## 6. Konsep Produk

Nama produk internal:

**Feira AI Newsroom Builder**

Nama publik yang bisa ditampilkan:

**Feira IT Newsroom**

Sub-brand:

**Feira IT News by Bintang Computer Feira**

Fungsi utama:

```text
Membuat ide artikel
→ mengelompokkan topik
→ memilih agent penulis
→ membuat draft
→ memeriksa klaim
→ menyunting gaya bahasa
→ menyiapkan SEO
→ masuk antrean publish
→ disetujui manusia
→ dipublikasikan
```

---

## 7. Struktur Organisasi Virtual

### 7.1 Owner Editorial

**Arief Dharma Agung**
Peran: Founder, Editor-in-Chief, dan pengambil keputusan final.

Tugas:

* menentukan arah topik,
* memilih kategori,
* menyetujui artikel,
* menolak artikel yang tidak layak,
* memberi sudut pandang pengalaman lapangan,
* menjaga reputasi brand Feira,
* memastikan artikel tidak asal klaim.

### 7.2 AI Agent Writers

Modul ini memiliki 5 agent virtual:

1. **Raka Kernel**
   Spesialis infrastructure, server, jaringan, cybersecurity dasar, NAS, VPN, Docker, CCTV.

2. **Naya Byte**
   Spesialis AI, software, tool builder, automation, API, SaaS, dan tren teknologi.

3. **Bima MarketTech**
   Spesialis bisnis IT, UMKM, digitalisasi usaha, pricing layanan IT, dan solusi teknologi bisnis.

4. **Salsa GadgetLab**
   Spesialis hardware, laptop, printer, router, CCTV, perangkat kantor, dan panduan pembelian.

5. **Faris Validata**
   Spesialis fact-check, critical analysis, anti-overclaim, verifikasi klaim, dan editorial risk.

Detail persona agent ditulis di dokumen terpisah:

```text
AI_NEWSROOM_AGENT_PROFILES.md
```

---

## 8. Masalah yang Harus Dicegah

Modul ini harus dirancang untuk mencegah kekacauan berikut:

### 8.1 Artikel Menumpuk Tanpa Arah

Setiap ide artikel wajib memiliki:

* kategori,
* target pembaca,
* agent penulis,
* status,
* prioritas,
* catatan sumber.

Tidak boleh ada artikel tanpa status.

### 8.2 Topik Campur Aduk

Kategori wajib dipakai.

Kategori awal:

```text
AI & Automation
Infrastructure & Server
Cybersecurity
Business IT
UMKM Digital
Hardware & Gadget
CCTV & Networking
Software & Web App
Opinion & Editorial
Buyer Guide
```

### 8.3 Draft Hilang atau Tidak Jelas Versinya

Setiap draft wajib memiliki versi.

Contoh:

```text
v1 - draft awal
v2 - revisi editor
v3 - revisi fact-check
v4 - siap publish
```

### 8.4 AI Mengarang Fakta

Setiap artikel yang memuat klaim faktual wajib memiliki sumber atau catatan keterbatasan.

Contoh klaim yang wajib dicek:

* angka statistik,
* harga,
* tanggal rilis,
* fitur produk terbaru,
* aturan hukum,
* kasus data breach,
* klaim vendor,
* perbandingan produk,
* pernyataan tokoh/perusahaan.

### 8.5 Publish Otomatis Tanpa Review

Pada tahap awal, sistem **dilarang publish otomatis**.

Semua artikel harus melalui approval manusia.

Status akhir sebelum publish:

```text
approved
```

---

## 9. Status Artikel

Setiap artikel wajib memiliki salah satu status berikut:

```text
idea
brief_ready
drafting
draft_ready
fact_check
revision_needed
editor_review
approved
scheduled
published
rejected
archived
```

Penjelasan:

### idea

Topik baru dicatat, belum dikembangkan.

### brief_ready

Topik sudah memiliki arahan, kategori, target pembaca, dan angle.

### drafting

Artikel sedang dibuat oleh agent.

### draft_ready

Draft awal sudah tersedia.

### fact_check

Draft sedang diperiksa klaimnya.

### revision_needed

Artikel perlu diperbaiki.

### editor_review

Artikel sudah masuk meja editor manusia.

### approved

Artikel disetujui untuk publish.

### scheduled

Artikel dijadwalkan tayang.

### published

Artikel sudah terbit.

### rejected

Artikel ditolak.

### archived

Artikel disimpan sebagai arsip dan tidak aktif.

---

## 10. Alur Kerja Editorial

Alur kerja wajib:

```text
1. Buat topik
2. Tentukan kategori
3. Tentukan target pembaca
4. Tentukan angle
5. Pilih agent penulis
6. Buat brief
7. Generate atau tulis draft
8. Simpan draft
9. Fact-check klaim
10. Revisi jika perlu
11. Review editor
12. Generate SEO package
13. Approve
14. Publish manual
```

Tidak boleh langsung:

```text
Topik → AI → Publish
```

Alur itu terlalu berbahaya.

Alur yang benar:

```text
Topik → Brief → Draft → Check → Edit → Approve → Publish
```

---

## 11. Mode Penulisan

Modul menyediakan beberapa mode artikel.

### 11.1 News Brief

Artikel berita singkat.

Cocok untuk:

* update teknologi,
* rilis produk,
* ringkasan berita,
* isu keamanan terkini.

Panjang ideal:

```text
400 - 700 kata
```

### 11.2 Explainer

Artikel edukatif.

Cocok untuk:

* menjelaskan istilah teknologi,
* menjelaskan konsep IT,
* artikel “apa itu”,
* panduan untuk orang awam.

Panjang ideal:

```text
800 - 1500 kata
```

### 11.3 Business Insight

Artikel teknologi dari sudut pandang bisnis.

Cocok untuk:

* UMKM,
* pemilik usaha,
* calon klien,
* digitalisasi bisnis,
* biaya IT,
* efisiensi operasional.

Panjang ideal:

```text
700 - 1200 kata
```

### 11.4 Opinion / Editorial

Artikel opini redaksi.

Cocok untuk:

* sudut pandang Feira,
* pengalaman lapangan,
* kritik terhadap tren teknologi,
* tulisan bergaya personal founder.

Panjang ideal:

```text
700 - 1400 kata
```

### 11.5 Buyer Guide

Artikel panduan membeli perangkat.

Cocok untuk:

* laptop,
* printer,
* router,
* CCTV,
* NAS,
* perangkat kantor,
* hardware second.

Panjang ideal:

```text
800 - 1500 kata
```

---

## 12. Struktur Halaman Tool Builder

Halaman utama:

```text
/tool-builder/ai-newsroom
```

Struktur UI:

```text
AI Newsroom Dashboard
├── KPI Cards
├── Topic Builder
├── Agent Selection
├── Article Queue
├── Draft Studio
├── Fact-Check Panel
├── SEO Package Panel
└── Publish Queue
```

---

## 13. Komponen UI

### 13.1 KPI Cards

Menampilkan:

* total ide artikel,
* draft aktif,
* artikel butuh revisi,
* artikel siap review,
* artikel approved,
* artikel published bulan ini.

### 13.2 Topic Builder

Form input:

```text
Judul/topik awal
Kategori
Target pembaca
Angle/sudut pandang
Mode artikel
Prioritas
Sumber URL
Catatan tambahan
Agent penulis
```

### 13.3 Agent Selection

Menampilkan 5 kartu agent.

Setiap kartu berisi:

* nama agent,
* spesialisasi,
* karakter,
* cocok untuk jenis artikel apa,
* tombol pilih agent,
* tombol lihat prompt.

### 13.4 Article Queue

Daftar artikel berdasarkan status.

Filter:

```text
All
Idea
Draft
Need Revision
Review
Approved
Published
Rejected
```

### 13.5 Draft Studio

Area utama untuk membaca dan mengedit artikel.

Isi:

```text
Headline
Subheadline
Summary
Content Markdown
CTA
Source Notes
Editor Notes
Version History
```

### 13.6 Fact-Check Panel

Panel untuk memeriksa klaim.

Isi:

```text
Claim
Source
Confidence Level
Risk Level
Fact-check Note
Status
```

### 13.7 SEO Package Panel

Output:

```text
SEO Title
Meta Description
Slug
Tags
Keywords
Social Caption
Excerpt
```

### 13.8 Publish Queue

Daftar artikel yang sudah approved.

Publish tetap manual pada tahap awal.

---

## 14. Struktur Data Minimum

Untuk tahap awal, data bisa disimpan dalam database sederhana.

Tabel minimum:

```text
ai_agents
news_topics
article_drafts
article_claims
article_reviews
published_articles
```

---

## 15. Desain Tabel Awal

### 15.1 ai_agents

```text
id
name
slug
role
specialty
personality
system_prompt
writing_style
is_active
created_at
updated_at
```

### 15.2 news_topics

```text
id
title
category
angle
target_reader
mode
priority
source_urls
notes
status
assigned_agent_id
created_at
updated_at
```

### 15.3 article_drafts

```text
id
topic_id
agent_id
headline
subheadline
summary
content_markdown
cta
seo_title
meta_description
slug
tags
version
status
created_at
updated_at
```

### 15.4 article_claims

```text
id
draft_id
claim_text
source_url
confidence_level
risk_level
fact_check_note
status
created_at
updated_at
```

### 15.5 article_reviews

```text
id
draft_id
reviewer_name
review_status
review_notes
approved_at
created_at
updated_at
```

### 15.6 published_articles

```text
id
draft_id
published_url
published_at
platform
status
created_at
updated_at
```

---

## 16. Output Artikel Wajib

Setiap draft artikel wajib memiliki struktur:

```text
Headline
Subheadline
Category
Target Reader
Summary
Article Markdown
Key Points
Claims
Source Notes
SEO Title
Meta Description
Slug
Tags
Social Caption
Editor Notes
```

Jika memakai AI, output ideal harus berbentuk JSON agar mudah disimpan.

Contoh format:

```json
{
  "headline": "",
  "subheadline": "",
  "category": "",
  "target_reader": "",
  "summary": "",
  "article_markdown": "",
  "key_points": [],
  "claims": [
    {
      "claim": "",
      "needs_source": true,
      "confidence": "low|medium|high",
      "risk": "low|medium|high"
    }
  ],
  "seo": {
    "title": "",
    "meta_description": "",
    "slug": "",
    "keywords": []
  },
  "social_caption": "",
  "editor_notes": ""
}
```

---

## 17. Aturan Editorial

### 17.1 Larangan

Agent dilarang:

1. membuat berita palsu,
2. mengarang kutipan,
3. membuat angka tanpa sumber,
4. membuat klaim terbaru tanpa validasi,
5. menyalin artikel orang lain,
6. membuat judul clickbait murahan,
7. membuat artikel terlalu promosi,
8. membuat artikel seolah pasti benar padahal masih prediksi,
9. publish otomatis,
10. menghapus draft lama tanpa arsip.

### 17.2 Kewajiban

Agent wajib:

1. membedakan fakta, opini, dan prediksi,
2. menandai klaim yang perlu sumber,
3. memberi catatan jika informasi belum kuat,
4. menulis dengan bahasa yang jelas,
5. mengikuti karakter agent,
6. menjaga gaya brand Feira,
7. memberi CTA yang relevan dan tidak memaksa,
8. menyimpan versi artikel,
9. mengikuti status workflow,
10. menunggu approval manusia.

---

## 18. Gaya Bahasa Brand

Gaya bahasa Feira AI Newsroom:

```text
Modern
Praktis
Ramah
Teknis secukupnya
Tidak lebay
Tidak gelap
Premium tapi membumi
Cocok untuk UMKM dan pemilik bisnis
```

Hindari gaya:

```text
Terlalu akademik
Terlalu robotik
Terlalu clickbait
Terlalu promosi
Terlalu panjang tanpa isi
Terlalu teknis untuk pembaca awam
```

---

## 19. Format Credit Artikel

Setiap artikel yang publish harus memiliki credit.

Contoh:

```text
Ditulis oleh: Raka Kernel — Feira AI Newsroom
Disunting oleh: Arief Dharma Agung
Dipublikasikan di: Feira IT News
```

Jika artikel dibantu AI, gunakan transparansi ringan:

```text
Artikel ini disusun dengan bantuan sistem Feira AI Newsroom dan melalui proses review editorial manusia.
```

---

## 20. CTA Artikel

Setiap artikel boleh memiliki CTA, tetapi tidak boleh memaksa.

Contoh CTA halus:

```text
Butuh konsultasi setup jaringan, NAS, CCTV, atau sistem IT untuk bisnis?
Bintang Computer Feira dapat membantu merancang solusi yang sesuai kebutuhan usaha Anda.
```

Contoh CTA yang harus dihindari:

```text
Segera beli sekarang sebelum bisnis Anda hancur!
```

Gaya seperti itu terlalu norak dan merusak trust.

---

## 21. Arsitektur Sederhana Tahap Awal

Arsitektur awal:

```text
Frontend feira.my.id
        ↓
AI Newsroom Page
        ↓
Backend Internal
        ↓
Database Draft
        ↓
Manual Prompt / Free AI Adapter
        ↓
Draft Studio
        ↓
Human Review
        ↓
Manual Publish
```

Prinsip:

* frontend menampilkan UI newsroom,
* backend mengatur data dan status,
* database menyimpan topik dan draft,
* AI engine bersifat opsional,
* publish tetap manual.

---

## 22. AI Engine Adapter

Sistem harus memakai konsep adapter.

Jangan tulis kode yang terlalu terikat pada satu provider AI.

Struktur konsep:

```text
ai_engine/
├── base_adapter
├── manual_prompt_adapter
├── local_llm_adapter
├── free_api_adapter
└── future_paid_api_adapter
```

Pada tahap awal yang wajib:

```text
manual_prompt_adapter
```

Adapter ini menghasilkan prompt siap pakai berdasarkan:

* topik,
* agent,
* mode artikel,
* target pembaca,
* kategori,
* sumber,
* catatan editor.

---

## 23. Manual Prompt Mode

Manual Prompt Mode adalah mode wajib untuk MVP.

Alurnya:

```text
1. User mengisi form topik
2. User memilih agent
3. Sistem membuat prompt lengkap
4. User menyalin prompt
5. User menjalankan prompt di AI yang tersedia
6. User menempel hasil ke Draft Studio
7. Sistem menyimpan draft
8. Artikel masuk status draft_ready
```

Keuntungan:

* tidak perlu API berbayar,
* tidak perlu billing,
* workflow bisa diuji,
* prompt agent bisa diperbaiki dulu,
* sistem tetap punya database dan status,
* risiko biaya nol.

---

## 24. Prompt Builder

Prompt Builder harus menghasilkan prompt lengkap.

Isi prompt:

```text
Nama agent
Karakter agent
Spesialisasi agent
Topik artikel
Target pembaca
Mode artikel
Kategori
Angle
Sumber
Aturan editorial
Format output
Larangan overclaim
Instruksi SEO
```

Prompt tidak boleh pendek dan liar.

Prompt harus seperti surat tugas redaksi.

---

## 25. Contoh Prompt Output

```text
Anda adalah Raka Kernel, agent penulis Feira AI Newsroom dengan spesialisasi infrastructure, server, jaringan, NAS, VPN, Docker, CCTV, dan cybersecurity dasar.

Tulis artikel dengan ketentuan:

Topik:
[TOPIK]

Kategori:
[KATEGORI]

Target pembaca:
[TARGET PEMBACA]

Mode artikel:
[MODE]

Sudut pandang:
[ANGLE]

Sumber:
[SUMBER URL / CATATAN SUMBER]

Aturan:
- Jangan membuat klaim tanpa sumber.
- Bedakan fakta, opini, dan prediksi.
- Jangan mengarang angka.
- Jangan mengarang kutipan.
- Jangan clickbait.
- Tulis dengan bahasa praktis, jelas, dan cocok untuk pembaca UMKM.
- Jika informasi kurang, beri catatan bahwa artikel perlu verifikasi tambahan.

Output wajib dalam format JSON:
{
  "headline": "",
  "subheadline": "",
  "category": "",
  "target_reader": "",
  "summary": "",
  "article_markdown": "",
  "key_points": [],
  "claims": [],
  "seo": {
    "title": "",
    "meta_description": "",
    "slug": "",
    "keywords": []
  },
  "social_caption": "",
  "editor_notes": ""
}
```

---

## 26. Anti-Content Pile-Up Rule

Agar artikel tidak menumpuk, sistem wajib punya batas kerja.

Aturan awal:

```text
Maksimal 10 topik aktif
Maksimal 5 draft aktif
Maksimal 3 artikel dalam editor_review
Maksimal 2 artikel scheduled
```

Jika batas tercapai, sistem harus menyarankan:

```text
Selesaikan/review artikel lama dulu sebelum membuat artikel baru.
```

Tujuan:

* menjaga fokus,
* mencegah gudang draft busuk,
* mencegah artikel setengah matang,
* menjaga kualitas editorial.

---

## 27. Weekly Editorial Rhythm

Agar konten teratur, gunakan ritme mingguan.

Contoh:

```text
Senin:
Pilih 3 topik utama

Selasa:
Buat brief dan draft

Rabu:
Fact-check dan revisi

Kamis:
Final edit dan SEO

Jumat:
Publish 1 artikel terbaik

Sabtu:
Review performa dan ide konten

Minggu:
Arsip, bersihkan queue, dan rencanakan minggu depan
```

Untuk tahap awal, target realistis:

```text
1 artikel bagus per minggu
```

Lebih baik 1 artikel matang daripada 10 artikel berisik.

---

## 28. Kategori Awal yang Direkomendasikan

Kategori awal jangan terlalu banyak.

Gunakan 8 kategori inti:

```text
AI & Automation
Infrastructure & Server
Cybersecurity
Business IT
Hardware & Gadget
CCTV & Networking
Software & Web App
Buyer Guide
```

Kategori tambahan bisa dibuat nanti jika konten sudah stabil.

---

## 29. Prioritas Topik

Setiap topik punya prioritas:

```text
low
medium
high
urgent
```

Definisi:

### low

Ide menarik, tapi tidak harus segera.

### medium

Cocok untuk konten mingguan.

### high

Relevan dengan layanan Feira atau kebutuhan calon klien.

### urgent

Berita penting, isu keamanan, atau tren yang sedang panas.

Catatan:

Status `urgent` tetap tidak boleh melewati fact-check.

---

## 30. Definition of Done

Satu artikel dianggap selesai jika memenuhi syarat:

```text
Topik jelas
Kategori jelas
Target pembaca jelas
Agent jelas
Draft tersimpan
Klaim penting dicek
Tidak ada overclaim
SEO title tersedia
Meta description tersedia
Slug tersedia
CTA tersedia
Editor manusia menyetujui
Status approved atau published
```

Jika salah satu belum ada, artikel belum selesai.

---

## 31. MVP Scope

MVP pertama hanya mencakup:

```text
1. Halaman AI Newsroom
2. 5 agent card
3. Topic Builder
4. Prompt Builder
5. Draft Studio manual
6. Article Queue
7. Status artikel
8. Simpan draft
9. Edit draft
10. Fact-check checklist manual
```

MVP pertama tidak mencakup:

```text
Auto publish
Auto scraping
API AI berbayar
Multi-user kompleks
Workflow SaaS
Payment
Newsletter otomatis
Komentar publik
Analytics detail
```

---

## 32. Phase Roadmap Ringkas

### Phase 1 — Static Newsroom UI

Target:

```text
Halaman AI Newsroom tampil rapi di feira.my.id.
```

Output:

```text
/tool-builder/ai-newsroom
Agent cards
Topic form
Article queue dummy
Draft studio dummy
```

### Phase 2 — Manual Prompt Builder

Target:

```text
Sistem bisa membuat prompt lengkap berdasarkan pilihan agent dan topik.
```

Output:

```text
Generated prompt
Copy prompt button
Paste result area
Save draft button
```

### Phase 3 — Draft Database

Target:

```text
Topik dan draft tersimpan rapi.
```

Output:

```text
CRUD topic
CRUD draft
Status workflow
Version draft
```

### Phase 4 — Fact-Check Checklist

Target:

```text
Draft tidak langsung dianggap benar.
```

Output:

```text
Claim list
Risk level
Need source flag
Fact-check note
Revision status
```

### Phase 5 — SEO Package

Target:

```text
Artikel siap dipublikasikan secara manual.
```

Output:

```text
SEO title
Meta description
Slug
Tags
Excerpt
Social caption
```

### Phase 6 — Free/Local AI Adapter

Target:

```text
Sistem mulai bisa mencoba integrasi AI tanpa platform berbayar.
```

Output:

```text
AI adapter layer
Local/free model connector
Fallback ke manual prompt mode
```

### Phase 7 — Future Paid API Ready

Target:

```text
Jika kelak dibutuhkan, API berbayar bisa dipasang tanpa merombak sistem.
```

Output:

```text
Provider abstraction
Config-based model selection
Usage logging
Cost guard
```

---

## 33. File Dokumen Lanjutan

Setelah README ini, dokumen berikutnya yang harus dibuat:

```text
AI_NEWSROOM_AGENT_PROFILES.md
AI_NEWSROOM_EDITORIAL_RULES.md
AI_NEWSROOM_UI_UX_GUIDE.md
AI_NEWSROOM_DATABASE_DESIGN.md
AI_NEWSROOM_API_CONTRACTS.md
AI_NEWSROOM_ROADMAP.md
```

Urutan pengerjaan:

```text
1. AI_NEWSROOM_README.md
2. AI_NEWSROOM_AGENT_PROFILES.md
3. AI_NEWSROOM_EDITORIAL_RULES.md
4. AI_NEWSROOM_UI_UX_GUIDE.md
5. AI_NEWSROOM_DATABASE_DESIGN.md
6. AI_NEWSROOM_API_CONTRACTS.md
7. AI_NEWSROOM_ROADMAP.md
```

---

## 34. Catatan Implementasi untuk Agent Coding

Agent coding wajib membaca README ini sebelum implementasi.

Aturan implementasi:

1. jangan langsung membuat API berbayar,
2. jangan langsung membuat auto publish,
3. jangan membuat fitur terlalu luas,
4. jangan menghapus konsep manual prompt mode,
5. jangan membuat agent tanpa prompt profile,
6. jangan membuat artikel tanpa status,
7. jangan membuat draft tanpa versioning,
8. jangan mencampur artikel published dengan draft,
9. jangan melewati approval manusia,
10. jangan membuat UI yang membingungkan.

Implementasi harus bertahap.

Jika ada fitur besar yang belum waktunya, masukkan ke roadmap, bukan dipaksakan ke MVP.

---

## 35. Ringkasan Final

Feira AI Newsroom Builder adalah sistem ruang redaksi virtual di `feira.my.id` untuk membuat konten teknologi dan IT secara terarah.

Tahap awal harus berjalan tanpa platform berbayar.

Fondasi utama:

```text
Manual Prompt Mode
5 AI Agent Persona
Topic Builder
Article Queue
Draft Studio
Fact-Check Checklist
SEO Package
Human Approval
Manual Publish
```

Tujuan utama bukan membuat artikel sebanyak-banyaknya.

Tujuan utama adalah membuat sistem yang:

```text
rapi
aman
terukur
tidak liar
tidak boros
tidak overclaim
dan bisa berkembang
```

Prinsip akhir:

> Jangan membangun mesin konten yang hanya ramai. Bangun ruang redaksi yang punya arah, martabat, dan manfaat bisnis untuk Feira.