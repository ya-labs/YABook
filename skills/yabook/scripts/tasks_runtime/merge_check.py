"""Conclusão de tarefa com issue: exige PR integrado quando a issue tem branch ou PR.

Consulta no GitHub as branches vinculadas, os PRs que fecham a issue e os PRs
ligados ou que a citam. Regras:
- algum PR integrado (em qualquer base; há repositórios que integram em `dev`): pode concluir;
- sem branch vinculada e sem PR: a issue não passa por código, pode concluir;
- com branch ou PR, mas nenhum integrado: não pode concluir.
Devolve True (pode), False (não pode) ou None (não foi possível consultar).
"""
import json
import re
import subprocess

_REF = re.compile(r"([^/]+)/([^#]+)#(\d+)")
_QUERY = """query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){issue(number:$n){
linkedBranches(first:5){totalCount}
closedByPullRequestsReferences(first:20,includeClosedPrs:true){nodes{merged}}
timelineItems(first:50,itemTypes:[CONNECTED_EVENT,CROSS_REFERENCED_EVENT]){nodes{
... on ConnectedEvent{subject{... on PullRequest{merged}}}
... on CrossReferencedEvent{source{... on PullRequest{merged}}}}}}}}"""


def evaluate(issue):
    """Regra aplicada ao resultado da consulta (separada para teste)."""
    prs = [n or {} for n in (issue.get("closedByPullRequestsReferences") or {}).get("nodes") or []]
    for item in (issue.get("timelineItems") or {}).get("nodes") or []:
        pr = ((item or {}).get("subject") or (item or {}).get("source")) or {}
        if "merged" in pr:  # citação por issue (não PR) não conta
            prs.append(pr)
    if any(pr.get("merged") for pr in prs):
        return True
    has_branch = ((issue.get("linkedBranches") or {}).get("totalCount") or 0) > 0
    return not (has_branch or prs)


def can_conclude(ref, timeout=20):
    match = _REF.fullmatch(ref or "")
    if not match:
        return None
    try:
        result = subprocess.run(["gh", "api", "graphql", "-f", "query=" + _QUERY, "-f", "o=" + match.group(1),
                                 "-f", "r=" + match.group(2), "-F", "n=" + match.group(3)],
                                capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode:
        return None
    issue = (((json.loads(result.stdout).get("data") or {}).get("repository") or {}).get("issue")) or {}
    return evaluate(issue) if issue else None
