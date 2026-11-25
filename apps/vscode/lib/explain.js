'use strict';
// Explicações dos blocos (explain.json, gravado por `yabook_diff.py explain`) e onde ancorar cada uma.
const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const sessions = require('./sessions');

function load(session) {
  try {
    const data = JSON.parse(fs.readFileSync(path.join(session.pasta, 'explain.json'), 'utf8'));
    return Array.isArray(data.blocos) ? data : null;
  } catch (error) {
    return null;
  }
}

function digest(file) {
  try {
    return crypto.createHash('sha1').update(fs.readFileSync(file)).digest('hex');
  } catch (error) {
    return null;
  }
}

// Linhas em base 0. Bloco com linhas atuais ancora no arquivo atual; arquivo removido, na cópia anterior;
// remoção dentro de arquivo que continua existindo ancora na linha atual seguinte ao trecho removido.
function anchor(session, block) {
  const [beforeStart, beforeCount] = block.antes;
  const [afterStart, afterCount] = block.depois;
  if (block.estado === 'removido') {
    const item = session.arquivos.find((a) => a.caminho === block.arquivo);
    const file = item && item.antes ? path.join(session.pasta, item.antes) : null;
    const start = Math.max(beforeStart - 1, 0);
    return file && { file, side: 'antes', start, end: start + Math.max(beforeCount - 1, 0), stale: false };
  }
  const file = sessions.target(session, block.arquivo);
  const last = Math.max(lineCount(file) - 1, 0);
  const start = Math.min(Math.max(afterStart - 1, 0), last);
  const end = Math.min(afterCount > 0 ? start + afterCount - 1 : start, last);
  return { file, side: 'depois', start, end, stale: Boolean(block.assinatura) && digest(file) !== block.assinatura };
}

function lineCount(file) {
  try {
    const text = fs.readFileSync(file, 'latin1');
    return text.split('\n').length - (text.endsWith('\n') ? 1 : 0);
  } catch (error) {
    return 0;
  }
}

function body(block, place) {
  const counts = `−${block.antes[1]} +${block.depois[1]}`;
  const warning = place.stale ? '\n\n_Arquivo alterado depois da explicação: a posição pode estar deslocada._' : '';
  const removed = block.depois[1] === 0 && block.estado !== 'removido' ? ' · trecho removido acima' : '';
  return `**${block.id}** · ${counts}${removed}\n\n${block.texto}${warning}`;
}

function anchors(session) {
  const data = load(session);
  if (!data) return [];
  return data.blocos.map((block) => ({ block, place: anchor(session, block) })).filter((row) => row.place)
    .map(({ block, place }) => ({ id: block.id, arquivo: block.arquivo, texto: block.texto, ...place, markdown: body(block, place) }));
}

module.exports = { load, anchor, anchors, body };
