"""Instalação portátil em diretório próprio do YABook, sem assumir o host."""
import shutil
import tempfile
from pathlib import Path

from memory_runtime.core import read_json, write_json
from plugin_sync import compare, validate_package

MARKER = ".yabook-install.json"


def sync_directory(source, installed, apply=False):
    source, installed = (Path(p).expanduser().resolve() for p in (source, installed))
    if source == installed or source in installed.parents or installed in source.parents:
        raise ValueError("Origem e instalação precisam ser diretórios independentes")
    marker = installed / MARKER
    if installed.exists():
        if not marker.is_file() or read_json(marker).get("manager") != "yabook-directory-v1":
            raise ValueError("Destino não gerenciado pelo YABook; preserve a instalação do host")
        extras = set(p.name for p in installed.iterdir()) - {
            "plugin.json", "assets", "hooks", ".claude-plugin", "skills", MARKER}
        if extras or set(p.name for p in (installed / "skills").iterdir()) - {"yabook"}:
            raise ValueError("Destino contém arquivos independentes; não substituir")
    report = compare(source, installed)
    if not apply or report["status"] == "synchronized":
        return report
    from yabook_plugin import build
    installed.parent.mkdir(parents=True, exist_ok=True)
    # Mesmo filesystem para renomeação e recuperação; não use /tmp aqui.
    staging = Path(tempfile.mkdtemp(prefix=".yabook-sync-", dir=installed.parent))
    candidate, backup = staging / "candidate", staging / "previous"
    moved = False
    replaced = False
    try:
        build(candidate, source=source)
        if compare(source, candidate)["status"] != "synchronized":
            raise ValueError("Origem mudou durante a preparação")
        write_json(candidate / MARKER, dict(manager="yabook-directory-v1"))
        if installed.exists():
            installed.rename(backup)
            moved = True
        candidate.rename(installed)
        replaced = True
        validate_package(installed)
        if compare(source, installed)["status"] != "synchronized":
            raise ValueError("Instalação divergente")
    except Exception:
        if moved:
            if installed.exists(): shutil.rmtree(installed)
            backup.rename(installed)
        elif replaced and installed.exists():
            shutil.rmtree(installed)
        raise
    finally:
        # Se a recuperação falhar, preserve o backup para recuperação manual.
        if not backup.exists(): shutil.rmtree(staging)
    return dict(status="updated", path=str(installed), adapter="directory",
                previous=str(backup) if moved else None, restart_required=True)
