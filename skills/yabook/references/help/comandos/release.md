# `$yabook release`

Gera a descrição da release no padrão YA LABS e orienta a tag quando aplicável.
O título segue `Publicar versão x.y.z`.

## Quando usar

- Um conjunto de mudanças foi integrado e vai virar versão.
- Você quer o texto da release a partir de issue, diff e commits.
- Precisa revisar como `main`, `dev` e `release/x.y.z` se encaixam.

## Altera alguma coisa?

`release` é somente leitura e devolve texto. Criar ou publicar a release exige
`do release` (ou pedido explícito). Em `mode: auto`, a release só entra quando
fizer parte do pedido. A tag aponta para o commit integrado na branch principal.

O corpo traz objetivo, entrega, issue, mudanças, validações e observações.
`main` guarda o estado estável; `dev` representa o ciclo atual e, após a
release, uma nova `dev` parte da `main`; `release/x.y.z` serve para homologação
ou ajustes finais. PR de release usa o mesmo título `Publicar versão x.y.z`.

## Sintaxe

```text
$yabook release
$yabook do release
```

- `release`: prévia do título e do corpo.
- `do release`: executa a release aprovada.

## Exemplos

```text
$yabook release
$yabook do release
$yabook help preparar uma release
```

- `release`: propõe `Publicar versão 1.4.0` com o resumo das mudanças.
- `do release`: executa a release aprovada, com a tag no commit integrado.
- `help preparar uma release`: recomenda a sequência de comandos para o objetivo.

## Contrato

Título:

```text
Publicar versão x.y.z
```

Corpo com objetivo, entrega, issue, mudanças, validações e observações. A tag
aponta para o commit integrado na branch principal.

## Relacionados

- `pr`: integrar as mudanças antes da release.
- `apk`: APK com nome da versão em `release/x.y.z`.
- `do`: o que cada ação autoriza.
