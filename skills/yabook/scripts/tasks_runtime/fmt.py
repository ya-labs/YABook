"""Subconjunto de YAML usado pelo YABook Tasks, sem dependências externas.

Aceita mapas por indentação, listas em bloco (`- item`), coleções em linha
(`[a, b]`, `{k: v}`), escalares com ou sem aspas e comentários `#`. É o
suficiente para frontmatter, `config.yml` e `quadro.yml`, legíveis também pelo
Obsidian. Recursos fora disso (âncoras, blocos multilinha) são recusados.
"""
import re

_INT = re.compile(r"-?\d+")
_PLAIN_UNSAFE = re.compile(r"^[\s\-?:#&*!|>'\"%@`]|[,\[\]{}]|:\s|\s#|:$|\s$")


class FormatError(ValueError):
    pass


def _strip_comment(line):
    quote = None
    for index, char in enumerate(line):
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == "#" and (index == 0 or line[index - 1] in " \t"):
            return line[:index].rstrip()
    return line.rstrip()


def _split_top(text):
    parts, depth, quote, current = [], 0, None, ""
    for char in text:
        if quote:
            current += char
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
        elif char in "[{":
            depth += 1
        elif char in "]}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(current.strip())
            current = ""
            continue
        current += char
    if quote or depth:
        raise FormatError("Coleção em linha malformada: " + text)
    if current.strip():
        parts.append(current.strip())
    return parts


def _key_value(text):
    quote = None
    for index, char in enumerate(text):
        if quote:
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
        elif char == ":" and (index + 1 == len(text) or text[index + 1] == " "):
            return text[:index].strip(), text[index + 1:].strip()
    return None


def scalar(text):
    text = text.strip()
    if not text:
        return None
    if text[0] == "[":
        if text[-1] != "]":
            raise FormatError("Lista em linha sem fechamento: " + text)
        return [scalar(part) for part in _split_top(text[1:-1])]
    if text[0] == "{":
        if text[-1] != "}":
            raise FormatError("Mapa em linha sem fechamento: " + text)
        result = {}
        for part in _split_top(text[1:-1]):
            pair = _key_value(part)
            if not pair:
                raise FormatError("Par inválido em mapa: " + part)
            result[_unquote(pair[0])] = scalar(pair[1])
        return result
    if text[0] in "\"'":
        return _unquote(text)
    if text in ("null", "~"):
        return None
    if text in ("true", "false"):
        return text == "true"
    if _INT.fullmatch(text):
        return int(text)
    if text[0] in "&*!|>":
        raise FormatError("Recurso de YAML não suportado: " + text)
    return text


def _unquote(text):
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return text[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    if len(text) >= 2 and text[0] == text[-1] == "'":
        return text[1:-1].replace("''", "'")
    if text[:1] in "\"'":
        raise FormatError("Aspas sem fechamento: " + text)
    return text


def loads(text):
    lines = []
    for number, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise FormatError("Tabulação na indentação, linha %d" % number)
        line = _strip_comment(raw)
        if line.strip():
            lines.append((len(line) - len(line.lstrip()), line.strip(), number))
    value, index = _block(lines, 0, 0)
    if index != len(lines):
        raise FormatError("Indentação inesperada na linha %d" % lines[index][2])
    return value if value is not None else {}


def _block(lines, index, indent):
    if index >= len(lines):
        return None, index
    if lines[index][1].startswith("- ") or lines[index][1] == "-":
        result = []
        while index < len(lines) and lines[index][0] == indent and (lines[index][1].startswith("- ") or lines[index][1] == "-"):
            item = lines[index][1][1:].strip()
            if not item:
                raise FormatError("Item de lista vazio na linha %d" % lines[index][2])
            result.append(scalar(item))
            index += 1
        return result, index
    result = {}
    while index < len(lines) and lines[index][0] == indent:
        _, content, number = lines[index]
        pair = _key_value(content)
        if not pair:
            raise FormatError("Esperado `chave: valor` na linha %d" % number)
        key, rest = _unquote(pair[0]), pair[1]
        if key in result:
            raise FormatError("Chave repetida `%s` na linha %d" % (key, number))
        index += 1
        if rest:
            result[key] = scalar(rest)
        elif index < len(lines) and lines[index][0] > indent:
            result[key], index = _block(lines, index, lines[index][0])
        else:
            result[key] = None
    return result, index


def _dump_scalar(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_dump_scalar(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(k + ": " + _dump_scalar(v) for k, v in value.items()) + "}"
    text = str(value)
    if (not text or _PLAIN_UNSAFE.search(text) or _INT.fullmatch(text)
            or text in ("null", "~", "true", "false") or "\n" in text):
        if "\n" in text:
            raise FormatError("Texto multilinha não é suportado no frontmatter")
        return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return text


def dumps(mapping, order=()):
    keys = [k for k in order if k in mapping] + [k for k in mapping if k not in order]
    lines = []
    for key in keys:
        value = mapping[key]
        if isinstance(value, dict) and value:
            lines.append(key + ":")
            lines.extend("  " + line for line in dumps(value).splitlines())
        elif isinstance(value, list) and value and all(isinstance(item, dict) for item in value):
            lines.append(key + ":")
            lines.extend("  - " + _dump_scalar(item) for item in value)
        else:
            lines.append(key + ": " + _dump_scalar(value))
    return "\n".join(lines) + "\n"


def split_frontmatter(text):
    if not text.startswith("---\n"):
        raise FormatError("Tarefa sem frontmatter")
    end = text.find("\n---\n", 3)
    if end < 0:
        if text.endswith("\n---"):
            end = len(text) - 4
        else:
            raise FormatError("Frontmatter sem fechamento")
    data = loads(text[4:end + 1])
    if not isinstance(data, dict):
        raise FormatError("Frontmatter precisa ser um mapa")
    return data, text[end + 5:]


def join_frontmatter(data, body, order=()):
    body = body.lstrip("\n")
    return "---\n" + dumps(data, order) + "---\n" + (("\n" + body.rstrip("\n") + "\n") if body.strip() else "")
