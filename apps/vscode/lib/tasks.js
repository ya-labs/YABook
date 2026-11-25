'use strict';
// Tarefa ativa do YABook Tasks: lida de local/ativa.json; detalhes vêm do `yabook_tasks.py show`.
const fs = require('fs');
const path = require('path');

function readJson(file) {
  try {
    return JSON.parse(fs.readFileSync(file, 'utf8'));
  } catch (error) {
    return null;
  }
}

function tasksRoot(configFile) {
  const cfg = readJson(configFile) || {};
  const root = cfg.tasks && cfg.tasks.root;
  return typeof root === 'string' && root ? root : null;
}

// Última tarefa iniciada na máquina (a de cada conversa fica em local/sessoes/).
function activeId(root) {
  const data = root ? readJson(path.join(root, 'local', 'ativa.json')) : null;
  return data && typeof data.id === 'string' && data.id ? data.id : null;
}

function issueUrl(ref) {
  const match = /^([^/#\s]+)\/([^/#\s]+)#(\d+)$/.exec(ref || '');
  return match ? `https://github.com/${match[1]}/${match[2]}/issues/${match[3]}` : null;
}

function list(value) {
  return Array.isArray(value) ? value : value ? [value] : [];
}

// Página Markdown com os detalhes da tarefa, para a aba de pré-visualização.
function markdown(task) {
  const data = (task && task.data) || {};
  const rows = [
    ['Número', data.numero ? `#${data.numero}` : ''],
    ['Coluna', data.coluna],
    ['Nível', data.nivel],
    ['Pai', data.pai],
    ['Issue', list(data.issue).map((ref) => (issueUrl(ref) ? `[${ref}](${issueUrl(ref)})` : ref)).join(', ')],
    ['Demanda', data.demanda],
    ['Size', data.size],
    ['Prazo', data.prazo],
    ['Aguardando', data.aguardando],
  ].filter(([, value]) => value !== undefined && value !== null && String(value) !== '');
  const parts = [`# ${data.titulo || data.id || 'Tarefa'}`, '', '| Campo | Valor |', '| --- | --- |',
    ...rows.map(([key, value]) => `| ${key} | ${String(value).replace(/\|/g, '\\|')} |`)];
  const section = (title, text) => (text && String(text).trim() ? ['', `## ${title}`, '', String(text).trim()] : []);
  parts.push(...section('Próximo passo', data.proximo_passo));
  parts.push(...section('Descrição', data.descricao && String(data.descricao).replace(/^## /gm, '### ')));
  parts.push(...section('Relatório de conclusão', data.relatorio_conclusao && String(data.relatorio_conclusao).replace(/^## /gm, '### ')));
  parts.push(...section('Registro', task && task.body));
  return parts.join('\n') + '\n';
}

module.exports = { tasksRoot, activeId, issueUrl, markdown };
