# Instalação do plugin YABook

Este guia instala o pacote que reúne a skill, os serviços de memória e os
hooks. Para os conceitos, comandos e compartilhamento, consulte o
[manual de memória](memoria-yabook.md). A instalação não migra dados nem cria
um repositório GitHub sem a aprovação do plano de inicialização.

## Requisitos

- Python 3.10 ou superior, Git e GitHub CLI (`gh`) autenticado.
- Linux ou macOS: o bloqueio de escrita usa `fcntl`, da biblioteca padrão.
- Um host que aceite plugins e os eventos registrados em `hooks/hooks.json`.
- Ollama somente se quiser busca semântica; a busca textual não depende dele.

O runtime usa a biblioteca padrão do Python e SQLite com FTS5. Não há instalação
de dependências por `pip` ou `npm`. Windows nativo não está homologado; use um
ambiente Linux compatível. Testes de callbacks não substituem a verificação
dos eventos na versão do Codex ou Claude instalada.

## 1. Preparar uma cópia do pacote

No checkout do YABook, gere uma pasta fora do repositório:

```bash
python3 skills/yabook/scripts/yabook_plugin.py build \
  --output "$HOME/.local/share/yabook/plugins/0.1.0"
```

O destino deve ser novo. O empacotador copia `plugin.json`, `.claude-plugin/`,
`hooks/` e `skills/yabook/`, excluindo testes e caches Python. Isso preserva a
instalação anterior para rollback. Ao atualizar, escolha outro diretório e
aponte o host para ele; não sobrescreva uma pasta carregada por uma sessão.

## 2. Carregar no Codex

O registrador incluído prepara uma cópia por hash de conteúdo e adiciona somente
a entrada YABook ao marketplace pessoal:

```bash
python3 skills/yabook/scripts/yabook_plugin.py install-codex
```

Repetir o comando não duplica a entrada; uma atualização usa outra pasta de
conteúdo. O resultado informa o path e a habilitação TOML. O script preserva
outras entradas e recusa substituir uma entrada `yabook` que não gerencia.
Ele registra a fonte; a instalação/habilitação e a confiança nos hooks continuam
no host. Para remover somente esse registro:

```bash
python3 skills/yabook/scripts/yabook_plugin.py uninstall-codex
```

`--home /PASTA-DE-TESTE` permite testar o registro sem alterar sua configuração
pessoal. O pacote e a memória não são apagados pela remoção do registro.

O pacote inclui o manifesto portátil `plugin.json` e a extensão de hooks do
Codex. A documentação oficial distingue o suporte a hooks em plugins
instalados manualmente no desktop; confirme o suporte no seu host antes de
remover qualquer guardrail existente.

Para registrar uma fonte local, edite o marketplace pessoal em
`~/.agents/plugins/marketplace.json`. Preserve as entradas existentes. Se o
arquivo ainda não existir, use:

