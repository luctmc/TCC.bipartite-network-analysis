/**
 * Animações da Introdução (contexto) e dos slides novos da Fundamentação.
 *
 * Sem bibliotecas e sem rede: SVG e JavaScript puros, scripts clássicos.
 * Dois tipos, como em motion.js:
 *
 *   FILMES (começam sozinhos; K pausa, J e L voltam e avançam):
 *     alunoSome  M1  linha do tempo de um aluno que some (ILUSTRATIVA)
 *     inep       M2  de cada 100 que entraram (Inep, js/contexto-dados.js)
 *     lista      M3  a planilha de matrículas vira o mapa da turma
 *     solucao    M10 entra a lista, sai o mapa
 *   Cada fábrica devolve {duracao, legendas, render(t)}; motion.js toca.
 *
 *   CENAS POR PASSOS (quem apresenta controla com a seta):
 *     ligacao M4 · forca M5 · comunidades M6 · papeis M7 · atencao M8 ·
 *     porque M9 · grafo M11 · escoreZ M12 · dicionario M13
 *   <svg data-ctx="nome">; o estado depende só do passo do slide.
 *
 * Números e textos do sistema vêm de js/dados.js (gerar_dados.py); os do
 * Inep, de js/contexto-dados.js. Nomes, cursos e posições são escolha de
 * desenho (js/desenho.js). Nada é digitado aqui.
 */
