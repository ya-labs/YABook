'use strict';
// Localiza o YABook instalado, lê a ajuda da versão instalada e verifica servidores locais.
const fs = require('fs');
const http = require('http');
const os = require('os');
const path = require('path');

const MARKER = 'yabook_tasks.py';

function isScripts(dir) {
  return Boolean(dir) && fs.existsSync(path.join(dir, MARKER));
}

// Ordem: configuração, pasta registrada pela sessão de diff mais recente, plugin do Claude, cópia mais nova.
function findScripts(setting, sessionsList = [], home = os.homedir()) {
  const candidates = [setting, ...sessionsList.map((s) => s.scripts),
    path.join(home, '.local/share/yabook/claude-marketplace/plugins/yabook/skills/yabook/scripts')];
  const found = candidates.find(isScripts);
  if (found) return found;
  const pool = path.join(home, '.local/share/yabook/plugins');
  let newest = null;
  for (const name of safeList(pool)) {
    const dir = path.join(pool, name, 'skills/yabook/scripts');
    if (!isScripts(dir)) continue;
    const time = fs.statSync(path.join(dir, MARKER)).mtimeMs;
    if (!newest || time > newest.time) newest = { dir, time };
  }
  return newest ? newest.dir : null;
}

function safeList(dir) {
  try {
    return fs.readdirSync(dir);
  } catch (error) {
    return [];
  }
}

function helpFile(scripts) {
  return scripts ? path.join(scripts, '..', 'references', 'help.md') : null;
}

// Grupos do "Índice geral" da ajuda: "- grupo: `cmd`, `cmd`;" vira {grupo, comandos}.
function parseHelp(markdown) {
  const section = /## Índice geral\n([\s\S]*?)(?:\n## |$)/.exec(markdown);
  if (!section) return [];
  // Só a lista logo abaixo do título: o texto seguinte pode ter outras listas.
  const lines = section[1].replace(/^\s*\n/, '').split('\n');
  const end = lines.findIndex((line) => !line.startsWith('- '));
  const list = end === -1 ? lines : lines.slice(0, end);
  return list.map((line) => /^- ([^:]+):\s*(.*)$/.exec(line.trim())).filter(Boolean)
    .map(([, grupo, rest]) => ({ grupo: grupo.trim(), comandos: [...rest.matchAll(/`([^`]+)`/g)].map((m) => m[1]) }))
    .filter((group) => group.comandos.length);
}

function readConfig(configFile) {
  try {
    return JSON.parse(fs.readFileSync(configFile, 'utf8'));
  } catch (error) {
    return {};
  }
}

// Página do comando: primeiro termo sem `do` ("do sync" e "sync" usam sync.md; "diff explain" usa diff.md).
function commandKey(token) {
  const words = token.trim().split(/\s+/);
  const rest = words[0] === 'do' && words.length > 1 ? words.slice(1) : words;
  return rest[0].split('|')[0].replace(/[^a-z0-9-]/gi, '').toLowerCase();
}

function commandPage(scripts, token) {
  return scripts ? path.join(scripts, '..', 'references', 'help', 'comandos', commandKey(token) + '.md') : null;
}

function tasksPort(configFile, fallback = 8765) {
  const port = (readConfig(configFile).tasks || {}).port;
  return Number.isInteger(port) ? port : fallback;
}

function memoryRoot(configFile) {
  const root = readConfig(configFile).memory_root;
  return typeof root === 'string' && root ? root : null;
}

function serving(port, host = '127.0.0.1', timeout = 600) {
  return new Promise((resolve) => {
    const request = http.get({ host, port, path: '/', timeout }, (response) => {
      response.resume();
      resolve(true);
    });
    request.on('timeout', () => request.destroy());
    request.on('error', () => resolve(false));
  });
}

async function waitServing(port, attempts = 20, delay = 300) {
  for (let i = 0; i < attempts; i += 1) {
    if (await serving(port)) return true;
    await new Promise((done) => setTimeout(done, delay));
  }
  return false;
}

module.exports = { findScripts, helpFile, parseHelp, commandKey, commandPage, tasksPort, memoryRoot, serving, waitServing };
