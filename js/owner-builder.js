const backgroundSections = [
  ["header", "Header navigation"],
  ["hero", "Hero"],
  ["about", "About Us"],
  ["solutions", "Solutions"],
  ["process", "Process"],
  ["contact", "Contact"],
  ["footer", "Footer"],
];

const toast = document.querySelector("[data-owner-toast]");
const saveState = document.querySelector("[data-save-state]");
const audioToggle = document.querySelector("[data-audio-toggle]");
const audioLabel = document.querySelector("[data-audio-label]");
const backgroundEditor = document.querySelector("[data-background-editor]");
const clientList = document.querySelector("[data-client-list]");
let settings;
let catalog = { products: [], categories: [] };
let members = [];
let news = { articles: [], categories: [] };
let toastTimer;

function showToast(message) {
  window.clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add("is-visible");
  toastTimer = window.setTimeout(() => toast.classList.remove("is-visible"), 3600);
}

async function request(url, options = {}) {
  const response = await fetch(url, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(payload.error || "Request gagal.");
    error.errors = payload.errors || {};
    throw error;
  }
  return payload;
}

const escapeHtml = (value = "") =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

function fileAsDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error("File tidak dapat dibaca."));
    reader.readAsDataURL(file);
  });
}

async function uploadFile(file, kind) {
  if (!file) throw new Error("Pilih file terlebih dahulu.");
  saveState.textContent = `Mengupload ${file.name}...`;
  const data = await fileAsDataUrl(file);
  const payload = await request("/api/owner/upload", {
    method: "POST",
    body: JSON.stringify({ kind, filename: file.name, data }),
  });
  saveState.textContent = "Upload selesai. Simpan perubahan untuk menerapkan.";
  return payload.url;
}

function renderBackgrounds() {
  backgroundEditor.innerHTML = "";
  backgroundSections.forEach(([key, label]) => {
    const item = document.createElement("article");
    item.className = "background-item";
    item.dataset.backgroundItem = key;
    item.innerHTML = `
      <span class="background-preview" data-background-preview></span>
      <div class="background-copy">
        <strong>${label}</strong>
        <small data-background-current>Background bawaan</small>
        <div class="background-actions">
          <label class="owner-file">
            <input type="file" accept="image/jpeg,image/png,image/webp,image/gif" data-background-file>
            <span>Pilih gambar</span>
          </label>
          <button class="owner-button owner-button-quiet" type="button" data-background-upload>Upload</button>
          <button class="owner-button owner-button-quiet" type="button" data-background-reset>Reset</button>
        </div>
      </div>
    `;
    backgroundEditor.append(item);

    const preview = item.querySelector("[data-background-preview]");
    const current = item.querySelector("[data-background-current]");
    const updatePreview = () => {
      const url = settings.backgrounds[key];
      preview.style.backgroundImage = url ? `url("${url}")` : "";
      current.textContent = url || "Background bawaan";
    };

    item.querySelector("[data-background-upload]").addEventListener("click", async () => {
      try {
        const file = item.querySelector("[data-background-file]").files[0];
        settings.backgrounds[key] = await uploadFile(file, "background");
        updatePreview();
        await saveSettings();
        showToast(`${label} berhasil diperbarui.`);
      } catch (error) {
        showToast(error.message);
      }
    });

    item.querySelector("[data-background-reset]").addEventListener("click", async () => {
      settings.backgrounds[key] = "";
      updatePreview();
      await saveSettings();
      showToast(`${label} kembali ke background bawaan.`);
    });

    updatePreview();
  });
}

function populateForm() {
  document.querySelectorAll("[data-testimonial-form]").forEach((form) => {
    const entry = settings.testimonials[form.dataset.testimonialForm];
    form.querySelectorAll("[data-field]").forEach((field) => {
      field.value = entry[field.dataset.field] || "";
    });
  });

  audioToggle.checked = settings.processAudioAutoplay;
  audioLabel.textContent = audioToggle.checked ? "Aktif" : "Nonaktif";
  clientList.value = Array.isArray(settings.clients) ? settings.clients.join("\n") : "";
  document.querySelector("[data-video-current]").textContent =
    settings.workVideo || "Belum ada video aktif.";
  renderBackgrounds();
}

