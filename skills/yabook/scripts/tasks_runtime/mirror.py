"""Espelhamento de saída: papel e `size` das tarefas viram Status e Size no GitHub Project da issue.

Só publica; o que mudar no Project não volta para o YABook. Roda em segundo plano
(`task espelhar`, disparado pelo Stop quando houve commit) e guarda em
`local/espelho.json` o último estado publicado por issue, para enviar apenas
diferenças e tentar de novo o que falhou.

Mapeamento do papel para a opção de Status, nesta ordem: `tasks.espelho.status` na
configuração por coluna ou papel (`{"dono/repo" ou "*": {"testes": "Validação interna",
"validacao": "Validação QA"}}`), a opção com o
mesmo nome da coluna do YABook e a opção cujo nome combina com o papel.

Segurança com o fluxo da equipe: o Status só avança (nunca volta) e estado que o
YABook não reconhece (bloqueado, ajustes, pronto para merge, épicos, arquivados)
não é alterado.
"""
import datetime
import json
import re
import subprocess
import unicodedata

from .store import atomic_write

WINDOW_DAYS = 14  # tarefas atualizadas há mais tempo não são republicadas
ROLE_PATTERNS = {
    "entrada": r"backlog|entrada|novo|nova",
    "pronto": r"^pronto$|pronto (para|pra) (dev|desenv)|ready|a fazer|to ?do",
    "ativo": r"andamento|progress|doing|desenvolv",
    "validacao": r"valida|revis|review|qa|teste|homolog",
    "concluido": r"conclu|done|feito|finaliz",
}
RANK = {"entrada": 0, "pronto": 1, "ativo": 2, "validacao": 3, "concluido": 4}
TEAM_ONLY = r"bloque|ajuste|merge|epico|arquiv|impedid"
_REF = re.compile(r"([^/]+)/([^#]+)#(\d+)")
_QUERY = """query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){projectItems(first:10){nodes{
id project{id status:field(name:"Status"){... on ProjectV2SingleSelectField{id options{id name}}}
size:field(name:"Size"){... on ProjectV2SingleSelectField{id options{id name}}}}
statusValue:fieldValueByName(name:"Status"){... on ProjectV2ItemFieldSingleSelectValue{name}}
sizeValue:fieldValueByName(name:"Size"){... on ProjectV2ItemFieldSingleSelectValue{name}}}}}}}"""
_MUTATION = """mutation($p:ID!,$i:ID!,$f:ID!,$v:String!){updateProjectV2ItemFieldValue(input:{projectId:$p,itemId:$i,fieldId:$f,
value:{singleSelectOptionId:$v}}){projectV2Item{id}}}"""


def _plain(text):
    return unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode().lower()


def gh_graphql(query, **variables):
    args = ["gh", "api", "graphql", "-f", "query=" + query]
    for key, value in variables.items():
        args += ["-F" if isinstance(value, int) else "-f", "%s=%s" % (key, value)]
    result = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout).strip()[:300])
    return json.loads(result.stdout).get("data") or {}


def status_option(options, role, repo, mapping, column_name=None, column_id=None):
    """Opção de Status: mapeamento da coluna ou do papel, nome da coluna ou nome semelhante."""
    wanted = next((m[k] for m in (mapping.get(repo) or {}, mapping.get("*") or {}) for k in (column_id, role) if k and m.get(k)), None)
    names = {_plain(o["name"]): o for o in options}
    if wanted and _plain(wanted) in names:  # Project sem a opção configurada cai no nome da coluna ou do papel
        return names[_plain(wanted)]
    if column_name and _plain(column_name) in names:
        return names[_plain(column_name)]
    pattern = ROLE_PATTERNS.get(role)
    return next((o for o in options if pattern and re.search(pattern, _plain(o["name"]))), None) if pattern else None


def role_of(name):
    """Papel de uma opção de Status do Project; None quando é estado só da equipe."""
    plain = _plain(name)
    if not plain or re.search(TEAM_ONLY, plain):
        return None
    return next((role for role, pattern in ROLE_PATTERNS.items() if re.search(pattern, plain)), None)


def advances(current, target, target_role, options):
    """Só avança: item sem Status recebe; estado da equipe ou etapa igual/à frente não muda.

    No mesmo papel (ex.: validação interna e validação QA) vale a ordem das opções no Project."""
    if not current:
        return True
    role = role_of(current)
    if role is None:
        return False
    if RANK.get(target_role, -1) != RANK.get(role, -1):
        return RANK.get(target_role, -1) > RANK.get(role, -1)
    order = [o["name"] for o in options]
    return current in order and target in order and order.index(target) > order.index(current)


def pending(store, state, roles, today=None):
    """(tarefa, ref, papel, size) cujo estado difere do último publicado."""
    today = today or datetime.date.today()
    result = []
    for task in store.list():
        data = task["data"]
        if data.get("tipo") == "pergunta" or not data.get("issue"):
            continue
        updated = (data.get("atualizada") or "")[:10]
        if updated and (today - datetime.date.fromisoformat(updated)).days > WINDOW_DAYS:
            continue
        role = roles.get(data.get("coluna"))
        for ref in data["issue"]:
            if state.get(ref) != [role, data.get("size")]:
                result.append((data, ref, role, data.get("size")))
    return result


def run(store, cfg, dry_run=False, graphql=gh_graphql, today=None):
    path = store.root / "local" / "espelho.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        state = {}
    roles = {c["id"]: c["papel"] for c in store.columns()}
    names = {c["id"]: c["nome"] for c in store.columns()}
    mapping = ((cfg or {}).get("espelho") or {}).get("status") or {}
    report = []
    for data, ref, role, size in pending(store, state, roles, today):
        match = _REF.fullmatch(ref)
        entry = dict(id=data["id"], ref=ref, papel=role, size=size, alteracoes=[])
        if not match:
            continue
        try:
            nodes = (((graphql(_QUERY, o=match.group(1), r=match.group(2), n=int(match.group(3)))
                       .get("repository") or {}).get("issue") or {}).get("projectItems") or {}).get("nodes") or []
            for node in nodes:
                project = node.get("project") or {}
                changes = []
                status = project.get("status") or {}
                option = (status_option(status.get("options") or [], role, "%s/%s" % match.group(1, 2), mapping,
                                        names.get(data.get("coluna")), data.get("coluna"))
                          if status and data.get("nivel") != "epico" else None)
                current = (node.get("statusValue") or {}).get("name")
                if option and current != option["name"] and advances(current, option["name"], role, status.get("options") or []):
                    changes.append(("Status", status["id"], option))
                sizes = project.get("size") or {}
                option = next((o for o in sizes.get("options") or [] if o["name"].strip() == str(size)), None) if size else None
                if option and (node.get("sizeValue") or {}).get("name") != option["name"]:
                    changes.append(("Size", sizes["id"], option))
                for field, field_id, option in changes:
                    if not dry_run:
                        graphql(_MUTATION, p=project["id"], i=node["id"], f=field_id, v=option["id"])
                    entry["alteracoes"].append("%s: %s" % (field, option["name"]))
            if not dry_run:
                state[ref] = [role, size]
        except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as error:
            entry["erro"] = str(error)[:200]  # tenta de novo no próximo espelhamento
        report.append(entry)
    if not dry_run:
        atomic_write(path, json.dumps(state, ensure_ascii=False, indent=0) + "\n")
    return dict(publicadas=[e for e in report if e["alteracoes"]], erros=[e for e in report if e.get("erro")],
                verificadas=len(report), simulacao=dry_run)
