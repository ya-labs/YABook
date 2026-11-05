"""Fontes conectadas: fetch incremental, visão filtrada e linhagem preservada."""
import re
import time
from pathlib import Path
from .core import Vault, COLLECTIONS, SCHEMA_VERSION, snapshot_entries, digest, read_json, scoped, write_json
from .gitstore import git, run, publish, clean


def source_config(vault):
    """Cadastro portátil; leituras aceitam o legado sem alterá-lo."""
    path = vault.root / "sources.json"
    if not path.exists(): path = vault.local / "sources.json"
    config = read_json(path) if path.exists() else {}
    if not isinstance(config, dict): raise ValueError("Cadastro de fontes inválido")
    for identifier, value in config.items():
        if not isinstance(value, dict) or identifier != value.get("id"):
            raise ValueError("Cadastro de fontes inválido")
        validate_source(value)
    return config


def validate_source(value):
    if not isinstance(value, dict): raise ValueError("Cadastro de fonte precisa ser objeto")
    if not isinstance(value.get("id"), str) or not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,63}", value["id"]):
        raise ValueError("ID de fonte inválido")
    if not isinstance(value.get("remote"), str) or not re.fullmatch(r"https://github\.com/[A-Za-z0-9-]+/[A-Za-z0-9_.-]+(?:\.git)?", value["remote"]):
        raise ValueError("Fonte deve ser URL HTTPS GitHub sem credenciais")
    if not value.get("includes"):
        raise ValueError("Declare escopos incluídos explicitamente")
    for prefixes in (value["includes"], value.get("excludes", [])):
        if not isinstance(prefixes, list) or not all(isinstance(p, list) and p and
                all(isinstance(x, str) and x.strip() for x in p) for p in prefixes):
            raise ValueError("Escopos inválidos")
    if "incorporate" in value and type(value["incorporate"]) is not bool:
        raise ValueError("incorporate precisa ser booleano explícito")
    branch = value.get("branch", "HEAD")
    if not isinstance(branch, str) or branch.startswith("-") or not re.fullmatch(r"[A-Za-z0-9_./-]+", branch):
        raise ValueError("Referência da fonte inválida")


def _registry_apply(vault, config=None):
    """Journal cobre a janela entre gravar cadastro e registrar intenção de publicar."""
    journal = vault.local / "source-config.json"
    path = vault.root / "sources.json"
    with vault.lock():
        if config is None and not journal.exists(): return None
        publication = vault.local / "publication.json"
        if publication.exists():
            receipt = read_json(publication)
            if not journal.exists() or set(receipt.get("paths", [])) != {"sources.json"}:
                raise ValueError("Concluir publicação pendente antes de configurar fontes")
        if journal.exists():
            pending = read_json(journal)
            if config is not None and pending["value"] != config:
                raise ValueError("Concluir cadastro de fontes pendente antes de alterá-lo")
        elif config is None:
            return None
        else:
            clean(vault)
            pending = dict(value=config, before=digest(read_json(path)) if path.exists() else None)
            write_json(journal, pending)
        current = digest(read_json(path)) if path.exists() else None
        if current not in (pending["before"], digest(pending["value"])):
            raise ValueError("Cadastro mudou durante a atualização; revisar sources.json")
        write_json(path, pending["value"])
        result = publish(vault, ["sources.json"], "docs: configura fontes de memória") \
            if (vault.root / ".git").exists() else dict(status="local_only")
        journal.unlink()
        return result


def source_add(vault, value):
    validate_source(value)
    remote = value.get("remote", "")
    permitted = ("id", "remote", "includes", "excludes", "branch", "incorporate", "refresh_seconds")
    if set(value) - set(permitted): raise ValueError("Campo desconhecido no cadastro de fonte")
    with vault.lock():
        config = source_config(vault)
        if value["id"] in config and config[value["id"]]["remote"] != remote:
            raise ValueError("Fonte existente tem outro remoto")
        try:
            interval = max(60, int(value.get("refresh_seconds", 900)))
        except (TypeError, ValueError) as error:
            raise ValueError("Intervalo de atualização inválido") from error
        updated = dict(value, refresh_seconds=interval)
        if config.get(value["id"]) == updated and (vault.root / "sources.json").exists() and \
                not (vault.local / "source-config.json").exists():
            return dict(updated, publication=dict(status="unchanged"))
        config[value["id"]] = updated
        publication = _registry_apply(vault, config)
        return dict(updated, publication=publication)


