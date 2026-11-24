"""Anotações, links e arquivos vinculados à revisão de uma tarefa."""
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

from .precommit_hook import find_terms

MAX_FILE = 1_000_000
MAX_NOTES = 100
MAX_ATTACHMENTS = 30
# Manter em sincronia com ATTACHMENT_ACCEPT no site.
EXTENSIONS = frozenset(".pdf .docx .xlsx .pptx .odt .ods .txt .md .csv .json .log .png .jpg .jpeg .gif .webp".split())
TEXT_EXTENSIONS = frozenset((".txt", ".md", ".csv", ".json", ".log"))
ID = re.compile(r"[0-9a-f]{64}")


def _integer(value, lower, upper):
    return type(value) is int and lower <= value <= upper


def _text(value, limit, field):
    if not isinstance(value, str) or not value.strip() or len(value) > limit or "\0" in value:
        raise ValueError(f"{field} precisa de texto entre 1 e {limit} caracteres")
    return value.strip()


def _name(value):
    name = _text(value, 160, "Nome do anexo")
    if any(ord(ch) < 32 or ch in "/\\" for ch in name) or Path(name).suffix.lower() not in EXTENSIONS:
        raise ValueError("Nome ou formato do anexo inválido")
    return name


def validate_links(links):
    if not isinstance(links, list):
        raise ValueError("Links precisam estar em uma lista")
    seen = set()
    for link in links:
        if not isinstance(link, str) or not link or any(ch.isspace() or ord(ch) < 32 or ch == "\\" for ch in link):
            raise ValueError("Informe um link HTTP ou HTTPS válido")
        try:
            url = urlsplit(link)
            valid = url.scheme in ("http", "https") and url.hostname and url.username is None and url.port != 0
        except ValueError:
            valid = False
        if not valid:
            raise ValueError("Informe um link HTTP ou HTTPS válido, sem credenciais na URL")
        if link in seen:
            raise ValueError("Link repetido")
        seen.add(link)


def validate(data):
    validate_links(data.get("links", []))
    seq = data.get("anotacoes_seq", 0)
    notes = data.get("anotacoes", [])
    if not _integer(seq, 0, 2**31 - 1) or not isinstance(notes, list) or len(notes) > MAX_NOTES:
        raise ValueError("Numeração ou lista de anotações inválida")
    seen = set()
    for note in notes:
        if not isinstance(note, dict) or set(note) != {"numero", "titulo", "texto"}:
            raise ValueError("Anotação inválida")
        number = note["numero"]
        if not _integer(number, 1, seq) or number in seen:
            raise ValueError("Número de anotação inválido ou repetido")
        _text(note["titulo"], 160, "Título da anotação")
        _text(note["texto"], 20_000, "Anotação")
        seen.add(number)
    attachments = data.get("anexos", [])
    if not isinstance(attachments, list) or len(attachments) > MAX_ATTACHMENTS:
        raise ValueError("Lista de anexos inválida ou acima do limite")
    seen.clear()
    for item in attachments:
        if not isinstance(item, dict) or set(item) != {"id", "nome", "local", "tamanho"}:
            raise ValueError("Metadados do anexo inválidos")
        key = item["id"]
        if not isinstance(key, str) or not ID.fullmatch(key) or key in seen:
            raise ValueError("Identificador de anexo inválido ou repetido")
        if type(item["local"]) is not bool or not _integer(item["tamanho"], 1, MAX_FILE):
            raise ValueError("Tamanho ou armazenamento do anexo inválido")
        _name(item["nome"])
        seen.add(key)


def blob_path(store, cfg, identifier, item):
    store.path(identifier)  # valida o identificador antes de compor qualquer caminho
    if item["local"]:
        base = cfg.get("confidential")
        if not base or not Path(base).expanduser().is_dir():
            raise ValueError("Base confidencial indisponível nesta máquina")
        root = Path(base).expanduser().resolve()
        if root == store.root or store.root in root.parents:
            raise ValueError("A base confidencial precisa ficar fora do repositório de tarefas")
    else:
        root = store.root
    path = root / "anexos-tasks" / identifier / item["id"]
    if path.resolve() != path:
        raise ValueError("Caminho de anexo incompatível com a base configurada")
    return path


def read_attachment(store, cfg, identifier, key):
    task = store.get(identifier)
    validate(task["data"])
    item = next((item for item in task["data"].get("anexos", []) if item["id"] == key), None)
    if not item:
        raise KeyError("Anexo inexistente nesta tarefa")
    try:
        with blob_path(store, cfg, task["data"]["id"], item).open("rb") as file:
            data = file.read(item["tamanho"] + 1)
    except FileNotFoundError as error:
        raise KeyError("Arquivo do anexo indisponível nesta máquina") from error
    if len(data) != item["tamanho"] or _attachment_id(item["nome"], item["local"], data) != item["id"]:
        raise ValueError("Arquivo do anexo não corresponde ao registro da tarefa")
    return item, data


