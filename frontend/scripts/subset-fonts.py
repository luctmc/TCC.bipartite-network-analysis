"""Gera os WOFF2 latinos do edugraph em ambiente temporário, sem dependência do app.

Executar com fonttools/brotli em venv separado (ver public/fonts/README.md).
As fontes de origem e as licenças são da Adobe, fixadas por commit.
"""

from __future__ import annotations

import argparse
import io
import json
from pathlib import Path
from urllib.request import urlopen

from fontTools import subset
from fontTools.ttLib import TTFont

SOURCES = {
    "source-serif-4-roman.woff2": "https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/WOFF2/VAR/SourceSerif4Variable-Roman.ttf.woff2",
    "source-serif-4-italic.woff2": "https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/WOFF2/VAR/SourceSerif4Variable-Italic.ttf.woff2",
    "source-sans-3.woff2": "https://raw.githubusercontent.com/adobe-fonts/source-sans/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e/WOFF2/VF/SourceSans3VF-Upright.ttf.woff2",
    "source-code-pro.woff2": "https://raw.githubusercontent.com/adobe-fonts/source-code-pro/803b7e23ec97ae58b6232ea76519a76d428ba268/WOFF2/TTF/SourceCodePro-Regular.ttf.woff2",
}
RANGES = [
    (0x0000, 0x024F),
    (0x0300, 0x036F),
    (0x1E00, 0x1EFF),
    (0x2000, 0x206F),
    (0x20A0, 0x20CF),
    (0x2100, 0x214F),
    (0x2190, 0x2199),
    (0x2212, 0x2212),
    (0x2264, 0x2265),
    (0xFFFD, 0xFFFD),
]
UNICODES = {c for lo, hi in RANGES for c in range(lo, hi + 1)}
PORTUGUESE = set(map(ord, "ÁÉÍÓÚÀÂÊÔÃÕÇáéíóúàâêôãõçüºª"))


def generate(source_dir: Path | None, out: Path) -> None:
    """Preserva eixos, acentos e licenças; renomeia nomes internos por causa do RFN."""
    metrics = []
    for filename, url in SOURCES.items():
        if source_dir is None:
            with urlopen(url, timeout=30) as response:
                data = response.read()
        else:
            data = (source_dir / filename).read_bytes()
        font = TTFont(io.BytesIO(data), recalcTimestamp=False)
        original_chars = set(font.getBestCmap())
        axes = (
            [(a.axisTag, a.minValue, a.maxValue) for a in font["fvar"].axes]
            if "fvar" in font
            else []
        )
        options = subset.Options()
        options.name_IDs = ["*"]
        options.layout_features = ["*"]
        worker = subset.Subsetter(options=options)
        worker.populate(unicodes=UNICODES)
        worker.subset(font)
        # OFL: "Source" é nome reservado. O alias CSS da família é independente
        # do nome interno do arquivo derivado; copyright e licença ficam intactos.
        for record in font["name"].names:
            if record.nameID in {1, 3, 4, 6, 16, 18, 21, 25} or record.nameID >= 256:
                text = record.toUnicode()
                if "Source" in text:
                    record.string = text.replace("Source", "Edugraph").encode(record.getEncoding())
        font.flavor = "woff2"
        path = out / filename
        font.save(path)
        checked = TTFont(path)
        chars = set(checked.getBestCmap())
        assert chars >= PORTUGUESE, f"{filename}: faltam caracteres portugueses"
        assert original_chars & UNICODES <= chars, f"{filename}: caractere latino perdido"
        after_axes = (
            [(a.axisTag, a.minValue, a.maxValue) for a in checked["fvar"].axes]
            if "fvar" in checked
            else []
        )
        assert axes == after_axes, f"{filename}: eixos variáveis alterados"
        metrics.append(
            {"file": filename, "before": len(data), "after": path.stat().st_size, "axes": axes}
        )
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir", type=Path, help="originais já baixados; padrão: URLs da Adobe"
    )
    args = parser.parse_args()
    generate(args.source_dir, Path(__file__).resolve().parents[1] / "public/fonts")
