"""Site local do YABook Tasks: `task board --serve` e `task board --output`.

Servidor só com biblioteca padrão, escutando em 127.0.0.1. A página recebe o
estado por `/api/estado` e é avisada de mudanças por SSE a partir da verificação
periódica dos arquivos do repositório de dados. Requisições com Host diferente
de 127.0.0.1/localhost são recusadas (proteção contra DNS rebinding); escrita
exige o token da página e a mesma origem.
"""
import base64
import datetime
import hashlib
import json
import mimetypes
import os
import secrets
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from . import events, sheet, tree
from .commands import Tasks, today

SITE = Path(__file__).resolve().parent / "site"
DEFAULT_PORT = 8765
POLL_SECONDS = 2.0
PING_SECONDS = 15.0
WATCHED_DIRS = ("tarefas", "eventos", "horas", "fichas")
WATCHED_FILES = ("quadro.yml", "config.yml", "local/ativa.json")
MAX_REF_BYTES = 20000
SHELL = ("index.html", "app.css", "app.js", "manifest.webmanifest", "sw.js", "icon-192.png", "icon-512.png", "icon.svg")


class Board:
    """Leitura do repositório de dados para o site; a escrita entra pelo mesmo `Tasks` do agente."""

    def __init__(self, store, cfg=None):
        self.store, self.cfg = store, cfg or {}
        self.tasks = Tasks(store, self.cfg)

    # Mudanças ---------------------------------------------------------------
    def fingerprint(self):
        digest = hashlib.sha256()
        root = self.store.root
        for name in WATCHED_DIRS:
            folder = root / name
            if not folder.is_dir():
                continue
            for entry in sorted(os.scandir(folder), key=lambda e: e.name):
                stat = entry.stat()
                digest.update(("%s/%s %d %d\n" % (name, entry.name, stat.st_mtime_ns, stat.st_size)).encode())
        for name in WATCHED_FILES:
            path = root / name
            if path.is_file():
                stat = path.stat()
                digest.update(("%s %d %d\n" % (name, stat.st_mtime_ns, stat.st_size)).encode())
        return digest.hexdigest()[:16]

    # Leitura ----------------------------------------------------------------
    def base(self):
        value = self.cfg.get("confidential")
        return Path(value).expanduser() if value and Path(value).expanduser().is_dir() else None

    def _ref_path(self, target):
        base = self.base()
        if base is None:
            return None
        base = base.resolve()
        targets = [Path(target)]
        # Algumas referências incluem o nome da própria pasta da base.
        if targets[0].parts and targets[0].parts[0] == base.name:
            targets.append(Path(*targets[0].parts[1:]))
        for relative in targets:
            candidate = base / relative
            for path in (candidate, candidate.with_name(candidate.name + ".md")):
                resolved = path.resolve()
                if base not in resolved.parents:
                    continue  # inclusive links simbólicos e o fallback com .md
                if resolved.is_file():
                    return resolved
        return None

    def confidential_state(self, data):
        refs = [r.split(":", 1)[1] for r in data.get("refs", []) if r.startswith("confidencial:")]
        base = self.base()
        local = base is not None and (base / "tarefas" / (data["id"] + ".md")).is_file()
        if local or (refs and all(self._ref_path(r) for r in refs)):
            return "disponivel"
        return "bloqueado" if refs else None

    def state(self):
        tasks, roles = self.store.list(), self.tasks.roles()
        index = tree.index_of(tasks)
        open_questions = {}
        for task in tasks:
            data = task["data"]
            if data.get("tipo") == "pergunta" and not data.get("resposta") and roles.get(data.get("coluna")) not in ("concluido", "arquivado"):
                open_questions[data.get("sobre")] = open_questions.get(data.get("sobre"), 0) + 1
        items = []
        for task in tasks:
            data = task["data"]
            item = dict(self.tasks.brief(task, index), ordem=data.get("ordem", 0), revision=task["revision"],
                        atualizada=data.get("atualizada"), criada=data.get("criada"), papel=roles.get(data.get("coluna")))
            for key in ("refs", "sobre", "resposta", "pessoal", "size_manual"):
                if key in data:
                    item[key + ("_marcado" if key == "pessoal" else "")] = data[key]
            item["perguntas_abertas"] = open_questions.get(data["id"], 0)
            confidential = self.confidential_state(data)
            if confidential:
                item["confidencial"] = confidential
            items.append(item)
        active_path = self.store.root / "local" / "ativa.json"
        try:
            active = json.loads(active_path.read_text(encoding="utf-8")) if active_path.is_file() else None
        except ValueError:
            active = None
        summary = self.tasks.summary(active)
        cfg = self.store.config()
        return dict(
            maquina=self.cfg.get("machine"), hoje=today().isoformat(), revisao=self.fingerprint(),
            base_confidencial=self.base() is not None, colunas=self.store.columns(),
            rotulos=cfg.get("rotulos", {}), tarefas=items, epicos=summary["epicos"], ativa=active,
            prazos=summary["prazos"], perguntas=summary["perguntas"],
            eventos_pendentes=len(events.pending(self.store.root, months=2)),
        )

    def task(self, identifier):
        task = self.store.get(identifier)
        index = tree.index_of(self.store.list())
        result = dict(task, resumo=self.tasks.brief(task, index), confidencial=self.confidential_state(task["data"]))
        complement = self.tasks.complement(identifier) if self.base() else None
        if complement:
            result["complemento"] = complement
        refs = {}
        for ref in task["data"].get("refs", []):
            if ref.startswith("confidencial:"):
                path = self._ref_path(ref.split(":", 1)[1])
                refs[ref] = path.read_text(encoding="utf-8", errors="replace")[:MAX_REF_BYTES] if path else None
        result["referencias"] = refs
        children = [t for t in self.store.list() if t["data"].get("pai") == identifier]
        result["filhos"] = [self.tasks.brief(t, index) for t in children]
        return result

    def sheet(self, day=None, week=False):
        day = day or today().isoformat()
        complement = self.tasks.complement if self.base() else None
        return (sheet.week_sheet if week else sheet.day_sheet)(self.store, day, complement)

    def week(self, day=None):
        """Horas estimadas e tarefas tocadas por dia, de segunda a domingo."""
        date = datetime.date.fromisoformat(day or today().isoformat())
        monday = date - datetime.timedelta(days=date.weekday())
        titles = {t["data"]["id"]: t["data"]["titulo"] for t in self.store.list()}
        days = []
        for offset in range(7):
            current = (monday + datetime.timedelta(days=offset)).isoformat()
            hours, _ = sheet.activity(self.store.root, current)
            entries = [dict(tarefa=k, titulo=titles.get(k, k), horas=round(v, 2)) for k, v in sorted(hours.items(), key=lambda i: -i[1])]
            days.append(dict(data=current, horas=round(sum(hours.values()), 2), tarefas=entries))
        return dict(inicio=monday.isoformat(), dias=days)

    def history(self, limit=200):
        entries = events.read_all(self.store.root, months=2)
        pending = {e["id"] for e in events.pending(self.store.root, months=2)}
        shown = entries[-limit:]
        for entry in shown:
            entry["pendente"] = entry["id"] in pending
        return dict(total=len(entries), pendentes=len(pending), eventos=list(reversed(shown)))

    # Exportação -------------------------------------------------------------
    def export(self, output):
        """Página única somente leitura com os dados embutidos, sem servidor."""
        html = (SITE / "index.html").read_text(encoding="utf-8")
        css = (SITE / "app.css").read_text(encoding="utf-8")
        js = (SITE / "app.js").read_text(encoding="utf-8")
        snapshot = dict(estado=self.state(), semana=self.week(), ficha=self.sheet(), historico=self.history())
        payload = json.dumps(snapshot, ensure_ascii=False).replace("</", "<\\/")
        html = html.replace('<link rel="stylesheet" href="app.css">', "<style>\n%s\n</style>" % css)
        html = html.replace('<link rel="manifest" href="manifest.webmanifest">', "")
        html = html.replace('<script src="app.js" defer></script>',
                            "<script>window.YABOOK_SNAPSHOT = %s;</script>\n<script>\n%s\n</script>" % (payload, js))
        html = html.replace("{{TOKEN}}", "")
        icon = base64.b64encode((SITE / "icon.svg").read_bytes()).decode("ascii")
        html = html.replace('"icon.svg"', '"data:image/svg+xml;base64,%s"' % icon)
        path = Path(output).expanduser()
        if path.is_dir() or not path.suffix:
            path = path / "yabook-tasks.html"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")
        return dict(arquivo=str(path.resolve()), tarefas=len(snapshot["estado"]["tarefas"]))


