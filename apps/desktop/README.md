# YABook Desktop

Base local do aplicativo desktop do YABook, construída com Tauri, React e
TypeScript.

## Como o aplicativo funciona

```text
Interface React e TypeScript
        │
        │ solicita uma ação tipada
        ▼
Tauri
        │ encaminha somente comandos permitidos
        ▼
Núcleo Rust
        │
        ▼
Arquivos locais e banco do aplicativo
```

- **React e TypeScript** criam a interface: biblioteca, árvore documental,
  leitor e telas de configuração.
- **Tauri** abre a janela nativa do aplicativo e faz a ponte segura entre a
  interface e o núcleo local. Ele usa a WebView do sistema operacional, em vez
  de levar um navegador inteiro dentro do aplicativo.
- **Rust** concentra as ações que precisam acessar o sistema: validar caminhos,
  ler documentos, observar alterações, manter o banco local e gravar a
  configuração compartilhada após confirmação.

A interface não acessa arquivos arbitrários diretamente. Quando precisar de uma
ação local, ela chama um comando Tauri; o Rust valida o pedido, executa a ação
permitida e devolve apenas o resultado necessário.

Durante o desenvolvimento, o Vite fornece a interface localmente. No pacote
final, o frontend compilado acompanha o aplicativo, sem exigir Node.js, npm ou
Vite na máquina de quem vai usá-lo.

As decisões de arquitetura, limites de dados e distribuição estão em
[Arquitetura e distribuição do YABook Desktop](../../produto/planejamento/yabook-desktop/arquitetura-e-distribuicao.md).

## Pré-requisitos

- Node.js e npm compatíveis com as dependências do projeto;
- toolchain Rust com `cargo`, necessário para executar e empacotar o Tauri.

## Comandos

Instale as dependências do aplicativo:

```bash
npm --prefix apps/desktop install
```

Depois, na raiz do repositório:

```bash
npm run desktop:dev
npm run desktop:check
npm run desktop:build
```

`desktop:dev` inicia o Vite e o aplicativo Tauri. `desktop:build` gera o
pacote nativo; ambos exigem o Rust instalado. `desktop:check` valida somente o
TypeScript.

O scaffold ainda não implementa biblioteca, leitor, busca ou configuração
documental.
