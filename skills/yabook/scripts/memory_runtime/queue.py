"""Fila de aprendizado: o sandbox do agente enfileira; o hook, fora dele, aplica pela mesma validação."""
import contextlib
import json
import os
import stat
from datetime import datetime, timezone
from pathlib import Path

from .core import digest


def queue_dir():
    # /tmp fixo: o TMPDIR do sandbox pode diferir do ambiente do hook.
    return Path(os.environ.get("YABOOK_QUEUE", "/tmp/yabook-queue-%d" % os.getuid()))


def _private(path):
    """Fila compartilha /tmp: só diretório/arquivo próprio, sem link e sem acesso de terceiros."""
    info = os.lstat(path)
    if stat.S_ISLNK(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError("Fila de aprendizado com dono ou permissão inválidos: " + str(path))


def enqueue(root, payload, actor, config_path, workspace):
    directory = queue_dir()
    directory.mkdir(mode=0o700, exist_ok=True)
    _private(directory)
    item = dict(memory_root=str(Path(root).resolve()), config=str(Path(config_path).expanduser().resolve()),
                workspace=str(workspace), actor=actor, payload=payload,
                queued_at=datetime.now(timezone.utc).isoformat())
    item["digest"] = digest(item)
    name = item["queued_at"].replace(":", "").replace("+", "_") + "-" + item["digest"][:12] + ".json"
    path = directory / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(item, stream, ensure_ascii=False)
    return path


@contextlib.contextmanager
def _locked(directory):
    import fcntl
    with open(directory / ".lock", "a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)


def apply_queue(config_path):
    """Aplica lotes enfileirados para a base configurada; resultado fica em results.jsonl."""
    from .core import Vault, read_json
    from .learning import learn
    directory = queue_dir()
    if not directory.is_dir():
        return []
    _private(directory)
    config_path = Path(config_path).expanduser().resolve()
    root = Path(read_json(config_path)["memory_root"]).expanduser().resolve()
    results = []
    with _locked(directory):
        for path in sorted(directory.glob("*.json")):
            outcome = dict(file=path.name)
            try:
                _private(path)
                item = json.loads(path.read_text(encoding="utf-8"))
                expected = item.pop("digest", None)
                if digest(item) != expected:
                    raise ValueError("Lote enfileirado alterado")
                # O lote só vale para a base e a configuração em uso; nunca grava em outro destino.
                if Path(item["memory_root"]) != root or Path(item["config"]) != config_path:
                    raise ValueError("Lote enfileirado para outra base/configuração")
                outcome.update(learn(Vault(root), item["payload"], item["actor"], config_path,
                                     item["workspace"], queue=False))
                outcome["topic"] = ", ".join(c["id"] for c in item["payload"].get("changes", []))[:200]
            except Exception as error:  # Falha fica registrada e é avisada no início da sessão.
                outcome.update(status="failed", error=str(error)[:300])
            with open(directory / "results.jsonl", "a", encoding="utf-8") as log:
                log.write(json.dumps(outcome, ensure_ascii=False) + "\n")
            path.unlink(missing_ok=True)
            results.append(outcome)
    return results


def pending_notices():
    """Resultados que exigem atenção (falha/revisão) desde o último aviso; consome o registro."""
    log = queue_dir() / "results.jsonl"
    if not log.is_file():
        return []
    _private(queue_dir())
    entries = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    log.unlink()
    return [e for e in entries if e.get("status") in ("failed", "pending_review")]
