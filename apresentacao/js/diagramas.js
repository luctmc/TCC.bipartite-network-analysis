/**
 * Diagramas da apresentação — todos desenhados com DADOS REAIS do TCC
 * (js/dados.js, gerado por gerar_dados.py a partir do repositório):
 *
 * 1. A rede da capa, do encerramento e da modularidade: a projeção
 *    aluno ↔ aluno de `synthetic_v1` (98 alunos), com o esqueleto de
 *    arestas que a própria API serve e as comunidades do Louvain.
 * 2. O exemplo da fundamentação: a fixture `tiny_v1` (6 alunos, 3
 *    disciplinas), cujos valores o grupo derivou no papel. O Louvain e o
 *    Girvan–Newman mostrados são o rastro real de `edugraph.lab.trace`.
 *
 * Só as POSIÇÕES dos nós (js/desenho.js) e os NOMES do exemplo (Ana a
 * Felipe; js/dados.js → contexto) são escolhas de desenho; nós, arestas,
 * pesos, grupos, Q e centralidades vêm dos artefatos.
 */
(() => {
  const NS = "http://www.w3.org/2000/svg";
  const D = window.EDUGRAPH_DADOS;
  const COR = ["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#0072B2", "#D55E00"];
  const el = (tag, attrs = {}, pai) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    pai?.appendChild(e);
    return e;
  };
  const num = (v, casas = 2) => v.toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });

  /** Forma da comunidade (a mesma ordem de frontend/src/palette.ts). */
  function forma(g, tipo, r, cor, traco, largura = 1.4) {
    if (tipo === 1) {
      const h = r * 1.18;
      return el("path", { d: `M0 ${-h} L${h} ${h * 0.78} L${-h} ${h * 0.78} Z`, fill: cor, stroke: traco, "stroke-width": largura, "stroke-linejoin": "round" }, g);
    }
    if (tipo === 2) return el("rect", { x: -r, y: -r, width: 2 * r, height: 2 * r, rx: r * 0.32, fill: cor, stroke: traco, "stroke-width": largura }, g);
    return el("circle", { r, fill: cor, stroke: traco, "stroke-width": largura }, g);
  }

  /* ——— 1. A rede real de synthetic_v1 ——— */
  function redeReal(svg) {
    const s = D.synthetic;
    const W = Number(svg.dataset.w || 860), H = Number(svg.dataset.h || 800), M = 40;
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    const tinta = svg.dataset.tema === "tinta";
    const pos = {};
    s.nos.forEach(([id, x, y]) => { pos[id] = [M + x * (W - 2 * M), M + y * (H - 2 * M)]; });
    const ga = el("g", { class: "rr-arestas" }, svg);
    s.arestas.forEach(([u, v], k) => {
      const [x1, y1] = pos[u], [x2, y2] = pos[v];
      el("line", { x1: x1.toFixed(1), y1: y1.toFixed(1), x2: x2.toFixed(1), y2: y2.toFixed(1), pathLength: 1, class: "rr-aresta", style: `--k:${k % 120}` }, ga);
    });
    const gn = el("g", { class: "rr-nos" }, svg);
    const metrica = svg.dataset.tamanho; // opcional: grau | intermediacao | autovetor
    const idx = { grau: 4, intermediacao: 5, autovetor: 6 }[metrica];
    const max = idx ? Math.max(...s.nos.map((n) => n[idx])) : 1;
    s.nos.forEach((n, k) => {
      const [id, , , com] = n;
      const r = idx ? 4 + 13 * (n[idx] / max) : 7.5;
      const g = el("g", { class: "rr-no", "data-com": com, style: `--k:${k}; transform: translate(${pos[id][0].toFixed(1)}px, ${pos[id][1].toFixed(1)}px)` }, gn);
      forma(g, com, r, COR[com], tinta ? "#161512" : "#1a1915", tinta ? 1.2 : 1);
      g.querySelector("*").classList.add("rr-forma");
    });
  }

  /* ——— 2. O exemplo tiny_v1 ——— */
  const T = D.tiny;
  const DES = window.EDUGRAPH_DESENHO;
  const ALUNOS = DES.ALUNOS_BIP;
  const { DISC, POS_BIP, POS_PROJ } = DES;
  const NOME = D.contexto.nomes;
  const DISCN = D.contexto.disciplinas;
  const nDisc = {};
  T.matriculas.forEach((m) => { nDisc[m.disciplina] = (nDisc[m.disciplina] || 0) + 1; });
  const final = T.louvain.membership;
  const ordemFinal = (() => {
    const tam = {};
    Object.values(final).forEach((c) => { tam[c] = (tam[c] || 0) + 1; });
    const ord = Object.keys(tam).sort((a, b) => tam[b] - tam[a] || a - b);
    return Object.fromEntries(ord.map((c, i) => [c, i]));
  })();
  const largura = (w, modo) => (modo === "s" ? DES.larguraSimples(w) : DES.larguraRA(w));

  function exemplo(svg) {
    const modo = svg.dataset.exemplo;
    svg.setAttribute("viewBox", modo === "gn" ? "0 0 900 720" : "0 0 900 600");
    svg.classList.add("ex", `ex-${modo}`);
    const camadas = {};
    ["bip", "proj", "pesos", "nos", "disc", "extra"].forEach((n) => { camadas[n] = el("g", { class: `ex-${n}` }, svg); });
    // Matrículas (bipartido)
    if (modo === "bipartido" || modo === "projecao") {
      T.matriculas.forEach((m, k) => {
        const [x1, y1] = POS_BIP[m.aluno];
        const [x2, y2] = DISC[m.disciplina];
        el("line", { x1: x1 + 24, y1, x2: x2 - 60, y2, pathLength: 1, class: `ex-mat d-${m.disciplina} a-${m.aluno}`, style: `--k:${k}` }, camadas.bip);
      });
      Object.entries(DISC).forEach(([d, [x, y]]) => {
        const g = el("g", { class: `ex-d ex-d-${d}`, transform: `translate(${x} ${y})` }, camadas.disc);
        el("rect", { x: -60, y: -24, width: 120, height: 48, rx: 10, class: "ex-d-forma" }, g);
        el("text", { y: 7, class: "ex-d-letra", "text-anchor": "middle" }, g).textContent = DISCN[d][1];
        el("text", { y: 50, class: "ex-rot2", "text-anchor": "middle" }, g).textContent = `${DISCN[d][0]} · ${nDisc[d]} alunos`;
      });
    }
    // Ligações da projeção (aluno ↔ aluno)
    if (modo !== "bipartido") {
      T.simples.forEach(([u, v, w], k) => {
        const ra = T.alocacao[k][2];
        const [x1, y1] = POS_PROJ[u], [x2, y2] = POS_PROJ[v];
        const ln = el("line", { x1, y1, x2, y2, pathLength: 1, class: `ex-lig e-${u}-${v}`, style: `--ws:${largura(w, "s")}px; --wr:${largura(ra, "r")}px; --k:${k}` }, camadas.proj);
        ln.dataset.par = `${u}-${v}`;
        if (modo === "projecao") {
          // Rótulo no meio da ligação; as duas que se cruzam no centro ganham posição própria.
          const AJUSTE = { "S1-S2": [0.3, -30, 8], "S3-S6": [0.72, 0, -14] };
          const [t, ox, oy] = AJUSTE[`${u}-${v}`] || [0.5, Math.abs(x2 - x1) < 10 ? -30 : 0, Math.abs(x2 - x1) < 10 ? 6 : -12];
          const mx = x1 + (x2 - x1) * t, my = y1 + (y2 - y1) * t;
          const off = [ox, oy];
          el("text", { x: mx + off[0], y: my + off[1], class: "ex-peso ps", "text-anchor": "middle" }, camadas.pesos).textContent = num(w, 0);
          el("text", { x: mx + off[0], y: my + off[1], class: "ex-peso pr", "text-anchor": "middle" }, camadas.pesos).textContent = num(ra, 2);
        }
      });
    }
    // Alunos (círculo e triângulo: a forma acompanha a comunidade, como na interface)
    ALUNOS.forEach((a) => {
      const [x, y] = modo === "bipartido" ? POS_BIP[a] : modo === "projecao" ? POS_BIP[a] : POS_PROJ[a];
      const g = el("g", { class: `ex-a ex-a-${a}`, style: `transform: translate(${x}px, ${y}px)` }, camadas.nos);
      g.dataset.id = a;
      const halo = el("circle", { r: 34, class: "ex-halo" }, g);
      halo.dataset.k = "halo";
      const c = forma(g, 0, 24, "#56B4E9", "#1a1915", 1.6);
      c.classList.add("ex-f0");
      const t = forma(g, 1, 22, "#E69F00", "#1a1915", 1.6);
      t.classList.add("ex-f1");
      el("text", { y: 8, class: "ex-a-num", "text-anchor": "middle" }, g).textContent = NOME[a][0];
      el("text", { y: 54, class: "ex-a-nome", "text-anchor": "middle" }, g).textContent = NOME[a];
    });
    if (modo === "bipartido") {
      el("text", { x: 190, y: 26, class: "ex-cab", "text-anchor": "middle" }, camadas.extra).textContent = "alunos";
      el("text", { x: 730, y: 26, class: "ex-cab", "text-anchor": "middle" }, camadas.extra).textContent = "disciplinas";
    }
    if (modo === "gn") {
      // Curva de Q a cada corte (rastro real do Girvan–Newman).
      const cortes = T.girvan_newman.cortes;
      const g = el("g", { class: "ex-curva", transform: "translate(250 600)" }, camadas.extra);
      const W = 470, H = 80, qs = cortes.map((c) => c.q), qmin = -0.25, qmax = 0.15;
      const X = (i) => (i / (cortes.length - 1)) * W, Y = (q) => H - ((q - qmin) / (qmax - qmin)) * H;
      el("line", { x1: 0, y1: Y(0), x2: W, y2: Y(0), class: "ex-curva-zero" }, g);
      el("text", { x: -8, y: Y(0) + 5, class: "ex-rot2", "text-anchor": "end" }, g).textContent = "0";
      el("polyline", { points: qs.map((q, i) => `${X(i)},${Y(q)}`).join(" "), class: "ex-curva-linha", pathLength: 1 }, g);
      qs.forEach((q, i) => {
        const p = el("g", { transform: `translate(${X(i)} ${Y(q)})`, class: `ex-curva-p ${i === T.girvan_newman.melhor ? "melhor" : ""}` }, g);
        el("circle", { r: i === T.girvan_newman.melhor ? 7 : 4.5 }, p);
        el("text", { y: i === T.girvan_newman.melhor ? -14 : 20, class: "ex-rot2", "text-anchor": "middle" }, p).textContent = `${cortes[i].k} grupos`;
      });
      el("text", { x: -14, y: -40, class: "ex-cab" }, g).textContent = "Q a cada corte do Girvan–Newman";
    }
    atualizarExemplo(svg, 0);
  }

  /** Estado do exemplo em cada passo do slide. */
  function atualizarExemplo(svg, passo) {
    const modo = svg.dataset.exemplo;
    const nos = [...svg.querySelectorAll(".ex-a")];
    const setGrupo = (membros, ativo) => {
      nos.forEach((n) => {
        const id = n.dataset.id;
        const com = membros?.[id];
        const tam = membros ? Object.values(membros).filter((c) => c === com).length : 1;
        n.classList.toggle("sozinho", !membros || tam < 2);
        const grupo = membros && tam >= 2 ? ordemFinal[final[id]] ?? 0 : -1;
        n.classList.toggle("g0", grupo === 0);
        n.classList.toggle("g1", grupo === 1);
        n.classList.toggle("movendo", id === ativo);
      });
    };
    svg.querySelectorAll(".ex-a").forEach((n) => n.style.removeProperty("--escala"));
    svg.dataset.passo = String(passo);

    if (modo === "bipartido") {
      svg.classList.toggle("com-mat", passo >= 1);
      svg.classList.toggle("destaca", passo >= 2);
      return;
    }
    if (modo === "projecao") {
      const proj = passo >= 1;
      svg.classList.toggle("com-mat", !proj);
      svg.classList.toggle("projetado", proj);
      svg.classList.toggle("alocacao", passo >= 2);
      nos.forEach((n) => {
        const [x, y] = (proj ? POS_PROJ : POS_BIP)[n.dataset.id];
        n.style.transform = `translate(${x}px, ${y}px)`;
      });
      return;
    }
    if (modo === "louvain") {
      const movs = T.louvain.movimentos;
      const k = Math.min(passo, movs.length);
      const membros = Object.fromEntries(ALUNOS.map((a) => [a, a]));
      for (let i = 0; i < k; i++) membros[movs[i].no] = membros[movs[i].para];
      setGrupo(passo === 0 ? null : membros, k > 0 && passo <= movs.length ? movs[k - 1].no : null);
      const painel = svg.closest(".slide")?.querySelector("[data-q-louvain]");
      if (painel) {
        const q = k ? movs[k - 1].q : null;
        painel.querySelector(".q-valor").textContent = q === null ? "—" : num(q, 3);
        painel.querySelector(".q-mov").textContent = `${k} de ${movs.length}`;
        painel.querySelector(".q-grupos").textContent = String(new Set(Object.values(membros)).size);
        painel.querySelector(".q-barra i").style.transform = `scaleX(${q === null ? 0 : Math.max(0, (q + 0.15) / 0.3)})`;
        const quem = painel.querySelector(".q-quem");
        if (quem) {
          const m = k ? movs[k - 1] : null;
          quem.textContent = passo === 0 ? "Cada aluno começa sozinho no próprio grupo."
            : m && passo <= movs.length ? `${NOME[m.no]} vai para o grupo de ${NOME[m.para]}.`
            : "Ninguém mais quer mudar: dois grupos.";
        }
      }
      return;
    }
    if (modo === "gn") {
      const rem = T.girvan_newman.removidas;
      // Passo 1: a ponte mais usada (Carla–Diego) em vermelho. Passo 2: Carla–Diego e Carla–Elisa saem e a
      // rede se parte. Passo 3: os cortes seguem até o fim, e a curva mostra o Q.
      const n = passo >= 3 ? rem.length : passo === 2 ? 2 : 0;
      svg.querySelectorAll(".ex-lig").forEach((l) => {
        const i = rem.findIndex(([u, v]) => l.dataset.par === `${u}-${v}` || l.dataset.par === `${v}-${u}`);
        l.classList.toggle("removida", i >= 0 && i < n);
        l.classList.toggle("ponte", passo === 1 && i === 0);
      });
      // Depois do 2º corte a rede se parte: os grupos do melhor corte (k = 2).
      setGrupo(passo >= 2 ? final : null, null);
      svg.classList.toggle("com-curva", passo >= 3);
      return;
    }
    if (modo === "centralidade") {
      const metrica = ["grau", "grau", "intermediacao", "autovetor"][Math.min(passo, 3)];
      const v = T.centralidade[metrica];
      const max = Math.max(...Object.values(v), 1e-9);
      nos.forEach((no) => {
        const id = no.dataset.id;
        const esc = passo === 0 ? 1 : 0.55 + 0.75 * (v[id] / max);
        no.style.setProperty("--escala", esc.toFixed(3));
        no.classList.toggle("vencedor", passo > 0 && v[id] === max);
      });
      const tab = svg.closest(".slide")?.querySelector(".tab-cent");
      tab?.querySelectorAll("[data-m]").forEach((c) => c.classList.toggle("ativa", passo > 0 && c.dataset.m === metrica));
    }
  }

  /* ——— 3. Contadores (números que sobem até o valor real) ——— */
  function contar(elm) {
    if (elm.dataset.contado === "1") return;
    elm.dataset.contado = "1";
    const alvo = Number(elm.dataset.contar);
    const casas = Number(elm.dataset.casas || 0);
    const milhar = elm.dataset.milhar !== undefined;
    const fmt = (x) => (milhar ? Math.round(x).toLocaleString("pt-BR") : num(x, casas));
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || document.body.classList.contains("embutido")) {
      elm.textContent = fmt(alvo);
      return;
    }
    const t0 = performance.now(), dur = 1300;
    const passo = (t) => {
      const f = Math.min(1, (t - t0) / dur);
      const e = 1 - Math.pow(1 - f, 4);
      elm.textContent = fmt(alvo * e);
      if (f < 1) requestAnimationFrame(passo);
    };
    requestAnimationFrame(passo);
  }

  window.iniciarDiagramas = function iniciarDiagramas(deck) {
    document.querySelectorAll("svg[data-rede-real]").forEach(redeReal);
    document.querySelectorAll("svg[data-exemplo]").forEach(exemplo);
    const aplicar = () => {
      const slide = deck.slideAtual();
      if (!slide) return;
      slide.querySelectorAll("svg[data-exemplo]").forEach((svg) => atualizarExemplo(svg, deck.passo));
      slide.querySelectorAll("[data-contar]").forEach((c) => {
        const dono = c.closest("[data-passo]");
        if (!dono || dono.classList.contains("passo-on")) setTimeout(() => contar(c), 250);
      });
    };
    deck.aoMudar((e) => {
      if (e.tipo === "slide") {
        if (e.mudouSlide) deck.slides.forEach((s) => { if (s !== deck.slideAtual()) s.querySelectorAll("[data-contar]").forEach((c) => { c.dataset.contado = "0"; }); });
        aplicar();
      }
    });
  };
})();
