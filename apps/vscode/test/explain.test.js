'use strict';
const assert = require('node:assert/strict');
const crypto = require('crypto');
const fs = require('fs');
const os = require('os');
const path = require('path');
const test = require('node:test');
const explain = require('../lib/explain');

function fixture() {
  const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'yabook-explain-'));
  const project = path.join(tmp, 'projeto');
  const pasta = path.join(tmp, 'diffs', 'p', 's1');
  fs.mkdirSync(path.join(pasta, 'antes'), { recursive: true });
  fs.mkdirSync(project);
  fs.writeFileSync(path.join(project, 'tela.p'), 'a\nB\nd\n');
  fs.writeFileSync(path.join(pasta, 'antes', 'velho.txt'), 'x\ny\n');
  const sign = crypto.createHash('sha1').update(fs.readFileSync(path.join(project, 'tela.p'))).digest('hex');
  const session = {
    projeto: project, pasta,
    arquivos: [{ caminho: 'tela.p', antes: 'antes/tela.p' }, { caminho: 'velho.txt', antes: 'antes/velho.txt' }],
  };
  fs.writeFileSync(path.join(pasta, 'explain.json'), JSON.stringify({
    versao: 1, sessao: 's1', blocos: [
      { id: 'b1', arquivo: 'tela.p', estado: 'alterado', antes: [2, 2], depois: [2, 1], texto: 'Troca.', assinatura: sign },
      { id: 'b2', arquivo: 'tela.p', estado: 'alterado', antes: [5, 1], depois: [4, 0], texto: 'Remove.', assinatura: 'outra' },
      { id: 'b3', arquivo: 'velho.txt', estado: 'removido', antes: [1, 2], depois: [1, 0], texto: 'Apaga.', assinatura: null },
    ],
  }));
  return { session, project, pasta };
}

test('ancora no arquivo atual, na cópia anterior para removido e marca posição desatualizada', () => {
  const { session, project, pasta } = fixture();
  const [changed, deletion, removed] = explain.anchors(session);
  assert.deepEqual([changed.file, changed.side, changed.start, changed.end, changed.stale], [path.join(project, 'tela.p'), 'depois', 1, 1, false]);
  assert.deepEqual([deletion.start, deletion.end, deletion.stale], [2, 2, true]); // remoção no fim: última linha
  assert.match(deletion.markdown, /trecho removido acima/);
  assert.match(deletion.markdown, /posição pode estar deslocada/);
  assert.deepEqual([removed.file, removed.side, removed.start, removed.end], [path.join(pasta, 'antes', 'velho.txt'), 'antes', 0, 1]);
  assert.match(changed.markdown, /^\*\*b1\*\* · −2 \+1\n\nTroca\.$/);
});

test('sessão sem explain.json não tem âncoras', () => {
  const { session, pasta } = fixture();
  fs.unlinkSync(path.join(pasta, 'explain.json'));
  assert.deepEqual(explain.anchors(session), []);
});
