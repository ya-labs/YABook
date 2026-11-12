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
  for (const child of children.flat(Infinity)) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return node;
}

// replaceChildren não aceita listas nem nulos: achata e filtra antes.
function fill(node, ...children) {
  node.replaceChildren(...children.flat(Infinity).filter((c) => c !== null && c !== undefined && c !== false));
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
const ICONS = {
  painel: '<rect x="1.5" y="2.5" width="13" height="11" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M6 2.5v10.5M3.5 5v6" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/>',
  usuario: '<circle cx="8" cy="5" r="2.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M3 14v-1a5 5 0 0 1 10 0v1" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>',
  camadas: '<path d="m8 1.5 6.5 3.8L8 9 1.5 5.3zM2 8.5 8 12l6-3.5M2 11.5 8 15l6-3.5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" stroke-linecap="round"/>',
  tarefa: '<rect x="2.5" y="2.5" width="11" height="11" rx="2" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="m5 8 2 2 4-4" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
  seta: '<path d="M2.5 8h10M9 4.5 12.5 8 9 11.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
  editar: '<path d="m10.5 2.5 3 3M3 10l8.5-8.5 3 3L6 13l-4 1z" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>',
  copiar: '<rect x="5.5" y="5.5" width="8" height="8" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M10.5 3V2H2v8.5h1" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>',
  check: '<path d="m3 8 3 3 7-7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>',
  alerta: '<path d="m8 1.8 6.4 11.4H1.6zM8 6v3M8 11v.2" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round" stroke-linecap="round"/>',
  alvo: '<circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" stroke-width="1.3"/><circle cx="8" cy="8" r="2.8" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  laptop: '<rect x="3" y="2.5" width="10" height="8" rx="1" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M1 13h14M5 10.5 4 13m7-2.5 1 2.5" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  livro: '<path d="M8 3.2C5 1.5 2 2.5 2 2.5v11s3-1 6 .7c3-1.7 6-.7 6-.7v-11s-3-1-6 .7zm0 0v11" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>',
  filtro: '<path d="M2 3h12L9.5 8.5V13l-3-1.5v-3z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>',
  salvar: '<path d="M2 2h10l2 2v10H2zM5 2v4h6V2M5 14V9h6v5" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/>',
  desfazer: '<path d="M5.5 3 2 6.5 5.5 10M2 6.5h7a4 4 0 0 1 0 8" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
  etiqueta: '<path d="M2 2h5l7 7-5 5-7-7z" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round"/><circle cx="5" cy="5" r="1" fill="currentColor"/>',
  campos: '<path d="M2 4h12M2 12h12" stroke="currentColor" stroke-width="1.3" stroke-linecap="round"/><rect x="5" y="2" width="3" height="4" rx="1" fill="var(--bg)" stroke="currentColor" stroke-width="1.3"/><rect x="9" y="10" width="3" height="4" rx="1" fill="var(--bg)" stroke="currentColor" stroke-width="1.3"/>',
  relacoes: '<path d="M8 5v3M3 11V8h10v3" fill="none" stroke="currentColor" stroke-width="1.3"/><rect x="6" y="1" width="4" height="4" rx="1" fill="none" stroke="currentColor" stroke-width="1.3"/><rect x="1" y="11" width="4" height="4" rx="1" fill="none" stroke="currentColor" stroke-width="1.3"/><rect x="11" y="11" width="4" height="4" rx="1" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  aberto: '<circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="1.75" fill="currentColor"/>',
  fechado: '<circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="m5.25 8.25 1.9 1.9 3.6-3.9" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>',
  arquivado: '<circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="m3.6 12.4 8.8-8.8" stroke="currentColor" stroke-width="1.5"/>',
  pergunta: '<path d="M2.75 3.5h10.5v7.25H8.5L5.5 13.25v-2.5H2.75z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>',
  hoje: '<circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M3 3l1 1M12 12l1 1M3 13l1-1M12 4l1-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  quadro: '<rect x="1.75" y="2.75" width="12.5" height="10.5" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M6 2.75v10.5M10 2.75v10.5" stroke="currentColor" stroke-width="1.5"/>',
  epicos: '<path d="M2.5 3.5h11M5 8h8.5M7.5 12.5h6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="2.75" cy="8" r=".9" fill="currentColor"/><circle cx="5.25" cy="12.5" r=".9" fill="currentColor"/>',
  prazos: '<rect x="1.75" y="2.75" width="12.5" height="11.5" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M1.75 6.25h12.5M5 1v3M11 1v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  semana: '<rect x="1.75" y="1.75" width="12.5" height="12.5" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M1.75 6h12.5M6 6v8.25" stroke="currentColor" stroke-width="1.5"/>',
  ficha: '<circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 4.5V8l2.5 1.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  historico: '<path d="M2.25 8a5.75 5.75 0 1 0 1.7-4.1M2 2.25v2.5h2.5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 5v3.25l2 1.25" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  mais: '<circle cx="3" cy="8" r="1.25" fill="currentColor"/><circle cx="8" cy="8" r="1.25" fill="currentColor"/><circle cx="13" cy="8" r="1.25" fill="currentColor"/>',
  fechar: '<path d="m3.5 3.5 9 9m0-9-9 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  cadeado: '<rect x="3" y="7" width="10" height="7.25" rx="1.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5.25 7V5a2.75 2.75 0 0 1 5.5 0v2" fill="none" stroke="currentColor" stroke-width="1.5"/>',
  calendario: '<rect x="2" y="3" width="12" height="11" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 6.5h12M5.5 1.5v3M10.5 1.5v3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  repo: '<path d="M3 2.75A1.75 1.75 0 0 1 4.75 1h8.5v11.5H4.75A1.75 1.75 0 0 0 3 14.25zM3 14.25A1.75 1.75 0 0 0 4.75 16h8.5" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/>',
  sol: '<circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1v1.5M8 13.5V15M1 8h1.5M13.5 8H15M3 3l1 1M12 12l1 1M3 13l1-1M12 4l1-1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>',
  lua: '<path d="M13.5 9.5A5.75 5.75 0 0 1 6.5 2.5a5.75 5.75 0 1 0 7 7Z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>',
  auto: '<circle cx="8" cy="8" r="6.25" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M8 1.75v12.5A6.25 6.25 0 0 0 8 1.75Z" fill="currentColor"/>',
};

function icon(name, cls) {
  const span = document.createElement("span");
  span.className = "icone" + (cls ? " " + cls : "");
  span.style.display = "inline-flex";
  span.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16" aria-hidden="true">${ICONS[name] || ""}</svg>`;
  return span;
}

function label(tipo) {
  return (app.estado.rotulos || {})[tipo] || tipo;
}

function columnName(id) {
  const column = (effectiveState().colunas || []).find((c) => c.id === id);
  return column ? column.nome : id;
}

function roleOf(id) {
  const column = app.estado.colunas.find((c) => c.id === id);
  return column ? column.papel : "";
}

function pill(text, color, extra = {}) {
  return h("span", { class: `selo cor-${color || "gray"}`, title: extra.title || null }, extra.icon ? icon(extra.icon) : null, text);
}

function switchInput(text, checked, onchange) {
  return h("label", { class: "switch" }, h("input", { type: "checkbox", role: "switch", checked, onchange }),
    h("span", { class: "switch-trilho", "aria-hidden": "true" }), h("span", {}, text));
}

function issueRef(task) {
  const first = (task.issue || [])[0];
  if (!first) return null;
  const [repo, number] = first.split("#");
  return { repo: repo.split("/").pop(), number, full: first };
}

function stateIcon(task) {
  if (task.tipo === "pergunta") return icon("pergunta", "estado-pergunta");
  if (task.papel === "concluido") return icon("fechado", "estado-fechado");
  if (task.papel === "arquivado") return icon("arquivado", "estado-arquivado");
  return icon("aberto", "estado-aberto");
}

function origin(task) {
  const ref = issueRef(task);
  if (ref) return `${ref.repo} #${ref.number}`;
  const own = task.demanda ? ["demanda", task.demanda] : task.projeto && task.tipo === "projeto" ? ["projeto", task.projeto] : null;
  if (own) return `${label(own[0])} ${own[1]}`;
  return label(task.tipo);
}

const LEVEL = { epico: ["épico", "purple"], historia: ["história", "blue"], tarefa: ["tarefa", "gray"] };

function badges(task, options = {}) {
  const items = [];
  if (options.status) items.push(h("span", { class: "selo neutro forte", title: "Status" }, h("span", { class: `status papel-${task.papel}` }), columnName(task.coluna)));
  if (task.nivel && !options.semNivel) items.push(pill(LEVEL[task.nivel][0], LEVEL[task.nivel][1]));
  const ref = issueRef(task);
  if (task.codigo && (!ref || task.codigo !== ref.full) && !options.semCodigo) {
    items.push(pill(task.codigo, "blue", { title: task.pessoal ? "Código" : "Código na ficha", icon: "repo" }));
  }
  if (task.pessoal && !options.semPessoal) items.push(pill("pessoal", "pink", { title: "Sem numeração da empresa" }));
  if (task.prazo && !CLOSED.includes(task.papel)) {
    const days = daysUntil(task.prazo);
    items.push(pill(fmtDate(task.prazo), days < 0 ? "red" : days <= 2 ? "orange" : "gray", { icon: "calendario", title: "Prazo" }));
  }
  if (task.aguardando && !CLOSED.includes(task.papel)) items.push(waitingPill(task));
  if (task.perguntas_abertas && !options.compacto) items.push(pill(`${task.perguntas_abertas} pergunta${task.perguntas_abertas > 1 ? "s" : ""}`, "blue", { icon: "pergunta" }));
  if (task.confidencial === "disponivel" && (!options.compacto || options.confidencial)) items.push(pill("Confidencial", "red", { icon: "cadeado", title: "Referência confidencial disponível nesta máquina" }));
  if (task.confidencial === "bloqueado" && (!options.compacto || options.confidencial)) items.push(pill("Confidencial", "red", { icon: "cadeado", title: "Base confidencial ausente nesta máquina" }));
  if (!options.semPai && task.pai) {
    const parent = (effectiveState().tarefas || []).find((t) => t.id === task.pai);
    if (parent) {
      const pref = issueRef(parent);
      items.push(h("span", { class: "selo neutro forte", title: "Faz parte de" }, icon("aberto", "estado-aberto"),
        parent.titulo + (pref ? ` #${pref.number}` : "")));
    }
  }
  if (task.papel === "concluido" && task.atualizada && !options.semData) items.push(h("span", { class: "selo neutro" }, "Concluída: " + fmtDate(task.atualizada)));
  return items;
}

function waitingDays(task) {
  return task.aguardando_desde ? Math.max(0, -daysUntil(task.aguardando_desde)) : 0;
}

function waitingPill(task) {
  const days = waitingDays(task);
  return pill(`Aguardando · ${task.aguardando}${days ? ` · ${days}d` : ""}`, days >= 3 ? "orange" : "yellow",
    { icon: "ficha", title: `Aguardando desde ${fmtDate(task.aguardando_desde || app.estado.hoje)}` });
}

function segments(done, total) {
  const count = Math.min(total, 20);
  const filled = total ? Math.round((done / total) * count) : 0;
  return h("div", { class: "progresso", title: `${done} de ${total} histórias concluídas` },
    h("span", {}, `${done} / ${total}`),
    total ? h("div", { class: "segmentos" }, Array.from({ length: count }, (_, i) => h("i", { class: i < filled ? "feito" : null }))) : null);
}

function epicProgress(task) {
  const epic = (app.estado.epicos || []).find((e) => e.id === task.id);
  return epic ? segments(epic.concluidas, epic.historias) : null;
}

const CHANGE_DATE = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "2-digit", year: "numeric", timeZone: "America/Sao_Paulo" });
const CHANGE_FULL = new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short", timeZone: "America/Sao_Paulo" });

function changeStamp(task) {
  const value = Date.parse(task.atualizada || task.criada || "");
  return Number.isFinite(value) ? value : null;
}

function changeText(stamp, now = Date.now()) {
  if (stamp === null) return "Última alteração: sem registro";
  const age = now - stamp;
  let text;
  if (age >= 0 && age < 60000) text = "agora";
  else if (age >= 60000 && age < 3600000) {
    const minutes = Math.floor(age / 60000);
    text = `há ${minutes} minuto${minutes === 1 ? "" : "s"}`;
  } else if (age >= 3600000 && age < 86400000) {
    const hours = Math.floor(age / 3600000);
    text = `há ${hours} hora${hours === 1 ? "" : "s"}`;
  } else {
    const full = CHANGE_DATE.format(stamp);
    text = full.slice(-4) === CHANGE_DATE.format(now).slice(-4) ? full.slice(0, 5) : full;
  }
  return "Última alteração: " + text;
}

function lastChange(task) {
  const stamp = changeStamp(task);
  return h(stamp === null ? "span" : "time", { class: "card-atualizada",
    datetime: stamp === null ? null : new Date(stamp).toISOString(),
    "data-updated": stamp,
    title: stamp === null ? "Data de alteração não registrada" : "Última alteração: " + CHANGE_FULL.format(stamp),
  }, icon("historico"), h("span", { class: "card-atualizada-texto" }, changeText(stamp)));
}

