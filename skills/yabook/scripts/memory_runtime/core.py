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

COLLECTIONS = ("records", "entities", "groups")
STATES = ("hypothesis", "confirmed", "superseded", "archived")
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,95}$")
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
            if metadata["owner"] != owner or metadata["schema_version"] != 1:
                raise ValueError("Base existente pertence a outro proprietário/formato")
            return metadata
        if self.root.exists() and any(self.root.iterdir()):
            raise ValueError("Destino não vazio; não sobrescrever uma base desconhecida")
        self.root.mkdir(parents=True, exist_ok=True)
        metadata = {"schema_version": 1, "vault_id": str(uuid.uuid4()), "owner": owner,
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
        if metadata.get("schema_version") != 1:
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
                if collection == "records":
                    if not entry.get("content", "").strip() or not entry.get("application", "").strip():
                        raise ValueError("Conhecimento precisa de conteúdo e aplicação")
                    if entry.get("state") == "confirmed" and not entry.get("evidence"):
                        raise ValueError("Conhecimento confirmado precisa de evidência")
                for reference in entry.get("members", []) + entry.get("entities", []):
                    if reference not in ids:
                        raise ValueError("Referência inexistente: " + reference)
                for relation in entry.get("relations", []):
                    if relation.get("target") not in ids or not relation.get("type"):
                        raise ValueError("Relação inválida")
                if collection == "groups" and entry.get("summary"):
                    if set(entry.get("summary_sources", {})) != set(entry.get("members", [])):
                        raise ValueError("Resumo precisa referenciar todos os membros")

    def prepare(self, changes, assessment, actor):
        required = ("verdict", "reason", "utility", "application", "evidence_status")
        if not all(isinstance(assessment.get(k), str) and assessment[k].strip() for k in required):
            raise ValueError("Avaliação do agente incompleta")
        if assessment["verdict"] not in ("add", "update", "relate", "archive", "delete"):
            raise ValueError("Veredito não executável; manter/rejeitar não gera proposta")
        if not changes:
            raise ValueError("Proposta vazia")
        with self.lock():
            before = self.snapshot()
            proposed = json.loads(json.dumps(before))
            touched = set()
            for change in changes:
                collection, identifier = change["collection"], change["id"]
                self.path(collection, identifier)
                if (collection, identifier) in touched:
                    raise ValueError("Registro repetido na proposta")
                touched.add((collection, identifier))
                if change.get("delete"):
                    if identifier not in proposed[collection]:
                        raise ValueError("Não é possível remover registro ausente")
                    del proposed[collection][identifier]
                else:
                    entry = dict(change["value"])
                    old = before[collection].get(identifier, {})
                    entry.update(id=identifier, revision=old.get("revision", 0) + 1)
                    entry.setdefault("origin", old.get("origin", {"vault_id": before["metadata"]["vault_id"], "id": identifier}))
                    proposed[collection][identifier] = entry
            self.validate(proposed)
            proposal = {"id": "P-" + uuid.uuid4().hex[:16], "base_hash": digest(before),
                        "created_at": now(), "actor": actor, "assessment": assessment,
                        "changes": changes, "result": proposed}
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
        receipt = {"proposal": proposal["id"], "approval_hash": proposal["approval_hash"],
                   "actor": proposal["actor"], "assessment": proposal["assessment"],
                   "changes": proposal["changes"], "snapshot": proposal["result"],
                   "result_hash": digest(proposal["result"])}
        history = self.root / "history" / (proposal["id"] + ".json")
        write_json(history, receipt)
        paths.append(str(history.relative_to(self.root)))
        if (self.root / ".git").exists():
            from .gitstore import publication_intent, git
            if git(self.root, "rev-parse", "--verify", "HEAD", check=False).returncode:
                paths += ["memory.json", ".gitignore"]
            publication_intent(self, paths, "docs: aplica memória " + proposal["id"])
        pending = self.local / "proposals" / (proposal["id"] + ".json")
        pending.unlink(missing_ok=True)
        (self.local / "transaction.json").unlink(missing_ok=True)
        return {"proposal": proposal["id"], "paths": sorted(set(paths)), "result_hash": receipt["result_hash"]}

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
        for collection in COLLECTIONS:
            for entry in snapshot[collection].values():
                if scoped(entry["scope"], includes, excludes) and (include_archived or entry.get("state") not in ("archived", "superseded")):
                    item = dict(entry, collection=collection, source="own")
                    if collection == "groups" and entry.get("summary"):
                        revisions = {i: snapshot[c][i].get("revision") for c in COLLECTIONS for i in snapshot[c]}
                        if any(revisions.get(i) != rev for i, rev in entry["summary_sources"].items()):
                            item.pop("summary", None)
                            item["summary_stale"] = True
                    yield item

    def review(self):
        seen, findings = {}, []
        for entry in self.entries(include_archived=True):
            key = (tuple(entry["scope"]), " ".join(entry.get("content", entry["title"]).casefold().split()))
            if key in seen:
                findings.append({"kind": "possible_duplicate", "ids": [seen[key], entry["id"]]})
            seen[key] = entry["id"]
            if entry.get("state") == "hypothesis" or entry.get("summary_stale"):
                findings.append({"kind": "needs_review", "id": entry["id"]})
        return findings
