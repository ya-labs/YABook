"""Leitura e escrita única das tarefas, usada por comandos, hooks e servidor."""
import contextlib
import datetime
import hashlib
import os
import re
import shutil
import tempfile
import threading
from pathlib import Path

from . import fmt
from .precommit_hook import find_terms, load_terms

FORMAT = 1
TIPOS = ("demanda", "projeto", "especificacao", "issue", "tarefa", "pergunta")
PAPEIS = ("entrada", "pronto", "ativo", "validacao", "concluido", "arquivado")
NIVEIS = ("epico", "historia", "tarefa")
CHILD_LEVEL = {"epico": "historia", "historia": "tarefa"}
ORDER = ("id", "numero", "tipo", "nivel", "titulo", "coluna", "ordem", "pai", "projeto", "demanda", "issue", "pessoal",
         "prazo", "proximo_passo", "ficha", "aguardando", "aguardando_desde", "sobre", "resposta", "refs", "criada", "atualizada")
REF_PREFIXES = ("confidencial", "yabook", "github")
_ID = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")
_ISSUE = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+#\d+")
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")

DEFAULT_CONFIG = """formato: 1
rotulos:
  demanda: Demanda
  projeto: Projeto
  especificacao: Especificação
  issue: Issue
ficha:
  horas_dia: 8
  arredondamento: 1
"""

DEFAULT_QUADRO = """colunas:
  - {id: backlog, nome: Backlog, papel: entrada}
  - {id: pronto, nome: Pronto pra dev, papel: pronto}
  - {id: andamento, nome: Em andamento, papel: ativo}
  - {id: testes, nome: Testes, papel: validacao}
  - {id: concluido, nome: Concluído, papel: concluido}
  - {id: arquivado, nome: Arquivado, papel: arquivado}
"""

README = """# YABook Tasks

Repositório de dados pessoal do YABook Tasks, mantido pelos comandos `task` e
pelos hooks do plugin YABook.

Os campos versionados usam texto técnico e genérico. Dados sensíveis ficam no
complemento confidencial local e entram aqui apenas como referência.
"""

GITIGNORE = """local/
.writing-*
"""

DATA_DIRS = ("tarefas", "eventos", "propostas", "horas", "fichas")


class Conflict(ValueError):
    """A tarefa mudou depois da leitura; recarregar antes de gravar."""