def sanitize(entries, includes, excludes):
    allowed = [dict(e) for e in entries if scoped(e["scope"], includes, excludes)]
    ids = {e["id"] for e in allowed}
    invalidated = set()
    for entry in allowed:
        original_members = entry.get("members", [])
        entry["members"] = [i for i in original_members if i in ids]
        entry["entities"] = [i for i in entry.get("entities", []) if i in ids]
        for field in ("episodes", "learnings"):
            if field in entry: entry[field] = [i for i in entry[field] if i in ids]
        if entry.get("parent") not in ids: entry.pop("parent", None)
        if entry.get("project_id") not in ids: entry.pop("project_id", None)
        entry["relations"] = [r for r in entry.get("relations", []) if r["target"] in ids]
        if len(original_members) != len(entry["members"]):
            entry.pop("summary", None)
            entry.pop("summary_sources", None)
            entry["summary_stale"] = True
            invalidated.add(entry["id"])
        if entry.get("summary_stale"): invalidated.add(entry["id"])
    # Um resumo ancestral também pode conter conteúdo de um filho filtrado.
    changed = True
    while changed:
        changed = False
        for entry in allowed:
            if entry.get("summary") and any(i in invalidated for i in entry.get("summary_sources", {})):
                entry.pop("summary", None); entry["summary_stale"] = True
                invalidated.add(entry["id"]); changed = True
    return allowed


def refresh(vault, force=False, deadline=None):
    config = source_config(vault)
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
        if not force and time.time() - before.get("checked_at", 0) < source.get("refresh_seconds", 900):
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
            if metadata.get("schema_version") not in (1, SCHEMA_VERSION): raise ValueError("Formato externo incompatível")
            if before.get("vault_id") and before["vault_id"] != metadata["vault_id"]:
                raise ValueError("Identidade da fonte mudou; recadastrar após revisão")
            filenames = git(mirror, "ls-tree", "-r", "--name-only", revision, timeout=remaining()).stdout.splitlines()
            snapshot = {"metadata": metadata, **{c: {} for c in COLLECTIONS}}
            for filename in filenames:
                match = re.fullmatch(r"(records|entities|groups|episodes)/([A-Za-z0-9_-]+)\.json", filename)
                if match:
                    collection, record_id = match.groups()
                    snapshot[collection][record_id] = document(filename)
            vault.validate(snapshot)
            entries = list(snapshot_entries(snapshot))
            # Preferências e perfil do colega não se tornam comportamento do agente local.
            entries = [e for e in entries if e.get("kind") not in ("profile", "preference")]
            entries = sanitize(entries, source["includes"], source.get("excludes", []))
            old = {e["id"]: digest(e) for e in before.get("entries", [])}
            new = {e["id"]: digest(e) for e in entries}
            report = dict(source=identifier, revision=revision,
                added=sorted(new.keys()-old.keys()), removed=sorted(old.keys()-new.keys()),
                updated=sorted(k for k in new.keys() & old.keys() if new[k] != old[k]), status="updated")
            with vault.lock():
                write_json(receipt_path, dict(vault_id=metadata["vault_id"], revision=revision,
                    checked_at=time.time(), policy_hash=digest(source), entries=entries, report=report))
            reports.append(report)
        except (OSError, ValueError, KeyError):
            reports.append(dict(source=identifier, status="offline_or_invalid", cached=bool(before)))
    return reports


