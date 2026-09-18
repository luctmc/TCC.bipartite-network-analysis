"""Download do OULAD com verificação de integridade  ``[A]`` — spec A-02.

Passo manual documentado: o grupo baixa uma vez e o arquivo fica fora do
git (``data/raw/`` está no ``.gitignore``). Este módulo automatiza e,
principalmente, **verifica** — um download truncado que só aparece como
número estranho na tabela do artigo é o pior tipo de erro.

De onde vem
-----------
Em 18/09/2026 o site da Open University (``research.stem.open.ac.uk/
ouanalyse/dataset``) apontava para ``schools.stem.open.ac.uk/cdn/files/
anonymisedData.zip``, que respondia **404**. O espelho oficial e citável
é o do UCI Machine Learning Repository (id 349), que é o que este módulo
usa. Se ele também sair do ar, baixe de qualquer espelho, extraia os sete
CSV em ``data/raw/oulad/`` e rode ``python scripts/download_oulad.py
--check``.

A citação continua sendo a do artigo original: Kuzilek, J.; Hlosta, M.;
Zdrahal, Z. *Open University Learning Analytics dataset.* Scientific
Data, 2017.
"""

from __future__ import annotations

import csv
import hashlib
import shutil
import sys
import urllib.request
import warnings
import zipfile
from pathlib import Path

from edugraph.contracts.errors import ContractError
from edugraph.data.oulad.schema import TABLES, table_path, validate_schema

#: Página oficial do dataset.
OULAD_PAGE = "https://research.stem.open.ac.uk/ouanalyse/dataset/"

#: Download direto do zip — espelho do UCI ML Repository (id 349).
OULAD_URL = (
    "https://archive.ics.uci.edu/static/public/349/open+university+learning+analytics+dataset.zip"
)

#: Onde o zip fica guardado depois de baixado (fora do git). Manter o zip
#: evita rebaixar ~450 MB para re-extrair.
ZIP_NAME = "oulad.zip"

#: SHA-256 do zip do espelho do UCI, conferido no download de 18/09/2026
#: (46.748.244 bytes). Um download com outro hash é truncado ou é outro
#: arquivo, e não é extraído. Se o espelho republicar o zip, atualize aqui
#: com o valor que :func:`download` imprime — e registre a data.
OULAD_SHA256 = "f2ed1902616c1fe8d2824d872c0b7d2d72be435bf0124d077044fe4be2c6d3e4"

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
        # csv.reader, não split(","): a base real vem com cabeçalhos entre
        # aspas ("code_module"), e o split cru os deixaria com aspas.
        with path.open("r", encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle), [])
        try:
            validate_schema(name, header)
        except ContractError as error:
            problemas.append(str(error))

    if problemas and strict:
        raise ContractError(f"OULAD incompleto em {directory}:\n  " + "\n  ".join(problemas))
    return not problemas


def _fetch(url: str, dest: Path) -> None:
    """Baixa ``url`` para ``dest`` em blocos, com progresso no stderr.

    Grava em ``dest.part`` e só renomeia no fim: um download interrompido
    nunca é confundido com um completo.
    """
    part = dest.with_suffix(dest.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "edugraph/0.1 (TCC UniAnchieta)"})
    with urllib.request.urlopen(request, timeout=120) as response, part.open("wb") as out:
        total = int(response.headers.get("Content-Length") or 0)
        done = 0
        for block in iter(lambda: response.read(_CHUNK), b""):
            out.write(block)
            done += len(block)
            if total:
                print(
                    f"\r[oulad] {done / 1e6:8.1f} / {total / 1e6:.1f} MB", end="", file=sys.stderr
                )
            else:
                print(f"\r[oulad] {done / 1e6:8.1f} MB", end="", file=sys.stderr)
        print(file=sys.stderr)
    part.replace(dest)


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


def _extract(zip_path: Path, dest: Path) -> list[str]:
    """Extrai só os sete CSV, ignorando subpastas — e entrando em zips aninhados.

    O espelho do UCI embrulha o zip original num zip próprio; o CSV pode
    estar a dois níveis de profundidade.
    """
    dest.mkdir(parents=True, exist_ok=True)
    wanted = {f"{name}.csv" for name in TABLES}
    found: list[str] = []

    def walk(archive: zipfile.ZipFile) -> None:
        for member in archive.infolist():
            if member.is_dir():
                continue
            leaf = Path(member.filename).name
            if leaf in wanted:
                with archive.open(member) as src, (dest / leaf).open("wb") as out:
                    shutil.copyfileobj(src, out)
                found.append(leaf)
            elif leaf.lower().endswith(".zip"):
                with archive.open(member) as inner_bytes, zipfile.ZipFile(inner_bytes) as inner:
                    walk(inner)

    with zipfile.ZipFile(zip_path) as archive:
        walk(archive)
    return sorted(found)


def download(dest: Path = Path("data/raw/oulad"), *, force: bool = False) -> Path:
    """Baixa e extrai o OULAD em ``dest``.

    Não sobrescreve um download válido a menos que ``force``. O zip fica
    em ``dest.parent / oulad.zip``: se já estiver lá, não é rebaixado —
    só conferido e re-extraído.

    Returns
    -------
    Path
        ``dest``, com os sete CSV.
    """
    dest = Path(dest)
    if not force and verify(dest):
        print(f"[oulad] já presente e válido em {dest}; use --force para rebaixar")
        return dest

    zip_path = dest.parent / ZIP_NAME
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists() and not force:
        print(f"[oulad] zip já baixado em {zip_path}; conferindo e extraindo")
    else:
        print(f"[oulad] baixando {OULAD_URL}")
        _fetch(OULAD_URL, zip_path)

    digest = _check_sha256(zip_path)
    print(f"[oulad] sha256 {digest}")
    found = _extract(zip_path, dest)
    print(f"[oulad] extraídos: {', '.join(found) or 'nenhum CSV encontrado no zip'}")

    verify(dest, strict=True)
    print(f"[oulad] {len(TABLES)} tabelas em {dest}")
    return dest
