#!/usr/bin/env python3
"""Trava de commit do repositório de dados do YABook Tasks.

Este arquivo é copiado como `.githooks/pre-commit` pelo `do task init` e também
é importado pelo runtime, para que a regra exista num único lugar. A lista de
termos proibidos fica fora do repositório; o caminho vem de `git config
yabook.terms`. Sem lista, o commit segue com aviso.
"""
import os
import re
import subprocess
import sys


def load_terms(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as stream:
        return [line.strip() for line in stream if line.strip() and not line.lstrip().startswith("#")]


def find_terms(text, terms):
    """Termos presentes como palavra inteira, sem diferenciar maiúsculas."""
    found = []
    for term in terms or ():
        if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text, re.IGNORECASE) and term not in found:
            found.append(term)
    return found


def _git(*args):
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def staged_hits(terms):
    hits, current = [], None
    diff = _git("diff", "--cached", "-U0", "--no-color", "--diff-filter=ACMR")
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else line[4:]
            for term in find_terms(current, terms):
                hits.append((current, term))
        elif line.startswith("+") and current:
            for term in find_terms(line[1:], terms):
                hits.append((current, term))
    return sorted(set(hits))


def main():
    terms = load_terms(_git("config", "--get", "yabook.terms").strip())
    if terms is None:
        print("YABook Tasks: lista de termos proibidos ausente nesta máquina; commit sem verificação.", file=sys.stderr)
        return 0
    hits = staged_hits(terms)
    if not hits:
        return 0
    print("YABook Tasks: commit bloqueado por termo proibido.", file=sys.stderr)
    for path, term in hits:
        print("  %s: %s" % (path, term), file=sys.stderr)
    print("Mova o texto para o complemento confidencial e use apenas referência.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