class Handler(BaseHTTPRequestHandler):
    server_version = "YABookTasks/1"
    board = None
    token = ""
    port = DEFAULT_PORT
    writer = None  # rotas de escrita registradas pela edição do site

    def log_message(self, *args):  # sem ruído no terminal
        pass

    def _allowed_host(self):
        host = (self.headers.get("Host") or "").lower()
        return host in ("127.0.0.1:%d" % self.port, "localhost:%d" % self.port)

    def _send(self, status, body, content_type="application/json; charset=utf-8", extra=None):
        data = body if isinstance(body, bytes) else (
            json.dumps(body, ensure_ascii=False).encode("utf-8") if not isinstance(body, str) else body.encode("utf-8"))
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, message):
        self._send(status, dict(error=message))

    def do_GET(self):
        if not self._allowed_host():
            return self._error(HTTPStatus.FORBIDDEN, "Host não permitido")
        url = urlparse(self.path)
        query = {k: v[-1] for k, v in parse_qs(url.query).items()}
        try:
            if url.path == "/api/estado":
                return self._send(HTTPStatus.OK, self.board.state())
            if url.path.startswith("/api/tarefa/"):
                return self._send(HTTPStatus.OK, self.board.task(unquote(url.path[len("/api/tarefa/"):])))
            if url.path == "/api/ficha":
                return self._send(HTTPStatus.OK, self.board.sheet(query.get("data"), query.get("semana") == "1"))
            if url.path == "/api/semana":
                return self._send(HTTPStatus.OK, self.board.week(query.get("data")))
            if url.path == "/api/historico":
                return self._send(HTTPStatus.OK, self.board.history(int(query.get("limite", 200))))
            if url.path == "/api/stream":
                return self._stream()
        except KeyError as error:
            return self._error(HTTPStatus.NOT_FOUND, str(error).strip("'\""))
        except ValueError as error:
            return self._error(HTTPStatus.BAD_REQUEST, str(error))
        return self._static(url.path)

    def do_POST(self):
        if not self._allowed_host():
            return self._error(HTTPStatus.FORBIDDEN, "Host não permitido")
        origin = self.headers.get("Origin")
        if origin and origin.lower() not in ("http://127.0.0.1:%d" % self.port, "http://localhost:%d" % self.port):
            return self._error(HTTPStatus.FORBIDDEN, "Origem não permitida")
        if not self.token or not secrets.compare_digest(self.headers.get("X-YABook-Token", ""), self.token):
            return self._error(HTTPStatus.FORBIDDEN, "Token da página ausente ou inválido; recarregue")
        if self.writer is None:
            return self._error(HTTPStatus.NOT_FOUND, "Escrita indisponível")
        length = int(self.headers.get("Content-Length") or 0)
        if length > 2_000_000:
            return self._error(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Requisição grande demais")
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            status, result = self.writer(self.board, urlparse(self.path).path, body)
        except (ValueError, KeyError) as error:
            return self._error(HTTPStatus.BAD_REQUEST, str(error).strip("'\""))
        except Exception as error:  # nunca derruba a conexão sem resposta
            return self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "%s: %s" % (type(error).__name__, error))
        return self._send(status, result)

    def _static(self, path):
        name = "index.html" if path in ("/", "/index.html") else path.lstrip("/")
        if name not in SHELL:
            return self._error(HTTPStatus.NOT_FOUND, "Não encontrado")
        file = SITE / name
        content_type = "application/manifest+json" if name.endswith(".webmanifest") else (
            mimetypes.guess_type(name)[0] or "application/octet-stream")
        if content_type.startswith("text/") or content_type.endswith(("javascript", "json")):
            content_type += "; charset=utf-8"
        data = file.read_bytes()
        if name == "index.html":
            data = data.replace(b"{{TOKEN}}", self.token.encode())
        extra = {"Service-Worker-Allowed": "/"} if name == "sw.js" else None
        return self._send(HTTPStatus.OK, data, content_type, extra)

    def _stream(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        last, last_ping = self.board.fingerprint(), time.monotonic()
        try:
            self.wfile.write(("event: pronto\ndata: %s\n\n" % last).encode())
            self.wfile.flush()
            while not getattr(self.server, "stopping", False):
                time.sleep(getattr(self.server, "poll_seconds", POLL_SECONDS))
                current = self.board.fingerprint()
                if current != last:
                    last = current
                    self.wfile.write(("event: mudou\ndata: %s\n\n" % current).encode())
                    self.wfile.flush()
                elif time.monotonic() - last_ping >= PING_SECONDS:
                    last_ping = time.monotonic()
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            return


def make_server(store, cfg=None, port=None, poll_seconds=POLL_SECONDS, writer=None):
    """Cria o servidor sem iniciá-lo; porta 0 escolhe uma livre (testes)."""
    cfg = cfg or {}
    board = Board(store, cfg)
    handler = type("BoundHandler", (Handler,), dict(board=board, token=secrets.token_urlsafe(24),
                                                    writer=staticmethod(writer) if writer else None))
    server = ThreadingHTTPServer(("127.0.0.1", DEFAULT_PORT if port is None else port), handler)
    server.daemon_threads = True
    server.poll_seconds = poll_seconds
    handler.port = server.server_address[1]
    return server


def serve(store, cfg=None, port=None, writer=None):
    server = make_server(store, cfg, port or (cfg or {}).get("port") or DEFAULT_PORT, writer=writer)
    url = "http://127.0.0.1:%d/" % server.server_address[1]
    print(json.dumps(dict(url=url, pid=os.getpid()), ensure_ascii=False), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.stopping = True
        server.server_close()
    return dict(url=url, encerrado=True)


def start_background(server):
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return thread
