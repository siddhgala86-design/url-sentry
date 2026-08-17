const form = document.getElementById("scan-form");
const input = document.getElementById("url-input");
const btn = document.getElementById("scan-btn");
const radar = document.getElementById("radar");
const verdictBox = document.getElementById("verdict");
const badge = document.getElementById("verdict-badge");
const icon = document.getElementById("verdict-icon");
const text = document.getElementById("verdict-text");
const recommendation = document.getElementById("verdict-recommendation");
const riskFill = document.getElementById("risk-fill");
const riskScoreText = document.getElementById("risk-score-text");
const checklist = document.getElementById("checklist");

function playBuzzer(kind) {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    if (kind === "SAFE") {
      osc.type = "sine"; osc.frequency.setValueAtTime(880, now);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc.start(now); osc.stop(now + 0.35);
    } else {
      osc.type = "square"; gain.gain.setValueAtTime(0.12, now);
      [0, 0.18, 0.36].forEach(t => osc.frequency.setValueAtTime(220, now + t));
      osc.start(now); osc.stop(now + 0.55);
    }
  } catch (e) {}
}

function verdictMeta(v) {
  if (v === "SAFE") return { cls: "safe", icon: "✔", label: "LINK IS SAFE" };
  if (v === "SUSPICIOUS") return { cls: "suspicious", icon: "⚠", label: "SUSPICIOUS LINK" };
  return { cls: "dangerous", icon: "✕", label: "INVALID LINK / SPAM ALERT" };
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = input.value.trim();
  if (!url) return;

  verdictBox.hidden = true;
  radar.hidden = false;
  btn.disabled = true;
  const start = Date.now();

  let report;
  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    report = await res.json();
    if (!res.ok) throw new Error(report.error || "Scan failed");
  } catch (err) {
    radar.hidden = true;
    btn.disabled = false;
    alert("Could not reach the backend: " + err.message);
    return;
  }

  const wait = Math.max(0, 900 - (Date.now() - start));
  setTimeout(() => {
    radar.hidden = true;
    btn.disabled = false;
    renderReport(report);
  }, wait);
});

function renderReport(report) {
  const meta = verdictMeta(report.verdict);
  badge.className = "verdict-badge " + meta.cls;
  icon.textContent = meta.icon;
  text.textContent = meta.label;
  recommendation.textContent = report.recommendation;

  const score = Math.min(100, report.risk_score);
  riskFill.style.width = score + "%";
  riskScoreText.textContent = score;

  checklist.innerHTML = "";
  report.checks.forEach((c) => {
    const li = document.createElement("li");
    li.className = c.status === "pass" ? "pass" : "flag";
    li.innerHTML = `<span class="mark">${c.status === "pass" ? "✔" : "✕"}</span>
      <span class="msg"><strong>${c.name}</strong><span>${c.message}</span></span>`;
    checklist.appendChild(li);
  });

  verdictBox.hidden = false;
  playBuzzer(report.verdict);
}
