/**
 * Demonstração ao vivo — o edugraph de verdade, dentro da apresentação.
 *
 * O sistema roda à parte (`python -m edugraph api serve`, porta 8000) e
 * entra aqui por um iframe, sem nenhuma mudança no código dele. O iframe
 * vive FORA do palco escalado, numa camada fixa: assim ele renderiza na
 * resolução real da tela e a passagem "janela no slide → tela inteira" é
 * só uma transformação (sem refazer o layout do app).
 *
 * Abre em `/?tour`, que força o tour de boas-vindas do laboratório
 * (frontend/src/tour/estado.ts → opcoesDaUrl). A turma de Computação
 * fictícia é gerada pelo próprio servidor a cada ▶ (src/edugraph/lab/demo.py).
 *
 * Se o sistema não responder, NADA é simulado: a janela mostra capturas
 * reais, com o rótulo "capturas, não é execução ao vivo".
 */

window.iniciarDemo = function iniciarDemo(deck, CONFIG, opcoes = {}) {
  const slide = document.getElementById("demo");
  if (!slide) return;
  const indiceDemo = deck.slides.indexOf(slide);
  const tela = slide.querySelector(".janela-app .tela");
  const estadoEl = slide.querySelector(".janela-barra .estado");
  const estadoTexto = estadoEl?.querySelector("span");
  const urlEl = slide.querySelector(".janela-barra .url");
  const aviso = slide.querySelector(".aviso-fallback");
  const previa = tela.querySelector("img.previa");
  const legenda = slide.querySelector(".legenda-janela");
  const legendaAoVivo = legenda ? legenda.innerHTML : "";

  const params = new URLSearchParams(location.search);
  const appUrl = (params.get("app") || CONFIG.appUrl).replace(/\/$/, "");
  if (urlEl) urlEl.textContent = appUrl.replace(/^https?:\/\//, "") + CONFIG.caminhoDemo;
  slide.querySelectorAll("a[data-app-link]").forEach((a) => { a.href = appUrl + CONFIG.caminhoDemo; });

  if (opcoes.estatico) {
    if (estadoTexto) estadoTexto.textContent = "Prévia";
    return;
  }

  const camada = document.getElementById("camada-demo");
  const moldura = document.createElement("div");
  moldura.className = "moldura";
  const iframe = document.createElement("iframe");
  iframe.title = "edugraph — sistema em execução";
  iframe.setAttribute("allow", "fullscreen");
  iframe.setAttribute("tabindex", "-1");
  moldura.appendChild(iframe);
  camada.appendChild(moldura);

  const botaoSair = document.getElementById("sair-demo");
  let online = null;
  let carregado = false;
  let expandida = false;
  let intervalo = 0;
  let discreto = 0;

  const naDemo = () => deck.atual === indiceDemo;

  function definirOnline(v) {
    const mudou = online !== v;
    online = v;
    estadoEl?.classList.toggle("ao-vivo", v);
    estadoEl?.classList.toggle("offline", !v);
    if (estadoTexto) estadoTexto.textContent = v ? "Ao vivo · sistema conectado" : "Sistema não respondeu";
    if (aviso) aviso.hidden = v;
    slide.classList.toggle("offline", !v);
    if (legenda) {
      legenda.innerHTML = v
        ? legendaAoVivo
        : "<b>Figura.</b> Capturas reais do edugraph, gravadas em 16/11/2026 — o sistema não está respondendo agora; <b>não é execução ao vivo</b>.";
    }
    if (v && !carregado) carregar();
    if (mudou) posicionar();
  }

  async function verificar() {
    const ctrl = new AbortController();
    const prazo = setTimeout(() => ctrl.abort(), 2500);
    try {
      // `no-cors`: a resposta é opaca, mas só chega se o servidor estiver de pé.
      await fetch(`${appUrl}/health`, { mode: "no-cors", cache: "no-store", signal: ctrl.signal });
      definirOnline(true);
    } catch {
      definirOnline(false);
    } finally {
      clearTimeout(prazo);
    }
  }

  function carregar(forcarNovo = false) {
    const sep = CONFIG.caminhoDemo.includes("?") ? "&" : "?";
    iframe.src = appUrl + CONFIG.caminhoDemo + (forcarNovo ? `${sep}r=${Date.now()}` : "");
    carregado = true;
  }

  function posicionar() {
    const W = window.innerWidth;
    const H = window.innerHeight;
    moldura.style.width = `${W}px`;
    moldura.style.height = `${H}px`;
    if (!naDemo() || !online) {
      moldura.classList.remove("visivel");
      return;
    }
    if (expandida) {
      moldura.style.transform = "translate(0px, 0px) scale(1)";
      moldura.style.borderRadius = "0px";
    } else {
      const r = tela.getBoundingClientRect();
      const s = Math.min(r.width / W, r.height / H);
      const x = r.left + (r.width - W * s) / 2;
      const y = r.top + (r.height - H * s) / 2;
      moldura.style.transform = `translate(${x}px, ${y}px) scale(${s})`;
      moldura.style.borderRadius = `${2 / s}px`;
    }
    moldura.classList.add("visivel");
    if (previa) previa.style.opacity = "0";
  }

  function entrar() {
    if (!online) return abrirGaleria(0);
    expandida = true;
    moldura.classList.add("expandida");
    document.body.classList.add("em-demo");
    posicionar();
    botaoSair.classList.add("mostrar");
    botaoSair.classList.remove("discreto");
    clearTimeout(discreto);
    discreto = setTimeout(() => botaoSair.classList.add("discreto"), 3500);
    setTimeout(() => { iframe.focus(); }, 500);
    deck.transmitir();
  }

  function sair() {
    if (!expandida) return;
    expandida = false;
    moldura.classList.remove("expandida");
    document.body.classList.remove("em-demo");
    botaoSair.classList.remove("mostrar", "discreto");
    posicionar();
    iframe.blur();
    window.focus();
    document.body.focus?.();
    deck.transmitir();
  }

  function reiniciar() {
    carregar(true);
  }

  botaoSair.addEventListener("click", sair);
  slide.querySelector("[data-demo='entrar']")?.addEventListener("click", entrar);
  slide.querySelector("[data-demo='reiniciar']")?.addEventListener("click", () => (online ? reiniciar() : verificar()));
  slide.querySelector("[data-demo='capturas']")?.addEventListener("click", () => abrirGaleria(0));

  deck.aoMudar((e) => {
    if (e.tipo === "escala") return posicionar();
    if (e.tipo === "slide") {
      if (naDemo()) {
        verificar();
        clearInterval(intervalo);
        intervalo = setInterval(verificar, CONFIG.intervaloSaude);
      } else {
        clearInterval(intervalo);
        if (expandida) sair();
      }
      // Espera a transição do slide para medir a janela no lugar certo.
      posicionar();
      setTimeout(posicionar, 680);
      return;
    }
    if (e.tipo === "comando") {
      if (e.acao === "demo-entrar") { if (!naDemo()) deck.ir(indiceDemo, 0); setTimeout(entrar, naDemo() ? 0 : 700); }
      else if (e.acao === "demo-sair") { sair(); fecharGaleria(); }
      else if (e.acao === "demo-reiniciar") reiniciar();
      return;
    }
    if (e.tipo === "tecla") {
      const k = e.evento.key;
      if (galeria.classList.contains("aberta")) {
        e.evento.preventDefault();
        if (k === "Escape") fecharGaleria();
        else if (k === "ArrowRight" || k === " ") mostrarCaptura(indiceCaptura + 1);
        else if (k === "ArrowLeft") mostrarCaptura(indiceCaptura - 1);
        return true;
      }
      if (k === "d" || k === "D") {
        e.evento.preventDefault();
        if (!naDemo()) deck.ir(indiceDemo, 0);
        else entrar();
        return true;
      }
      if (naDemo() && k === "Enter") { e.evento.preventDefault(); entrar(); return true; }
      if (naDemo() && (k === "r" || k === "R")) { e.evento.preventDefault(); reiniciar(); return true; }
    }
    return undefined;
  });

  /* ——— Galeria de capturas reais (reserva) ——— */
  const galeria = document.getElementById("galeria");
  const gImg = galeria.querySelector("img");
  const gLegenda = galeria.querySelector(".g-legenda");
  const gContador = galeria.querySelector(".g-contador");
  let indiceCaptura = 0;
  function mostrarCaptura(i) {
    const lista = CONFIG.capturas;
    indiceCaptura = (i + lista.length) % lista.length;
    gImg.src = lista[indiceCaptura].src;
    gImg.alt = lista[indiceCaptura].legenda;
    gLegenda.textContent = lista[indiceCaptura].legenda;
    gContador.textContent = `${indiceCaptura + 1} / ${lista.length}`;
  }
  function abrirGaleria(i) {
    mostrarCaptura(i);
    galeria.classList.add("aberta");
  }
  function fecharGaleria() { galeria.classList.remove("aberta"); }
  galeria.addEventListener("click", (e) => {
    const b = e.target.closest("button[data-g]");
    if (!b) return;
    if (b.dataset.g === "ant") mostrarCaptura(indiceCaptura - 1);
    else if (b.dataset.g === "prox") mostrarCaptura(indiceCaptura + 1);
    else fecharGaleria();
  });

  // Aquece o sistema logo na abertura: quando a demo chegar, o tour já está na tela.
  setTimeout(verificar, 1200);
  window.addEventListener("resize", () => posicionar());
};