```json
{
  "name": "yabook-local",
  "interface": { "displayName": "YABook local" },
  "plugins": [
    {
      "name": "yabook",
      "source": {
        "source": "local",
        "path": "./.local/share/yabook/plugins/0.1.0"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

O caminho da fonte é relativo à raiz pessoal documentada pelo Codex. Abra o
gerenciamento de plugins do aplicativo, localize o YABook e instale/habilite a
entrada local. Quando seu host usar habilitação por configuração TOML:

```toml
[plugins."yabook@yabook-local"]
enabled = true
```

Use o nome real do marketplace se já houver um arquivo com outro nome. Não
substitua o restante de `config.toml`. Abra uma nova sessão após habilitar o
plugin e confirme a execução dos hooks conforme a seção de verificação abaixo.
A mera descoberta da skill no CLI não demonstra suporte ao carregamento por
hooks. Se o host não emitir os eventos, a skill funciona por invocação, mas
essa instalação ainda não oferece memória automática na abertura.

No Codex CLI 0.144.6 consultado durante o desenvolvimento, a ajuda também
disponibiliza `codex plugin marketplace add <fonte>` e
`codex plugin add yabook@<marketplace>`. A presença desses comandos não comprova
execução dos eventos deste plugin; valide instalação e confiança no runtime
usado. O procedimento acima segue o registro pessoal documentado para o desktop.

Referências: [criação e instalação de plugins do Codex](https://developers.openai.com/plugins/build/plugins)
e [hooks do Codex](https://developers.openai.com/codex/hooks).

## 3. Carregar no Claude Code

Para testar a instalação local em uma nova sessão:

```bash
claude --plugin-dir "$HOME/.local/share/yabook/plugins/0.1.0"
```

O manifesto específico fica em `.claude-plugin/plugin.json`; a skill e os hooks
ficam na raiz do pacote. Para instalação persistente, registre essa pasta no
marketplace local conforme a versão do Claude Code e instale a entrada na
interface de plugins. Os comandos de skills podem aparecer com namespace,
como `/yabook:yabook`; `$yabook` nos exemplos deste manual identifica a intenção
que o agente deve encaminhar à skill.

Se a sua versão disponibilizar o validador:

```bash
claude plugin validate "$HOME/.local/share/yabook/plugins/0.1.0"
```

Consulte a [referência de plugins do Claude Code](https://code.claude.com/docs/en/plugins-reference)
para instalação persistente e a [referência de hooks](https://code.claude.com/docs/en/hooks)
para permissões e eventos.

## 4. Criar a memória inicial

Na sessão com o plugin ativo, peça:

```text
$yabook memory init
```

O agente inventaria os arquivos acessíveis da memória atual, elimina conteúdo
temporário ou inadequado, relaciona conhecimento útil e apresenta o plano:
conta autenticada, base local, repositório privado, registros e publicação.
Revise a curadoria e aprove com:

```text
$yabook do memory init
```

O nome é `YABook-memory-<loginGitHub>`, usando o login da conta autenticada pelo
`gh`, não o nome de exibição. Um destino existente deve ser privado e compatível.
A origem permanece intacta. A ferramenta só inventaria arquivos acessíveis;
não promete capturar memória interna ou oculta do provedor.

Para outra máquina, clone seu repositório privado e configure a cópia local,
em vez de repetir a migração da origem:

```bash
gh repo clone LOGIN/YABook-memory-LOGIN "$HOME/.local/share/yabook/memory"
```

## 5. Configurar a máquina e o projeto

A configuração padrão é `~/.config/yabook/config.json`. A inicialização grava
`memory_root` e `repository`. Complete os projetos com caminhos absolutos reais:

```json
{
  "memory_root": "/home/voce/.local/share/yabook/memory",
  "repository": "LOGIN/YABook-memory-LOGIN",
  "projects": {
    "/home/voce/projetos/app": ["Organização", "Apps comerciais", "App"]
  },
  "refresh_on_start": false
}
```

O hook resolve a raiz Git do projeto e carrega um mapa compacto desse escopo.
Sem projeto configurado, usa o escopo `Pessoa`; não adivinha a organização pelo
nome da pasta. O agente consulta detalhes sob demanda. Configure as fontes
conectadas pelo fluxo descrito no manual de memória.

`YABOOK_CONFIG` substitui o caminho da configuração e `YABOOK_STATE` substitui
o diretório de recibos de sessão. Para configuração alternativa, essas variáveis
precisam existir no ambiente que inicia o host, inclusive o desktop. Não grave
essas opções no repositório de conhecimento.

## 6. Verificar antes de retirar guardrails

Abra uma sessão nova em um projeto de teste. Confirme:

1. `SessionStart` adicionou o método e o mapa do escopo correto.
2. Uma consulta recupera a memória esperada e identifica a origem.
3. `PreToolUse` foi chamado numa ferramenta compatível.
4. Uma tentativa sem autorização, como commit fora de `auto`, recebe negação
   no caminho de ferramenta coberto pelo hook.
5. Outra sessão começa sem herdar `auto`, `do`, `bypass` ou autorização de merge.

Os recibos ficam em `~/.config/yabook/sessions/`, com nome derivado do ID da
sessão. `startup_seen` e `pretool_seen` registram eventos observados; não provam
que todo tipo de ferramenta ou comando composto é interceptado. Confira também
o comportamento no host. Os hooks reforçam o método; a skill continua necessária
para avaliar comandos indiretos, scripts, MCP e regras locais.

Só depois dessa verificação migre o bloco global canônico:

```bash
python3 "$HOME/.local/share/yabook/plugins/0.1.0/skills/yabook/scripts/yabook_plugin.py" \
  migrate-guardrails --agents /CAMINHO/AGENTS.md \
  --receipt /CAMINHO/recibo-da-sessao.json
