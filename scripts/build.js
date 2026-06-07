const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "..");
const dist = path.join(root, "dist");

const files = {
  html: path.join(root, "index.html"),
  css: [
    path.join(root, "css", "style.css"),
    path.join(root, "css", "components.css"),
    path.join(root, "css", "responsive.css"),
  ],
  js: path.join(root, "js", "app.js"),
  rootAssets: ["robots.txt", "sitemap.xml", "site.webmanifest"],
};

function ensureDir(dir) {
  fs.mkdirSync(dir, { recursive: true });
}

function removeDir(dir) {
  if (fs.existsSync(dir)) {
    fs.rmSync(dir, { recursive: true, force: true });
  }
}

function copyDir(source, target) {
  ensureDir(target);
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    const from = path.join(source, entry.name);
    const to = path.join(target, entry.name);
    if (entry.isDirectory()) {
      copyDir(from, to);
    } else {
      fs.copyFileSync(from, to);
    }
  }
}

function minifyCss(input) {
  return input
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/\s+/g, " ")
    .replace(/\s*([{}:;,>])\s*/g, "$1")
    .replace(/;}/g, "}")
    .trim();
}

function minifyJs(input) {
  return input
    .replace(/\/\*[\s\S]*?\*\//g, "")
    .replace(/(^|\s)\/\/.*$/gm, "")
    .replace(/\s+/g, " ")
    .replace(/\s*([{}()[\];,:])\s*/g, "$1")
    .trim();
}

function minifyHtml(input) {
  return input
    .replace(/<!--[\s\S]*?-->/g, "")
    .replace(/\s+/g, " ")
    .replace(/>\s+</g, "><")
    .trim();
}

removeDir(dist);
ensureDir(path.join(dist, "css"));
ensureDir(path.join(dist, "js"));
copyDir(path.join(root, "assets"), path.join(dist, "assets"));

files.rootAssets.forEach((file) => {
  const source = path.join(root, file);
  if (fs.existsSync(source)) {
    fs.copyFileSync(source, path.join(dist, file));
  }
});

const cssBundle = files.css.map((file) => fs.readFileSync(file, "utf8")).join("\n");
fs.writeFileSync(path.join(dist, "css", "main.min.css"), minifyCss(cssBundle));

const jsBundle = fs.readFileSync(files.js, "utf8");
fs.writeFileSync(path.join(dist, "js", "app.min.js"), minifyJs(jsBundle));

let html = fs.readFileSync(files.html, "utf8");
html = html
  .replace(/<link rel="stylesheet" href="\.\/css\/style\.css">\s*<link rel="stylesheet" href="\.\/css\/components\.css">\s*<link rel="stylesheet" href="\.\/css\/responsive\.css">/, '<link rel="stylesheet" href="./css/main.min.css">')
  .replace('<script src="./js/app.js" defer></script>', '<script src="./js/app.min.js" defer></script>');
fs.writeFileSync(path.join(dist, "index.html"), minifyHtml(html));

const report = {
  html: "dist/index.html",
  css: "dist/css/main.min.css",
  js: "dist/js/app.min.js",
  assets: "dist/assets",
};

console.log(JSON.stringify(report, null, 2));
