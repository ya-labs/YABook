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

## Instalação

```bash
code --install-extension "$(npm run -s vscode:package)"
```

Depois, recarregue a janela (`Developer: Reload Window`).

## Configuração

- `yabook.diffsDir`: pasta das sessões; vazio usa `YABOOK_DIFFS` ou
  `~/.config/yabook/diffs`.

## Desenvolvimento

JavaScript sem dependências nem build. Testes da lógica: `npm run vscode:test`.
