"""Fluxo de issue no YABook Tasks: a tarefa ligada a `dono/repo#n` acompanha o `dev`.

- inicio: branch da issue criada ou selecionada -> papel `ativo` e tarefa ativa;
- revisao: fim do `dev` ou PR aberto -> papel `validacao`;
- integrado: PR integrado -> papel `concluido`.

A fase nunca recua a tarefa (abrir a branch de uma tarefa em validação não a
devolve para andamento) e repetir a mesma fase não duplica o registro.
"""
import json
import re
import subprocess
from pathlib import Path

from .commands import Tasks
from .store import atomic_write, now

PHASES = ("inicio", "revisao", "integrado")
_RANK = {"entrada": 0, "pronto": 1, "ativo": 2, "validacao": 3, "concluido": 4, "arquivado": 5}
_TARGET = {"inicio": "ativo", "revisao": "validacao", "integrado": "concluido"}
_BRANCH = re.compile(r"^(\d+)-")
_REMOTE = re.compile(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$")


def _git(cwd, *args):
    try:
        result = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return result.stdout.strip() if not result.returncode else ""


def repo_of(cwd):
    match = _REMOTE.search(_git(cwd, "remote", "get-url", "origin"))
    return "%s/%s" % (match.group(1), match.group(2)) if match else None


def ref_from_branch(cwd, branch=None):
    """`dono/repo#n` a partir da branch `n-descricao` e do remoto `origin` do GitHub."""
    branch = branch or _git(cwd, "rev-parse", "--abbrev-ref", "HEAD")
    match = _BRANCH.match(branch or "")
    repo = repo_of(cwd) if match else None
    return "%s#%s" % (repo, match.group(1)) if match and repo else None


def find(store, ref):
    wanted = ref.lower()
    roles = {c["id"]: c["papel"] for c in store.columns()}
    for task in store.list():
        data = task["data"]
        if roles.get(data.get("coluna")) == "arquivado" or data.get("tipo") == "pergunta":
            continue
        if wanted in (i.lower() for i in data.get("issue", [])):
            return task
    return None


def advance(store, cfg, ref, fase, registro=None, pr=None, branch=None, session=None):
    """Aplica a fase à tarefa da issue; devolve None quando não há tarefa para a referência."""
    if fase not in PHASES:
        raise ValueError("Fase inválida: %s; use %s" % (fase, ", ".join(PHASES)))
    task = find(store, ref)
    if task is None:
        return None
    tasks = Tasks(store, cfg)
    roles = tasks.roles()
    data, role = task["data"], roles.get(task["data"].get("coluna"))
    target = _TARGET[fase]
    changes, unset = {}, []
    if _RANK.get(role, 0) < _RANK[target] and role != "arquivado":
        changes["coluna"] = tasks.first_column(target)
    if fase == "revisao" and changes:
        changes["proximo_passo"] = "Revisar e integrar o PR" if pr else "Revisar a implementação e abrir o PR"
    if fase == "integrado" and role != "concluido":
        unset = [k for k in ("proximo_passo", "aguardando") if k in data]
    note = registro or {"inicio": "Desenvolvimento iniciado%s." % (" na branch " + branch if branch else ""),
                        "revisao": "PR aberto: %s." % pr if pr else "Desenvolvimento concluído; aguardando revisão.",
                        "integrado": "Integrado no PR %s." % pr if pr else "Integrado."}[fase]
    if ("— " + note) in task["body"]:
        note = None  # mesma fase repetida não duplica o registro
    result = dict(id=data["id"], fase=fase, coluna=changes.get("coluna", data["coluna"]), movida=bool(changes.get("coluna")))
    if changes or unset or note:
        tasks.edit(data["id"], changes, unset, note, task["revision"])
    if fase == "inicio":
        atomic_write(store.root / "local" / "ativa.json",
                     json.dumps(dict(id=data["id"], desde=now(), origem="issue"), ensure_ascii=False) + "\n")
        if session:
            from . import capture
            capture.set_active(store, session, data["id"])
    return result


def merged_pr(cwd, number):
    """Referência da issue e URL de um PR integrado, consultando o GitHub; None se não integrado."""
    try:
        result = subprocess.run(["gh", "pr", "view", str(number), "--json", "state,headRefName,url"],
                                cwd=str(cwd), capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    info = json.loads(result.stdout)
    if info.get("state") != "MERGED":
        return None
    ref = ref_from_branch(cwd, info.get("headRefName"))
    return (ref, info.get("url")) if ref else None
