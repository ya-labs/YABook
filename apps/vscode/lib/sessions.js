'use strict';
// Leitura das sessões de diff gravadas pelo hook do YABook (diff_runtime). Sem dependência do VS Code.
const fs = require('fs');
const os = require('os');
const path = require('path');

const OUTSIDE = '_externos/';

function defaultBase(setting, env = process.env) {
  if (setting) return expand(setting);
  if (env.YABOOK_DIFFS) return expand(env.YABOOK_DIFFS);
  const config = env.YABOOK_CONFIG ? expand(env.YABOOK_CONFIG) : path.join(os.homedir(), '.config', 'yabook', 'config.json');
  return path.join(path.dirname(config), 'diffs');
}

function expand(value) {
  return value.startsWith('~') ? path.join(os.homedir(), value.slice(1)) : value;
}

function readManifest(file) {
  try {
    const data = JSON.parse(fs.readFileSync(file, 'utf8'));
    return data && Array.isArray(data.arquivos) ? Object.assign(data, { manifesto: file, pasta: path.dirname(file) }) : null;
  } catch (error) {
    return null;
  }
}

// Todas as sessões, da atualizada mais recentemente para a mais antiga.
function listSessions(base) {
  const found = [];
  for (const project of safeDir(base)) {
    for (const session of safeDir(path.join(base, project))) {
      const data = readManifest(path.join(base, project, session, 'manifest.json'));
      if (data) found.push(data);
    }
  }
  return found.sort((a, b) => String(b.atualizada).localeCompare(String(a.atualizada)));
}

function safeDir(folder) {
  try {
    return fs.readdirSync(folder, { withFileTypes: true }).filter((e) => e.isDirectory()).map((e) => e.name);
  } catch (error) {
    return [];
  }
}

function within(child, parent) {
  const rel = path.relative(parent, child);
  return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel));
}

// Sessão pertence ao workspace quando o projeto contém a pasta aberta ou está dentro dela.
function forWorkspace(sessions, folders) {
  return sessions.filter((s) => folders.some((f) => within(f, s.projeto) || within(s.projeto, f)));
}

function target(session, rel) {
  return rel.startsWith(OUTSIDE) ? '/' + rel.slice(OUTSIDE.length) : path.join(session.projeto, rel);
}

function read(file) {
  try {
    return fs.readFileSync(file);
  } catch (error) {
    return null;
  }
}

// Arquivos alterados: antes (cópia guardada ou null se novo) e depois (atual ou null se removido).
function changes(session) {
  const result = [];
  for (const item of session.arquivos) {
    const before = item.antes ? path.join(session.pasta, item.antes) : null;
    const after = target(session, item.caminho);
    const old = before ? read(before) : null;
    const now = read(after);
    if (old === null && now === null) continue;
    if (old !== null && now !== null && old.equals(now)) continue;
    const estado = old === null ? 'novo' : now === null ? 'removido' : 'alterado';
    result.push({ caminho: item.caminho, estado, antes: old === null ? null : before, depois: now === null ? null : after });
  }
  return result;
}

function label(session) {
  const when = String(session.atualizada || '').replace('T', ' ').slice(0, 16);
  return `${path.basename(session.projeto)} · ${when}`;
}

module.exports = { defaultBase, listSessions, forWorkspace, changes, label, readManifest, target };
