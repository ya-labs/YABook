"""Faxina periódica da memória: diagnóstico, recomendação por tempo/volume/problemas e registro."""
import glob
import re
import os
from datetime import datetime, timezone

from .core import read_json, snapshot_entries, stale_groups, write_json

DEFAULTS = dict(days=14, changes=10, problems=10, max_days=30, proposal_days=14, hypothesis_days=60)
LIMIT = 20  # itens listados por categoria; a contagem é sempre completa


def now():
    return datetime.now(timezone.utc)


def parse(value):
    try:
        moment = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return moment if moment.tzinfo else moment.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def settings(cfg):
    return dict(DEFAULTS, **(cfg.get("learning", {}).get("cleanup") or {}))


def last_cleanup(snapshot):
    """Data da última faxina; sem registro, conta desde a criação da base."""
    metadata = snapshot["metadata"]
    return parse(metadata.get("maintenance", {}).get("last_cleanup") or metadata.get("created_at")) or now()


def changes_since(vault, moment):
    """Lotes aplicados depois da data (recibos do histórico)."""
    count = 0
    for path in glob.glob(str(vault.root / "history" / "*.json")):
        receipt = read_json(path)
        created = parse(receipt.get("created_at"))
        # O lote que só registra a faxina não é alteração de conhecimento.
        if all(c.get("collection") == "metadata" for c in receipt.get("changes", [])):
            continue
        count += bool(created and created > moment)
    return count


def problems(snapshot):
    """Problemas baratos de contar, usados também na recomendação."""
    entries = list(snapshot_entries(snapshot))
    groups = [e for e in entries if e["collection"] == "groups"]
    members = {m for g in groups for m in g.get("members", [])}
    group_ids = {g["id"] for g in groups}
    orphans = sorted(e["id"] for e in entries if e["collection"] == "records" and e["id"] not in members
                     and e.get("parent") not in group_ids and e.get("kind") != "profile"
                     and e.get("state") not in ("archived", "superseded"))
    return dict(stale_summaries=sorted(stale_groups(snapshot)), orphans=orphans)


def status(vault, cfg, snapshot=None):
    """Recomenda a faxina quando tempo e volume ou problemas acumulados passam dos limites."""
    snapshot = snapshot or vault.snapshot()
    limits = settings(cfg)
    since = last_cleanup(snapshot)
    days = (now() - since).days
    changes = changes_since(vault, since)
    found = problems(snapshot)
    count = len(found["stale_summaries"]) + len(found["orphans"])
    reasons = []
    if days >= limits["days"] and changes >= limits["changes"]:
        reasons.append(f"{days} dias e {changes} lotes desde a última faxina")
    if count >= limits["problems"]:
        reasons.append(f"{count} problema{'s' if count != 1 else ''} acumulado{'s' if count != 1 else ''}")
    if days >= limits["max_days"] and changes:
        reasons.append(f"{days} dias com alterações desde a última faxina")
    return dict(due=bool(reasons), days=days, changes=changes, stale_summaries=len(found["stale_summaries"]),
                orphans=len(found["orphans"]), reasons=reasons, last_cleanup=since.isoformat(timespec="seconds"))


def diagnose(vault, cfg):
    """Diagnóstico somente leitura para `memory clean`: o que é mecânico e o que exige julgamento."""
    snapshot = vault.snapshot()
    limits = settings(cfg)
    entries = list(snapshot_entries(snapshot))
    found = problems(snapshot)
    cutoff = now().timestamp()
    proposals = []
    for path in glob.glob(str(vault.local / "proposals" / "*.json")):
        if (cutoff - os.path.getmtime(path)) / 86400 >= limits["proposal_days"]:
            proposals.append(os.path.basename(path)[:-5])
    hypotheses, triggers, evidence = [], [], []
    for entry in entries:
        if entry["collection"] != "records" or entry.get("state") in ("archived", "superseded"):
            continue
        dates = [parse(e.get("date")) for e in entry.get("evidence", []) if e.get("date")]
        newest = max((d for d in dates if d), default=None)
        if entry.get("state") == "hypothesis" and (not newest or (now() - newest).days >= limits["hypothesis_days"]):
            hypotheses.append(entry["id"])
        found_triggers = entry.get("triggers") or []
        if entry.get("kind") in ("knowledge", "procedure") and found_triggers and all(len(t.split()) == 1 for t in found_triggers):
            triggers.append(entry["id"])
        if any(not portable(e) for e in entry.get("evidence", [])):
            evidence.append(entry["id"])
    judgment = dict(old_proposals=sorted(proposals), old_hypotheses=sorted(hypotheses),
                    single_word_triggers=sorted(triggers), evidence_elsewhere=sorted(evidence))
    return dict(status(vault, cfg, snapshot),
                totals={k: len(v) for k, v in dict(found, **judgment).items()},
                # Mecânico: encaixar em grupo e revisar resumo. Julgamento: decidir antes de mudar.
                mechanical={k: v[:LIMIT] for k, v in found.items()},
                judgment={k: v[:LIMIT] for k, v in judgment.items()})


LOCAL_REPORT = re.compile(r"rollout_summaries/|(?:^|/)sessions?/|\.jsonl\b|^(?:/home/|/Users/|/tmp/|~/|[A-Za-z]:\\)")


def portable(item):
    """Evidência vale em outra máquina se não aponta para relato/arquivo local ou se traz resumo."""
    return bool(item.get("summary")) or not LOCAL_REPORT.search(item.get("ref", ""))


def check(vault, cfg):
    """Diagnóstico que também fica salvo localmente como o "antes" da próxima conclusão."""
    report = diagnose(vault, cfg)
    write_json(vault.local / "clean-check.json", dict(at=now().isoformat(), totals=report["totals"]))
    return report


def done_change(vault, batches, note="", cfg=None):
    """Registra a faxina só se o número de lotes bate com o histórico; guarda o diagnóstico de
    antes (último clean-check desde a faxina anterior) e de depois, e as pendências mantidas."""
    batches = int(batches)
    snapshot = vault.snapshot()
    applied = changes_since(vault, last_cleanup(snapshot))
    after = diagnose(vault, cfg or {})
    pending = sum(len(v) for v in after["mechanical"].values())
    if batches < 0 or batches > applied:
        raise ValueError(f"Lotes informados ({batches}) não batem com os aplicados desde a última faxina ({applied})")
    if batches == 0 and pending:
        raise ValueError("Faxina sem lotes com pendências mecânicas: encaixe registros e revise resumos antes de concluir")
    saved = vault.local / "clean-check.json"
    before = read_json(saved) if saved.exists() else None
    if before and (parse(before.get("at")) or now()) < last_cleanup(snapshot):
        before = None  # diagnóstico anterior à última faxina não descreve esta
    return dict(collection="metadata", id="memory", value=dict(maintenance=dict(
        last_cleanup=now().isoformat(), batches=batches, note=note[:200],
        before=before["totals"] if before else None, after=after["totals"],
        kept={k: v for k, v in after["judgment"].items() if v})))