function refreshChangeTimes() {
  if (document.hidden) return;
  const now = Date.now();
  document.querySelectorAll("time.card-atualizada[data-updated]").forEach((node) => {
    const text = changeText(Number(node.dataset.updated), now);
    const label = node.querySelector(".card-atualizada-texto");
    if (label.textContent !== text) label.textContent = text;
  });
}

function card(task, options = {}) {
  const editable = app.editando && task.tipo !== "pergunta";
  const signal = (name, title, text) => h("span", { class: "sinal", role: "img", "aria-label": title, title }, icon(name), text || null);
  const parent = task.pai ? effectiveState().tarefas.find((t) => t.id === task.pai) : null;
  return h("div", { class: `card papel-${task.papel}` + (task.nivel === "epico" ? " card-epico" : "") + (task.prazo && daysUntil(task.prazo) < 0 && !CLOSED.includes(task.papel) ? " prazo-vencido" : "") + (task.editado ? " editado" : ""), role: "button", tabindex: "0", "data-id": task.id,
    draggable: editable ? "true" : null,
    ondragstart: editable ? (e) => { app.dragId = task.id; e.dataTransfer.setData("text/plain", task.id); e.dataTransfer.effectAllowed = "move"; e.currentTarget.classList.add("arrastando"); } : null,
    ondragend: editable ? () => { app.dragId = null; clearDrop(); document.querySelectorAll(".arrastando").forEach((n) => n.classList.remove("arrastando")); } : null,
    onclick: () => openTask(task.id), onkeydown: (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openTask(task.id); }
    } },
    h("div", { class: "card-origem" }, stateIcon(task), h("span", { class: "origem-texto" }, origin(task)),
      h("span", { class: "card-sinais" },
        task.nivel ? signal(task.nivel === "epico" ? "epicos" : task.nivel === "historia" ? "camadas" : "tarefa", LEVEL[task.nivel][0], task.nivel === "epico" ? "Épico" : null) : null,
        task.pessoal ? signal("usuario", "Pessoal") : null,
        task.confidencial ? signal("cadeado", task.confidencial === "disponivel" ? "Referência confidencial disponível nesta máquina" : "Base confidencial ausente nesta máquina") : null,
        task.perguntas_abertas ? signal("pergunta", `${task.perguntas_abertas} perguntas abertas`, String(task.perguntas_abertas)) : null)),
    h("div", { class: "card-titulo" }, task.titulo),
    h("div", { class: "rotulos" }, badges(task, { ...options, confidencial: currentView() === "quadro", compacto: true, semNivel: true, semPai: true, semPessoal: true })),
    parent && !options.semPai ? h("div", { class: "card-pai", title: "Faz parte de: " + parent.titulo }, icon("relacoes"), h("span", {}, parent.titulo)) : null,
    task.nivel === "epico" ? epicProgress(task) : null,
    task.proximo_passo && !CLOSED.includes(task.papel) ? h("div", { class: "card-passo" }, icon("seta"), h("span", { class: "passo-texto" }, task.proximo_passo)) : null,
    lastChange(task));
}

// Registro em Markdown simples, montado em nós (sem innerHTML): títulos, listas, parágrafos e `código`.
// Texto sempre vira nós DOM; HTML e protocolos de links não confiáveis não são executados.
function markdownInline(text, depth = 0) {
  if (depth > 4) return [text];
  const tokens = /(`[^`\n]+`|\*\*[^*\n]+\*\*|__[^_\n]+__|\[[^\]\n]+\]\([^\s)]+\)|\*[^*\n]+\*)/g;
  return text.split(tokens).filter(Boolean).map((part) => {
    if (part.startsWith("`") && part.endsWith("`")) return h("code", {}, part.slice(1, -1));
    if (/^(\*\*[^*]+\*\*|__[^_]+__)$/.test(part)) return h("strong", {}, markdownInline(part.slice(2, -2), depth + 1));
    if (part.startsWith("*") && part.endsWith("*")) return h("em", {}, markdownInline(part.slice(1, -1), depth + 1));
    const link = part.match(/^\[([^\]]+)\]\(([^\s)]+)\)$/);
    if (link && /^https?:\/\//i.test(link[2])) return h("a", { href: link[2], target: "_blank", rel: "noopener noreferrer" }, link[1]);
    return part;
  });
}

function markdown(text, depth = 0) {
  const nodes = [], lines = (text || "").replace(/\r\n?/g, "\n").split("\n");
  let i = 0, para = [], lists = [];
  const flush = () => { if (para.length) { nodes.push(h("p", {}, markdownInline(para.join(" ")))); para = []; } };
  const cells = (line) => line.trim().replace(/^\|/, "").replace(/\|$/, "").split(/(?<!\\)\|/).map((cell) => cell.trim().replace(/\\\|/g, "|"));
  const separator = (line) => line && line.includes("|") && cells(line).every((cell) => /^:?-{3,}:?$/.test(cell));
  // Front matter é informação de origem, recolhida sem descartar campos ou linhas.
  if (lines[0]?.trim() === "---") {
    const end = lines.findIndex((line, index) => index > 0 && /^(---|\.\.\.)\s*$/.test(line));
    if (end > 0) {
      const fields = [];
      for (const line of lines.slice(1, end)) {
        const field = line.match(/^([\w-]+):\s*(.*)$/);
        if (field) fields.push({ name: field[1], value: field[2] });
        else if (fields.length) fields[fields.length - 1].value += "\n" + line;
        else fields.push({ name: "Metadados", value: line });
      }
      nodes.push(h("details", { class: "documento-metadados" }, h("summary", {}, icon("campos"), "Metadados do arquivo"),
        h("dl", {}, fields.map((field) => [h("dt", {}, field.name), h("dd", {}, field.value)]))));
      i = end + 1;
    }
  }
  for (; i < lines.length; i++) {
    const line = lines[i].trimEnd();
    const heading = line.match(/^(#{1,6})\s+(.*)$/);
    const item = line.match(/^(\s*)([-*+] |\d+[.)] )(.*)$/);
    const fence = line.match(/^\s*(`{3,}|~{3,})(.*)$/);
    if (fence) {
      flush(); lists = [];
      const code = [], marker = fence[1][0], length = fence[1].length;
      while (++i < lines.length) {
        if (new RegExp("^\\s*" + marker + "{" + length + ",}\\s*$").test(lines[i])) break;
        code.push(lines[i]);
      }
      nodes.push(h("pre", { class: "documento-codigo", tabindex: "0", role: "region", "aria-label": "Trecho de código" }, h("code", {}, code.join("\n"))));
    } else if (line.includes("|") && separator(lines[i + 1])) {
      flush(); lists = [];
      const headers = cells(line), align = cells(lines[++i]), rows = [];
      while (i + 1 < lines.length && lines[i + 1].trim() && lines[i + 1].includes("|")) rows.push(cells(lines[++i]));
      const attrs = (index) => ({ style: "text-align:" + (align[index]?.endsWith(":") ? align[index].startsWith(":") ? "center" : "right" : "left") });
      nodes.push(h("div", { class: "tabela-rolagem documento-tabela", role: "region", tabindex: "0", "aria-label": "Tabela: " + headers.join(", ") },
        h("table", {}, h("thead", {}, h("tr", {}, headers.map((title, index) => h("th", { ...attrs(index), scope: "col" }, markdownInline(title))))),
          h("tbody", {}, rows.map((row) => h("tr", {}, headers.map((_, index) => h("td", attrs(index), markdownInline(row[index] || "")))))))));
    } else if (heading) {
      flush(); lists = [];
      nodes.push(h("h" + Math.min(heading[1].length + 2, 6), {}, markdownInline(heading[2])));
    } else if (/^\s*(---+|\*\*\*+|___+)\s*$/.test(line)) {
      flush(); lists = []; nodes.push(h("hr", {}));
    } else if (/^\s*>/.test(line)) {
      flush(); lists = [];
      const quote = [line.replace(/^\s*>\s?/, "")];
      while (i + 1 < lines.length && /^\s*>/.test(lines[i + 1])) quote.push(lines[++i].replace(/^\s*>\s?/, ""));
      nodes.push(h("blockquote", {}, depth < 4 ? markdown(quote.join("\n"), depth + 1) : h("p", {}, quote.join("\n"))));
    } else if (item) {
      flush();
      const indent = item[1].replace(/\t/g, "    ").length, tag = /^\d/.test(item[2]) ? "ol" : "ul";
      while (lists.length && (lists.at(-1).indent > indent || (lists.at(-1).indent === indent && lists.at(-1).tag !== tag))) lists.pop();
      if (!lists.length || lists.at(-1).indent < indent) {
        const list = h(tag, tag === "ol" ? { start: parseInt(item[2], 10) } : {});
        if (lists.length) lists.at(-1).last.append(list); else nodes.push(list);
        lists.push({ indent, tag, list, last: null });
      }
      const check = item[3].match(/^\[([ xX])\]\s+(.*)$/);
      const li = h("li", {}, check ? [h("span", { class: "documento-check", "aria-label": check[1] === " " ? "Pendente: " : "Concluído: " }, check[1] === " " ? "○" : "✓"), markdownInline(check[2])] : markdownInline(item[3]));
      lists.at(-1).list.append(li); lists.at(-1).last = li;
    } else if (!line.trim()) { flush(); lists = []; }
    else if (/^\s+/.test(line) && lists.length) lists.at(-1).last.append(" ", ...markdownInline(line.trim()));
    else { lists = []; para.push(line.trim()); }
  }
  flush();
  return nodes;
}

function taskDocument(text) {
  const match = /^## Registro\s*$/m.exec(text);
  if (!match) return markdown(text);
  const after = text.slice(match.index + match[0].length), next = /^#{1,2}\s+/m.exec(after);
  const log = next ? after.slice(0, next.index) : after;
  const entries = [], remainder = [];
  for (const line of log.split("\n")) {
    const entry = line.match(/^\s*[-*]\s+(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})\s+[—–-]\s*(.*)$/);
    if (entry) entries.push({ date: entry[1], time: entry[2], text: entry[3] });
    else if (entries.length) entries.at(-1).text += "\n" + line;
    else remainder.push(line);
  }
  if (!entries.length) return markdown(text);
  entries.sort((a, b) => (b.date + b.time).localeCompare(a.date + a.time));
  return [...markdown(text.slice(0, match.index)), h("section", { class: "registros", "aria-label": "Registro da tarefa" },
    h("div", { class: "registros-topo" }, h("h3", {}, icon("historico"), "Registro"), h("span", { class: "contador" }, entries.length)),
    h("p", { class: "registros-legenda" }, "Mais recentes primeiro"), markdown(remainder.join("\n")),
    h("ol", { class: "registros-lista" }, entries.map((entry) => h("li", { class: "registro-entrada" },
      h("header", {}, h("time", { datetime: entry.date + "T" + entry.time }, icon("calendario"), fmtDate(entry.date), h("span", {}, entry.time))),
      h("div", { class: "registro-texto" }, markdown(entry.text)))))), ...markdown(next ? after.slice(next.index) : "")];
}

function stateLabel(task) {
  if (task.tipo === "pergunta") return h("span", { class: "estado-grande aberto" }, icon("pergunta"), task.resposta ? "Respondida" : "Pergunta");
  if (task.papel === "concluido") return h("span", { class: "estado-grande fechado" }, icon("fechado"), "Concluída");
  if (task.papel === "arquivado") return h("span", { class: "estado-grande arquivado" }, icon("arquivado"), "Arquivada");
  return h("span", { class: "estado-grande aberto" }, icon("aberto"), "Aberta");
}

function sideSection(title, ...content) {
  const body = content.flat(Infinity).filter(Boolean);
  const symbols = { "Rótulos": "etiqueta", "Campos": "campos", "Projeto": "quadro", "Relacionamentos": "relacoes" };
  return h("section", { class: "lateral-secao" }, h("h4", {}, icon(symbols[title] || "mais"), title), body.length ? body : h("p", { class: "vazio" }, "Nenhum"));
}

