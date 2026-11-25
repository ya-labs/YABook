"""Captura pelo hook: cópia antes de `Edit`/`Write`/`apply_patch` e backup de comandos de edição.

Edições por comando (ex.: script que preserva encoding) não informam o alvo de forma confiável.
Para elas o hook marca o início no `PreToolUse` e, no `PostToolUse`, procura os backups que o
próprio comando gravou depois dessa marca. O backup traz a versão anterior, então não há cópia extra.
"""
from __future__ import annotations

import os
import re
import time
from pathlib import Path

from . import store

STARTED = "diff_command_started"


def session(cfg, root, event):
    options = store.settings(cfg)
    current = store.Session(options["base"], root, store.session_key(event), event.get("agent", ""))
    if not current.folder.exists():
        store.prune(options["base"], options["retention"], keep=current.folder)
    return current, options


def new_round(prompt):
    """Rodada aberta por uma mensagem da pessoa; o trecho ajuda a reconhecê-la na lista."""
    text = re.sub(r"<([\w-]+)[^>]*>.*?</\1>", " ", prompt or "", flags=re.S)
    text = " ".join(text.split())
    return dict(chave="%.6f" % time.time(), pedido=text[:80] + ("…" if len(text) > 80 else ""))


def before_edit(cfg, root, event, targets, round_info=None):
    """Guarda a versão de cada alvo antes da primeira edição na sessão e na rodada."""
    if not targets or not store.settings(cfg)["enabled"]:
        return 0
    current, _ = session(cfg, root, event)
    recorded = 0
    for target in targets:
        target = Path(target)
        if target.is_dir():
            continue
        source = target if target.exists() else None
        recorded += current.record(target, source)
        current.record_round(round_info, target, source)
    return recorded


def edit_command(cfg, command):
    options = store.settings(cfg)
    return options["enabled"] and any(pattern in command for pattern in options["commands"])


def before_command(cfg, command, state):
    if command and edit_command(cfg, command):
        state[STARTED] = time.time()
        return True
    return False


def backups_since(root, rules, started):
    """Backups gravados desde `started`: (arquivo original, backup) por regra configurada."""
    found = []
    for rule in rules:
        folder = Path(rule.get("dir", "backup")).expanduser()
        folder = folder if folder.is_absolute() else Path(root) / folder
        origin = Path(rule.get("origin")).expanduser() if rule.get("origin") else folder.parent
        pattern = re.compile(rule.get("pattern") or store.BACKUP_PATTERN)
        if not folder.is_dir():
            continue
        for current, _, files in os.walk(folder):
            for name in files:
                path = Path(current) / name
                match = pattern.search(name)
                if not match or path.stat().st_mtime < started - 1:
                    continue
                rel = path.relative_to(folder).as_posix()[: -len(match.group(0))]
                found.append((origin / rel, path))
    return sorted(found, key=lambda pair: pair[1].stat().st_mtime)


def after_command(cfg, root, event, state):
    """Registra o backup mais antigo de cada arquivo alterado pelo comando de edição, na sessão e na rodada."""
    started = state.pop(STARTED, None)
    if started is None:
        return 0
    pairs = backups_since(root, store.settings(cfg)["backups"], started)
    if not pairs:
        return 0
    current, _ = session(cfg, root, event)
    recorded = 0
    for original, backup in pairs:
        recorded += current.record(original, backup, origin="backup")
        current.record_round(state.get("diff_round"), original, backup, origin="backup")
    return recorded
