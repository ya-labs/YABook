"""Fontes conectadas: fetch incremental, visão filtrada e linhagem preservada."""
import re
import time
from pathlib import Path
from .core import Vault, digest, read_json, scoped, write_json
from .gitstore import git, run, publish, clean


def source_add(vault, value):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", value.get("id", "")):
        raise ValueError("ID de fonte inválido")
    remote = value.get("remote", "")
    if not re.fullmatch(r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+(?:\.git)?", remote):
        raise ValueError("Fonte deve ser URL HTTPS GitHub sem credenciais")
    if not value.get("includes"):
        raise ValueError("Declare escopos incluídos explicitamente")
    for prefixes in (value["includes"], value.get("excludes", [])):
        if not all(isinstance(p, list) and p and all(isinstance(x, str) and x.strip() for x in p) for p in prefixes):
            raise ValueError("Escopos inválidos")
    path = vault.local / "sources.json"
    config = read_json(path) if path.exists() else {}
    if value["id"] in config and config[value["id"]]["remote"] != remote:
        raise ValueError("Fonte existente tem outro remoto")
    config[value["id"]] = dict(value, refresh_seconds=max(60, int(value.get("refresh_seconds", 900))))
    write_json(path, config)
    return config[value["id"]]


def sanitize(entries, includes, excludes):
    allowed = [dict(e) for e in entries if scoped(e["scope"], includes, excludes)]
    ids = {e["id"] for e in allowed}
    for entry in allowed:
        original_members = entry.get("members", [])
        entry["members"] = [i for i in original_members if i in ids]
        entry["entities"] = [i for i in entry.get("entities", []) if i in ids]
        entry["relations"] = [r for r in entry.get("relations", []) if r["target"] in ids]
        if len(original_members) != len(entry["members"]):
            entry.pop("summary", None)
            entry.pop("summary_sources", None)
    return allowed


def refresh(vault, force=False, deadline=None):
    path = vault.local / "sources.json"
    config = read_json(path) if path.exists() else {}
    reports = []
    def remaining():
        if deadline is None: return 60
        budget = deadline - time.monotonic()
        if budget <= 0: raise ValueError("Orçamento de atualização da sessão esgotado")
        return budget
    for identifier, source in config.items():
        cache = vault.local / "sources" / identifier
        receipt_path = cache / "receipt.json"
        before = read_json(receipt_path) if receipt_path.exists() else {}
        if not force and time.time() - before.get("checked_at", 0) < source["refresh_seconds"]:
            continue
        mirror = cache / "repo.git"
        try:
            cache.mkdir(parents=True, exist_ok=True)
            if mirror.exists():
                # Não executar hooks, checkout, submodules ou código vindo do colega.
                git(mirror, "fetch", "origin", "+refs/heads/*:refs/heads/*", timeout=remaining())
            else:
                run("git", "clone", "--bare", source["remote"], str(mirror), timeout=remaining())
            ref = source.get("branch", "HEAD")
            if ref.startswith("-") or not re.fullmatch(r"[A-Za-z0-9_./-]+", ref):
                raise ValueError("Referência da fonte inválida")
            revision = git(mirror, "rev-parse", "--verify", ref + "^{commit}", timeout=remaining()).stdout.strip()
            def document(filename):
                import json
                return json.loads(git(mirror, "show", revision + ":" + filename, timeout=remaining()).stdout)
            metadata = document("memory.json")
            if metadata.get("schema_version") != 1: raise ValueError("Formato externo incompatível")
            if before.get("vault_id") and before["vault_id"] != metadata["vault_id"]:
                raise ValueError("Identidade da fonte mudou; recadastrar após revisão")
            filenames = git(mirror, "ls-tree", "-r", "--name-only", revision, timeout=remaining()).stdout.splitlines()
            snapshot = {"metadata": metadata, "records": {}, "entities": {}, "groups": {}}
            for filename in filenames:
                match = re.fullmatch(r"(records|entities|groups)/([A-Za-z0-9_-]+)\.json", filename)
                if match:
                    collection, record_id = match.groups()
                    snapshot[collection][record_id] = document(filename)
            vault.validate(snapshot)
            entries = [dict(e, collection=c) for c in ("records", "entities", "groups") for e in snapshot[c].values()]
            entries = sanitize(entries, source["includes"], source.get("excludes", []))
            old = {e["id"]: digest(e) for e in before.get("entries", [])}
            new = {e["id"]: digest(e) for e in entries}
            report = dict(source=identifier, revision=revision,
                added=sorted(new.keys()-old.keys()), removed=sorted(old.keys()-new.keys()),
                updated=sorted(k for k in new.keys() & old.keys() if new[k] != old[k]), status="updated")
            write_json(receipt_path, dict(vault_id=metadata["vault_id"], revision=revision,
                checked_at=time.time(), policy_hash=digest(source), entries=entries, report=report))
            reports.append(report)
        except (OSError, ValueError, KeyError):
            reports.append(dict(source=identifier, status="offline_or_invalid", cached=bool(before)))
    return reports


def external_entries(vault, includes=(), excludes=(), include_inactive=False):
    config_path = vault.local / "sources.json"
    config = read_json(config_path) if config_path.exists() else {}
    for identifier, source in config.items():
        path = vault.local / "sources" / identifier / "receipt.json"
        if not path.exists(): continue
        receipt = read_json(path)
        revisions = {e["id"]: e.get("revision") for e in receipt["entries"]}
        # Política pode ter mudado desde fetch; nunca usar cache com escopo antigo.
        entries = sanitize(receipt["entries"], source["includes"], source.get("excludes", []))
        entries = sanitize(entries, includes, excludes)
        for entry in entries:
            if entry.get("state") in ("archived", "superseded") and not include_inactive: continue
            if entry.get("summary") and any(revisions.get(i) != rev for i, rev in entry.get("summary_sources", {}).items()):
                entry.pop("summary", None)
                entry["summary_stale"] = True
            yield dict(entry, source=identifier, source_revision=receipt["revision"],
                       source_vault=receipt["vault_id"], external=True)


def all_entries(vault, includes=(), excludes=()):
    own = sanitize(list(vault.entries()), includes, excludes)
    result = list(own)
    vault_id = vault.snapshot()["metadata"]["vault_id"]
    known = {(e.get("origin", {}).get("vault_id", vault_id),
              e.get("origin", {}).get("id", e["id"])) for e in own}
    for entry in external_entries(vault, includes, excludes, include_inactive=True):
        origin = entry.get("origin", {})
        identity = (origin.get("vault_id", entry["source_vault"]), origin.get("id", entry["id"]))
        if identity not in known:
            if entry.get("state") in ("archived", "superseded"): continue
            result.append(entry); known.add(identity)
        else:
            # Não promover nova revisão silenciosamente; a curadoria verá a divergência.
            existing = next((e for e in result if (e.get("origin", {}).get("vault_id", vault_id), e.get("origin", {}).get("id", e["id"])) == identity), None)
            fields = ("content", "application", "state", "conditions", "evidence", "title", "summary")
            if existing and any(entry.get(k) != existing.get(k) for k in fields):
                existing.setdefault("origin_updates", []).append(dict(source=entry["source"], id=entry["id"], revision=entry["revision"],state=entry.get("state")))
    return result


def sync(vault):
    publication = publish(vault)
    clean(vault)
    if (vault.root / ".git").exists():
        # FF-only não resolve conflito sem avaliação e não mistura históricos de colegas.
        branch = git(vault.root, "branch", "--show-current").stdout.strip()
        result = git(vault.root, "pull", "--ff-only", "origin", branch, check=False)
        own = "updated" if result.returncode == 0 else "offline_or_diverged"
    else: own = "local_only"
    return dict(publication=publication, own=own, sources=refresh(vault, force=True))