function collectForm() {
  document.querySelectorAll("[data-testimonial-form]").forEach((form) => {
    const entry = settings.testimonials[form.dataset.testimonialForm];
    form.querySelectorAll("[data-field]").forEach((field) => {
      entry[field.dataset.field] = field.value.trim();
    });
  });
  settings.clients = clientList.value
    .split(/\r?\n/)
    .map((client) => client.trim())
    .filter(Boolean);
  settings.processAudioAutoplay = audioToggle.checked;
}

function resetProductForm() {
  const form = document.querySelector("[data-product-form]");
  form.reset();
  form.elements.id.value = "";
  form.elements.status.value = "active";
  form.querySelector('button[type="submit"]').textContent = "Simpan produk";
}

function populateProductForm(product) {
  const form = document.querySelector("[data-product-form]");
  form.elements.id.value = product.id;
  form.elements.name.value = product.name;
  form.elements.slug.value = product.slug;
  form.elements.category.value = product.category.slug;
  form.elements.badge.value = product.badge || "";
  form.elements.shortDescription.value = product.shortDescription;
  form.elements.description.value = product.description;
  form.elements.price.value = product.price;
  form.elements.stock.value = product.stock;
  form.elements.status.value = product.status;
  form.elements.featured.checked = product.featured;
  form.elements.thumbnail.value = product.image;
  form.elements.images.value = (product.images || []).join("\n");
  form.querySelector('button[type="submit"]').textContent = "Perbarui produk";
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderProducts() {
  const list = document.querySelector("[data-product-list]");
  if (!catalog.products.length) {
    list.innerHTML = '<p class="owner-note">Belum ada produk.</p>';
    return;
  }
  list.innerHTML = catalog.products.map((product) => `
    <article class="owner-record">
      <div class="owner-record-heading">
        <div>
          <strong>${escapeHtml(product.name)}</strong>
          <small>${escapeHtml(product.category.name)} · Rp ${Number(product.price).toLocaleString("id-ID")} · stok ${product.stock}</small>
        </div>
        <span class="owner-record-status" data-status="${product.status}">${product.status}</span>
      </div>
      <p class="owner-record-meta">${escapeHtml(product.shortDescription)}</p>
      <div class="owner-record-actions">
        <button class="owner-button owner-button-quiet" type="button" data-product-edit="${product.id}">Edit</button>
        ${product.status === "archived" ? "" : `<button class="owner-button owner-button-quiet" type="button" data-product-archive="${product.id}">Arsipkan</button>`}
        <a class="owner-button owner-button-quiet" href="/marketplace/product/${encodeURIComponent(product.slug)}" target="_blank" rel="noreferrer">Lihat</a>
      </div>
    </article>
  `).join("");
}

async function loadCatalog() {
  catalog = await request("/api/owner/catalog");
  const select = document.querySelector("[data-product-category]");
  select.innerHTML = catalog.categories.map((category) =>
    `<option value="${category.slug}">${escapeHtml(category.name)}</option>`
  ).join("");
  renderProducts();
}

function renderMembers() {
  const list = document.querySelector("[data-member-list]");
  if (!members.length) {
    list.innerHTML = '<p class="owner-note">Belum ada member terdaftar.</p>';
    return;
  }
  list.innerHTML = members.map((member) => `
    <article class="owner-record">
      <div class="owner-record-heading">
        <div>
          <strong>${escapeHtml(member.name)}</strong>
          <small>${escapeHtml(member.email)} · ${escapeHtml(member.role)}</small>
        </div>
        <span class="owner-record-status" data-status="${member.status}">${member.status === "inactive" ? "menunggu approval" : member.status}</span>
      </div>
      <div class="owner-record-actions">
        ${member.status !== "active" ? `<button class="owner-button" type="button" data-member-status="${member.id}" data-status="active">Approve</button>` : ""}
        ${member.role !== "super_admin" && member.status !== "inactive" ? `<button class="owner-button owner-button-quiet" type="button" data-member-status="${member.id}" data-status="inactive">Nonaktifkan</button>` : ""}
        ${member.role !== "super_admin" && member.status !== "suspended" ? `<button class="owner-button owner-button-quiet" type="button" data-member-status="${member.id}" data-status="suspended">Suspend</button>` : ""}
      </div>
    </article>
  `).join("");
}

async function loadMembers() {
  const payload = await request("/api/owner/members");
  members = payload.members || [];
  renderMembers();
}

function resetNewsCategoryForm() {
  const form = document.querySelector("[data-news-category-form]");
  form.reset();
  form.elements.id.value = "";
  form.elements.status.value = "active";
  form.querySelector('button[type="submit"]').textContent = "Simpan kategori";
}

function resetNewsArticleForm() {
  const form = document.querySelector("[data-news-article-form]");
  form.reset();
  form.elements.id.value = "";
  form.elements.status.value = "draft";
  form.elements.readingTime.value = "3 min read";
  form.elements.trendingScore.value = "0";
  form.querySelector('button[type="submit"]').textContent = "Simpan artikel";
}

function populateNewsCategoryForm(category) {
  const form = document.querySelector("[data-news-category-form]");
  form.elements.id.value = category.id;
  form.elements.name.value = category.name;
  form.elements.slug.value = category.slug;
  form.elements.status.value = category.status;
  form.elements.description.value = category.description || "";
  form.querySelector('button[type="submit"]').textContent = "Perbarui kategori";
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

function populateNewsArticleForm(article) {
  const form = document.querySelector("[data-news-article-form]");
  form.elements.id.value = article.id;
  form.elements.title.value = article.title;
  form.elements.slug.value = article.slug;
  form.elements.category.value = article.category.slug;
  form.elements.readingTime.value = article.readingTime;
  form.elements.status.value = article.status;
  form.elements.trendingScore.value = article.trendingScore;
  form.elements.featured.checked = article.featured;
  form.elements.excerpt.value = article.excerpt;
  form.elements.body.value = article.body;
  form.elements.image.value = article.image;
  form.querySelector('button[type="submit"]').textContent = "Perbarui artikel";
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderNewsCategories() {
  const list = document.querySelector("[data-news-category-list]");
  list.innerHTML = news.categories.length ? news.categories.map((category) => `
    <article class="owner-record">
      <div class="owner-record-heading">
        <div>
          <strong>${escapeHtml(category.name)}</strong>
          <small>${escapeHtml(category.slug)} · ${category.articleCount} artikel</small>
        </div>
        <span class="owner-record-status" data-status="${category.status}">${category.status}</span>
      </div>
      <p class="owner-record-meta">${escapeHtml(category.description || "")}</p>
      <div class="owner-record-actions">
        <button class="owner-button owner-button-quiet" type="button" data-news-category-edit="${category.id}">Edit</button>
      </div>
    </article>
  `).join("") : '<p class="owner-note">Belum ada kategori news.</p>';
}

function renderNewsArticles() {
  const list = document.querySelector("[data-news-article-list]");
  list.innerHTML = news.articles.length ? news.articles.map((article) => `
    <article class="owner-record owner-news-record">
      <img src="${escapeHtml(article.image)}" alt="" loading="lazy">
      <div>
        <div class="owner-record-heading">
          <div>
            <strong>${escapeHtml(article.title)}</strong>
            <small>${escapeHtml(article.category.name)} · ${escapeHtml(article.readingTime)} · trending ${article.trendingScore}</small>
          </div>
          <span class="owner-record-status" data-status="${article.status}">${article.status}</span>
        </div>
        <p class="owner-record-meta">${escapeHtml(article.excerpt)}</p>
        <div class="owner-record-actions">
          <button class="owner-button owner-button-quiet" type="button" data-news-article-edit="${article.id}">Edit</button>
          ${article.status === "archived" ? "" : `<button class="owner-button owner-button-quiet" type="button" data-news-article-archive="${article.id}">Arsipkan</button>`}
          ${article.status === "published" ? `<a class="owner-button owner-button-quiet" href="/news/${encodeURIComponent(article.slug)}" target="_blank" rel="noreferrer">Lihat</a>` : ""}
        </div>
      </div>
    </article>
  `).join("") : '<p class="owner-note">Belum ada artikel news.</p>';
}

async function loadNews() {
  news = await request("/api/owner/news");
  const select = document.querySelector("[data-news-article-category]");
  select.innerHTML = news.categories.map((category) =>
    `<option value="${category.slug}">${escapeHtml(category.name)}${category.status === "inactive" ? " (inactive)" : ""}</option>`
  ).join("");
  renderNewsCategories();
  renderNewsArticles();
}

async function saveSettings() {
  collectForm();
  saveState.textContent = "Menyimpan perubahan...";
  const payload = await request("/api/owner/settings", {
    method: "POST",
    body: JSON.stringify(settings),
  });
  settings = payload.settings;
  saveState.textContent = "Semua perubahan tersimpan di server.";
}

async function boot() {
  const session = await request("/api/owner/session");
  if (!session.authenticated) {
    window.location.replace("/");
    return;
  }
  settings = await request("/api/public-settings");
  populateForm();
  await Promise.all([loadCatalog(), loadMembers(), loadNews()]);
}

document.querySelectorAll("[data-theme]").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll("[data-theme]").forEach((item) => {
      item.classList.toggle("is-active", item === button);
    });
    document.body.dataset.previewTheme = button.dataset.theme;
    showToast("Preview tema aktif. Mode ini tidak mengubah website publik.");
  });
});

