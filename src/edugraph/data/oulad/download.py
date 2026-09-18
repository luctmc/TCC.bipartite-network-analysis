"""Download do OULAD com verificação de integridade  ``[A]`` — spec A-02.

Passo manual documentado: o grupo baixa uma vez e o arquivo fica fora do
git (``data/raw/`` está no ``.gitignore``). Este módulo automatiza e,
principalmente, **verifica** — um download truncado que só aparece como
número estranho na tabela do artigo é o pior tipo de erro.

Alternativa manual, se o script falhar: baixe o zip em
https://analyse.kmi.open.ac.uk/open_dataset e extraia os sete CSV em
``data/raw/oulad/``; depois ``python scripts/download_oulad.py --check``.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import tempfile
import urllib.request
import warnings
import zipfile
from pathlib import Path

from edugraph.contracts.errors import ContractError
from edugraph.data.oulad.schema import TABLES, table_path, validate_schema

#: Página oficial do dataset (Kuzilek; Hlosta; Zdrahal, 2017).
OULAD_PAGE = "https://analyse.kmi.open.ac.uk/open_dataset"

#: Download direto do zip.
OULAD_URL = "https://analyse.kmi.open.ac.uk/open_dataset/download"

#: SHA-256 do zip. **Preencher após o primeiro download real**, com o
#: valor que :func:`download` imprime. Enquanto estiver vazio, a
#: verificação avisa em vez de falhar — o grupo ainda não tem o número
#: de referência para comparar.
OULAD_SHA256 = ""

_CHUNK = 1 << 20  # 1 MiB


def sha256_of(path: Path) -> str:
    """SHA-256 de um arquivo, lido em blocos."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(_CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def verify(directory: Path = Path("data/raw/oulad"), *, strict: bool = False) -> bool:
    """Confere que as sete tabelas existem e têm as colunas do esquema.

    Parameters
    ----------
    directory
        Onde os CSV deveriam estar.
    strict
        Levanta :class:`ContractError` em vez de devolver ``False``.
    """
    directory = Path(directory)
    problemas: list[str] = []
    for name in TABLES:
        path = table_path(directory, name)
        if not path.exists():
            problemas.append(f"{name}.csv ausente")
            continue
        with path.open("r", encoding="utf-8", newline="") as handle:
            header = handle.readline().rstrip("\r\n").split(",")
        try:
            validate_schema(name, header)
        except ContractError as error:
            problemas.append(str(error))

    if problemas and strict:
        raise ContractError(f"OULAD incompleto em {directory}:\n  " + "\n  ".join(problemas))
    return not problemas


def _fetch(url: str, dest: Path) -> None:
    """Baixa ``url`` para ``dest`` em blocos, com progresso no stderr."""
    request = urllib.request.Request(url, headers={"User-Agent": "edugraph/0.1 (TCC UniAnchieta)"})
    with urllib.request.urlopen(request, timeout=60) as response, dest.open("wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        for block in iter(lambda: response.read(_CHUNK), b""):
            out.write(block)
            done += len(block)
            if total:
                print(
                    f"\r[oulad] {done / 1e6:8.1f} / {total / 1e6:.1f} MB", end="", file=sys.stderr
                )
        print(file=sys.stderr)


def _check_sha256(zip_path: Path) -> str:
    digest = sha256_of(zip_path)
    if not OULAD_SHA256:
        warnings.warn(
            f"OULAD_SHA256 vazio: sem referência para conferir. Preencha com {digest} "
            "em edugraph/data/oulad/download.py depois de conferir o download.",
            RuntimeWarning,
            stacklevel=2,
        )
    elif digest != OULAD_SHA256:
        raise ContractError(
            f"SHA-256 do zip não confere: esperado {OULAD_SHA256}, obtido {digest}. "
            "Download truncado ou arquivo diferente — não extraído."
        )
    return digest


def _extract(zip_path: Path, dest: Path) -> None:
    """Extrai só os sete CSV, ignorando subpastas do zip."""
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        wanted = {f"{name}.csv" for name in TABLES}
        for member in archive.infolist():
            leaf = Path(member.filename).name
            if leaf in wanted and not member.is_dir():
                with archive.open(member) as src, (dest / leaf).open("wb") as out:
                    shutil.copyfileobj(src, out)


def download(dest: Path = Path("data/raw/oulad"), *, force: bool = False) -> Path:
    """Baixa e extrai o OULAD em ``dest``.

    Não sobrescreve um download válido a menos que ``force``. O zip é
    baixado para um diretório temporário, conferido e só então extraído.

    Returns
    -------
    Path
        ``dest``, com os sete CSV.
    """
    dest = Path(dest)
    if not force and verify(dest):
        print(f"[oulad] já presente e válido em {dest}; use --force para rebaixar")
        return dest

    with tempfile.TemporaryDirectory(prefix="oulad-") as tmp:
        zip_path = Path(tmp) / "oulad.zip"
        print(f"[oulad] baixando {OULAD_URL}")
        _fetch(OULAD_URL, zip_path)
        digest = _check_sha256(zip_path)
        print(f"[oulad] sha256 {digest}")
        _extract(zip_path, dest)

    verify(dest, strict=True)
    print(f"[oulad] {len(TABLES)} tabelas em {dest}")
    return dest
