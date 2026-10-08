"""Diagnóstico do sandbox do Codex para gravar a memória; sugere, nunca altera a configuração."""
import errno
import os
import re
from pathlib import Path

READ_ONLY = (errno.EROFS, errno.EACCES, errno.EPERM)


def codex_config_path():
    return Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))) / "config.toml"


def read_codex_sandbox(path=None):
    """Leitura mínima: Python 3.10 não tem tomllib e só duas chaves interessam."""
    path = Path(path) if path else codex_config_path()
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    top = text.split("\n[", 1)[0]
    section = re.search(r"^\[sandbox_workspace_write\]\s*$(.*?)(?=^\[|\Z)", text, re.M | re.S)
    roots = None
    if section:
        match = re.search(r"^\s*writable_roots\s*=\s*\[(.*?)\]", section.group(1), re.M | re.S)
        if match:
            roots = re.findall(r"""["']([^"']+)["']""", match.group(1))
    return dict(default_permissions=bool(re.search(r"^\s*default_permissions\s*=", top, re.M)),
                writable_roots=roots or [])


def hint(root, settings=None):
    root = str(Path(root).expanduser().resolve())
    settings = settings if settings is not None else read_codex_sandbox() or {}
    if settings.get("default_permissions"):
        change = ("Declare " + root + " como raiz gravável no perfil de `default_permissions` em "
                  + str(codex_config_path()) + " (perfis não usam sandbox_workspace_write).")
    else:
        change = '[sandbox_workspace_write]\nwritable_roots = ["' + root + '"]'
    return dict(reason="O sandbox do agente monta a memória como somente leitura; a base não foi alterada.",
                config=str(codex_config_path()), suggestion=change,
                note="Sugira à pessoa; não edite config.toml sem autorização. .git e rede seguem protegidos: hooks publicam.")


def codex_blocks(root, settings=None):
    """Retorna a sugestão quando a configuração do Codex não libera a memória."""
    settings = settings if settings is not None else read_codex_sandbox()
    if settings is None:
        return None
    root = Path(root).expanduser().resolve()
    for entry in settings.get("writable_roots", []):
        allowed = Path(entry).expanduser().resolve()
        if root == allowed or allowed in root.parents:
            return None
    return hint(root, settings)


def is_read_only(error):
    return isinstance(error, OSError) and error.errno in READ_ONLY
