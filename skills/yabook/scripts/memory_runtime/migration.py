"""Leitura integral em blocos e cobertura retomável; a avaliação pertence ao agente."""
from pathlib import Path
from contextlib import contextmanager
import fcntl

from .core import COLLECTIONS, digest, read_json, write_json
from .gitstore import inventory

DECISIONS = {"migrated", "consolidated", "kept", "discarded", "pending"}


@contextmanager
def state_lock(path):
    path = Path(path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    with Path(str(path) + ".lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def start(agent, source, output, block_lines=200):
    if not 1 <= block_lines <= 1000:
        raise ValueError("Blocos devem conter de 1 a 1000 linhas")
    inv = inventory(agent, source)
    if not inv["accessible"]:
        raise ValueError("Origem inacessível; não equivale a memória inexistente")
    output = Path(output).expanduser().resolve()
    origin = Path(inv["source"])
    if output == origin or (origin.is_dir() and origin in output.parents):
        raise ValueError("Checkpoint precisa ficar fora da origem")
    with state_lock(output):
        previous = read_json(output) if output.exists() else None
        if previous and (previous["agent"] != inv["agent"] or previous["source"] != inv["source"]):
            raise ValueError("Checkpoint pertence a outra origem/agente")
        if previous and previous["block_lines"] != block_lines:
            raise ValueError("Preserve o tamanho dos blocos ao retomar")
        old = {b["id"]: b for b in previous["blocks"]} if previous else {}
        blocks = []
        for file in inv["files"]:
            # Nenhum segredo é devolvido por block(); sua exclusão exige justificativa.
            count = file.get("lines", 0)
            spans = [(n, min(n + block_lines - 1, count)) for n in range(1, count + 1, block_lines)]
            if not spans:
                spans = [(0, 0)]
            for first, last in spans:
                identity = digest([file["path"], file.get("hash"), first, last])
                item = dict(id=identity, path=file["path"], hash=file.get("hash"),
                            first=first, last=last, status=file["status"])
                if identity in old:
                    item.update({k: old[identity][k] for k in ("decision", "reason", "targets") if k in old[identity]})
                blocks.append(item)
        state = dict(version=1, agent=inv["agent"], source=inv["source"], block_lines=block_lines,
                     inventory=inv, blocks=blocks)
        write_json(output, state)
        return coverage(state)


def verify(state):
    if state.get("version") != 1:
        raise ValueError("Formato de checkpoint desconhecido")
    current = inventory(state["agent"], state["source"])
    def signatures(inv):
        return [(f["path"], f.get("hash"), f["status"]) for f in inv["files"]]
    if not current["accessible"] or signatures(current) != signatures(state["inventory"]):
        raise ValueError("Origem mudou; retomar com migration-start para invalidar os blocos afetados")


def block(state, identifier=None):
    verify(state)
    item = next((b for b in state["blocks"] if b["id"] == identifier), None) if identifier else next(
        (b for b in state["blocks"] if b.get("decision") in (None, "pending")), None)
    if item is None:
        if identifier:
            raise ValueError("Bloco inexistente")
        return {"status": "complete", "coverage": coverage(state)}
    text = ""
    if item["status"] == "candidate" and item["first"]:
        lines = Path(item["path"]).read_text(encoding="utf-8").splitlines(keepends=True)
        text = "".join(lines[item["first"] - 1:item["last"]])
    return dict(item, text=text, checkpoint_hash=digest(state))


def checkpoint(path, payload):
    with state_lock(path):
        return _checkpoint(path, payload)


def _checkpoint(path, payload):
    state = read_json(path)
    verify(state)
    if payload.get("checkpoint_hash") != digest(state):
        raise ValueError("Checkpoint mudou; releia antes de registrar decisões")
    updates = payload.get("reviews", [])
    if not updates:
        raise ValueError("Informe avaliações dos blocos")
    by_id = {b["id"]: b for b in state["blocks"]}
    if len({r["id"] for r in updates}) != len(updates):
        raise ValueError("Bloco repetido no lote")
    for review in updates:
        item = by_id.get(review["id"])
        decision = review.get("decision")
        if item is None or decision not in DECISIONS or not isinstance(review.get("reason"), str) or not review["reason"].strip():
            raise ValueError("Avaliação exige bloco, decisão e justificativa")
        targets = review.get("targets", [])
        if not isinstance(targets, list) or any(not isinstance(t, dict) or t.get("collection") not in COLLECTIONS or not isinstance(t.get("id"), str) or not t["id"] for t in targets):
            raise ValueError("Referências de destino inválidas")
        if decision in {"migrated", "consolidated", "kept"} and not targets:
            raise ValueError("Memória aproveitada exige referências de destino")
        if item["status"] != "candidate" and decision != "discarded":
            raise ValueError("Arquivo sensível/inacessível só pode ser excluído com justificativa")
        item.update(decision=decision, reason=review["reason"], targets=targets)
    write_json(path, state)
    return coverage(state)


def coverage(state):
    verify(state)
    counts = {d: 0 for d in DECISIONS}
    counts["unreviewed"] = 0
    for item in state["blocks"]:
        counts[item.get("decision", "unreviewed")] += 1
    return dict(complete=not counts["unreviewed"] and not counts["pending"],
                files=len(state["inventory"]["files"]), blocks=len(state["blocks"]), counts=counts,
                checkpoint_hash=digest(state),
                limitations=state["inventory"]["limitations"] + [
                    "Cobertura de leitura não comprova correção semântica; o agente deve revisar fatos, conflitos e aplicação"])


def validate_targets(state, curated, baseline=None):
    changes = {(c["collection"], c["id"]): c for c in curated["changes"]}
    for item in state["blocks"]:
        for target in item.get("targets", []):
            key = (target["collection"], target["id"])
            change = changes.get(key)
            existing = (baseline or {}).get(key[0], {}).get(key[1])
            if (change and change.get("delete")) or (not change and existing is None):
                raise ValueError("Cobertura aponta para memória ausente ou removida")
            if item["decision"] in {"migrated", "consolidated"}:
                value = change["value"] if change else existing
                provenance = value.get("provenance", [])
                lines = str(item["first"]) if item["first"] == item["last"] else f'{item["first"]}-{item["last"]}'
                if not any(p.get("file") == item["path"] and p.get("hash") == item["hash"] and p.get("lines") == lines for p in provenance):
                    raise ValueError("Memória migrada exige procedência do bloco: arquivo, hash e linhas")
