"""Conhecimento canônico, propostas revisáveis e histórico imutável por revisão."""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

COLLECTIONS = ("records", "entities", "groups", "episodes")
SCHEMA_VERSION = 2
RECORD_KINDS = ("profile", "preference", "procedure", "knowledge")
STATES = ("hypothesis", "confirmed", "superseded", "archived")
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}$")
EVIDENCE_TYPES = ("code", "commit", "test", "build", "system", "document", "conversation", "session")
# Níveis não são equivalentes: inspeção estática não comprova execução em APK/ERP.
EVIDENCE_LEVELS = ("static", "automated", "runtime", "manual", "statement", "reported")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
HASH = re.compile(r"^[0-9a-f]{64}$")
LINES = re.compile(r"^\d+(?:-\d+)?$")
# Campos controlados pelo runtime; não contam como remoção em atualização.
MANAGED = ("id", "revision", "origin")
SECRET = re.compile(r"(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN .*PRIVATE KEY-----)")


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".writing-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def scoped(scope, includes=(), excludes=()):
    """Prefixos são componentes, nunca substring ou prefixo de nome."""
    def matches(prefix):
        return scope[:len(prefix)] == prefix
    return (not includes or any(matches(p) for p in includes)) and not any(
        matches(p) for p in excludes)


def snapshot_entries(snapshot):
    """Visão de conhecimento vigente, sem reescrever bases ou resumos."""
    values = {i: e for c in COLLECTIONS for i, e in snapshot[c].items()}
    def stale(entry, visited):
        if entry["id"] in visited: return True
        visited = visited | {entry["id"]}
        for identifier, revision in entry.get("summary_sources", {}).items():
            member = values.get(identifier)
            if not member or member.get("revision") != revision or member.get("state") in ("archived", "superseded"):
                return True
            if member.get("summary") and stale(member, visited): return True
        return False
    for collection in COLLECTIONS:
        for entry in snapshot[collection].values():
            item = dict(entry, collection=collection, source="own")
            if collection == "records": item.setdefault("kind", "knowledge")
            if collection == "groups": item.setdefault("kind", "collection")
            if collection == "groups" and entry.get("summary") and stale(entry, set()):
                item.pop("summary", None); item["summary_stale"] = True
            yield item


def check_evidence(entry):
    """Evidência estruturada exigida em itens escritos; leitura aceita formato legado."""
    for item in entry.get("evidence", []):
        if not isinstance(item, dict) or item.get("type") not in EVIDENCE_TYPES or item.get("level") not in EVIDENCE_LEVELS:
            raise ValueError("Evidência precisa de type e level válidos")
        if not isinstance(item.get("ref"), str) or not item["ref"].strip():
            raise ValueError("Evidência precisa de referência")
        if "date" in item and not (isinstance(item["date"], str) and DATE.fullmatch(item["date"])):
            raise ValueError("Data de evidência inválida (AAAA-MM-DD)")
    provenance = entry.get("provenance", [])
    if not isinstance(provenance, list):
        raise ValueError("Procedência precisa ser lista")
    for item in provenance:
        if not isinstance(item, dict) or not all(isinstance(item.get(k), str) and item[k].strip() for k in ("agent", "file")):
            raise ValueError("Procedência precisa de agent e file")
        if not isinstance(item.get("hash"), str) or not HASH.fullmatch(item["hash"]):
            raise ValueError("Procedência precisa de hash SHA-256 do snapshot")
        if "lines" in item and not (isinstance(item["lines"], str) and LINES.fullmatch(item["lines"])):
            raise ValueError("Intervalo de linhas inválido")


def stale_groups(snapshot):
    return {e["id"] for e in snapshot_entries(snapshot) if e["collection"] == "groups" and e.get("summary_stale")}


