'use strict';
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const test = require('node:test');
const sessions = require('../lib/sessions');

function fixture() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'yabook-vscode-'));
  const project = path.join(tmp, 'projeto');
  const folder = path.join(tmp, 'diffs', 'projeto-abc', 's1');
  fs.mkdirSync(path.join(folder, 'antes', 'src'), { recursive: true });
  fs.mkdirSync(path.join(project, 'src'), { recursive: true });
  const write = (file, text) => fs.writeFileSync(file, Buffer.from(text, 'latin1'));
  write(path.join(folder, 'antes', 'src', 'tela.p'), 'ação antiga\n');
  write(path.join(project, 'src', 'tela.p'), 'ação nova\n');
  write(path.join(folder, 'antes', 'igual.txt'), 'x\n');
  write(path.join(project, 'igual.txt'), 'x\n');
  write(path.join(project, 'novo.md'), 'novo\n');
  write(path.join(folder, 'antes', 'apagado.js'), 'velho\n');
  const manifest = {
    versao: 1, projeto: project, agente: 'claude', sessao: 's1', criada: '2026-11-25T08:00:00-03:00',
    atualizada: '2026-11-25T09:00:00-03:00',
    arquivos: [
      { caminho: 'src/tela.p', antes: 'antes/src/tela.p', novo: false },
      { caminho: 'igual.txt', antes: 'antes/igual.txt', novo: false },
      { caminho: 'novo.md', antes: null, novo: true },
      { caminho: 'apagado.js', antes: 'antes/apagado.js', novo: false },
    ],
  };
  fs.writeFileSync(path.join(folder, 'manifest.json'), JSON.stringify(manifest));
  const older = path.join(tmp, 'diffs', 'outro-def', 's0');
  fs.mkdirSync(older, { recursive: true });
  fs.writeFileSync(path.join(older, 'manifest.json'), JSON.stringify({ ...manifest, projeto: '/outro', sessao: 's0', atualizada: '2026-11-20T09:00:00-03:00', arquivos: [] }));
  return { tmp, project, base: path.join(tmp, 'diffs') };
}

test('lista sessões da mais recente e filtra pelo workspace', () => {
  const { base, project } = fixture();
  const all = sessions.listSessions(base);
  assert.deepEqual(all.map((s) => s.sessao), ['s1', 's0']);
  assert.deepEqual(sessions.forWorkspace(all, [path.join(project, 'src')]).map((s) => s.sessao), ['s1']);
  assert.deepEqual(sessions.forWorkspace(all, ['/sem-relacao']), []);
});

test('changes ignora arquivo igual e classifica novo, removido e alterado', () => {
  const { base } = fixture();
  const [session] = sessions.listSessions(base);
  const found = sessions.changes(session);
  assert.deepEqual(found.map((c) => [c.caminho, c.estado]), [['src/tela.p', 'alterado'], ['novo.md', 'novo'], ['apagado.js', 'removido']]);
  assert.equal(found[1].antes, null);
  assert.equal(found[2].depois, null);
  assert.ok(found[0].antes.endsWith(path.join('antes', 'src', 'tela.p')));
});

test('pasta padrão segue YABOOK_DIFFS e YABOOK_CONFIG', () => {
  assert.equal(sessions.defaultBase('', { YABOOK_DIFFS: '/x/diffs' }), '/x/diffs');
  assert.equal(sessions.defaultBase('', { YABOOK_CONFIG: '/c/config.json' }), '/c/diffs');
  assert.equal(sessions.defaultBase('/definida', {}), '/definida');
});

test('manifesto inválido é ignorado', () => {
  const { base } = fixture();
  fs.mkdirSync(path.join(base, 'quebrado', 's9'), { recursive: true });
  fs.writeFileSync(path.join(base, 'quebrado', 's9', 'manifest.json'), '{');
  assert.equal(sessions.listSessions(base).length, 2);
});
