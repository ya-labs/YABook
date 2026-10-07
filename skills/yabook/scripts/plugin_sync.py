"""Comparação do pacote e atualização pelo host, com recuperação da instalação."""
import json
import os
import re
import subprocess
from pathlib import Path

from memory_runtime.core import read_json, write_json

ROOTS = ("plugin.json", "assets", "hooks", ".claude-plugin", "skills/yabook")


def package_files(root):
    root = Path(root).resolve()
    files = {}
    for item in ROOTS:
        base = root / item
        if base.is_symlink():
            raise ValueError(f"Link simbólico não permitido no pacote: {item}")
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


def validate_package(root):
    files = package_files(root)
    for name in ("plugin.json", ".claude-plugin/plugin.json", "hooks/hooks.json",
                 "skills/yabook/SKILL.md", "skills/yabook/scripts/yabook_hook.py"):
        if name not in files:
            raise ValueError(f"Origem não é um plugin YABook completo: falta {name}")
    manifest = json.loads(files["plugin.json"])
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
    extension = manifest.get("extensions", {}).get("com.openai", {})
    references = [extension.get("hooks")]
    references += list(extension.get("interface", {}).get(key) for key in ("logo", "composerIcon"))
    for reference in references:
        if reference and reference.removeprefix("./") not in files:
            raise ValueError(f"Arquivo referenciado ausente: {reference}")
    skill = files["skills/yabook/SKILL.md"].decode("utf-8")
    if not skill.startswith("---\n") or "name: yabook" not in skill.split("---", 2)[1]:
        raise ValueError("Skill inválida")
    return files


def compare(source, installed):
    wanted = validate_package(source)
    actual = package_files(installed)
    return dict(status="outdated" if wanted != actual else "synchronized",
                changed=sorted(k for k in wanted.keys() & actual.keys() if wanted[k] != actual[k]),
                missing=sorted(wanted.keys() - actual.keys()), extra=sorted(actual.keys() - wanted.keys()))


def run_host(arguments):
    subprocess.run(["rtk", "proxy", "codex", "plugin", *arguments, "--json"], check=True,
                   capture_output=True, text=True)


def sync_codex(source, installed, home, apply=False, runner=run_host):
    source, installed, home = map(lambda p: Path(p).expanduser().resolve(), (source, installed, home))
    report = compare(source, installed)
    if not apply or report["status"] == "synchronized":
        return report
    # O CLI usa a casa real. --home é útil para comparação/testes, não para redirecioná-lo.
    if runner is run_host and home != Path.home().resolve():
        raise ValueError("Atualização real exige a casa atual do host")
    registry = home / ".agents/plugins/marketplace.json"
    previous = read_json(registry) if registry.exists() else None
    marketplace = (previous or {}).get("name", "yabook-local")
    was_installed = installed.exists()
    target = installed
    if runner is run_host:
        cache = Path(os.environ.get("CODEX_HOME", str(home / ".codex"))) / "plugins/cache"
        version = json.loads((source / "plugin.json").read_text())["version"]
        listing = subprocess.run(["rtk", "proxy", "codex", "plugin", "list", "--json"], check=True,
                                 capture_output=True, text=True)
        entries = json.loads(listing.stdout).get("installed", [])
        entry = next((p for p in entries if p.get("pluginId") == "yabook@" + marketplace), None)
        if entry and not entry.get("enabled"):
            raise ValueError("Plugin desativado: atualização preserva esse estado e exige habilitação prévia")
        current_version = entry["version"] if entry else version
        if installed != (cache / marketplace / "yabook" / current_version).resolve():
            raise ValueError("Destino não corresponde ao cache YABook do Codex")
        target = (cache / marketplace / "yabook" / version).resolve()
    old_entry = next((p for p in (previous or {}).get("plugins", []) if p.get("name") == "yabook"), None)
    old_root = home / old_entry["source"]["path"] if old_entry and old_entry.get("source", {}).get("source") == "local" else None
    if installed.exists() and (old_root is None or not old_root.exists()):
        raise ValueError("Instalação existente sem origem local recuperável; não foi alterada")
    if old_root:
        validate_package(old_root)
    from yabook_plugin import register_codex, fingerprint
    expected = fingerprint(source)
    registration = register_codex(home, source=source)
    candidate = Path(registration["path"])
    try:
        validate_package(candidate)
        if fingerprint(candidate) != expected or fingerprint(source) != expected:
            raise ValueError("Origem mudou durante a preparação; instalação preservada")
    except Exception:
        restore_registry(registry, previous, old_entry)
        raise
    selector = "yabook@" + registration["marketplace"]
    touched = False
    try:
        if was_installed:
            touched = True
            runner(["remove", selector])
        touched = True
        runner(["add", selector])
        final = compare(candidate, target)
        if final["status"] != "synchronized":
            raise ValueError("Host não instalou o pacote esperado")
    except Exception as error:
        restore_registry(registry, previous, old_entry)
        if touched and old_entry and was_installed:
            try:
                if target.exists() or installed.exists():
                    runner(["remove", selector])
                runner(["add", selector])
                if compare(old_root, installed)["status"] != "synchronized":
                    raise ValueError("Pacote anterior não foi recuperado")
            except Exception as rollback_error:
                raise RuntimeError("Atualização falhou e recuperação pelo host falhou; origem anterior preservada") from rollback_error
        raise RuntimeError("Atualização falhou; origem anterior restaurada" if old_entry else
                           "Instalação falhou; registro anterior restaurado") from error
    return dict(status="updated", package=str(candidate), fingerprint=expected,
                restart_required=True, comparison=final)


def restore_registry(registry, previous, old_entry):
    current = read_json(registry)
    current["plugins"] = [p for p in current["plugins"] if p.get("name") != "yabook"]
    if old_entry:
        current["plugins"].append(old_entry)
    if previous is None and not current["plugins"]:
        registry.unlink()
    else:
        write_json(registry, current)
