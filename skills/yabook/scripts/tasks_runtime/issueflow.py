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
from .precommit_hook import find_terms
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


def advance(store, cfg, ref, fase, registro=None, pr=None, branch=None, session=None, relatorio=None):
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
    if fase == "integrado":
        if role != "concluido":
            unset = [k for k in ("proximo_passo", "aguardando") if k in data]
        if relatorio and not (data.get("relatorio_conclusao") or "").strip() and not find_terms(relatorio, store.terms):
            changes["relatorio_conclusao"] = relatorio
    note = registro or {"inicio": "Desenvolvimento iniciado%s." % (" na branch " + branch if branch else ""),
                        "revisao": "PR aberto: %s." % pr if pr else "Desenvolvimento concluído; aguardando revisão.",
                        "integrado": "Integrado no PR %s." % pr if pr else "Integrado."}[fase]
    if ("— " + note) in task["body"]:
        note = None  # mesma fase repetida não duplica o registro
    result = dict(id=data["id"], fase=fase, coluna=changes.get("coluna", data["coluna"]), movida=bool(changes.get("coluna")))
    if changes or unset or note:
        tasks.merge_confirmed = fase == "integrado"  # o merge já foi conferido no GitHub
        tasks.edit(data["id"], changes, unset, note, task["revision"])
    if fase == "inicio":
        atomic_write(store.root / "local" / "ativa.json",
                     json.dumps(dict(id=data["id"], desde=now(), origem="issue"), ensure_ascii=False) + "\n")
        if session:
            from . import capture
            notice = capture.set_active(store, session, data["id"], cfg)
            if notice:
                result["aviso_retroativo"] = notice
    return result


def issue_description(body):
    """Corpo de issue YABook no contrato da descrição da tarefa (bloco de IA vira seção)."""
    text = (body or "").replace("\r\n", "\n").strip()
    text = re.sub(r"^- (Tarefa|Entrega esperada|Limite|Objetivo|Entrega): ", r"- **\1** — ", text, flags=re.M)
    text = re.sub(r"<details>\s*<summary>Informações para IA</summary>\s*", "## Informações para IA\n\n", text)
    text = text.replace("</details>", "")
    return re.sub(r"^- \*\*(.+?):\*\* ", r"- **\1** — ", text, flags=re.M).strip()


def _gh_json(args, timeout=6):
    try:
        result = subprocess.run(["gh", *args], capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    try:
        return json.loads(result.stdout)
    except ValueError:
        return None


def create_from_issue(store, cfg, ref):
    """Cria a tarefa de uma issue sem tarefa, abaixo da tarefa do épico quando a issue é subissue.

    Sem `projeto`: o vínculo é a issue; projeto é código da empresa e tiraria a tarefa do trabalho pessoal."""
    match = re.match(r"^([^/#]+)/([^/#]+)#(\d+)$", ref or "")
    if not match or find(store, ref):
        return None
    owner, name, number = match.groups()
    info = _gh_json(["issue", "view", number, "-R", "%s/%s" % (owner, name), "--json", "title,body"])
    if not info or not info.get("title"):
        return None
    query = ("query($o:String!,$n:String!,$i:Int!){repository(owner:$o,name:$n){issue(number:$i){parent{number}}}}")
    parent = _gh_json(["api", "graphql", "-f", "query=" + query, "-f", "o=" + owner, "-f", "n=" + name, "-F", "i=" + number])
    parent_number = (((parent or {}).get("data") or {}).get("repository") or {}).get("issue") or {}
    parent_number = (parent_number.get("parent") or {}).get("number")
    epic = find(store, "%s/%s#%s" % (owner, name, parent_number)) if parent_number else None
    fields = dict(issue=[ref], descricao=issue_description(info.get("body")))
    if epic:
        fields.update(nivel="historia", pai=epic["data"]["id"])
    return Tasks(store, cfg).add("issue", info["title"], **fields)["id"]


def _report_from_pr(info):
    body = (info.get("body") or "").replace("\r\n", "\n").strip()
    body = re.sub(r"^<details>[^\S\n]*\n<summary>Informações para IA</summary>(.*?)^</details>[^\S\n]*$",
                  lambda block: "## Informações para IA\n\n" + block[1].strip(), body, flags=re.M | re.S)
    link = "[PR #%s](%s)" % (info["number"], info["url"])
    if re.match(r"^## Resumo rápido[^\S\n]*(?:\n|$)", body):
        return body + "\n\nPR integrado — " + link
    report = "## Resumo rápido\n\n- **Entrega** — %s\n- **PR integrado** — %s" % (info["title"], link)
    return report + "\n\n## O que mudou\n\n" + body if body else report


def merged_pr(cwd, number):
    """Referência da issue e relatório de um PR integrado; None se não integrado."""
    try:
        result = subprocess.run(["gh", "pr", "view", str(number), "--json", "state,headRefName,url,number,title,body"],
                                cwd=str(cwd), capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    info = json.loads(result.stdout)
    if info.get("state") != "MERGED":
        return None
    ref = ref_from_branch(cwd, info.get("headRefName"))
    return (ref, _report_from_pr(info)) if ref else None


_SIZE_QUERY = """query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){
projectItems(first:10){nodes{fieldValueByName(name:"Size"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}"""


def issue_size(ref):
    """`Size` da issue no Project (1 a 5), consultando o GitHub; None se ausente."""
    match = re.fullmatch(r"([^/]+)/([^#]+)#(\d+)", ref or "")
    if not match:
        return None
    try:
        result = subprocess.run(["gh", "api", "graphql", "-f", "query=" + _SIZE_QUERY, "-f", "o=" + match.group(1),
                                 "-f", "r=" + match.group(2), "-F", "n=" + match.group(3)],
                                capture_output=True, text=True, timeout=20)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    nodes = (((json.loads(result.stdout).get("data") or {}).get("repository") or {}).get("issue") or {}).get("projectItems", {}).get("nodes", [])
    for node in nodes:
        name = str((node.get("fieldValueByName") or {}).get("name") or "").strip()
        if name in ("1", "2", "3", "4", "5"):
            return int(name)
    return None


def sync_size(store, cfg, ref, size=None):
    """Copia o `Size` da issue para a tarefa; tamanho marcado pela pessoa prevalece."""
    task = find(store, ref)
    if task is None:
        return dict(id=None, ref=ref, motivo="Sem tarefa para a issue")
    data = task["data"]
    size = size if size is not None else issue_size(ref)
    if size is None or data.get("size_manual") or data.get("size") == size:
        return dict(id=data["id"], size=data.get("size"), alterada=False)
    Tasks(store, cfg).edit(data["id"], dict(size=size), append="Size %d copiado da issue %s." % (size, ref),
                           expected_revision=task["revision"])
    return dict(id=data["id"], size=size, alterada=True)
