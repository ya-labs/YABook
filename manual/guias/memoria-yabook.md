# Memória do YABook: uso e funcionamento

O YABook mantém uma base própria de conhecimento, em arquivos JSON legíveis e
versionados no repositório privado de cada pessoa. O agente interpreta a conversa,
avalia descobertas e propõe mudanças; os serviços do plugin validam a proposta,
gravam somente o conteúdo aprovado e publicam os arquivos correspondentes.

Comece pelo [manual de instalação](instalacao-plugin-yabook.md). Este guia cobre
o uso diário, organização, Git, colaboração, busca e visualização. Os exemplos
são ilustrativos, não documentação funcional de uma aplicação.

## O que guardar

Uma boa memória modifica uma decisão futura: onde investigar um comportamento,
qual contrato foi confirmado, em que condição um procedimento funciona ou por
que uma hipótese foi descartada. Inclua evidência, limite de aplicação e situação.

Não transforme toda conversa em memória. Logs, status transitório, tarefas
pendentes e descrições repetidas de commits geralmente pertencem à issue ou ao
histórico do projeto. Credenciais e autorizações de sessão não pertencem à base.
A detecção de padrões de segredo é uma ajuda, não substitui a revisão do conteúdo.

`add`, `edit` e `forget` passam pela curadoria do agente. Um pedido pode resultar
em adicionar, atualizar, relacionar, arquivar, remover, manter ou rejeitar. O
agente explica utilidade, motivo, evidência e aplicação antes de propor escrita.

## Organização: tipos e níveis de recuperação

A memória tem duas dimensões independentes: o tipo de informação e o nível de
detalhe necessário para executar a tarefa. O formato canônico atual é o schema 2.

| Tipo | Conteúdo | Coleção canônica |
| --- | --- | --- |
| `profile` | Idioma, áreas de trabalho e estilo de colaboração | `records` |
| `preference` | Comportamento desejado, explícito ou inferido, com aplicação | `records` |
| `procedure` | Forma aprendida de investigar, executar ou validar | `records` |
| `knowledge` | Fato, hipótese, decisão ou responsabilidade técnica | `records` |
| `project` | Índice estável de um projeto | `groups` |
| `topic` | Assunto que reúne conhecimentos e experiências | `groups` |
| `collection` | Agrupamento auxiliar, inclusive grupos antigos | `groups` |
| Entidade | Fonte, módulo, operação, tabela ou conceito | `entities` |
| Experiência | Relato compacto de uma tarefa e seus resultados | `episodes` |

Grupos por projeto e assunto apontam para os registros; não copiam suas
informações. `parent` liga grupos hierárquicos; ciclos e filhos fora do escopo
do pai são recusados. `members` pode reunir registros, entidades, grupos e
experiências. Um registro pode participar de mais de um assunto.

Use IDs estáveis para projetos, nomes relativos ao repositório para fontes e
componentes de escopo que funcionem em qualquer máquina. `project_id`, quando
informado, precisa apontar para um grupo `project` do mesmo escopo. Caminhos
absolutos dos checkouts ficam no mapa local de `projects` da configuração.

### Perfil, preferências e procedimentos

Registros usam `kind`. A ausência desse campo em uma base antiga significa
`knowledge`; o leitor não tenta inferir um perfil nem reescrever a origem.
Preferências têm `authority: explicit|inferred` e `activation: always|conditional`.
A aplicação permanente de preferências e procedimentos exige origem explícita.
Perfil confirmado e preferências próprias, explícitas, confirmadas e permanentes
entram no contexto inicial. Preferências condicionais e procedimentos são
indexados e consultados conforme a tarefa. `priority` é opcional, inteiro de
0 a 100; organiza a seleção dentro do orçamento, sem aumentar a confiança.

Regras normativas do método permanecem na skill, no arquivo de instruções e
nos hooks aplicáveis. Um procedimento aprendido não cria autorização nem vira
um bloqueio obrigatório por estar na memória. Dados de fontes conectadas podem
ser pistas; perfil e preferências pessoais do colaborador são excluídos da visão
aplicável, mesmo quando a política permitir ler o escopo pessoal.

### Assuntos, nomes e situações de aplicação

