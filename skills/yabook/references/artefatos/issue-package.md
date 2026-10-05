# `$yabook issue package`

Prepara uma issue documental para reunir entregas em uma branch e um PR.
Use o projeto e o propósito geral informados na conversa. Não exija formulário
de demandas iniciais, limites ou encerramento; pergunte só por contexto indispensável.

## Descrição estável

- Identifique o pacote no resumo e preserve sua descrição durante o trabalho.
- Não liste as demandas do documento recebido, nem copie seus pontos para
  escopo, critérios de aceite, checklist ou bloco de IA.
- Documento e pedido atual orientam o desenvolvimento; podem ser referenciados
  quando útil, sem duplicar seu conteúdo na issue.
- Novas demandas são executadas a partir dos pedidos autorizados, sem atualizar
  escopo, acrescentar pendências ou criar uma issue por entrada.
- Cada entrega tem commit documentado; o PR resume assuntos e corpos contra a
  base e confere o diff final para não declarar alterações revertidas ou removidas.
- Use merge commit para preservar esses registros. O merge do PR encerra o
  pacote; novas entregas após o encerramento entram em outro pacote.

Estrutura própria, sem `Escopo` ou `Critérios de aceite` obrigatórios:

```md
## Resumo rápido

- Tarefa: reunir ajustes e melhorias do projeto em um pacote de trabalho.
- Entrega esperada: uma branch com commits documentados e um PR consolidado.

## Observações

- A issue identifica o pacote; as entregas realizadas ficam nos commits e no PR.
```

Inclua `Informações para IA` conforme `contratos.md`, só com contexto geral
estável. Não converta os tópicos desse bloco em acompanhamento de tarefas.

## Trabalho em dupla

Uma issue e a mesma branch para os dois, trabalhando por vez. Antes de assumir,
confira branch/worktree e atualize a cópia com os commits publicados pela outra
pessoa. Ao entregar a vez, valide, faça commits documentados e publique-os.
Combine quem está executando a demanda atual e mantenha referências acessíveis
aos dois. Não edite simultaneamente a mesma branch nem descarte trabalho alheio.
Commit, atualização e publicação seguem `do` fora de `auto`; criar o pacote não
autoriza essas mutações por si só.

## Saída e criação

Retorne título, corpo, labels oficiais sugeridas e `Size (Project)`, como `issue`.
Não invente label `package`. `issue package` é prévia; `do issue package` cria
o pacote. `do issue` após prévia inequívoca de pacote mantém este contrato.
