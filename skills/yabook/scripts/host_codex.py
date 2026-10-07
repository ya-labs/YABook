"""Adaptador Codex: comandos e caminhos específicos isolados do núcleo portátil."""
import json
import os
import subprocess
from pathlib import Path
from memory_runtime.core import read_json, write_json
from plugin_sync import compare, validate_package

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
        version = json.loads((source / ".codex-plugin/plugin.json").read_text())["version"]
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

def register_codex(home, remove=False, source=None):
    from yabook_plugin import build, fingerprint
    home = Path(home).expanduser().resolve()
    registry = home / ".agents/plugins/marketplace.json"
    data = read_json(registry) if registry.exists() else dict(name="yabook-local",interface=dict(displayName="YABook local"),plugins=[])
    if not isinstance(data.get("plugins"), list) or not isinstance(data.get("name"), str):
        raise ValueError("Marketplace existente tem formato incompatível")
    existing = next((p for p in data["plugins"] if p.get("name") == "yabook"), None)
    if existing and not (existing.get("source", {}).get("source") == "local" and
                         existing["source"].get("path", "").startswith("./.local/share/yabook/plugins/")):
        raise ValueError("Entrada yabook existente não pertence a este instalador")
    if remove:
        if existing:
            data["plugins"].remove(existing); write_json(registry, data)
        return dict(status="unregistered",preserved="pacotes, configuração do host e memória")
    root = Path(source).resolve() if source else Path(__file__).resolve().parents[3]
    relative = ".local/share/yabook/plugins/" + fingerprint(root)
    destination = home / relative
    if destination.exists():
        if fingerprint(destination) != fingerprint(root): raise ValueError("Pacote instalado foi alterado")
    else: build(destination, source=root)
    entry = dict(name="yabook",source=dict(source="local",path="./"+relative),
                 policy=dict(installation="AVAILABLE",authentication="ON_INSTALL"),category="Productivity")
    if existing: data["plugins"][data["plugins"].index(existing)] = entry
    else: data["plugins"].append(entry)
    write_json(registry, data)
    return dict(status="registered",path=str(destination),marketplace=data["name"],
                enable=f'[plugins."yabook@{data["name"]}"]\nenabled = true')



def owns_destination(installed, home):
    cache = Path(os.environ.get("CODEX_HOME", str(Path(home).expanduser() / ".codex"))) / "plugins/cache"
    return cache.resolve() in Path(installed).expanduser().resolve().parents