`keywords`, `aliases` e `triggers` são listas de textos pesquisáveis. Exemplo
fictício: um assunto de sincronização pode ter o alias “dados não chegaram” e
ligar a entidade `exemplo-sync.p` aos conhecimentos que explicam seu papel.
O nome do fonte é uma entidade; o assunto pode envolver vários fontes e camadas.
A associação e a responsabilidade precisam de evidência antes de confirmação.

Um resumo de grupo tem `summary_sources` com a revisão de cada membro. Se um
membro mudar, sair da visão ou tiver resumo desatualizado, o resumo dependente
não é usado como atual. Essa invalidação alcança os grupos ancestrais.
Na busca externa, filtros são aplicados antes da composição dos índices e
resumos, incluindo a retirada de vínculos e conteúdo agregado incompatível.

### Experiências de tarefas e evidências

Uma experiência preserva o contexto da descoberta: `objective`, `context`,
`actions` (lista), `outcome` e `validation` (lista). `learnings` referencia IDs
em `records`; registros podem apontar de volta por `episodes`. Evidências ficam
em `evidence`, com referências a código, commits, issues ou documentos. Não
copie conversas e logs integrais para o relato. Uma experiência confirmada exige
evidência; validação pendente deve permanecer explicitamente descrita.

O relato histórico não é automaticamente conhecimento vigente. Ao corrigir um
fato, atualize ou arquive o registro apropriado e preserve a experiência como
contexto histórico. O histórico em `history/` continua registrando as operações
de curadoria; é diferente das experiências em `episodes/`.

### Visões geradas e Git

Após uma aplicação aprovada, o serviço gera:

- `views/memory_summary.md`: perfil, preferências, procedimentos e entrada para o índice.
- `views/MEMORY.md`: índice por escopo, tipo, situação e termos, apontando para os JSON.
- `views/topics/<id>.md`: resumo aprovado do grupo, vínculos e revisões.

Essas visões são derivadas, identificadas por hash e publicadas no mesmo commit
do conhecimento. Não as edite como fontes independentes. A geração reorganiza
os dados aprovados; não produz conclusões novas com um modelo. Um novo resumo
semântico exige curadoria e aprovação. Só arquivos cujo conteúdo mudou são
reescritos; assuntos independentes conservam sua versão. Arquivos sem a marca
de geração e links simbólicos nos destinos são recusados.

### Recuperação progressiva

Na abertura da sessão, o plugin entrega perfil, preferências permanentes e um
índice do escopo pessoal e do projeto. O resultado respeita um orçamento e
mantém JSON válido: itens que não cabem ficam para consulta, com `truncated`.
Ao receber a tarefa, o hook consulta assuntos e conhecimento pertinente,
incluindo preferências condicionais que correspondem aos termos da mensagem.
Não carrega experiências ou evidências extensas por padrão.

O agente aprofunda com `retrieve`: assunto → conhecimento → experiência →
evidência. Também busca registros sem grupo para não esconder conhecimento
cuja classificação está incompleta. Expande relações explícitas até três saltos,
sem abrir assuntos irmãos apenas porque têm o mesmo projeto. `index` mostra a
organização; `show` permite conferir o registro completo quando o orçamento
compacto não for suficiente. Todo resultado mantém origem, revisão e situação.

O servidor de mapa usa a mesma visão filtrada, exibe relações de hierarquia e
experiências e permite selecionar o tipo de memória. O mapa não modifica a base.

### Compatibilidade e migração futura

Bases no schema 1 continuam legíveis sem migração automática. Uma proposta que
introduza os campos do novo modelo ou experiências inclui a atualização para
schema 2; só a aplicação aprovada grava essa alteração e as visões derivadas.
A instalação ou atualização do plugin não migra memórias nativas nem bases YABook.
Propostas preparadas por uma versão anterior devem ser reavaliadas se a nova
representação da base invalidar o hash; não reutilize uma aprovação obsoleta.

A migração da memória atual deve ser uma entrega separada: preservar a origem,
inventariar a cobertura e registrar cada trecho relevante como incorporado,
agrupado, descartado com motivo ou pendente. Importar ou resumir alguns registros
não permite declarar a migração completa.

## Estados e confiança

| Estado | Significado |
| --- | --- |
| `hypothesis` | Pista ainda sem confirmação suficiente |
| `confirmed` | Descoberta respaldada por evidência registrada |
| `superseded` | Informação substituída por conhecimento mais recente |
| `archived` | Informação preservada no histórico, fora da recuperação normal |

