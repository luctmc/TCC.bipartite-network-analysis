"""Gera ROTEIRO.md a partir das notas do apresentador em index.html.

    python apresentacao/gerar_roteiro.py

As notas moram num lugar só — o `<aside class="notas">` de cada slide —
para o roteiro impresso e o modo apresentador nunca divergirem. Edite o
slide e rode este script de novo. Só biblioteca padrão.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path

AQUI = Path(__file__).resolve().parent

#: As mesmas seções de js/config.js (data-secao="n" no slide).
SECOES = (
    "Introdução",
    "Fundamentação teórica",
    "Metodologia",
    "Desenvolvimento",
    "Resultados e discussão",
    "Considerações finais",
)

MARCAS = {"b": "**", "strong": "**", "i": "*", "em": "*", "code": "`"}


def _secao(a: dict[str, str | None]) -> str:
    if "data-apendice" in a:
        return "Apêndice técnico"
    n = a.get("data-secao")
    if n and n.isdigit() and 1 <= int(n) <= len(SECOES):
        return f"{n} · {SECOES[int(n) - 1]}"
    if a.get("id") in ("referencias", "encerramento"):
        return "Referências e encerramento"
    return "Abertura e sumário"


class Leitor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[dict[str, object]] = []
        self.em_notas = 0
        self.atual: dict[str, object] | None = None
        self.paragrafo: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "section" and "slide" in classes:
            self.atual = {
                "id": a.get("id") or "",
                "titulo": a.get("data-titulo") or "",
                "ato": _secao(a),
                "apendice": "data-apendice" in a,
                "notas": [],
            }
            self.slides.append(self.atual)
        elif tag == "aside" and "notas" in classes:
            self.em_notas = 1
        elif self.em_notas:
            if tag == "aside":
                self.em_notas += 1
            if tag == "p":
                self.paragrafo = []
            elif tag in MARCAS:
                self.paragrafo.append(MARCAS[tag])
            elif tag == "br":
                self.paragrafo.append(" ")

    def handle_endtag(self, tag: str) -> None:
        if not self.em_notas:
            return
        if tag == "aside":
            self.em_notas -= 1
        elif tag == "p" and self.atual is not None:
            texto = re.sub(r"\s+", " ", "".join(self.paragrafo)).strip()
            if texto:
                self.atual["notas"].append(texto)  # type: ignore[union-attr]
            self.paragrafo = []
        elif tag in MARCAS:
            self.paragrafo.append(MARCAS[tag])

    def handle_data(self, data: str) -> None:
        if self.em_notas:
            self.paragrafo.append(data)


def main() -> None:
    leitor = Leitor()
    leitor.feed((AQUI / "index.html").read_text(encoding="utf-8"))
    principais = [s for s in leitor.slides if not s["apendice"]]
    linhas = [
        "# Roteiro da defesa — edugraph",
        "",
        "Gerado de `index.html` por `gerar_roteiro.py`: **não edite à mão** — edite as",
        'notas (`<aside class="notas">`) de cada slide e rode o script de novo.',
        "",
        f"{len(principais)} slides principais e "
        f"{len(leitor.slides) - len(principais)} de apêndice.",
        "Marcas: **Fala** é o que dizer; **Ação** é o que fazer (avançar, clicar);",
        "**Se perguntarem** antecipa perguntas da banca.",
        "",
    ]
    ato = None
    ap = 0
    for s in leitor.slides:
        if s["ato"] != ato:
            ato = s["ato"]
            linhas += ["", f"## {ato}", ""]
        if s["apendice"]:
            ap += 1
            rotulo = f"A{ap}"
        else:
            rotulo = f"{principais.index(s) + 1:02d}"
        linhas += [f"### {rotulo} · {s['titulo']}", ""]
        for paragrafo in s["notas"]:  # type: ignore[union-attr]
            linhas += [paragrafo, ""]
    texto = "\n".join(linhas).rstrip() + "\n"
    (AQUI / "ROTEIRO.md").write_text(texto, encoding="utf-8", newline="\n")
    print(f"ROTEIRO.md: {len(leitor.slides)} slides")


if __name__ == "__main__":
    main()
