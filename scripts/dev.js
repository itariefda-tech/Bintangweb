const http = require("http");
const { spawn } = require("child_process");

const port = process.env.PORT || "8000";
const url = `http://localhost:${port}`;
const server = spawn("python", ["app.py"], {
  env: process.env,
  stdio: "inherit",
});

let browserOpened = false;
let healthCheck;

function openEdge() {
  if (browserOpened || server.exitCode !== null) {
    return;
  }

  browserOpened = true;
  clearInterval(healthCheck);

  const edge = spawn(
    "cmd",
    ["/c", "start", "", `microsoft-edge:${url}`],
    { detached: true, stdio: "ignore" },
  );
  edge.unref();
}

function checkServer() {
  const request = http.get(url, (response) => {
    response.resume();
    openEdge();
  });

  request.setTimeout(500, () => request.destroy());
  request.on("error", () => {});
}

healthCheck = setInterval(checkServer, 250);
checkServer();

server.on("error", (error) => {
  clearInterval(healthCheck);
  console.error(`Gagal menjalankan development server: ${error.message}`);
  process.exitCode = 1;
});

server.on("exit", (code, signal) => {
  clearInterval(healthCheck);
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exitCode = code ?? 1;
});

function stopServer(signal) {
  clearInterval(healthCheck);
  if (server.exitCode === null) {
    server.kill(signal);
  }
}

process.on("SIGINT", () => stopServer("SIGINT"));
process.on("SIGTERM", () => stopServer("SIGTERM"));
