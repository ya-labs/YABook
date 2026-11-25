"""Captura pelo hook: cópia antes de `Edit`/`Write`/`apply_patch` e backup de comandos de edição.

Edições por comando (ex.: script que preserva encoding) não informam o alvo de forma confiável.
Para elas o hook marca o início no `PreToolUse` e, no `PostToolUse`, procura os backups que o
próprio comando gravou depois dessa marca. O backup traz a versão anterior, então não há cópia extra.

Em repositório Git, qualquer comando de shell também é comparado: o hook tira um retrato do worktree
antes e depois (árvore gravada por um índice temporário, sem tocar no índice real nem no stash) e
registra a versão anterior de cada arquivo que o comando alterou, criou ou removeu.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from . import store

STARTED = "diff_command_started"
GIT_SNAPSHOT = "diff_git_snapshot"
GIT_TIMEOUT = 4
# Comandos Git que trocam o conteúdo do worktree por decisão da pessoa, não por edição do agente.
GIT_WORKTREE = re.compile(r"\bgit\b[^;&|]*\b(switch|checkout|pull|merge|rebase|reset|stash|cherry-pick|revert|restore|"
                          r"apply|am|clone)\b")


def _git(cwd, *args, env=None):
    return subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, timeout=GIT_TIMEOUT, env=env)


def git_snapshot(root):
    """Árvore com o estado atual do worktree (rastreados e novos não ignorados); None fora do Git ou em falha."""
    try:
        top = _git(root, "rev-parse", "--show-toplevel")
        if top.returncode:
            return None
        top = top.stdout.decode().strip()
        index = _git(top, "rev-parse", "--git-path", "index").stdout.decode().strip()
        index = Path(index) if Path(index).is_absolute() else Path(top) / index
        with tempfile.TemporaryDirectory() as folder:
            temporary = Path(folder) / "index"
            if index.exists():
                shutil.copy2(index, temporary)  # parte do índice real: o cache de stat deixa o add rápido
            env = dict(os.environ, GIT_INDEX_FILE=str(temporary))
            if _git(top, "add", "-A", env=env).returncode:
                return None
            tree = _git(top, "write-tree", env=env)
        return dict(top=top, tree=tree.stdout.decode().strip()) if tree.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def shell_command(cfg, command):
    options = store.settings(cfg)
    return bool(command) and options["enabled"] and options["shell"] and not GIT_WORKTREE.search(command)


def before_shell(cfg, root, command, state):
    if shell_command(cfg, command):
        snapshot = git_snapshot(root)
        if snapshot:
            state[GIT_SNAPSHOT] = snapshot


def after_shell(cfg, root, event, state):
    """Registra a versão anterior dos arquivos que o comando de shell mudou no repositório."""
    before = state.pop(GIT_SNAPSHOT, None)
    if not before:
        return 0
    after = git_snapshot(before["top"])
    if not after or after["tree"] == before["tree"]:
        return 0
    listing = _git(before["top"], "diff", "--name-status", "-z", "--no-renames", before["tree"], after["tree"])
    fields = listing.stdout.decode("utf-8", "surrogateescape").split("\0")
    changes = list(zip(fields[0::2], fields[1::2]))
    current, _ = session(cfg, root, event)
    recorded = 0
    with tempfile.TemporaryDirectory() as folder:
        for status, rel in changes:
            target = Path(before["top"]) / rel
            source = None
            if status != "A":  # versão anterior vem da árvore do retrato; arquivo criado não tem
                content = _git(before["top"], "show", "%s:%s" % (before["tree"], rel)).stdout
                source = Path(folder) / rel
                source.parent.mkdir(parents=True, exist_ok=True)
                source.write_bytes(content)
            recorded += current.record(target, source, origin="shell")
            current.record_round(state.get("diff_round"), target, source, origin="shell")
    return recorded


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
