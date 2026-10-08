"""Aprendizado por checkpoint; a curadoria semântica continua sendo do agente."""
from pathlib import Path

from .core import digest, read_json, write_json
from .gitstore import apply_and_publish, clean, git, pending_automatic


TRIGGERS = ("agent", "issue", "dev", "pr", "hook", "user", "retrieval")
SEARCH_TERMS = ("triggers", "aliases", "keywords")


def policy(config_path, root):
    cfg = read_json(Path(config_path).expanduser())
    if not cfg.get("memory_root") or Path(cfg["memory_root"]).expanduser().resolve() != root.resolve():
        raise ValueError("Aprendizado exige a base configurada nesta máquina")
    mode = cfg.get("learning", {}).get("mode", "manual")
    if mode not in ("automatic", "manual"):
        raise ValueError("Política de aprendizado inválida")
    return cfg, mode


def set_policy(config_path, root, mode):
    if mode not in ("automatic", "manual"):
        raise ValueError("Política de aprendizado inválida")
    cfg, _ = policy(config_path, root)
    cfg.setdefault("learning", {})["mode"] = mode
    write_json(Path(config_path).expanduser(), cfg)
    return dict(status="configured", mode=mode)


def learn(vault, payload, actor, config_path, workspace, queue=True):
    original = payload
    cfg, mode = policy(config_path, vault.root)
    learning = payload.get("learning", {})
    source = learning.get("source")
    conflicts = learning.get("conflicts")
    if source not in ("development", "user_statement") or not isinstance(conflicts, list):
        raise ValueError("Informe learning.source e learning.conflicts após a curadoria")
    # Origem da decisão de gravar: permite medir o efeito do pedido do hook.
    learning = dict(learning, trigger=learning.get("trigger", "agent"))
    if learning["trigger"] not in TRIGGERS:
        raise ValueError("learning.trigger inválido: " + ", ".join(TRIGGERS))
    workspace = str(Path(workspace).expanduser().resolve())
    workspace = git(workspace, "rev-parse", "--show-toplevel", check=False).stdout.strip() or workspace
    scope = cfg.get("projects", {}).get(workspace)
    snapshot = vault.snapshot()
    changes = []
    reasons = []
    for change in payload["changes"]:
        collection, identifier = change["collection"], change["id"]
        vault.path(collection, identifier)
        previous = snapshot[collection].get(identifier)
        value = change.get("value", {})
        ignored = {"id", "revision", "origin"}
        if not change.get("delete") and previous is not None:
            if {k: v for k, v in previous.items() if k not in ignored} == {k: v for k, v in value.items() if k not in ignored}:
                continue
        changes.append(change)
        # Só termos de busca mudaram: enriquecimento não altera fato, estado nem preferência.
        enrichment = previous is not None and not change.get("delete") and {
            k for k in set(previous) | set(value) if k not in ignored and previous.get(k) != value.get(k)} <= set(SEARCH_TERMS)
        if change.get("delete"):
            reasons.append("Exclusão definitiva exige revisão")
            continue
        if collection == "records" and value.get("kind", "knowledge") in ("knowledge", "procedure") and not value.get("triggers"):
            # Recuperação parte do sintoma que a pessoa descreve, não só do termo técnico da solução.
            raise ValueError("Conhecimento/procedimento precisa de triggers com o sintoma como a pessoa o "
                             "descreveria (ex.: \"checklist não chega no supervisor\"): " + identifier)
        personal = collection == "records" and value.get("kind") in ("profile", "preference")
        if enrichment:
            if not personal and (not scope or value.get("scope", [])[:len(scope)] != scope):
                reasons.append("Conhecimento fora do projeto configurado exige revisão")
            continue
        origin = value.get("origin", previous.get("origin", {}) if previous else {})
        if origin.get("vault_id", snapshot["metadata"]["vault_id"]) != snapshot["metadata"]["vault_id"]:
            reasons.append("Incorporação de fonte externa exige revisão")
        if collection == "records":
            normalized = " ".join(value.get("content", "").casefold().split())
            others = list(snapshot["records"].items()) + [
                (c["id"], c.get("value", {})) for c in payload["changes"]
                if c["collection"] == "records" and not c.get("delete")]
            if any(other_id != identifier and other.get("scope") == value.get("scope")
                   and other.get("kind", "knowledge") == value.get("kind", "knowledge")
                   and " ".join(other.get("content", "").casefold().split()) == normalized
                   for other_id, other in others):
                reasons.append("Possível duplicação exige agrupamento/revisão")
        if personal:
            if source != "user_statement" or value.get("scope") != ["Pessoa"]:
                reasons.append("Perfil/preferência exige declaração da pessoa no escopo Pessoa")
            if value.get("kind") == "preference" and value.get("authority") != "explicit":
                reasons.append("Preferência inferida exige revisão")
        elif not scope or value.get("scope", [])[:len(scope)] != scope:
            reasons.append("Conhecimento fora do projeto configurado exige revisão")
        if collection in ("records", "episodes"):
            if value.get("state") != "confirmed":
                # Arquivar/superar exige registro existente e evidência do novo veredito.
                if not (previous and value.get("state") in ("archived", "superseded") and value.get("evidence")):
                    reasons.append("Hipótese ou mudança de estado sem evidência exige revisão")
            if not value.get("evidence"):
                reasons.append("Aprendizado automático exige evidência")
            if value.get("activation") == "always" and source != "user_statement":
                reasons.append("Comportamento permanente exige declaração da pessoa")
    if not changes:
        return dict(status="unchanged")
    if not any(c["collection"] in ("records", "episodes") for c in changes):
        reasons.append("Agrupamento isolado exige revisão")
    if conflicts:
        reasons.append("Conflitos não resolvidos exigem revisão")
    if mode != "automatic":
        reasons.append("Política de aprendizado manual")
    # Uma transação interrompida/publicação pendente não permite novas escritas.
    # Lote automático sem commit (sandbox) não impede o próximo; manual pendente, sim.
    accumulated = pending_automatic(vault)
    if (vault.local / "publication.json").exists() and not accumulated or (vault.local / "transaction.json").exists():
        raise ValueError("Concluir recuperação/publicação pendente antes de aprender")
    clean(vault, accumulated["paths"] if accumulated else ())
    assessment = dict(payload["assessment"], learning=dict(learning, mode=mode,
                      execution="manual_review" if reasons else "automatic", review_reasons=sorted(set(reasons))))
    try:
        proposal = vault.prepare(changes, assessment, actor, expected_base_hash=digest(snapshot))
    except OSError as error:
        from .sandbox import hint, is_read_only
        if not is_read_only(error): raise
        if queue:
            # Base somente leitura no sandbox: valida tudo agora (o agente ainda pode corrigir)
            # e o hook aplica fora dele, revalidando o lote.
            vault.prepare(changes, assessment, actor, expected_base_hash=digest(snapshot), dry_run=True)
            from .queue import enqueue
            try:
                path = enqueue(vault.root, original, actor, config_path, workspace)
                return dict(status="queued", changed=False, queue=str(path),
                            apply="O hook YABook aplica fora do sandbox ao concluir esta ferramenta; o resultado final "
                                  "(aplicado ou revisão) aparece no próximo início de sessão. Informe "
                                  "'Memória enviada para atualização', não 'Memória atualizada'.")
            except OSError:
                pass
        return dict(status="sandbox_read_only", changed=False, hint=hint(vault.root))
    if reasons:
        return dict(status="pending_review", proposal=proposal["id"], reasons=sorted(set(reasons)),
                    stale_summaries=proposal["stale_summaries"])
    current, _ = policy(config_path, vault.root)
    if current != cfg:
        return dict(status="pending_review", proposal=proposal["id"], reasons=["Política/configuração mudou durante a curadoria"])
    result = apply_and_publish(vault, proposal["id"], proposal["approval_hash"], automatic=True)
    # Resumos invalidados pedem atualização do grupo em novo lote, sem bloquear este.
    return dict(status="memory_updated", proposal=result["proposal"], paths=result["paths"],
                publication=result["publication"], stale_summaries=result["stale_summaries"])


