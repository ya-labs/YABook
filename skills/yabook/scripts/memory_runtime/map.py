"""Mapa local somente leitura da mesma base canônica usada pelo agente."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from .core import digest, read_json
from .sources import all_entries


def hierarchy(nodes, links):
    """Um pai de navegação por localização; vínculos múltiplos continuam no grafo."""
    by_id = {n["id"]: n for n in nodes}
    candidates = {n["id"]: [] for n in nodes}
    for link in links:
        if link["type"] != "contains":
            continue
        parent, child = by_id[link["source"]], by_id[link["target"]]
        pentry, centry = parent.get("entry", {}), child.get("entry", {})
        if parent["kind"] != "scope" and pentry.get("collection") != "groups":
            continue
        pscope, cscope = pentry.get("scope", parent.get("scope", [])), centry.get("scope", child.get("scope", []))
        if cscope[:len(pscope)] != pscope:
            continue
        explicit = bool(centry.get("parent") and centry["parent"] == pentry.get("id"))
        # Pai explícito, grupo mais específico, depois localização sintética.
        priority = (3 if explicit else 2 if pentry else 1, len(pscope),
                    {"topic": 3, "collection": 2, "project": 1}.get(pentry.get("kind"), 0))
        candidates[child["id"]].append((priority, parent["id"]))
    parents = {}
    for identifier in sorted(by_id):
        for _, parent in sorted(candidates[identifier], key=lambda c: (tuple(-v for v in c[0]), c[1])):
            cursor, seen = parent, {identifier}
            while cursor is not None and cursor not in seen:
                seen.add(cursor)
                cursor = parents.get(cursor)
            if cursor is None:
                parents[identifier] = parent
                break
        by_id[identifier]["tree_parent"] = parents.get(identifier)


def map_data(vault, includes=()):
    entries = all_entries(vault, includes)
    # Datas vêm do histórico canônico, nunca do mtime do checkout/sync.
    dates = {}
    for path in (vault.root / "history").glob("*.json"):
        receipt = read_json(path)
        stamp = receipt.get("created_at")
        if not stamp:
            continue
        for change in receipt.get("changes", []):
            if not change.get("after"):
                continue
            key = (change.get("collection"), change.get("id"))
            item = dates.setdefault(key, {})
            item["updated_at"] = max(stamp, item.get("updated_at", stamp))
            if change.get("before") is None:
                item["created_at"] = min(stamp, item.get("created_at", stamp))
    nodes, links, seen = [], [], set()
    def node(identifier, title, kind, **values):
        if identifier not in seen:
            seen.add(identifier); nodes.append(dict(id=identifier,title=title,kind=kind,**values))
    for entry in entries:
        namespace = entry.get("source", "own")
        identifier = namespace + ":" + entry["id"]
        parent = None
        for index, part in enumerate(entry["scope"]):
            group = "scope:" + digest(entry["scope"][:index+1])[:16]
            node(group, part, "scope", scope=entry["scope"][:index+1])
            if parent: links.append(dict(source=parent,target=group,type="contains"))
            parent = group
        entry_dates = {key: entry[key] for key in ("created_at", "updated_at", "last_verified") if entry.get(key)}
        if namespace == "own":
            entry_dates.update(dates.get((entry["collection"], entry["id"]), {}))
        node(identifier, entry["title"], entry["collection"], entry=entry, dates=entry_dates)
        if parent: links.append(dict(source=parent,target=identifier,type="contains"))
        if entry.get("parent"):
            links.append(dict(source=namespace+":"+entry["parent"],target=identifier,type="contains"))
        for target in entry.get("members", []):
            links.append(dict(source=identifier,target=namespace+":"+target,type="contains"))
        for target in entry.get("entities", []) + entry.get("episodes", []) + entry.get("learnings", []):
            links.append(dict(source=identifier,target=namespace+":"+target,type="references"))
        for relation in entry.get("relations", []):
            links.append(dict(source=identifier,target=namespace+":"+relation["target"],type=relation["type"],
                              suggested=relation.get("suggested",False)))
    unique = {(e['source'],e['target'],e['type']): e for e in links if e['source'] in seen and e['target'] in seen}
    hierarchy(nodes, list(unique.values()))
    return dict(schema_version=1,revision=digest(vault.snapshot()),nodes=nodes,links=list(unique.values()))


def html(data):
    template = (Path(__file__).parent / "map.html").read_text(encoding="utf-8")
    payload = json.dumps(data,ensure_ascii=False).replace("<","\\u003c").replace("&","\\u0026")
    return template.replace("__YABOOK_DATA__", payload)


def export_map(vault, output, includes=()):
    path = Path(output).expanduser().resolve()
    if path.exists(): raise ValueError("Destino existente; escolha novo arquivo de exportação")
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(html(map_data(vault,includes)),encoding="utf-8")
    return dict(output=str(path),mode="snapshot-read-only")


def query_map(vault, query, includes=()):
    """Consulta manual explicável, sem registrar entrega ao agente nem escrever índices."""
    from .search import search
    query = query.strip()
    if not query or len(query) > 1000:
        raise ValueError("Informe uma consulta de 1 a 1.000 caracteres")
    result = search(vault, query, includes, limit=12, budget=100000, explain=True)
    return dict(result, query=query, revision=digest(vault.snapshot()), manual=True)


def serve(vault, port=8765, includes=()):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.headers.get("Origin") not in (None,f"http://127.0.0.1:{port}"):
                self.send_error(403);return
            parsed = urlparse(self.path)
            if parsed.path not in ("/", "/api/map", "/api/query"):
                self.send_error(404);return
            try:
                if parsed.path == "/api/query":
                    query = parse_qs(parsed.query).get("q", [""])[0]
                    if not query.strip() or len(query.strip()) > 1000:
                        self.send_error(400, "Consulta vazia ou muito longa");return
                    payload = json.dumps(query_map(vault, query, includes), ensure_ascii=False).encode()
                else:
                    data=map_data(vault,includes)
                    payload=(json.dumps(data,ensure_ascii=False) if parsed.path=="/api/map" else html(data)).encode()
            except (ValueError,OSError,KeyError):
                self.send_error(503,"Memória indisponível");return
            self.send_response(200)
            self.send_header("Content-Type","application/json; charset=utf-8" if parsed.path.startswith("/api/") else "text/html; charset=utf-8")
            self.send_header("Cache-Control","no-store")
            self.send_header("X-Content-Type-Options","nosniff")
            self.send_header("Content-Security-Policy","default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'")
            self.end_headers();self.wfile.write(payload)
        def log_message(self,*args): pass
    server=ThreadingHTTPServer(("127.0.0.1",port),Handler)
    print(f"Mapa somente leitura: http://127.0.0.1:{port}",flush=True)
    try: server.serve_forever()
    finally: server.server_close()