audioToggle.addEventListener("change", () => {
  audioLabel.textContent = audioToggle.checked ? "Aktif" : "Nonaktif";
});

document.querySelector("[data-save-settings]").addEventListener("click", async () => {
  try {
    await saveSettings();
    showToast("Daftar client, testimoni, dan audio berhasil diperbarui.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-video-upload]").addEventListener("click", async () => {
  try {
    const file = document.querySelector("[data-video-file]").files[0];
    settings.workVideo = await uploadFile(file, "video");
    document.querySelector("[data-video-current]").textContent = settings.workVideo;
    await saveSettings();
    showToast("Video Work berhasil diaktifkan.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-owner-logout]").addEventListener("click", async () => {
  await request("/api/owner/logout", { method: "POST", body: "{}" });
  window.location.replace("/");
});

document.querySelector("[data-product-reset]").addEventListener("click", resetProductForm);

document.querySelector("[data-product-image-upload]").addEventListener("click", async () => {
  const form = document.querySelector("[data-product-form]");
  const file = document.querySelector("[data-product-image-file]").files[0];
  try {
    const url = await uploadFile(file, "product");
    form.elements.thumbnail.value = url;
    const images = form.elements.images.value
      .split(/\r?\n/)
      .map((item) => item.trim())
      .filter(Boolean);
    if (!images.includes(url)) images.unshift(url);
    form.elements.images.value = images.join("\n");
    showToast("Gambar produk berhasil diupload.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-product-form]").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const values = Object.fromEntries(new FormData(form));
  const productId = values.id;
  const payload = {
    ...values,
    price: Number(values.price),
    stock: Number(values.stock),
    featured: form.elements.featured.checked,
    images: values.images.split(/\r?\n/).map((item) => item.trim()).filter(Boolean),
  };
  delete payload.id;
  try {
    saveState.textContent = "Menyimpan produk...";
    await request(productId ? `/api/owner/products/${productId}` : "/api/owner/products", {
      method: productId ? "PUT" : "POST",
      body: JSON.stringify(payload),
    });
    await loadCatalog();
    resetProductForm();
    saveState.textContent = "Produk tersimpan di katalog.";
    showToast(productId ? "Produk berhasil diperbarui." : "Produk berhasil ditambahkan.");
  } catch (error) {
    saveState.textContent = "Produk belum tersimpan.";
    showToast(error.message);
  }
});

document.querySelector("[data-product-list]").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-product-edit]");
  const archive = event.target.closest("[data-product-archive]");
  if (edit) {
    const product = catalog.products.find((item) => item.id === edit.dataset.productEdit);
    if (product) populateProductForm(product);
    return;
  }
  if (!archive) return;
  try {
    await request(`/api/owner/products/${archive.dataset.productArchive}`, {
      method: "DELETE",
    });
    await loadCatalog();
    showToast("Produk dipindahkan ke arsip.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-member-list]").addEventListener("click", async (event) => {
  const button = event.target.closest("[data-member-status]");
  if (!button) return;
  button.disabled = true;
  try {
    await request(`/api/owner/members/${button.dataset.memberStatus}/status`, {
      method: "PUT",
      body: JSON.stringify({ status: button.dataset.status }),
    });
    await loadMembers();
    showToast(button.dataset.status === "active" ? "Member berhasil disetujui." : "Status member diperbarui.");
  } catch (error) {
    button.disabled = false;
    showToast(error.message);
  }
});

document.querySelector("[data-news-category-reset]").addEventListener("click", resetNewsCategoryForm);
document.querySelector("[data-news-article-reset]").addEventListener("click", resetNewsArticleForm);

document.querySelector("[data-news-image-upload]").addEventListener("click", async () => {
  const form = document.querySelector("[data-news-article-form]");
  const file = document.querySelector("[data-news-image-file]").files[0];
  try {
    form.elements.image.value = await uploadFile(file, "news");
    showToast("Cover artikel berhasil diupload.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-news-category-form]").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const values = Object.fromEntries(new FormData(form));
  const categoryId = values.id;
  delete values.id;
  try {
    await request(
      categoryId ? `/api/owner/news/categories/${categoryId}` : "/api/owner/news/categories",
      {
        method: categoryId ? "PUT" : "POST",
        body: JSON.stringify(values),
      },
    );
    await loadNews();
    resetNewsCategoryForm();
    showToast(categoryId ? "Kategori news diperbarui." : "Kategori news ditambahkan.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-news-article-form]").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  if (!form.reportValidity()) return;
  const values = Object.fromEntries(new FormData(form));
  const articleId = values.id;
  const payload = {
    ...values,
    featured: form.elements.featured.checked,
    trendingScore: Number(values.trendingScore),
  };
  delete payload.id;
  try {
    await request(
      articleId ? `/api/owner/news/articles/${articleId}` : "/api/owner/news/articles",
      {
        method: articleId ? "PUT" : "POST",
        body: JSON.stringify(payload),
      },
    );
    await loadNews();
    resetNewsArticleForm();
    showToast(articleId ? "Artikel berhasil diperbarui." : "Artikel berhasil ditambahkan.");
  } catch (error) {
    showToast(error.message);
  }
});

document.querySelector("[data-news-category-list]").addEventListener("click", (event) => {
  const button = event.target.closest("[data-news-category-edit]");
  if (!button) return;
  const category = news.categories.find((item) => item.id === button.dataset.newsCategoryEdit);
  if (category) populateNewsCategoryForm(category);
});

document.querySelector("[data-news-article-list]").addEventListener("click", async (event) => {
  const edit = event.target.closest("[data-news-article-edit]");
  const archive = event.target.closest("[data-news-article-archive]");
  if (edit) {
    const article = news.articles.find((item) => item.id === edit.dataset.newsArticleEdit);
    if (article) populateNewsArticleForm(article);
    return;
  }
  if (!archive) return;
  const article = news.articles.find((item) => item.id === archive.dataset.newsArticleArchive);
  if (!article || !window.confirm(`Arsipkan artikel "${article.title}"?`)) return;
  try {
    await request(`/api/owner/news/articles/${article.id}`, { method: "DELETE" });
    await loadNews();
    showToast("Artikel dipindahkan ke arsip.");
  } catch (error) {
    showToast(error.message);
  }
});

boot().catch((error) => {
  showToast(error.message);
  window.setTimeout(() => window.location.replace("/"), 1600);
});
