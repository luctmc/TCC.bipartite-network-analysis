/**
 * Modo apresentador. Abra pela tecla P na janela da plateia (ou direto em
 * apresentador.html). As duas janelas conversam por BroadcastChannel —
 * mesma origem, sem servidor de sincronização. As prévias são a própria
 * apresentação em modo embutido (`?embed`), e as notas vêm de index.html.
 */

(async () => {
const CONFIG = window.EDUGRAPH_CONFIG;

const canal = new BroadcastChannel(CONFIG.canal);
const base = new URL("index.html", location.href);
base.search = location.search;

const previaAtual = document.getElementById("previa-atual");
const previaProxima = document.getElementById("previa-proxima");
const notasEl = document.getElementById("notas");
const tituloAtual = document.getElementById("titulo-atual");
const tituloProximo = document.getElementById("titulo-proximo");
const contador = document.getElementById("contador");
const aviso = document.getElementById("aviso");
const estadoDemo = document.getElementById("estado-demo");

let slides = [];
let n = 0;
let p = 0;
let maxPassos = [];
let ultimoContato = 0;

function urlPrevia(i, passo, todos) {
  const u = new URL(base);
  u.searchParams.set("embed", "1");
  if (todos) u.searchParams.set("todos", "1");
  u.hash = `${i + 1}${passo ? "." + passo : ""}`;
  return u.toString();
}

async function carregarNotas() {
  const texto = await (await fetch(base, { cache: "no-store" })).text();
  const doc = new DOMParser().parseFromString(texto, "text/html");
  if (new URLSearchParams(location.search).has("curta")) doc.querySelectorAll(".palco > .slide[data-opcional]").forEach((s) => s.remove());
  slides = [...doc.querySelectorAll(".palco > .slide")].map((s) => {
    const passos = [...s.querySelectorAll("[data-passo],[data-sai],[data-esmaece]")]
      .flatMap((el) => [el.dataset.passo, el.dataset.sai, el.dataset.esmaece])
      .filter((v) => v !== undefined).map(Number);
    return {
      titulo: s.dataset.titulo || s.id,
      apendice: s.hasAttribute("data-apendice"),
      notas: s.querySelector(".notas")?.innerHTML || "<p>(sem notas)</p>",
      max: passos.length ? Math.max(...passos) : 0,
    };
  });
  maxPassos = slides.map((s) => s.max);
}

function render() {
  if (!slides.length) return;
  const s = slides[n];
  const principais = slides.filter((x) => !x.apendice).length;
  const numero = s.apendice ? `A${n - principais + 1}` : `${n + 1} / ${principais}`;
  contador.textContent = `${numero}${s.max ? ` · passo ${p}/${s.max}` : ""}`;
  tituloAtual.textContent = s.titulo;
  tituloProximo.textContent = p < s.max ? `${s.titulo} — passo ${p + 1}` : slides[n + 1]?.titulo ?? "— fim —";
  const novaAtual = urlPrevia(n, p, false);
  if (previaAtual.dataset.url !== novaAtual) { previaAtual.src = novaAtual; previaAtual.dataset.url = novaAtual; }
  const [pn, pp, todos] = p < s.max ? [n, p + 1, false] : [Math.min(n + 1, slides.length - 1), 0, true];
  const novaProx = urlPrevia(pn, pp, todos);
  if (previaProxima.dataset.url !== novaProx) { previaProxima.src = novaProx; previaProxima.dataset.url = novaProx; }
  if (notasEl.dataset.n !== String(n)) {
    notasEl.innerHTML = s.notas;
    notasEl.dataset.n = String(n);
    notasEl.scrollTop = 0;
  }
}

/* Comandos: vão para a plateia; sem plateia, o apresentador anda sozinho. */
function comando(acao, extra = {}) {
  canal.postMessage({ tipo: "comando", acao, ...extra });
  if (Date.now() - ultimoContato > 3000) {
    if (acao === "proximo") { if (p < maxPassos[n]) p++; else if (n < slides.length - 1) { n++; p = 0; } }
    else if (acao === "anterior") { if (p > 0) p--; else if (n > 0) { n--; p = maxPassos[n]; } }
    render();
  }
}

canal.onmessage = (ev) => {
  const m = ev.data || {};
  if (m.tipo !== "estado") return;
  ultimoContato = Date.now();
  aviso.classList.remove("on");
  n = m.n;
  p = m.p;
  estadoDemo.textContent = m.demo ? "demo aberta" : "demo fechada";
  estadoDemo.classList.toggle("on", !!m.demo);
  render();
};

document.addEventListener("click", (e) => {
  const b = e.target.closest("button[data-cmd]");
  if (b) comando(b.dataset.cmd);
});
document.getElementById("abrir-plateia").addEventListener("click", () => {
  window.open(base.toString(), "edugraph-plateia");
});

document.addEventListener("keydown", (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  switch (e.key) {
    case "ArrowRight": case "PageDown": case " ": e.preventDefault(); comando("proximo"); break;
    case "ArrowLeft": case "PageUp": e.preventDefault(); comando("anterior"); break;
    case "d": case "D": comando("demo-entrar"); break;
    case "Escape": comando("demo-sair"); break;
    case "b": case "B": case ".": comando("cortina"); break;
    case "t": case "T": zerar(); break;
    default:
  }
});

/* Cronômetro e relógio. */
const cronometro = document.querySelector("#cronometro span");
const alvo = document.getElementById("alvo");
let inicio = Date.now();
function zerar() { inicio = Date.now(); tick(); }
document.getElementById("zerar").addEventListener("click", zerar);
function tick() {
  const seg = Math.floor((Date.now() - inicio) / 1000);
  cronometro.textContent = `${String(Math.floor(seg / 60)).padStart(2, "0")}:${String(seg % 60).padStart(2, "0")}`;
  alvo.textContent = `de ${CONFIG.duracaoAlvoMin} min`;
  document.getElementById("cronometro").classList.toggle("atrasado", seg > CONFIG.duracaoAlvoMin * 60);
  document.getElementById("hora").textContent = new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" });
}
setInterval(tick, 1000);
tick();

try {
  await carregarNotas();
} catch {
  notasEl.innerHTML = "<p><b>Não consegui ler as notas.</b> Abra a apresentação por <code>python apresentacao/servir.py</code> (o navegador bloqueia a leitura de arquivos abertos direto do disco). Na janela da plateia, a tecla N mostra as notas na própria tela.</p>";
}
render();
canal.postMessage({ tipo: "ola" });
setInterval(() => { aviso.classList.toggle("on", Date.now() - ultimoContato > 4000); }, 1500);
})();