def now():
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def revision(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def slug(text, limit=48):
    import unicodedata
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")[:limit].strip("-") or "tarefa"


def atomic_write(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".writing-")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def is_data_repo(root):
    root = Path(root)
    return (root / "config.yml").is_file() and (root / "quadro.yml").is_file()


def scaffold(root, hook_source=None):
    """Cria a estrutura inicial sem sobrescrever arquivos existentes."""
    root = Path(root)
    created = []
    for name, content in (("README.md", README), ("config.yml", DEFAULT_CONFIG),
                          ("quadro.yml", DEFAULT_QUADRO), (".gitignore", GITIGNORE)):
        if not (root / name).exists():
            atomic_write(root / name, content)
            created.append(name)
    for directory in DATA_DIRS:
        keep = root / directory / ".gitkeep"
        if not keep.exists():
            keep.parent.mkdir(parents=True, exist_ok=True)
            keep.write_text("", encoding="utf-8")
            created.append(directory + "/.gitkeep")
    hook = root / ".githooks" / "pre-commit"
    if not hook.exists():
        hook.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(hook_source or Path(__file__).with_name("precommit_hook.py"), hook)
        created.append(".githooks/pre-commit")
    hook.chmod(0o755)
    return created


def infer_level(data, index):
    """Sem `nivel` explícito, o filho assume o nível abaixo do pai."""
    if data.get("pai") and not data.get("nivel"):
        parent = index.get(data["pai"]) or {}
        if parent.get("nivel") in CHILD_LEVEL:
            data["nivel"] = CHILD_LEVEL[parent["nivel"]]
    return data


def check_tree(index, ids=None):
    """Valida nível e pai dos nós `ids` (todos por padrão) contra o índice id -> dados.

    Épico não tem pai, história fica sob épico e tarefa sob história; como o
    nível desce a cada passo, não há ciclo possível.
    """
    for identifier in (list(index) if ids is None else ids):
        data = index[identifier]
        nivel, pai = data.get("nivel"), data.get("pai")
        if data.get("tipo") == "pergunta" and (nivel or pai):
            raise ValueError("Pergunta não tem nível nem pai; use `sobre`: " + identifier)
        if nivel is not None and nivel not in NIVEIS:
            raise ValueError("Nível inválido em %s: %r; use %s" % (identifier, nivel, ", ".join(NIVEIS)))
        if not pai:
            continue
        if pai == identifier:
            raise ValueError("Tarefa não pode ser pai de si mesma: " + identifier)
        if nivel == "epico":
            raise ValueError("Épico não tem pai: " + identifier)
        parent = index.get(pai)
        if parent is None:
            raise ValueError("Pai inexistente em %s: %s" % (identifier, pai))
        expected = CHILD_LEVEL.get(parent.get("nivel"))
        if expected is None:
            raise ValueError("Pai de %s precisa ser épico ou história: %s" % (identifier, pai))
        if nivel != expected:
            raise ValueError("%s precisa ter nível %s sob %s (%s)" % (identifier, expected, pai, parent.get("nivel")))


def validate_quadro(quadro):
    columns = quadro.get("colunas") if isinstance(quadro, dict) else None
    if not isinstance(columns, list) or not columns:
        raise ValueError("quadro.yml precisa de `colunas`")
    seen = set()
    for column in columns:
        if not isinstance(column, dict) or not all(isinstance(column.get(k), str) and column[k] for k in ("id", "nome", "papel")):
            raise ValueError("Coluna precisa de id, nome e papel")
        if not _ID.fullmatch(column["id"]) or column["id"] in seen:
            raise ValueError("Id de coluna inválido ou repetido: " + column["id"])
        if column["papel"] not in PAPEIS:
            raise ValueError("Papel inválido: " + column["papel"])
        seen.add(column["id"])
    return columns


class TaskStore:
    def __init__(self, root, terms=None):
        self.root = Path(root).expanduser().resolve()
        if not is_data_repo(self.root):
            raise ValueError("Repositório de dados do YABook Tasks não encontrado em " + str(self.root))
        self.terms = load_terms(terms) if isinstance(terms, (str, Path)) else terms
        self._mutex = threading.RLock()
        self._depth = 0

    # Configuração -------------------------------------------------------
    def config(self):
        data = fmt.loads((self.root / "config.yml").read_text(encoding="utf-8"))
        if data.get("formato") != FORMAT:
            raise ValueError("Formato do repositório de dados não suportado: %r" % data.get("formato"))
        return data

    def columns(self):
        return validate_quadro(fmt.loads((self.root / "quadro.yml").read_text(encoding="utf-8")))

    def column_ids(self, papel=None):
        return [c["id"] for c in self.columns() if papel is None or c["papel"] == papel]

    # Concorrência ------------------------------------------------------
    @contextlib.contextmanager
    def lock(self):
        with self._mutex:
            if self._depth:
                self._depth += 1
                try:
                    yield
                finally:
                    self._depth -= 1
                return
            local = self.root / "local"
            local.mkdir(exist_ok=True)
            with (local / "lock").open("a+") as stream:
                _lock_file(stream)
                self._depth = 1
                try:
                    yield
                finally:
                    self._depth = 0
                    _unlock_file(stream)

    # Tarefas -----------------------------------------------------------
    def resolve(self, identifier):
        """`@n` vira o id da tarefa de número n; ids seguem como estão."""
        if isinstance(identifier, str) and identifier.startswith("@") and identifier[1:].isdigit():
            number = int(identifier[1:])
            found = next((t["data"]["id"] for t in self.list() if t["data"].get("numero") == number), None)
            if found is None:
                raise KeyError("Tarefa inexistente: " + identifier)
            return found
        return identifier

    def next_number(self):
        return max((t["data"].get("numero") or 0 for t in self.list()), default=0) + 1

    def number_all(self, fix_duplicates=False):
        """Numera as tarefas sem número pela ordem de criação; com `fix_duplicates`, renumera as repetidas
        (a mais antiga mantém o número)."""
        with self.lock():
            tasks = sorted(self.list(), key=lambda t: (t["data"].get("criada") or "", t["data"]["id"]))
            top = max((t["data"].get("numero") or 0 for t in tasks), default=0)
            seen, changed = set(), []
            for task in tasks:
                number = task["data"].get("numero")
                if number and (number not in seen or not fix_duplicates):
                    seen.add(number)
                    continue
                top += 1
                self.save(dict(task["data"], numero=top), task["body"], task["revision"])
                changed.append(dict(id=task["data"]["id"], numero=top))
            return changed

    def duplicate_numbers(self):
        counts = {}
        for task in self.list():
            number = task["data"].get("numero")
            if number:
                counts.setdefault(number, []).append(task["data"]["id"])
        return {n: ids for n, ids in counts.items() if len(ids) > 1}

    def path(self, identifier):
        identifier = self.resolve(identifier)
        if not isinstance(identifier, str) or not _ID.fullmatch(identifier):
            raise ValueError("Id de tarefa inválido: %r" % (identifier,))
        return self.root / "tarefas" / (identifier + ".md")

    def get(self, identifier):
        path = self.path(identifier)
        if not path.is_file():
            raise KeyError("Tarefa inexistente: " + identifier)
        text = path.read_text(encoding="utf-8")
        data, body = fmt.split_frontmatter(text)
        return dict(data=data, body=body, revision=revision(text))

    def list(self):
        tasks = []
        for path in sorted((self.root / "tarefas").glob("*.md")):
            text = path.read_text(encoding="utf-8")
            data, body = fmt.split_frontmatter(text)
            tasks.append(dict(data=data, body=body, revision=revision(text)))
        return tasks

    def exists(self, identifier):
        return self.path(identifier).is_file()

    def new_id(self, tipo, code=None, title=None):
        if tipo not in TIPOS:
            raise ValueError("Tipo inválido: " + str(tipo))
        if code is not None and tipo in ("demanda", "projeto", "especificacao"):
            base = tipo + "-" + slug(str(code), 32)
        elif tipo == "pergunta":
            base = "pergunta-" + datetime.datetime.now().strftime("%Y%m%d-%H%M")
        else:
            base = tipo + "-" + slug(title or tipo)
        candidate, counter = base, 2
        while self.exists(candidate):
            candidate, counter = "%s-%d" % (base, counter), counter + 1
        return candidate

    def normalize(self, data):
        data = {k: v for k, v in data.items() if v is not None and v != [] and v != ""}
        for key in ("projeto", "demanda"):
            if isinstance(data.get(key), int):
                data[key] = str(data[key])
        for key in ("issue", "refs"):
            if isinstance(data.get(key), str):
                data[key] = [data[key]]
        return data

    def validate(self, data):
        if not isinstance(data.get("id"), str):
            raise ValueError("Tarefa sem id")
        self.path(data["id"])
        if data.get("tipo") not in TIPOS:
            raise ValueError("Tipo inválido: %r" % (data.get("tipo"),))
        if not isinstance(data.get("titulo"), str) or not data["titulo"].strip():
            raise ValueError("Tarefa sem título")
        if data.get("coluna") not in self.column_ids():
            raise ValueError("Coluna inexistente no quadro: %r" % (data.get("coluna"),))
        if "numero" in data and (not isinstance(data["numero"], int) or data["numero"] < 1):
            raise ValueError("`numero` precisa ser inteiro positivo")
        if "ordem" in data and not isinstance(data["ordem"], int):
            raise ValueError("`ordem` precisa ser inteiro")
        if "pessoal" in data and not isinstance(data["pessoal"], bool):
            raise ValueError("`pessoal` precisa ser true ou false")
        if "nivel" in data and data["nivel"] not in NIVEIS:
            raise ValueError("Nível inválido: %r; use %s" % (data["nivel"], ", ".join(NIVEIS)))
        for key in ("projeto", "demanda", "pai", "proximo_passo", "ficha", "aguardando", "sobre", "resposta", "criada", "atualizada"):
            if key in data and not isinstance(data[key], str):
                raise ValueError("`%s` precisa ser texto" % key)
        for key in ("prazo", "aguardando_desde"):
            if key in data:
                if not isinstance(data[key], str) or not _DATE.fullmatch(data[key]):
                    raise ValueError("`%s` precisa estar em AAAA-MM-DD" % key)
                datetime.date.fromisoformat(data[key])
        for item in data.get("issue", []):
            if not isinstance(item, str) or not _ISSUE.fullmatch(item):
                raise ValueError("Issue inválida, use dono/repositório#numero: %r" % (item,))
        for item in data.get("refs", []):
            if not isinstance(item, str) or item.split(":", 1)[0] not in REF_PREFIXES or ":" not in item:
                raise ValueError("Referência inválida, use %s:<alvo>: %r" % ("|".join(REF_PREFIXES), item))
        if "sobre" in data:
            self.path(data["sobre"])

    def render(self, data, body=""):
        return fmt.join_frontmatter(data, body, ORDER)

    def save(self, data, body="", expected_revision=None):
        """Grava a tarefa. Sem `expected_revision`, a tarefa precisa ser nova."""
        data = self.normalize(dict(data))
        with self.lock():
            path = self.path(data.get("id"))
            current = path.read_text(encoding="utf-8") if path.exists() else None
            if current is None and expected_revision is not None:
                raise Conflict("Tarefa removida depois da leitura: " + data["id"])
            if current is not None and expected_revision is None:
                raise Conflict("Tarefa já existe: " + data["id"])
            if current is not None and revision(current) != expected_revision:
                raise Conflict("Tarefa mudou depois da leitura; recarregue antes de gravar: " + data["id"])
            stamp = now()
            if current is None:
                data.setdefault("criada", stamp)
                data.setdefault("numero", self.next_number())
            else:
                data["criada"] = fmt.split_frontmatter(current)[0].get("criada", data.get("criada", stamp))
            data["atualizada"] = stamp
            previous = fmt.split_frontmatter(current)[0] if current else {}
            # Espera: a data nasce quando o texto aparece ou muda e some junto com ele.
            if not data.get("aguardando"):
                data.pop("aguardando", None)
                data.pop("aguardando_desde", None)
            elif data["aguardando"] != previous.get("aguardando") or not data.get("aguardando_desde"):
                data["aguardando_desde"] = stamp[:10]
            if data.get("pai") or data.get("nivel") or previous.get("nivel"):
                index = {t["data"]["id"]: t["data"] for t in self.list()}
                index[data["id"]] = data
                infer_level(data, index)
                check_tree(index, [data["id"]] + [i for i, d in index.items() if d.get("pai") == data["id"]])
            self.validate(data)
            text = self.render(data, body)
            hits = find_terms(text, self.terms)
            if hits:
                raise ValueError("Texto com termo confidencial (%s); mova para o complemento confidencial"
                                 % ", ".join(hits))
            atomic_write(path, text)
            return revision(text)


def _lock_file(stream):
    try:
        import fcntl
        fcntl.flock(stream, fcntl.LOCK_EX)
    except ImportError:  # Windows
        import msvcrt
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_LOCK, 1)


def _unlock_file(stream):
    try:
        import fcntl
        fcntl.flock(stream, fcntl.LOCK_UN)
    except ImportError:
        import msvcrt
        stream.seek(0)
        msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