(() => {
  const NS = "http://www.w3.org/2000/svg";
  const D = window.EDUGRAPH_DADOS;
  const C = D.contexto;
  const T = D.tiny;
  const I = window.EDUGRAPH_INEP;
  const P = window.EDUGRAPH_DESENHO;
  const COR = ["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#0072B2", "#D55E00", "#CC79A7"];
  const TINTA = "#1a1915", PAPEL = "#fbfaf7", MUTED = "#6e6a60", REGRA = "#cdc7b8";

  /* ——— Utilidades ——— */
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, f) => a + (b - a) * f;
  const easeIO = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const easeOut = (x) => 1 - Math.pow(1 - x, 3);
  const easeBack = (x) => { const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const seg = (t, a, b, curva = easeIO) => curva(clamp((t - a) / (b - a)));
  const num = (v, c = 2) => v.toLocaleString("pt-BR", { minimumFractionDigits: c, maximumFractionDigits: c });
  const el = (tag, attrs = {}, pai) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    pai?.appendChild(e);
    return e;
  };
  const txt = (pai, x, y, texto, cls, ancora = "middle", extra = {}) => {
    const t = el("text", { x, y, class: cls, "text-anchor": ancora, ...extra }, pai);
    t.textContent = texto;
    return t;
  };
  const set = (e, attrs) => { for (const k in attrs) e.setAttribute(k, attrs[k]); };
  function forma(g, tipo, r, cor, traco = TINTA, larg = 1.6) {
    if (tipo === 1) {
      const h = r * 1.18;
      return el("path", { d: `M0 ${-h} L${h} ${h * 0.78} L${-h} ${h * 0.78} Z`, fill: cor, stroke: traco, "stroke-width": larg, "stroke-linejoin": "round" }, g);
    }
    if (tipo === 2) return el("rect", { x: -r, y: -r, width: 2 * r, height: 2 * r, rx: r * 0.32, fill: cor, stroke: traco, "stroke-width": larg }, g);
    return el("circle", { r, fill: cor, stroke: traco, "stroke-width": larg }, g);
  }
  const mover = (g, [x, y]) => { g.style.transform = `translate(${x}px, ${y}px)`; };

  /* ——— O exemplo ——— */
  const nome = (id) => C.nomes[id];
  const cursoCurto = (id) => (C.cursos[id] === "ADS" ? "ADS" : "Eng. Elétrica");
  const disc = (d) => C.disciplinas[d][0];
  const final = T.louvain.membership;
  const grupoDe = (id) => (final[id] === final.S1 ? 0 : 1);
  const chave = (u, v) => (u < v ? `${u}-${v}` : `${v}-${u}`);
  const RA = Object.fromEntries(T.alocacao.map(([u, v, w]) => [chave(u, v), w]));
  const SIMPLES = Object.fromEntries(T.simples.map(([u, v, w]) => [chave(u, v), w]));
  const PARES = T.simples.map(([u, v]) => [u, v]);
  const A = C.alunos;

  /** Um aluno: halo, forma (círculo → triângulo conforme o grupo), inicial, nome e curso. */
  function noAluno(pai, id, { nomeY = 58, nomeX = 0, ancora = "middle", curso = true } = {}) {
    const g = el("g", { class: `ctx-a ctx-a-${id}` }, pai);
    g.dataset.id = id;
    el("circle", { r: 37, class: "ctx-halo" }, g);
    forma(g, 0, 24, PAPEL).classList.add("ctx-f0");
    forma(g, 1, 22, COR[1]).classList.add("ctx-f1");
    txt(g, 0, 8, nome(id)[0], "ctx-ini");
    txt(g, nomeX, nomeY, nome(id), "ctx-nome", ancora);
    if (curso) {
      const c = el("g", { class: "ctx-curso", transform: "translate(0 -60)" }, g);
      const rotulo = cursoCurto(id);
      const w = rotulo.length * 10.5 + 26;
      el("rect", { x: -w / 2, y: -17, width: w, height: 32, rx: 16 }, c);
      txt(c, 0, 6, rotulo, "ctx-curso-t");
    }
    return g;
  }
  /** Uma ligação entre dois alunos (a espessura vem do peso real). */
  function linha(pai, [x1, y1], [x2, y2], largura, cls = "") {
    const l = el("line", { x1, y1, x2, y2, pathLength: 1, class: `ctx-lig ${cls}` }, pai);
    l.style.setProperty("--w", `${largura}px`);
    return l;
  }
  /** Mancha de um grupo: o contorno convexo engrossado com cantos redondos. */
  function mancha(pai, ids, pos, cls, raio = 58) {
    const pts = ids.map((i) => pos[i]);
    return el("path", { d: casco(pts), class: `ctx-mancha ${cls}`, "stroke-width": raio * 2 }, pai);
  }
  function casco(pts) {
    if (pts.length < 3) return `M${pts[0][0]} ${pts[0][1]} L${pts[pts.length - 1][0]} ${pts[pts.length - 1][1]}`;
    const p = [...pts].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
    const cruz = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], hi = [];
    for (const q of p) { while (lo.length >= 2 && cruz(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (const q of [...p].reverse()) { while (hi.length >= 2 && cruz(hi[hi.length - 2], hi[hi.length - 1], q) <= 0) hi.pop(); hi.push(q); }
    const h = lo.slice(0, -1).concat(hi.slice(0, -1));
    return `M${h.map(([x, y]) => `${x} ${y}`).join(" L")} Z`;
  }
  /** Rótulo em pílula, para "ponte", "beirada", "nó"… */
  function pilula(pai, x, y, texto, cls = "") {
    const g = el("g", { class: `ctx-pil ${cls}`, transform: `translate(${x} ${y})` }, pai);
    const w = texto.length * 11.5 + 30;
    el("rect", { x: -w / 2, y: -19, width: w, height: 36, rx: 18 }, g);
    txt(g, 0, 7, texto, "ctx-pil-t");
    return g;
  }

  /**
   * O mapa dos seis alunos nas posições de POS_PROJ, com as espessuras reais
   * (alocação de recursos). Diego, Elisa e a ligação entre eles ficam num
   * grupo próprio (a "ilha"), para o slide dos papéis poder afastá-los.
   */
  function mapa(svg, { cursos = true, manchas = true, nomes = true } = {}) {
    const pos = P.POS_PROJ;
    const camadas = {};
    ["manchas", "ligs", "nos", "extra"].forEach((n) => { camadas[n] = el("g", { class: `ctx-${n}` }, svg); });
    const ilha = el("g", { class: "ctx-ilha" }, svg);
    const ilhaManchas = el("g", {}, ilha), ilhaLigs = el("g", {}, ilha), ilhaNos = el("g", {}, ilha);
    svg.insertBefore(ilha, camadas.nos);
    const naIlha = (id) => id === "S4" || id === "S5";
    const m = {};
    if (manchas) {
      m.g0 = mancha(camadas.manchas, ["S1", "S2", "S3", "S6"].filter((i) => grupoDe(i) === 0), pos, "m0");
      m.g1 = mancha(ilhaManchas, ["S4", "S5"], pos, "m1");
    }
    const ligs = PARES.map(([u, v]) => {
      const dentroIlha = naIlha(u) && naIlha(v);
      const l = linha(dentroIlha ? ilhaLigs : camadas.ligs, pos[u], pos[v], P.larguraRA(RA[chave(u, v)]));
      l.dataset.u = u; l.dataset.v = v;
      return l;
    });
    const nos = Object.fromEntries(P.ALUNOS.map((id) => {
      const g = noAluno(naIlha(id) ? ilhaNos : camadas.nos, id, { curso: cursos });
      if (!nomes) g.querySelector(".ctx-nome").remove();
      mover(g, pos[id]);
      return [id, g];
    }));
    return { camadas, ilha, ligs, nos, manchas: m, pos };
  }
  const colorir = (nos, sim = true) => Object.entries(nos).forEach(([id, g]) => {
    g.classList.toggle("g0", sim && grupoDe(id) === 0);
    g.classList.toggle("g1", sim && grupoDe(id) === 1);
  });
  const toca = (l, id) => l.dataset.u === id || l.dataset.v === id;

  /* ═══════════════════ M4 · Uma disciplina, uma ligação ═══════════════════ */
  function cenaLigacao(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const POS = {
      0: { S1: [110, 330], S3: [790, 330], S2: [300, 470], S6: [600, 470], caixa: [450, 330] },
      1: { S1: [300, 160], S3: [600, 160], S2: [300, 470], S6: [600, 470], caixa: [450, 330] },
      3: { S1: [300, 160], S3: [600, 160], S2: [300, 440], S6: [600, 440], caixa: [450, 572] },
    };
    const gMat = el("g", { class: "ctx-mats" }, svg);
    const gLig = el("g", {}, svg);
    const caixa = el("g", { class: "ctx-caixa" }, svg);
    el("rect", { x: -170, y: -34, width: 340, height: 68, rx: 12 }, caixa);
    txt(caixa, 0, 9, disc("DA"), "ctx-caixa-t");
    const quatro = ["S1", "S3", "S2", "S6"];
    const nos = Object.fromEntries(quatro.map((id) => [id, noAluno(svg, id)]));
    // Matrículas (aluno → caixa), desenhadas na posição do passo 1.
    const mats = quatro.map((id) => {
      const [x, y] = POS[1][id];
      const cima = y < 330;
      const l = el("line", { x1: x, y1: y + (cima ? 30 : -30), x2: 450 + (x - 450) * 0.35, y2: cima ? 296 : 364, pathLength: 1, class: "ctx-mat" }, gMat);
      l.dataset.id = id;
      return l;
    });
    // As seis ligações entre os quatro (passo 3); Ana–Carla aparece já no passo 2.
    const pares = [["S1", "S3"], ["S1", "S2"], ["S3", "S6"], ["S1", "S6"], ["S2", "S3"], ["S2", "S6"]];
    const ligs = pares.map(([u, v]) => {
      const l = linha(gLig, POS[3][u], POS[3][v], P.larguraSimples(1));
      l.dataset.par = `${u}-${v}`;
      return l;
    });
    const rotLig = pilula(svg, 450, 122, "ligação", "ctx-pil-lig");
    // Passos 4 e 5: a força da ligação (antes, slide próprio "Nem toda ligação é igual").
    const tagAlg = pilula(svg, 450, 300, disc("DB"), "ctx-pil-disc");
    return (p) => {
      ligs.forEach((l) => {
        const k = chave(...l.dataset.par.split("-"));
        const w = p >= 5 ? P.larguraRA(RA[k]) : p >= 4 ? P.larguraSimples(SIMPLES[k]) : P.larguraSimples(1);
        l.style.setProperty("--w", `${w}px`);
        l.classList.toggle("realce", p === 4 && SIMPLES[k] >= 2);
        l.classList.toggle("so-sc", p >= 5 && SIMPLES[k] < 2);
      });
      tagAlg.classList.toggle("on", p === 4);
      const e = p >= 3 ? POS[3] : p >= 1 ? POS[1] : POS[0];
      quatro.forEach((id) => {
        mover(nos[id], e[id]);
        const visivel = id === "S1" || id === "S3" || p >= 3;
        nos[id].classList.toggle("oculto", !visivel);
        nos[id].classList.toggle("com-curso-on", id === "S1" || id === "S3");
      });
      mover(caixa, e.caixa);
      caixa.classList.toggle("rebaixada", p >= 3);
      mats.forEach((l) => l.classList.toggle("on", p >= 1 && p < 3 && (l.dataset.id === "S1" || l.dataset.id === "S3")));
      ligs.forEach((l) => l.classList.toggle("on", (p >= 2 && l.dataset.par === "S1-S3") || p >= 3));
      rotLig.classList.toggle("on", p === 2);
    };
  }

  /* ═══════════════════ M5 · Nem toda ligação é igual ═══════════════════ */
  function cenaForca(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const POS = { S1: [300, 160], S3: [600, 160], S2: [300, 440], S6: [600, 440] };
    const gLig = el("g", {}, svg);
    const quatro = ["S1", "S3", "S2", "S6"];
    const pares = [["S1", "S3"], ["S1", "S2"], ["S3", "S6"], ["S1", "S6"], ["S2", "S3"], ["S2", "S6"]];
    const ligs = pares.map(([u, v]) => {
      const l = linha(gLig, POS[u], POS[v], 4);
      l.dataset.u = u; l.dataset.v = v;
      l.classList.add("on");
      return l;
    });
    const nos = Object.fromEntries(quatro.map((id) => { const g = noAluno(svg, id, { curso: false }); mover(g, POS[id]); return [id, g]; }));
    const tagAlg = pilula(svg, 450, 82, disc("DB"), "ctx-pil-disc");
    const legenda = el("g", { class: "ctx-leg-forca" }, svg);
    txt(legenda, 450, 560, "", "ctx-nota");
    return (p) => {
      ligs.forEach((l) => {
        const k = chave(l.dataset.u, l.dataset.v);
        // Passo 0: uma disciplina em comum para todos (Sistemas de Computação).
        // Passo 1+: o peso simples (Ana, Bruno e Carla também dividem Algoritmos).
        // Passo 3: o peso de alocação de recursos, na mesma escala.
        const w = p >= 3 ? P.larguraRA(RA[k]) : p >= 1 ? P.larguraSimples(SIMPLES[k]) : P.larguraSimples(1);
        l.style.setProperty("--w", `${w}px`);
        l.classList.toggle("realce", p >= 1 && p < 3 && SIMPLES[k] >= 2);
        l.classList.toggle("so-sc", p >= 3 && SIMPLES[k] < 2);
      });
      tagAlg.classList.toggle("on", p >= 1 && p < 3);
      Object.values(nos).forEach((g) => g.classList.add("neutro"));
      legenda.querySelector("text").textContent = p >= 3
        ? `As ligações que vêm só de ${disc("DA")}, a turma mais cheia, afinam.`
        : p >= 1 ? "Ana, Bruno e Carla também dividem Algoritmos: a ligação engrossa." : "";
    };
  }

  /** As duas turmas do cartão "turma lotada × turma pequena" (desenho fixo, ilustrativo). */
  function cenaTurmas(svg) {
    svg.setAttribute("viewBox", "0 0 640 190");
    const bloco = (x0, n, cols, r, larg, titulo) => {
      const g = el("g", { transform: `translate(${x0} 0)` }, svg);
      const linhas = Math.ceil(n / cols);
      const dx = 280 / cols, dy = Math.min(140 / linhas, dx);
      const pontos = [];
      for (let i = 0; i < n; i++) {
        const x = 12 + dx * (i % cols) + dx / 2, y = 10 + dy * Math.floor(i / cols) + dy / 2;
        pontos.push([x, y]);
        el("circle", { cx: x, cy: y, r, class: "ctx-ponto" }, g);
      }
      const a = pontos[Math.floor(n * 0.3)], b = pontos[Math.floor(n * 0.62)];
      el("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: "ctx-par", "stroke-width": larg }, g);
      [a, b].forEach(([x, y]) => el("circle", { cx: x, cy: y, r: r * 1.9, class: "ctx-ponto par" }, g));
      txt(g, 152, 182, titulo, "ctx-nota");
    };
    bloco(0, 300, 25, 2.3, 1.2, "uma turma de 300: quase não diz nada");
    bloco(330, 15, 5, 8, 9, "uma turma de 15: diz bastante");
    return () => {};
  }

  /* ═══════════════════ M6 · Os grupos aparecem ═══════════════════ */
  function cenaComunidades(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const m = mapa(svg);
    m.ligs.forEach((l) => l.classList.add("on"));
    return (p) => {
      colorir(m.nos, p >= 1);
      Object.values(m.manchas).forEach((x) => x.classList.toggle("on", p >= 1));
      Object.entries(m.nos).forEach(([id, g]) => {
        g.classList.toggle("neutro", p < 1);
        g.classList.toggle("com-curso-on", p === 2);
        g.classList.toggle("curso-destaque", p === 2 && id === "S3");
      });
    };
  }

  /* ═══════════ M6 + M7 · Os grupos e o lugar de cada aluno (um slide) ═══════════ */
  function cenaGrupos(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const m = mapa(svg);
    m.ligs.forEach((l) => l.classList.add("on"));
    const ponte = pilula(m.camadas.extra, 470, 236, "ponte", "ctx-pil-papel");
    const beirada = pilula(m.camadas.extra, 86, 236, "beirada", "ctx-pil-papel");
    return (p) => {
      const semCarla = p === 4;
      colorir(m.nos, p >= 1);
      Object.values(m.manchas).forEach((x) => x.classList.toggle("on", p >= 1));
      Object.entries(m.nos).forEach(([id, g]) => {
        g.classList.toggle("neutro", p < 1);
        g.classList.toggle("com-curso-on", p === 2);
        g.classList.toggle("curso-destaque", p === 2 && id === "S3");
      });
      m.nos.S3.classList.toggle("halo", p === 3);
      m.nos.S3.classList.toggle("apagado", semCarla);
      m.ligs.forEach((l) => {
        l.classList.toggle("some", semCarla && toca(l, "S3"));
        l.classList.toggle("pulsa", p === 5 && toca(l, "S6"));
      });
      m.ilha.classList.toggle("afastada", semCarla);
      m.nos.S6.classList.toggle("halo", p === 5);
      ponte.classList.toggle("on", p >= 3 && !semCarla);
      beirada.classList.toggle("on", p >= 5);
    };
  }

  /* ═══════════════════ M7 · Ponte e beirada ═══════════════════ */
  function cenaPapeis(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const m = mapa(svg, { cursos: false });
    m.ligs.forEach((l) => l.classList.add("on"));
    colorir(m.nos);
    Object.values(m.manchas).forEach((x) => x.classList.add("on"));
    const ponte = pilula(m.camadas.extra, 470, 236, "ponte", "ctx-pil-papel");
    const beirada = pilula(m.camadas.extra, 86, 236, "beirada", "ctx-pil-papel");
    return (p) => {
      const semCarla = p === 2;
      m.nos.S3.classList.toggle("halo", p === 1);
      m.nos.S3.classList.toggle("apagado", semCarla);
      m.ligs.forEach((l) => {
        l.classList.toggle("some", semCarla && toca(l, "S3"));
        l.classList.toggle("pulsa", p >= 3 && toca(l, "S6"));
      });
      m.ilha.classList.toggle("afastada", semCarla);
      m.nos.S6.classList.toggle("halo", p === 3);
      ponte.classList.toggle("on", p >= 1 && !semCarla);
      beirada.classList.toggle("on", p >= 3);
    };
  }

  /* ═══════════════════ M8 · As três perguntas ═══════════════════ */
  function cenaAtencao(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const felipe = A.S6;
    const turma = C.turma;
    // Vista 1: três réguas, com a marca da turma e o marcador do Felipe.
    const vR = el("g", { class: "ctx-vista ctx-reguas" }, svg);
    const X0 = 120, X1 = 820;
    const regua = (y, titulo, dom, ticks, media, valor, fmt) => {
      const g = el("g", { transform: `translate(0 ${y})` }, vR);
      txt(g, X0, -70, titulo, "ctx-regua-t", "start");
      el("line", { x1: X0, y1: 0, x2: X1, y2: 0, class: "ctx-regua" }, g);
      const X = (v) => X0 + ((v - dom[0]) / (dom[1] - dom[0])) * (X1 - X0);
      ticks.forEach(([v, r]) => {
        el("line", { x1: X(v), y1: -7, x2: X(v), y2: 7, class: "ctx-regua" }, g);
        txt(g, X(v), 34, r, "ctx-nota");
      });
      const mm = el("g", { class: "ctx-media", transform: `translate(${X(media)} 0)` }, g);
      el("line", { x1: 0, y1: -26, x2: 0, y2: 26, class: "ctx-media-l" }, mm);
      txt(mm, 0, -32, fmt(media), "ctx-media-t");
      const mk = el("g", { class: "ctx-marcador" }, g);
      mk.dataset.x0 = String(X(media)); mk.dataset.x1 = String(X(valor));
      el("circle", { r: 17, class: "ctx-marcador-c" }, mk);
      txt(mk, 0, 6, "F", "ctx-marcador-i");
      return mk;
    };
    const mk = [
      regua(110, "Quantas disciplinas cursa", [0, 3], [[0, "0"], [1, "1"], [2, "2"], [3, "3"]],
        turma.disciplinas_por_aluno, felipe.n_disciplinas, (v) => `turma: ${num(v, 2)}`),
      regua(300, "Como vai nas notas", [50, 100], [[50, "50"], [60, "60"], [70, "70"], [80, "80"], [90, "90"], [100, "100"]],
        turma.nota_media, felipe.nota_media, (v) => `turma: ${num(v, 0)}`),
      regua(490, "O quanto está ligado ao próprio grupo", [-2, 2], [[-1.33, "abaixo"], [0, "na média"], [1.33, "acima"]],
        0, -1.33, () => "turma"),
    ];
    const legF = txt(vR, X1, 596, "", "ctx-nota", "end");
    // Vista 2: o mapa, com o grupo de Diego e Elisa em destaque.
    const vM = el("g", { class: "ctx-vista ctx-mapa-v" }, svg);
    const m = mapa(vM, { cursos: false });
    m.ligs.forEach((l) => l.classList.add("on"));
    colorir(m.nos);
    Object.values(m.manchas).forEach((x) => x.classList.add("on"));
    return (p) => {
      vR.classList.toggle("on", p <= 1);
      vM.classList.toggle("on", p >= 2);
      mk.forEach((k) => {
        k.style.transform = `translate(${p >= 1 ? k.dataset.x1 : k.dataset.x0}px, 0px)`;
        k.classList.toggle("on", p >= 1);
      });
      legF.textContent = p >= 1 ? "F = Felipe · traço = média da turma" : "";
      m.manchas.g1?.classList.toggle("pulsa", p === 2);
      ["S4", "S5"].forEach((id) => m.nos[id].classList.toggle("halo", p === 2));
      ["S1", "S2", "S6"].forEach((id) => m.nos[id].classList.toggle("apagado", p === 2));
    };
  }

  /* ═══════════════════ M9 · Do aluno ao grupo ═══════════════════ */
  function cenaPorque(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const v = [1, 2, 3, 4].map((k) => el("g", { class: `ctx-vista v${k}` }, svg));
    // 1: a nota sozinha "pousa" no Felipe, na beirada do grupo.
    const m = mapa(v[0], { cursos: false });
    m.ligs.forEach((l) => l.classList.add("on"));
    colorir(m.nos);
    Object.values(m.manchas).forEach((x) => x.classList.add("on"));
    const nota = el("g", { class: "ctx-nota66" }, v[0]);
    el("rect", { x: -62, y: -26, width: 124, height: 48, rx: 8 }, nota);
    txt(nota, 0, 8, `nota ${num(A.S6.nota_media, 0)}`, "ctx-nota66-t");
    // 2: um aluno se afastando do grupo (ilustração, sem dado).
    const cx = 470, cy = 300;
    const viz = [[-110, -70], [0, -120], [110, -60], [95, 70], [-20, 120], [-120, 60]].map(([dx, dy]) => [cx + dx, cy + dy]);
    const gl = el("g", {}, v[1]);
    viz.forEach(([x, y], i) => viz.forEach(([x2, y2], j) => { if (j > i && (j - i) % 2 === 1) el("line", { x1: x, y1: y, x2, y2, class: "ctx-ilu-l" }, gl); }));
    viz.forEach(([x, y]) => el("circle", { cx: x, cy: y, r: 18, class: "ctx-ilu-p" }, v[1]));
    const sai = el("g", { class: "ctx-sai" }, v[1]);
    const ls = [viz[0], viz[5]].map(([x, y]) => el("line", { x1: cx - 60, y1: cy, x2: x, y2: y, class: "ctx-ilu-l sai" }, sai));
    el("circle", { cx: cx - 60, cy, r: 18, class: "ctx-ilu-p sai" }, sai);
    txt(v[1], cx, 560, "ilustração, sem dado de aluno", "ctx-nota");
    // 3: 69% × 7% (Open University).
    const barra = (y, rotulo, pct, cls) => {
      txt(v[2], 120, y - 22, rotulo, "ctx-barra-t", "start");
      el("rect", { x: 120, y, width: 640, height: 44, class: "ctx-barra-fundo" }, v[2]);
      const b = el("rect", { x: 120, y, width: 6.4 * pct, height: 44, class: `ctx-barra ${cls}` }, v[2]);
      txt(v[2], 120 + 6.4 * pct + 16, y + 32, `${pct}%`, "ctx-barra-n", "start");
      return b;
    };
    txt(v[2], 120, 110, "Reprovaram ou desistiram, por grupo encontrado pelo sistema", "ctx-regua-t", "start");
    barra(210, "«Pouco engajados»", 69, "b-alto");
    barra(360, "«Engajamento moderado»", 7, "b-baixo");
    txt(v[2], 120, 470, "Open University (base pública e anônima), turma BBB 2013J", "ctx-nota", "start");
    // 4: a referência do grupo, monitora natural (turma da demonstração).
    const centro = [450, 300];
    const membros = [[-170, -110], [10, -170], [180, -100], [190, 90], [0, 160], [-180, 80]].map(([dx, dy]) => [centro[0] + dx, centro[1] + dy]);
    membros.forEach(([x, y]) => {
      const ang = Math.atan2(y - centro[1], x - centro[0]);
      el("line", { x1: centro[0] + 44 * Math.cos(ang), y1: centro[1] + 44 * Math.sin(ang), x2: x - 26 * Math.cos(ang), y2: y - 26 * Math.sin(ang), class: "ctx-seta", "marker-end": "url(#ctx-ponta)" }, v[3]);
      forma(el("g", { transform: `translate(${x} ${y})` }, v[3]), 0, 18, COR[0]);
    });
    const defs = el("defs", {}, svg);
    const mk = el("marker", { id: "ctx-ponta", viewBox: "0 0 10 10", refX: 8, refY: 5, markerWidth: 7, markerHeight: 7, orient: "auto-start-reverse" }, defs);
    el("path", { d: "M0 0 L10 5 L0 10 Z", fill: TINTA }, mk);
    const ref = el("g", { transform: `translate(${centro[0]} ${centro[1]})` }, v[3]);
    forma(ref, 0, 34, COR[0], TINTA, 3);
    txt(ref, 0, 9, C.demo.apoio.nome[0], "ctx-ini");
    txt(v[3], centro[0], 520, `${C.demo.apoio.nome}: monitora natural do próprio grupo`, "ctx-regua-t");
    txt(v[3], centro[0], 556, "turma da demonstração (outra turma, nomes inventados)", "ctx-nota");
    return (p) => {
      v.forEach((g, i) => g.classList.toggle("on", p === i + 1 || (p === 0 && i === 0)));
      nota.classList.toggle("pousou", p >= 1);
      m.nos.S6.classList.toggle("halo", p === 1);
      sai.classList.toggle("longe", p >= 2);
      v[2].classList.toggle("cresce", p >= 3);
      svg.classList.toggle("some-tudo", p >= 5);
    };
  }

  /* ═══════════════════ M11 · O que é um grafo ═══════════════════ */
  function cenaGrafo(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    // Um mapa de metrô genérico: 9 estações sem nome, três linhas com cores da paleta.
    const EST = { m1: [110, 300], m2: [250, 300], m3: [390, 300], m4: [530, 300], m5: [700, 300], m6: [530, 110], m7: [530, 480], m8: [250, 480], m9: [700, 480] };
    const LINHAS = [
      [COR[4], ["m1", "m2", "m3", "m4", "m5"]],
      [COR[1], ["m6", "m4", "m7"]],
      [COR[2], ["m2", "m8", "m7", "m9", "m5"]],
    ];
    const gMetro = el("g", { class: "ctx-metro" }, svg);
    const segs = [];
    LINHAS.forEach(([cor, est]) => {
      for (let i = 0; i < est.length - 1; i++) {
        const [a, b] = [EST[est[i]], EST[est[i + 1]]];
        const l = el("line", { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: "ctx-trilho" }, gMetro);
        l.style.setProperty("--cor", cor);
        segs.push(l);
      }
    });
    // Destino de cada estação no passo 3: o grafo bipartido do exemplo.
    const DEST = { m1: ["S6"], m2: ["S1"], m3: ["S2"], m4: ["S3"], m5: ["S4"], m6: ["S5"], m7: ["DA"], m8: ["DB"], m9: ["DC"] };
    const gBip = el("g", { class: "ctx-bipg" }, svg);
    T.matriculas.forEach((mt) => {
      const [x1, y1] = P.POS_BIP[mt.aluno], [x2, y2] = P.DISC[mt.disciplina];
      el("line", { x1: x1 + 26, y1, x2: x2 - 60, y2, class: `ctx-mat-bip a-${mt.aluno} d-${mt.disciplina}` }, gBip);
    });
    const gEst = el("g", {}, svg);
    const ests = Object.entries(EST).map(([k, p]) => {
      const g = el("g", { class: "ctx-est" }, gEst);
      const id = DEST[k][0];
      const ehAluno = id.startsWith("S");
      el("circle", { r: ["m2", "m4", "m5", "m7"].includes(k) ? 15 : 11, class: "ctx-est-metro" }, g);
      el("circle", { r: 9, class: "ctx-est-no" }, g);
      const vira = el("g", { class: "ctx-est-vira" }, g);
      if (ehAluno) {
        forma(vira, 0, 24, COR[0]);
        txt(vira, 0, 8, nome(id)[0], "ctx-ini");
        txt(vira, -40, 7, nome(id), "ctx-nome", "end");
      } else {
        el("rect", { x: -58, y: -24, width: 116, height: 48, rx: 10, class: "ctx-disc" }, vira);
        txt(vira, 0, 7, C.disciplinas[id][1], "ctx-disc-t");
      }
      g.dataset.de = k; g.dataset.para = id;
      mover(g, p);
      return { g, de: p, para: ehAluno ? P.POS_BIP[id] : P.DISC[id] };
    });
    const ann = el("g", { class: "ctx-anot" }, svg);
    const no = pilula(ann, 390, 238, "nó", "ctx-pil-def");
    const aresta = pilula(ann, 180, 360, "aresta", "ctx-pil-def");
    const pesoT = pilula(ann, 615, 362, "peso: 3", "ctx-pil-peso");
    const cab = el("g", { class: "ctx-cab-bip" }, svg);
    txt(cab, 190, 26, "alunos", "ctx-cab");
    txt(cab, 730, 26, "disciplinas", "ctx-cab");
    return (p) => {
      svg.classList.toggle("vazio", p === 0);
      svg.classList.toggle("metro", p <= 1);
      svg.classList.toggle("abstrato", p === 2);
      svg.classList.toggle("bip", p >= 3);
      svg.classList.toggle("destaca", p >= 4);
      ests.forEach((e) => mover(e.g, p >= 3 ? e.para : e.de));
      no.classList.toggle("on", p === 2);
      aresta.classList.toggle("on", p === 2);
      pesoT.classList.toggle("on", p === 2);
    };
  }

  /* ═══════════════════ M12 · A régua do z ═══════════════════ */
  function cenaEscoreZ(svg) {
    svg.setAttribute("viewBox", "0 0 960 660");
    const p1 = el("g", { class: "ctx-zp z1" }, svg);
    const X0 = 70, X1 = 890, X = (v) => X0 + ((v - 40) / 60) * (X1 - X0);
    txt(p1, X0, 30, "Exemplo de conta · média 70, passo típico de 10 pontos", "ctx-regua-t", "start");
    el("rect", { x: X(60), y: 64, width: X(80) - X(60), height: 56, class: "ctx-faixa f1" }, p1);
    el("rect", { x: X(50), y: 64, width: X(60) - X(50), height: 56, class: "ctx-faixa f2" }, p1);
    el("rect", { x: X(80), y: 64, width: X(90) - X(80), height: 56, class: "ctx-faixa f2" }, p1);
    el("line", { x1: X0, y1: 120, x2: X1, y2: 120, class: "ctx-regua" }, p1);
    [40, 50, 60, 70, 80, 90, 100].forEach((v) => {
      el("line", { x1: X(v), y1: 113, x2: X(v), y2: 127, class: "ctx-regua" }, p1);
      txt(p1, X(v), 152, String(v), "ctx-nota");
    });
    txt(p1, X(70), 188, "z = 0", "ctx-z");
    [[60, "−1"], [80, "+1"], [50, "−2"], [90, "+2"]].forEach(([v, z]) => txt(p1, X(v), 188, z, "ctx-z leve"));
    el("line", { x1: X(70), y1: 52, x2: X(70), y2: 132, class: "ctx-media-l" }, p1);
    const marca = (v, rot, cls) => {
      const g = el("g", { class: `ctx-zm ${cls}`, transform: `translate(${X(v)} 92)` }, p1);
      forma(g, 0, 14, cls === "acima" ? COR[4] : COR[5]);
      txt(g, 0, -26, rot, "ctx-zm-t");
    };
    marca(90, "90 → z = +2", "acima");
    marca(60, "60 → z = −1", "abaixo");
    // 2: as três medidas e os pesos fixos.
    const p2 = el("g", { class: "ctx-zp z2", transform: "translate(0 250)" }, svg);
    txt(p2, X0, 20, "O sistema faz a conta em três medidas e soma com pesos fixos", "ctx-regua-t", "start");
    const pesos = [["carga", "quantas disciplinas", 0.35, COR[0]], ["desempenho", "nota frente à disciplina", 0.35, COR[1]], ["vínculo", "ligação com o grupo", 0.3, COR[2]]];
    let x = X0;
    pesos.forEach(([rot, sub, w, cor]) => {
      const larg = (X1 - X0) * w;
      const r = el("rect", { x: x + 2, y: 46, width: larg - 4, height: 52, rx: 6, class: "ctx-peso-b" }, p2);
      r.style.setProperty("--cor", cor);
      txt(p2, x + larg / 2, 80, `${rot} · ${num(w * 100, 0)}%`, "ctx-peso-t");
      txt(p2, x + larg / 2, 126, sub, "ctx-nota");
      x += larg;
    });
    // 3: a régua do risco, com os cortes e o Felipe.
    const p3 = el("g", { class: "ctx-zp z3", transform: "translate(0 440)" }, svg);
    const R = (v) => X0 + v * (X1 - X0);
    txt(p3, X0, 20, "Risco, de 0 a 1 (cortes fixos)", "ctx-regua-t", "start");
    [[0, 0.25, "sem sinais", "f0"], [0.25, 0.5, "em atenção", "f1"], [0.5, 1, "risco alto", "f2"]].forEach(([a, b, rot, cls]) => {
      el("rect", { x: R(a), y: 50, width: R(b) - R(a), height: 48, class: `ctx-risco ${cls}` }, p3);
      txt(p3, (R(a) + R(b)) / 2, 82, rot, "ctx-risco-t");
    });
    [0, 0.25, 0.5, 1].forEach((v) => txt(p3, R(v), 126, num(v, 2), "ctx-nota"));
    const fel = el("g", { class: "ctx-zfel", transform: `translate(${R(A.S6.risco)} 74)` }, p3);
    el("line", { x1: 0, y1: -40, x2: 0, y2: 40, class: "ctx-media-l forte" }, fel);
    txt(fel, 0, 74, `Felipe · ${num(A.S6.risco, 2)}`, "ctx-zm-t");
    return (p) => {
      p1.classList.toggle("on", p >= 1);
      p2.classList.toggle("on", p >= 2);
      p3.classList.toggle("on", p >= 3);
    };
  }

  /* ═══════════════════ M13 · O dicionário ═══════════════════ */
  function cenaDicionario(svg) {
    svg.setAttribute("viewBox", "0 0 900 620");
    const m = mapa(svg, { cursos: false });
    m.ligs.forEach((l) => l.classList.add("on"));
    const pos = P.POS_PROJ;
    const extra = m.camadas.extra;
    const meio = (u, v) => [(pos[u][0] + pos[v][0]) / 2, (pos[u][1] + pos[v][1]) / 2];
    const [mx, my] = meio("S1", "S3");
    const anots = [
      pilula(extra, pos.S1[0], pos.S1[1] - 62, "nó"),
      pilula(extra, mx + 58, my - 18, "aresta"),
      pilula(extra, mx + 58, my - 18, `peso ${num(RA[chave("S1", "S3")], 2)}`),
      pilula(extra, 720, 312, "comunidade"),
      pilula(extra, pos.S3[0], pos.S3[1] - 62, "maior intermediação"),
      pilula(extra, pos.S6[0] + 20, pos.S6[1] - 62, "z negativo"),
    ];
    const ligAC = m.ligs.find((l) => chave(l.dataset.u, l.dataset.v) === "S1-S3");
    return (p) => {
      colorir(m.nos, p >= 4);
      Object.values(m.manchas).forEach((x) => x.classList.toggle("on", p >= 4));
      anots.forEach((a, i) => a.classList.toggle("on", p === i + 1));
      m.nos.S1.classList.toggle("halo", p === 1);
      ligAC?.classList.toggle("realce", p === 2 || p === 3);
      m.nos.S3.classList.toggle("halo", p === 5);
      m.nos.S6.classList.toggle("halo", p === 6);
      Object.values(m.nos).forEach((g) => g.classList.toggle("neutro", p < 4));
    };
  }

  /* ═══════════════════ FILMES ═══════════════════ */

  /** M1 · Linha do tempo de um aluno que some (ILUSTRATIVA: nenhum dado de aluno real). */
  function seqAlunoSome(svg) {
    svg.setAttribute("viewBox", "0 0 1600 420");
    const X0 = 110, X1 = 1500, Y = 250;
    const W = (s) => X0 + ((s - 1) / 15) * (X1 - X0);
    el("line", { x1: X0, y1: Y, x2: X1, y2: Y, class: "ctx-regua grossa" }, svg);
    for (let s = 1; s <= 16; s++) {
      el("line", { x1: W(s), y1: Y - 8, x2: W(s), y2: Y + 8, class: "ctx-regua" }, svg);
      txt(svg, W(s), Y + 40, s === 1 ? "sem. 1" : String(s), "ctx-nota");
    }
    const faixa = el("rect", { x: W(3) - 20, y: Y - 130, width: 0, height: 200, rx: 12, class: "ctx-sinais" }, svg);
    const faixaT = txt(svg, (W(3) + W(9)) / 2, Y - 142, "os sinais estavam aqui", "ctx-sinais-t");
    const EV = [[3, "falta"], [5, "falta de novo"], [7, "não entrega um trabalho"], [9, "para de acessar o ambiente virtual"], [14, "pede trancamento"]];
    const eventos = EV.map(([s, rot], i) => {
      const g = el("g", { transform: `translate(${W(s)} ${Y})` }, svg);
      const cima = i % 2 === 0;
      el("line", { x1: 0, y1: 0, x2: 0, y2: cima ? -70 : 70, class: "ctx-ev-l" }, g);
      el("circle", { r: 7, class: "ctx-ev-p" }, g);
      txt(g, 0, cima ? -82 : 96, rot, "ctx-ev-t");
      return { g, s };
    });
    const fim = el("g", { transform: `translate(${W(16)} ${Y})` }, svg);
    el("rect", { x: -14, y: -14, width: 28, height: 28, rx: 5, class: "ctx-fim-p" }, fim);
    txt(fim, 0, -40, "a instituição percebe aqui", "ctx-fim-t", "end");
    txt(fim, 0, -14 - 50, "nota final", "ctx-nota", "end");
    const aluno = el("g", {}, svg);
    el("circle", { r: 22, class: "ctx-aluno" }, aluno);
    const t0 = 0.6, t1 = 8.6;
    return {
      duracao: 12,
      legendas: [
        [0, "Um semestre de um aluno, semana a semana."],
        [1.6, "Primeiro ele <b>falta</b>. Depois falta de novo."],
        [4.0, "Deixa de entregar um trabalho e <b>para de acessar</b> o ambiente virtual."],
        [7.0, "Perto do fim, pede o <b>trancamento</b>."],
        [8.8, "A instituição costuma perceber aqui: quando sai a nota final."],
        [10.0, "Mas os <b>sinais estavam aqui</b>, semanas antes."],
      ],
      render(t) {
        const s = 1 + 15 * seg(t, t0, t1, (x) => x);
        const passados = EV.filter(([e]) => s >= e).length;
        aluno.setAttribute("transform", `translate(${W(s)} ${Y})`);
        aluno.setAttribute("opacity", String(1 - 0.15 * passados));
        eventos.forEach(({ g, s: e }) => g.setAttribute("opacity", String(seg(t, t0 + ((e - 1) / 15) * (t1 - t0), t0 + ((e - 1) / 15) * (t1 - t0) + 0.4))));
        fim.setAttribute("opacity", String(seg(t, 8.6, 9.2)));
        const f = seg(t, 10, 11.2);
        const larg = (W(9) - W(3) + 40) * f;
        set(faixa, { x: W(9) + 20 - larg, width: larg, opacity: f > 0 ? 1 : 0 });
        faixaT.setAttribute("opacity", String(seg(t, 10.8, 11.4)));
      },
    };
  }

  /** M2 · De cada 100 que entraram em 2015 (Inep, 2026). */
  function seqInep(svg) {
    svg.setAttribute("viewBox", "0 0 1000 540");
    // Ordem fixa e "embaralhada" de saída dos pontos (permutação com semente).
    const ordem = [...Array(100).keys()];
    let s = 7;
    for (let i = 99; i > 0; i--) { s = (s * 9301 + 49297) % 233280; const j = Math.floor((s / 233280) * (i + 1)); [ordem[i], ordem[j]] = [ordem[j], ordem[i]]; }
    const rank = new Array(100); ordem.forEach((p, k) => { rank[p] = k; });
    const pontos = [...Array(100).keys()].map((i) => {
      const x = 46 + (i % 10) * 44, y = 46 + Math.floor(i / 10) * 44;
      const g = el("g", { transform: `translate(${x} ${y})` }, svg);
      const c = el("circle", { r: 15, class: "ctx-pct" }, g);
      return { g, c, x, y, k: rank[i] };
    });
    const marcos = I.desistencia;
    const tAno = [1.2, 3.0, 4.8, 7.4];
    const X = 560;
    const ano = txt(svg, X, 70, "", "ctx-ano", "start");
    const grande = txt(svg, X, 230, "", "ctx-grande", "start");
    const sub = txt(svg, X, 284, "", "ctx-grande-sub", "start");
    const fimT = txt(svg, X, 360, "", "ctx-grande-sub2", "start");
    const leg = el("g", { transform: `translate(${X} 430)` }, svg);
    const item = (y, cls, texto) => {
      const g = el("g", { transform: `translate(0 ${y})` }, leg);
      el(cls === "cursa" ? "rect" : "circle", cls === "cursa" ? { x: -11, y: -11, width: 22, height: 22, rx: 4, class: `ctx-pct ${cls}` } : { r: 11, class: `ctx-pct ${cls}` }, g);
      txt(g, 24, 8, texto, "ctx-nota", "start");
      return g;
    };
    const legs = [item(0, "saiu", "deixou o curso em que ingressou"), item(36, "concluiu", "concluiu"), item(72, "cursa", "ainda cursava")];
    const pctEm = (t) => {
      let atual = 0;
      marcos.forEach((m, i) => { if (t >= tAno[i]) atual = m.pct; });
      return atual;
    };
    return {
      duracao: 12,
      legendas: [
        [0, `Cada ponto é <b>1%</b> dos alunos que entraram na graduação em ${I.turma}.`],
        [tAno[0], `No primeiro ano, <b>${marcos[0].pct}%</b> já tinham deixado o curso.`],
        [tAno[1], `Até o segundo ano, <b>${marcos[1].pct}%</b>.`],
        [tAno[2], `Até o terceiro, <b>${marcos[2].pct}%</b>.`],
        [tAno[3], `Dez anos depois, <b>${marcos[3].pct}%</b> tinham deixado o curso em que ingressaram.`],
        [9.4, `${I.concluiram}% concluíram; ${I.cursando}% ainda cursava.`],
      ],
      render(t) {
        const anoAtual = marcos.filter((m, i) => t >= tAno[i]).pop();
        const intervalo = t >= tAno[2] + 1.4 && t < tAno[3];
        ano.textContent = t < tAno[0] ? `Turma que entrou em ${I.turma}` : intervalo ? "…" : `Até o ${anoAtual.ano}º ano`;
        // Número grande: conta do valor anterior ao novo, em 0,6 s.
        let alvo = 0, antes = 0, tm = 0;
        marcos.forEach((m, i) => { if (t >= tAno[i]) { antes = alvo; alvo = m.pct; tm = tAno[i]; } });
        const mostra = Math.round(lerp(antes, alvo, seg(t, tm, tm + 0.6, easeOut)));
        grande.textContent = `${mostra}%`;
        sub.textContent = t < tAno[0] ? "" : "deixaram o curso";
        const fimF = seg(t, 9.4, 10.6);
        fimT.textContent = fimF > 0 ? `${I.concluiram}% concluíram · ${I.cursando}% ainda cursava` : "";
        fimT.setAttribute("opacity", String(fimF));
        const saiu = (k) => {
          // Quando o ponto de posição k na ordem sai: no primeiro ano em que pct > k.
          for (let i = 0; i < marcos.length; i++) if (k < marcos[i].pct) return tAno[i] + 0.05 * (k - (i ? marcos[i - 1].pct : 0)) / 2;
          return Infinity;
        };
        pontos.forEach((pt) => {
          const ts = saiu(pt.k);
          const f = Number.isFinite(ts) ? seg(t, ts, ts + 0.5) : 0;
          const conclui = pt.k >= marcos[marcos.length - 1].pct && pt.k < 100 - I.cursando;
          const cursa = pt.k >= 100 - I.cursando;
          const ff = seg(t, 9.4 + 0.012 * (pt.k - 60), 9.9 + 0.012 * (pt.k - 60));
          pt.g.setAttribute("transform", `translate(${pt.x + 5 * f} ${pt.y + 5 * f})`);
          pt.c.setAttribute("class", `ctx-pct ${f > 0.5 ? "saiu" : ff > 0.5 ? (cursa ? "cursa" : conclui ? "concluiu" : "") : ""}`);
          pt.c.setAttribute("r", String(f > 0.5 ? 13 : 15));
        });
        legs.forEach((g, i) => g.setAttribute("opacity", String(i === 0 ? seg(t, tAno[0], tAno[0] + 0.5) : fimF)));
      },
    };
  }

  /** M3 · A lista vira mapa. */
  function seqLista(svg) {
    svg.setAttribute("viewBox", "0 0 1200 540");
    const ordemAluno = ["S1", "S2", "S3", "S4", "S5", "S6"];
    const mats = [...T.matriculas].sort((a, b) => ordemAluno.indexOf(a.aluno) - ordemAluno.indexOf(b.aluno) || a.disciplina.localeCompare(b.disciplina));
    const tab = el("g", {}, svg);
    const cab = el("g", {}, tab);
    txt(cab, 24, 26, "ALUNO", "m-cab", "start");
    txt(cab, 132, 26, "DISCIPLINA", "m-cab", "start");
    txt(cab, 476, 26, "NOTA", "m-cab", "end");
    const linhas = mats.map((m, i) => {
      const g = el("g", { class: "m-linha" }, tab);
      el("rect", { x: 10, y: 40 + i * 49, width: 480, height: 43, rx: 6, class: "m-linha-fundo" }, g);
      txt(g, 24, 69 + i * 49, nome(m.aluno), "m-cel ctx-cel", "start");
      txt(g, 132, 69 + i * 49, disc(m.disciplina), "m-cel ctx-cel", "start");
      txt(g, 476, 69 + i * 49, num(m.nota, 0), "m-cel n ctx-cel", "end");
      return { g, m, y: 61 + i * 49 };
    });
    const DX = 440, DY = -14;
    const pos = Object.fromEntries(Object.entries(P.POS_PROJ).map(([k, [x, y]]) => [k, [x + DX, y + DY]]));
    const gl = el("g", {}, svg);
    const ligs = PARES.map(([u, v]) => ({ l: linha(gl, pos[u], pos[v], P.larguraRA(RA[chave(u, v)]), "filme"), u, v }));
    const origem = Object.fromEntries(ordemAluno.map((a) => [a, [60, linhas.find((l) => l.m.aluno === a).y]]));
    const nos = Object.fromEntries(ordemAluno.map((a) => {
      const g = el("g", { class: "ctx-a filme neutro" }, svg);
      el("circle", { r: 37, class: "ctx-halo" }, g);
      forma(g, 0, 24, PAPEL).classList.add("ctx-f0");
      txt(g, 0, 8, nome(a)[0], "ctx-ini");
      txt(g, 0, 58, nome(a), "ctx-nome");
      return [a, g];
    }));
    return {
      duracao: 15,
      legendas: [
        [0, "A lista que a instituição já tem: uma linha por matrícula."],
        [2.6, "Numa lista, o <b>Felipe</b> é só mais uma linha. Nada chama a atenção."],
        [5.4, "Agora, em vez de ler linha por linha, olhamos para as <b>relações</b>: quem estuda com quem."],
        [8.6, "Cada linha liga dois alunos que cursam a mesma disciplina."],
        [11.4, "No mapa, dá para ver o que a lista esconde: o Felipe está <b>quase sozinho</b>, na beirada."],
      ],
      render(t) {
        cab.setAttribute("opacity", String(seg(t, 0, 0.4) * (1 - seg(t, 5.6, 6.4))));
        linhas.forEach(({ g, m }, i) => {
          const a = seg(t, 0.2 + i * 0.12, 0.7 + i * 0.12, easeOut);
          const fora = seg(t, 5.6 + i * 0.05, 6.6 + i * 0.05);
          g.setAttribute("opacity", String(a * (1 - fora)));
          g.setAttribute("transform", `translate(${lerp(-20, 0, a)} 0)`);
          const pisca = m.aluno === "S6" && t > 2.8 && t < 5.2 ? 0.5 + 0.5 * Math.sin((t - 2.8) * 6) : 0;
          g.classList.toggle("acesa", pisca > 0.5);
        });
        ordemAluno.forEach((a, i) => {
          const ap = seg(t, 5.8 + i * 0.08, 6.4 + i * 0.08, easeBack);
          const mv = seg(t, 6.4 + i * 0.1, 8.2 + i * 0.1);
          const [x0, y0] = origem[a], [x1, y1] = pos[a];
          nos[a].setAttribute("transform", `translate(${lerp(x0, x1, mv)} ${lerp(y0, y1, mv)}) scale(${ap})`);
          const halo = a === "S6" ? seg(t, 11.6, 12.2) : 0;
          nos[a].querySelector(".ctx-halo").setAttribute("style", `opacity:${halo}`);
        });
        ligs.forEach(({ l }, i) => {
          const a = seg(t, 8.6 + i * 0.16, 9.6 + i * 0.16);
          l.setAttribute("style", `--w:${l.style.getPropertyValue("--w")}; stroke-dashoffset:${1 - a}`);
        });
      },
    };
  }

  /** M10 · Entra a lista, sai o mapa. */
  function seqSolucao(svg) {
    svg.setAttribute("viewBox", "0 0 1600 470");
    const ordemAluno = ["S1", "S2", "S3", "S4", "S5", "S6"];
    const mats = [...T.matriculas].sort((a, b) => ordemAluno.indexOf(a.aluno) - ordemAluno.indexOf(b.aluno)).slice(0, 6);
    const linhas = mats.map((m, i) => {
      const g = el("g", { class: "m-linha" }, svg);
      el("rect", { x: 0, y: -22, width: 340, height: 44, rx: 6, class: "m-linha-fundo" }, g);
      txt(g, 14, 8, `${nome(m.aluno)} · ${C.disciplinas[m.disciplina][1]} · ${num(m.nota, 0)}`, "m-cel ctx-cel", "start");
      return { g, y: 90 + i * 56 };
    });
    txt(svg, 150, 40, "ENTRA", "ctx-cab");
    txt(svg, 600, 40, "EDUGRAPH", "ctx-cab");
    txt(svg, 1010, 40, "SAI", "ctx-cab");
    const marca = el("g", { transform: "translate(600 235)" }, svg);
    const fM = [forma(el("g", { transform: "translate(-58 0)" }, marca), 0, 26, COR[0]), forma(el("g", {}, marca), 1, 25, COR[1]), forma(el("g", { transform: "translate(58 0)" }, marca), 2, 22, COR[2])];
    const esc = 0.62, DX = 760, DY = 40;
    const pos = Object.fromEntries(Object.entries(P.POS_PROJ).map(([k, [x, y]]) => [k, [DX + x * esc, DY + y * esc]]));
    const gm = el("g", {}, svg);
    const mm = el("g", {}, gm);
    mancha(mm, ["S1", "S2", "S3", "S6"], pos, "m0 on", 40);
    mancha(mm, ["S4", "S5"], pos, "m1 on", 40);
    const ligs = PARES.map(([u, v]) => linha(gm, pos[u], pos[v], P.larguraRA(RA[chave(u, v)]) * 0.7, "filme"));
    const nos = ordemAluno.map((a) => {
      const g = el("g", { transform: `translate(${pos[a][0]} ${pos[a][1]})` }, gm);
      forma(g, grupoDe(a), grupoDe(a) ? 15 : 16, COR[grupoDe(a)]);
      return g;
    });
    const TAGS = ["grupos com nome", "o papel de cada aluno", "quem merece atenção, e por quê", "quem se destaca, e por quê"];
    const tags = TAGS.map((t, i) => {
      const g = el("g", { transform: `translate(1300 ${110 + i * 64})` }, svg);
      el("rect", { x: -16, y: -24, width: 300, height: 46, rx: 23, class: "ctx-tag" }, g);
      txt(g, -2, 6, `✓ ${t}`, "ctx-tag-t", "start");
      return g;
    });
    const selo = el("g", { transform: "translate(1150 430)" }, svg);
    el("rect", { x: -230, y: -24, width: 460, height: 46, rx: 23, class: "ctx-selo" }, selo);
    txt(selo, 0, 7, "e mostra como chegou ao resultado", "ctx-selo-t");
    return {
      duracao: 10,
      legendas: [
        [0, "<b>Entra</b> a lista de matrículas (e, quando há, os acessos ao ambiente virtual)."],
        [3.4, "<b>Sai</b> o mapa da turma…"],
        [5.4, "…com os grupos, o papel de cada aluno, quem merece atenção e quem se destaca, <b>sempre com o motivo</b>."],
        [8.6, "E o sistema mostra, passo a passo, <b>como chegou</b> ao resultado."],
      ],
      render(t) {
        linhas.forEach(({ g, y }, i) => {
          const a = seg(t, 0.2 + i * 0.3, 0.6 + i * 0.3, easeOut);
          const vai = seg(t, 1.6 + i * 0.25, 2.8 + i * 0.25);
          const x = lerp(lerp(-40, 30, a), 470, vai), yy = lerp(y, 235, vai);
          g.setAttribute("transform", `translate(${x} ${yy}) scale(${1 - 0.6 * vai})`);
          g.setAttribute("opacity", String(a * (1 - seg(t, 2.4 + i * 0.25, 3.0 + i * 0.25))));
        });
        const pulso = 1 + 0.12 * Math.sin(clamp((t - 2.2) / 1.6) * Math.PI);
        fM.forEach((f, i) => f.parentNode.setAttribute("transform", `translate(${(i - 1) * 58} 0) scale(${pulso})`));
        marca.setAttribute("opacity", String(seg(t, 0, 0.5)));
        const ap = seg(t, 3.4, 4.4);
        ligs.forEach((l, i) => l.setAttribute("style", `--w:${l.style.getPropertyValue("--w")}; stroke-dashoffset:${1 - seg(t, 3.6 + i * 0.1, 4.4 + i * 0.1)}`));
        nos.forEach((n, i) => n.setAttribute("opacity", String(seg(t, 3.4 + i * 0.08, 3.8 + i * 0.08))));
        mm.setAttribute("opacity", String(seg(t, 4.6, 5.4)));
        gm.setAttribute("opacity", String(ap > 0 ? 1 : 0));
        tags.forEach((g, i) => {
          const a = seg(t, 5.5 + i * 0.7, 6.0 + i * 0.7, easeBack);
          g.setAttribute("opacity", String(clamp(a)));
          g.setAttribute("transform", `translate(${1300 + 20 * (1 - a)} ${110 + i * 64})`);
        });
        selo.setAttribute("opacity", String(seg(t, 8.6, 9.2)));
      },
    };
  }

  /* ═══════════════════ Ligação com o deck ═══════════════════ */
  window.EDUGRAPH_SEQS = Object.assign(window.EDUGRAPH_SEQS || {}, {
    alunoSome: seqAlunoSome,
    inep: seqInep,
    lista: seqLista,
    solucao: seqSolucao,
  });

  const CENAS = {
    ligacao: cenaLigacao,
    forca: cenaForca,
    turmas: cenaTurmas,
    comunidades: cenaComunidades,
    grupos: cenaGrupos,
    papeis: cenaPapeis,
    atencao: cenaAtencao,
    porque: cenaPorque,
    grafo: cenaGrafo,
    escoreZ: cenaEscoreZ,
    dicionario: cenaDicionario,
  };

  window.iniciarContexto = function iniciarContexto(deck) {
    const cenas = [...document.querySelectorAll("svg[data-ctx]")].map((svg) => {
      svg.classList.add("ctx");
      const atualizar = CENAS[svg.dataset.ctx](svg);
      atualizar(0);
      return { svg, slide: svg.closest(".slide"), atualizar };
    });
    deck.aoMudar((e) => {
      if (e.tipo !== "slide") return;
      const atual = deck.slideAtual();
      cenas.forEach((c) => { if (c.slide === atual) c.atualizar(deck.passo); });
    });
  };

  /* Textos do sistema dentro do HTML: [data-sistema="caminho.no.objeto"]. */
  window.preencherSistema = function preencherSistema() {
    document.querySelectorAll("[data-sistema]").forEach((n) => {
      const valor = n.dataset.sistema.split(".").reduce((o, k) => (o == null ? o : o[k]), D);
      if (Array.isArray(valor)) n.innerHTML = valor.map((v) => `<span>“${v}”</span>`).join("");
      else if (typeof valor === "number") n.textContent = num(valor, Number(n.dataset.casas ?? 0));
      else if (valor != null) n.textContent = String(valor);
    });
    // A tabela dos seis alunos (nomes e cursos: desenho; matrículas e notas: tiny_v1).
    document.querySelectorAll("[data-tabela-seis]").forEach((tb) => {
      tb.innerHTML = P.ALUNOS.map((id) => {
        const ms = T.matriculas.filter((m) => m.aluno === id).sort((x, y) => x.disciplina.localeCompare(y.disciplina));
        const ds = ms.map((m) => `${C.disciplinas[m.disciplina][1]} (${num(m.nota, 0)})`).join(", ");
        return `<tr><td>${nome(id)}</td><td>${C.cursos[id]}</td><td class="disc">${ds}</td></tr>`;
      }).join("");
    });
    // Números do Inep (js/contexto-dados.js).
    document.querySelectorAll("[data-inep]").forEach((n) => { n.textContent = String(I[n.dataset.inep]); });
    document.querySelectorAll("[data-inep-barra]").forEach((n) => { n.style.setProperty("--v", `${I[n.dataset.inepBarra]}%`); });
  };
})();