def _attachment_id(name, local, data):
    prefix = json.dumps([name, local], ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(prefix + b"\0" + data).hexdigest()


def prepare(store, cfg, task, operations, uploads):
    """Valida todas as mudanças e calcula metadados, sem gravar arquivos."""
    if not isinstance(operations, list) or not isinstance(uploads, list):
        raise ValueError("Anotações e anexos precisam ser listas")
    if len(operations) > 2 * MAX_NOTES or len(uploads) > MAX_ATTACHMENTS:
        raise ValueError("Excesso de operações em anotações ou anexos")
    current = task["data"]
    validate(current)
    seq = current.get("anotacoes_seq", 0)
    notes = {note["numero"]: note for note in current.get("anotacoes", [])}
    items = {item["id"]: item for item in current.get("anexos", [])}
    fields, blobs = {}, {}
    for op in operations:
        if not isinstance(op, dict):
            raise ValueError("Operação de anotação inválida")
        action = op.get("acao")
        number = op.get("numero")
        if action == "criar" and number is None:
            seq += 1
            number = seq
        elif action not in ("editar", "excluir") or not _integer(number, 1, seq) or number not in notes:
            raise ValueError("Operação refere-se a uma anotação inexistente")
        if action == "excluir":
            del notes[number]
            continue
        title = _text(op.get("titulo"), 160, "Título da anotação")
        text = _text(op.get("texto"), 20_000, "Anotação")
        if find_terms(title + "\n" + text, store.terms):
            raise ValueError("Anotação contém termo confidencial. Use o complemento local.")
        notes[number] = dict(numero=number, titulo=title, texto=text)

    # Anexo novo (sem `acao`), `editar` (nome e/ou conteúdo, mesma extensão) ou `excluir`, por id.
    # O id é o hash de nome, armazenamento e conteúdo: editar gera id e arquivo novos e o antigo
    # entra em `blobs` com valor None, para ser removido só depois de gravar a tarefa.
    order = list(items)
    for upload in uploads:
        if not isinstance(upload, dict):
            raise ValueError("Operação de anexo inválida")
        action = upload.get("acao")
        if action is None:
            if type(upload.get("local")) is not bool:
                raise ValueError("Informe se o anexo é confidencial")
            local, name = upload["local"], _name(upload.get("nome"))
            raw = _content(store, name, local, upload.get("base64"))
            old = None
        elif action in ("editar", "excluir"):
            old = items.get(upload.get("id")) if isinstance(upload.get("id"), str) else None
            if old is None:
                raise ValueError("Operação refere-se a um anexo inexistente")
            blobs[blob_path(store, cfg, current["id"], old)] = None
            del items[old["id"]]
            if action == "excluir":
                continue
            local = old["local"]
            name = _name(upload["nome"]) if upload.get("nome") is not None else old["nome"]
            if Path(name).suffix.lower() != Path(old["nome"]).suffix.lower():
                raise ValueError("Renomeie o anexo mantendo a extensão " + Path(old["nome"]).suffix.lower())
            if upload.get("base64") is not None:
                raw = _content(store, name, local, upload["base64"])
            elif name == old["nome"]:
                raise ValueError("Informe um nome novo ou um conteúdo novo para o anexo")
            else:
                try:
                    raw = read_attachment(store, cfg, current["id"], old["id"])[1]
                except KeyError as error:
                    raise ValueError("Arquivo do anexo indisponível nesta máquina; não é possível renomear") from error
                _check(store, name, local, raw)
        else:
            raise ValueError("Ação de anexo inválida: %s" % action)
        key = _attachment_id(name, local, raw)
        if key in items:
            raise ValueError("Já existe um anexo igual nesta tarefa: " + name)
        item = dict(id=key, nome=name, local=local, tamanho=len(raw))
        path = blob_path(store, cfg, current["id"], item)
        items[key] = item
        if old is not None:
            order[order.index(old["id"])] = key  # mantém a posição do anexo editado
        else:
            order.append(key)
        blobs[path] = raw

    if operations:
        fields.update(anotacoes=list(notes.values()), anotacoes_seq=seq)
    if uploads:
        fields["anexos"] = [items[key] for key in order if key in items]
    validate(dict(current, **fields))
    return fields, blobs


def _content(store, name, local, encoded):
    if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_FILE + 2) // 3):
        raise ValueError("Cada anexo pode ter até 1 MB")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("Conteúdo do anexo inválido") from error
    _check(store, name, local, raw)
    return raw


def _check(store, name, local, raw):
    if not 1 <= len(raw) <= MAX_FILE:
        raise ValueError("O anexo deve ter entre 1 byte e 1 MB")
    if find_terms(name, store.terms):
        raise ValueError("Use um nome genérico no card para o anexo confidencial")
    if not local and Path(name).suffix.lower() in TEXT_EXTENSIONS:
        try:
            content = raw.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise ValueError("Anexo compartilhado de texto precisa estar em UTF-8") from error
        if find_terms(content, store.terms):
            raise ValueError("Anexo contém termo confidencial. Use armazenamento local.")


def write_blobs(blobs):
    """Grava os arquivos novos; os marcados com None são removidos depois, por drop_blobs."""
    from .store import atomic_write

    for path, raw in blobs.items():
        if raw is not None:
            atomic_write(path, raw)


def drop_blobs(blobs):
    """Remove arquivos substituídos ou excluídos, depois que a tarefa já aponta para os novos."""
    for path, raw in blobs.items():
        if raw is None:
            Path(path).unlink(missing_ok=True)
            try:
                Path(path).parent.rmdir()  # pasta da tarefa vazia
            except OSError:
                pass
