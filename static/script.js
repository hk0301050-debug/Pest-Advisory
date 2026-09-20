"use strict";
const $ = (s) => document.querySelector(s);
const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const FULL_MONTHS = ["January","February","March","April","May","June","July","August","September","October","November","December"];
const SEASON_OF = { 12:"Winter",1:"Winter",2:"Winter",3:"Summer",4:"Summer",5:"Summer",6:"Monsoon",7:"Monsoon",8:"Monsoon",9:"Monsoon",10:"Post-monsoon",11:"Post-monsoon" };
const BAND_TEXT = { HIGH: "Strong signal", MEDIUM: "Moderate signal", LOW: "Weak signal", BENEFICIAL: "Beneficial insect" };
const WEATHER = ["avg_temp", "min_temp", "max_temp", "rainfall", "wind_speed"];
const LAG_FIELDS = [["avg_temp", "Temp"], ["rainfall", "Rain"], ["wind_speed", "Wind"]];

let meta = null;
let month = new Date().getMonth() + 1;
let lastResult = null;

const title = (s) => s.replace(/\b[a-z]/g, (c) => c.toUpperCase());
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

function setStatus(text, kind = "") {
  const el = $("#status");
  el.textContent = text;
  el.className = "status " + kind;
}

/* ---------- start-up: load options (retry while a free server wakes up) ---------- */
async function loadMeta() {
  for (let i = 0; i < 30; i++) {
    try {
      const r = await fetch("/api/meta");
      if (r.ok) { meta = await r.json(); return init(); }
    } catch (e) { /* server not reachable yet */ }
    setStatus("Waking the server. This can take up to a minute.");
    await sleep(3000);
  }
  setStatus("Server not reachable. Refresh to retry.", "bad");
}

function fill(select, values, label) {
  select.innerHTML = values.map((v) => `<option value="${esc(v)}">${esc(label ? label(v) : v)}</option>`).join("");
}

function init() {
  setStatus("Model ready", "ok");
  fill($("#state"), meta.states, title);
  fill($("#season"), meta.seasons);
  $("#state").addEventListener("change", onState);
  onState();

  $("#months").innerHTML = MONTHS.map((m, i) => `<button type="button" data-m="${i + 1}" aria-pressed="false" title="${FULL_MONTHS[i]}">${m}</button>`).join("");
  $("#months").addEventListener("click", (e) => { const b = e.target.closest("button"); if (b) setMonth(+b.dataset.m); });
  setMonth(month);

  $("#lagTable").insertAdjacentHTML("beforeend", [1, 2, 3].map((n) =>
    `<span>${n} month${n > 1 ? "s" : ""} ago</span>` +
    LAG_FIELDS.map(([f, name]) => `<input id="${f}_lag${n}" type="number" step="0.1" aria-label="${name} ${n} months ago">`).join("")
  ).join(""));
  $("#sameLags").addEventListener("change", onSameLags);

  $("#form").addEventListener("submit", onSubmit);
  $("#example").addEventListener("click", fillExample);
}

function onState() {
  const s = $("#state").value;
  fill($("#district"), meta.state_districts[s] || [], title);
  fill($("#crop"), meta.state_crops[s] || [], title);
}

function setMonth(m) {
  month = m;
  document.querySelectorAll("#months button").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.m === m)));
  $("#season").value = SEASON_OF[m];
}

function onSameLags() {
  const same = $("#sameLags").checked;
  $("#lagTable").hidden = same;
  if (!same) {
    [1, 2, 3].forEach((n) => LAG_FIELDS.forEach(([f]) => {
      const el = $(`#${f}_lag${n}`);
      if (!el.value) el.value = $("#" + f).value;
    }));
  }
}

function fillExample() {
  $("#state").value = "haryana"; onState();
  $("#district").value = "karnal"; $("#crop").value = "rice";
  setMonth(7);
  const w = { avg_temp: 31, min_temp: 27, max_temp: 36, rainfall: 210, wind_speed: 9 };
  WEATHER.forEach((f) => ($("#" + f).value = w[f]));
  $("#sameLags").checked = false; $("#lagTable").hidden = false;
  const lags = { avg_temp: [34, 36, 35], rainfall: [90, 30, 10], wind_speed: [11, 12, 10] };
  [1, 2, 3].forEach((n) => LAG_FIELDS.forEach(([f]) => ($(`#${f}_lag${n}`).value = lags[f][n - 1])));
}

