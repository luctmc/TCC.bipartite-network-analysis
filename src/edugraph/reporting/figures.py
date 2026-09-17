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
    """Grava a figura em PNG e SVG e devolve os dois caminhos."""
    written = []
    for ext in ("png", "svg"):
        path = figure_path(name, out_dir=out_dir, ext=ext)
        fig.savefig(path)
        written.append(path)
    return written


def build_index(out_dir: Path = FIGURES_DIR) -> Path:
    """Gera ``docs/artigo/indice-figuras.md`` a partir do que existe em disco.

    Arquivo **gerado**, nunca editado à mão: três pessoas editando o
    mesmo índice é conflito de merge em todo PR (§7 do plano).
    Disponível como ``python -m edugraph figures --index`` quando a spec
    A-07 fechar.
    """
    raise NotImplementedError("A-07/B-07: geração do índice de figuras")
