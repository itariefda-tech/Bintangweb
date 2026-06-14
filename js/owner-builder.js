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
  if (!response.ok) throw new Error(payload.error || "Request gagal.");
  return payload;
}

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

boot().catch((error) => {
  showToast(error.message);
  window.setTimeout(() => window.location.replace("/"), 1600);
});
