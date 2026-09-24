// The playground's whole browser side. Pyodide runs CPython in WebAssembly;
// the compiler and astero are pure Python with no dependencies, so the
// toolchain is one zip and one `unpackArchive` call.
//
// Bump this when the CDN drops a version. Nothing else here names one.
const PYODIDE_VERSION = "314.0.6";
const PYODIDE_URL = `https://cdn.jsdelivr.net/npm/pyodide@${PYODIDE_VERSION}/`;
const HOME = "/home/pyodide";
// The text panes, and the tabs. `step` is a panel of controls rather than a
// block of text, so it is a tab without being something `render` fills in.
const TEXT_VIEWS = ["run", "types", "names", "python", "printed"];
const VIEWS = [...TEXT_VIEWS, "step"];

// Every string the reader sees. `index.html` carries this edition's,
// which is how the page is French on /fr/ and English on /en/.
const S = window.STRINGS;

const $ = (id) => document.getElementById(id);
const els = {
  source: $("source"),
  example: $("example"),
  run: $("run-button"),
  share: $("share"),
  status: $("status"),
  errors: $("errors"),
  stepAt: $("step-at"),
  stepCount: $("step-count"),
  stepNote: $("step-note"),
  stepSource: $("step-source"),
  stepWhere: $("step-where"),
  stepEnv: $("step-env"),
  stepStore: $("step-store"),
  stepPython: $("step-python"),
  stepOutput: $("step-output"),
  stepCursor: $("step-cursor"),
};

let analyse = null;
let stepping = null;

function say(text, tone = "") {
  els.status.textContent = text;
  els.status.className = tone;
}

// ------------------------------------------------------------------ sharing

