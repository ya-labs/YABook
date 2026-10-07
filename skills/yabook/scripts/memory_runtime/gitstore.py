"""Migração avaliada e publicação restrita ao repositório próprio de memória."""
import json
import re
import subprocess
import tempfile
from pathlib import Path
from .core import Vault, digest, read_json, write_json, SECRET


def run(*args, check=True, timeout=60):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Tempo esgotado em " + args[0] + "; usar cache ou repetir após verificar rede") from exc
    if check and result.returncode:
        raise ValueError("Falha em " + args[0] + " " + args[1] + "; verificar autenticação/conectividade")
    return result


def git(root, *args, check=True, timeout=60):
    return run("git", "-C", str(root), *args, check=check, timeout=timeout)


def clean(vault):
    if (vault.root / ".git").exists():
        if Path(git(vault.root, "rev-parse", "--show-toplevel").stdout.strip()).resolve() != vault.root:
            raise ValueError("Base precisa de repositório próprio")
        if git(vault.root, "status", "--porcelain").stdout.strip():
            raise ValueError("Alterações independentes; separar antes de publicar")


def inventory(agent, source):
    source = Path(source).expanduser().resolve()
    if agent not in ("codex", "claude"): raise ValueError("Adaptador não suportado")
    result = dict(agent=agent, source=str(source), accessible=source.is_dir(), files=[],
                  limitations=["Somente arquivos persistentes acessíveis; não inclui memória oculta ou transcripts"])
    if not source.is_dir(): return result
    for path in sorted(source.rglob("*.md")):
        if path.is_symlink(): continue
        try: text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            result["files"].append(dict(path=str(path), status="unreadable")); continue
        if len(text.encode()) > 1_000_000:
            result["files"].append(dict(path=str(path), status="oversized")); continue
        sensitive = bool(SECRET.search(text))
        result["files"].append(dict(path=str(path), hash=digest(text), characters=len(text),
            status="sensitive" if sensitive else "candidate", excerpt="" if sensitive else text[:3000]))
    return result


def init_plan(root, agent, source, curated=None):
    owner = json.loads(run("gh", "api", "user").stdout)["login"]
    repository = owner + "/YABook-memory-" + owner
    remote = run("gh", "api", "repos/" + repository, check=False)
    if remote.returncode and "404" not in remote.stderr: raise ValueError("Falha de acesso ao destino")
    if not remote.returncode and not json.loads(remote.stdout).get("private"):
        raise ValueError("Repositório existente não é privado")
    plan = dict(owner=owner, repository=repository, private=True,
                root=str(Path(root).expanduser().resolve()), existing=remote.returncode == 0,
                inventory=inventory(agent, source), curated_hash=digest(curated) if curated else None,
                operations=["create-or-reuse-private-repository", "write-approved-records", "commit", "push", "configure-plugin"])
    plan["approval_hash"] = digest(plan)
    return plan