async function openTask(id) {
  const panel = document.getElementById("painel");
  const request = beginPanel();
  panel.setAttribute("aria-busy", "true");
  fill(panel, panelHeader("Carregando tarefa…"), h("div", { class: "painel-corpo" }, loadingState()));
  focusPanel();
  try {
    const detail = await api("/api/tarefa/" + encodeURIComponent(id));
    if (request !== app.painelRequest) return;
    const task = effectiveState().tarefas.find((t) => t.id === id) || detail.resumo;
    const data = { ...detail.data, ...task };
    const draft = app.editando && app.rascunho.tarefas[id];
    if (draft) {
      const changed = new Set([...(draft.unset || []), ...Object.keys(draft.campos || {})]);
      for (const key of changed) if (!(key in task)) delete data[key];
    }
    const parent = data.pai ? effectiveState().tarefas.find((t) => t.id === data.pai) : null;
    const ref = issueRef(data);
    const parentRef = parent ? issueRef(parent) : null;
    const epic = (app.estado.epicos || []).find((e) => e.id === (data.nivel === "epico" ? data.id : data.pai));
    const field = (name, value) => value ? h("div", { class: "campo-lateral" }, h("span", {}, name), h("span", {}, value)) : null;
    const goTo = (target, text) => h("button", { class: "link", type: "button", onclick: () => openTask(target.id) }, text || target.titulo);
    fill(panel,
      h("div", { class: "painel-topo" },
        h("h2", { id: "painel-titulo", tabindex: "-1" }, data.titulo, ref ? [" ", h("span", { class: "numero-issue" }, `#${ref.number}`)] : null),
        h("button", { class: "botao-icone discreto", type: "button", title: "Fechar", "aria-label": "Fechar painel", onclick: closePanel }, icon("fechar"))),
      h("div", { class: "faixa-estado" },
        stateLabel(task),
        parent ? h("button", { class: "selo neutro forte grande", type: "button", onclick: () => openTask(parent.id) },
          stateIcon(parent), `Parent: ${parent.titulo}${parentRef ? " #" + parentRef.number : ""}`) : null,
        task.codigo && (!ref || task.codigo !== ref.full) ? h("span", { class: "selo neutro forte grande" }, icon("repo"), task.codigo) : null,
        ref ? h("span", { class: "selo neutro forte grande" }, icon("repo"), ref.full.split("#")[0]) : null,
        task.pessoal ? h("span", { class: "selo cor-pink grande" }, "pessoal") : null),
      h("div", { class: "painel-colunas" },
        h("div", { class: "painel-principal" },
          h("div", { class: "comentario" },
            h("header", {}, h("strong", {}, label(data.tipo)), h("span", { class: "vazio" }, ` · ${data.id}`),
              data.atualizada ? h("span", { class: "vazio" }, ` · atualizada ${when(data.atualizada)}`) : null),
            h("div", { class: "comentario-corpo markdown" },
              data.proximo_passo ? h("div", { class: "proximo-destaque" }, h("h3", {}, icon("seta"), "Próximo passo"), h("p", {}, data.proximo_passo)) : null,
              detail.body ? taskDocument(detail.body) : (!data.proximo_passo ? h("p", { class: "vazio" }, "Sem registro.") : null))),
          detail.filhos && detail.filhos.length ? h("div", { class: "caixa" },
            h("header", {}, h("h3", {}, data.nivel === "epico" ? "Histórias" : "Itens"),
              epic && data.nivel === "epico" ? h("span", { class: "direita" }, segments(epic.concluidas, epic.historias)) : null),
            detail.filhos.map((child) => h("div", { class: "linha-caixa" }, stateIcon(child), goTo(child),
              h("span", { class: "selo neutro" }, h("span", { class: `status papel-${roleOf(child.coluna)}` }), columnName(child.coluna))))) : null,
          detail.complemento ? h("section", { class: "comentario documento-confidencial" }, h("header", {}, icon("cadeado"), h("strong", {}, "Complemento confidencial"), h("span", { class: "vazio" }, " · só nesta máquina")),
            h("div", { class: "comentario-corpo markdown" }, markdown(detail.complemento))) : null,
          Object.entries(detail.referencias || {}).map(([refName, text]) => h("section", { class: "comentario documento-confidencial" },
            h("header", {}, icon("cadeado"), h("strong", {}, "Referência confidencial"), h("span", { class: "vazio" }, "Só nesta máquina")),
            h("p", { class: "documento-origem" }, refName),
            h("div", { class: "comentario-corpo markdown" }, text ? markdown(text) : h("p", { class: "vazio" }, "Referência indisponível: arquivo não encontrado na base confidencial ou acesso fora da base.")))),
          detail.confidencial === "bloqueado" && !Object.keys(detail.referencias || {}).length
            ? h("p", { class: "vazio" }, "Complemento confidencial só na máquina que possui a base.") : null,
          app.editando && data.tipo !== "pergunta" ? h("div", { class: "comentario" }, h("div", { class: "comentario-corpo" }, editForm(id))) : null),
        h("aside", { class: "painel-lateral" },
          sideSection("Rótulos", h("div", { class: "rotulos" }, badges(task, { semPai: true, semCodigo: true, semData: true }))),
          sideSection("Campos",
            field("Status", h("span", { class: "selo neutro forte" }, h("span", { class: `status papel-${roleOf(data.coluna)}` }), columnName(data.coluna))),
            field("Tipo", label(data.tipo)),
            field("Nível", data.nivel ? LEVEL[data.nivel][0] : null),
            field("Código", task.codigo),
            field("Prazo", data.prazo ? fmtDate(data.prazo) : null),
            field("Concluída", task.papel === "concluido" && data.atualizada ? fmtDate(data.atualizada) : null),
            field("Pessoal", task.pessoal ? (("pessoal_marcado" in task) ? "sim (marcado)" : "sim (calculado)") : (("pessoal_marcado" in task) ? "não (marcado)" : null))),
          sideSection("Relacionamentos",
            parent ? [h("span", { class: "vazio" }, "Faz parte de"), h("div", { class: "relacao" }, stateIcon(parent), goTo(parent),
              epic && data.nivel !== "epico" ? h("span", { class: "contador" }, `${epic.concluidas} / ${epic.historias}`) : null)] : null,
            (data.issue || []).length ? [h("span", { class: "vazio" }, "Issues"), (data.issue || []).map((i) => h("div", { class: "relacao" }, icon("aberto", "estado-aberto"), i))] : null))));
    panel.setAttribute("aria-busy", "false");
    focusPanel();
  } catch (error) {
    if (request !== app.painelRequest) return;
    showPanel(h("h2", {}, "Não foi possível abrir a tarefa"), h("p", { class: "aviso erro", role: "alert" }, error.message),
      h("button", { class: "botao", type: "button", onclick: () => openTask(id) }, "Tentar novamente"));
  }
}

function panelHeader(title) {
  return h("div", { class: "painel-topo" }, h("h2", { id: "painel-titulo", tabindex: "-1" }, title),
    h("button", { class: "botao-icone discreto", type: "button", title: "Fechar", "aria-label": "Fechar painel", onclick: closePanel }, icon("fechar")));
}

function beginPanel() {
  const panel = document.getElementById("painel");
  const focused = document.activeElement;
  if (focused && focused !== document.body && !panel.contains(focused)) app.painelOrigem = focused;
  app.painelRequest = (app.painelRequest || 0) + 1;
  clearTimeout(app.painelFechando);
  app.abrindoPainel = true;
  setTimeout(() => { app.abrindoPainel = false; }, 0);
  panel.hidden = false;
  panel.scrollTop = 0;
  panel.classList.remove("fechando");
  requestAnimationFrame(() => { if (!panel.hidden && !panel.classList.contains("fechando")) panel.classList.add("aberto"); });
  return app.painelRequest;
}

function focusPanel() {
  const panel = document.getElementById("painel");
  const title = panel.querySelector("#painel-titulo");
  if (title) title.focus({ preventScroll: true });
}

function closePanel(restoreFocus = true) {
  const panel = document.getElementById("painel");
  if (panel.hidden || panel.classList.contains("fechando")) return;
  app.painelRequest = (app.painelRequest || 0) + 1;
  panel.setAttribute("aria-busy", "false");
  panel.classList.remove("aberto");
  panel.classList.add("fechando");
  const duration = matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 180;
  app.painelFechando = setTimeout(() => { panel.hidden = true; panel.classList.remove("fechando"); }, duration);
  if (restoreFocus !== false) {
    const target = app.painelOrigem && app.painelOrigem.isConnected ? app.painelOrigem : document.getElementById("conteudo");
    target.focus({ preventScroll: true });
  }
}

// Visões ------------------------------------------------------------------------
// Cada visão: { titulo, render(estado) -> Node | Promise<Node> }.
const CLOSED = ["concluido", "arquivado"];
const ROLE_ORDER = ["ativo", "validacao", "pronto", "entrada", "concluido", "arquivado"];

function pref(key, fallback) {
  try { return localStorage.getItem("yabook." + key) ?? fallback; } catch (error) { return fallback; }
}
function setPref(key, value) {
  try { localStorage.setItem("yabook." + key, value); } catch (error) { /* armazenamento indisponível */ }
}

function work(estado) {
  return estado.tarefas.filter((t) => t.tipo !== "pergunta");
}

function byOrder(a, b) {
  return (a.ordem || 0) - (b.ordem || 0) || a.titulo.localeCompare(b.titulo);
}

function byRecent(a, b) {
  return ((changeStamp(b) ?? -Infinity) - (changeStamp(a) ?? -Infinity)) || byOrder(a, b);
}

function boardOrder(a, b) {
  return pref("quadro.ordem", "recentes") === "manual" ? byOrder(a, b) : byRecent(a, b);
}

function epicOf(task, map) {
  let current = task, guard = 0;
  while (current && guard++ < 5) {
    if (current.nivel === "epico") return current.id;
    current = current.pai ? map[current.pai] : null;
  }
  return null;
}

function filtered(tasks) {
  const text = (app.busca || "").trim().toLowerCase();
  if (!text) return tasks;
  return tasks.filter((t) => [t.titulo, t.codigo, t.id, t.proximo_passo, (t.issue || []).join(" ")].join(" ").toLowerCase().includes(text));
}

function titleLink(task) {
  return h("button", { class: "link titulo", type: "button", title: task.titulo, onclick: () => openTask(task.id) }, task.titulo);
}

function row(task) {
  return h("div", { class: "linha-caixa" }, stateIcon(task), titleLink(task),
    h("span", { class: "selo neutro" }, h("span", { class: `status papel-${task.papel}` }), columnName(task.coluna)));
}

function progress(epic) {
  const pct = epic.historias ? Math.round((100 * epic.concluidas) / epic.historias) : 0;
  return h("div", { class: "progresso", title: `${epic.concluidas} de ${epic.historias} concluídas` },
    h("div", { class: "barra" }, h("i", { style: `width:${pct}%` })),
    h("span", {}, `${epic.concluidas}/${epic.historias}`));
}

