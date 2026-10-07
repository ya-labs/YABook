# Sincronização do plugin YABook

Use para `$yabook sync [local|remote]` e `$yabook do sync [local|remote]`.
`sync` apenas compara; `do sync` atualiza automaticamente o pacote instalado.
O pacote inclui `plugin.json`, `.claude-plugin/`, `hooks/`, `assets/` e
`skills/yabook/`. A antiga pasta `~/.codex/skills/yabook` deixa de ser o destino.
Não confunda com `memory sync`, que sincroniza conhecimento.

## Origem

Sem modo explícito, prefira origem local válida; caso indisponível, use remoto.
Local: checkout atual de `YA-LABS/YABook`, `YABOOK_REPO_PATH` ou checkout conhecido.
Valide identidade, versão, manifestos, hooks, skill e arquivos referenciados.
Uma árvore contendo somente a skill é incompatível; não reduza o pacote.

Remote: branch principal de `https://github.com/YA-LABS/YABook`.
`sync remote` consulta árvore e conteúdos pela API, sem clone/fetch, temporários
ou mutações. Em `do sync remote`, baixe o pacote completo para diretório temporário
e valide; não use pull nem altere o checkout local. Se a branch principal ainda
não contiver o plugin, informe origem incompatível.

## Destino e comparação

Identifique o host e a raiz do plugin que forneceu a skill atual. No Codex,
confirme identidade, marketplace, versão e ativação com `codex plugin list --json`.
O cache fica em `$CODEX_HOME/plugins/cache/<marketplace>/yabook/<versão>` ou
`~/.codex/plugins/cache/...`. Não crie esse diretório manualmente.
Ignore somente testes de desenvolvimento, `__pycache__` e `*.pyc`.
Compare bytes, inclusive imagens, scripts e manifestos; reporte arquivos alterados,
ausentes e excedentes. Não imprima conteúdo de memória ou configuração.

Para uma origem local no Codex, execute via RTK:

```sh
python3 <origem>/skills/yabook/scripts/yabook_plugin.py sync --source <origem> --installed <raiz-do-plugin-atual>
```

Relate origem, destino, host, versão, estado e diferenças. Estados: sincronizado,
desatualizado, não instalado, origem indisponível ou validação falhou.
`sync` não modifica arquivos, registros, Git ou configurações.

## Aplicação autorizada

`do sync` repete a comparação e acrescenta `--apply` ao comando acima.
Não exija comandos manuais de instalação após essa aprovação.
Se já estiver sincronizado, encerre sem reinstalar.

O serviço prepara um pacote imutável por hash, valida os arquivos, atualiza
somente a entrada YABook do marketplace pessoal e executa os comandos oficiais
`codex plugin remove` / `codex plugin add`. Valida o cache instalado contra o
pacote completo. Não edite o cache diretamente. Preserve pacote anterior para
recuperação; em falha, restaure a entrada e reinstale a origem anterior, verificando
o resultado. Se a recuperação falhar, reporte explicitamente a pendência.

Preserve outros plugins, memória nativa, repositório de memórias e configurações
do YABook. Plugin desativado ou instalação externa não gerenciada exige resolver
a incompatibilidade antes de atualizar. Não remova a antiga skill avulsa sem
pedido específico. Não faça commit, push, merge, pull nem troque branches.

O serviço automático atual atende Codex. Em outro host, verifique seu fluxo
suportado antes de aplicar; não use o instalador Codex em Claude. Informe quando
o adaptador de atualização automática não estiver disponível.

Após sucesso, informe versão/hash e necessidade de abrir nova sessão para usar
os hooks atualizados. A sessão atual mantém instruções já carregadas.
Esta operação atualiza a instalação somente após `do sync`; `bypass` não o substitui.
