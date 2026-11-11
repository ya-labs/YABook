"""`task init` (prévia) e `do task init` (aplicação) do repositório de dados."""
import hashlib
import json
import re
import socket
from pathlib import Path

from . import remote
from .store import is_data_repo, scaffold

DEFAULT_ROOT = Path.home() / ".local/share/yabook/tasks"
_REPOSITORY = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+")


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def read_config(path):
    path = Path(path).expanduser()
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def write_config(path, value):
    from .store import atomic_write
    atomic_write(Path(path).expanduser(), json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def machine_name(value=None):
    name = re.sub(r"[^a-z0-9-]+", "-", (value or socket.gethostname()).lower()).strip("-")
    if not name:
        raise ValueError("Informe --machine com letras, números ou hífen")
    return name[:40]


def _resolve(path):
    return str(Path(path).expanduser().resolve()) if path else None


def _local_state(root, repository):
    root = Path(root)
    if not root.exists() or not any(root.iterdir()):
        return "absent"
    if not (root / ".git").exists():
        raise ValueError("Destino local ocupado por outro conteúdo: " + str(root))
    origin = remote.git(root, "remote", "get-url", "origin", check=False).stdout.strip()
    if origin not in remote.accepted_urls(repository):
        raise ValueError("Remoto local diverge do destino solicitado: " + (origin or "sem origin"))
    return "reuse"


def init_plan(config_path, repository=None, root=None, machine=None, confidential=None, terms=None):
    owner = remote.whoami()
    cfg = read_config(config_path).get("tasks", {})
    repository = repository or cfg.get("repository") or owner + "/YABook-task-" + owner
    if not _REPOSITORY.fullmatch(repository) or repository.split("/")[1] in (".", ".."):
        raise ValueError("Informe o repositório no formato proprietário/nome")
    if cfg.get("repository") and cfg["repository"] != repository:
        raise ValueError("Configuração já usa outro repositório: " + cfg["repository"])
    found = remote.info(repository)
    if found is None and repository.split("/")[0].lower() != owner.lower():
        raise ValueError("Repositório de outra conta precisa existir e estar acessível")
    if found is not None and not found["private"]:
        raise ValueError("Repositório existente não é privado")
    root = _resolve(root or cfg.get("root") or DEFAULT_ROOT)
    if cfg.get("root") and cfg["root"] != root:
        raise ValueError("Configuração já usa outra pasta local: " + cfg["root"])
    local = _local_state(root, repository)
    if local == "reuse" and found is None:
        raise ValueError("Repositório local existe, mas o remoto não foi encontrado")
    confidential = _resolve(confidential or cfg.get("confidential"))
    terms = _resolve(terms or cfg.get("terms"))
    operations = []
    if found is None:
        operations += ["create-private-repository", "scaffold", "commit", "push"]
    elif local == "absent":
        operations += ["clone-existing", "scaffold-if-empty"]
    else:
        operations += ["reuse-local", "scaffold-if-empty"]
    operations += ["set-hooks-path", "set-terms" if terms else "warn-no-terms", "write-machine-config"]
    plan = dict(owner=owner, repository=repository, existing=found is not None, local=local, root=root,
                machine=machine_name(machine or cfg.get("machine")), confidential=confidential, terms=terms,
                warnings=[w for w in (
                    None if terms else "Sem lista de termos proibidos: o pre-commit apenas avisa nesta máquina.",
                    None if not confidential or Path(confidential).is_dir() else "Base confidencial não existe nesta máquina.",
                    None if not terms or Path(terms).is_file() else "Lista de termos ainda não existe; crie o arquivo antes do primeiro commit.",
                ) if w],
                operations=operations)
    plan["approval_hash"] = digest(plan)
    return plan


def _commit_scaffold(root, message):
    created = scaffold(root)
    if not created:
        return None
    remote.git(root, "add", "-A")
    if not remote.git(root, "diff", "--cached", "--name-only").stdout.strip():
        return None
    remote.git(root, "commit", "-m", message)
    return remote.git(root, "rev-parse", "--short", "HEAD").stdout.strip()


def init_apply(plan, approval_hash, config_path):
    expected = dict(plan)
    expected.pop("approval_hash", None)
    if digest(expected) != approval_hash or plan.get("approval_hash") != approval_hash:
        raise ValueError("Plano alterado; refazer task init")
    if remote.whoami() != plan["owner"]:
        raise ValueError("Conta autenticada mudou; refazer task init")
    repository, root = plan["repository"], Path(plan["root"])
    full = read_config(config_path)
    cfg = full.get("tasks", {})
    if cfg.get("repository") and cfg["repository"] != repository:
        raise ValueError("Configuração já usa outro repositório")
    found = remote.info(repository)
    if (found is not None) != plan["existing"]:
        raise ValueError("Existência do repositório mudou; refazer task init")
    if found is not None and not found["private"]:
        raise ValueError("Repositório deixou de ser privado")
    if _local_state(root, repository) != plan["local"]:
        raise ValueError("Pasta local mudou; refazer task init")
    message = "chore: inicializa repositório do YABook Tasks"
    commit = None
    if found is None:
        remote.create(repository)
        root.mkdir(parents=True, exist_ok=True)
        remote.git(root, "init", "-b", "main")
        remote.git(root, "remote", "add", "origin", remote.url(repository))
    elif plan["local"] == "absent":
        root.parent.mkdir(parents=True, exist_ok=True)
        remote.clone(repository, root)
    remote.git(root, "config", "core.hooksPath", ".githooks")
    if plan["terms"]:
        remote.git(root, "config", "yabook.terms", plan["terms"])
    if not is_data_repo(root):
        commit = _commit_scaffold(root, message)
    elif not (root / ".githooks" / "pre-commit").exists():
        commit = _commit_scaffold(root, "chore: restaura trava de commit do YABook Tasks")
    pushed = False
    if commit:
        branch = remote.git(root, "branch", "--show-current").stdout.strip() or "main"
        remote.git(root, "push", "-u", "origin", branch)
        pushed = True
    cfg = dict(cfg, repository=repository, root=str(root), machine=plan["machine"])
    for key in ("confidential", "terms"):
        if plan[key]:
            cfg[key] = plan[key]
        else:
            cfg.pop(key, None)
    cfg.setdefault("policy", "automatic")
    full["tasks"] = cfg
    write_config(config_path, full)
    return dict(repository=repository, root=str(root), machine=plan["machine"], created=found is None,
                commit=commit, pushed=pushed, warnings=plan["warnings"])
