"""Curadoria de fontes: decisões do agente, linhagem e aplicação transacional."""
import copy

from .core import COLLECTIONS, ID, digest, scoped, read_json
from .gitstore import apply_and_publish, clean


TRANSIENT = {"id", "revision", "origin", "source", "source_revision", "source_vault",
             "external", "collection", "summary_stale", "origin_updates"}


def value_of(entry):
    if not isinstance(entry, dict): raise ValueError("Memória curada precisa ser objeto")
    value = {k: copy.deepcopy(v) for k, v in entry.items() if k not in TRANSIENT}
    # sanitize acrescenta listas vazias para consulta: isso não é uma descoberta nova.
    for field in ("members", "entities", "relations", "episodes", "learnings"):
        if value.get(field) == []: value.pop(field)
    return value


def identity(entry, vault_id):
    origin = entry.get("origin", {})
    if not isinstance(origin, dict): raise ValueError("Identidade original inválida na fonte")
    result = dict(vault_id=origin.get("vault_id", vault_id), id=origin.get("id", entry["id"]))
    if not isinstance(result["vault_id"], str) or not result["vault_id"].strip() or \
            not isinstance(result["id"], str) or not ID.fullmatch(result["id"]):
        raise ValueError("Identidade original inválida na fonte")
    return result


def curation_plan(vault):
    from .sources import source_config, external_entries
    snapshot = vault.snapshot()
    config = source_config(vault)
    ledger = snapshot["metadata"].get("source_sync", {}).get("entries", {})
    own_id = snapshot["metadata"]["vault_id"]
    current_sources, skipped = set(), []
    for source, policy in config.items():
        if policy.get("incorporate") is not True: continue
        path = vault.local / "sources" / source / "receipt.json"
        if path.exists() and read_json(path).get("policy_hash") == digest(policy):
            current_sources.add(source)
        else:
            skipped.append(dict(source=source, reason="Atualizar cache após aprovar a política da fonte"))
    own = {i: (collection, entry) for collection in COLLECTIONS for i, entry in snapshot[collection].items()}
    origins = {digest(identity(entry, own_id)): i for i, (_, entry) in own.items()}
    candidates, seen = [], set()
    for entry in external_entries(vault, include_inactive=True):
        source = entry["source"]
        if source not in current_sources: continue
        origin = identity(entry, entry["source_vault"])
        key = digest(origin)
        seen.add((source, key))
        previous = ledger.get(key, {})
        remote_hash = digest(value_of(entry))
        target = previous.get("target") or origins.get(key)
        local = own.get(target)
        if previous.get("decision") == "ignore" and previous.get("seen_hash") == remote_hash: continue
        if previous.get("remote_hash") == remote_hash: continue
        if not previous and local and digest(value_of(local[1])) == remote_hash: continue
        status, reason = "new", "Descoberta externa ainda não avaliada"
        if entry.get("state", "confirmed") != "confirmed":
            if not local and not previous: continue
            status, reason = "invalidated", "A origem deixou de confirmar o conhecimento; revisar sem apagar a versão local"
        elif local:
            if previous.get("local_hash") == digest(value_of(local[1])) and local[0] == entry["collection"] \
                    and previous.get("strategy", "copy") == "copy":
                status, reason = "updated", "Nova revisão externa; versão local permanece igual à incorporada"
            else:
                status, reason = "conflict", "Versão local mudou ou não há base comum; resolver com evidência"
        elif previous.get("target"):
            status, reason = "conflict", "Destino incorporado foi removido localmente; não recriar automaticamente"
        else:
            # Igualdade exata é pista para mesclar, nunca licença para duplicar.
            for identifier, (collection, candidate) in own.items():
                if collection == entry["collection"] == "records" and candidate.get("scope") == entry.get("scope") \
                        and candidate.get("kind", "knowledge") == entry.get("kind", "knowledge") \
                        and " ".join(candidate.get("content", "").casefold().split()) == \
                            " ".join(entry.get("content", "").casefold().split()):
                    target, reason = identifier, "Conteúdo equivalente já existe; avaliar complemento em vez de duplicar"
                    break
        candidate = dict(source=source, source_vault=entry["source_vault"], source_revision=entry["source_revision"],
                         origin=origin, collection=entry["collection"], entry=copy.deepcopy(entry), target=target,
                         status=status, reason=reason, remote_hash=remote_hash)
        candidate["candidate"] = digest(candidate)
        candidates.append(candidate)
    # Remoção só é inferida de um recibo válido, nunca de falha de rede ou cache ausente.
    for key, previous in ledger.items():
        source = previous.get("source")
        policy = config.get(source, {})
        if source not in current_sources or (source, key) in seen: continue
        if not scoped(previous.get("scope", []), policy["includes"], policy.get("excludes", [])): continue
        path = vault.local / "sources" / source / "receipt.json"
        if not path.exists(): continue
        receipt = read_json(path)
        if receipt.get("vault_id") != previous.get("source_vault"): continue
        remote_hash = digest(dict(removed=True, origin=previous["origin"]))
        if previous.get("decision") == "ignore" and previous.get("seen_hash") == remote_hash: continue
        candidate = dict(source=source, source_vault=receipt["vault_id"], source_revision=receipt["revision"],
                         origin=previous["origin"], collection=previous["collection"], entry=None,
                         target=previous.get("target"), status="removed", reason="Registro ausente na origem; revisar sem apagar a memória local",
                         remote_hash=remote_hash)
        candidate["candidate"] = digest(candidate)
        candidates.append(candidate)
    candidates.sort(key=lambda c: (c["source"], c["collection"], c["origin"]["id"]))
    return dict(base_hash=digest(snapshot), candidates_hash=digest(dict(sources=config, candidates=candidates)),
                candidates=candidates, skipped_sources=skipped)


