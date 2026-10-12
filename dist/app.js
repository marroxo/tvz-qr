"use strict";
(() => {
  const form = document.getElementById("qr-form");
  const input = document.getElementById("jmbag");
  const result = document.getElementById("result");
  const canvas = document.getElementById("qr");
  const error = document.getElementById("error");
  const status = document.getElementById("status");
  const display = document.getElementById("display-jmbag");
  let downloadUrl = null;

  function discardCode() {
    if (downloadUrl) URL.revokeObjectURL(downloadUrl);
    downloadUrl = null;
    canvas.width = canvas.height = 0;
    result.hidden = true;
    display.textContent = "";
  }
  function clearAll() {
    discardCode();
    form.reset();
    input.value = "";
    input.removeAttribute("aria-invalid");
    error.hidden = true;
    error.textContent = status.textContent = "";
  }
  input.addEventListener("input", () => {
    discardCode();
    error.hidden = true;
    input.removeAttribute("aria-invalid");
    status.textContent = "";
  });
  form.addEventListener("submit", event => {
    event.preventDefault();
    discardCode();
    const jmbag = input.value.trim();
    if (!/^[0-9]{10}$/.test(jmbag)) {
      error.textContent = "JMBAG mora sadržavati točno 10 znamenki.";
      error.hidden = false;
      input.setAttribute("aria-invalid", "true");
      input.focus();
      return;
    }
    const qr = qrcode(0, "M");
    qr.addData("https://kinezioloska-kultura.tvz.hr/" + jmbag, "Byte");
    qr.make();
    const quiet = 4;
    const scale = 12;
    const modules = qr.getModuleCount();
    canvas.width = canvas.height = (modules + quiet * 2) * scale;
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = "#000000";
    for (let row = 0; row < modules; row++) {
      for (let col = 0; col < modules; col++) {
        if (qr.isDark(row, col)) ctx.fillRect((col + quiet) * scale, (row + quiet) * scale, scale, scale);
      }
    }
    error.hidden = true;
    input.removeAttribute("aria-invalid");
    display.textContent = jmbag;
    result.hidden = false;
    result.scrollIntoView({block: "start", behavior: "auto"});
    status.textContent = "QR kod je spreman za prikaz profesoru.";
  });
  document.getElementById("download").addEventListener("click", () => {
    if (result.hidden) return;
    canvas.toBlob(blob => {
      if (!blob || result.hidden) return;
      if (downloadUrl) URL.revokeObjectURL(downloadUrl);
      downloadUrl = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = "tvz-tzk-qr.png";
      document.body.appendChild(link);
      link.click();
      link.remove();
      status.textContent = "QR slika je preuzeta na tvoj uređaj.";
    }, "image/png");
  });
  document.getElementById("clear").addEventListener("click", () => {
    clearAll();
    input.focus();
  });
  window.addEventListener("pagehide", clearAll);
  window.addEventListener("pageshow", clearAll);
  clearAll();
  document.getElementById("generate").disabled = false;
})();