const VIEWS = {
  hoje: {
    titulo: "Hoje",
    icone: "hoje",
    render(estado) {
      const tasks = filtered(work(estado));
      const doing = tasks.filter((t) => t.papel === "ativo").sort(byRecent);
      const testing = tasks.filter((t) => t.papel === "validacao").sort(byRecent);
      const late = estado.prazos.filter((t) => daysUntil(t.prazo) < 0).length;
      app.contagem = doing.length + testing.length;
      const list = (title, symbol, items, empty, render = row) => h("div", { class: "caixa" },
        h("header", {}, icon(symbol), h("h3", {}, title), h("span", { class: "contador" }, String(items.length))),
        items.length ? items.map(render) : h("div", { class: "corpo vazio" }, icon("check"), empty));
      const full = (t) => estado.tarefas.find((x) => x.id === t.id) || t;
      const heading = (title, symbol, count) => h("h2", { class: "titulo-secao" }, icon(symbol), title,
        count === undefined ? null : h("span", { class: "contador" }, String(count)));
      const blank = (symbol, text) => h("div", { class: "foco-vazio" }, icon(symbol), h("span", {}, text));
      const activeEpics = doing.filter((t) => t.nivel === "epico").length;
      const activeTasks = doing.length - activeEpics;
      const metrics = [
        ["Em andamento", doing.length, "alvo", "purple", "quadro", `${activeTasks} ${activeTasks === 1 ? "tarefa" : "tarefas"} · ${activeEpics} ${activeEpics === 1 ? "épico" : "épicos"}`],
        ["Em validação", testing.length, "tarefa", "green", "quadro", ""],
        ["Prazos próximos", estado.prazos.length, "calendario", late ? "red" : "orange", "prazos", late ? `${late} em atraso` : ""],
        ["Perguntas", estado.perguntas.length, "pergunta", "blue", "perguntas", ""],
      ];
      return h("section", { class: "visao-hoje" },
        h("div", { class: "numeros" }, metrics.map(([name, total, symbol, color, target, detail]) =>
          h("button", { class: `numero cor-${color}`, type: "button", title: `Abrir ${VIEWS[target].titulo}`, onclick: () => { location.hash = target; } },
            h("b", {}, total), h("span", { class: "numero-icone" }, icon(symbol)), h("span", { class: "numero-nome" }, name),
            detail ? h("small", {}, detail) : null))),
        h("div", { class: "painel-dia" },
          h("div", { class: "andamento-hoje" }, heading("Em andamento", "quadro", doing.length),
            doing.length ? h("div", { class: "cards" }, doing.map((t) => card(t, { status: t.nivel === "epico", semNivel: true })))
              : blank("check", "Nenhuma tarefa ou épico em andamento.")),
          h("div", { class: "atencao" }, heading("Sua atenção", "alerta"),
            list("Prazos", "calendario", filtered(estado.prazos.map(full)), "Nenhum prazo próximo.",
              (t) => h("div", { class: "linha-caixa" }, stateIcon(t), titleLink(t), badges(t, { semNivel: true, semPai: true, semCodigo: true }).filter((n) => n.title === "Prazo"))),
            list("Perguntas", "pergunta", filtered(estado.perguntas.map(full)), "Nenhuma pergunta aberta."),
            list("Aguardando", "ficha", tasks.filter((t) => t.aguardando && !CLOSED.includes(t.papel)).sort((a, b) => waitingDays(b) - waitingDays(a)),
              "Nada aguardando terceiros.", (t) => h("div", { class: "linha-caixa" }, stateIcon(t), titleLink(t), waitingPill(t))),
            list("Em validação", "tarefa", testing, "Nada para revisar."))));
    },
  },
  quadro: {
    titulo: "Quadro",
    icone: "quadro",
    opcoes(estado) {
      const epicFilter = pref("quadro.epico", "");
      const levelFilter = pref("quadro.nivel", "");
      const showArchived = pref("quadro.arquivadas", "0") === "1";
      return [
        h("select", { title: "Épico", onchange: (e) => { setPref("quadro.epico", e.target.value); render(); } },
          h("option", { value: "" }, "Épico: todos"), h("option", { value: "-", selected: epicFilter === "-" }, "Sem épico"),
          estado.epicos.map((e) => h("option", { value: e.id, selected: e.id === epicFilter }, e.titulo))),
        h("select", { title: "Nível", onchange: (e) => { setPref("quadro.nivel", e.target.value); render(); } },
          [["", "Nível: todos"], ["epico", "Épicos"], ["historia", "Histórias"], ["tarefa", "Tarefas"], ["-", "Sem nível"]]
            .map(([v, n]) => h("option", { value: v, selected: v === levelFilter }, n))),
        switchInput("Arquivadas", showArchived, (e) => { setPref("quadro.arquivadas", e.target.checked ? "1" : "0"); render(); }),
        switchInput("Só aguardando", pref("quadro.aguardando", "0") === "1", (e) => { setPref("quadro.aguardando", e.target.checked ? "1" : "0"); render(); }),
        h("select", { "aria-label": "Ordenar cards", title: "Em Última alteração, arraste entre colunas. Para reordenar na coluna, use Ordem manual.",
          onchange: (e) => { setPref("quadro.ordem", e.target.value); render(); } },
          [["recentes", "Última alteração"], ["manual", "Ordem manual"]].map(([value, text]) =>
            h("option", { value, selected: pref("quadro.ordem", "recentes") === value }, text))),
      ];
    },
    render(estado) {
      const map = Object.fromEntries(estado.tarefas.map((t) => [t.id, t]));
      const epicFilter = pref("quadro.epico", "");
      const levelFilter = pref("quadro.nivel", "");
      const showArchived = pref("quadro.arquivadas", "0") === "1";
      const onlyWaiting = pref("quadro.aguardando", "0") === "1";
      const visible = filtered(work(estado)).filter((t) => (!onlyWaiting || t.aguardando) &&
        (!epicFilter || (epicFilter === "-" ? !epicOf(t, map) : epicOf(t, map) === epicFilter)) &&
        (!levelFilter || (levelFilter === "-" ? !t.nivel : t.nivel === levelFilter)));
      const columns = estado.colunas.filter((c) => showArchived || c.papel !== "arquivado");
      const epics = visible.filter((t) => t.nivel === "epico" && columns.some((c) => c.id === t.coluna))
        .sort((a, b) => CLOSED.includes(a.papel) - CLOSED.includes(b.papel) || boardOrder(a, b));
      const items = visible.filter((t) => t.nivel !== "epico");
      app.contagem = items.filter((t) => columns.some((c) => c.id === t.coluna)).length + epics.length;
      const epicColumn = h("div", { class: "coluna coluna-epicos", "data-coluna": "epicos" },
        h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, "Épicos"), h("span", { class: "contador" }, String(epics.length))),
        h("div", { class: "itens" }, epics.length ? epics.map((t) => card(t, { status: true, semNivel: true }))
          : h("p", { class: "vazio", style: "text-align:center;font-size:12px" }, "Nenhum épico")));
      return h("div", { class: "quadro" }, columns.map((column) => {
        const cards = items.filter((t) => t.coluna === column.id).sort(boardOrder);
        return h("div", { class: `coluna papel-${column.papel}`, "data-coluna": column.id,
          ondragover: app.editando ? indicateDrop : null,
          ondragleave: app.editando ? (e) => { if (!e.currentTarget.contains(e.relatedTarget)) clearDrop(); } : null,
          ondrop: app.editando ? (e) => { e.currentTarget.classList.remove("alvo"); dropCard(e, column.id, cards); } : null },
          h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, column.nome), h("span", { class: "contador" }, String(cards.length)),
            h("span", { class: "acoes" }, app.editando
              ? h("button", { class: "botao-icone discreto", type: "button", title: "Renomear coluna", "aria-label": "Renomear coluna " + column.nome, onclick: () => renameColumn(column) }, icon("editar"))
              : null)),
          h("div", { class: "itens" }, cards.length ? cards.map((t) => card(t)) : h("p", { class: "vazio", style: "text-align:center;font-size:12px" }, "Nenhum item")));
      }), epicColumn);
    },
  },
  epicos: {
    titulo: "Épicos",
    descricao: "Acompanhe as histórias e o progresso de cada iniciativa.",
    icone: "epicos",
    render(estado) {
      const tasks = work(estado);
      const children = (id) => tasks.filter((t) => t.pai === id)
        .sort((a, b) => ROLE_ORDER.indexOf(a.papel) - ROLE_ORDER.indexOf(b.papel) || byRecent(a, b));
      const text = (app.busca || "").toLowerCase();
      const matches = (t) => !text || [t.titulo, t.codigo, t.id].join(" ").toLowerCase().includes(text);
      const epics = estado.epicos.filter((e) => matches(e) || children(e.id).some(matches));
      const loose = filtered(tasks.filter((t) => !t.pai && t.nivel !== "epico" && !CLOSED.includes(t.papel))).sort(byRecent);
      app.contagem = epics.length;
      const storyRow = (story, sub) => h("div", { class: "linha-caixa" + (sub ? " sub" : "") }, stateIcon(story), titleLink(story),
        badges(story, { semNivel: true, semPai: true, semPessoal: true, semData: true }),
        h("span", { class: "selo neutro" }, h("span", { class: `status papel-${story.papel}` }), columnName(story.coluna)));
      return h("section", {},
        epics.length ? epics.map((epic) => {
          const full = tasks.find((t) => t.id === epic.id) || epic;
          const stories = children(epic.id);
          const open = stories.filter((s) => !CLOSED.includes(s.papel));
          const closed = stories.filter((s) => CLOSED.includes(s.papel));
          const withTasks = (story) => [storyRow(story), children(story.id).map((sub) => storyRow(sub, true))];
          return h("div", { class: "caixa" },
            h("header", {}, stateIcon(full), h("button", { class: "link", type: "button", onclick: () => openTask(epic.id) }, h("h3", {}, epic.titulo)),
              h("span", { class: "rotulos" }, badges(full, { semNivel: true })),
              h("span", { class: "direita" }, h("span", { class: "selo neutro" }, h("span", { class: `status papel-${roleOf(epic.coluna)}` }), columnName(epic.coluna)))),
            h("div", { class: "corpo" }, segments(epic.concluidas, epic.historias),
              epic.proximo_passo ? h("div", { class: "card-passo", style: "margin-top:6px" }, epic.proximo_passo) : null),
            open.map(withTasks),
            closed.length ? h("details", {}, h("summary", {}, `${closed.length} concluída(s) ou arquivada(s)`), closed.map(withTasks)) : null);
        }) : emptyState(app.busca ? "Nenhum épico com esse filtro" : "Nenhum épico", "Os épicos reúnem histórias e mostram o progresso da iniciativa."),
        loose.length ? [h("h2", {}, "Sem épico"), h("div", { class: "cards" }, loose.map(card))] : null);
    },
  },
  prazos: {
    titulo: "Prazos",
    descricao: "Calendário e agenda das tarefas com prazo.",
    icone: "prazos",
    render(estado) {
      const rows = filtered(work(estado)).filter((t) => t.prazo && !CLOSED.includes(t.papel)).sort((a, b) => a.prazo.localeCompare(b.prazo));
      app.contagem = rows.length;
      const agenda = app.prazoDia ? rows.filter((t) => t.prazo === app.prazoDia) : rows;
      const groups = [
        { title: "Atrasados", icon: "alerta", class: "atrasada", test: (days) => days < 0 },
        { title: "Próximos 2 dias", icon: "calendario", class: "proximo", test: (days) => days >= 0 && days <= 2 },
        { title: "Mais adiante", icon: "prazos", class: "", test: (days) => days > 2 },
      ];
      return h("section", { class: "prazos-visao" }, deadlineCalendar(rows, estado.hoje),
        h("section", { class: "prazos-lista", "aria-label": "Agenda de prazos" },
          h("div", { class: "prazos-agenda-topo" },
            h("h2", { id: "prazos-agenda-titulo", tabindex: "-1" }, app.prazoDia ? "Prazos de " + fmtDate(app.prazoDia) : "Todos os prazos"),
            app.prazoDia ? h("button", { class: "botao pequeno", type: "button", onclick: () => { app.prazoDia = null; render(); } }, "Ver todos") : null),
          !agenda.length ? emptyState(app.prazoDia ? "Nenhum prazo neste dia" : app.busca ? "Nenhum prazo com esse filtro" : "Nenhuma tarefa aberta com prazo", "Os prazos aparecem aqui quando definidos nas tarefas.") : groups.map((group) => {
            const items = agenda.filter((task) => group.test(daysUntil(task.prazo)));
            if (!items.length) return null;
            return h("section", { class: "prazo-grupo " + group.class },
              h("header", {}, h("h3", {}, icon(group.icon), group.title), h("span", { class: "contador" }, items.length)),
              items.map((task) => {
                const days = daysUntil(task.prazo);
                const date = new Date(task.prazo + "T12:00:00");
                const month = date.toLocaleDateString("pt-BR", { month: "short" }).replace(".", "");
                const distance = days < 0 ? `${-days} dia${days === -1 ? "" : "s"} de atraso` : days === 0 ? "Hoje" : days === 1 ? "Amanhã" : `Em ${days} dias`;
                return h("article", { class: "prazo-item " + group.class },
                  h("time", { class: "prazo-data", datetime: task.prazo, "aria-label": fmtDate(task.prazo) },
                    h("strong", {}, task.prazo.slice(8, 10)), h("span", {}, month + (task.prazo.slice(0, 4) !== estado.hoje.slice(0, 4) ? " " + task.prazo.slice(0, 4) : ""))),
                  h("div", { class: "prazo-conteudo" }, titleLink(task),
                    h("div", { class: "prazo-meta" },
                      task.codigo ? pill(task.codigo, "gray", { icon: "repo", title: "Código" }) : null,
                      h("span", { class: "selo neutro" }, h("span", { class: `status papel-${task.papel}` }), columnName(task.coluna)))),
                  h("span", { class: "prazo-indicador" }, days < 0 ? icon("alerta") : icon("calendario"), distance));
              }));
          })));
    },
  },
  perguntas: {
    titulo: "Perguntas",
    descricao: "Decisões pendentes e respostas recentes para continuar o trabalho.",
    icone: "pergunta",
    render(estado) {
      const questions = filtered(estado.tarefas.filter((t) => t.tipo === "pergunta"));
      app.contagem = questions.length;
      const open = questions.filter((t) => !t.resposta && !CLOSED.includes(t.papel));
      const answered = questions.filter((t) => t.resposta).sort((a, b) => (b.atualizada || "").localeCompare(a.atualizada || "")).slice(0, 10);
      const about = (t) => {
        const target = t.sobre && estado.tarefas.find((x) => x.id === t.sobre);
        return target ? h("button", { class: "link pergunta-vinculo", type: "button", title: "Abrir tarefa relacionada", onclick: () => openTask(target.id) }, icon("camadas"), target.titulo) : null;
      };
      const questionCard = (task, answered) => h("li", { class: "pergunta-card" + (answered ? " respondida" : "") },
        h("div", { class: "pergunta-topo" }, icon(answered ? "check" : "pergunta", answered ? "estado-aberto" : "estado-pergunta"),
          h("h3", {}, task.titulo), answered ? pill("Respondida", "green") : null),
        about(task),
        answered ? h("div", { class: "pergunta-resposta" }, icon("seta"), h("p", {}, task.resposta))
          : h("details", { class: "passo" }, h("summary", {}, "Como responder"), h("code", {}, `task answer ${task.id} <resposta>`)));
      return h("section", {},
        h("h2", {}, "Aguardando você", h("span", { class: "contador" }, open.length)),
        open.length ? h("ul", { class: "perguntas" }, open.map((t) => questionCard(t, false)))
          : emptyState(app.busca ? "Nenhuma pergunta com esse filtro" : "Tudo respondido por aqui", "As decisões pendentes aparecem aqui."),
        answered.length ? [h("h2", {}, "Respondidas recentes", h("span", { class: "contador" }, answered.length)),
          h("ul", { class: "perguntas" }, answered.map((t) => questionCard(t, true)))] : null);
    },
  },
  semana: {
    titulo: "Semana",
    descricao: "Atividade por dia e totais da ficha. Abra um dia para ver os detalhes.",
    icone: "semana",
    async render(estado) {
      const ref = app.semana || estado.hoje;
      const [week, sheetWeek] = await Promise.all([api("/api/semana?data=" + ref), api("/api/ficha?semana=1&data=" + ref)]);
      const confirmed = Object.fromEntries((sheetWeek.dias || []).filter((d) => d.confirmada).map((d) => [d.data, true]));
      const total = week.dias.reduce((sum, d) => sum + d.horas, 0);
      const peak = Math.max(1, ...week.dias.map((d) => d.horas));
      return h("section", {},
        dayNav("semana", ref, 7, `Semana de ${fmtDate(week.inicio)}`),
        h("div", { class: "numeros" }, h("div", { class: "numero" }, h("b", {}, hours(total)), h("span", { class: "numero-icone" }, icon("ficha")), h("span", { class: "numero-nome" }, "Atividade estimada")),
          h("div", { class: "numero" }, h("b", {}, Array.isArray(sheetWeek.dias) ? Object.keys(confirmed).length : "—"), h("span", { class: "numero-icone" }, icon("check")), h("span", { class: "numero-nome" }, "Dias confirmados"))),
        h("h2", {}, "Por dia"),
        h("div", { class: "semana-grade" }, week.dias.map((day) => h("article", {
          class: "dia-card" + (day.data === estado.hoje ? " hoje" : "") + (confirmed[day.data] ? " confirmado" : ""),
        },
          h("div", { class: "dia-topo" },
            h("button", { class: "link", type: "button", disabled: !!SNAPSHOT && day.data !== SNAPSHOT.ficha.data,
              title: SNAPSHOT && day.data !== SNAPSHOT.ficha.data ? "Ficha deste dia disponível no painel local" : "Abrir ficha de " + fmtDate(day.data),
              onclick: () => { app.ficha = day.data; location.hash = "ficha"; } },
              h("span", {}, weekday(day.data)), h("strong", {}, day.data.slice(8, 10))),
            confirmed[day.data] ? h("span", { role: "img", title: "Ficha confirmada", "aria-label": "Ficha confirmada" }, icon("check")) : null),
          h("div", { class: "dia-horas" }, h("strong", {}, hours(day.horas)), h("span", {}, "estimadas")),
          h("div", { class: "dia-barra", "aria-hidden": "true", title: "Atividade em relação ao dia mais ativo da semana" }, h("i", { style: `width:${Math.round(day.horas / peak * 100)}%` })),
          day.tarefas.length ? h("ul", { class: "dia-tarefas" }, day.tarefas.slice(0, 3).map((task) =>
            h("li", {}, h("button", { class: "link", type: "button", title: task.titulo, onclick: () => openTask(task.tarefa) }, task.titulo), h("span", {}, hours(task.horas)))))
            : h("p", { class: "dia-vazio" }, "Sem atividade"),
          day.tarefas.length > 3 ? h("button", { class: "link dia-mais", type: "button", disabled: !!SNAPSHOT && day.data !== SNAPSHOT.ficha.data,
            onclick: () => { app.ficha = day.data; location.hash = "ficha"; } }, `+${day.tarefas.length - 3} tarefas na ficha`) : null))),
        h("section", { class: "totais-semana" }, h("h2", {}, "Totais da ficha na semana"),
          !Array.isArray(sheetWeek.totais) ? h("p", { class: "vazio" }, "Totais semanais disponíveis no painel local.")
            : sheetWeek.totais.length ? h("table", {}, h("thead", {}, h("tr", {}, h("th", {}, "Tipo"), h("th", {}, "Código"), h("th", { class: "num" }, "Total"))),
            h("tbody", {}, sheetWeek.totais.map((r) => h("tr", {}, h("td", {}, label(r.tipo)), h("td", {}, r.codigo || "Sem código"), h("td", { class: "num" }, hours(r.total))))))
            : h("p", { class: "vazio" }, "Sem horas que contam na ficha nesta semana.")));
    },
  },
  ficha: {
    titulo: "Ficha",
    descricao: "Revise as horas do dia e copie a ficha para o seu registro.",
    icone: "ficha",
    async render(estado) {
      const day = SNAPSHOT ? SNAPSHOT.ficha.data : app.ficha || estado.hoje;
      const sheet = await api("/api/ficha?data=" + day);
      const confirmed = sheet.confirmada;
      const rows = sheet.linhas;
      const text = rows.map((r) => [r.rotulo, r.codigo || "", r.inicio || "", r.fim || "", hours(r.total), r.observacao].join("\t")).join("\n");
      return h("section", {},
        dayNav("ficha", day, 1, `${weekday(day)} ${fmtDate(day)}`),
        confirmed ? h("p", { class: "aviso" }, "Confirmada: ", confirmed.linhas.map((r) => `${label(r.tipo)} ${r.codigo || "sem código"} ${hours(r.total)}`).join(" · ")) : null,
        h("div", { class: "filtros" },
          h("span", {}, `Sugestão: ${hours(sheet.total)} de ${hours(sheet.horas_dia)}`),
          rows.length ? h("button", { class: "botao", type: "button", onclick: (e) => copy(text, e.currentTarget) }, icon("copiar"), "Copiar ficha") : null,
          app.editando && rows.length ? h("button", { class: "botao", type: "button", onclick: () => setSheetRow(sheet) },
            app.rascunho.ficha && app.rascunho.ficha.data === day ? "Confirmação no rascunho" : "Confirmar no salvamento") : null),
        rows.length ? h("table", {}, h("thead", {}, h("tr", {}, ["Tipo", "Código", "Início", "Fim", "Total", "Observação", ""].map((c, i) => h("th", { class: i === 4 ? "num" : null }, c)))),
          h("tbody", {}, rows.map((r) => h("tr", {},
            h("td", {}, r.rotulo), h("td", {}, r.codigo || "Sem código"), h("td", {}, r.inicio || ""), h("td", {}, r.fim || ""),
            h("td", { class: "num", title: `estimado ${hours(r.estimado)}` }, app.editando
              ? h("input", { class: "horas", "aria-label": `Horas de ${r.rotulo} ${r.codigo || "sem código"}`, type: "number", min: "0", max: "24", step: "0.25", value: sheetValue(day, r),
                  onchange: (e) => setSheetRow(sheet, r, e.target.value) }) : hours(r.total)),
            h("td", {}, app.editando && r.tipo !== "demanda"
              ? h("textarea", { class: "observacao", rows: 2, "aria-label": `Observação de ${r.rotulo} ${r.codigo || "sem código"}`, onchange: (e) => setSheetRow(sheet, r, null, e.target.value) }, sheetText(day, r))
              : r.observacao, r.complemento ? h("details", {}, h("summary", {}, "Complemento local"), h("div", { class: "markdown" }, markdown(r.complemento))) : null),
            h("td", {}, h("button", { class: "botao", type: "button", onclick: (e) => copy(r.observacao, e.currentTarget) }, icon("copiar"), "Copiar"))))))
          : h("p", { class: "vazio" }, "Nenhuma hora que conta na ficha neste dia."),
        h("h2", {}, "Extras (fora do total)"),
        sheet.extras.length ? h("table", {}, h("tbody", {}, sheet.extras.map((e) => h("tr", {},
          h("td", {}, h("button", { class: "link", type: "button", onclick: () => openTask(e.tarefa) }, e.titulo)), h("td", { class: "num" }, hours(e.horas))))))
          : h("p", { class: "vazio" }, "Nenhum extra."));
    },
  },
  historico: {
    titulo: "Histórico",
    descricao: "Ações do agente e do quadro, com as mudanças que ainda precisam de análise.",
    icone: "historico",
    async render(estado) {
      const limit = app.historicoLimite || 200;
      const data = await api("/api/historico?limite=" + limit);
      const onlyPending = pref("historico.pendentes", "0") === "1";
      const origin = pref("historico.origem", "");
      const titles = Object.fromEntries(estado.tarefas.map((t) => [t.id, t.titulo]));
      const search = (app.busca || "").trim().toLowerCase();
      const rows = data.eventos.filter((e) => (!onlyPending || e.pendente) && (!origin || e.origem === origin) &&
        (!search || [when(e.ts), e.origem, e.acao, titles[e.tarefa], eventDetail(e, titles)].join(" ").toLowerCase().includes(search)));
      const actions = {
        criar: ["tarefa", "Tarefa criada"], editar: ["editar", "Tarefa atualizada"],
        mover: ["seta", "Card movido"], reordenar: ["camadas", "Ordem ajustada"],
        iniciar: ["alvo", "Tarefa iniciada"], horas: ["ficha", "Horas registradas"],
        analise: ["check", "Ações analisadas"], capturar: ["camadas", "Tarefas capturadas"],
        responder: ["pergunta", "Pergunta respondida"], arquivar: ["arquivado", "Tarefa arquivada"],
        coluna: ["quadro", "Coluna atualizada"], ficha: ["ficha", "Ficha atualizada"],
        complemento: ["cadeado", "Complemento atualizado"],
      };
      app.contagem = rows.length;
      return h("section", {},
        h("div", { class: "filtros" },
          h("span", {}, icon("historico"), ` ${data.total} ações · ${data.pendentes} não analisadas`),
          switchInput("Só não analisadas", onlyPending, (e) => { setPref("historico.pendentes", e.target.checked ? "1" : "0"); render(); }),
          h("label", {}, "Origem ", h("select", { onchange: (e) => { setPref("historico.origem", e.target.value); render(); } },
            [["", "Todas"], ["agente", "Agente"], ["quadro", "Quadro"]].map(([v, n]) => h("option", { value: v, selected: v === origin }, n))))),
        rows.length ? h("ol", { class: "historico-lista", "aria-label": "Ações registradas" }, rows.map((event) => {
          const action = actions[event.acao] || ["historico", event.acao];
          const detail = eventDetail(event, titles);
          const source = event.origem === "agente" ? "Agente" : event.origem === "quadro" ? "Quadro" : event.origem;
          return h("li", { class: "evento" + (event.pendente ? " pendente" : "") },
            h("div", { class: "evento-icone", title: action[1] }, icon(action[0])),
            h("div", { class: "evento-corpo" },
              h("div", { class: "evento-topo" }, h("strong", { title: event.acao }, action[1]),
                event.pendente ? pill("Não analisada", "orange", { icon: "alerta" }) : null,
                h("time", { class: "evento-hora", datetime: event.ts }, when(event.ts))),
              event.tarefa ? h("button", { class: "link titulo", type: "button", onclick: () => openTask(event.tarefa) }, titles[event.tarefa] || event.tarefa)
                : event.coluna ? h("span", {}, columnName(event.coluna)) : null,
              h("div", { class: "evento-detalhe" }, source, detail ? " · " + detail : "")));
        }))
          : emptyState("Nenhuma ação com esses filtros", "Tente outra origem ou desmarque o filtro de ações não analisadas."),
        data.total > limit ? h("p", {}, h("button", { class: "botao", type: "button", onclick: () => { app.historicoLimite = limit + 200; render(); } }, "Carregar mais")) : null);
    },
  },
};
const ORDER = ["hoje", "quadro", "epicos", "prazos", "perguntas", "semana", "ficha", "historico"];

