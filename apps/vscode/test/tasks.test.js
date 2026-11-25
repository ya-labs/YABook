'use strict';
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const test = require('node:test');
const tasks = require('../lib/tasks');

test('tarefa ativa vem de tasks.root/local/ativa.json', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yabook-tasks-'));
  const config = path.join(dir, 'config.json');
  assert.equal(tasks.tasksRoot(config), null);
  fs.writeFileSync(config, JSON.stringify({ tasks: { root: path.join(dir, 'dados') } }));
  const root = tasks.tasksRoot(config);
  assert.equal(tasks.activeId(root), null);
  fs.mkdirSync(path.join(root, 'local'), { recursive: true });
  fs.writeFileSync(path.join(root, 'local', 'ativa.json'), JSON.stringify({ id: 'issue-x', desde: 'agora' }));
  assert.equal(tasks.activeId(root), 'issue-x');
});

test('markdown traz campos, issue com link, seções e escapa barras da tabela', () => {
  const page = tasks.markdown({
    data: { id: 'issue-x', titulo: 'Fazer X', numero: 148, coluna: 'andamento', issue: ['ya-labs/YABook#327'],
      proximo_passo: 'Abrir o PR', descricao: '## Resumo rápido\n\n- **Tarefa** — x', aguardando: 'a | b' },
    body: '- 25/11 — Desenvolvimento iniciado.',
  });
  assert.match(page, /^# Fazer X\n/);
  assert.match(page, /\| Issue \| \[ya-labs\/YABook#327\]\(https:\/\/github\.com\/ya-labs\/YABook\/issues\/327\) \|/);
  assert.match(page, /\| Aguardando \| a \\\| b \|/);
  assert.match(page, /## Próximo passo\n\nAbrir o PR/);
  assert.match(page, /## Descrição\n\n### Resumo rápido/); // títulos da descrição descem um nível
  assert.match(page, /## Registro\n\n- 25\/11/);
  assert.doesNotMatch(page, /Relatório de conclusão/);
  assert.equal(tasks.issueUrl('sem formato'), null);
});