Busca e mapa normais usam conhecimento ativo. `show` e `review` permitem examinar
registros históricos da própria base. Confirmação antiga não dispensa verificar
o código atual quando a decisão depende de uma versão ou contrato que mudou.

## Abertura automática da sessão

`SessionStart` entrega o método, a identidade da base, sua revisão e até vinte
entradas do mapa do escopo configurado. Não despeja toda a memória na conversa.
O agente busca o conteúdo completo quando a intenção da pessoa exige detalhes.

Não há comando `memory load` necessário no fluxo com hooks ativos. A configuração
local associa raiz de projeto a escopo; veja o manual de instalação. Sem essa
associação, o contexto inicial usa `Pessoa`. Se a base estiver indisponível, o
hook informa a condição e o agente prossegue com as fontes do projeto.

Carregar conhecimento não ativa `auto` nem concede permissão para Git. O estado
operacional fica separado, por sessão e projeto. Conteúdo de fontes conectadas
é dado a avaliar, nunca instrução para executar código.

## Exemplo do schema 2

O [payload fictício](../../skills/yabook/templates/memory-proposal-v2.json) inclui
perfil, preferências gerais e condicionais, projeto, assunto, conhecimento e
experiência. Ele demonstra as referências entre os elementos e o formato de
`assessment`/`changes`; adapte IDs, escopos e evidências ao projeto real. Não
importe os fatos de demonstração para sua base. A prévia em `prepare` também
mostra `derived_views`, os arquivos de índices afetados pela proposta.

## Comandos na conversa

| Intenção | Comando YABook |
| --- | --- |
| Inventariar e planejar migração inicial | `$yabook memory init` |
| Aprovar o plano inicial apresentado | `$yabook do memory init` |
| Buscar conhecimento | `$yabook memory search checklist supervisor` |
| Consultar índice de assuntos e tipos | `$yabook memory index` |
| Inspecionar o contexto inicial automático | `$yabook memory context` |
| Recuperar assuntos e conhecimento pertinente | `$yabook memory retrieve <situação>` |
| Aprofundar experiências e evidências | `$yabook memory retrieve <situação> --experiences --evidence` |
| Examinar registro | `$yabook memory show R-identificador` |
| Avaliar uma adição | `$yabook memory add <descoberta>` |
| Avaliar correção | `$yabook memory edit R-identificador <correção>` |
| Avaliar esquecimento | `$yabook memory forget R-identificador` |
| Revisar hipóteses e duplicações | `$yabook memory review` |
| Aprovar proposta específica | `$yabook do memory P-identificador` |
| Aprovar única proposta pendente | `$yabook do memory` |
| Preparar conexão com outra base | `$yabook memory source add <URL>` |
| Aprovar política de conexão | `$yabook do memory source add <fonte>` |
| Examinar política de sincronização | `$yabook memory sync` |
| Sincronizar conforme política apresentada | `$yabook do memory sync` |
| Abrir ou exportar mapa | `$yabook memory map` |

Esses comandos são intenções encaminhadas pela skill. O agente monta os argumentos
dos serviços; não existe um executável de shell chamado `yabook`. O hook de
aprovação distingue `do memory [P-id]` de `do memory init`, `do memory sync`,
`do memory source add`, `do memory publish` e `do memory recover`. Operações
administrativas devem ser avaliadas pela skill com a política exata apresentada;
um nome de operação não é um ID de proposta.

## Exemplo: descoberta durante desenvolvimento

Imagine investigar “checklist não está chegando para o supervisor”. A busca
deve recuperar conhecimento do app, da sincronização e da operação relacionada.
Se uma memória aponta para `lnws-pv200c2`, isso direciona a leitura; não prova,
sozinho, a causa do incidente. Esse nome vem do exemplo de desenho da solução
e não foi confirmado por este guia como responsável por um fluxo real.

Após investigar o código, o agente pode apresentar:

```text
Possível atualização de memória
Descoberta: a operação X participa do recebimento do checklist no cenário Y.
Veredito: atualizar R-operacao-checklist e relacionar à entidade E-operacao.
Motivo: evita repetir a identificação do ponto de entrada.
Evidência: caminho do fonte e revisão examinada.
Aplicação: ao investigar falha de recebimento no cenário Y, começar por X;
verificar também os filtros atuais e a versão do contrato.
Limite: não explica todos os casos de checklist ausente.
Proposta: P-...; arquivos e publicação apresentados na prévia.
Aprovação: $yabook do memory P-...
```