function deadlineMonth(iso, delta = 0) {
  const date = new Date(iso.slice(0, 7) + "-01T12:00:00Z");
  date.setUTCMonth(date.getUTCMonth() + delta);
  return date.toISOString().slice(0, 10);
}

function deadlineCalendar(tasks, today) {
  const month = app.prazoMes || deadlineMonth(today);
  const start = new Date(month + "T12:00:00Z");
  const offset = (start.getUTCDay() + 6) % 7;
  const count = new Date(Date.UTC(start.getUTCFullYear(), start.getUTCMonth() + 1, 0)).getUTCDate();
  const groups = new Map();
  for (const task of tasks) {
    if (!groups.has(task.prazo)) groups.set(task.prazo, []);
    groups.get(task.prazo).push(task);
  }
  const showMonth = (value, control) => {
    app.prazoMes = value;
    app.prazoDia = null;
    render().then(() => document.querySelector(`[data-calendar-nav="${control}"]`)?.focus({ preventScroll: true }));
  };
  const selectDay = (day) => {
    app.prazoDia = app.prazoDia === day ? null : day;
    render().then(() => {
      const agenda = document.getElementById("prazos-agenda-titulo");
      agenda?.focus({ preventScroll: true });
      agenda?.scrollIntoView({ block: "nearest" });
    });
  };
  const navigateDay = (event, iso) => {
    const steps = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 };
    if (!(event.key in steps)) return;
    event.preventDefault();
    const next = new Date(iso + "T12:00:00Z");
    next.setUTCDate(next.getUTCDate() + steps[event.key]);
    const day = next.toISOString().slice(0, 10);
    const focus = () => document.querySelector(`[data-calendar-day="${day}"]`)?.focus({ preventScroll: true });
    if (day.slice(0, 7) !== month.slice(0, 7)) {
      app.prazoMes = deadlineMonth(day);
      app.prazoDia = null;
      render().then(focus);
    } else focus();
  };
  const title = start.toLocaleDateString("pt-BR", { month: "long", year: "numeric", timeZone: "UTC" });
  const monthTasks = tasks.filter((t) => t.prazo.slice(0, 7) === month.slice(0, 7)).length;
  return h("section", { class: "calendario caixa", "aria-labelledby": "calendario-mes" },
    h("header", { class: "calendario-topo" },
      h("div", {}, h("h2", { id: "calendario-mes" }, title[0].toUpperCase() + title.slice(1)),
        h("span", { class: "vazio" }, `${monthTasks} prazo${monthTasks === 1 ? "" : "s"} neste mês`)),
      h("div", { class: "calendario-nav" },
        h("button", { class: "botao-icone", type: "button", "aria-label": "Mês anterior", "data-calendar-nav": "anterior", onclick: () => showMonth(deadlineMonth(month, -1), "anterior") }, "‹"),
        h("button", { class: "botao", type: "button", "data-calendar-nav": "hoje", onclick: () => showMonth(deadlineMonth(today), "hoje") }, "Hoje"),
        h("button", { class: "botao-icone", type: "button", "aria-label": "Próximo mês", "data-calendar-nav": "proximo", onclick: () => showMonth(deadlineMonth(month, 1), "proximo") }, "›"))),
    h("div", { class: "calendario-semana", "aria-hidden": "true" }, ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"].map((day) => h("span", {}, day))),
    h("div", { class: "calendario-grade", role: "group", "aria-label": "Dias de " + title },
      Array.from({ length: Math.ceil((offset + count) / 7) * 7 }, (_, index) => {
        const number = index - offset + 1;
        if (number < 1 || number > count) return h("div", { class: "calendario-vazio", "aria-hidden": "true" });
        const day = month.slice(0, 7) + "-" + String(number).padStart(2, "0");
        const due = groups.get(day) || [];
        const label = new Date(day + "T12:00:00Z").toLocaleDateString("pt-BR", { dateStyle: "full", timeZone: "UTC" });
        return h("button", { class: "calendario-dia" + (day === today ? " hoje" : "") + (due.length && day < today ? " atrasado" : ""),
          type: "button", "data-calendar-day": day, "aria-label": `${label}: ${due.length} prazo${due.length === 1 ? "" : "s"}`,
          "aria-current": day === today ? "date" : null, "aria-pressed": String(app.prazoDia === day),
          onclick: () => selectDay(day), onkeydown: (event) => navigateDay(event, day) },
          h("span", { class: "calendario-dia-topo" }, h("time", { datetime: day }, number), due.length ? h("span", { class: "contador" }, due.length) : null),
          h("span", { class: "calendario-tarefas", "aria-hidden": "true" }, due.slice(0, 2).map((task) => h("span", {}, task.titulo)), due.length > 2 ? h("small", {}, `+${due.length - 2}`) : null));
      })));
}

