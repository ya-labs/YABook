#!/usr/bin/env python3
"""Publica a versão atual da extensão como release do GitHub, com o `.vsix` anexado.

Tag `vscode-v<versão>` (separada das releases do plugin), apontando para o commit integrado
na branch principal. Recusa worktree sujo, commit fora da `main` remota e tag já publicada.

Uso: python3 apps/vscode/scripts/release.py [--notas <arquivo.md>] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import package  # noqa: E402

ROOT = package.ROOT
REPO_ROOT = ROOT.parents[1]


def run(*args, check=True):
    result = subprocess.run(args, cwd=REPO_ROOT, capture_output=True, text=True)
    if check and result.returncode:
        raise SystemExit("Falhou: %s\n%s" % (" ".join(args), result.stderr.strip()))
    return result


def body(version, notes):
    changes = notes.strip() if notes else "- Veja os PRs integrados desde a release anterior da extensão."
    return f"""## Resumo rápido

- Objetivo: distribuir a extensão YABook para VS Code por link, sem clonar o repositório.
- Entrega: `yabook-{version}.vsix` anexado a esta release.

## O que mudou

{changes}

## Instalação

```bash
gh release download vscode-v{version} -R ya-labs/YABook -p 'yabook-*.vsix'
code --install-extension yabook-{version}.vsix
```

Ou baixe o `.vsix` abaixo e use **Extensões → ... → Install from VSIX**; depois, `Developer: Reload Window`.

## Observações

- A extensão mostra o que o plugin YABook grava: instale e atualize o plugin (`$yabook do sync`).
"""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--notas", help="Markdown com a lista do que mudou nesta versão")
    parser.add_argument("--dry-run", action="store_true", help="Só mostra o que seria publicado")
    args = parser.parse_args(argv)

    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    tag = "vscode-v" + version
    if run("git", "status", "--porcelain").stdout.strip():
        raise SystemExit("Worktree com alterações: publique a partir do commit integrado, sem mudanças locais.")
    run("git", "fetch", "-q", "origin")
    head, main_head = run("git", "rev-parse", "HEAD").stdout.strip(), run("git", "rev-parse", "origin/main").stdout.strip()
    if head != main_head:
        raise SystemExit("HEAD (%s) não é o commit integrado em origin/main (%s)." % (head[:7], main_head[:7]))
    if run("gh", "release", "view", tag, check=False).returncode == 0:
        raise SystemExit("A release %s já existe; suba a versão em apps/vscode/package.json." % tag)
    notes = Path(args.notas).read_text(encoding="utf-8") if args.notas else ""
    title = "Publicar versão %s da extensão do VS Code" % version
    if args.dry_run:
        print(json.dumps(dict(tag=tag, titulo=title, commit=head[:7], corpo=body(version, notes)), ensure_ascii=False, indent=2))
        return 0
    vsix = package.build()
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as file:
        file.write(body(version, notes))
    created = run("gh", "release", "create", tag, str(vsix), "--target", head, "--title", title, "--notes-file", file.name)
    print(created.stdout.strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