function encode(text) {
  const bytes = new TextEncoder().encode(text);
  let binary = "";
  for (const byte of bytes) binary += String.fromCharCode(byte);
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

function decode(text) {
  const padded = text.replace(/-/g, "+").replace(/_/g, "/");
  const binary = atob(padded + "=".repeat((4 - (padded.length % 4)) % 4));
  const bytes = Uint8Array.from(binary, (c) => c.charCodeAt(0));
  return new TextDecoder().decode(bytes);
}

function fromFragment() {
  const match = /(?:^|[#&])code=([^&]+)/.exec(location.hash);
  if (!match) return null;
  try {
    return decode(match[1]);
  } catch {
    return null;
  }
}

// -------------------------------------------------------------------- views

function show(name) {
  for (const view of VIEWS) $(view).hidden = view !== name;
  for (const tab of document.querySelectorAll('[role="tab"]')) {
    tab.setAttribute("aria-selected", String(tab.dataset.view === name));
  }
  // Recording costs more than running, so it waits until someone asks.
  if (name === "step" && trace === null) record();
}

function render(found) {
  // A new run invalidates the recording; the Step view records again when
  // it is next opened.
  trace = null;
  for (const view of TEXT_VIEWS) $(view).textContent = found[view] || "";
  const problems = found.errors || [];
  els.errors.hidden = problems.length === 0;
  els.errors.textContent = problems.join("\n");
  if (problems.length) show("run");
}


// ------------------------------------------------------------------ stepping
//
// The whole run is recorded before the first step is shown, which is what
// makes going backwards free: it is an index into a list, not a second run.
// `at` is where we are in that list, and every button computes a new `at`.

let trace = null;
let at = 0;

const escaped = (text) =>
  text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function record() {
  if (!stepping) return;
  say(S.recording);
  const proxy = stepping(els.source.value);
  try {
    trace = proxy.toJs({ dict_converter: Object.fromEntries });
  } finally {
    proxy.destroy();
  }
  at = 0;
  els.stepAt.max = String(Math.max(0, trace.steps.length - 1));
  const notes = [];
  if (trace.truncated) notes.push(`${S.truncated} ${trace.steps.length}`);
  if (trace.error) notes.push(trace.error);
  if (trace.errors && trace.errors.length) notes.push(trace.errors.join("\n"));
  els.stepNote.hidden = notes.length === 0;
  els.stepNote.textContent = notes.join(" · ");
  draw();
  say(`${trace.steps.length} ${S.steps}`);
}

// The emitted Python takes its own steps and there is no honest mapping
// between them, so the two are lined up on the one thing they share: how
// much each has printed. Exact where output happens, nearest-so-far between.
function pyStepFor(printed) {
  const steps = trace.pysteps || [];
  let found = null;
  for (const step of steps) {
    if (step.printed <= printed) found = step;
    else break;
  }
  return found;
}

function rows(table, pairs, empty) {
  table.textContent = "";
  if (!pairs.length) {
    const row = table.insertRow();
    const cell = row.insertCell();
    cell.colSpan = 2;
    cell.className = "quiet";
    cell.textContent = empty;
    return;
  }
  for (const [name, value] of pairs) {
    const row = table.insertRow();
    row.insertCell().textContent = name;
    row.insertCell().textContent = value;
  }
}

function draw() {
  if (!trace || !trace.steps.length) {
    els.stepSource.textContent = "";
    els.stepCount.textContent = "0 / 0";
    return;
  }
  const step = trace.steps[at];
  const source = els.source.value;
  els.stepAt.value = String(at);
  els.stepCount.textContent = `${at + 1} / ${trace.steps.length}`;

  if (step.span) {
    const [from, to] = step.span;
    els.stepSource.innerHTML =
      escaped(source.slice(0, from)) +
      `<mark class="${step.kind}">${escaped(source.slice(from, to))}</mark>` +
      escaped(source.slice(to));
  } else {
    els.stepSource.textContent = source;
  }

  const verb = step.kind === "enter" ? S.evaluating : S.gives;
  const tail = step.value === null ? "" : ` ${step.value}`;
  els.stepWhere.textContent =
    `${verb}${tail} · ${step.stack.join(" \u25b8 ")} · ${step.scope}`;

  rows(els.stepEnv, step.env, S.nothingBound);
  rows(els.stepStore, step.store, S.nothingMutable);

  const py = pyStepFor(step.printed);
  els.stepPython.textContent = py ? `${py.line}  ${py.text}` : S.notYet;
  els.stepOutput.textContent = trace.output.slice(0, step.printed);
}

// Step over, in and out count function calls rather than sub-expressions:
// every operand of an expression is deeper and none of them is a call.
function moveTo(next) {
  at = Math.max(0, Math.min(trace.steps.length - 1, next));
  draw();
}

function seek(direction, test) {
  const here = trace.steps[at].call;
  for (let i = at + direction; i >= 0 && i < trace.steps.length; i += direction) {
    if (test(trace.steps[i].call, here)) return moveTo(i);
  }
  moveTo(direction > 0 ? trace.steps.length - 1 : 0);
}

const MOVES = {
  start: () => moveTo(0),
  end: () => moveTo(trace.steps.length - 1),
  back: () => moveTo(at - 1),
  forward: () => moveTo(at + 1),
  in: () => seek(1, (call, here) => call > here),
  out: () => seek(1, (call, here) => call < here),
};

function toCursor() {
  const where = els.source.selectionStart;
  const found = trace.steps.findIndex(
    (step) => step.span && step.span[0] <= where && where < step.span[1],
  );
  if (found >= 0) moveTo(found);
}

function wireStepping() {
  for (const button of document.querySelectorAll("[data-step]")) {
    button.addEventListener("click", () => {
      if (trace && trace.steps.length) MOVES[button.dataset.step]();
    });
  }
  els.stepAt.addEventListener("input", () => {
    if (trace) moveTo(Number(els.stepAt.value));
  });
  els.stepCursor.addEventListener("click", () => {
    if (trace && trace.steps.length) toCursor();
  });
  document.addEventListener("keydown", (event) => {
    if ($("step").hidden || !trace || event.metaKey || event.ctrlKey) return;
    if (event.target === els.source) return;
    const move = { ArrowRight: "forward", ArrowLeft: "back" }[event.key];
    if (move) {
      event.preventDefault();
      MOVES[move]();
    }
  });
}

// --------------------------------------------------------------------- work

function run() {
  if (!analyse) return;
  const started = performance.now();
  say(S.running);
  let found;
  const proxy = analyse(els.source.value);
  try {
    found = proxy.toJs({ dict_converter: Object.fromEntries });
  } finally {
    proxy.destroy();
  }
  render(found);
  const took = Math.round(performance.now() - started);
  if (found.errors.length) {
    say(`${found.errors.length} ${S.problems} · ${took} ms`, "bad");
  } else if (!found.ran) {
    say(`${took} ms`);
  } else if (found.agree) {
    say(`${S.agree} · ${took} ms`, "good");
  } else {
    say(`${S.disagree} · ${took} ms`, "bad");
  }
}

// --------------------------------------------------------------------- boot

function loadScript(url) {
  return new Promise((done, failed) => {
    const tag = document.createElement("script");
    tag.src = url;
    tag.onload = done;
    tag.onerror = () => failed(new Error(`cannot load ${url}`));
    document.head.append(tag);
  });
}

async function boot() {
  say(S.loadingPython);
  await loadScript(`${PYODIDE_URL}pyodide.js`);
  const py = await loadPyodide({ indexURL: PYODIDE_URL });

  say(S.loadingCompiler);
  const bundle = await fetch("py/playground.zip");
  if (!bundle.ok) {
    throw new Error(S.noBundle);
  }
  await py.unpackArchive(await bundle.arrayBuffer(), "zip", { extractDir: HOME });
  py.runPython(`import sys\nsys.path.insert(0, ${JSON.stringify(HOME)})`);
  analyse = py.runPython("from ocaml.pipeline import analyse\nanalyse");
  stepping = py.runPython("from ocaml.pipeline import stepping\nstepping");
  wireStepping();

  const programmes = py.FS.readdir(`${HOME}/corpus`)
    .filter((name) => name.endsWith(".ml"))
    .sort();
  for (const name of programmes) {
    const option = document.createElement("option");
    option.value = name;
    option.textContent = name.replace(/\.ml$/, "");
    els.example.append(option);
  }

  const load = (name) =>
    py.FS.readFile(`${HOME}/corpus/${name}`, { encoding: "utf8" });

  els.example.addEventListener("change", () => {
    els.source.value = load(els.example.value);
    run();
  });

  const shared = fromFragment();
  els.source.value = shared !== null ? shared : load(programmes[0]);
  if (shared === null) els.example.value = programmes[0];

  els.example.disabled = false;
  els.run.disabled = false;
  els.share.disabled = false;
  run();
}

// ------------------------------------------------------------------- wiring

for (const tab of document.querySelectorAll('[role="tab"]')) {
  tab.addEventListener("click", () => show(tab.dataset.view));
}

els.run.addEventListener("click", run);

// Switching language from here is a plain link; this only records the
// choice, under the key the chooser at the site root reads.
for (const link of document.querySelectorAll("a.switch[data-lang]")) {
  link.addEventListener("click", () => {
    try {
      localStorage.setItem("caml-prepa:lang", link.dataset.lang);
    } catch {
      /* a browser that refuses storage still follows the link */
    }
  });
}

els.source.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) {
    event.preventDefault();
    run();
  }
});

els.share.addEventListener("click", async () => {
  const url = `${location.origin}${location.pathname}#code=${encode(els.source.value)}`;
  history.replaceState(null, "", url);
  try {
    await navigator.clipboard.writeText(url);
    say(S.linkCopied);
  } catch {
    say(S.linkInBar);
  }
});

boot().catch((bad) => {
  say(String(bad.message || bad), "bad");
  els.errors.hidden = false;
  els.errors.textContent = `${bad}\n\n${S.bootHelp}`;
});