function hours(value) {
  const n = Math.round((value || 0) * 100) / 100;
  return (Number.isInteger(n) ? n : n.toFixed(2).replace(/0$/, "")).toString().replace(".", ",") + "h";
}

function weekday(iso) {
  return ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"][new Date(iso + "T12:00:00").getDay()];
}

function shiftDate(iso, days) {
  const date = new Date(iso + "T12:00:00");
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function dayNav(view, current, step, title) {
  const go = (value) => { app[view] = value; render(); };
  return h("div", { class: "filtros" },
    h("button", { class: "botao", type: "button", "data-focus": "data-anterior", "aria-label": step === 7 ? "Semana anterior" : "Dia anterior", disabled: !!SNAPSHOT, onclick: () => go(shiftDate(current, -step)) }, "←"),
    h("strong", {}, title),
    h("button", { class: "botao", type: "button", "data-focus": "data-proxima", "aria-label": step === 7 ? "Próxima semana" : "Próximo dia", disabled: !!SNAPSHOT, onclick: () => go(shiftDate(current, step)) }, "→"),
    h("button", { class: "botao", type: "button", "data-focus": "data-hoje", disabled: !!SNAPSHOT, onclick: () => go(app.estado.hoje) }, "Hoje"));
}

function when(ts) {
  if (!ts) return "";
  const [date, time] = ts.split("T");
  return `${fmtDate(date)} ${time.slice(0, 5)}`;
}

function eventDetail(e, titles) {
  if (e.acao === "analise") return `${(e.eventos || []).length} ação(ões): ${e.resultado || ""}`;
  if (e.de && e.para) return `${columnName(e.de)} → ${columnName(e.para)}`;
  if (e.campos) return e.campos.join(", ");
  if (e.acao === "capturar") return `${(e.criadas || []).length} criada(s), ${(e.atualizadas || []).length} atualizada(s)`;
  if (e.horas) return hours(e.horas);
  return e.resultado || e.coluna || "";
}

async function copy(text, button) {
  try {
    await navigator.clipboard.writeText(text);
    const old = [...button.childNodes];
    fill(button, icon("check"), "Copiado");
    setTimeout(() => { fill(button, old); }, 1500);
  } catch (error) {
    window.prompt("Copie o texto:", text);
  }
}

function currentView() {
  const name = location.hash.replace("#", "");
  return VIEWS[name] ? name : ORDER[0];
}

function renderViewHeader(name) {
  if (app.headerView !== name) {
    document.getElementById("visao-titulo").textContent = VIEWS[name].titulo;
    fill(document.getElementById("visao-icone"), icon(VIEWS[name].icone));
    document.title = VIEWS[name].titulo + " · YABook Tasks";
    app.headerView = name;
  }
  const date = document.getElementById("hoje-data");
  if (date.dateTime !== app.estado.hoje) {
    date.dateTime = app.estado.hoje;
    fill(date, icon("calendario"), new Date(app.estado.hoje + "T12:00:00").toLocaleDateString("pt-BR", { day: "numeric", month: "short", timeZone: "America/Sao_Paulo" }));
  }
}

function renderTabs() {
  const nav = document.getElementById("abas");
  const current = currentView();
  const counts = { perguntas: app.estado.perguntas.length, prazos: app.estado.prazos.length, historico: app.estado.eventos_pendentes };
  if (!nav.children.length) {
    fill(nav, ORDER.map((name, index) => h("button", {
      type: "button", class: "nav-item", title: `${VIEWS[name].titulo} (Alt+${index + 1})`, "data-view": name, "aria-keyshortcuts": `Alt+${index + 1}`,
      onclick: () => { location.hash = name; }, onkeydown: (event) => {
        let target = index;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") target = (index + 1) % ORDER.length;
        else if (event.key === "ArrowLeft" || event.key === "ArrowUp") target = (index - 1 + ORDER.length) % ORDER.length;
        else if (event.key === "Home") target = 0;
        else if (event.key === "End") target = ORDER.length - 1;
        else return;
        event.preventDefault();
        nav.children[target].focus();
        location.hash = ORDER[target];
      },
    }, icon(VIEWS[name].icone), h("span", { class: "nav-texto" }, VIEWS[name].titulo), h("span", { class: "contador", "data-count": name }))));
  }
  for (const button of nav.children) {
    const name = button.dataset.view;
    if (name === current) button.setAttribute("aria-current", "page");
    else button.removeAttribute("aria-current");
    button.tabIndex = name === current ? 0 : -1;
    const count = button.querySelector(".contador");
    count.textContent = counts[name] || "";
    count.hidden = !counts[name];
  }
  if (app.tabsView !== current) {
    nav.querySelector('[aria-current="page"]').scrollIntoView({ block: "nearest", inline: "nearest" });
    app.tabsView = current;
  }
}

function announce(message) {
  const feedback = document.getElementById("feedback");
  if (!feedback) return;
  clearTimeout(app.feedbackTimer);
  feedback.textContent = message;
  app.feedbackTimer = setTimeout(() => { feedback.textContent = ""; }, 3500);
}

function emptyState(title, description, action) {
  return h("div", { class: "estado-vazio" }, icon("quadro"), h("h3", {}, title),
    description ? h("p", {}, description) : null, action || null);
}

function loadingState() {
  return h("div", { class: "carregando", role: "status" }, h("p", { class: "vazio" }, "Carregando…"),
    h("div", { class: "esqueleto-pilha", "aria-hidden": "true" }, Array.from({ length: 3 }, () => h("div", { class: "esqueleto" }))));
}

function rememberControl() {
  const focused = document.activeElement;
  for (const group of ["opcoes", "edicao", "conteudo"]) {
    const container = document.getElementById(group);
    if (!container.contains(focused)) continue;
    const controls = [...container.querySelectorAll("button, input, select")];
    return { node: focused, group, key: focused.dataset.focus, id: focused.id, index: controls.indexOf(focused) };
  }
  return null;
}

function restoreControl(saved) {
  if (!saved || saved.node.isConnected || document.activeElement !== document.body) return;
  const container = document.getElementById(saved.group);
  const controls = [...container.querySelectorAll("button, input, select")];
  const target = controls.find((node) => (saved.id && node.id === saved.id) || (saved.key && node.dataset.focus === saved.key)) || controls[saved.index];
  if (target && !target.disabled) target.focus({ preventScroll: true });
}

function prepareTables(node, name) {
  const tables = [...(node.tagName === "TABLE" ? [node] : []), ...node.querySelectorAll("table")];
  for (const table of tables) {
    if (table.parentElement?.classList.contains("tabela-rolagem")) continue;
    const title = "Tabela de " + VIEWS[name].titulo;
    table.setAttribute("aria-label", title);
    const wrapper = h("div", { class: "tabela-rolagem", tabindex: "0", role: "region", "aria-label": title });
    if (table === node) { wrapper.append(table); node = wrapper; }
    else { table.replaceWith(wrapper); wrapper.append(table); }
  }
  return node;
}

async function render() {
  if (!app.estado) return;
  const request = app.renderRequest = (app.renderRequest || 0) + 1;
  const savedFocus = rememberControl();
  renderTabs();
  const name = currentView();
  renderViewHeader(name);
  const main = document.getElementById("conteudo");
  main.dataset.view = name;
  const changedView = app.view !== name;
  const oldBoard = !changedView && main.querySelector(".quadro");
  const scroll = oldBoard ? { x: oldBoard.scrollLeft, mainX: main.scrollLeft, mainY: main.scrollTop,
    columns: [...oldBoard.querySelectorAll(".coluna")].map((n) => [n.dataset.coluna, n.querySelector(".itens").scrollTop]) } : null;
  app.view = name;
  main.classList.toggle("quadro-ativo", name === "quadro");
  main.setAttribute("aria-busy", "true");
  const filter = document.querySelector(".filtro");
  filter.hidden = name === "semana" || name === "ficha";
  document.getElementById("filtro").setAttribute("aria-label", name === "historico" ? "Filtrar histórico" : "Filtrar tarefas");
  document.getElementById("filtro").placeholder = name === "historico" ? "Buscar nas ações carregadas…" : "Buscar nesta visão…";
  const estado = effectiveState();
  fill(document.getElementById("opcoes"), VIEWS[name].opcoes ? VIEWS[name].opcoes(estado) : []);
  app.contagem = null;
  let loading;
  try {
    renderToolbar();
    restoreControl(savedFocus);
    const result = VIEWS[name].render(estado);
    const asynchronous = result && typeof result.then === "function";
    if (asynchronous) loading = setTimeout(() => {
      if (request === app.renderRequest) main.replaceChildren(loadingState());
    }, 120);
    let node = asynchronous ? await result : result;
    if (request !== app.renderRequest) return;
    clearTimeout(loading);
    node = prepareTables(node, name);
    fill(main, node);
    if (scroll) {
      const board = main.querySelector(".quadro");
      if (board) {
        board.scrollLeft = scroll.x;
        for (const column of board.querySelectorAll(".coluna")) {
          const saved = scroll.columns.find(([id]) => id === column.dataset.coluna);
          if (saved) column.querySelector(".itens").scrollTop = saved[1];
        }
      }
      main.scrollLeft = scroll.mainX; main.scrollTop = scroll.mainY;
    } else if (changedView) { main.scrollTop = 0; main.scrollLeft = 0; }
    if (changedView) {
      main.classList.remove("entrando");
      requestAnimationFrame(() => { if (request === app.renderRequest) main.classList.add("entrando"); });
      document.getElementById("anuncio").textContent = "Visão " + VIEWS[name].titulo;
    }
  } catch (error) {
    if (request !== app.renderRequest) return;
    main.replaceChildren(h("div", { class: "aviso erro", role: "alert" }, h("p", {}, "Não foi possível carregar esta visão: " + error.message),
      h("button", { class: "botao", type: "button", onclick: render }, "Tentar novamente")));
  } finally {
    clearTimeout(loading);
    if (request === app.renderRequest) main.setAttribute("aria-busy", "false");
  }
  if (request !== app.renderRequest) return;
  restoreControl(savedFocus);
  document.getElementById("contagem").textContent = app.contagem === null || app.contagem === undefined ? "" : String(app.contagem);
}

const THEMES = [["auto", "Tema: automático", "auto"], ["light", "Tema: claro", "sol"], ["dark", "Tema: escuro", "lua"]];

function renderNavigation() {
  let saved = app.navPreference;
  try { saved = localStorage.getItem("yabook.navegacao") || saved; } catch (error) { /* preferência só nesta página */ }
  const compact = saved ? saved === "compacta" : matchMedia("(max-width: 1190px)").matches;
  document.documentElement.dataset.nav = compact ? "compacta" : "expandida";
  const button = document.getElementById("compactar");
  button.setAttribute("aria-expanded", String(!compact));
  button.title = compact ? "Expandir navegação" : "Compactar navegação";
  button.setAttribute("aria-label", button.title);
  fill(button, icon("painel"));
}

function renderTheme() {
  const current = pref("tema", "auto");
  const [, title, iconName] = THEMES.find((t) => t[0] === current) || THEMES[0];
  const button = document.getElementById("tema");
  button.title = title + " (clique para trocar)";
  button.setAttribute("aria-label", button.title);
  fill(button, icon(iconName));
  if (current === "auto") delete document.documentElement.dataset.theme;
  else document.documentElement.dataset.theme = current;
}

function cycleTheme() {
  const index = THEMES.findIndex((t) => t[0] === pref("tema", "auto"));
  setPref("tema", THEMES[(index + 1) % THEMES.length][0]);
  renderTheme();
}

async function refresh() {
  const request = app.refreshRequest = (app.refreshRequest || 0) + 1;
  try {
    const state = await api("/api/estado");
    if (request !== app.refreshRequest) return;
    app.estado = state;
    app.cache = {};
    document.getElementById("maquina").textContent = app.estado.maquina || "local";
    const open = app.estado.tarefas.filter((t) => t.tipo !== "pergunta" && !["concluido", "arquivado"].includes(t.papel)).length;
    document.getElementById("resumo").textContent = `${open} abertas · ${app.estado.epicos.length} épicos`;
    document.getElementById("resumo").title = "Atualizado às " + new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit", timeZone: "America/Sao_Paulo" });
    await render();
  } catch (error) {
    if (request !== app.refreshRequest) return;
    const main = document.getElementById("conteudo");
    main.setAttribute("aria-busy", "false");
    main.replaceChildren(h("div", { class: "aviso erro", role: "alert" }, h("p", {}, "Falha ao ler as tarefas: " + error.message),
      h("button", { class: "botao", type: "button", onclick: refresh }, "Tentar novamente")));
  }
}

function listen() {
  const dot = document.getElementById("conexao");
  const connection = (className, message) => {
    dot.className = "ponto " + className; dot.title = message; dot.setAttribute("aria-label", message);
    const status = document.getElementById("conexao-texto");
    status.textContent = SNAPSHOT ? "Cópia estática" : className === "vivo" ? "Ao vivo" : "Reconectando";
    status.title = message;
  };
  if (SNAPSHOT) { connection("", "Cópia estática: dados do momento da exportação"); return; }
  if (!window.EventSource) { connection("offline", "Atualização automática indisponível neste navegador"); return; }
  const source = new EventSource("/api/stream");
  source.addEventListener("pronto", () => { connection("vivo", "Atualização automática ativa"); });
  source.addEventListener("mudou", () => { if (!app.editando) refresh(); else { app.pendente = true; renderToolbar(); } });
  source.onerror = () => { connection("offline", "Servidor indisponível; tentando reconectar"); };
}

window.addEventListener("hashchange", render);
function showShortcuts() {
  showPanel(h("h2", {}, "Atalhos de teclado"), h("p", { class: "vazio" }, "Disponíveis quando você não estiver preenchendo um campo."),
    h("dl", { class: "atalhos" },
      h("dt", {}, h("kbd", {}, "/")), h("dd", {}, "Focar o filtro da visão"),
      h("dt", {}, h("kbd", {}, "Alt"), " + ", h("kbd", {}, "1–8")), h("dd", {}, "Trocar de visão na ordem das abas"),
      h("dt", {}, h("kbd", {}, "←"), " / ", h("kbd", {}, "→"), " / ", h("kbd", {}, "↑"), " / ", h("kbd", {}, "↓")), h("dd", {}, "Trocar de visão com o foco na navegação"),
      h("dt", {}, h("kbd", {}, "Home"), " / ", h("kbd", {}, "End")), h("dd", {}, "Ir à primeira ou à última aba"),
      h("dt", {}, h("kbd", {}, "Enter"), " / ", h("kbd", {}, "Espaço")), h("dd", {}, "Abrir o card em foco"),
      h("dt", {}, h("kbd", {}, "Esc")), h("dd", {}, "Fechar o painel e voltar ao item de origem"),
      h("dt", {}, h("kbd", {}, "?")), h("dd", {}, "Mostrar esta ajuda")));
}

document.addEventListener("keydown", (event) => {
  if (event.defaultPrevented || event.isComposing) return;
  if (event.key === "Escape" && !document.getElementById("painel").hidden) { event.preventDefault(); closePanel(); return; }
  const target = event.target instanceof Element ? event.target : null;
  if (target && target.closest("input, textarea, select, [contenteditable]:not([contenteditable=false])")) return;
  if (event.ctrlKey || event.metaKey) return;
  if (event.altKey) {
    if (!event.shiftKey && /^[1-8]$/.test(event.key)) {
      event.preventDefault(); closePanel(false); location.hash = ORDER[Number(event.key) - 1];
    }
    return;
  }
  if (event.key === "/" && !event.shiftKey) {
    const filter = document.getElementById("filtro");
    if (!filter.closest(".filtro").hidden) { event.preventDefault(); closePanel(false); filter.focus(); filter.select(); }
  } else if (event.key === "?") { event.preventDefault(); showShortcuts(); }
});
// Clique fora do painel fecha; clique que abre outra tarefa apenas troca o conteúdo.
document.addEventListener("click", (event) => {
  const panel = document.getElementById("painel");
  if (app.abrindoPainel) { app.abrindoPainel = false; return; }
  if (!panel.hidden && !panel.contains(event.target)) closePanel(false);
});
document.addEventListener("DOMContentLoaded", () => {
  renderTheme();
  renderNavigation();
  document.getElementById("compactar").addEventListener("click", () => {
    const next = document.documentElement.dataset.nav === "compacta" ? "expandida" : "compacta";
    app.navPreference = next;
    try { localStorage.setItem("yabook.navegacao", next); } catch (error) { /* sem armazenamento persistente */ }
    document.documentElement.dataset.nav = next;
    renderNavigation();
  });
  matchMedia("(max-width: 1190px)").addEventListener("change", renderNavigation);
  const skip = document.querySelector(".pular-conteudo");
  if (skip) skip.addEventListener("click", (event) => {
    event.preventDefault();
    document.getElementById("conteudo").focus();
  });
  document.getElementById("tema").addEventListener("click", cycleTheme);
  const help = document.getElementById("ajuda");
  if (help) help.addEventListener("click", showShortcuts);
  const filter = document.getElementById("filtro");
  filter.addEventListener("input", () => { app.busca = filter.value; clearTimeout(app.buscaTimer); app.buscaTimer = setTimeout(render, 150); });
  app.rascunho = loadDraft();
  app.editando = !SNAPSHOT && draftCount() > 0;
  setInterval(refreshChangeTimes, 60000);
  document.addEventListener("visibilitychange", refreshChangeTimes);
  refresh();
  listen();
  if (!SNAPSHOT && "serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
});

// Edição -----------------------------------------------------------------------
// Rascunho local: {tarefas: {id: {revision, campos, unset, registro}}, colunas: {id: nome}, complementos: [], ficha}.
function emptyDraft() {
  return { tarefas: {}, colunas: {}, complementos: [], ficha: null };
}

function loadDraft() {
  try { return Object.assign(emptyDraft(), JSON.parse(localStorage.getItem("yabook.rascunho") || "{}")); } catch (error) { return emptyDraft(); }
}

function persistDraft() {
  app.draftVersion = (app.draftVersion || 0) + 1;
  try { localStorage.setItem("yabook.rascunho", JSON.stringify(app.rascunho)); } catch (error) { /* sem armazenamento: rascunho só na memória */ }
}

function draftCount() {
  const d = app.rascunho || emptyDraft();
  return Object.keys(d.tarefas).length + Object.keys(d.colunas).length + d.complementos.length + (d.ficha ? 1 : 0);
}

function effectiveState() {
  const estado = app.estado;
  if (!app.editando || !draftCount()) return estado;
  const cached = app.cache.effective;
  if (cached && cached.source === estado && cached.version === app.draftVersion) return cached.value;
  const roles = Object.fromEntries(estado.colunas.map((c) => [c.id, c.papel]));
  const tarefas = estado.tarefas.map((t) => {
    const entry = app.rascunho.tarefas[t.id];
    if (!entry) return t;
    const merged = { ...t, ...entry.campos, editado: true };
    for (const key of entry.unset || []) delete merged[key];
    for (const [key, value] of Object.entries(entry.campos)) if (value === null) delete merged[key];
    merged.papel = roles[merged.coluna];
    return merged;
  });
  const colunas = estado.colunas.map((c) => (app.rascunho.colunas[c.id] ? { ...c, nome: app.rascunho.colunas[c.id] } : c));
  const value = { ...estado, tarefas, colunas };
  app.cache.effective = { source: estado, version: app.draftVersion, value };
  return value;
}

function draftTask(id, campos, extra = {}) {
  if (app.salvando) return;
  const original = app.estado.tarefas.find((t) => t.id === id);
  const entry = app.rascunho.tarefas[id] || { revision: original.revision, campos: {}, unset: [] };
  Object.assign(entry.campos, campos);
  Object.assign(entry, extra);
  app.rascunho.tarefas[id] = entry;
  persistDraft();
}

function clearDrop() {
  document.querySelectorAll(".alvo, .inserir-antes, .inserir-depois").forEach((node) => {
    node.classList.remove("alvo", "inserir-antes", "inserir-depois");
  });
}

function indicateDrop(event) {
  if (!app.dragId) return;
  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
  const column = event.currentTarget;
  const nodes = [...column.querySelectorAll(".card")].filter((n) => n.dataset.id !== app.dragId);
  const before = nodes.find((n) => { const rect = n.getBoundingClientRect(); return event.clientY < rect.top + rect.height / 2; });
  const marker = before || nodes[nodes.length - 1];
  const cls = before ? "inserir-antes" : "inserir-depois";
  if (!column.classList.contains("alvo") || (marker && !marker.classList.contains(cls))) {
    clearDrop();
    column.classList.add("alvo");
    if (marker) marker.classList.add(cls);
  }
}

function dropCard(event, columnId, cards) {
  if (app.salvando) return;
  event.preventDefault();
  const id = event.dataTransfer.getData("text/plain");
  clearDrop();
  app.dragId = null;
  if (!id || !effectiveState().tarefas.some((t) => t.id === id && t.tipo !== "pergunta")) return;
  const target = event.currentTarget;
  const others = cards.filter((t) => t.id !== id);
  let position = others.length;
  [...target.querySelectorAll(".card")].filter((n) => n.dataset.id !== id).forEach((node, index) => {
    const box = node.getBoundingClientRect();
    if (position === others.length && event.clientY < box.top + box.height / 2) position = index;
  });
  const ordered = [...others.slice(0, position), { id }, ...others.slice(position)];
  const state = effectiveState();
  const moving = state.tarefas.find((t) => t.id === id);
  if (pref("quadro.ordem", "recentes") !== "manual") {
    if (moving.coluna === columnId) {
      if (!ordered.every((t, i) => t.id === cards[i]?.id)) announce("Para reordenar na coluna, selecione Ordem manual.");
      return;
    }
    draftTask(id, { coluna: columnId });
    render();
    announce("Tarefa movida no rascunho. Salve para gravar.");
    return;
  }
  if (moving.nivel === "epico") {
    if (moving.coluna === columnId) return;
    draftTask(id, { coluna: columnId });
    render();
    announce("Épico movido no rascunho. Salve para gravar.");
    return;
  }
  // Não normalizar a numeração quando a sequência visível não mudou.
  if (moving.coluna === columnId && ordered.every((t, i) => t.id === cards[i]?.id)) return;
  const all = state.tarefas.filter((t) => t.coluna === columnId && t.tipo !== "pergunta" && t.nivel !== "epico").sort(byOrder);
  const destination = all.filter((t) => t.id !== id);
  const anchor = others[position];
  const previous = others[position - 1];
  const insertAt = anchor ? destination.findIndex((t) => t.id === anchor.id)
    : previous ? destination.findIndex((t) => t.id === previous.id) + 1 : destination.length;
  destination.splice(insertAt, 0, moving);
  if (moving.coluna === columnId && destination.every((t, i) => t.id === all[i]?.id)) return;
  const before = destination[insertAt - 1], after = destination[insertAt + 1];
  const low = before ? (before.ordem || 0) : null;
  const high = after ? (after.ordem || 0) : null;
  const order = low === null ? (high === null ? 1 : high - 1)
    : high === null ? low + 1 : high - low > 1 ? low + 1 : null;
  // Aproveitar espaços entre ordinais; renumerar só se não houver inteiro livre.
  const changes = order === null ? destination.map((t, i) => [t, i + 1]) : [[moving, order]];
  changes.forEach(([current, ordinal]) => {
    const campos = {};
    if (current.coluna !== columnId) campos.coluna = columnId;
    if ((current.ordem || 0) !== ordinal) campos.ordem = ordinal;
    if (Object.keys(campos).length) draftTask(current.id, campos);
  });
  render();
  announce("Tarefa movida no rascunho. Salve para gravar.");
}

function renameColumn(column) {
  if (app.salvando) return;
  const input = h("input", { name: "nome-coluna", value: column.nome, required: true, autocomplete: "off" });
  const form = h("form", { class: "formulario", onsubmit: async (event) => {
    event.preventDefault();
    if (app.salvando) return;
    const name = input.value.trim();
    if (!name) { input.setCustomValidity("Informe um nome para a coluna."); input.reportValidity(); return; }
    const original = app.estado.colunas.find((c) => c.id === column.id);
    if (name === original.nome) delete app.rascunho.colunas[column.id];
    else app.rascunho.colunas[column.id] = name;
    persistDraft();
    closePanel(false);
    await render();
    announce("Nome da coluna atualizado no rascunho. Salve para gravar.");
  } },
    h("label", { class: "campo" }, h("span", {}, "Nome da coluna"), input),
    h("p", { class: "vazio" }, "O papel da coluna permanece o mesmo. A mudança será gravada ao salvar o rascunho."),
    h("button", { class: "botao primario", type: "submit" }, icon("check"), "Aplicar ao rascunho"));
  input.addEventListener("input", () => input.setCustomValidity(""));
  showPanel(h("h2", {}, "Renomear coluna"), form);
  input.focus({ preventScroll: true });
  input.select();
}

function editForm(id) {
  const task = effectiveState().tarefas.find((t) => t.id === id);
  const original = app.estado.tarefas.find((t) => t.id === id);
  const parents = app.estado.tarefas.filter((t) => t.id !== id && ["epico", "historia"].includes(t.nivel));
  const marked = "pessoal_marcado" in task ? (task.pessoal_marcado ? "sim" : "nao") : "auto";
  const field = (name, labelText, input) => h("label", { class: "campo" }, h("span", {}, labelText), input);
  const form = h("form", { class: "formulario", onsubmit: (e) => {
    e.preventDefault();
    if (app.salvando) return;
    const values = Object.fromEntries(new FormData(e.target).entries());
    const campos = {};
    const compare = (key, value, before) => { if ((value ?? "") !== (before ?? "")) campos[key] = value === "" ? null : value; };
    compare("titulo", values.titulo.trim(), original.titulo);
    compare("coluna", values.coluna, original.coluna);
    compare("prazo", values.prazo, original.prazo);
    compare("proximo_passo", values.proximo_passo.trim(), original.proximo_passo);
    compare("ficha", values.ficha.trim(), original.ficha);
    compare("aguardando", values.aguardando.trim(), original.aguardando);
    compare("projeto", values.projeto.trim(), original.projeto);
    compare("demanda", values.demanda.trim(), original.demanda);
    compare("nivel", values.nivel, original.nivel);
    compare("pai", values.pai, original.pai);
    const issues = values.issue.split(",").map((i) => i.trim()).filter(Boolean);
    if (issues.join(",") !== (original.issue || []).join(",")) campos.issue = issues.length ? issues : null;
    const before = "pessoal_marcado" in original ? (original.pessoal_marcado ? "sim" : "nao") : "auto";
    if (values.pessoal !== before) campos.pessoal = values.pessoal === "auto" ? null : values.pessoal === "sim";
    if (!campos.titulo && campos.titulo === null) delete campos.titulo;
    const entry = app.rascunho.tarefas[id];
    const registro = values.registro.trim();
    if (!Object.keys(campos).length && !registro) {
      if (entry) { delete app.rascunho.tarefas[id]; persistDraft(); }
    } else {
      const keep = entry && entry.campos.ordem !== undefined && !("coluna" in campos && campos.coluna !== entry.campos.coluna) ? { ordem: entry.campos.ordem } : {};
      app.rascunho.tarefas[id] = { revision: original.revision, campos: { ...keep, ...campos }, unset: [], ...(registro ? { registro } : {}) };
      persistDraft();
    }
    closePanel();
    render();
    announce("Rascunho atualizado. Use Salvar para gravar as alterações.");
  } },
    h("h2", { style: "margin:0" }, "Editar tarefa"),
    h("p", { class: "vazio", style: "margin:0" }, "Aplique as mudanças ao rascunho e depois use Salvar na barra de filtros."),
    field("titulo", "Título", h("input", { name: "titulo", value: task.titulo, required: true })),
    field("coluna", "Coluna", h("select", { name: "coluna" }, effectiveState().colunas.map((c) => h("option", { value: c.id, selected: c.id === task.coluna }, c.nome)))),
    field("prazo", "Prazo", h("input", { name: "prazo", type: "date", value: task.prazo || "" })),
    field("proximo_passo", "Próximo passo", h("textarea", { name: "proximo_passo", rows: 2 }, task.proximo_passo || "")),
    field("ficha", "Texto na observação da ficha (curto, ex.: tela de clientes em atraso)", h("input", { name: "ficha", value: task.ficha || "" })),
    field("aguardando", "Aguardando (de quem ou do quê; vazio encerra a espera)", h("input", { name: "aguardando", value: task.aguardando || "", placeholder: "ex.: validação de QA" })),
    h("div", { class: "campos-linha" },
      field("projeto", "Projeto", h("input", { name: "projeto", value: task.projeto || "" })),
      field("demanda", label("demanda"), h("input", { name: "demanda", value: task.demanda || "" }))),
    field("issue", "Issues (dono/repo#n, separadas por vírgula)", h("input", { name: "issue", value: (task.issue || []).join(", ") })),
    h("div", { class: "campos-linha" },
      field("nivel", "Nível", h("select", { name: "nivel" }, [["", "—"], ["epico", "Épico"], ["historia", "História"], ["tarefa", "Tarefa"]]
        .map(([v, n]) => h("option", { value: v, selected: (task.nivel || "") === v }, n)))),
      field("pai", "Faz parte de", h("select", { name: "pai" }, h("option", { value: "" }, "—"),
        parents.map((p) => h("option", { value: p.id, selected: p.id === task.pai }, `${p.nivel === "epico" ? "Épico" : "História"}: ${p.titulo}`)))),
      field("pessoal", "Pessoal", h("select", { name: "pessoal" }, [["auto", "Automático"], ["sim", "Sim"], ["nao", "Não"]]
        .map(([v, n]) => h("option", { value: v, selected: marked === v }, n))))),
    field("registro", "Acrescentar ao registro", h("textarea", { name: "registro", rows: 2 }, (app.rascunho.tarefas[id] || {}).registro || "")),
    h("div", { class: "filtros" }, h("button", { class: "botao primario", type: "submit" }, "Aplicar ao rascunho")));
  return form;
}

function sheetValue(day, row) {
  const draft = app.rascunho.ficha;
  if (!draft || draft.data !== day) return row.total;
  const found = draft.linhas.find((r) => r.tipo === row.tipo && String(r.codigo) === String(row.codigo));
  return found ? found.total : row.total;
}

function sheetText(day, row) {
  const draft = app.rascunho.ficha;
  const found = draft && draft.data === day && draft.linhas.find((r) => r.tipo === row.tipo && String(r.codigo) === String(row.codigo));
  return found && found.observacao !== undefined ? found.observacao : row.observacao;
}

function setSheetRow(sheet, row, value, text) {
  if (app.salvando) return;
  const draft = app.rascunho.ficha && app.rascunho.ficha.data === sheet.data ? app.rascunho.ficha : {
    data: sheet.data,
    linhas: sheet.linhas.map((r) => ({ tipo: r.tipo, codigo: r.codigo, total: r.total, observacao: r.observacao })),
    extras: sheet.extras.map((e) => ({ tarefa: e.tarefa, horas: e.horas })),
  };
  if (row) {
    const target = draft.linhas.find((r) => r.tipo === row.tipo && String(r.codigo) === String(row.codigo));
    if (value !== null && value !== undefined) target.total = Math.max(0, Math.min(24, Number(String(value).replace(",", ".")) || 0));
    if (text !== undefined) target.observacao = text;
  }
  app.rascunho.ficha = draft;
  persistDraft();
  render();
}

function renderToolbar() {
  const bar = document.getElementById("edicao");
  const filterBar = document.querySelector(".barra-filtro");
  filterBar.classList.toggle("editando", !!app.editando);
  let help = filterBar.querySelector(".edicao-ajuda");
  if (app.editando && !help) {
    help = h("div", { class: "edicao-ajuda" }, "Rascunho no navegador. Abra um card para editar ou mover pela coluna; Salvar grava as alterações.");
    filterBar.append(help);
  } else if (!app.editando && help) help.remove();
  if (SNAPSHOT || !TOKEN) { bar.replaceChildren(); return; }
  const count = draftCount();
  const items = app.editando ? [
    app.pendente ? h("span", { class: "selo cor-orange", title: "Salve ou descarte para ver as mudanças" }, "repositório mudou") : null,
    h("span", { class: "selo cor-orange" }, count ? `${count} ${count === 1 ? "alteração" : "alterações"} no rascunho` : "Modo Editar"),
    h("button", { id: "descartar", class: "botao", type: "button", disabled: !!app.salvando, onclick: discardDraft }, icon("desfazer"), count ? "Descartar" : "Sair"),
    h("button", { id: "salvar", class: "botao primario", type: "button", disabled: !count || !!app.salvando, onclick: saveDraft }, icon("salvar"), app.salvando ? "Salvando…" : "Salvar"),
  ] : [h("button", { class: "botao", type: "button", onclick: () => { app.editando = true; render(); } }, icon("editar"), "Editar")];
  bar.replaceChildren(...items.filter(Boolean));
}

function discardDraft() {
  if (app.salvando) return;
  if (draftCount() && !window.confirm("Descartar as alterações não salvas?")) return;
  app.rascunho = emptyDraft();
  persistDraft();
  app.editando = false;
  app.pendente = false;
  refresh();
}

async function saveDraft() {
  if (app.salvando || !draftCount()) return;
  app.salvando = true;
  renderToolbar();
  announce("Salvando alterações…");
  const d = app.rascunho;
  const body = {
    tarefas: Object.entries(d.tarefas).map(([id, e]) => ({ id, revision: e.revision, campos: e.campos, unset: e.unset || [], registro: e.registro })),
    colunas: Object.entries(d.colunas).map(([id, nome]) => ({ id, nome })),
    complementos: d.complementos,
    ficha: d.ficha,
  };
  let response, result;
  try {
    response = await fetch("/api/salvar", { method: "POST", headers: { "Content-Type": "application/json", "X-YABook-Token": TOKEN }, body: JSON.stringify(body) });
    result = await response.json();
  } catch (error) {
    app.salvando = false;
    renderToolbar();
    announce("Falha ao salvar. O rascunho continua guardado.");
    return showPanel(h("p", { class: "aviso erro" }, "Servidor indisponível; o rascunho continua guardado. " + error.message));
  }
  app.salvando = false;
  renderToolbar();
  if (response.ok) {
    app.rascunho = emptyDraft();
    persistDraft();
    app.editando = false;
    app.pendente = false;
    await refresh();
    announce("Alterações salvas.");
    return showPanel(
      h("h2", {}, "Salvo"),
      result.aviso ? h("p", { class: "aviso erro" }, result.aviso) : null,
      h("pre", { class: "registro" }, result.resumo),
      h("button", { class: "botao primario", type: "button", onclick: (e) => copy(result.resumo, e.currentTarget) }, icon("copiar"), "Copiar resumo"));
  }
  if (response.status === 409) {
    announce("Conflito ao salvar. Revise as tarefas alteradas em outro lugar.");
    const lost = (result.conflitos || []).map((id) => [id, d.tarefas[id]]);
    for (const [id] of lost) delete d.tarefas[id];
    persistDraft();
    app.pendente = false;
    await refresh();
    return showPanel(h("h2", {}, "Tarefas alteradas em outro lugar"),
      h("p", { class: "aviso erro" }, result.error),
      h("p", {}, "Nada foi gravado. A tela foi recarregada; refaça estas alterações sobre a versão atual:"),
      h("pre", { class: "registro" }, lost.map(([id, e]) => `${id}: ${JSON.stringify(e && e.campos)}${e && e.registro ? " + registro: " + e.registro : ""}`).join("\n")));
  }
  if (response.status === 422) {
    announce("Nada foi gravado. Revise o termo confidencial indicado.");
    return showPanel(h("h2", {}, "Termo confidencial"),
      h("p", { class: "aviso erro" }, result.error + ". Nada foi gravado."),
      h("ul", { class: "perguntas" }, (result.termos || []).map((hit) => h("li", {},
        h("strong", {}, `${hit.id} · ${hit.campo}: `), hit.termos.join(", "), h("div", { class: "passo" }, hit.texto),
        result.base_confidencial && hit.campo !== "titulo" && hit.campo !== "coluna"
          ? h("button", { class: "botao", type: "button", onclick: () => moveToComplement(hit) }, "Mover para o complemento confidencial")
          : h("div", { class: "passo" }, "Reescreva este texto sem o termo.")))));
  }
  return showPanel(h("p", { class: "aviso erro" }, result.error || "Falha ao salvar"));
}

function moveToComplement(hit) {
  const entry = app.rascunho.tarefas[hit.id];
  if (entry) {
    if (hit.campo === "registro") delete entry.registro;
    else entry.campos[hit.campo] = null;
  }
  app.rascunho.complementos.push({ id: hit.id, texto: `${hit.campo}: ${hit.texto}` });
  persistDraft();
  closePanel();
  render();
}

function showPanel(...children) {
  const panel = document.getElementById("painel");
  beginPanel();
  panel.setAttribute("aria-busy", "false");
  const [first, ...rest] = children.flat(Infinity).filter(Boolean);
  const title = first && first.tagName === "H2" ? first.textContent : "YABook Tasks";
  fill(panel,
    panelHeader(title),
    h("div", { class: "painel-corpo" }, first && first.tagName === "H2" ? rest : [first, ...rest]));
  focusPanel();
}
