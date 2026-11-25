"""Sessões de diff: a versão de cada arquivo antes da primeira edição do agente na sessão.

Layout: `<base>/<projeto>/<sessão>/manifest.json` e `antes/<caminho relativo>`. A cópia mantém a
extensão original para o VS Code aplicar a mesma associação de linguagem e encoding (ex.: ABL em
ISO-8859-1). Nada aqui chama modelo: a captura roda no hook, sem custo de tokens.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import time
from datetime import datetime
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    ZONE = ZoneInfo("America/Sao_Paulo")
except Exception:  # pragma: no cover - zoneinfo ausente só em Python antigo
    ZONE = None

VERSION = 1
RETENTION_DAYS = 14
BACKUP_PATTERN = r"\.bak-\d{8}-\d{6}(?:-[^/\\]*)?$"
OUTSIDE = "_externos"


def now_iso(stamp=None):
    moment = datetime.fromtimestamp(stamp if stamp is not None else time.time(), ZONE)
    return moment.isoformat(timespec="seconds")


def settings(cfg):
    """Configuração `diff` do YABook com padrões seguros."""
    diff = cfg.get("diff", {}) if isinstance(cfg.get("diff"), dict) else {}
    config_dir = Path(os.environ.get("YABOOK_CONFIG", str(Path.home() / ".config/yabook/config.json"))).expanduser().parent
    base = os.environ.get("YABOOK_DIFFS") or diff.get("dir") or str(config_dir / "diffs")
    commands = diff.get("commands")
    if not isinstance(commands, list):
        commands = cfg.get("learning", {}).get("edit_commands", []) if isinstance(cfg.get("learning"), dict) else []
    backups = diff.get("backups")
    if not isinstance(backups, list):
        backups = [{"dir": "backup", "pattern": BACKUP_PATTERN}]
    return dict(base=Path(base).expanduser(), enabled=diff.get("enabled", True) is not False,
                shell=diff.get("shell", True) is not False,
                retention=int(diff.get("retention_days", RETENTION_DAYS)),
                commands=[c for c in commands if isinstance(c, str) and c], backups=backups)


def project_key(root):
    root = str(Path(root).resolve())
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", Path(root).name).strip("-") or "projeto"
    return name + "-" + hashlib.sha256(root.encode()).hexdigest()[:8]


def session_key(event):
    agent, session = event.get("agent", ""), event.get("session_id", "")
    if not isinstance(session, str) or not session:
        raise ValueError("Evento sem sessão")
    return hashlib.sha256((agent + "\0" + session).encode()).hexdigest()[:16]


def relative(path, root):
    """Caminho dentro do projeto; fora dele, sob `_externos/` para não colidir."""
    path, root = Path(path).resolve(), Path(root).resolve()
    if path == root or root in path.parents:
        return path.relative_to(root).as_posix()
    return OUTSIDE + "/" + path.as_posix().lstrip("/")


def read_manifest(folder):
    path = Path(folder) / "manifest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_manifest(folder, data):
    path = Path(folder) / "manifest.json"
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


class Session:
    """Sessão de diff de um projeto; criada na primeira captura."""

    def __init__(self, base, root, key, agent="", scripts=None, title=None):
        self.root = str(Path(root).resolve())
        self.folder = Path(base) / project_key(self.root) / key
        self.key, self.agent = key, agent or ""
        self.scripts = str(scripts or Path(__file__).resolve().parents[1])
        self.title = title or None  # nome do chat do agente, quando conhecido

    def manifest(self):
        current = read_manifest(self.folder)
        if current:
            if self.title and current.get("titulo") != self.title:
                current["titulo"] = self.title  # chat renomeado: vale o nome mais recente
            return current
        stamp = now_iso()
        data = dict(versao=VERSION, projeto=self.root, agente=self.agent, sessao=self.key, criada=stamp,
                    atualizada=stamp, scripts=self.scripts, arquivos=[])
        if self.title:
            data["titulo"] = self.title
        return data

    def has(self, rel):
        current = read_manifest(self.folder)
        return bool(current) and any(item["caminho"] == rel for item in current["arquivos"])

    def record(self, target, source=None, origin="copia"):
        """Guarda a versão anterior de `target` uma única vez; `source` ausente marca arquivo novo."""
        rel = relative(target, self.root)
        if self.has(rel):
            return False
        data = self.manifest()
        before = "antes/" + rel
        destination = self.folder / before
        destination.parent.mkdir(parents=True, exist_ok=True)
        new = source is None or not Path(source).exists()
        if not new:
            shutil.copy2(source, destination)
        data["arquivos"].append(dict(caminho=rel, antes=None if new else before, novo=new, origem=origin,
                                     capturado=now_iso()))
        data["atualizada"] = now_iso()
        write_manifest(self.folder, data)
        return True

    def record_round(self, round_info, target, source=None, origin="copia"):
        """Guarda a versão anterior na primeira edição do arquivo dentro da rodada (mensagem da pessoa)."""
        if not round_info or not round_info.get("chave"):
            return False
        rel = relative(target, self.root)
        data = self.manifest()
        rounds = data.setdefault("rodadas", [])
        if not rounds or rounds[-1].get("chave") != round_info["chave"]:
            rounds.append(dict(numero=len(rounds) + 1, chave=round_info["chave"], inicio=now_iso(),
                               pedido=round_info.get("pedido", ""), arquivos=[]))
        current = rounds[-1]
        if any(item["caminho"] == rel for item in current["arquivos"]):
            return False
        before = "rodadas/%d/antes/%s" % (current["numero"], rel)
        new = source is None or not Path(source).exists()
        if not new:
            destination = self.folder / before
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        current["arquivos"].append(dict(caminho=rel, antes=None if new else before, novo=new, origem=origin,
                                        capturado=now_iso()))
        data["atualizada"] = now_iso()
        write_manifest(self.folder, data)
        return True


def session_title(data):
    """Nome para mostrar: título do chat; sem ele, a primeira mensagem com edição; senão vazio."""
    rounds = data.get("rodadas") or []
    return data.get("titulo") or (rounds[0].get("pedido") if rounds else "") or ""


def view_items(data, view=None):
    """Arquivos da visão: `sessao` (tudo), `ultima` (padrão, última rodada) ou o número de uma rodada.

    Sessão sem rodadas (gravada antes delas) cai na sessão inteira. Devolve (chave da visão, itens)."""
    rounds = data.get("rodadas") or []
    if view == "sessao" or not rounds:
        return "sessao", data["arquivos"]
    if view in (None, "", "ultima"):
        chosen = rounds[-1]
    else:
        chosen = next((r for r in rounds if str(r["numero"]) == str(view)), None)
        if chosen is None:
            raise ValueError("Rodada não encontrada: %s (há %d)" % (view, len(rounds)))
    # O "depois" de uma rodada antiga é o "antes" do arquivo na próxima rodada que o editou.
    later = rounds[rounds.index(chosen) + 1:]
    items = []
    for item in chosen["arquivos"]:
        following = next((i for r in later for i in r["arquivos"] if i["caminho"] == item["caminho"]), None)
        items.append(dict(item, depois=following["antes"]) if following else item)
    return "rodada-%d" % chosen["numero"], items


def target(root, rel):
    """Arquivo atual correspondente a um caminho do manifesto."""
    if rel.startswith(OUTSIDE + "/"):
        return Path("/" + rel[len(OUTSIDE) + 1:])
    return Path(root) / rel


def prune(base, retention_days, keep=None, now=None):
    """Remove sessões sem atualização além do prazo de guarda."""
    base, limit = Path(base), (now or time.time()) - retention_days * 86400
    removed = 0
    if not base.exists():
        return removed
    for project in base.iterdir():
        if not project.is_dir():
            continue
        for folder in project.iterdir():
            manifest = folder / "manifest.json"
            if folder == keep or not folder.is_dir():
                continue
            stamp = manifest.stat().st_mtime if manifest.exists() else folder.stat().st_mtime
            if stamp < limit:
                shutil.rmtree(folder, ignore_errors=True)
                removed += 1
        if not any(project.iterdir()):
            project.rmdir()
    return removed


def sessions(base, root):
    """Sessões do projeto, da mais recente para a mais antiga."""
    folder = Path(base) / project_key(root)
    found = []
    for child in folder.iterdir() if folder.exists() else ():
        data = read_manifest(child) if child.is_dir() else None
        if data:
            found.append((data.get("atualizada", ""), child, data))
    return [(child, data) for _, child, data in sorted(found, key=lambda row: row[0], reverse=True)]
