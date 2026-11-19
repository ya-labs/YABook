"""Anotações numeradas e arquivos vinculados à revisão de uma tarefa."""
import base64
import binascii
import hashlib
import json
import re
from pathlib import Path

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


def validate(data):
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

    for upload in uploads:
        if not isinstance(upload, dict) or type(upload.get("local")) is not bool:
            raise ValueError("Informe se o anexo é confidencial")
        local = upload["local"]
        name = _name(upload.get("nome"))
        encoded = upload.get("base64")
        if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_FILE + 2) // 3):
            raise ValueError("Cada anexo pode ter até 1 MB")
        try:
            raw = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error) as error:
            raise ValueError("Conteúdo do anexo inválido") from error
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
        key = _attachment_id(name, local, raw)
        item = dict(id=key, nome=name, local=local, tamanho=len(raw))
        path = blob_path(store, cfg, current["id"], item)
        items[key] = item
        blobs[path] = raw

    if operations:
        fields.update(anotacoes=list(notes.values()), anotacoes_seq=seq)
    if uploads:
        fields["anexos"] = list(items.values())
    validate(dict(current, **fields))
    return fields, blobs


def write_blobs(blobs):
    from .store import atomic_write

    for path, raw in blobs.items():
        atomic_write(path, raw)
