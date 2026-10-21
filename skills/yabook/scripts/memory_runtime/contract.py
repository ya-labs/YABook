"""Revisão de memória após mudança de contrato: registros que ainda citam o que saiu da documentação."""
import re
import subprocess

from .search import fold, text

def spans(line):
    """Trechos de código da linha (segmentos ímpares entre crases) com cara de comando ou
    expressão: palavra solta como `bypass` é genérica demais para apontar contradição."""
    result = []
    for span in (s.strip() for s in line.split("`")[1::2]):
        if 4 <= len(span) <= 80 and re.search(r"[\s$/.:-]", span):
            result.append(span)
    return result


def removed_terms(repository, base, head="HEAD", paths=("*.md",)):
    """Trechos de código removidos no diff e não reescritos nas linhas adicionadas. `gone`: o
    contrato em `head` não os cita mais; `changed`: saíram de um trecho, mas seguem citados em outro."""
    def git(*args):
        return subprocess.run(["git", "-C", str(repository), *args], capture_output=True, text=True, check=True).stdout
    diff = git("diff", "--unified=0", base, head, "--", *paths)
    removed, added = [], []
    for line in diff.splitlines():
        if line.startswith("-") and not line.startswith("---"): removed.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"): added.append(line[1:])
    rewritten = fold("\n".join(added))
    terms = [t for t in dict.fromkeys(s for line in removed for s in spans(line)) if fold(t) not in rewritten]
    current = fold("\n".join(git("show", head + ":" + path) for path in git("ls-tree", "-r", "--name-only", head).splitlines()
                             if any(path.endswith(p.lstrip("*")) for p in paths)))
    return dict(gone=[t for t in terms if fold(t) not in current], changed=[t for t in terms if fold(t) in current])


def review(vault, gone=(), changed=()):
    """Registros próprios ativos que citam termos removidos; os que citam termos extintos vêm primeiro.
    A lista aponta candidatos: o agente lê cada registro e decide entre atualizar, substituir ou manter."""
    groups = dict(gone=[t for t in dict.fromkeys(gone) if t.strip()], changed=[t for t in dict.fromkeys(changed) if t.strip()])
    result = []
    for entry in vault.entries():
        if entry["collection"] not in ("records", "groups"):
            continue
        body = fold(text(entry))
        found = {name: [t for t in terms if fold(t) in body] for name, terms in groups.items()}
        if found["gone"] or found["changed"]:
            result.append(dict(id=entry["id"], title=entry["title"], revision=entry.get("revision"), **found))
    result.sort(key=lambda r: (-len(r["gone"]), -len(r["changed"]), r["id"]))
    return dict(terms=groups, candidates=result)
