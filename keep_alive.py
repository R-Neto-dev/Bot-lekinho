"""Health check HTTP para o deployment do bot."""

from __future__ import annotations

import os
import threading

from flask import Flask


app = Flask(__name__)


@app.get("/")
def index() -> tuple[str, int]:
    return "Bot online!", 200


@app.get("/health")
def health() -> tuple[dict[str, str], int]:
    return {"status": "ok"}, 200


def _run_server() -> None:
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port, use_reloader=False)


def keep_alive() -> None:
    """Inicia o servidor Flask sem bloquear o loop do Discord."""
    thread = threading.Thread(target=_run_server, name="health-server", daemon=True)
    thread.start()