class Vault:
    def __init__(self, root):
        self.root = Path(root).expanduser().resolve()
        self.local = self.root / ".yabook-local"
        self._mutex = threading.RLock()
        self._lock_depth = 0

    def path(self, collection, identifier):
        if collection not in COLLECTIONS or not isinstance(identifier, str) or not ID.fullmatch(identifier):
            raise ValueError("Coleção ou identificador inválido")
        path = self.root / collection / (identifier + ".json")
        if (self.root / collection).is_symlink() or path.resolve().parent != (self.root / collection).resolve() or path.is_symlink():
            raise ValueError("Caminho canônico inválido")
        return path

    def bootstrap(self, owner):
        if not isinstance(owner, str) or not ID.fullmatch(owner):
            raise ValueError("Proprietário inválido")
        if (self.root / "memory.json").exists():
            metadata = read_json(self.root / "memory.json")
            if metadata["owner"] != owner or metadata["schema_version"] not in (1, SCHEMA_VERSION):
                raise ValueError("Base existente pertence a outro proprietário/formato")
            return metadata
        if self.root.exists() and any(self.root.iterdir()):
            raise ValueError("Destino não vazio; não sobrescrever uma base desconhecida")
        self.root.mkdir(parents=True, exist_ok=True)
        metadata = {"schema_version": SCHEMA_VERSION, "vault_id": str(uuid.uuid4()), "owner": owner,
                    "created_at": now()}
        write_json(self.root / "memory.json", metadata)
        for collection in COLLECTIONS + ("history",):
            (self.root / collection).mkdir(exist_ok=True)
        (self.root / ".gitignore").write_text(".yabook-local/\n__pycache__/\n", encoding="utf-8")
        return metadata

    @contextlib.contextmanager
    def lock(self):
        import fcntl
        with self._mutex:
            if self._lock_depth:
                yield
                return
            self.local.mkdir(parents=True, exist_ok=True)
            with (self.local / "lock").open("a") as stream:
                fcntl.flock(stream, fcntl.LOCK_EX)
                self._lock_depth += 1
                try:
                    yield
                finally:
                    self._lock_depth -= 1
                    fcntl.flock(stream, fcntl.LOCK_UN)

    def snapshot(self):
        with self.lock():
            if (self.local / "transaction.json").exists():
                raise ValueError("Transação interrompida; recuperar antes de consultar")
            return self._snapshot()

    def _snapshot(self):
        metadata = read_json(self.root / "memory.json")
        if metadata.get("schema_version") not in (1, SCHEMA_VERSION):
            raise ValueError("Formato de memória não suportado")
        data = {c: {} for c in COLLECTIONS}
        for collection in COLLECTIONS:
            if (self.root / collection).is_symlink():
                raise ValueError("Symlink em coleção canônica")
            for path in sorted((self.root / collection).glob("*.json")):
                if path.is_symlink():
                    raise ValueError("Symlink em armazenamento canônico")
                entry = read_json(path)
                if entry.get("id") != path.stem:
                    raise ValueError("ID e arquivo divergentes")
                data[collection][path.stem] = entry
        return {"metadata": metadata, **data}

    def validate(self, snapshot):
        ids = {identifier for c in COLLECTIONS for identifier in snapshot[c]}
        if len(ids) != sum(len(snapshot[c]) for c in COLLECTIONS):
            raise ValueError("IDs devem ser únicos na base")
        for collection in COLLECTIONS:
            for identifier, entry in snapshot[collection].items():
                self.path(collection, identifier)
                if entry.get("id") != identifier or not entry.get("title", "").strip():
                    raise ValueError("Registro sem ID/título")
                scope = entry.get("scope")
                if not isinstance(scope, list) or not scope or not all(isinstance(s, str) and s.strip() for s in scope):
                    raise ValueError("Escopo precisa de componentes explícitos")
                if SECRET.search(json.dumps(entry)):
                    raise ValueError("Possível credencial no conteúdo")
                if any(k in entry for k in ("authorization", "permission_mode", "session_grant")):
                    raise ValueError("Autorização operacional não pertence à memória")
                if entry.get("state", "confirmed") not in STATES:
                    raise ValueError("Situação inválida")
                if "priority" in entry and (type(entry["priority"]) is not int or not 0 <= entry["priority"] <= 100):
                    raise ValueError("Prioridade precisa ser inteiro entre 0 e 100")
                if entry.get("project_id"):
                    project = snapshot["groups"].get(entry["project_id"])
                    if not project or project.get("kind") != "project" or entry["scope"][:len(project["scope"])] != project["scope"]:
                        raise ValueError("Projeto inválido ou fora do escopo")
                for field in ("keywords", "aliases", "triggers"):
                    if field in entry and (not isinstance(entry[field], list) or
                                          not all(isinstance(x, str) and x.strip() for x in entry[field])):
                        raise ValueError("Termos de busca inválidos: " + field)
                if not isinstance(entry.get("evidence", []), list):
                    raise ValueError("Evidência precisa ser lista")
                if collection == "records":
                    if entry.get("kind", "knowledge") not in RECORD_KINDS:
                        raise ValueError("Tipo de memória inválido")
                    if entry.get("authority", "inferred") not in ("explicit", "inferred"):
                        raise ValueError("Origem da preferência inválida")
                    if entry.get("activation", "conditional") not in ("always", "conditional"):
                        raise ValueError("Ativação inválida")
                    if entry.get("activation") == "always" and entry.get("kind") in ("preference", "procedure") and entry.get("authority") != "explicit":
                        raise ValueError("Aplicação permanente exige preferência explícita")
                    if not entry.get("content", "").strip() or not entry.get("application", "").strip():
                        raise ValueError("Conhecimento precisa de conteúdo e aplicação")
                    if entry.get("state") == "confirmed" and not entry.get("evidence"):
                        raise ValueError("Conhecimento confirmado precisa de evidência")
                if collection == "episodes":
                    for field in ("objective", "context", "outcome"):
                        if not isinstance(entry.get(field), str) or not entry[field].strip():
                            raise ValueError("Experiência incompleta: " + field)
                    for field in ("actions", "validation"):
                        if not isinstance(entry.get(field), list) or not entry[field] or not all(isinstance(x, str) and x.strip() for x in entry[field]):
                            raise ValueError("Experiência incompleta: " + field)
                    if entry.get("state") == "confirmed" and not entry.get("evidence"):
                        raise ValueError("Experiência confirmada precisa de evidência")
                for reference in entry.get("members", []) + entry.get("entities", []) + entry.get("episodes", []) + entry.get("learnings", []):
                    if reference not in ids:
                        raise ValueError("Referência inexistente: " + reference)
                if any(i not in snapshot["episodes"] for i in entry.get("episodes", [])):
                    raise ValueError("Experiência precisa referenciar episodes")
                if any(i not in snapshot["records"] for i in entry.get("learnings", [])):
                    raise ValueError("Aprendizado precisa referenciar records")
                for relation in entry.get("relations", []):
                    if relation.get("target") not in ids or not relation.get("type"):
                        raise ValueError("Relação inválida")
                if collection == "groups" and entry.get("summary"):
                    if set(entry.get("summary_sources", {})) != set(entry.get("members", [])):
                        raise ValueError("Resumo precisa referenciar todos os membros")
                if collection == "groups":
                    if entry.get("kind", "collection") not in ("project", "topic", "collection"):
                        raise ValueError("Tipo de grupo inválido")
                    visited = {identifier}
                    parent = entry.get("parent")
                    child = entry
                    while parent:
                        if parent in visited or parent not in snapshot["groups"]:
                            raise ValueError("Hierarquia de grupos cíclica ou inexistente")
                        ancestor = snapshot["groups"][parent]
                        if child["scope"][:len(ancestor["scope"])] != ancestor["scope"]:
                            raise ValueError("Grupo filho fora do escopo do pai")
                        visited.add(parent); parent = ancestor.get("parent"); child = ancestor

    def prepare(self, changes, assessment, actor, expected_base_hash=None):
        required = ("verdict", "reason", "utility", "application", "evidence_status")
        if not all(isinstance(assessment.get(k), str) and assessment[k].strip() for k in required):
            raise ValueError("Avaliação do agente incompleta")
        if assessment["verdict"] not in ("add", "update", "relate", "archive", "delete"):
            raise ValueError("Veredito não executável; manter/rejeitar não gera proposta")
        if not changes:
            raise ValueError("Proposta vazia")
        with self.lock():
            before = self.snapshot()
            if expected_base_hash is not None and digest(before) != expected_base_hash:
                raise ValueError("Base mudou durante a curadoria; reavaliar aprendizado")
            proposed = json.loads(json.dumps(before))
            touched = set()
            previous = {}
            for change in changes:
                collection, identifier = change["collection"], change["id"]
                self.path(collection, identifier)
                if (collection, identifier) in touched:
                    raise ValueError("Registro repetido na proposta")
                touched.add((collection, identifier))
                previous[collection + "/" + identifier] = before[collection].get(identifier)
                if change.get("delete"):
                    if identifier not in proposed[collection]:
                        raise ValueError("Não é possível remover registro ausente")
                    del proposed[collection][identifier]
                else:
                    entry = dict(change["value"])
                    old = before[collection].get(identifier, {})
                    # Valor completo: omitir campo existente exige declaração explícita.
                    removed = change.get("remove_fields", [])
                    if not isinstance(removed, list) or not all(isinstance(f, str) for f in removed):
                        raise ValueError("remove_fields precisa ser lista de campos")
                    if set(removed) & (set(entry) | set(MANAGED)):
                        raise ValueError("Campo declarado para remoção continua no valor ou é controlado pelo runtime")
                    if set(removed) - set(old):
                        raise ValueError("Campo declarado para remoção não existe: " + ", ".join(sorted(set(removed) - set(old))))
                    omitted = set(old) - set(entry) - set(MANAGED) - set(removed)
                    if omitted:
                        raise ValueError("Atualização omite campos existentes sem remove_fields: " + ", ".join(sorted(omitted)))
                    check_evidence(entry)
                    entry.update(id=identifier, revision=old.get("revision", 0) + 1)
                    entry.setdefault("origin", old.get("origin", {"vault_id": before["metadata"]["vault_id"], "id": identifier}))
                    proposed[collection][identifier] = entry
            # A atualização de formato é parte da proposta, nunca efeito de uma leitura.
            if any(c["collection"] == "episodes" or any(k in c.get("value", {}) for k in
                   ("kind", "parent", "keywords", "aliases", "triggers", "activation", "episodes")) for c in changes):
                proposed["metadata"]["schema_version"] = SCHEMA_VERSION
            self.validate(proposed)
            stale = sorted(stale_groups(proposed) - stale_groups(before))
            from .views import render_views
            derived = render_views(proposed)
            affected_views = [p for p, content in derived.items() if not (self.root / p).exists() or
                              (self.root / p).read_text(encoding="utf-8") != content]
            affected_views += [p.relative_to(self.root).as_posix() for p in (self.root / "views/topics").glob("*.md")
                               if p.relative_to(self.root).as_posix() not in derived]
            proposal = {"id": "P-" + uuid.uuid4().hex[:16], "base_hash": digest(before),
                        "created_at": now(), "actor": actor, "assessment": assessment,
                        "changes": changes, "previous": previous, "result": proposed,
                        "stale_summaries": stale, "derived_views": sorted(affected_views)}
            if proposed["metadata"] != before["metadata"]:
                proposal["previous_metadata"] = before["metadata"]
            proposal["approval_hash"] = digest(proposal)
            write_json(self.local / "proposals" / (proposal["id"] + ".json"), proposal)
            return proposal

    def proposal(self, identifier=None):
        pending = sorted((self.local / "proposals").glob("P-*.json"))
        if identifier is None:
            if len(pending) != 1:
                raise ValueError("Informe o ID: nenhuma proposta ou aprovação ambígua")
            path = pending[0]
        else:
            if not ID.fullmatch(identifier):
                raise ValueError("ID inválido")
            path = self.local / "proposals" / (identifier + ".json")
        proposal = read_json(path)
        value = dict(proposal)
        expected = value.pop("approval_hash")
        if digest(value) != expected:
            raise ValueError("Proposta foi alterada; prepare nova prévia")
        return proposal

    def apply(self, identifier, approval_hash):
        with self.lock():
            if (self.local / "transaction.json").exists():
                raise ValueError("Transação interrompida; execute recover antes de continuar")
            proposal = self.proposal(identifier)
            if approval_hash != proposal["approval_hash"]:
                raise ValueError("Aprovação não corresponde ao conteúdo apresentado")
            if digest(self.snapshot()) != proposal["base_hash"]:
                raise ValueError("Base mudou; reavaliar proposta")
            self.validate(proposal["result"])
            write_json(self.local / "transaction.json", proposal)
            return self._finish(proposal)

    def _finish(self, proposal):
        paths = [str(self.path(c["collection"], c["id"]).relative_to(self.root)) for c in proposal["changes"]]
        metadata_path = self.root / "memory.json"
        if read_json(metadata_path) != proposal["result"]["metadata"]:
            write_json(metadata_path, proposal["result"]["metadata"])
            paths.append("memory.json")
        for collection in COLLECTIONS:
            expected = proposal["result"][collection]
            for path in (self.root / collection).glob("*.json"):
                if path.stem not in expected:
                    path.unlink()
                    paths.append(str(path.relative_to(self.root)))
            for identifier, value in expected.items():
                path = self.path(collection, identifier)
                if not path.exists() or read_json(path) != value:
                    write_json(path, value)
                    paths.append(str(path.relative_to(self.root)))
        # Histórico permanente proporcional aos itens alterados; o journal mantém o resultado completo.
        items = [dict(collection=c["collection"], id=c["id"], delete=bool(c.get("delete")),
                      remove_fields=c.get("remove_fields", []),
                      before=proposal.get("previous", {}).get(c["collection"] + "/" + c["id"]),
                      after=proposal["result"][c["collection"]].get(c["id"])) for c in proposal["changes"]]
        receipt = {"proposal": proposal["id"], "approval_hash": proposal["approval_hash"],
                   "created_at": proposal["created_at"],
                   "actor": proposal["actor"], "assessment": proposal["assessment"],
                   "changes": items, "base_hash": proposal["base_hash"],
                   "result_hash": digest(proposal["result"])}
        if "previous_metadata" in proposal:
            receipt["metadata"] = dict(before=proposal["previous_metadata"], after=proposal["result"]["metadata"])
        history = self.root / "history" / (proposal["id"] + ".json")
        write_json(history, receipt)
        paths.append(str(history.relative_to(self.root)))
        from .views import write_views
        paths.extend(write_views(self, proposal["result"]))
        if (self.root / ".git").exists():
            from .gitstore import publication_intent, git
            if git(self.root, "rev-parse", "--verify", "HEAD", check=False).returncode:
                paths += ["memory.json", ".gitignore"]
            publication_intent(self, paths, "docs: aplica memória " + proposal["id"])
        pending = self.local / "proposals" / (proposal["id"] + ".json")
        pending.unlink(missing_ok=True)
        (self.local / "transaction.json").unlink(missing_ok=True)
        return {"proposal": proposal["id"], "paths": sorted(set(paths)), "result_hash": receipt["result_hash"],
                "stale_summaries": proposal.get("stale_summaries", [])}

    def recover(self):
        with self.lock():
            proposal = read_json(self.local / "transaction.json")
            value = dict(proposal)
            expected = value.pop("approval_hash")
            if digest(value) != expected:
                raise ValueError("Journal alterado")
            self.validate(proposal["result"])
            return self._finish(proposal)

    def entries(self, includes=(), excludes=(), include_archived=False):
        snapshot = self.snapshot()
        self.validate(snapshot)
        for item in snapshot_entries(snapshot):
            if scoped(item["scope"], includes, excludes) and (include_archived or item.get("state") not in ("archived", "superseded")):
                yield item

    def review(self):
        seen, findings = {}, []
        for path in sorted((self.local / "proposals").glob("P-*.json")):
            proposal = self.proposal(path.stem)
            findings.append({"kind": "pending_proposal", "id": proposal["id"],
                             "reasons": proposal["assessment"].get("learning", {}).get("review_reasons", [])})
        for entry in self.entries(include_archived=True):
            key = (tuple(entry["scope"]), " ".join(entry.get("content", entry["title"]).casefold().split()))
            if key in seen:
                findings.append({"kind": "possible_duplicate", "ids": [seen[key], entry["id"]]})
            seen[key] = entry["id"]
            if entry.get("state") == "hypothesis" or entry.get("summary_stale"):
                findings.append({"kind": "needs_review", "id": entry["id"]})
        return findings