```

O migrador exige os dois eventos, remove somente o bloco delimitado e idêntico
ao texto canônico, e salva `AGENTS.md.before-yabook-plugin`. Um bloco personalizado
ou backup existente bloqueia a operação para revisão. Preserve instruções
pessoais, RTK, limites do ambiente e regras específicas de cada projeto.

## Atualização, rollback e remoção

Para atualizar, gere outra cópia, altere a referência do host e abra uma nova
sessão. Preserve a cópia antiga até a verificação. Para rollback, reaponte o
host para a versão anterior; se retirou guardrails, restaure o bloco pelo backup.
Não substitua um `AGENTS.md` que recebeu outras alterações sem revisar o diff.

Para desinstalar, desabilite/remova o plugin no host e retire somente sua entrada
do marketplace e sua habilitação TOML. A base de memória, configuração e
repositório privado permanecem disponíveis. Apagar conhecimento ou excluir o
repositório remoto é uma operação separada.

## Diagnóstico

| Sintoma | Verificação |
| --- | --- |
| Skill aparece, memória não carrega | Confirmar hooks e nova sessão; presença da skill não prova execução de `SessionStart` |
| Hook retorna erro | Conferir Python, JSON de configuração, paths e log do host; o stderr informa a classe do erro |
| Mapa traz só memórias pessoais | Cadastrar raiz Git exata em `projects` |
| Fonte conectada está desatualizada | Executar sync aprovado; verificar intervalo, acesso GitHub e cache |
| Publicação pendente | Corrigir rede/autenticação e repetir `publish` autorizado; não reaplicar a proposta |
| Troca de máquina trouxe divergência | Inspecionar as branches; sync aceita somente avanço direto, sem resolução automática |
| Destino já existe | Usar uma nova pasta para pacote; para memória, revisar compatibilidade do destino |

## Situação da validação

O repositório contém testes dos serviços, callbacks, isolamento de sessão,
curadoria, publicação Git, busca e mapa. A instalação real no desktop Codex e
no Claude Code deve ser homologada na versão usada pela pessoa. Não remova os
guardrails globais com base somente nos testes unitários.

## Atualizar pelo YABook

Use `$yabook sync local` para comparar o plugin instalado com o checkout,
ou `$yabook do sync local` para aplicar a atualização automaticamente no Codex.
O pacote inclui manifestos, hooks, ícone e skill. O serviço valida a instalação
e recupera a versão anterior em caso de falha; memória e outros plugins são preservados.
Abra uma nova sessão após o sucesso para carregar os novos hooks.
Use `remote` quando a origem desejada for a branch principal oficial; ela precisa
conter o plugin completo. Outros agentes podem usar o adaptador de diretório gerenciado descrito abaixo.

## Uso com outros agentes

O método e os serviços de memória não dependem do Codex. Qualquer agente com
acesso a arquivos e Python pode consultar e manipular a mesma base YABook.
Instalação e eventos são integrações separadas: o host precisa saber carregar
uma skill ou instruções e, para automação, chamar e interpretar os eventos.

### Instalação portátil

Escolha um diretório exclusivo, fora do checkout e dos caches de marketplaces.
Execute pelo terminal do agente, usando RTK quando disponível:

```sh
python3 skills/yabook/scripts/yabook_plugin.py install \
  --source /CAMINHO/YABook --output /CAMINHO/plugins/yabook
