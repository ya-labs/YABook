// YABook Tasks: site local sem build. Lê o estado do servidor (ou o retrato
// embutido por `task board --output`) e atualiza por SSE quando os arquivos mudam.
"use strict";

const SNAPSHOT = window.YABOOK_SNAPSHOT || null;
const TOKEN = (document.querySelector('meta[name="yabook-token"]') || {}).content || "";
const app = { estado: null, view: null, cache: {} };

// Utilidades ------------------------------------------------------------------
function h(tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (value === null || value === undefined || value === false) continue;
    if (key.startsWith("on")) node.addEventListener(key.slice(2), value);
    else if (key === "class") node.className = value;
    else node.setAttribute(key, value === true ? "" : value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

function fmtDate(iso) {
  if (!iso) return "";
  const [y, m, d] = iso.slice(0, 10).split("-");
  return `${d}/${m}${y !== app.estado?.hoje?.slice(0, 4) ? "/" + y.slice(2) : ""}`;
}

function daysUntil(iso) {
  const today = new Date(app.estado.hoje + "T00:00:00");
  return Math.round((new Date(iso + "T00:00:00") - today) / 86400000);
}

async function api(path) {
  if (SNAPSHOT) {
    const key = path.split("?")[0].replace("/api/", "");
    const map = { estado: SNAPSHOT.estado, semana: SNAPSHOT.semana, ficha: SNAPSHOT.ficha, historico: SNAPSHOT.historico };
    if (key in map) return map[key];
    if (key.startsWith("tarefa/")) return snapshotTask(decodeURIComponent(key.slice(7)));
    throw new Error("Indisponível na cópia estática");
  }
  const response = await fetch(path, { headers: { Accept: "application/json" } });
  const body = await response.json();
  if (!response.ok) throw new Error(body.error || response.statusText);
  return body;
}

function snapshotTask(id) {
  const resumo = app.estado.tarefas.find((t) => t.id === id);
  return { data: resumo, body: "", resumo, referencias: {}, filhos: app.estado.tarefas.filter((t) => t.pai === id) };
}

// Componentes compartilhados --------------------------------------------------
function label(tipo) {
  return (app.estado.rotulos || {})[tipo] || tipo;
}

function columnName(id) {
  const column = app.estado.colunas.find((c) => c.id === id);
  return column ? column.nome : id;
}

function badges(task) {
  const items = [];
  if (task.nivel) items.push(h("span", { class: "selo nivel" }, task.nivel === "epico" ? "épico" : task.nivel === "historia" ? "história" : "tarefa"));
  if (task.codigo) items.push(h("span", { class: "selo", title: "Código" }, task.codigo));
  if (task.pessoal) items.push(h("span", { class: "selo pessoal", title: "Sem numeração da empresa" }, "pessoal"));
  if (task.prazo && !["concluido", "arquivado"].includes(task.papel)) {
    const days = daysUntil(task.prazo);
    const cls = days < 0 ? "selo atrasado" : days <= 2 ? "selo prazo" : "selo";
    items.push(h("span", { class: cls, title: "Prazo" }, "⏱ " + fmtDate(task.prazo)));
  }
  if (task.perguntas_abertas) items.push(h("span", { class: "selo pergunta" }, `? ${task.perguntas_abertas}`));
  if (task.confidencial === "disponivel") items.push(h("span", { class: "selo", title: "Referência confidencial disponível nesta máquina" }, "🔓 confidencial"));
  if (task.confidencial === "bloqueado") items.push(h("span", { class: "selo bloqueado", title: "Base confidencial ausente nesta máquina" }, "🔒 confidencial"));
  return items;
}

function card(task) {
  return h("button", { class: "card", type: "button", "data-id": task.id, onclick: () => openTask(task.id) },
    h("span", { class: "titulo" }, task.titulo),
    h("span", { class: "linha" }, badges(task)),
    task.proximo_passo ? h("span", { class: "passo" }, "→ " + task.proximo_passo) : null);
}

async function openTask(id) {
  const panel = document.getElementById("painel");
  panel.hidden = false;
  panel.replaceChildren(h("p", { class: "vazio" }, "Carregando…"));
  try {
    const detail = await api("/api/tarefa/" + encodeURIComponent(id));
    const data = detail.data;
    const parent = data.pai ? app.estado.tarefas.find((t) => t.id === data.pai) : null;
    panel.replaceChildren(
      h("button", { class: "botao fechar", type: "button", onclick: closePanel }, "Fechar"),
      h("h2", {}, data.titulo),
      h("div", { class: "linha card", style: "cursor:default" }, h("span", { class: "linha" }, badges(detail.resumo))),
      h("p", {}, `${label(data.tipo)} · ${columnName(data.coluna)} · ${data.id}`),
      parent ? h("p", {}, "Faz parte de ", h("a", { href: "#", onclick: (e) => { e.preventDefault(); openTask(parent.id); } }, parent.titulo)) : null,
      data.proximo_passo ? h("p", {}, h("strong", {}, "Próximo passo: "), data.proximo_passo) : null,
      (data.issue || []).length ? h("p", {}, "Issues: ", data.issue.join(", ")) : null,
      detail.filhos && detail.filhos.length ? [h("h2", {}, "Itens"), h("div", { class: "grade" }, detail.filhos.map(card))] : null,
      detail.body ? [h("h2", {}, "Registro"), h("pre", { class: "registro" }, detail.body.trim())] : null,
      detail.complemento ? [h("h2", {}, "Complemento confidencial (local)"), h("pre", { class: "registro" }, detail.complemento.trim())] : null,
      Object.entries(detail.referencias || {}).map(([ref, text]) =>
        [h("h2", {}, ref), text ? h("pre", { class: "registro" }, text.trim()) : h("p", { class: "vazio" }, "🔒 Bloqueado: base confidencial ausente nesta máquina.")]),
      detail.confidencial === "bloqueado" && !Object.keys(detail.referencias || {}).length
        ? h("p", { class: "vazio" }, "🔒 Complemento confidencial só na máquina que possui a base.") : null,
    );
  } catch (error) {
    panel.replaceChildren(h("button", { class: "botao fechar", type: "button", onclick: closePanel }, "Fechar"), h("p", { class: "aviso erro" }, error.message));
  }
}

function closePanel() {
  document.getElementById("painel").hidden = true;
}

// Visões ------------------------------------------------------------------------
// Cada visão: { titulo, render(estado) -> Node | Promise<Node> }.
const VIEWS = {
  resumo: {
    titulo: "Resumo",
    render(estado) {
      const byColumn = estado.colunas.map((c) => ({ ...c, total: estado.tarefas.filter((t) => t.coluna === c.id).length }));
      return h("section", {},
        h("h2", {}, "Colunas"),
        h("div", { class: "numeros" }, byColumn.map((c) => h("div", { class: "numero" }, h("b", {}, c.total), h("span", {}, c.nome)))),
        h("h2", {}, "Épicos"),
        estado.epicos.length ? h("div", { class: "grade" }, estado.epicos.map(card)) : h("p", { class: "vazio" }, "Nenhum épico."),
      );
    },
  },
};
const ORDER = ["resumo"];

function currentView() {
  const name = location.hash.replace("#", "");
  return VIEWS[name] ? name : ORDER[0];
}

function renderTabs() {
  const nav = document.getElementById("abas");
  const current = currentView();
  nav.replaceChildren(...ORDER.map((name) =>
    h("button", { type: "button", "aria-current": name === current ? "page" : null, onclick: () => { location.hash = name; } }, VIEWS[name].titulo)));
}

async function render() {
  if (!app.estado) return;
  renderTabs();
  const main = document.getElementById("conteudo");
  try {
    const node = await VIEWS[currentView()].render(app.estado);
    main.replaceChildren(node);
  } catch (error) {
    main.replaceChildren(h("p", { class: "aviso erro" }, error.message));
  }
}

async function refresh() {
  try {
    app.estado = await api("/api/estado");
    app.cache = {};
    document.getElementById("maquina").textContent = (app.estado.maquina || "") + (SNAPSHOT ? " · cópia estática" : "");
    await render();
  } catch (error) {
    document.getElementById("conteudo").replaceChildren(h("p", { class: "aviso erro" }, "Falha ao ler as tarefas: " + error.message));
  }
}

function listen() {
  const dot = document.getElementById("conexao");
  if (SNAPSHOT || !window.EventSource) return;
  const source = new EventSource("/api/stream");
  source.addEventListener("pronto", () => { dot.className = "ponto vivo"; dot.title = "Atualização automática ativa"; });
  source.addEventListener("mudou", () => { if (!app.editando) refresh(); else app.pendente = true; });
  source.onerror = () => { dot.className = "ponto offline"; dot.title = "Servidor indisponível; tentando reconectar"; };
}

window.addEventListener("hashchange", render);
document.addEventListener("keydown", (event) => { if (event.key === "Escape") closePanel(); });
document.addEventListener("DOMContentLoaded", () => {
  refresh();
  listen();
  if (!SNAPSHOT && "serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
});
