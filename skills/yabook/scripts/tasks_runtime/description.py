"""Contrato de descrição para tarefas novas e modelos apresentados pelo CLI."""
import re

SUMMARY = "Resumo rápido"
SCOPE = "Escopo"
ACCEPTANCE = "Critérios de aceite"
NOTES = "Observações"
AI_INFO = "Informações para IA"

SUMMARY_FIELDS = (
    ("Tarefa", "O que precisa ser feito."),
    ("Entrega esperada", "Resultado para quem vai usar ou receber a entrega."),
)
LIMIT = ("Limite", "Até onde vai a tarefa.")
AI_FIELDS = (
    ("Contexto confirmado e objetivo", "Situação atual e o resultado pretendido."),
    ("Decisões, limites e premissas", "Condições que orientam a execução."),
    ("Abordagem e pontos relevantes para continuidade", "O que outra sessão precisa saber para retomar."),
    ("Validações executadas ou esperadas", "Como verificar a entrega e o que já foi verificado."),
    ("Riscos, dependências e pendências", "O que pode afetar a entrega ou ainda depende de definição."),
)

MODEL_COMMANDS = "Veja o modelo em add --help ou capture --help."
SESSION_RULE = ("Ao criar tarefa com add ou capture, preencha a descrição no contrato Markdown. " + MODEL_COMMANDS)
_HEADING = re.compile(r"^ {0,3}(#{1,2})[ \t]+(.+)$")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FIELD = re.compile(r"^ {0,3}(?:[-*+]|\d+[.)])[ \t]+(?:\*\*([^*]+)\*\*|([^:—–]+?)\s*[:—–])[ \t]*(.*)$")


def description_model(*, package=False):
    """Modelo legível no CLI, com os mesmos nomes usados pelo validador."""
    summary = SUMMARY_FIELDS if package else SUMMARY_FIELDS + (LIMIT,)
    sections = [(SUMMARY, summary)]
    if package:
        sections.append((NOTES, "- Contexto estável do pacote."))
    else:
        sections += [(SCOPE, "- Mudanças incluídas nesta tarefa."),
                     (ACCEPTANCE, "- Condições verificáveis para considerar a entrega concluída.")]
    sections.append((AI_INFO, AI_FIELDS))
    return "\n\n".join(
        f"## {title}\n\n" + (body if isinstance(body, str) else
                             "\n".join(f"- **{name}** — {example}" for name, example in body))
        for title, body in sections
    )


def description_help():
    return ("Descrição de tarefas novas em Markdown. Substitua os exemplos por informações da tarefa.\n\n"
            "Modelo de issue:\n\n" + description_model() + "\n\n"
            "Modelo de issue pacote:\n\n" + description_model(package=True))


def _sections(text):
    sections, body, fence = {}, None, ""
    for line in re.sub(r"<!--.*?(?:-->|$)", "", text, flags=re.S).splitlines():
        marker = _FENCE.match(line)
        if marker:
            token, rest = marker.groups()
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence) and not rest.strip():
                fence = ""
            continue
        if fence:
            continue
        heading = _HEADING.match(line)
        if heading:
            level, title = heading.groups()
            body = sections.setdefault(title.rstrip(" #\t").casefold(), []) if level == "##" else None
        elif body is not None:
            body.append(line)
    return sections


def _has_text(value):
    return any(char.isalnum() for char in value)


def _missing_fields(body, required):
    present = set()
    for index, line in enumerate(body):
        item = _FIELD.match(line)
        if item:
            bold, plain, value = item.groups()
            next_line = body[index + 1] if index + 1 < len(body) else ""
            written_on_next_line = (next_line.startswith(("  ", "\t"))
                                    and not _FIELD.match(next_line) and _has_text(next_line))
            if _has_text(value) or written_on_next_line:
                present.add((bold or plain).strip(" :\t").casefold())
    return [label for label, _ in required if label.casefold() not in present]


def description_issues(text):
    """Retorna seções ou campos ausentes, com a variante do pacote já prevista."""
    sections = _sections(text)
    package = NOTES.casefold() in sections and not ({SCOPE.casefold(), ACCEPTANCE.casefold()} & sections.keys())
    summary_fields = SUMMARY_FIELDS if package else SUMMARY_FIELDS + (LIMIT,)
    required = [(SUMMARY, summary_fields)]
    required.extend((title, ()) for title in ((NOTES,) if package else (SCOPE, ACCEPTANCE)))
    required.append((AI_INFO, AI_FIELDS))
    issues = []
    for title, fields in required:
        body = sections.get(title.casefold(), [])
        if not any(_has_text(line) and not line.lstrip().startswith("#") for line in body):
            issues.append(f"preencha a seção ## {title}")
        elif fields and (missing := _missing_fields(body, fields)):
            issues.append(f"preencha em ## {title}: " + ", ".join(missing))
    return issues
