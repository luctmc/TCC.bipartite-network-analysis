/**
 * Motor da apresentação — sem dependências.
 *
 * Cada `<section class="slide">` de index.html é um slide. Dentro dele:
 *   data-entra          entra em cascata quando o slide aparece;
 *   data-passo="n"      aparece no passo n (seta → ou espaço);
 *   data-sai="n"        some no passo n;
 *   data-esmaece="n"    fica esmaecido a partir do passo n;
 *   <aside class="notas"> fala do apresentador (nunca aparece no palco).
 * O slide recebe `data-etapa` com o passo atual, para o CSS dos diagramas.
 *
 * Teclado: → espaço PgDn avançam; ← PgUp voltam; Home/End; O visão geral;
 * F tela cheia; P modo apresentador; N notas na própria tela; B tela preta;
 * D demonstração; A apêndice; número + Enter vai ao slide.
 */

(() => {
const CONFIG = window.EDUGRAPH_CONFIG;
const { iniciarDemo, iniciarDiagramas } = window;

const params = new URLSearchParams(location.search);
const EMBUTIDO = params.has("embed");
const TODOS = params.has("todos");
if (EMBUTIDO) document.body.classList.add("embutido");
if (TODOS) document.body.classList.add("todos");

const palco = document.querySelector(".palco");
// Versão curta (?curta): tira os slides marcados com data-opcional antes de numerar.
if (params.has("curta")) palco.querySelectorAll(":scope > .slide[data-opcional]").forEach((s) => s.remove());
const slides = [...palco.querySelectorAll(":scope > .slide")];
const canal = !EMBUTIDO && "BroadcastChannel" in window ? new BroadcastChannel(CONFIG.canal) : null;
const reduzido = window.matchMedia("(prefers-reduced-motion: reduce)");

const principais = slides.filter((s) => !s.hasAttribute("data-apendice"));
const apendice = slides.filter((s) => s.hasAttribute("data-apendice"));

let atual = -1;
let passo = 0;
const ouvintes = new Set();

/* ——— Preparação dos slides ——— */
slides.forEach((slide, i) => {
  slide.setAttribute("aria-roledescription", "slide");
  slide.setAttribute("aria-hidden", "true");
  slide.dataset.indice = String(i);
  const passos = [...slide.querySelectorAll("[data-passo],[data-sai],[data-esmaece]")]
    .flatMap((el) => [el.dataset.passo, el.dataset.sai, el.dataset.esmaece])
    .filter((v) => v !== undefined)
    .map(Number);
  slide.dataset.maxPasso = String(passos.length ? Math.max(...passos) : 0);
  slide.querySelectorAll("[data-entra]").forEach((el, k) => {
    if (!el.style.getPropertyValue("--d")) el.style.setProperty("--d", el.dataset.entra || String(k));
  });
  if (!slide.classList.contains("sem-rodape")) {
    const rodape = document.createElement("footer");
    rodape.className = "rodape-slide";
    rodape.setAttribute("aria-hidden", "true");
    const ap = slide.hasAttribute("data-apendice");
    const numero = ap
      ? `Apêndice A${apendice.indexOf(slide) + 1}`
      : `${String(principais.indexOf(slide) + 1).padStart(2, "0")} / ${String(principais.length).padStart(2, "0")}`;
    const atual = Number(slide.dataset.secao || 0);
    const meio = ap
      ? `<span class="r-ato">Apêndice técnico</span>`
      : `<span class="r-secoes">${(CONFIG.secoes || []).map((nome, k) => `<span class="${k + 1 === atual ? "on" : k + 1 < atual ? "feita" : ""}">${k + 1} ${nome}</span>`).join("")}</span>`;
    rodape.innerHTML = `<span class="r-marca">edugraph · TCC Grupo 16</span>${meio}<span class="r-num">${numero}</span>`;
    slide.appendChild(rodape);
  }
});

// Mapa dos capítulos: os seis tracinhos no pé de cada divisor.
document.querySelectorAll(".div-mapa").forEach((mapa) => {
  const atual = Number(mapa.closest(".slide")?.dataset.secao || 0);
  mapa.innerHTML = (CONFIG.secoes || []).map((nome, k) =>
    `<li class="${k + 1 === atual ? "on" : k + 1 < atual ? "feita" : ""}" style="--i:${k}"><b>${String(k + 1).padStart(2, "0")}</b>${nome}</li>`).join("");
});

const deck = {
  slides,
  get atual() { return atual; },
  get passo() { return passo; },
  embutido: EMBUTIDO,
  ir,
  proximo,
  anterior,
  aoMudar(fn) { ouvintes.add(fn); },
  slideAtual() { return slides[atual]; },
};

/* ——— Escala do palco 1920 × 1080 ——— */
function escalar() {
  const s = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
  const x = (window.innerWidth - 1920 * s) / 2;
  const y = (window.innerHeight - 1080 * s) / 2;
  palco.style.left = "0";
  palco.style.top = "0";
  palco.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
  ouvintes.forEach((fn) => fn({ tipo: "escala" }));
}
window.addEventListener("resize", escalar);

/* ——— Passos ——— */
function aplicarPassos(slide, p) {
  slide.dataset.etapa = String(p);
  slide.querySelectorAll("[data-passo],[data-sai],[data-esmaece]").forEach((el) => {
    const entra = el.dataset.passo !== undefined ? Number(el.dataset.passo) : 0;
    const sai = el.dataset.sai !== undefined ? Number(el.dataset.sai) : Infinity;
    const esmaece = el.dataset.esmaece !== undefined ? Number(el.dataset.esmaece) : Infinity;
    const visivel = p >= entra && p < sai;
    if (el.dataset.passo !== undefined || el.dataset.sai !== undefined) el.classList.toggle("passo-on", visivel);
    el.classList.toggle("passo-fora", p >= esmaece && visivel);
  });
}

function ir(n, p = 0, origem = "local") {
  n = Math.max(0, Math.min(slides.length - 1, n));
  const max = Number(slides[n].dataset.maxPasso);
  p = TODOS ? max : Math.max(0, Math.min(max, p));
  const mudouSlide = n !== atual;
  const anteriorIdx = atual;
  if (mudouSlide) {
    if (anteriorIdx >= 0) {
      const velho = slides[anteriorIdx];
      velho.classList.remove("ativo", "entrou");
      velho.classList.toggle("saindo-frente", n > anteriorIdx);
      velho.classList.toggle("saindo-tras", n < anteriorIdx);
      velho.setAttribute("aria-hidden", "true");
      setTimeout(() => velho.classList.remove("saindo-frente", "saindo-tras"), 900);
    }
    const novo = slides[n];
    novo.classList.remove("saindo-frente", "saindo-tras", "entrou", "vem-de-tras");
    // Ponto de partida da entrada conforme a direção (profundidade): para a
    // frente, o novo slide chega de levemente maior; para trás, de menor.
    if (anteriorIdx >= 0 && n < anteriorIdx) {
      novo.classList.add("vem-de-tras");
      void novo.offsetWidth;
    }
    novo.classList.add("ativo");
    requestAnimationFrame(() => novo.classList.remove("vem-de-tras"));
    novo.setAttribute("aria-hidden", "false");
    document.body.classList.toggle("tela-tinta", novo.classList.contains("tinta"));
    // Dois quadros para o navegador registrar o estado inicial antes da cascata.
    requestAnimationFrame(() => requestAnimationFrame(() => {
      if (slides[atual] === novo) novo.classList.add("entrou");
    }));
    if (EMBUTIDO || reduzido.matches) novo.classList.add("entrou");
  }
  atual = n;
  passo = p;
  aplicarPassos(slides[n], p);
  if (!EMBUTIDO) {
    const hash = `#${n + 1}${p ? "." + p : ""}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
  }
  atualizarControles();
  ouvintes.forEach((fn) => fn({ tipo: "slide", n, p, mudouSlide, origem }));
  transmitir();
}

function proximo() {
  const max = Number(slides[atual].dataset.maxPasso);
  if (passo < max) ir(atual, passo + 1);
  else if (atual < slides.length - 1) ir(atual + 1, 0);
}
function anterior() {
  if (passo > 0) ir(atual, passo - 1);
  else if (atual > 0) ir(atual - 1, Number(slides[atual - 1].dataset.maxPasso));
}

function lerHash() {
  const m = /^#(\d+)(?:\.(\d+))?$/.exec(location.hash);
  if (!m) return null;
  return { n: Number(m[1]) - 1, p: Number(m[2] || 0) };
}

/* ——— Sincronização com o modo apresentador ——— */
function transmitir() {
  if (!canal) return;
  canal.postMessage({ tipo: "estado", n: atual, p: passo, total: slides.length, demo: document.body.classList.contains("em-demo") });
}
if (canal) {
  canal.onmessage = (ev) => {
    const m = ev.data || {};
    if (m.tipo === "comando") {
      if (m.acao === "proximo") proximo();
      else if (m.acao === "anterior") anterior();
      else if (m.acao === "ir") ir(m.n, m.p ?? 0, "remoto");
      else if (m.acao === "cortina") alternarCortina();
      else ouvintes.forEach((fn) => fn({ tipo: "comando", acao: m.acao }));
    } else if (m.tipo === "ola") {
      transmitir();
    }
  };
}
deck.transmitir = transmitir;

/* ——— Controles da plateia ——— */
const controles = document.querySelector(".controles");
const contador = document.querySelector(".controles .contador");
const progresso = document.querySelector(".progresso");
function atualizarControles() {
  if (!contador) return;
  const s = slides[atual];
  const ap = s.hasAttribute("data-apendice");
  contador.textContent = ap ? `A${apendice.indexOf(s) + 1}` : `${principais.indexOf(s) + 1} / ${principais.length}`;
  const fracao = ap ? 1 : (principais.indexOf(s) + (Number(s.dataset.maxPasso) ? passo / (Number(s.dataset.maxPasso) + 1) : 0)) / (principais.length - 1);
  if (progresso) progresso.style.width = `${Math.min(100, fracao * 100)}%`;
}
let temporizador = 0;
function mostrarControles() {
  if (!controles) return;
  controles.classList.remove("oculto");
  clearTimeout(temporizador);
  temporizador = setTimeout(() => controles.classList.add("oculto"), 2200);
}
if (controles && !EMBUTIDO) {
  document.addEventListener("mousemove", mostrarControles);
  controles.addEventListener("mouseenter", () => clearTimeout(temporizador));
  controles.addEventListener("mouseleave", mostrarControles);
  controles.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-acao]");
    if (!b) return;
    const acao = b.dataset.acao;
    if (acao === "anterior") anterior();
    else if (acao === "proximo") proximo();
    else if (acao === "visao") alternarVisao();
    else if (acao === "tela-cheia") alternarTelaCheia();
    else if (acao === "apresentador") abrirApresentador();
    else if (acao === "notas") alternarNotas();
  });
  setTimeout(() => controles.classList.add("oculto"), 2500);
}

/* ——— Toque (navegação de reserva) ——— */
let toqueX = null;
palco.addEventListener("touchstart", (e) => { toqueX = e.touches[0].clientX; }, { passive: true });
palco.addEventListener("touchend", (e) => {
  if (toqueX === null) return;
  const dx = e.changedTouches[0].clientX - toqueX;
  if (Math.abs(dx) > 50) (dx < 0 ? proximo : anterior)();
  toqueX = null;
});

/* ——— Tela cheia, apresentador, cortina ——— */
function alternarTelaCheia() {
  if (!document.fullscreenElement) document.documentElement.requestFullscreen?.().catch(() => {});
  else document.exitFullscreen?.();
}
function abrirApresentador() {
  const url = new URL("apresentador.html", location.href);
  url.search = location.search;
  window.open(url.toString(), "edugraph-apresentador", "width=1440,height=900");
}
const cortina = document.getElementById("cortina");
function alternarCortina() { cortina?.classList.toggle("on"); }

/* ——— Notas na própria tela (tela única) ——— */
const notasInline = document.getElementById("notas-inline");
function alternarNotas() {
  if (!notasInline) return;
  notasInline.classList.toggle("aberta");
  renderNotasInline();
}
function renderNotasInline() {
  if (!notasInline?.classList.contains("aberta")) return;
  const s = slides[atual];
  const notas = s.querySelector(".notas");
  notasInline.innerHTML = `<h4>${s.dataset.titulo || ""}</h4>${notas ? notas.innerHTML : "<p>(sem notas)</p>"}`;
  notasInline.scrollTop = 0;
}
ouvintes.add((e) => { if (e.tipo === "slide" && e.mudouSlide) renderNotasInline(); });

/* ——— Visão geral ——— */
const visao = document.getElementById("visao-geral");
let visaoMontada = false;
function montarVisao() {
  const grupos = new Map();
  slides.forEach((s, i) => {
    const sec = Number(s.dataset.secao || 0);
    const chave = s.hasAttribute("data-apendice") ? "Apêndice técnico" : sec ? `${sec} · ${CONFIG.secoes[sec - 1]}` : ["referencias", "encerramento"].includes(s.id) ? "Referências e encerramento" : "Abertura e sumário";
    if (!grupos.has(chave)) grupos.set(chave, []);
    grupos.get(chave).push(i);
  });
  const frag = document.createDocumentFragment();
  const h = document.createElement("h2");
  h.textContent = "Visão geral";
  const ajuda = document.createElement("p");
  ajuda.className = "vg-ajuda";
  ajuda.textContent = "Clique num slide para ir até ele · Esc fecha";
  frag.append(h, ajuda);
  for (const [ato, indices] of grupos) {
    const t = document.createElement("p");
    t.className = "vg-ato";
    t.textContent = ato;
    const grade = document.createElement("div");
    grade.className = "vg-grade";
    for (const i of indices) {
      const s = slides[i];
      const b = document.createElement("button");
      b.className = "vg-item";
      b.dataset.n = String(i);
      const mini = document.createElement("div");
      mini.className = "vg-mini";
      const clone = s.cloneNode(true);
      clone.classList.add("ativo", "entrou");
      clone.querySelectorAll("[data-passo]").forEach((el) => el.classList.add("passo-on"));
      clone.querySelectorAll("iframe, .notas").forEach((el) => el.remove());
      clone.removeAttribute("id");
      clone.querySelectorAll("[id]").forEach((el) => el.removeAttribute("id"));
      mini.appendChild(clone);
      const leg = document.createElement("div");
      leg.className = "vg-legenda";
      const ap = s.hasAttribute("data-apendice");
      leg.innerHTML = `<b>${ap ? "A" + (apendice.indexOf(s) + 1) : principais.indexOf(s) + 1}</b><span>${s.dataset.titulo || ""}</span>`;
      b.append(mini, leg);
      b.addEventListener("click", () => { fecharVisao(); ir(i, 0); });
      grade.appendChild(b);
    }
    frag.append(t, grade);
  }
  visao.appendChild(frag);
  visaoMontada = true;
}
function escalarMinis() {
  visao.querySelectorAll(".vg-mini").forEach((m) => {
    const s = m.clientWidth / 1920;
    const c = m.firstElementChild;
    c.style.transform = `scale(${s})`;
    c.style.width = "1920px";
    c.style.height = "1080px";
  });
}
function alternarVisao() {
  if (!visao) return;
  if (visao.classList.contains("aberta")) return fecharVisao();
  if (!visaoMontada) montarVisao();
  visao.classList.add("aberta");
  escalarMinis();
  visao.querySelectorAll(".vg-item").forEach((b) => b.classList.toggle("atual", Number(b.dataset.n) === atual));
  visao.querySelector(".vg-item.atual")?.focus();
}
function fecharVisao() { visao?.classList.remove("aberta"); }
window.addEventListener("resize", () => { if (visao?.classList.contains("aberta")) escalarMinis(); });

/* ——— Teclado ——— */
const irPara = document.getElementById("ir-para");
let digitos = "";
let tempoDigitos = 0;
function aoTeclar(e) {
  if (EMBUTIDO) return;
  if (e.target.closest?.("input, textarea, select")) return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (visao?.classList.contains("aberta")) {
    if (k === "Escape" || k === "o" || k === "O") { e.preventDefault(); fecharVisao(); }
    return;
  }
  for (const fn of ouvintes) if (fn({ tipo: "tecla", evento: e }) === true) return;
  if (/^\d$/.test(k)) {
    digitos += k;
    irPara.textContent = `Ir para ${digitos}`;
    irPara.classList.add("on");
    clearTimeout(tempoDigitos);
    tempoDigitos = setTimeout(() => { digitos = ""; irPara.classList.remove("on"); }, 2500);
    return;
  }
  if (k === "Enter" && digitos) {
    e.preventDefault();
    const alvo = principais[Number(digitos) - 1];
    if (alvo) ir(slides.indexOf(alvo), 0);
    digitos = "";
    irPara.classList.remove("on");
    return;
  }
  switch (k) {
    case "ArrowRight": case "PageDown": case " ": case "Spacebar":
      e.preventDefault(); proximo(); break;
    case "ArrowLeft": case "PageUp": case "Backspace":
      e.preventDefault(); anterior(); break;
    case "ArrowDown": e.preventDefault(); ir(atual + 1, 0); break;
    case "ArrowUp": e.preventDefault(); ir(atual - 1, 0); break;
    case "Home": e.preventDefault(); ir(0, 0); break;
    case "End": e.preventDefault(); ir(slides.indexOf(principais[principais.length - 1]), 0); break;
    case "o": case "O": case "g": case "G": e.preventDefault(); alternarVisao(); break;
    case "f": case "F": e.preventDefault(); alternarTelaCheia(); break;
    case "p": case "P": e.preventDefault(); abrirApresentador(); break;
    case "n": case "N": e.preventDefault(); alternarNotas(); break;
    case "b": case "B": case ".": e.preventDefault(); alternarCortina(); break;
    case "a": case "A": if (apendice.length) { e.preventDefault(); ir(slides.indexOf(apendice[0]), 0); } break;
    case "Escape":
      if (cortina?.classList.contains("on")) alternarCortina();
      else if (notasInline?.classList.contains("aberta")) alternarNotas();
      break;
    default: return;
  }
  mostrarControlesSeTeclado();
}
function mostrarControlesSeTeclado() { /* controles só reaparecem com o mouse: a plateia não precisa vê-los */ }
document.addEventListener("keydown", aoTeclar);

/* ——— Início ——— */
escalar();
iniciarDiagramas(deck);
window.preencherSistema?.();
window.iniciarContexto?.(deck);
window.iniciarMotion?.(deck);
if (!EMBUTIDO) iniciarDemo(deck, CONFIG);
else iniciarDemo(deck, CONFIG, { estatico: true });

window.addEventListener("hashchange", () => {
  const h = lerHash();
  if (h && (h.n !== atual || h.p !== passo)) ir(h.n, h.p, "hash");
});
const inicio = lerHash();
ir(inicio ? inicio.n : 0, inicio ? inicio.p : 0);
document.fonts?.ready.then(() => ouvintes.forEach((fn) => fn({ tipo: "escala" })));
window.deck = deck;
})();
