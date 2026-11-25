# YABook para VS Code

Mostra no VS Code o que o YABook registra durante o trabalho do agente. A
extensão só lê o que os scripts Python do YABook geram; regras, hooks e memória
continuam no plugin.

## Alterações do agente

O hook do YABook guarda a versão de cada arquivo antes da primeira edição do
agente na sessão. A extensão abre essas alterações em uma única aba de diff, com
cada arquivo expansível e recolhível:

- `$yabook diff` no agente abre a aba da sessão mais recente;
- `YABook: Ver alterações da última sessão` faz o mesmo pela paleta;
- `YABook: Escolher sessão de diff` lista sessões anteriores;
- a visão **Alterações do agente**, na barra lateral YABook, lista sessões e
  arquivos; clicar em um arquivo abre o diff só dele.

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

## Instalação

```bash
code --install-extension "$(npm run -s vscode:package)"
```

Depois, recarregue a janela (`Developer: Reload Window`).

## Configuração

- `yabook.diffsDir`: pasta das sessões; vazio usa `YABOOK_DIFFS` ou
  `~/.config/yabook/diffs`;
- `yabook.scriptsDir`, `yabook.python`, `yabook.tasksPort` e
  `yabook.memoryMapPort`: localização do YABook e portas dos atalhos.

## Desenvolvimento

JavaScript sem dependências nem build. Testes da lógica: `npm run vscode:test`.