Ao concluir `dev`, o agente avalia esse aprendizado contra o que já existe.
Se não há novidade útil, encerra sem recomendar memória. O modo `auto` para
desenvolvimento não transforma automaticamente cada descoberta em escrita.

## Prévia e aprovação exata

A proposta contém a avaliação, mudanças, snapshot resultante e hash de aprovação.
O serviço detecta alteração da prévia e mudança da base após a proposta. Nessas
situações, exige reavaliação. Sem ID, a aprovação só é inequívoca quando existe
exatamente uma proposta pendente.

O hash liga a execução ao conteúdo, mas não prova autorização da pessoa. O agente
obtém a aprovação na conversa atual antes de chamar o serviço. A publicação Git
faz parte da operação apresentada quando a base já é um repositório configurado.

Prefira arquivar informação que perdeu aplicação. Remover exclui o arquivo
canônico, mas snapshots e Git podem preservar versões anteriores. `forget`
não é apagamento definitivo de todos os históricos ou cópias dos colaboradores.

## Armazenamento e versionamento

```text
YABook-memory-LOGIN/
  memory.json
  records/*.json
  entities/*.json
  groups/*.json
  episodes/*.json
  views/memory_summary.md
  views/MEMORY.md
  views/topics/*.md
  history/*.json
  .gitignore
  .yabook-local/              # ignorado pelo Git
    proposals/
    transaction.json         # somente durante escrita interrompida
    publication.json         # somente enquanto publicação está pendente
    search.sqlite
    sources/
```

`memory.json` identifica formato (schema 2 para novas bases), proprietário e UUID da base. IDs são estáveis
e únicos; cada alteração incrementa a revisão. O histórico registra veredito,
motivo, ator, mudanças e snapshot para rastrear a aplicação.

`do memory` aplica a proposta, adiciona apenas os paths correspondentes ao
index, faz commit e push. Um worktree sujo bloqueia nova escrita. Falha de rede
após commit retorna `pending_push`: repita a publicação, sem gerar nova proposta
para o mesmo conteúdo. Índice staged com arquivos independentes também bloqueia.

Casa e trabalho usam clones do mesmo repositório privado. Antes de escrever em
outra máquina, sincronize. O fluxo aceita `pull --ff-only`; históricos divergentes
precisam de revisão. Não há force push nem resolução automática de conflitos.

Repositório privado não substitui curadoria de dados. Acesso GitHub pode conceder
leitura da base inteira. A configuração por escopo controla uso pelo plugin,
não restringe o que um colaborador autorizado consegue ler no GitHub.

## Compartilhamento com outra pessoa

Cada pessoa mantém seu próprio repositório. Após conceder acesso no GitHub por
um procedimento separado, configure o repositório da outra pessoa como fonte:

```json
{
  "id": "marco",
  "remote": "https://github.com/LOGIN-MARCO/YABook-memory-LOGIN-MARCO.git",
  "branch": "main",
  "includes": [["Organização", "Apps comerciais"]],
  "excludes": [["Pessoa"]],
  "refresh_seconds": 900
}
```

A configuração fica em `.yabook-local/sources.json`, por máquina. Sem includes
explícitos, a conexão é recusada. O plugin usa um espelho Git e lê JSON canônico;
não executa arquivos, hooks ou scripts do repositório conectado.

Após sync, registros relevantes já podem participar da busca e do mapa, com
origem externa identificada, sem importação manual. Informação pessoal excluída
não deve entrar na recuperação nem nas relações apresentadas. Uma mudança na
política é reaplicada às consultas, mesmo quando o cache já existe.

Para incorporar uma descoberta à sua base, prepare outra proposta com origem
preservada (`vault_id`, ID e revisão de origem). Isso permite detectar cópias
e atualizações; não copie uma descoberta como se fosse originalmente sua.
Diferenças entre a versão incorporada e a fonte são sinalizadas para avaliação.

`do memory sync` publica commit aprovado pendente, atualiza a própria base e
avalia diferenças das fontes conectadas. Pode ser usado no fim do dia. Para
antecipar novidades, configure `refresh_on_start: true`, aprovando essa política;
o intervalo da fonte limita a frequência. Sem essa configuração não há fetch
automático nem um agendador diário. Falhas de rede não tornam cache antigo atual.

