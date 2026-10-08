"""Adaptador Claude Code: marketplace local gerenciado e comandos oficiais `claude plugin`."""
import glob
import json
import shutil
import subprocess
from pathlib import Path

from memory_runtime.core import read_json, write_json
from plugin_sync import compare, validate_package

MARKETPLACE = "yabook-local"
SELECTOR = "yabook@" + MARKETPLACE


def marketplace_root(home):
    return Path(home).expanduser().resolve() / ".local/share/yabook/claude-marketplace"


def owns_destination(installed, home):
    return Path(installed).expanduser().resolve() == marketplace_root(home) / "plugins/yabook"


def find_claude():
    """Executável no PATH ou o binário da extensão do VS Code (versão mais recente)."""
    found = shutil.which("claude")
    if found:
        return found
    candidates = sorted(glob.glob(str(Path.home() / ".vscode/extensions/anthropic.claude-code-*/resources/native-binary/claude")))
    return candidates[-1] if candidates else None


def run_claude(arguments):
    binary = find_claude()
    if not binary:
        raise FileNotFoundError("Claude Code não encontrado")
    result = subprocess.run([binary, "plugin", *arguments], capture_output=True, text=True, timeout=120,
                            stdin=subprocess.DEVNULL)
    if result.returncode:
        raise ValueError("claude plugin " + " ".join(arguments[:2]) + " falhou: " + (result.stderr or result.stdout)[-300:])
    return result.stdout


def write_marketplace(root):
    manifest = root / ".claude-plugin/marketplace.json"
    if manifest.exists():
        data = read_json(manifest)
        if data.get("name") != MARKETPLACE:
            raise ValueError("Marketplace local pertence a outro instalador")
        return False
    write_json(manifest, {"name": MARKETPLACE, "owner": {"name": "YA LABS"},
                          "description": "Marketplace local do plugin YABook (Método YA LABS e memória própria).",
                          "plugins": [{"name": "yabook", "source": "./plugins/yabook",
                                       "description": "Método YA LABS e memória própria rastreável para agentes de desenvolvimento."}]})
    return True


def adopt(installed):
    """Instalação feita antes do adaptador: só adota se for pacote YABook válido sem arquivos alheios."""
    from host_directory import MARKER
    if not installed.exists() or (installed / MARKER).exists():
        return False
    validate_package(installed, previous=True)
    write_json(installed / MARKER, dict(manager="yabook-directory-v1"))
    return True


def sync_claude(source, installed, home, apply=False, runner=run_claude):
    from host_directory import sync_directory
    root = marketplace_root(home)
    installed = Path(installed).expanduser().resolve()
    if installed != root / "plugins/yabook":
        raise ValueError("Destino não corresponde ao marketplace local YABook do Claude")
    if not apply:
        if not installed.exists():
            return dict(status="not_installed", adapter="claude", path=str(installed))
        return dict(compare(source, installed), adapter="claude")
    created = write_marketplace(root)
    adopted = adopt(installed)
    fresh = not installed.exists()
    report = sync_directory(source, installed, apply=True)
    report.update(adapter="claude", adopted=adopted)
    # Registro no Claude Code pelos comandos oficiais; sem o executável, vale na próxima sessão.
    try:
        if created or fresh:
            runner(["marketplace", "add", str(root)])
            runner(["install", SELECTOR, "--scope", "user"])
            report["registration"] = "installed"
        elif report["status"] != "synchronized":
            runner(["marketplace", "update", MARKETPLACE])
            runner(["update", SELECTOR, "--scope", "user"])
            report["registration"] = "updated"
    except FileNotFoundError:
        report["registration"] = "pending: Claude Code não encontrado; o pacote vale em nova sessão"
    report["restart_required"] = report["status"] != "synchronized"
    return report
