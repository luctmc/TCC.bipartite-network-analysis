/**
 * Configuração da apresentação — o único lugar com valores que o grupo
 * pode querer trocar sem mexer no motor.
 *
 * Script clássico (sem módulos), para a apresentação abrir até direto do disco.
 *
 * O endereço do sistema pode ser trocado também pela URL:
 *   index.html?app=http://127.0.0.1:8001
 * (é o que `servir.py --app-url ...` faz sozinho).
 */
window.EDUGRAPH_CONFIG = {
  /** Seções da apresentação (as mesmas do artigo). O slide aponta a sua com data-secao="n". */
  secoes: ["Introdução", "Fundamentação", "Metodologia", "Desenvolvimento", "Resultados", "Considerações finais"],

  /** Onde o edugraph está rodando (`python -m edugraph api serve`). */
  appUrl: "http://127.0.0.1:8000",

  /** Caminho aberto na demonstração. `?tour` força o tour do laboratório (ver frontend/src/tour/estado.ts). */
  caminhoDemo: "/?tour",

  /** Intervalo da verificação de saúde do sistema enquanto o slide da demo está na tela (ms). */
  intervaloSaude: 5000,

  /** Duração alvo da defesa, para o cronômetro do modo apresentador (min). */
  duracaoAlvoMin: 20,

  /** Canal de sincronização entre a janela da plateia e a do apresentador. */
  canal: "edugraph-apresentacao",

  /** Capturas reais usadas quando o sistema não responde (fallback rotulado). */
  capturas: [
    { src: "img/app/tour-01.webp", legenda: "Tour · 1 de 9 — boas-vindas: o que o sistema faz, sem inteligência artificial." },
    { src: "img/app/tour-02.webp", legenda: "Tour · 2 de 9 — as duas telas: Laboratório ao vivo e Explorar resultados." },
    { src: "img/app/tour-03.webp", legenda: "Tour · 3 de 9 — a turma fictícia de Computação, o número de alunos e a mistura entre áreas." },
    { src: "img/app/tour-04.webp", legenda: "Tour · 4 de 9 — a rede: projetar alunos ou disciplinas, ponderação e ligação mínima." },
    { src: "img/app/tour-05.webp", legenda: "Tour · 5 de 9 — o algoritmo: Louvain ou Girvan–Newman." },
    { src: "img/app/tour-06.webp", legenda: "Tour · 6 de 9 — as quatro etapas: matrículas, projeção, algoritmo e resultado." },
    { src: "img/app/tour-07.webp", legenda: "Tour · 7 de 9 — o grafo: cada ponto é um aluno; forma e cor mostram o grupo." },
    { src: "img/app/tour-08.webp", legenda: "Tour · 8 de 9 — a narração em português de cada etapa." },
    { src: "img/app/tour-09.webp", legenda: "Tour · 9 de 9 — a rede só é montada quando se aperta ▶." },
    { src: "img/app/louvain-etapa-1.webp", legenda: "Etapa 1 · Matrículas — 43 alunos, 8 disciplinas, 93 matrículas (grafo bipartido)." },
    { src: "img/app/louvain-etapa-2.webp", legenda: "Etapa 2 · Projeção — as disciplinas somem e os alunos se ligam: 337 ligações." },
    { src: "img/app/louvain-etapa-3.webp", legenda: "Etapa 3 · Louvain — cada aluno muda para o grupo em que Q mais sobe (movimento 12 de 41)." },
    { src: "img/app/louvain-etapa-4.webp", legenda: "Etapa 4 · Resultado — três grupos com nome, Q = 0,53, papéis e perfis dos alunos." },
    { src: "img/app/louvain-revelar.webp", legenda: "Revelação — as áreas que o gerador plantou: o Louvain acertou 100% dos alunos (NMI = 1,00)." },
    { src: "img/app/gn-algoritmo.webp", legenda: "Girvan–Newman — a curva de Q a cada corte; o pico é o melhor corte." },
    { src: "img/app/gn-resultado.webp", legenda: "Girvan–Newman — mesma turma: três grupos, Q = 0,49, em cerca de 0,5 s." },
    { src: "img/app/explorar.webp", legenda: "Explorar resultados — synthetic_v1, alunos · projeção simples, Louvain com Q = 0,4666." },
  ],
};