python3 skills/yabook/scripts/yabook_plugin.py sync \
  --source /CAMINHO/YABook --installed /CAMINHO/plugins/yabook --adapter directory
```

`install` cria um pacote completo e uma marca de gerenciamento. Configure o
host para carregar a skill em `/CAMINHO/plugins/yabook/skills/yabook/SKILL.md`,
conforme seu mecanismo real de skills ou instruções. Não copie a base de memória
para dentro do pacote. Para atualizar, `do sync` executa a segunda linha com
`--apply`; o serviço preserva um backup e informa seu caminho.

A preparação ocorre ao lado da instalação para permitir renomeação no mesmo
filesystem. O serviço recusa destinos sem marca de gerenciamento e pastas de
outras skills. Não use esse caminho para substituir uma instalação de marketplace.
O adaptador Codex continua disponível para instalações gerenciadas pelo Codex.

### Ponte de eventos

Em hosts sem protocolo compatível com os hooks empacotados, chame:

```sh
python3 /CAMINHO/plugins/yabook/skills/yabook/scripts/yabook_hook.py --format generic
```

Envie um objeto JSON pela entrada padrão:

```json
{
  "event": "session.start",
  "agent": "meu-agente",
  "session": "identificador-estavel-da-sessao",
  "workspace": "/CAMINHO/projeto"
}
```

| Evento | Dados adicionais | Aplicação pelo host |
| --- | --- | --- |
| `session.start` | `source`: `startup`, `resume` ou `compact` | Injetar `context` antes do trabalho |
| `user.prompt` | `message`: mensagem real do usuário | Atualizar autorizações desta sessão |
| `tool.before` | `tool`: `name`, `kind` e `input` | Bloquear a ferramenta quando `decision` for `deny` |
| `tool.after` | Mesmo objeto `tool` | Registrar edição realizada |
| `session.stop` | `stop_active`: evita repetição | Entregar avaliação de memória quando solicitada |

`tool.kind` pode ser `edit` ou `shell`; comandos ficam em `tool.input.command`
ou `tool.input.cmd`. Outros tipos mantêm o nome fornecido e precisam de análise
pela skill. A resposta neutra contém `context`, `decision` (`deny` ou `observe`)
e `reason`. `observe` não concede autorização nem certifica segurança. O host
deve propagar erros do callback e as negações; ignorar o resultado elimina a
verificação. Não há cobertura completa para shell composto ou ferramentas opacas.

Os identificadores de agente e sessão isolam o estado operacional. Use nomes
estáveis e não reutilize uma sessão encerrada para uma conversa nova. Ao iniciar
nova conversa, envie `source: startup`; aprovação e auto não são memória durável.
Os serviços de memória continuam usando `YABOOK_CONFIG` e a mesma `memory_root`.

### Agentes sem hooks

Carregue a skill ou seu método pelo mecanismo de instruções reconhecido pelo
host e use os serviços explicitamente durante o trabalho. O plugin não pode
criar eventos em um host que não os oferece. Informe a ausência de carregamento
automático e de bloqueio antes de ferramentas, sem remover guardrails existentes.

Para guardrails globais, use o arquivo reconhecido pelo host e confirmado na
sessão, ou `YABOOK_INSTRUCTIONS`. O destino deixa de ser presumido como Codex.
No Claude, instruções pessoais podem ficar em `~/.claude/CLAUDE.md`, conforme a
[documentação oficial](https://code.claude.com/docs/en/memory).
