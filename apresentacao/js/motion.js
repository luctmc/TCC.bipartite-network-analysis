/**
 * Motion design da apresentação — sem dependências, funciona offline.
 *
 * Cada sequência é uma função pura do tempo: `render(t)` desenha o quadro
 * do instante t. Isso dá, de graça, o que um vídeo renderizado daria
 * (tocar, pausar, voltar, arrastar a barra) com nitidez vetorial em
 * qualquer projetor e sem arquivo de vídeo para carregar.
 *
 * Todos os números e grafos vêm de js/dados.js (gerado do repositório) ou
 * de medições documentadas em VERIFICACAO.md. Só posições e tempos são
 * escolhas de direção.
 *
 * Sequências:
 *   abertura      capa: a marca vira a rede real de synthetic_v1
 *   encerramento  a rede volta a ser a marca
 *   metodo        "Do dado ao resultado", com tiny_v1 (pipeline)
 *   clique        "Por dentro de um clique": POST /lab/run até a tela
 *   acaso         "O teste contra o acaso": rede real × réplica nula
 */
(() => {
  const D = window.EDUGRAPH_DADOS;
  const NS = "http://www.w3.org/2000/svg";
  const COR = ["#56B4E9", "#E69F00", "#009E73", "#F0E442", "#0072B2", "#D55E00"];
  const TINTA = "#1a1915", PAPEL = "#fbfaf7";

  /* ——— Utilidades de tempo ——— */
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, f) => a + (b - a) * f;
  const easeIO = (x) => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const easeOut = (x) => 1 - Math.pow(1 - x, 3);
  const easeBack = (x) => { const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  /** Progresso 0→1 entre a e b, com curva. */
  const seg = (t, a, b, curva = easeIO) => curva(clamp((t - a) / (b - a)));
  const num = (v, c = 2) => v.toLocaleString("pt-BR", { minimumFractionDigits: c, maximumFractionDigits: c });
  const el = (tag, attrs = {}, pai) => {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, String(v));
    pai?.appendChild(e);
    return e;
  };
  const set = (e, attrs) => { for (const k in attrs) e.setAttribute(k, attrs[k]); };
  const reduzido = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function forma(g, tipo, r, cor, traco = TINTA, larg = 1.4) {
    if (tipo === 1) {
      const h = r * 1.18;
      return el("path", { d: `M0 ${-h} L${h} ${h * 0.78} L${-h} ${h * 0.78} Z`, fill: cor, stroke: traco, "stroke-width": larg, "stroke-linejoin": "round" }, g);
    }
    if (tipo === 2) return el("rect", { x: -r, y: -r, width: 2 * r, height: 2 * r, rx: r * 0.32, fill: cor, stroke: traco, "stroke-width": larg }, g);
    return el("circle", { r, fill: cor, stroke: traco, "stroke-width": larg }, g);
  }

  /* ═════════════ Player: tocar, pausar, arrastar, legendas ═════════════ */
  class Filme {
    constructor(raiz, seq) {
      this.raiz = raiz;
      this.seq = seq;
      this.t = 0;
      this.tocando = false;
      this.ultimo = 0;
      const ctr = document.createElement("div");
      ctr.className = "filme-controles";
      ctr.innerHTML = `<button type="button" class="filme-play" aria-label="Tocar ou pausar (K)"><span class="i-play">▶</span><span class="i-pausa">❚❚</span></button>
        <div class="filme-trilho"><input type="range" min="0" max="${seq.duracao * 100}" value="0" step="1" aria-label="Posição na sequência" /><div class="filme-marcos"></div></div>
        <span class="filme-tempo">0:00 / ${this.fmt(seq.duracao)}</span>`;
      this.legenda = document.createElement("p");
      this.legenda.className = "filme-legenda";
      this.legenda.setAttribute("aria-live", "polite");
      raiz.append(this.legenda, ctr);
      this.range = ctr.querySelector("input");
      this.tempo = ctr.querySelector(".filme-tempo");
      const marcos = ctr.querySelector(".filme-marcos");
      (seq.legendas || []).forEach(([a]) => {
        const m = document.createElement("i");
        m.style.left = `${(a / seq.duracao) * 100}%`;
        marcos.appendChild(m);
      });
      ctr.querySelector(".filme-play").addEventListener("click", () => this.alternar());
      this.range.addEventListener("input", () => { this.pausar(); this.ir(this.range.value / 100); });
      this.passo = this.passo.bind(this);
      this.ir(0);
    }
    fmt(s) { return `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, "0")}`; }
    ir(t) {
      this.t = clamp(t, 0, this.seq.duracao);
      this.seq.render(this.t);
      this.range.value = String(Math.round(this.t * 100));
      this.tempo.textContent = `${this.fmt(this.t)} / ${this.fmt(this.seq.duracao)}`;
      this.raiz.style.setProperty("--progresso", `${(this.t / this.seq.duracao) * 100}%`);
      const leg = (this.seq.legendas || []).filter(([a]) => a <= this.t + 0.001).pop();
      const html = leg ? leg[1] : "";
      if (this.legenda.dataset.html !== html) {
        this.legenda.dataset.html = html;
        this.legenda.classList.remove("troca");
        void this.legenda.offsetWidth;
        this.legenda.innerHTML = html;
        this.legenda.classList.add("troca");
      }
      this.seq.aoTempo?.(this.t);
      this.raiz.classList.toggle("terminou", this.t >= this.seq.duracao);
    }
    tocar() {
      if (this.t >= this.seq.duracao) this.ir(0);
      this.tocando = true;
      this.raiz.classList.add("tocando");
      this.ultimo = performance.now();
      requestAnimationFrame(this.passo);
    }
    pausar() { this.tocando = false; this.raiz.classList.remove("tocando"); }
    alternar() { (this.tocando ? this.pausar : this.tocar).call(this); }
    passo(agora) {
      if (!this.tocando) return;
      const dt = Math.min(0.1, (agora - this.ultimo) / 1000);
      this.ultimo = agora;
      this.ir(this.t + dt);
      if (this.t >= this.seq.duracao) return this.pausar();
      requestAnimationFrame(this.passo);
    }
  }

  /* ═════════════ Sequência: Do dado ao resultado (tiny_v1) ═════════════ */
  function seqMetodo(svg) {
    const T = D.tiny;
    svg.setAttribute("viewBox", "0 0 1040 560");
    const ALUNOS = ["S1", "S2", "S3", "S4", "S5", "S6"];
    const yA = (i) => 70 + i * 82;
    const POS_B = Object.fromEntries(ALUNOS.map((a, i) => [a, [470, yA(i)]]));
    const POS_D = { DA: [800, 150], DB: [800, 280], DC: [800, 410] };
    const POS_P = { S1: [560, 120], S2: [560, 440], S6: [400, 280], S3: [720, 280], S4: [930, 130], S5: [930, 430] };
    const final = T.louvain.membership;
    const grupoDe = (id) => (final[id] === final.S1 ? 0 : 1);

    // Tabela de matrículas (a "planilha").
    const tab = el("g", { class: "m-tab" }, svg);
    el("text", { x: 30, y: 46, class: "m-cab m-linha" }, tab).textContent = "aluno   disciplina   nota";
    const cabecalho = tab.querySelector(".m-cab");
    const linhas = T.matriculas.map((m, i) => {
      const g = el("g", { class: "m-linha" }, tab);
      el("rect", { x: 20, y: 64 + i * 46, width: 300, height: 38, rx: 6, class: "m-linha-fundo" }, g);
      el("text", { x: 34, y: 89 + i * 46, class: "m-cel" }, g).textContent = `Aluno ${m.aluno.slice(1)}`;
      el("text", { x: 150, y: 89 + i * 46, class: "m-cel" }, g).textContent = `Disc. ${m.disciplina.slice(1)}`;
      el("text", { x: 300, y: 89 + i * 46, class: "m-cel n", "text-anchor": "end" }, g).textContent = String(m.nota);
      return g;
    });
    // Arestas do bipartido.
    const gb = el("g", {}, svg);
    const mats = T.matriculas.map((m) => {
      const [x1, y1] = POS_B[m.aluno], [x2, y2] = POS_D[m.disciplina];
      return el("line", { x1: x1 + 20, y1, x2: x2 - 24, y2, class: "m-mat", pathLength: 1 }, gb);
    });
    // Disciplinas.
    const discs = Object.entries(POS_D).map(([d, [x, y]]) => {
      const g = el("g", { transform: `translate(${x} ${y})` }, svg);
      el("rect", { x: -24, y: -24, width: 48, height: 48, rx: 10, fill: COR[1], stroke: TINTA, "stroke-width": 1.6 }, g);
      el("text", { y: 8, class: "m-num", "text-anchor": "middle" }, g).textContent = d.slice(1);
      return g;
    });
    // Ligações da projeção.
    const gp = el("g", {}, svg);
    const ligs = T.simples.map(([u, v, w]) => {
      const [x1, y1] = POS_P[u], [x2, y2] = POS_P[v];
      return { e: el("line", { x1, y1, x2, y2, class: "m-lig", pathLength: 1, "stroke-width": w >= 2 ? 8 : 3 }, gp), u, v };
    });
    // Alunos (círculo branco → cor do grupo).
    const nos = Object.fromEntries(ALUNOS.map((a) => {
      const g = el("g", {}, svg);
      const anel = el("circle", { r: 34, class: "m-anel" }, g);
      const c = el("circle", { r: 20, fill: PAPEL, stroke: TINTA, "stroke-width": 1.6 }, g);
      const tri = forma(g, 1, 19, COR[1], TINTA, 1.6);
      el("text", { y: 7, class: "m-num", "text-anchor": "middle" }, g).textContent = a.slice(1);
      return [a, { g, c, tri, anel }];
    }));
    const placar = el("text", { x: 1010, y: 540, class: "m-placar", "text-anchor": "end" }, svg);

    const tMov = [8.9, 9.6, 10.3, 11.0];
    return {
      duracao: 16,
      legendas: [
        [0, "Tudo começa numa <b>planilha</b>: cada linha é uma matrícula — aluno, disciplina e nota."],
        [2.8, "Cada matrícula vira uma <b>ligação</b> entre aluno e disciplina: o <b>grafo bipartido</b>."],
        [5.6, "Na <b>projeção</b>, ligam-se os alunos que dividem disciplinas; quanto mais em comum, mais grossa a linha."],
        [8.6, "O <b>Louvain</b> move um aluno por vez para o grupo em que <i>Q</i> mais sobe: dois grupos, <i>Q</i> = 0,111."],
        [12, "A <b>intermediação</b> aponta o aluno 3: todo caminho até 4 e 5 passa por ele."],
        [14.4, "É o mesmo caminho que o edugraph percorre — com 6 alunos ou com 22.425."],
      ],
      marcos: [[0, 0], [2.8, 1], [5.6, 2], [8.6, 3], [12, 4]],
      render(t) {
        // Planilha
        linhas.forEach((g, i) => {
          const a = seg(t, 0.2 + i * 0.16, 0.7 + i * 0.16, easeOut);
          const fora = seg(t, 5.2, 6.2);
          const m = T.matriculas[i];
          const tLig = 2.9 + i * 0.22;
          const acesa = t >= tLig && t < tLig + 0.5 ? 1 : 0;
          g.setAttribute("opacity", (a * (1 - 0.85 * seg(t, 2.6, 3.4)) + acesa * 0.85 * seg(t, 2.6, 3.4)) * (1 - fora));
          g.setAttribute("transform", `translate(${lerp(-24, 0, a)} 0)`);
          g.classList.toggle("acesa", acesa === 1 && m);
        });
        cabecalho.setAttribute("opacity", seg(t, 0, 0.4) * (1 - seg(t, 5.2, 6.2)));
        // Bipartido
        mats.forEach((e, i) => {
          const a = seg(t, 2.9 + i * 0.22, 3.5 + i * 0.22);
          const fora = seg(t, 5.6, 6.6);
          set(e, { "stroke-dashoffset": 1 - a, opacity: 1 - fora });
        });
        discs.forEach((g, i) => {
          const a = seg(t, 2.6 + i * 0.12, 3.2 + i * 0.12, easeBack);
          const fora = seg(t, 5.6, 6.4);
          g.setAttribute("opacity", a * (1 - fora));
        });
        // Alunos: aparecem no bipartido, deslizam para a projeção.
        const mov = seg(t, 5.8, 7.4);
        ALUNOS.forEach((a, i) => {
          const n = nos[a];
          const ap = seg(t, 2.6 + i * 0.1, 3.2 + i * 0.1, easeBack);
          const [xb, yb] = POS_B[a], [xp, yp] = POS_P[a];
          const x = lerp(xb, xp, mov), y = lerp(yb, yp, mov);
          // Louvain: cor ao mover-se (rastro real).
          const k = T.louvain.movimentos.findIndex((m) => m.no === a);
          const dono = T.louvain.movimentos.find((m) => m.para === a);
          let cor = 0;
          if (k >= 0) cor = seg(t, tMov[k], tMov[k] + 0.4);
          else if (dono) cor = seg(t, tMov[T.louvain.movimentos.indexOf(dono)], tMov[T.louvain.movimentos.indexOf(dono)] + 0.4);
          const grupo = grupoDe(a);
          // Centralidade: o 3 cresce pela intermediação.
          const cres = a === "S3" ? 1 + 0.45 * seg(t, 12.1, 13, easeBack) : 1 - 0.18 * seg(t, 12.1, 13);
          n.g.setAttribute("transform", `translate(${x} ${y}) scale(${ap * cres})`);
          n.c.setAttribute("fill", grupo === 0 && cor > 0.5 ? COR[0] : PAPEL);
          n.c.setAttribute("opacity", grupo === 1 ? 1 - cor : 1);
          n.tri.setAttribute("opacity", grupo === 1 ? cor : 0);
          const ativo = k >= 0 && t >= tMov[k] - 0.15 && t < tMov[k] + 0.55;
          n.anel.setAttribute("opacity", ativo ? 1 : a === "S3" ? seg(t, 12.1, 12.6) : 0);
        });
        // Projeção
        ligs.forEach(({ e }, i) => {
          const a = seg(t, 6.6 + i * 0.12, 7.4 + i * 0.12);
          set(e, { "stroke-dashoffset": 1 - a, opacity: 1 - 0.55 * seg(t, 12.1, 12.8) });
        });
        // Placar de Q (rastro do Louvain)
        const feitos = tMov.filter((x) => t >= x).length;
        placar.textContent = t < 8.6 ? "" : feitos === 0 ? "6 grupos" : `movimento ${feitos} de 4 · Q = ${num(T.louvain.movimentos[feitos - 1].q, 3)}`;
        if (t >= 12) placar.textContent = `intermediação do aluno 3 = ${num(T.centralidade.intermediacao.S3, 2)}`;
      },
    };
  }

  /* ═════════════ Sequência: Por dentro de um clique ═════════════ */
  function seqClique(svg) {
    svg.setAttribute("viewBox", "0 0 1600 560");
    const caixa = (x, y, w, h, titulo, sub, cls = "") => {
      const g = el("g", { class: `c-caixa ${cls}`, transform: `translate(${x} ${y})` }, svg);
      el("rect", { width: w, height: h, rx: 14, class: "c-fundo" }, g);
      el("text", { x: 22, y: 40, class: "c-tit" }, g).textContent = titulo;
      el("text", { x: 22, y: 68, class: "c-sub" }, g).textContent = sub;
      const dado = el("text", { x: 22, y: h - 22, class: "c-dado" }, g);
      return { g, dado, cx: x + w / 2, cy: y + h / 2, x, y, w, h };
    };
    const nav = caixa(30, 190, 300, 180, "Navegador", "React · Cytoscape.js", "nav");
    const api = caixa(430, 190, 280, 180, "API", "FastAPI · /lab/run");
    const lab = caixa(810, 190, 260, 180, "edugraph.lab", "compõe pelo registro");
    const fa = caixa(1190, 20, 380, 150, "Frente A · dados", "gerador + projeção à mão", "fa");
    const fb = caixa(1190, 205, 380, 150, "Frente B · comunidades", "Louvain com rastro", "fb");
    const fc = caixa(1190, 390, 380, 150, "Frente C · centralidade", "grau · intermediação · autovetor", "fc");
    const fios = el("g", { class: "c-fios" }, svg);
    const fio = (d) => el("path", { d, class: "c-fio", pathLength: 1 }, fios);
    const f1 = fio(`M330 280 H430`), f2 = fio(`M710 280 H810`);
    const fA = fio(`M1070 260 C1130 260 1130 95 1190 95`), fB = fio(`M1070 280 H1190`), fC = fio(`M1070 300 C1130 300 1130 465 1190 465`);
    const volta = el("path", { d: "M940 370 C940 520 180 520 180 370", class: "c-volta", pathLength: 1 }, svg);
    const pacote = el("g", { class: "c-pacote" }, svg);
    el("circle", { r: 13 }, pacote);
    const rotulo = el("text", { class: "c-rot", "text-anchor": "middle", y: -24 }, pacote);
    // Mini-rede na tela do navegador (tiny_v1, cores do Louvain real).
    const mini = el("g", { transform: `translate(${nav.x + 218} ${nav.y + 112}) scale(0.13)`, class: "c-mini" }, svg);
    const P = { S1: [-120, -150], S2: [-120, 150], S6: [-260, 0], S3: [40, 0], S4: [230, -140], S5: [230, 140] };
    D.tiny.simples.forEach(([u, v]) => el("line", { x1: P[u][0], y1: P[u][1], x2: P[v][0], y2: P[v][1], stroke: TINTA, "stroke-width": 10, opacity: 0.5 }, mini));
    const miniNos = Object.entries(P).map(([id, [x, y]]) => ({ id, c: el("circle", { cx: x, cy: y, r: 40, fill: PAPEL, stroke: TINTA, "stroke-width": 8 }, mini) }));
    const caminho = [
      [0.6, 2.0, nav, api, "POST /lab/run"],
      [2.8, 3.8, api, lab, ""],
      [4.6, 5.6, lab, fa, ""],
      [6.6, 7.4, fa, fb, ""],
      [8.6, 9.4, fb, fc, ""],
      [10.2, 11.6, fc, nav, "JSON"],
    ];
    const pt = (b) => [b.cx, b.cy];
    return {
      duracao: 15,
      legendas: [
        [0, "Ao apertar ▶, o navegador envia o pedido: 45 alunos, semente 12, mistura de 20%, Louvain."],
        [2.2, "A API confere os limites — 24 a 75 alunos, até 4.000 ligações — e chama o pacote <b>lab</b>."],
        [4.2, "O lab não importa as frentes: ele as chama pelo <b>registro</b>. Primeiro, a turma: 43 alunos, 93 matrículas."],
        [6.2, "A projeção à mão liga os alunos: <b>337 ligações</b>. O Louvain registra cada um dos <b>41 movimentos</b>: <i>Q</i> = 0,53."],
        [8.4, "A biblioteca python-louvain confere: mesma partição. Em seguida, as três centralidades de cada aluno."],
        [10.2, "Tudo volta numa resposta só: o grafo, o rastro do algoritmo e a leitura em português — cerca de 0,13 s no total."],
        [12.2, "No navegador, o rastro vira quadros de animação: <b>o que a banca vê é o que o algoritmo fez</b>."],
      ],
      render(t) {
        const caixas = [nav, api, lab, fa, fb, fc];
        const acesa = t < 2.4 ? nav : t < 4.2 ? api : t < 6.2 ? lab : t < 8.4 ? fa : t < 10.1 ? fb : t < 11.6 ? fc : nav;
        caixas.forEach((c) => c.g.classList.toggle("acesa", c === acesa));
        [[f1, 0.6, 2], [f2, 2.8, 3.8], [fA, 4.6, 5.6], [fB, 6.6, 7.4], [fC, 8.6, 9.4]].forEach(([f, a, b]) => f.setAttribute("stroke-dashoffset", 1 - seg(t, a, b)));
        volta.setAttribute("stroke-dashoffset", 1 - seg(t, 10.2, 11.6));
        api.dado.textContent = t >= 2.6 ? "limites ok" : "";
        lab.dado.textContent = t >= 4.4 ? "turma: 43 alunos" : "";
        fa.dado.textContent = t >= 5.6 ? "93 matrículas → 337 ligações" : "";
        fb.dado.textContent = t >= 7.4 ? "41 movimentos · Q = 0,53 · ≈ 1 ms" : "";
        fc.dado.textContent = t >= 9.4 ? "3 medidas por aluno" : "";
        nav.dado.textContent = t >= 11.6 ? "anima o rastro" : t >= 0.4 ? "▶ 45 alunos · Louvain" : "";
        // Pacote
        let vis = 0, x = nav.cx, y = nav.cy, txt = "";
        for (const [a, b, de, para, r] of caminho) {
          if (t >= a - 0.3 && t <= b + 0.3) {
            const f = seg(t, a, b);
            let [x1, y1] = pt(de), [x2, y2] = pt(para);
            if (para === nav) {
              // volta pela curva de baixo
              const len = volta.getTotalLength();
              const p = volta.getPointAtLength(len * f);
              x = p.x; y = p.y;
            } else {
              x = lerp(x1, x2, f); y = lerp(y1, y2, f);
            }
            vis = Math.min(seg(t, a - 0.3, a), 1 - seg(t, b, b + 0.3));
            txt = r;
          }
        }
        pacote.setAttribute("transform", `translate(${x} ${y})`);
        pacote.setAttribute("opacity", vis);
        rotulo.textContent = txt;
        // Mini-rede: o rastro do Louvain virando cor
        const tm = [12.4, 12.8, 13.2, 13.6];
        mini.setAttribute("opacity", seg(t, 11.8, 12.3));
        miniNos.forEach(({ id, c }) => {
          const k = D.tiny.louvain.movimentos.findIndex((m) => m.no === id || m.para === id);
          const on = k >= 0 && t >= tm[k];
          const g1 = D.tiny.louvain.membership[id] === D.tiny.louvain.membership.S1;
          c.setAttribute("fill", on ? (g1 ? COR[0] : COR[1]) : PAPEL);
        });
      },
    };
  }

  /* ═════════════ Sequência: O teste contra o acaso ═════════════ */
  function seqAcaso(svg) {
    const S = D.synthetic, N = D.nulo;
    svg.setAttribute("viewBox", "0 0 1640 600");
    const W = 760, H = 540, X0 = 20, Y0 = 30;
    const real = {}, nulo = {};
    S.nos.forEach(([id, x, y]) => { real[id] = [X0 + x * W, Y0 + y * H]; });
    Object.entries(N.nos).forEach(([id, [x, y]]) => { nulo[id] = [X0 + x * W, Y0 + y * H]; });
    const gR = el("g", { class: "a-arestas" }, svg), gN = el("g", { class: "a-arestas" }, svg);
    S.arestas.forEach(([u, v]) => el("line", { x1: real[u][0], y1: real[u][1], x2: real[v][0], y2: real[v][1] }, gR));
    N.arestas.forEach(([u, v]) => el("line", { x1: nulo[u][0], y1: nulo[u][1], x2: nulo[v][0], y2: nulo[v][1] }, gN));
    const gNos = el("g", {}, svg);
    const nos = S.nos.map(([id, , , com], k) => {
      const g = el("g", {}, gNos);
      forma(g, com, 7, COR[com], TINTA, 1);
      return { id, g, k };
    });
    // Painel à direita
    const px = 900;
    const rotQ = el("text", { x: px, y: 92, class: "a-rot" }, svg);
    const valQ = el("text", { x: px, y: 190, class: "a-q" }, svg);
    const subQ = el("text", { x: px, y: 232, class: "a-sub" }, svg);
    // Reta numérica de Q (0 a 0,5)
    const R = { x: px, y: 420, w: 680 };
    const xq = (q) => R.x + (q / 0.5) * R.w;
    const reta = el("g", { class: "a-reta" }, svg);
    el("line", { x1: R.x, y1: R.y, x2: R.x + R.w, y2: R.y, class: "a-eixo" }, reta);
    [0, 0.1, 0.2, 0.3, 0.4, 0.5].forEach((q) => {
      el("line", { x1: xq(q), y1: R.y - 6, x2: xq(q), y2: R.y + 6, class: "a-eixo" }, reta);
      el("text", { x: xq(q), y: R.y + 34, class: "a-tick", "text-anchor": "middle" }, reta).textContent = num(q, 1);
    });
    el("text", { x: R.x, y: R.y + 70, class: "a-tick" }, reta).textContent = "modularidade Q";
    const pontos = N.qs.map((q) => el("circle", { cx: xq(q), cy: R.y, r: 9, class: "a-nulo" }, svg));
    const media = el("g", {}, svg);
    el("line", { x1: xq(N.media), y1: R.y - 54, x2: xq(N.media), y2: R.y + 12, class: "a-media" }, media);
    el("text", { x: xq(N.media), y: R.y - 64, class: "a-tick", "text-anchor": "middle" }, media).textContent = `acaso: ${num(N.media, 3)}`;
    const marca = el("g", {}, svg);
    el("line", { x1: xq(N.q_real), y1: R.y - 90, x2: xq(N.q_real), y2: R.y + 12, class: "a-real" }, marca);
    el("circle", { cx: xq(N.q_real), cy: R.y, r: 12, class: "a-real-p" }, marca);
    el("text", { x: xq(N.q_real), y: R.y - 100, class: "a-tick forte", "text-anchor": "middle" }, marca).textContent = `real: ${num(N.q_real, 3)}`;
    const chave = el("g", { class: "a-chave" }, svg);
    el("path", { d: `M${xq(N.media)} ${R.y - 128} V${R.y - 140} H${xq(N.q_real)} V${R.y - 128}`, class: "a-chave-l", pathLength: 1 }, chave);
    el("text", { x: (xq(N.media) + xq(N.q_real)) / 2, y: R.y - 156, class: "a-z", "text-anchor": "middle" }, chave).textContent = `z = +${num(N.z, 1)}`;

    return {
      duracao: 15,
      legendas: [
        [0, `A rede real de <b>synthetic_v1</b>: 98 alunos e três comunidades. O Louvain dá <i>Q</i> = ${num(N.q_real, 3)}.`],
        [2.4, "O <b>modelo nulo</b> sorteia de novo quem cursou o quê, mantendo quantas disciplinas cada aluno e cada disciplina têm."],
        [6, `Na rede sorteada as cores se misturam — e mesmo assim o Louvain acha <i>Q</i> = ${num(N.qs[0], 3)}: é o <i>Q</i> do acaso.`],
        [8.6, `Cinco sorteios dão <i>Q</i> entre ${num(Math.min(...N.qs), 3)} e ${num(Math.max(...N.qs), 3)}: média de ${num(N.media, 3)}.`],
        [11.4, `O <i>Q</i> real fica <b>${num(N.z, 1)} desvios</b> acima do acaso: a estrutura é real, não coincidência.`],
      ],
      render(t) {
        const emb = seg(t, 2.8, 5.4);
        // Opacidade no grupo, não em cada linha: 840 linhas custariam caro por quadro.
        gR.setAttribute("opacity", 0.28 * (1 - seg(t, 2.4, 3.4)));
        gN.setAttribute("opacity", 0.24 * seg(t, 4.6, 5.8));
        const chave = Math.round(emb * 400);
        if (chave === this.ultimaChave) return this.painel(t);
        this.ultimaChave = chave;
        nos.forEach(({ id, g, k }) => {
          const f = easeIO(clamp((emb * 1.25) - (k % 10) * 0.025));
          const [x1, y1] = real[id], [x2, y2] = nulo[id] || real[id];
          g.setAttribute("transform", `translate(${lerp(x1, x2, f)} ${lerp(y1, y2, f)})`);
        });
        this.painel(t);
      },
      painel(t) {
        const q = t < 5.6 ? N.q_real : lerp(N.q_real, N.qs[0], seg(t, 5.8, 7.4));
        rotQ.textContent = t < 5.6 ? "REDE REAL" : "RÉPLICA SORTEADA Nº 1";
        valQ.textContent = `Q = ${num(q, 3)}`;
        subQ.textContent = t < 5.6 ? "Louvain, semente 42 · 3 comunidades" : `${N.n_arestas_total.toLocaleString("pt-BR")} ligações · mesmos graus`;
        reta.setAttribute("opacity", seg(t, 8.4, 9));
        pontos.forEach((p, i) => {
          const a = seg(t, 8.8 + i * 0.4, 9.3 + i * 0.4, easeBack);
          p.setAttribute("opacity", a);
          p.setAttribute("cy", lerp(R.y - 80, R.y, seg(t, 8.8 + i * 0.4, 9.3 + i * 0.4, easeOut)));
        });
        media.setAttribute("opacity", seg(t, 10.9, 11.3));
        marca.setAttribute("opacity", seg(t, 11.6, 12.2));
        chave.setAttribute("opacity", seg(t, 12.4, 12.8));
        chave.querySelector("path").setAttribute("stroke-dashoffset", 1 - seg(t, 12.4, 13.4));
      },
    };
  }

  /* ═════════════ Abertura e encerramento (canvas) ═════════════ */
  function cena(canvas, modo) {
    const S = D.synthetic;
    const ctx = canvas.getContext("2d");
    const W = 1920, H = 1080, ESC = 1.5;
    canvas.width = W * ESC; canvas.height = H * ESC;
    // Região da rede (lado direito do palco) e posição da marca.
    const R = { x: 1010, y: 120, w: 820, h: 820 };
    const pos = {};
    S.nos.forEach(([id, x, y]) => { pos[id] = [R.x + x * R.w, R.y + y * R.h]; });
    const marca = modo === "abertura" ? { x: 960, y: 520, s: 1 } : { x: 1300, y: 540, s: 1 };
    const centros = [[-110, 0], [0, 0], [110, 0]].map(([dx, dy]) => [marca.x + dx * marca.s, marca.y + dy]);
    const nos = S.nos.map(([id, , , com], k) => ({ id, com, k, alvo: pos[id], ordem: (k * 37) % S.nos.length }));
    const arestas = S.arestas.map(([u, v], k) => ({ a: pos[u], b: pos[v], ordem: (k * 53) % S.arestas.length }));
    const RAIO = 8.5;

    function desenhaForma(tipo, x, y, r, cor, alpha) {
      ctx.globalAlpha = alpha;
      ctx.fillStyle = cor;
      ctx.strokeStyle = "#161512";
      ctx.lineWidth = 1.4;
      ctx.beginPath();
      if (tipo === 1) {
        const h = r * 1.18;
        ctx.moveTo(x, y - h); ctx.lineTo(x + h, y + h * 0.78); ctx.lineTo(x - h, y + h * 0.78); ctx.closePath();
      } else if (tipo === 2) {
        const rr = r * 0.32;
        ctx.roundRect ? ctx.roundRect(x - r, y - r, 2 * r, 2 * r, rr) : ctx.rect(x - r, y - r, 2 * r, 2 * r);
      } else ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fill(); ctx.stroke();
    }
    function wordmark(alpha) {
      ctx.globalAlpha = alpha;
      ctx.fillStyle = "#ece8df";
      ctx.font = `600 84px "Source Serif 4", Georgia, serif`;
      ctx.textBaseline = "middle";
      ctx.fillText("edugraph", marca.x + 190, marca.y + 4);
    }

    const duracao = modo === "abertura" ? 4.6 : 4.2;
    function render(t) {
      ctx.setTransform(ESC, 0, 0, ESC, 0, 0);
      ctx.clearRect(0, 0, W, H);
      // f: 0 = marca, 1 = rede. Abertura vai de 0 a 1; encerramento, de 1 a 0.
      const marcaVis = modo === "abertura" ? seg(t, 0.15, 0.8, easeOut) * (1 - seg(t, 1.3, 2.1)) : seg(t, 1.9, 2.6);
      // Arestas
      ctx.lineWidth = 1.1;
      ctx.strokeStyle = "#ece8df";
      arestas.forEach((e) => {
        const a0 = modo === "abertura" ? 2.3 + (e.ordem / arestas.length) * 1.3 : 0;
        const p = modo === "abertura" ? seg(t, a0, a0 + 0.5) : 1 - seg(t, 0.1 + (e.ordem / arestas.length) * 0.6, 0.5 + (e.ordem / arestas.length) * 0.6);
        if (p <= 0) return;
        ctx.globalAlpha = 0.2 * Math.min(1, p * 1.5);
        ctx.beginPath();
        ctx.moveTo(e.a[0], e.a[1]);
        ctx.lineTo(lerp(e.a[0], e.b[0], p), lerp(e.a[1], e.b[1], p));
        ctx.stroke();
      });
      // Nós: saem da marca da sua comunidade e vão à posição real.
      nos.forEach((n) => {
        const atraso = (n.ordem / nos.length) * 0.7;
        const p = modo === "abertura" ? seg(t, 1.2 + atraso, 2.2 + atraso) : 1 - seg(t, 0.6 + atraso, 1.6 + atraso);
        if (p <= 0.001 && marcaVis > 0.98) return;
        const [cx, cy] = centros[n.com];
        const x = lerp(cx, n.alvo[0], p), y = lerp(cy, n.alvo[1], p);
        const r = lerp(4, RAIO, p);
        desenhaForma(n.com, x, y, r, COR[n.com], Math.min(1, p * 3));
      });
      // A marca: as três formas grandes.
      if (marcaVis > 0) {
        const esc = modo === "abertura" ? lerp(0.6, 1, seg(t, 0.15, 0.9, easeBack)) : lerp(0.7, 1, seg(t, 1.9, 2.6, easeBack));
        centros.forEach(([x, y], i) => desenhaForma(i, x, y, 34 * esc, COR[i], marcaVis));
        if (modo === "encerramento") wordmark(seg(t, 2.2, 2.9));
      }
      ctx.globalAlpha = 1;
    }
    return { duracao, render };
  }

  /* ═════════════ Ligação com o deck ═════════════ */
  window.iniciarMotion = function iniciarMotion(deck) {
    const estatico = deck.embutido || reduzido();
    const filmes = [];
    const fabricas = { metodo: seqMetodo, clique: seqClique, acaso: seqAcaso };
    document.querySelectorAll(".filme[data-seq]").forEach((raiz) => {
      const svg = raiz.querySelector("svg");
      const seq = fabricas[raiz.dataset.seq](svg);
      const filme = new Filme(raiz, seq);
      filme.slide = raiz.closest(".slide");
      // Marcos sincronizados com uma lista fora do filme (ex.: etapas do método).
      if (seq.marcos && raiz.dataset.alvoMarcos) {
        const lista = document.querySelectorAll(raiz.dataset.alvoMarcos);
        seq.aoTempo = (t) => {
          const atual = seq.marcos.filter(([a]) => a <= t).pop()?.[1] ?? -1;
          lista.forEach((item, i) => { item.classList.toggle("on", i === atual); item.classList.toggle("feito", i < atual); });
        };
        seq.aoTempo(0);
      }
      if (estatico) filme.ir(seq.duracao);
      filmes.push(filme);
    });
    // Abertura e encerramento
    const cenas = [];
    document.querySelectorAll("canvas[data-cena]").forEach((cv) => {
      const c = cena(cv, cv.dataset.cena);
      c.slide = cv.closest(".slide");
      c.t = 0;
      c.rodar = () => {
        cancelAnimationFrame(c.raf);
        const t0 = performance.now();
        const passo = (agora) => {
          c.t = (agora - t0) / 1000;
          c.render(Math.min(c.t, c.duracao));
          if (c.t < c.duracao && deck.slideAtual() === c.slide) c.raf = requestAnimationFrame(passo);
          else c.render(c.duracao);
        };
        c.raf = requestAnimationFrame(passo);
      };
      if (estatico) c.render(c.duracao);
      else c.render(0);
      cenas.push(c);
    });
    const pronto = document.fonts?.ready || Promise.resolve();
    pronto.then(() => cenas.forEach((c) => { if (estatico) c.render(c.duracao); }));

    deck.aoMudar((e) => {
      if (e.tipo === "slide" && e.mudouSlide) {
        const atual = deck.slideAtual();
        filmes.forEach((f) => {
          if (f.slide === atual && !estatico) { f.ir(0); setTimeout(() => { if (deck.slideAtual() === atual) f.tocar(); }, 700); }
          else f.pausar();
        });
        cenas.forEach((c) => {
          if (c.slide === atual && !estatico) { c.render(0); setTimeout(() => c.rodar(), 250); }
        });
      }
      if (e.tipo === "tecla") {
        const f = filmes.find((x) => x.slide === deck.slideAtual());
        if (!f) return undefined;
        const k = e.evento.key.toLowerCase();
        if (k === "k") { e.evento.preventDefault(); f.alternar(); return true; }
        if (k === "j") { e.evento.preventDefault(); f.ir(f.t - 2); return true; }
        if (k === "l") { e.evento.preventDefault(); f.ir(f.t + 2); return true; }
      }
      return undefined;
    });
  };
})();