## Busca textual e vetorial

A consulta textual usa SQLite FTS5, escopo e relações explícitas. Um modelo
Ollama opcional acrescenta resultados semânticos, combinados por ranking. A
busca continua textual se o serviço de embeddings falhar.

Os resultados incluem origem, estado e motivo de recuperação. Conteúdo superado
ou arquivado não volta à busca normal por semelhança. O orçamento limita o
contexto entregue; o agente aprofunda apenas os resultados relevantes.

Embeddings são derivados do conteúdo, mas podem ser versionados ou compartilhados
quando fizer sentido. O pacote registra hash do conteúdo, revisão, identidade,
modelo e pipeline. A importação aceita somente vetores compatíveis com o
conhecimento atualmente visível; não cria registros nem amplia escopos.

O índice FTS fica local porque é reconstruível e produz alterações pouco úteis
em revisão. O cache de vetores também fica local por padrão. Exportar um pacote
de vetores e incluí-lo em Git é uma operação explícita, separada do commit da
memória. Use versões estáveis de modelo; modelos diferentes ou alterados exigem
regeração compatível. O runtime atual envia embeddings somente a endpoint local
Ollama; não integra automaticamente provedores externos.

## Mapa visual

O mapa apresenta a mesma base filtrada usada na recuperação: hierarquia de
escopos, registros, entidades, grupos e relações. O painel de detalhes mostra
conteúdo, aplicação, evidência, estado, revisão e origem. Filtros ajudam a explorar
assunto e fonte sem criar outra base de conhecimento.

Há dois modos: HTML exportado, que é um snapshot, ou servidor local somente
leitura, que consulta novamente a base. O navegador verifica atualizações a cada
quinze segundos. O servidor escuta somente `127.0.0.1`; não é um site público.
O grafo limita a quantidade desenhada para manter a interação utilizável.

A visualização não altera registros. Correções passam pela curadoria e proposta.
Exportações podem conter conhecimento pessoal conforme o escopo escolhido;
revise o conteúdo antes de compartilhar o HTML.

## Serviços de terminal

Os exemplos abaixo são para diagnóstico ou automação do agente após as aprovações
pertinentes. Substitua os paths; `SCRIPT` aponta para a cópia instalada:

```bash
SCRIPT="$HOME/.local/share/yabook/plugins/0.1.0/skills/yabook/scripts/yabook_memory.py"
BASE="$HOME/.local/share/yabook/memory"

python3 "$SCRIPT" --root "$BASE" list
python3 "$SCRIPT" --root "$BASE" search "checklist supervisor" \
  --scope "Organização/Apps comerciais/App" --limit 8 --budget 6000
python3 "$SCRIPT" --root "$BASE" show R-operacao-checklist
python3 "$SCRIPT" --root "$BASE" review
python3 "$SCRIPT" --root "$BASE" pending
python3 "$SCRIPT" --root "$BASE" map --serve --port 8765
python3 "$SCRIPT" --root "$BASE" map --output /CAMINHO/mapa-novo.html
```

Para busca híbrida, adicione `--model NOME-MODELO` à consulta; o endpoint padrão
é `http://127.0.0.1:11434/api/embed`. Para exportar/importar vetores:

```bash
python3 "$SCRIPT" --root "$BASE" vectors-export --output /CAMINHO/vetores.json
python3 "$SCRIPT" --root "$BASE" vectors-import --input /CAMINHO/vetores.json
```

### Preparar uma mudança

Exemplo mínimo de payload `mudanca.json`, com hipótese explicitamente delimitada:

```json
{
  "assessment": {
    "verdict": "add",
    "reason": "Preservar ponto de investigação ainda não confirmado",
    "utility": "Reduzir descoberta repetida do ponto de entrada",
    "application": "Pesquisar esta pista antes de repetir a investigação",
    "evidence_status": "Hipótese; confirmar no código atual"
  },
  "changes": [
    {
      "collection": "records",
      "id": "R-pista-sync",
      "value": {
        "title": "Pista de sincronização do checklist",
        "scope": ["Organização", "Apps comerciais", "App", "Sincronização"],
        "state": "hypothesis",
        "content": "A operação X pode participar do recebimento no cenário Y.",
        "application": "Investigar X quando ocorrer Y; não assumir causa confirmada.",
        "conditions": "Somente cenário Y",
        "evidence": []
      }
    }
  ]
}
```

