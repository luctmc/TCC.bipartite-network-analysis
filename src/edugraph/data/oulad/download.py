"""Download do OULAD com verificação de checksum  ``[A]`` — spec A-02.

Passo manual documentado: o grupo baixa uma vez e o arquivo fica fora do
git (``data/raw/`` está no ``.gitignore``). Este módulo automatiza e,
principalmente, **verifica** — um download truncado que só aparece como
número estranho na tabela do artigo é o pior tipo de erro.
"""

from __future__ import annotations

from pathlib import Path

#: Página oficial do dataset (Kuzilek; Hlosta; Zdrahal, 2017).
OULAD_URL = "https://analyse.kmi.open.ac.uk/open_dataset/download"

#: SHA-256 do zip, a preencher em A-02 com o valor conferido no download
#: real. Enquanto estiver vazio, :func:`verify` avisa em vez de falhar.
OULAD_SHA256 = ""


def download(dest: Path = Path("data/raw/oulad"), *, force: bool = False) -> Path:
    """Baixa e extrai o OULAD em ``dest``.

    Notes
    -----
    A implementar em A-02: baixar com barra de progresso, conferir o
    checksum antes de extrair, e não sobrescrever um download válido a
    menos que ``force``.
    """
    raise NotImplementedError("A-02: ver docs/specs/frente-a/A-02-etl-oulad.md")


def verify(directory: Path = Path("data/raw/oulad")) -> bool:
    """Confere que as sete tabelas estão presentes e íntegras."""
    raise NotImplementedError("A-02: verificação de integridade do download")
