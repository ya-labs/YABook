# YABook Desktop

Base local do aplicativo desktop do YABook, construída com Tauri, React e
TypeScript.

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
