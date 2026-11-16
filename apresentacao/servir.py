"""Sobe a apresentação da defesa — e o edugraph junto, se ele não estiver no ar.

    python apresentacao/servir.py              # apresentação em :8765, sistema em :8000
    python apresentacao/servir.py --sem-app    # só a apresentação; o sistema sobe à parte
    python apresentacao/servir.py --porta 9000 --app-url http://127.0.0.1:8001
    python apresentacao/servir.py --sem-navegador
    python apresentacao/servir.py --curta      # sem os slides marcados como opcionais

**Só biblioteca padrão.** A apresentação é estática (HTML, CSS e JS, sem
build) e não muda nada no sistema: ela abre o edugraph num iframe, no
endereço de ``--app-url``. Servir por HTTP, e não abrir o ``index.html``
direto do disco, é o que faz o modo apresentador (duas janelas
sincronizadas) e a leitura das notas funcionarem.

Para subir o sistema, o script usa o Python da ``.venv`` do repositório (a
que ``scripts/iniciar.py`` cria) e roda ``python -m edugraph api serve``
com ``data/processed`` (se existir) e ``data/fixtures``. Sem ``.venv``, ele
avisa e serve só a apresentação: a janela da demonstração então mostra as
capturas reais, rotuladas como capturas.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import os
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from typing import ClassVar

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
STATIC_INDEX = RAIZ / "src" / "edugraph" / "api" / "static" / "index.html"


def aviso(texto: str) -> None:
    print(f"[apresentacao] {texto}", flush=True)


def python_da_venv() -> Path | None:
    for candidato in (RAIZ / ".venv" / "Scripts" / "python.exe", RAIZ / ".venv" / "bin" / "python"):
        if candidato.exists():
            return candidato
    return None


def no_ar(url: str, prazo: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/health", timeout=prazo) as resposta:
            return resposta.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def subir_app(app_url: str) -> subprocess.Popen[bytes] | None:
    python = python_da_venv()
    if python is None:
        aviso("não achei a .venv do repositório. Rode antes:  python scripts/iniciar.py")
        aviso("sigo só com a apresentação; a demonstração mostrará as capturas reais.")
        return None
    porta = app_url.rstrip("/").rsplit(":", 1)[-1]
    raizes: list[str] = []
    if (RAIZ / "data" / "processed").is_dir():
        raizes += ["--root", "data/processed"]
    raizes += ["--root", "data/fixtures"]
    comando = [str(python), "-m", "edugraph", "api", "serve", *raizes]
    if porta.isdigit() and porta != "8000":
        comando += ["--port", porta]
    if not STATIC_INDEX.exists():
        aviso("a interface do sistema não está compilada: em / ele responde só um JSON.")
        aviso("compile com:  python scripts/iniciar.py   (precisa de Node 20+)")
    aviso("subindo o sistema: " + " ".join(comando[1:]))
    processo = subprocess.Popen(comando, cwd=RAIZ)
    for _ in range(60):
        if no_ar(app_url, 0.5):
            aviso(f"sistema no ar em {app_url}")
            return processo
        if processo.poll() is not None:
            aviso("o sistema terminou ao subir; veja a mensagem acima.")
            return None
        time.sleep(0.5)
    aviso("o sistema não respondeu em 30 s; a apresentação sobe mesmo assim.")
    return processo


class SemCache(http.server.SimpleHTTPRequestHandler):
    """Arquivos estáticos sem cache: editar um slide e recarregar já mostra a mudança."""

    extensions_map: ClassVar[dict[str, str]] = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
        ".html": "text/html; charset=utf-8",
        ".webp": "image/webp",
        ".woff2": "font/woff2",
    }

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, formato: str, *args: object) -> None:  # silencia o log por requisição
        return


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve a apresentação da defesa do TCC.")
    parser.add_argument("--porta", type=int, default=8765, help="porta da apresentação")
    parser.add_argument("--app-url", default="http://127.0.0.1:8000", help="onde o edugraph roda")
    parser.add_argument("--sem-app", action="store_true", help="não tenta subir o sistema")
    parser.add_argument("--sem-navegador", action="store_true", help="não abre o navegador")
    parser.add_argument("--curta", action="store_true", help="sem os slides data-opcional")
    args = parser.parse_args()

    processo = None
    if no_ar(args.app_url):
        aviso(f"sistema já está no ar em {args.app_url}")
    elif not args.sem_app:
        processo = subir_app(args.app_url)
    else:
        aviso(f"sistema fora do ar em {args.app_url} (--sem-app): a demo mostrará capturas.")

    handler = functools.partial(SemCache, directory=str(AQUI))
    servidor = http.server.ThreadingHTTPServer(("127.0.0.1", args.porta), handler)
    consulta = []
    if args.app_url.rstrip("/") != "http://127.0.0.1:8000":
        consulta.append(f"app={args.app_url.rstrip('/')}")
    if args.curta:
        consulta.append("curta")
    sufixo = ("?" + "&".join(consulta)) if consulta else ""
    url = f"http://127.0.0.1:{args.porta}/index.html{sufixo}"
    aviso(f"apresentação em   {url}")
    aviso(f"apresentador em   http://127.0.0.1:{args.porta}/apresentador.html{sufixo}")
    aviso("(ou tecla P na janela da apresentação)")
    aviso("Ctrl+C encerra.")
    if not args.sem_navegador and not os.environ.get("CI"):
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        servidor.server_close()
        if processo is not None and processo.poll() is None:
            aviso("encerrando o sistema que este script subiu…")
            processo.terminate()
            try:
                processo.wait(timeout=10)
            except subprocess.TimeoutExpired:
                processo.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
