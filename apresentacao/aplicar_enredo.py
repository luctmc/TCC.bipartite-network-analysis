"""Leva a fala do ``ENREDO.md`` para as notas do apresentador do ``index.html``.

    python apresentacao/aplicar_enredo.py           (aplica)
    python apresentacao/aplicar_enredo.py --contar  (só conta palavras e tempo)

Cada trecho do enredo começa com ``**Na tela:** `id` ``. A fala desse trecho
substitui, no ``<aside class="notas">`` do slide com esse ``id``, os parágrafos
de fala e de ação; os de fonte, observação e "se perguntarem" ficam. Depois,
rode ``gerar_roteiro.py`` para atualizar o ``ROTEIRO.md``.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

PASTA = Path(__file__).resolve().parent
ENREDO = PASTA / "ENREDO.md"
INDEX = PASTA / "index.html"
PALAVRAS_POR_MINUTO = 140

#: Parágrafos das notas que não são fala e por isso são mantidos.
MANTIDOS = (
    "<b>Fonte",
    "<b>Observação",
    "<b>Se perguntarem",
    "<b>Nota",
    "<b>Não revelar",
    "<b>Para leigos",
    "<b>Durante",
    "<b>Perguntas",
    "<b>Antes",
)


def _trechos(texto: str) -> list[tuple[str, str, list[str]]]:
    """Devolve (id, rubrica, parágrafos de fala) de cada ``**Na tela:**``."""
    corpo = texto.split("\n## Se perguntarem")[0]
    saida = []
    for bloco in re.split(r"\n(?=\*\*Na tela:\*\*)", corpo)[1:]:
        primeira, _, resto = bloco.partition("\n")
        ident = re.search(r"`([^`]+)`", primeira).group(1)
        rubrica = " ".join(re.findall(r"\*\[([^\]]+)\]\*", primeira))
        resto = re.split(r"\n---|\n## ", resto)[0]
        paragrafos = [" ".join(p.split()) for p in resto.strip().split("\n\n") if p.strip()]
        saida.append((ident, rubrica, paragrafos))
    return saida


def _inline(texto: str) -> str:
    texto = html.escape(texto, quote=False)
    texto = re.sub(r"\*\[([^\]]+)\]\*", r"<i>[\1]</i>", texto)
    texto = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", texto)
    texto = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", texto)
    return re.sub(r"`([^`]+)`", r"<code>\1</code>", texto)


def _paragrafo(texto: str, primeiro: bool) -> str:
    m = re.match(r"((?:▸\s*)+)", texto)
    if m:
        n = m.group(1).count("▸")
        resto = _inline(texto[m.end() :]).replace("▸", "<b>▸</b>")
        acao = "avance" if n == 1 else f"avance {n} vezes"
        return f"<p><b>Ação:</b> {acao}. {resto}</p>"
    rotulo = "<b>Fala:</b> " if primeiro else ""
    return f"<p>{rotulo}{_inline(texto).replace('▸', '<b>▸</b>')}</p>"


def _palavras(paragrafos: list[str]) -> int:
    limpo = re.sub(r"\*\[[^\]]+\]\*", "", " ".join(paragrafos)).replace("▸", "")
    return len(limpo.split())


def main() -> None:
    args = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    args.add_argument("--contar", action="store_true", help="só conta palavras e tempo")
    contar = args.parse_args().contar
    trechos = _trechos(ENREDO.read_text(encoding="utf-8"))
    total = sum(_palavras(p) for _, _, p in trechos)
    if contar:
        for ident, _, paragrafos in trechos:
            n = _palavras(paragrafos)
            print(f"{ident:24} {n:4} palavras  ≈ {60 * n / PALAVRAS_POR_MINUTO:4.0f} s")
        print(f"{'total':24} {total:4} palavras  ≈ {total / PALAVRAS_POR_MINUTO:4.1f} min de fala")
        return
    pagina = INDEX.read_text(encoding="utf-8")
    for ident, rubrica, paragrafos in trechos:
        padrao = re.compile(
            rf'(<section [^>]*id="{re.escape(ident)}"[\s\S]*?<aside class="notas">)'
            r"([\s\S]*?)(</aside>)"
        )
        achado = padrao.search(pagina)
        if not achado:
            raise SystemExit(f"slide sem notas no index.html: {ident}")
        antigos = re.findall(r"<p>[\s\S]*?</p>", achado.group(2))
        mantidos = [p for p in antigos if p[3:].lstrip().startswith(MANTIDOS)]
        novos = [f"<p><b>Ação:</b> {_inline(rubrica)}.</p>"] if rubrica else []
        novos += [_paragrafo(p, i == 0) for i, p in enumerate(paragrafos)]
        corpo = "\n    " + "\n    ".join(novos + mantidos) + "\n  "
        pagina = pagina[: achado.start(2)] + corpo + pagina[achado.end(2) :]
    INDEX.write_text(pagina, encoding="utf-8", newline="\n")
    minutos = total / PALAVRAS_POR_MINUTO
    print(f"notas de {len(trechos)} slides; fala: {total} palavras (≈ {minutos:.1f} min)")


if __name__ == "__main__":
    main()
