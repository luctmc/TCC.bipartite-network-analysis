"""Escrita de tabelas e figuras do artigo  ``[T]``.

Transversal às três frentes porque o requisito é do artigo, não de
nenhuma frente (briefing §9): figuras reprodutíveis por um comando,
métricas em formato tabelável, e índices gerados — nunca editados à mão,
porque arquivo compartilhado editado por três pessoas é conflito de
merge garantido (§7 do plano de arquitetura).

Este subpacote **não** conhece as frentes: ele recebe linhas e caminhos.
"""

from edugraph.reporting.figures import figure_path, save_figure
from edugraph.reporting.tables import write_table

__all__ = ["figure_path", "save_figure", "write_table"]