def init_apply(plan, approval_hash, curated, config_path):
    expected = dict(plan); expected.pop("approval_hash", None)
    if digest(expected) != approval_hash or plan["approval_hash"] != approval_hash:
        raise ValueError("Plano alterado")
    if plan.get("curated_hash") != digest(curated): raise ValueError("Curadoria diferente da aprovada")
    if json.loads(run("gh", "api", "user").stdout)["login"] != plan["owner"]:
        raise ValueError("Conta autenticada mudou")
    for entry in plan["inventory"]["files"]:
        if entry.get("hash") and digest(Path(entry["path"]).read_text(encoding="utf-8")) != entry["hash"]:
            raise ValueError("Origem mudou; atualizar inventário")
    root = Path(plan["root"]); repository = plan["repository"]
    if not re.fullmatch(r"[A-Za-z0-9-]+/YABook-memory-[A-Za-z0-9-]+", repository):
        raise ValueError("Nome de destino inválido")
    cfg_path = Path(config_path).expanduser()
    cfg = read_json(cfg_path) if cfg_path.exists() else {}
    if cfg.get("memory_root") and cfg["memory_root"] != str(root.resolve()):
        raise ValueError("Configuração já usa outra base")
    if root.exists() and any(root.iterdir()) and not (root / "memory.json").exists():
        raise ValueError("Destino local ocupado")
    # Validar estrutura antes de criar qualquer artefato remoto.
    if curated["changes"]:
        with tempfile.TemporaryDirectory(prefix="yabook-init-validation-") as directory:
            validator = Vault(Path(directory) / "vault")
            validator.bootstrap(plan["owner"])
            if (root / "memory.json").exists():
                baseline = Vault(root).snapshot()
                for collection in ("records", "entities", "groups"):
                    for identifier, entry in baseline[collection].items():
                        write_json(validator.path(collection, identifier), entry)
            validator.prepare(curated["changes"], curated["assessment"], "validation")
    remote = run("gh", "api", "repos/" + repository, check=False)
    if remote.returncode:
        if "404" not in remote.stderr: raise ValueError("Falha ao consultar destino")
        run("gh", "repo", "create", repository, "--private")
    elif not json.loads(remote.stdout).get("private"):
        raise ValueError("Destino não é privado")
    if plan["existing"] and not (root / "memory.json").exists():
        run("gh", "repo", "clone", repository, str(root))
    vault = Vault(root); vault.bootstrap(plan["owner"])
    if not (root / ".git").exists():
        git(root, "init", "-b", "main")
        git(root, "remote", "add", "origin", "https://github.com/" + repository + ".git")
    url = git(root, "remote", "get-url", "origin").stdout.strip()
    if url not in ("https://github.com/" + repository + ".git", "git@github.com:" + repository + ".git"):
        raise ValueError("Remoto diverge do plano")
    has_head = git(root, "rev-parse", "--verify", "HEAD", check=False).returncode == 0
    if has_head: clean(vault)
    paths = []
    snapshot = vault.snapshot()
    def effective(change):
        previous = snapshot[change["collection"]].get(change["id"])
        if change.get("delete"): return previous is not None
        ignored = {"id", "revision", "origin"}
        return previous is None or {k:v for k,v in previous.items() if k not in ignored} != {k:v for k,v in change["value"].items() if k not in ignored}
    changes = [c for c in curated["changes"] if effective(c)]
    if changes:
        proposal = vault.prepare(changes, curated["assessment"], "migration:" + plan["inventory"]["agent"])
        paths = vault.apply(proposal["id"], proposal["approval_hash"])["paths"]
    if not has_head: paths += ["memory.json", ".gitignore"]
    result = publish(vault, paths, "feat: inicializa memória YABook avaliada")
    cfg.update(memory_root=str(root.resolve()), repository=repository)
    write_json(cfg_path, cfg)
    return result


def publication_intent(vault, paths, message):
    pending = vault.local / "publication.json"
    receipt = dict(paths=sorted(set(paths)), message=message, commit=None)
    for path in receipt["paths"]:
        if vault.root not in (vault.root / path).resolve().parents or path.startswith(".yabook-local/"):
            raise ValueError("Path fora da proposta")
    receipt["files"] = {p: digest((vault.root / p).read_bytes().hex()) if (vault.root / p).exists() else None for p in receipt["paths"]}
    if pending.exists():
        previous = read_json(pending)
        if previous.get("files") != receipt["files"] or previous["paths"] != receipt["paths"]:
            raise ValueError("Outra publicação já está pendente")
        return previous
    write_json(pending, receipt)
    return receipt


def publish(vault, paths=None, message=None):
    pending = vault.local / "publication.json"
    with vault.lock():
        if pending.exists():
            receipt = read_json(pending); paths = receipt["paths"]; message = receipt["message"]
        else:
            if not paths: return {"status": "unchanged"}
            if git(vault.root, "diff", "--cached", "--name-only").stdout.strip():
                raise ValueError("Index contém alterações independentes")
            receipt = publication_intent(vault, paths, message)
        if not receipt["commit"]:
            current = {p: digest((vault.root / p).read_bytes().hex()) if (vault.root / p).exists() else None for p in receipt["paths"]}
            if current != receipt.get("files"):
                raise ValueError("Arquivos aprovados mudaram antes do commit; revisar publicação")
            git(vault.root, "add", "--", *receipt["paths"])
            staged = set(git(vault.root, "diff", "--cached", "--name-only").stdout.splitlines())
            if staged - set(receipt["paths"]): raise ValueError("Staged fora da proposta")
            if staged: git(vault.root, "commit", "-m", message)
            receipt["commit"] = git(vault.root, "rev-parse", "HEAD").stdout.strip()
            write_json(pending, receipt)
        branch = git(vault.root, "branch", "--show-current").stdout.strip()
        if not branch: raise ValueError("Publicação exige branch")
        if git(vault.root, "rev-parse", "HEAD").stdout.strip() != receipt["commit"]:
            raise ValueError("HEAD mudou; revisar publicação pendente")
        result = git(vault.root, "push", "-u", "origin", branch, check=False)
        if result.returncode: return dict(status="pending_push", commit=receipt["commit"], retry="publish")
        pending.unlink()
        return dict(status="published", commit=receipt["commit"])


def apply_and_publish(vault, identifier, approval_hash):
    if (vault.local / "publication.json").exists(): raise ValueError("Publicação pendente; execute publish")
    clean(vault)
    result = vault.apply(identifier, approval_hash)
    result["publication"] = publish(vault, result["paths"], "docs: aplica memória " + result["proposal"]) if (vault.root / ".git").exists() else dict(status="local_only")
    return result
