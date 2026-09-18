"""Estilo e gravação das figuras do artigo  ``[T]``.

Um só lugar decide tamanho, fonte e resolução, para que as figuras das
três frentes pareçam do mesmo trabalho. Cada figura é gravada em PNG
(rascunho) e SVG (versão final do artigo).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

#: Onde as figuras do artigo são gravadas.
FIGURES_DIR = Path("results/figures")

#: Largura de uma coluna do artigo, em polegadas. Figura desenhada no
#: tamanho certo não precisa ser reescalada, e texto reescalado é a
#: causa número um de legenda ilegível na banca.
COLUMN_WIDTH_IN = 3.4
FULL_WIDTH_IN = 7.0

DPI = 300

#: Estilo aplicado a toda figura do projeto.
STYLE: dict[str, Any] = {
    "figure.dpi": 110,
    "savefig.dpi": DPI,
    "savefig.bbox": "tight",
    "font.size": 9,
    "axes.titlesize": 10,
    "axes.labelsize": 9,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.25,
    # Ids de clip-path e gradiente no SVG são derivados de um hash; sem sal
    # fixo o matplotlib usa o endereço do objeto em memória, e a mesma
    # figura sai com ids diferentes a cada execução. Com o sal, o SVG é
    # reproduzível byte a byte (ADR-0011).
    "svg.hashsalt": "edugraph",
}


def figure_path(name: str, *, out_dir: Path = FIGURES_DIR, ext: str = "png") -> Path:
    """Caminho canônico de uma figura, criando o diretório."""
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{name}.{ext}"


def apply_style() -> None:
    """Aplica :data:`STYLE` ao matplotlib."""
    import matplotlib.pyplot as plt

    plt.rcParams.update(STYLE)


def save_figure(fig: Any, name: str, *, out_dir: Path = FIGURES_DIR) -> list[Path]:
    """Grava a figura em PNG e SVG e devolve os dois caminhos.

    Sem data nos metadados: o SVG do matplotlib carrega um carimbo de
    tempo por padrão, e aí a mesma figura gerada duas vezes teria bytes
    diferentes — o que tornaria inútil versionar ``results/figures``
    (ADR-0011, o mesmo princípio das fixtures).
    """
    import io

    png = figure_path(name, out_dir=out_dir, ext="png")
    fig.savefig(png)

    # SVG passa por memória para normalizar o fim de linha: gravado direto
    # em disco, o matplotlib usa o padrão do sistema (CRLF no Windows) e a
    # figura mudaria de bytes conforme quem a gerou.
    buffer = io.BytesIO()
    fig.savefig(buffer, format="svg", metadata={"Date": None})
    svg = figure_path(name, out_dir=out_dir, ext="svg")
    svg.write_bytes(buffer.getvalue().replace(b"\r\n", b"\n"))
    return [png, svg]


#: Onde o índice gerado é gravado.
INDEX_PATH = Path("docs/artigo/indice-figuras.md")

#: As figuras que o artigo planeja, por prefixo de arquivo. É a única
#: parte "escrita à mão" do índice — e mora aqui, no código, não no .md,
#: justamente para que o .md possa ser regenerado sem medo. Uma figura
#: fora desta lista aparece no índice como "não planejada": ou é nova e
#: entra aqui, ou é lixo e sai de ``results/figures``.
PLANNED_FIGURES: tuple[tuple[str, str, str, str], ...] = (
    # (prefixo, título, spec, onde no artigo)
    ("fig1-arquitetura", "Arquitetura de componentes", "—", "abertura do cap. 3"),
    ("fig2-bipartido", "Grafo bipartido", "A-07", "seção de dados"),
    (
        "fig3-ponderacoes",
        "Distribuição de pesos: simples × alocação de recursos",
        "A-05",
        "seção de projeção",
    ),
    ("fig4-comunidades", "Comunidades na projeção aluno↔aluno", "B-07", "seção de comunidades"),
    ("fig5-tamanhos", "Distribuição de tamanhos de comunidade", "B-07", "seção de comunidades"),
    ("fig6-q-tempo", "Q × tempo por algoritmo", "B-04/B-07", "comparação de algoritmos"),
    (
        "fig7-disciplinas",
        "Ranking de disciplinas por intermediação",
        "C-03/C-07",
        "disciplinas críticas",
    ),
    ("fig8-validacao", "Desfecho por quartil de centralidade", "C-06", "validação"),
    ("ui-", "Capturas da interface", "C-05", "aplicação"),
)


def _scan(out_dir: Path) -> dict[str, dict[str, Any]]:
    """Figuras em disco, agrupadas por nome-base: formatos, tamanho e legenda."""
    found: dict[str, dict[str, Any]] = {}
    if not out_dir.is_dir():
        return found
    for path in sorted(out_dir.iterdir()):
        if path.suffix.lower() not in {".png", ".svg"}:
            continue
        entry = found.setdefault(path.stem, {"formats": [], "bytes": 0, "caption": ""})
        entry["formats"].append(path.suffix.lstrip(".").lower())
        entry["bytes"] += path.stat().st_size
        caption = path.with_suffix(".caption.txt")
        if caption.exists():
            entry["caption"] = caption.read_text(encoding="utf-8").strip()
    return found


def build_index(out_dir: Path = FIGURES_DIR, index_path: Path = INDEX_PATH) -> Path:
    """Gera ``docs/artigo/indice-figuras.md`` a partir do que existe em disco.

    Arquivo **gerado**, nunca editado à mão: três pessoas editando o
    mesmo índice é conflito de merge em todo PR (§7 do plano). Comando:
    ``python -m edugraph figures --index``.

    O índice cruza :data:`PLANNED_FIGURES` com ``results/figures``: cada
    figura planejada aparece como *presente* (com formatos e legenda,
    quando o gerador gravou um ``.caption.txt``) ou *pendente*; arquivos
    fora do plano aparecem numa seção própria, para serem adotados ou
    removidos.
    """
    found = _scan(out_dir)
    claimed: set[str] = set()

    lines = [
        "# Índice de figuras",
        "",
        "> **Arquivo gerado** por `python -m edugraph figures --index` a partir de",
        f"> `{out_dir.as_posix()}/`. Não editar à mão: a lista planejada vive em",
        "> `edugraph.reporting.figures.PLANNED_FIGURES`; para acrescentar uma",
        "> figura ao plano, edite lá e regenere.",
        "",
        "| # | Figura | Spec | Estado | Arquivos | Onde no artigo |",
        "|---|---|---|---|---|---|",
    ]
    captions: list[tuple[str, str]] = []
    for number, (prefix, title, spec, where) in enumerate(PLANNED_FIGURES, start=1):
        matches = sorted(stem for stem in found if stem.startswith(prefix))
        claimed.update(matches)
        if matches:
            files = ", ".join(
                f"`{stem}.{{{','.join(found[stem]['formats'])}}}`" for stem in matches
            )
            estado = "presente"
            for stem in matches:
                if found[stem]["caption"]:
                    captions.append((stem, found[stem]["caption"]))
        else:
            files, estado = "—", "pendente"
        lines.append(f"| {number} | {title} | {spec} | {estado} | {files} | {where} |")

    unplanned = sorted(set(found) - claimed)
    if unplanned:
        lines += ["", "## Fora do plano", "", "Adote em `PLANNED_FIGURES` ou remova de disco.", ""]
        lines += [f"- `{stem}` ({', '.join(found[stem]['formats'])})" for stem in unplanned]

    if captions:
        lines += ["", "## Legendas geradas", ""]
        for stem, caption in captions:
            lines += [f"**`{stem}`** — {caption}", ""]

    lines += [
        "",
        "## Regras",
        "",
        "- Toda figura sai em **PNG e SVG** (`reporting.figures.save_figure`), sem",
        "  data nos metadados: a mesma figura gerada duas vezes tem os mesmos bytes.",
        "- Estilo comum em `reporting.figures.STYLE`: tamanho no valor final, sem",
        "  reescalar — texto reescalado é a causa número um de legenda ilegível.",
        "- Cores distinguem **também em escala de cinza**: o artigo pode ser",
        "  impresso em preto e branco.",
        "- Figura de grafo grande é **amostrada ou agregada**, e a legenda diz o",
        "  que foi feito (gravada em `<nome>.caption.txt` ao lado da figura).",
        "",
        "A figura 1 é exportada do Mermaid de",
        "[`../arquitetura/diagrama-cap3.md`](../arquitetura/diagrama-cap3.md).",
        "",
    ]
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return index_path
