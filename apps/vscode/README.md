# YABook para VS Code

Mostra no VS Code o que o YABook registra durante o trabalho do agente. A
extensão só lê o que os scripts Python do YABook geram; regras, hooks e memória
continuam no plugin.

## Tarefa ativa

No topo da barra lateral, a visão **Tarefa ativa** mostra a última tarefa
iniciada no YABook Tasks desta máquina (`local/ativa.json`): título, número,
coluna, issue e próximo passo. Clicar no título abre uma aba com os detalhes
(descrição, relatório e registro, lidos pelo `task show`); **Abrir no site do
YABook Tasks** abre o site já com o painel da tarefa. A visão se atualiza
sozinha quando a tarefa ativa muda. Com várias conversas na mesma máquina, ela
mostra a última tarefa iniciada em qualquer uma delas.

## Alterações do agente

O hook do YABook guarda a versão de cada arquivo antes da primeira edição do
agente na sessão. A extensão abre essas alterações em uma única aba de diff, com
cada arquivo expansível e recolhível:

- `$yabook diff` no agente abre a última rodada (o que mudou desde a sua última
  mensagem); `$yabook diff sessao`, a sessão inteira;
- `YABook: Ver alterações da última rodada` e `YABook: Ver alterações da última
  sessão` fazem o mesmo pela paleta e pela visão **Ajuda e atalhos**;
- `YABook: Escolher sessão de diff` lista sessões anteriores;
- a visão **Alterações do agente**, na barra lateral YABook, lista as sessões e,
  em cada uma, **Sessão inteira** e as rodadas com horário e o início da
  mensagem; clicar em um arquivo abre o diff só dele.

## Explicação dos blocos

Com `$yabook diff explain [arquivo]`, o agente escreve uma explicação curta
para cada bloco do diff. A extensão mostra cada explicação como comentário
ancorado no bloco, no diff e no editor comum. `YABook: Navegar pelas
explicações do diff` lista os blocos e abre cada um; `YABook: Ocultar
explicações do diff` remove os comentários da tela. Se o arquivo mudar depois
da explicação, o comentário avisa que a posição pode ter se deslocado.

A cópia anterior mantém a extensão do arquivo, então o VS Code aplica a mesma
linguagem e encoding (por exemplo, fontes ABL em ISO-8859-1).

## Comandos

A visão **Comandos** lista os comandos do YABook lidos da ajuda da versão
instalada, agrupados como no `$yabook help`. Clicar em um comando abre uma aba
com a página dele (o que faz, quando usar, se altera algo, sintaxe, exemplos e
relacionados), que vem do próprio plugin em `references/help/comandos/`. O
ícone ao lado do comando copia `$yabook <comando>`, e `YABook: Explicar um
comando do YABook` procura qualquer comando pela paleta.

## Ajuda e atalhos

A visão **Ajuda e atalhos** abre:

- o site do YABook Tasks (`task board --serve`, porta `tasks.port` ou 8765);
- o mapa de memória (`memory map --serve`, porta 8766 por padrão);
- a ajuda completa (`help.md`) em pré-visualização.

Se o servidor não estiver rodando, a extensão o inicia em um terminal próprio
(fechar o terminal encerra) e abre o navegador quando ele responder. Os scripts
são localizados por `yabook.scriptsDir` ou, sem ela, pela sessão de diff mais
recente, pelo plugin do Claude ou pela cópia mais nova em
`~/.local/share/yabook/plugins`.

## Tema YA LABS

A extensão traz os temas **YA LABS Escuro** e **YA LABS Claro**
(`Preferences: Color Theme`), com o azul escuro da marca nas superfícies. O
realce de sintaxe e o contraste seguem o Night Owl sem itálico (Light Owl na
variante clara): base fria em tons pastel (azul, turquesa, verde-claro e roxo) e
acentos quentes suaves em strings e números. O laranja da marca, suavizado,
aparece só onde o Night Owl usa o roxo de destaque: botões, contadores e a marca
da aba e da visão ativas. Os arquivos em
`themes/` são gerados por `python3 apps/vscode/scripts/themes.py`; edite a
paleta no script, não o JSON.

## Instalação

Cada versão é publicada nas [releases do YABook](https://github.com/ya-labs/YABook/releases)
com a tag `vscode-v<versão>` e o `.vsix` anexado. Para instalar a partir da release:

```bash
gh release download vscode-v<versão> -R ya-labs/YABook -p 'yabook-*.vsix'
code --install-extension yabook-<versão>.vsix
```

Ou baixe o `.vsix` pela página da release e use **Extensões → ... → Install from
VSIX**. A partir do checkout, sem release:

```bash
code --install-extension "$(npm run -s vscode:package)"
```

Depois, recarregue a janela (`Developer: Reload Window`). Atualizar é instalar a
versão nova do mesmo jeito.

## Publicar uma versão

Suba `version` em `apps/vscode/package.json` no PR da mudança. Depois do merge,
na `main` atualizada e sem alterações locais:

```bash
npm run vscode:release -- --notas <arquivo-com-o-que-mudou.md>
```

O script recusa commit fora da `origin/main` e tag já publicada; `--dry-run`
mostra a tag, o título e o corpo sem publicar.

## Configuração

- `yabook.diffsDir`: pasta das sessões; vazio usa `YABOOK_DIFFS` ou
  `~/.config/yabook/diffs`;
- `yabook.scriptsDir`, `yabook.python`, `yabook.tasksPort` e
  `yabook.memoryMapPort`: localização do YABook e portas dos atalhos.

## Desenvolvimento

JavaScript sem dependências nem build. Testes da lógica: `npm run vscode:test`.
