# Fontes Source — Adobe, SIL OFL 1.1

Obtidas diretamente dos repositórios oficiais em 20/10/2026 e reduzidas localmente
a um subset latino, com português, pontuação e símbolos usados pela interface.
Os eixos variáveis e as licenças foram preservados.
Nenhum carregamento de CDN em runtime.

- `source-serif-4-roman.woff2` — [source-serif: WOFF2/VAR/SourceSerif4Variable-Roman.ttf.woff2](https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/WOFF2/VAR/SourceSerif4Variable-Roman.ttf.woff2); licença `source-serif-OFL.md`.
- `source-serif-4-italic.woff2` — [source-serif: WOFF2/VAR/SourceSerif4Variable-Italic.ttf.woff2](https://raw.githubusercontent.com/adobe-fonts/source-serif/80d3f8894c09c937bebfa9011247d2e1c79fd6f4/WOFF2/VAR/SourceSerif4Variable-Italic.ttf.woff2); licença `source-serif-OFL.md`.
- `source-sans-3.woff2` — [source-sans: WOFF2/VF/SourceSans3VF-Upright.ttf.woff2](https://raw.githubusercontent.com/adobe-fonts/source-sans/87b37a2daaed80fcb8e8ccb0085c4d72ddade12e/WOFF2/VF/SourceSans3VF-Upright.ttf.woff2); licença `source-sans-OFL.md`.
- `source-code-pro.woff2` — [source-code-pro: WOFF2/TTF/SourceCodePro-Regular.ttf.woff2](https://raw.githubusercontent.com/adobe-fonts/source-code-pro/803b7e23ec97ae58b6232ea76519a76d428ba268/WOFF2/TTF/SourceCodePro-Regular.ttf.woff2); licença `source-code-pro-OFL.md`.


## Subset reproduzível

| Arquivo | Original (bytes) | Subset (bytes) |
| --- | ---: | ---: |
| source-serif-4-roman.woff2 | 429.100 | 249.860 |
| source-serif-4-italic.woff2 | 346.688 | 212.288 |
| source-sans-3.woff2 | 170.188 | 88.516 |
| source-code-pro.woff2 | 74.052 | 37.404 |
| **Total** | **1.020.028** | **588.068** |

Redução de **42,3%**. `unicode-range` em `src/styles.css` corresponde às faixas
selecionadas em `scripts/subset-fonts.py`: Latin básico/estendido, acentos
combinantes, Latin Extended Additional, pontuação, moedas, símbolos, setas
simples, menos e desigualdades. O script verifica os caracteres portugueses,
a cobertura selecionada da origem e os eixos de peso/tamanho óptico.

Para respeitar o nome reservado “Source” da OFL, os nomes internos das fontes
derivadas usam “Edugraph”; os aliases CSS continuam identificando a família de
origem. Copyright, licença embutida e os três arquivos OFL permanecem intactos.

Regeneração, a partir dos URLs oficiais fixados acima, sem instalar no projeto
nem no sistema (fonttools 4.67.0, Brotli 1.2.0):

```bash
FONT_TMP=$(mktemp -d /tmp/edugraph-fonts.XXXXXX)
python3 -m venv "$FONT_TMP/venv"
PIP_CACHE_DIR="$FONT_TMP/cache" "$FONT_TMP/venv/bin/python" -m pip install fonttools==4.67.0 brotli==1.2.0
"$FONT_TMP/venv/bin/python" frontend/scripts/subset-fonts.py
```

Execute da raiz do repositório. Para reutilizar originais já baixados, forneça
`--source-dir /caminho/dos/originais`; não forneça os próprios subsets como origem.