def _remap(value, mapping, revisions, safe_members=()):
    """Referências da origem tornam-se referências locais; dependências não aceitas são filtradas."""
    result = copy.deepcopy(value)
    for field in ("members", "entities", "episodes", "learnings"):
        if field in result: result[field] = list(dict.fromkeys(mapping[i] for i in result[field] if i in mapping))
    for field in ("parent", "project_id"):
        if field in result:
            if result[field] in mapping: result[field] = mapping[result[field]]
            else: result.pop(field)
    if "relations" in result:
        result["relations"] = [dict(r, target=mapping[r["target"]]) for r in result["relations"] if r.get("target") in mapping]
    if result.get("summary"):
        # Resumo só sobrevive se todos os membros forem aceitos e suas revisões forem conhecidas.
        if len(result.get("members", [])) != len(value.get("members", [])) or \
                not set(value.get("members", [])) <= set(safe_members):
            result.pop("summary", None); result.pop("summary_sources", None)
        else:
            result["summary_sources"] = {i: revisions[i] for i in result.get("members", [])}
    elif "summary_sources" in result:
        result.pop("summary_sources")
    return result


def sync_apply(vault, payload, actor):
    with vault.lock():
        return _sync_apply(vault, payload, actor)


def _sync_apply(vault, payload, actor):
    from .sources import source_config
    if not isinstance(actor, str) or not actor.strip(): raise ValueError("Informe o agente responsável pela curadoria")
    plan = curation_plan(vault)
    if payload.get("base_hash") != plan["base_hash"] or payload.get("candidates_hash") != plan["candidates_hash"]:
        raise ValueError("Base, fonte ou política mudou durante a curadoria; gere novo sync")
    decisions = payload.get("decisions")
    if not isinstance(decisions, list) or not decisions: raise ValueError("Informe decisões explícitas de curadoria")
    snapshot = vault.snapshot()
    config = source_config(vault)
    original = snapshot["metadata"].get("source_sync", dict(version=1, entries={}))
    ledger = copy.deepcopy(original)
    by_hash = {c["candidate"]: c for c in plan["candidates"]}
    chosen, touched, destinations = [], set(), set()
    all_own = {i: (collection, entry) for collection in COLLECTIONS for i, entry in snapshot[collection].items()}
    for decision in decisions:
        if not isinstance(decision, dict) or decision.get("candidate") not in by_hash:
            raise ValueError("Decisão não corresponde a candidato vigente")
        candidate = by_hash[decision["candidate"]]
        key = digest(candidate["origin"])
        if key in touched: raise ValueError("Origem repetida no mesmo lote de curadoria")
        touched.add(key)
        action = decision.get("action")
        if action not in ("add", "update", "merge", "ignore", "pending"):
            raise ValueError("Ação de curadoria inválida")
        if not isinstance(decision.get("reason"), str) or not decision["reason"].strip():
            raise ValueError("Cada decisão precisa explicar utilidade, descarte ou pendência")
        if action in ("add", "update", "merge"):
            if candidate["status"] in ("removed", "invalidated"):
                raise ValueError("Remoção/invalidação externa exige revisão; mantenha pendente")
            if candidate["status"] == "conflict" and action != "merge":
                raise ValueError("Conflito exige mesclagem explícita com evidência ou pendência")
            entry = candidate["entry"]
            value = value_of(decision.get("value", entry))
            if value.get("kind") in ("profile", "preference") or value.get("activation") == "always":
                raise ValueError("Fonte externa não define perfil, preferência ou comportamento permanente")
            if not isinstance(value.get("scope"), list) or not value["scope"] or \
                    not scoped(value["scope"], config[candidate["source"]]["includes"],
                          config[candidate["source"]].get("excludes", [])):
                raise ValueError("Memória curada fora do escopo aprovado da fonte")
            if candidate["collection"] in ("records", "episodes"):
                if value.get("state") != "confirmed" or not value.get("evidence"):
                    raise ValueError("Incorporação exige confirmação e evidências")
                if candidate["collection"] == "records" and value.get("kind", "knowledge") in ("knowledge", "procedure") \
                        and not value.get("triggers"):
                    raise ValueError("Conhecimento incorporado precisa de gatilhos de busca")
            target = decision.get("target") or candidate.get("target") or entry["id"]
            if not isinstance(target, str) or not ID.fullmatch(target): raise ValueError("Destino local inválido")
            if action == "add":
                if candidate.get("target"): raise ValueError("Origem/conteúdo já existe; use update ou merge")
                if target in all_own:
                    target = ("ext-" + key[:16] + "-" + entry["id"])[:96]
                if target in all_own: raise ValueError("Colisão de identidade local; indique outro destino")
            else:
                if target not in all_own or all_own[target][0] != candidate["collection"]:
                    raise ValueError("Destino da atualização/mesclagem não existe na coleção")
                if action == "update" and (candidate["status"] != "updated" or target != candidate["target"]):
                    raise ValueError("Update exige versão local intacta e destino incorporado")
                if action == "merge" and "value" not in decision:
                    raise ValueError("Merge exige valor completo curado; não sobrescrever por omissão")
            if not isinstance(target, str) or not ID.fullmatch(target): raise ValueError("Destino local inválido")
            if target in destinations: raise ValueError("Destino repetido; consolide as descobertas num único lote")
            destinations.add(target)
            chosen.append((candidate, decision, key, target, value))
        else:
            previous = ledger["entries"].get(key, {})
            if previous.get("decision") == action and previous.get("seen_hash") == candidate["remote_hash"] \
                    and previous.get("reason") == decision["reason"]:
                continue
            ledger["entries"][key] = dict(previous, origin=candidate["origin"], source=candidate["source"],
                source_vault=candidate["source_vault"], source_revision=candidate["source_revision"],
                source_entry_id=(candidate["entry"] or {}).get("id", previous.get("source_entry_id")),
                collection=candidate["collection"], target=candidate.get("target"),
                scope=(candidate["entry"] or {}).get("scope", previous.get("scope", [])),
                seen_hash=candidate["remote_hash"], decision=action, status=candidate["status"], reason=decision["reason"])
    # Tradução por fonte evita que IDs iguais em duas bases sejam confundidos.
    mappings, safe_members = {}, {}
    for key, previous in ledger["entries"].items():
        if previous.get("target") in all_own:
            mappings.setdefault(previous["source"], {})[previous.get("source_entry_id", previous["origin"]["id"])] = previous["target"]
    for candidate, decision, key, target, value in chosen:
        mappings.setdefault(candidate["source"], {})[candidate["entry"]["id"]] = target
    # Uma origem já incorporada pode ter chegado por outro colega.
    for candidate in plan["candidates"]:
        previous = ledger["entries"].get(digest(candidate["origin"]), {})
        if previous.get("target") in all_own and candidate.get("entry"):
            mappings.setdefault(candidate["source"], {})[candidate["entry"]["id"]] = previous["target"]
    from .sources import external_entries
    current_entries = list(external_entries(vault, include_inactive=True))
    for entry in current_entries:
        previous = ledger["entries"].get(digest(identity(entry, entry["source_vault"])), {})
        if previous.get("target") not in all_own: continue
        mappings.setdefault(entry["source"], {})[entry["id"]] = previous["target"]
        if previous.get("remote_hash") == digest(value_of(entry)) and previous.get("strategy", "copy") == "copy" \
                and previous.get("local_hash") == digest(value_of(all_own[previous["target"]][1])):
            safe_members.setdefault(entry["source"], set()).add(entry["id"])
    for candidate, decision, key, target, value in chosen:
        if decision["action"] != "merge" and value == value_of(candidate["entry"]):
            safe_members.setdefault(candidate["source"], set()).add(candidate["entry"]["id"])
    # A segurança de um resumo é transitiva: um ancestral não confirma membros pendentes de um filho.
    changed = True
    while changed:
        changed = False
        for entry in current_entries:
            safe = safe_members.get(entry["source"], set())
            if entry["collection"] == "groups" and entry["id"] in safe and not set(entry.get("members", [])) <= safe:
                safe.remove(entry["id"]); changed = True
    revisions = {i: entry.get("revision", 0) for i, (_, entry) in all_own.items()}
    revisions.update({target: revisions.get(target, 0) + 1 for _, _, _, target, _ in chosen})
    changes = []
    for candidate, decision, key, target, value in chosen:
        # Values explícitos de merge já usam IDs locais; cópias da origem são remapeadas.
        strategy = "merge" if decision["action"] == "merge" or value != value_of(candidate["entry"]) else "copy"
        if decision["action"] != "merge":
            value = _remap(value, mappings.get(candidate["source"], {}), revisions,
                           safe_members.get(candidate["source"], set()))
        previous = all_own.get(target)
        if previous:
            value["origin"] = copy.deepcopy(previous[1].get("origin", dict(vault_id=snapshot["metadata"]["vault_id"], id=target)))
        else:
            value["origin"] = candidate["origin"]
        # Não permitir add exato de uma descoberta com outra identidade.
        if candidate["collection"] == "records" and not previous:
            normalized = " ".join(value.get("content", "").casefold().split())
            compared = list(all_own.values()) + [(c["collection"], c["value"]) for c in changes]
            if any(collection == "records" and entry.get("scope") == value.get("scope") and
                   entry.get("kind", "knowledge") == value.get("kind", "knowledge") and
                   " ".join(entry.get("content", "").casefold().split()) == normalized
                   for collection, entry in compared):
                raise ValueError("Conhecimento equivalente já existe; faça merge com o registro local")
        change = dict(collection=candidate["collection"], id=target, value=value)
        if previous:
            removed = sorted(set(previous[1]) - set(value) - {"id", "revision", "origin"})
            if removed: change["remove_fields"] = removed
        changes.append(change)
        ledger["entries"][key] = dict(origin=candidate["origin"], source=candidate["source"],
            source_vault=candidate["source_vault"], source_revision=candidate["source_revision"],
            source_entry_id=candidate["entry"]["id"], strategy=strategy,
            collection=candidate["collection"], target=target, scope=candidate["entry"]["scope"],
            remote_hash=candidate["remote_hash"], local_hash=digest(value_of(value)),
            seen_hash=candidate["remote_hash"], decision="incorporated", reason=decision["reason"])
    if ledger == original: return dict(status="unchanged", incorporated=[], publication=dict(status="unchanged"))
    changes.append(dict(collection="metadata", id="memory", value=dict(source_sync=ledger)))
    clean(vault)
    proposal = vault.prepare(changes, payload.get("assessment", {}), actor, expected_base_hash=plan["base_hash"])
    result = apply_and_publish(vault, proposal["id"], proposal["approval_hash"])
    return dict(status="memory_updated" if chosen else "decisions_recorded", incorporated=[target for _, _, _, target, _ in chosen],
                pending=[key for key, entry in ledger["entries"].items() if entry.get("decision") == "pending"],
                proposal=result["proposal"], paths=result["paths"], publication=result["publication"],
                stale_summaries=proposal["stale_summaries"])