def external_entries(vault, includes=(), excludes=(), include_inactive=False):
    config = source_config(vault)
    for identifier, source in config.items():
        path = vault.local / "sources" / identifier / "receipt.json"
        if not path.exists(): continue
        receipt = read_json(path)
        revisions = {e["id"]: e.get("revision") for e in receipt["entries"]}
        # Política pode ter mudado desde fetch; nunca usar cache com escopo antigo.
        entries = sanitize([e for e in receipt["entries"] if e.get("kind") not in ("profile", "preference")], source["includes"], source.get("excludes", []))
        entries = sanitize(entries, includes, excludes)
        for entry in entries:
            if entry.get("state") in ("archived", "superseded") and not include_inactive: continue
            if entry.get("summary") and any(revisions.get(i) != rev for i, rev in entry.get("summary_sources", {}).items()):
                entry.pop("summary", None)
                entry["summary_stale"] = True
            yield dict(entry, source=identifier, source_revision=receipt["revision"],
                       source_vault=receipt["vault_id"], external=True)


def all_entries(vault, includes=(), excludes=()):
    snapshot = vault.snapshot()
    vault.validate(snapshot)
    complete = list(snapshot_entries(snapshot))
    own = sanitize([e for e in complete if e.get("state") not in ("archived", "superseded")], includes, excludes)
    result = list(own)
    metadata = snapshot["metadata"]
    vault_id = metadata["vault_id"]
    known = {(e.get("origin", {}).get("vault_id", vault_id),
              e.get("origin", {}).get("id", e["id"])) for e in complete}
    ledger = metadata.get("source_sync", {}).get("entries", {})
    targets = {e["id"]: e for e in own}
    incorporated = {(e["origin"]["vault_id"], e["origin"]["id"]): e["target"]
                    for e in ledger.values() if e.get("remote_hash")}
    known.update(incorporated)
    for entry in ledger.values():
        if entry.get("decision") == "pending" and entry.get("target") in targets:
            targets[entry["target"]].setdefault("origin_updates", []).append(dict(source=entry["source"],
                source_revision=entry["source_revision"], id=entry["origin"]["id"],
                status=entry.get("status", "pending"), reason=entry["reason"]))
    for entry in external_entries(vault, includes, excludes, include_inactive=True):
        origin = entry.get("origin", {})
        identity = (origin.get("vault_id", entry["source_vault"]), origin.get("id", entry["id"]))
        if identity not in known:
            if entry.get("state") in ("archived", "superseded"): continue
            result.append(entry); known.add(identity)
        else:
            # Não promover nova revisão silenciosamente; a curadoria verá a divergência.
            from .incorporation import value_of
            accepted = ledger.get(digest(dict(vault_id=identity[0], id=identity[1])), {})
            if accepted.get("remote_hash") == digest(value_of(entry)):
                continue
            existing = targets.get(incorporated.get(identity)) or next((e for e in result if
                (e.get("origin", {}).get("vault_id", vault_id), e.get("origin", {}).get("id", e["id"])) == identity), None)
            fields = ("content", "application", "state", "conditions", "evidence", "title", "summary",
                      "kind", "keywords", "aliases", "triggers", "parent", "members", "episodes",
                      "objective", "context", "actions", "outcome", "validation", "learnings")
            if existing and any(entry.get(k) != existing.get(k) for k in fields):
                existing.setdefault("origin_updates", []).append(dict(source=entry["source"], id=entry["id"], revision=entry["revision"],state=entry.get("state")))
    return result


def sync(vault):
    from .gitstore import reconcile, settle
    # Publicação pendente presa por divergência é reconciliada e publicada aqui mesmo.
    publication = settle(vault) or dict(status="unchanged")
    own = reconcile(vault)
    if own.get("status") == "conflict":
        return dict(publication=publication, own=own, sources=[], status="pending_review")
    if own.get("status") == "rebased":
        publication = settle(vault) or publication
    registry = _registry_apply(vault)
    if not (vault.root / "sources.json").exists() and (vault.local / "sources.json").exists():
        registry = _registry_apply(vault, source_config(vault))
    reports = refresh(vault, force=True)
    return dict(publication=publication, own=own, sources=reports, registry=registry,
                curation=curation_plan(vault))


def curation_plan(vault):
    from .incorporation import curation_plan as plan
    return plan(vault)


def sync_apply(vault, payload, actor):
    from .incorporation import sync_apply as apply
    return apply(vault, payload, actor)