def learn_triggers(vault, identifier, phrases, actor, config_path, workspace):
    """Acrescenta a frase da pessoa como gatilho de um registro achado fora das pistas."""
    phrases = [" ".join(p.split()) for p in phrases if isinstance(p, str) and p.strip()]
    if not 1 <= len(phrases) <= 3 or any(len(p) > 160 for p in phrases):
        raise ValueError("Informe de 1 a 3 frases de até 160 caracteres")
    current = vault.snapshot()["records"].get(identifier)
    if current is None:
        raise ValueError("Registro inexistente: " + identifier)
    value = {k: v for k, v in current.items() if k not in ("id", "revision", "origin")}
    value["triggers"] = list(dict.fromkeys(value.get("triggers", []) + phrases))
    payload = {"learning": {"source": "development", "conflicts": [], "trigger": "retrieval"},
               "assessment": {"verdict": "update", "reason": "Pergunta da pessoa não recuperou este registro pelas pistas.",
                              "utility": "Recuperar o registro na próxima pergunta com a mesma formulação.",
                              "application": "Pistas de memória por sintoma.",
                              "evidence_status": "Somente gatilho de busca acrescentado; fato e evidências inalterados."},
               "changes": [{"collection": "records", "id": identifier, "value": value}]}
    return learn(vault, payload, actor, config_path, workspace)


def recent(vault, limit=10):
    if not 1 <= limit <= 100:
        raise ValueError("Limite de histórico deve estar entre 1 e 100")
    entries = []
    for path in (vault.root / "history").glob("*.json"):
        receipt = read_json(path)
        entries.append(dict(proposal=receipt["proposal"], created_at=receipt.get("created_at", ""),
                            trigger=receipt["assessment"].get("learning", {}).get("trigger"),
                            actor=receipt["actor"], assessment=receipt["assessment"],
                            changes=[dict(collection=c["collection"], id=c["id"], delete=bool(c.get("delete")))
                                     for c in receipt["changes"]]))
    return sorted(entries, key=lambda r: (r["created_at"], r["proposal"]), reverse=True)[:limit]
