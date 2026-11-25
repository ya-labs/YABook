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

test('visões por rodada: última, sessão inteira e rodada antiga até a seguinte', () => {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'yabook-rodadas-'));
  const project = path.join(tmp, 'p'); const pasta = path.join(tmp, 'd');
  fs.mkdirSync(project); fs.mkdirSync(path.join(pasta, 'antes'), { recursive: true });
  fs.mkdirSync(path.join(pasta, 'rodadas/1/antes'), { recursive: true }); fs.mkdirSync(path.join(pasta, 'rodadas/2/antes'), { recursive: true });
  fs.writeFileSync(path.join(pasta, 'antes/a.txt'), 'um\n');
  fs.writeFileSync(path.join(pasta, 'rodadas/1/antes/a.txt'), 'um\n');
  fs.writeFileSync(path.join(pasta, 'rodadas/2/antes/a.txt'), 'dois\n');
  fs.writeFileSync(path.join(project, 'a.txt'), 'tres\n');
  fs.writeFileSync(path.join(project, 'b.txt'), 'novo\n');
  const session = { projeto: project, pasta,
    arquivos: [{ caminho: 'a.txt', antes: 'antes/a.txt' }, { caminho: 'b.txt', antes: null }],
    rodadas: [
      { numero: 1, arquivos: [{ caminho: 'a.txt', antes: 'rodadas/1/antes/a.txt' }] },
      { numero: 2, arquivos: [{ caminho: 'a.txt', antes: 'rodadas/2/antes/a.txt' }, { caminho: 'b.txt', antes: null }] },
    ] };
  assert.equal(sessions.viewItems(session, 'ultima').key, 'rodada-2');
  assert.deepEqual(sessions.changes(session, 'ultima').map((c) => c.caminho), ['a.txt', 'b.txt']);
  assert.deepEqual(sessions.changes(session, 'sessao').map((c) => [c.caminho, c.estado]), [['a.txt', 'alterado'], ['b.txt', 'novo']]);
  const [first] = sessions.changes(session, 1);
  assert.equal(fs.readFileSync(first.depois, 'utf8'), 'dois\n'); // rodada 1 termina onde a 2 começou
  assert.equal(sessions.viewArg('rodada-2'), 2);
  assert.equal(sessions.viewArg('sessao'), 'sessao');
  assert.equal(sessions.viewItems({ arquivos: [] }, 'ultima').key, 'sessao'); // sessão antiga, sem rodadas
});

test('rótulo da sessão: nome do chat, senão primeira mensagem, senão projeto e data', () => {
  const base = { projeto: '/p/YABook', atualizada: '2026-11-25T11:28:00-03:00', arquivos: [] };
  assert.equal(sessions.label({ ...base, titulo: 'Visualização de diffs no yabook' }), 'Visualização de diffs no yabook');
  assert.equal(sessions.label({ ...base, rodadas: [{ numero: 1, pedido: 'crie o tema' }] }), 'crie o tema');
  assert.equal(sessions.label(base), 'YABook · 25/11 11:28');
  assert.equal(sessions.when(base), '25/11 11:28');
});