```bash
python3 "$SCRIPT" --root "$BASE" prepare --input /CAMINHO/mudanca.json --actor meu-agente
python3 "$SCRIPT" --root "$BASE" pending P-ID-RETORNADO
# Apenas após aprovação do conteúdo exato na conversa:
python3 "$SCRIPT" --root "$BASE" apply P-ID-RETORNADO --approval-hash HASH-RETORNADO
```

Uma atualização fornece o valor completo do registro; uma remoção usa `delete:
true` em vez de `value`. Ajuste referências na mesma proposta para evitar links
inexistentes. IDs e revisões são gerenciados pelo serviço. Evidência é obrigatória
para estado confirmado; cite fonte e revisão de forma verificável.

### Inicialização e conexão

```bash
python3 "$SCRIPT" --root "$BASE" inventory --agent meu-agente --source /MEMORIA/ACESSIVEL
python3 "$SCRIPT" --root "$BASE" init-plan --agent meu-agente --source /MEMORIA/ACESSIVEL \
  --curated /CAMINHO/curadoria.json --output /CAMINHO/plano.json
# Após revisar e aprovar plano, conta e curadoria:
python3 "$SCRIPT" --root "$BASE" init-apply --plan /CAMINHO/plano.json \
  --curated /CAMINHO/curadoria.json --approval-hash HASH-PLANO \
  --config "$HOME/.config/yabook/config.json"

# Após aprovar a política contida no JSON da fonte:
python3 "$SCRIPT" --root "$BASE" source-add --input /CAMINHO/fonte.json
python3 "$SCRIPT" --root "$BASE" sync
```

`bootstrap --owner LOGIN` cria uma base local vazia para testes ou uso sem Git;
não cria o repositório remoto. A inicialização com Git usa `init-plan/init-apply`.

## Recuperação de falhas

| Condição | Ação |
| --- | --- |
| Proposta alterada ou base mudou | Reavaliar e preparar nova proposta |
| Mais de uma proposta pendente | Identificar a proposta aprovada pelo ID |
| Transação interrompida | Inspecionar o journal e executar `recover` autorizado |
| Commit pronto, push falhou | Executar `publish` autorizado após corrigir acesso |
| Worktree/index sujo | Identificar e separar a alteração independente antes de escrever |
| Históricos divergentes | Revisar Git; não forçar sync nem descartar trabalho |
| Grupo com resumo antigo | Reavaliar membros e revisões antes de preparar outro resumo |
| Registro externo contradiz sua cópia | Verificar evidência e propor atualização com linhagem |

Não apague journals para fazer a ferramenta ignorar um erro. Faça backup da base
antes de uma recuperação manual. Sync e configuração de fontes são locais por
máquina; revê-las faz parte da preparação de um novo ambiente.

## Limites da primeira versão

A curadoria inteligente é feita pelo agente seguindo a skill; o runtime não
contém um modelo autônomo julgando a verdade das descobertas. Validações
estruturais, hashes e filtros tornam o resultado verificável, mas não comprovam
uma afirmação técnica sem evidência real.

Não há daemon de sincronização, editor visual, serviço web público, ACL por
arquivo nem extração de memória interna do provedor. Hooks dependem do suporte
do host. A instalação e a remoção de guardrails exigem a verificação descrita
no manual de instalação. O esquema atual é versão 1; mudanças de formato precisam
de migração explícita.

## Independência do agente

A mesma `memory_root` pode ser usada por qualquer agente com acesso ao serviço
Python. `inventory` e `init-plan` aceitam `--agent <nome>` sem lista fechada;
`--source` pode ser um arquivo ou pasta com Markdown, texto, JSON ou YAML.
O nome identifica a origem, sem conceder permissões. Arquivos candidatos ainda
precisam de curadoria: exportações não são memórias aprovadas automaticamente.
Memórias ocultas ou disponíveis somente por API precisam ser exportadas pelo
mecanismo real do agente; o YABook não presume acesso a elas.

Consulte a [instalação portátil e ponte de eventos](instalacao-plugin-yabook.md#uso-com-outros-agentes)
para carregar o mesmo método e contexto em outro host. Sem hooks, o método
continua disponível pela skill; automação depende da integração do host.