/* ---------- predict ---------- */
function buildPayload() {
  const num = (id) => parseFloat($("#" + id).value);
  const p = {
    state: $("#state").value, district: $("#district").value, crop: $("#crop").value,
    season: $("#season").value, month,
  };
  WEATHER.forEach((f) => (p[f] = num(f)));
  const same = $("#sameLags").checked;
  [1, 2, 3].forEach((n) => LAG_FIELDS.forEach(([f]) => (p[`${f}_lag${n}`] = same ? p[f] : num(`${f}_lag${n}`))));
  return p;
}

function showError(msg) {
  $("#results").innerHTML = `<div class="notice reveal" role="alert"><strong>Could not predict</strong>${esc(msg)}</div>`;
}

async function onSubmit(e) {
  e.preventDefault();
  const form = $("#form");
  if (!form.reportValidity()) return;
  const p = buildPayload();
  if ([...Object.values(p)].some((v) => typeof v === "number" && Number.isNaN(v))) return showError("Fill in every weather value, including the previous three months.");
  if (p.min_temp > p.max_temp) return showError("The lowest temperature cannot be higher than the highest temperature.");

  const btn = $("#submit");
  btn.disabled = true; btn.textContent = "Predicting…";
  try {
    const r = await fetch("/api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(p) });
    const data = await r.json();
    if (!r.ok) {
      const d = data.detail;
      return showError(typeof d === "string" ? d : "Some values are outside the allowed range. Check the weather inputs.");
    }
    lastResult = { data, p };
    render(data);
    if (window.matchMedia("(max-width: 900px)").matches) $("#results").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showError("The server did not respond. If it was idle, wait a few seconds and try again.");
  } finally {
    btn.disabled = false; btn.textContent = "Predict pests";
  }
}

function bandOf(p) { return p.beneficial ? "BENEFICIAL" : p.severity; }

function render(d) {
  const top = d.predictions[0], tb = bandOf(top);
  const rows = d.predictions.map((p) => {
    const b = bandOf(p), pct = Math.max(p.probability * 100, 0);
    return `<li>
      <div class="row"><span class="name">${esc(p.pest)}</span><span class="pct">${esc(p.percent)}</span></div>
      <div class="track ${b}" role="img" aria-label="${esc(p.pest)}: ${esc(p.percent)}, ${BAND_TEXT[b]}"><span style="width:${pct}%"></span></div>
      <div class="scale"><span>0%</span><span>30%</span><span>50%</span><span>100%</span></div>
      <p class="remedy"><b>${p.beneficial ? "Note:" : "What to do:"}</b> ${esc(p.remedy)}</p>
    </li>`;
  }).join("");

  $("#results").innerHTML = `<div class="reveal">
    <p class="where">${esc(title(d.crop))} in ${esc(title(d.district))}, ${esc(title(d.state))}, ${FULL_MONTHS[d.month - 1]}</p>
    <div class="lead ${tb}">
      <h2>${esc(top.pest)}</h2>
      <div class="conf"><span class="dot"></span>${BAND_TEXT[tb]}, ${esc(top.percent)} model confidence</div>
    </div>
    <div class="advice"><h3>Advice for this month</h3><ul>${d.advisory.map((a) => `<li>${esc(a)}</li>`).join("")}</ul></div>
    <div class="ranked"><h3>Three most likely pests</h3><ol>${rows}</ol></div>
    <div class="tools"><button type="button" id="csv">Download as CSV</button></div>
    <p class="caveat">Confidence is the model’s estimated probability among all pests and diseases it was trained on. It shows how closely this month’s conditions match past records, not a measured outbreak. Treat remedies as general guidance and confirm doses and permitted products with your local agricultural extension officer.</p>
  </div>`;
  $("#csv").addEventListener("click", downloadCsv);
}

function downloadCsv() {
  const { data } = lastResult;
  const q = (v) => `"${String(v).replace(/"/g, '""')}"`;
  const lines = [["Pest", "Confidence", "Signal", "Advice"].join(",")].concat(
    data.predictions.map((p) => [q(title(p.pest)), q(p.percent), q(BAND_TEXT[bandOf(p)]), q(p.remedy)].join(","))
  );
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/csv" }));
  a.download = `pest_advisory_${data.district.replace(/\s+/g, "_")}_${FULL_MONTHS[data.month - 1]}.csv`;
  a.click(); URL.revokeObjectURL(a.href);
}

loadMeta();
