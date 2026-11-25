'use strict';
const assert = require('node:assert/strict');
const fs = require('fs');
const http = require('http');
const os = require('os');
const path = require('path');
const test = require('node:test');
const yabook = require('../lib/yabook');

function scripts(root) {
  fs.mkdirSync(root, { recursive: true });
  fs.writeFileSync(path.join(root, 'yabook_tasks.py'), '');
  return root;
}

test('findScripts segue configuração, sessão, plugin do Claude e cópia mais nova', () => {
  const home = fs.mkdtempSync(path.join(os.tmpdir(), 'yabook-home-'));
  assert.equal(yabook.findScripts('', [], home), null);
  const old = scripts(path.join(home, '.local/share/yabook/plugins/a/skills/yabook/scripts'));
  const recent = scripts(path.join(home, '.local/share/yabook/plugins/b/skills/yabook/scripts'));
  fs.utimesSync(path.join(old, 'yabook_tasks.py'), new Date(2020, 1, 1), new Date(2020, 1, 1));
  assert.equal(yabook.findScripts('', [], home), recent);
  const claude = scripts(path.join(home, '.local/share/yabook/claude-marketplace/plugins/yabook/skills/yabook/scripts'));
  assert.equal(yabook.findScripts('', [], home), claude);
  assert.equal(yabook.findScripts('', [{ scripts: old }], home), old);
  assert.equal(yabook.findScripts(recent, [{ scripts: old }], home), recent);
  assert.equal(yabook.findScripts('/nao/existe', [], home), claude);
});

test('parseHelp lê os grupos do índice geral', () => {
  const markdown = '# Help\n\n## Índice geral\n\n- contexto: `load`, `status`;\n- revisão: `diff`, `diff explain [arquivo]` (alterações);\n- sem comando\n\nPara tópico...\n\n## Outra\n- x: `nao`';
  assert.deepEqual(yabook.parseHelp(markdown), [
    { grupo: 'contexto', comandos: ['load', 'status'] },
    { grupo: 'revisão', comandos: ['diff', 'diff explain [arquivo]'] },
  ]);
  assert.deepEqual(yabook.parseHelp('sem índice'), []);
});

test('tasksPort usa tasks.port ou o padrão', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yabook-cfg-'));
  const file = path.join(dir, 'config.json');
  assert.equal(yabook.tasksPort(file), 8765);
  assert.equal(yabook.memoryRoot(file), null);
  fs.writeFileSync(file, JSON.stringify({ tasks: { port: 9100 }, memory_root: '/m' }));
  assert.equal(yabook.tasksPort(file), 9100);
  assert.equal(yabook.memoryRoot(file), '/m');
});

test('serving detecta servidor ativo e porta livre', async () => {
  const server = http.createServer((req, res) => res.end('ok'));
  await new Promise((done) => server.listen(0, '127.0.0.1', done));
  const { port } = server.address();
  assert.equal(await yabook.serving(port), true);
  await new Promise((done) => server.close(done));
  assert.equal(await yabook.serving(port), false);
});
