"""Comparação do pacote e atualização pelo host, com recuperação da instalação."""
import json
import re
from pathlib import Path

# Manifesto legado do Codex: o formato Agent Plugins (plugin.json na raiz com $schema)
# faz o carregador atual ignorar hooks de plugin (openai/codex#47925).
MANIFEST = ".codex-plugin/plugin.json"
ROOTS = (".codex-plugin", "assets", "hooks", ".claude-plugin", "skills/yabook")
PREVIOUS_MANIFEST = "plugin.json"  # Agent Plugins, aceito só para recuperar pacote anterior


def package_files(root):
    root = Path(root).resolve()
    files = {}
    for item in ROOTS + (PREVIOUS_MANIFEST,):
        base = root / item
        if base.is_symlink():
            raise ValueError(f"Link simbólico não permitido no pacote: {item}")
        if item == PREVIOUS_MANIFEST and not base.is_file():
            continue
        paths = [base] if base.is_file() else base.rglob("*")
        for path in paths:
            relative = path.relative_to(root)
            if "__pycache__" in relative.parts or "tests" in relative.parts or path.suffix == ".pyc":
                continue
            if path.is_symlink():
                raise ValueError(f"Link simbólico não permitido no pacote: {relative}")
            if path.is_file():
                files[relative.as_posix()] = path.read_bytes()
    return files


def validate_package(root, previous=False):
    """previous aceita o formato anterior apenas para validar recuperação."""
    files = package_files(root)
    if PREVIOUS_MANIFEST in files and not previous:
        raise ValueError("plugin.json na raiz ativa o formato Agent Plugins, que ignora hooks no Codex")
    legacy = PREVIOUS_MANIFEST in files
    for name in (PREVIOUS_MANIFEST if legacy else MANIFEST, ".claude-plugin/plugin.json", "hooks/hooks.json",
                 "skills/yabook/SKILL.md", "skills/yabook/scripts/yabook_hook.py"):
        if name not in files:
            raise ValueError(f"Origem não é um plugin YABook completo: falta {name}")
    manifest = json.loads(files[PREVIOUS_MANIFEST if legacy else MANIFEST])
    if manifest.get("name") != "yabook" or not manifest.get("version"):
        raise ValueError("Identidade ou versão incompatível")
    if not isinstance(manifest["version"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]*", manifest["version"]):
        raise ValueError("Versão incompatível com o caminho do cache")
    claude = json.loads(files[".claude-plugin/plugin.json"])
    if (claude.get("name"), claude.get("version")) != ("yabook", manifest["version"]):
        raise ValueError("Manifestos divergentes")
    hooks = json.loads(files["hooks/hooks.json"])
    if not isinstance(hooks.get("hooks"), dict):
        raise ValueError("Hooks inválidos")
    declared = manifest.get("extensions", {}).get("com.openai", {}) if legacy else manifest
    if not legacy and (manifest.get("skills") != "./skills/" or not manifest.get("hooks")):
        raise ValueError("Manifesto Codex precisa declarar skills e hooks")
    references = [declared.get("hooks")]
    references += list(declared.get("interface", {}).get(key) for key in ("logo", "composerIcon"))
    for reference in references:
        if reference and reference.removeprefix("./") not in files:
            raise ValueError(f"Arquivo referenciado ausente: {reference}")
    skill = files["skills/yabook/SKILL.md"].decode("utf-8")
    if not skill.startswith("---\n") or "name: yabook" not in skill.split("---", 2)[1]:
        raise ValueError("Skill inválida")
    return files


def compare(source, installed, previous=False):
    wanted = validate_package(source, previous)
    # plugin.json remanescente na instalação desativa os hooks; aparece como excedente.
    actual = package_files(installed)
    return dict(status="outdated" if wanted != actual else "synchronized",
                changed=sorted(k for k in wanted.keys() & actual.keys() if wanted[k] != actual[k]),
                missing=sorted(wanted.keys() - actual.keys()), extra=sorted(actual.keys() - wanted.keys()))



def sync_codex(*args, **kwargs):
    """Compatibilidade com consumidores do adaptador anterior."""
    from host_codex import sync_codex as apply
    return apply(*args, **kwargs)


def sync_plugin(source, installed, home, apply=False, adapter="auto"):
    installed = Path(installed).expanduser().resolve()
    if adapter == "auto":
        from host_codex import owns_destination
        adapter = "codex" if owns_destination(installed, home) else "directory"
    if adapter == "codex":
        return sync_codex(source, installed, home, apply=apply)
    if adapter == "directory":
        from host_directory import sync_directory
        return sync_directory(source, installed, apply=apply)
    raise ValueError("Adaptador desconhecido")
