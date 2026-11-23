// YABook Tasks: site local sem build. Lê o estado do servidor (ou o retrato
// embutido por `task board --output`) e atualiza por SSE quando os arquivos mudam.
"use strict";

const SNAPSHOT = window.YABOOK_SNAPSHOT || null;
const TOKEN = (document.querySelector('meta[name="yabook-token"]') || {}).content || "";
const app = { estado: null, view: null, cache: {}, anexosRascunho: {} };

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
  clipe: '<path d="m6.1 8.9 4.2-4.3a1.4 1.4 0 0 1 2 2l-5.5 5.5a2.7 2.7 0 1 1-3.8-3.8l5.8-5.8" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
  regua: '<path d="m2.2 9.6 7.4-7.4 4.2 4.2-7.4 7.4zM7.5 4.3l1.6 1.6M5.7 6.1l1.2 1.2M3.9 7.9l1.6 1.6" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>',
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
  return h("label", { class: "switch" }, h("span", {}, text), h("input", { type: "checkbox", role: "switch", checked, onchange }),
    h("span", { class: "switch-trilho", "aria-hidden": "true" }));
}

function issueRef(task) {
  const first = (task.issue || [])[0];
  if (!first) return null;
  const [repo, number] = first.split("#");
  return { repo: repo.split("/").pop(), number, full: first };
}

function stateIcon(task) {
  if (task.tipo === "pergunta") return icon("pergunta", "estado-pergunta");
  const [name, , symbol] = LEVEL[task.nivel] || LEVEL.tarefa;
  const state = task.papel === "concluido" ? "fechado" : task.papel === "arquivado" ? "arquivado" : "aberto";
  const title = name[0].toUpperCase() + name.slice(1) + " · " + columnName(task.coluna);
  const node = icon(symbol, "estado-" + state);
  node.setAttribute("role", "img");
  node.setAttribute("aria-label", title);
  node.setAttribute("title", title);
  return node;
}

function origin(task) {
  const tag = task.numero ? `@${task.numero} · ` : "";
  return tag + originText(task);
}

function originText(task) {
  const ref = issueRef(task);
  if (ref) return `${ref.repo} #${ref.number}`;
  const own = task.demanda ? ["demanda", task.demanda] : task.projeto && task.tipo === "projeto" ? ["projeto", task.projeto] : null;
  if (own) return `${label(own[0])} ${own[1]}`;
  return label(task.tipo);
}

const LEVEL = { epico: ["épico", "purple", "epicos"], historia: ["história", "blue", "livro"], tarefa: ["tarefa", "gray", "tarefa"] };

function badges(task, options = {}) {
  const items = [];
  if (options.status) items.push(h("span", { class: "selo neutro forte", title: "Status" }, h("span", { class: `status papel-${task.papel}` }), columnName(task.coluna)));
  if (task.nivel && !options.semNivel) items.push(pill(LEVEL[task.nivel][0], LEVEL[task.nivel][1]));
  const ref = issueRef(task);
  if (task.size && options.compacto && !options.semSize) items.push(sizeNumber(task));
  if (task.codigo && (!ref || task.codigo !== ref.full) && !options.semCodigo) {
    items.push(pill(task.codigo, "blue", { title: task.pessoal ? "Código" : "Código na ficha", icon: "repo" }));
  }
  if (task.pessoal && !options.semPessoal) items.push(pill("pessoal", "pink", { title: "Sem numeração da empresa" }));
  if (task.prazo && !CLOSED.includes(task.papel) && !options.semPrazo) {
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
      items.push(h("span", { class: "selo neutro forte", title: "Faz parte de" }, stateIcon(parent),
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

// Apresentação do quadro e do calendário: no celular, lista e agenda por padrão.
const NARROW = () => matchMedia("(max-width: 760px)").matches;
function boardMode() { return pref("quadro.modo", NARROW() ? "lista" : "quadro"); }
function calendarMode() { return pref("prazos.modo", NARROW() ? "agenda" : "mes"); }

// Fração "feitas / total" e uma linha tracejada com um traço por história; os concluídos ficam preenchidos.
function segments(done, total) {
  return h("div", { class: "progresso", title: `${done} de ${total} histórias concluídas` },
    h("span", { class: "progresso-fracao" }, `${done} / ${total}`),
    total ? h("div", { class: "tracos-progresso", role: "progressbar", "aria-valuemin": "0", "aria-valuemax": String(total), "aria-valuenow": String(done),
      "aria-label": `${done} de ${total} histórias concluídas` },
      Array.from({ length: total }, (_, i) => h("i", { class: i < done ? "feito" : null }))) : null);
}

function epicProgress(task) {
  const epic = (app.estado.epicos || []).find((e) => e.id === task.id);
  return epic && epic.historias ? segments(epic.concluidas, epic.historias) : null;
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
  const tasks = effectiveState().tarefas;
  const parent = task.pai ? tasks.find((t) => t.id === task.pai) : null;
  const issue = issueRef(task);
  const demand = cardDemand(task, tasks);
  return h("div", { class: `card papel-${task.papel}` + (task.nivel === "epico" ? " card-epico" : "") + (task.prazo && daysUntil(task.prazo) < 0 && !CLOSED.includes(task.papel) ? " prazo-vencido" : "") + (task.editado ? " editado" : ""), role: "button", tabindex: "0", "data-id": task.id,
    title: [task.titulo, task.descricao, changeText(changeStamp(task))].filter(Boolean).join("\n\n"),
    draggable: editable ? "true" : null,
    ondragstart: editable ? (e) => { app.dragId = task.id; e.dataTransfer.setData("text/plain", task.id); e.dataTransfer.effectAllowed = "move"; e.currentTarget.classList.add("arrastando"); } : null,
    ondragend: editable ? () => { app.dragId = null; clearDrop(); document.querySelectorAll(".arrastando").forEach((n) => n.classList.remove("arrastando")); } : null,
    onclick: () => openTask(task.id), onkeydown: (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openTask(task.id); }
    } },
    // Card compacto com título, rótulos e rodapé com identificadores.
    // Próximo passo, descrição e última alteração ficam no painel (e no título ao passar o mouse).
    h("div", { class: "card-titulo" }, task.titulo),
    cardMeta(task, parent, options, demand && (issue || String(demand) !== String(task.codigo)) ? demand : null, tasks),
    task.nivel === "epico" ? epicProgress(task) : null,
    h("footer", { class: "card-rodape" },
      h("span", { class: "card-identificadores" },
        h("span", { class: "card-chave" }, stateIcon(task), cardKey(task, issue))),
      h("span", { class: "card-sinais" },
        task.pessoal ? signal("usuario", "Pessoal") : null,
        task.confidencial ? signal("cadeado", task.confidencial === "disponivel" ? "Referência confidencial disponível nesta máquina" : "Base confidencial ausente nesta máquina") : null,
        task.perguntas_abertas ? signal("pergunta", `${task.perguntas_abertas} perguntas abertas`, String(task.perguntas_abertas)) : null)));
}

const CARD_DATE = new Intl.DateTimeFormat("pt-BR", { day: "2-digit", month: "short", timeZone: "UTC" });
const FULL_DATE = new Intl.DateTimeFormat("pt-BR", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });

// Data curta nas listas ("27 nov"; ano só quando difere do atual); a completa fica no title e no detalhe.
function cardDate(day) {
  const date = new Date(day + "T12:00:00Z");
  const short = CARD_DATE.format(date).replace(/\s*de\s*/, " ").replace(".", "");
  return day.slice(0, 4) === String(new Date().getFullYear()) ? short : `${short} ${day.slice(0, 4)}`;
}

function fullDate(day) {
  return FULL_DATE.format(new Date(day + "T12:00:00Z"));
}

function cardDemand(task, tasks) {
  const seen = new Set();
  let current = task;
  while (current && !seen.has(current.id)) {
    if (current.demanda) return current.demanda;
    seen.add(current.id);
    current = current.pai ? tasks.find((item) => item.id === current.pai) : null;
  }
  return null;
}

// Prioriza a issue vinculada e mantém o número interno como referência secundária.
function cardKey(task, ref) {
  const code = ref ? ref.full.split("/").pop() : task.codigo;
  const number = task.numero ? `@${task.numero}` : null;
  if (!code) return h("span", { class: "card-codigo" }, number || label(task.tipo));
  return [h("span", { class: "card-codigo", title: ref?.full || null }, code),
    number ? h("span", { class: "card-numero" }, number) : null];
}

function cardMeta(task, parent, options, demand = null, tasks = []) {
  const lines = [], selos = [];
  if (task.size) selos.push(sizeNumber(task, true));
  const attachments = task.anexos_total;
  if (attachments > 0) {
    const title = attachments === 1 ? "1 anexo" : `${attachments} anexos`;
    selos.push(h("span", { class: "card-anexos", role: "img", title, "aria-label": title },
      icon("clipe"), String(attachments)));
  }
  if (options.status) lines.push(h("span", { class: "card-status", title: "Status" }, h("span", { class: `status papel-${task.papel}` }), columnName(task.coluna)));
  if (task.prazo && !CLOSED.includes(task.papel)) {
    const days = daysUntil(task.prazo);
    lines.push(h("span", { class: "card-data" + (days < 0 ? " vencida" : days <= 2 ? " proxima" : ""), title: "Prazo: " + fullDate(task.prazo) }, cardDate(task.prazo)));
  } else if (task.papel === "concluido" && task.atualizada) {
    lines.push(h("span", { class: "card-data", title: "Concluída em " + fullDate(task.atualizada.slice(0, 10)) }, "Concluída em " + cardDate(task.atualizada.slice(0, 10))));
  }
  // Rodada de ajuste a partir da segunda (a primeira entrega é a rodada 1).
  if (task.rodada > 1 && !CLOSED.includes(task.papel)) {
    selos.push(h("span", { class: "card-rodada", title: `Rodada ${task.rodada} de ajuste: ${task.rodada - 1} retorno(s) da validação` },
      icon("seta"), h("span", {}, `Rodada ${task.rodada}`)));
  }
  if (task.aguardando && !CLOSED.includes(task.papel)) {
    const days = waitingDays(task);
    selos.push(h("span", { class: "card-espera" + (days >= 3 ? " longa" : ""),
      title: `Aguardando: ${task.aguardando} (desde ${fmtDate(task.aguardando_desde || app.estado.hoje)})` },
      icon("ficha"), h("span", {}, `Aguardando${days ? ` · ${days}d` : ""}`)));
  }
  const parentCode = parent && !options.semPai ? parent.codigo || parent.projeto || parent.demanda : null;
  if (parent && !options.semPai) {
    // Só o código do pai (@n e projeto/demanda); o título fica no texto ao passar o mouse.
    selos.push(h("button", { class: "card-pai", type: "button", title: "Abrir " + parent.titulo,
      onclick: (e) => { e.stopPropagation(); openTask(parent.id); }, onkeydown: (e) => e.stopPropagation() },
      icon(parent.nivel === "epico" ? "epicos" : "relacoes"),
      h("span", { class: "card-pai-numero" }, [parent.numero ? `@${parent.numero}` : null, parentCode].filter(Boolean).join(" · "))));
  }
  // Demanda própria ou herdada no mesmo desenho do pai; omitida quando o selo do pai já mostra o código.
  if (demand && String(parentCode ?? "") !== String(demand)) {
    const owner = sheetTask({ tipo: "demanda", codigo: demand, tarefas: [task.id] }, tasks);
    const content = [icon("etiqueta"), h("span", { class: "card-pai-numero" }, `Demanda ${demand}`)];
    selos.push(owner && owner.id !== task.id
      ? h("button", { class: "card-demanda", type: "button", title: "Abrir " + owner.titulo,
        onclick: (e) => { e.stopPropagation(); openTask(owner.id); }, onkeydown: (e) => e.stopPropagation() }, content)
      : h("span", { class: "card-demanda", title: "Demanda " + demand }, content));
  }
  if (selos.length) lines.push(h("div", { class: "card-selos" }, selos));
  return lines.length ? h("div", { class: "card-meta" }, lines) : null;
}

function sizeNumber(task, withIcon = false) {
  return h("span", { class: `size-numero size-${task.size}`, title: sizeTitle(task), "aria-label": sizeTitle(task) },
    withIcon ? icon("regua") : null, String(task.size));
}

function sizeTitle(task) {
  return `Tamanho ${task.size}: ${["", "menos de uma hora com agente", "uma sessão longa ou duas curtas", "cerca de um dia ou validação fora do código",
    "vários dias, outra equipe, QA ou retrabalho", "semana ou mais; dividir"][task.size]}` + (task.size_manual ? " · marcado no quadro" : " · estimado pelo agente");
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
  return h("span", { class: "estado-grande aberto", title: "Situação da tarefa; a etapa do fluxo aparece em Status" }, icon("aberto"), "Situação: aberta");
}

function sideSection(title, ...content) {
  const body = content.flat(Infinity).filter(Boolean);
  const symbols = { "Rótulos": "etiqueta", "Campos": "campos", "Projeto": "quadro", "Relacionamentos": "relacoes" };
  return h("section", { class: "lateral-secao" }, h("h4", {}, icon(symbols[title] || "mais"), title), body.length ? body : h("p", { class: "vazio" }, "Nenhum"));
}

function draftAnnotations(data, operations = []) {
  let seq = data.anotacoes_seq || 0;
  const notes = new Map((data.anotacoes || []).map(note => [note.numero, note]));
  for (const op of operations) {
    const number = op.acao === "criar" ? ++seq : op.numero;
    if (op.acao === "excluir") notes.delete(number);
    else notes.set(number, { numero: number, titulo: op.titulo, texto: op.texto });
  }
  return [...notes.values()];
}

async function fetchAttachment(id, item) {
  const query = new URLSearchParams({ tarefa: id, id: item.id });
  const response = await fetch("/api/anexo?" + query, { headers: { "X-YABook-Token": TOKEN } });
  if (!response.ok) throw new Error((await response.json()).error);
  return response.blob();
}

function saveBlob(blob, name) {
  const url = URL.createObjectURL(blob);
  const link = h("a", { href: url, download: name, onclick: event => event.stopPropagation() });
  document.body.append(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

async function downloadAttachment(id, item) {
  try {
    saveBlob(await fetchAttachment(id, item), item.nome);
  } catch (error) {
    announce("Falha ao baixar anexo: " + error.message);
  }
}

// Visualizador de anexos: o tipo vem da extensão; o conteúdo vira nós DOM (sem innerHTML).
const ATTACHMENT_ACCEPT = ".pdf,.docx,.xlsx,.pptx,.odt,.ods,.txt,.md,.csv,.json,.log,.png,.jpg,.jpeg,.gif,.webp";
const PREVIEW_KIND = { ".pdf": "pdf", ".png": "imagem", ".jpg": "imagem", ".jpeg": "imagem", ".gif": "imagem", ".webp": "imagem",
  ".md": "markdown", ".txt": "texto", ".log": "texto", ".json": "json", ".csv": "csv" };
const PREVIEW_MIME = { ".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
  ".gif": "image/gif", ".webp": "image/webp" };
const PREVIEW_ROWS = 500;

function attachmentExt(name) {
  return (String(name || "").match(/\.[^./\\]+$/)?.[0] || "").toLowerCase();
}

function previewKind(name) {
  return PREVIEW_KIND[attachmentExt(name)] || null;
}

function formatBytes(bytes) {
  if (!Number.isFinite(bytes)) return "";
  const text = bytes < 1024 ? `${bytes} B` : bytes < 1048576 ? `${(bytes / 1024).toFixed(bytes < 10240 ? 1 : 0)} KB` : `${(bytes / 1048576).toFixed(1)} MB`;
  return text.replace(".", ",");
}

// UTF-8 primeiro; arquivos antigos (Latin-1/Windows-1252) caem no recuo sem caracteres trocados por "�".
function decodeText(buffer) {
  try {
    return new TextDecoder("utf-8", { fatal: true }).decode(buffer).replace(/^﻿/, "");
  } catch {
    return new TextDecoder("windows-1252").decode(buffer);
  }
}

// CSV com aspas, quebra de linha dentro de campo e separador detectado na primeira linha (; , ou tab).
function parseCsv(text) {
  const first = text.split(/\r?\n/, 1)[0] || "";
  const delimiter = [";", ",", "\t"].reduce((best, d) => first.split(d).length > first.split(best).length ? d : best, ";");
  const rows = [];
  let row = [], cell = "", quoted = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (quoted) {
      if (ch === '"' && text[i + 1] === '"') { cell += '"'; i++; }
      else if (ch === '"') quoted = false;
      else cell += ch;
    } else if (ch === '"' && !cell) quoted = true;
    else if (ch === delimiter) { row.push(cell); cell = ""; }
    else if (ch === "\n" || ch === "\r") {
      if (ch === "\r" && text[i + 1] === "\n") i++;
      row.push(cell); rows.push(row); row = []; cell = "";
    } else cell += ch;
  }
  if (cell || row.length) { row.push(cell); rows.push(row); }
  return { delimiter, rows };
}

function csvTable(text) {
  const { rows } = parseCsv(text);
  if (!rows.length) return h("p", { class: "vazio" }, "Arquivo vazio.");
  const [head, ...body] = rows;
  const shown = body.slice(0, PREVIEW_ROWS);
  return [h("div", { class: "tabela-rolagem visualizador-tabela", role: "region", tabindex: "0", "aria-label": "Tabela do CSV" },
    h("table", {}, h("thead", {}, h("tr", {}, head.map(cell => h("th", {}, cell)))),
      h("tbody", {}, shown.map(cells => h("tr", {}, cells.map(cell => h("td", {}, cell))))))),
    body.length > shown.length ? h("p", { class: "vazio" }, `Mostrando ${shown.length} de ${body.length} linhas; baixe para ver tudo.`) : null];
}

// Conteúdo do visualizador para um tipo; `url` só é usado por PDF e imagem.
function previewContent(kind, buffer, url, name) {
  if (kind === "pdf") return h("iframe", { class: "visualizador-pdf", src: url, title: name });
  if (kind === "imagem") {
    const image = h("img", { class: "visualizador-imagem", src: url, alt: name, title: "Clique para alternar entre ajustar à tela e tamanho real" });
    image.addEventListener("click", () => image.classList.toggle("real"));
    return h("div", { class: "visualizador-imagem-area" }, image);
  }
  const text = decodeText(buffer);
  if (kind === "csv") return csvTable(text);
  if (kind === "json") {
    let pretty = text;
    try { pretty = JSON.stringify(JSON.parse(text), null, 2); } catch { /* JSON inválido: mostra o texto original. */ }
    return h("pre", { class: "visualizador-texto", tabindex: "0" }, pretty);
  }
  if (kind === "markdown") {
    const rendered = h("div", { class: "markdown visualizador-markdown" }, markdown(text));
    const raw = h("pre", { class: "visualizador-texto", tabindex: "0", hidden: true }, text);
    const toggle = h("button", { type: "button", class: "botao pequeno visualizador-alternar" }, "Ver texto original");
    toggle.addEventListener("click", () => {
      raw.hidden = !raw.hidden;
      rendered.hidden = !raw.hidden;
      toggle.textContent = raw.hidden ? "Ver texto original" : "Ver formatado";
    });
    return [toggle, rendered, raw];
  }
  return h("pre", { class: "visualizador-texto", tabindex: "0" }, text);
}

// entries: [{ nome, tamanho, nota, load: () => Promise<Blob> }]; abre em `index`.
function openPreview(entries, index) {
  closePreview();
  const body = h("div", { class: "visualizador-corpo" });
  const title = h("h2", {}), info = h("span", { class: "visualizador-info" });
  const prev = h("button", { type: "button", class: "botao pequeno", title: "Anterior (←)", "aria-label": "Anexo anterior" }, "‹");
  const next = h("button", { type: "button", class: "botao pequeno", title: "Próximo (→)", "aria-label": "Próximo anexo" }, "›");
  const download = h("button", { type: "button", class: "botao pequeno" }, "Baixar");
  const close = h("button", { type: "button", class: "botao pequeno", "aria-label": "Fechar visualizador", title: "Fechar (Esc)" }, icon("fechar"));
  const dialog = h("dialog", { class: "visualizador", "aria-label": "Visualizar anexo" },
    h("header", { class: "visualizador-topo" }, h("div", { class: "visualizador-titulo" }, title, info),
      h("div", { class: "visualizador-acoes" }, entries.length > 1 ? [prev, next] : null, download, close)),
    body);
  const state = { dialog, index, generation: 0, url: null, blob: null };
  app.visualizador = state;
  const release = () => { if (state.url) URL.revokeObjectURL(state.url); state.url = null; state.blob = null; };
  const show = async (position) => {
    state.index = (position + entries.length) % entries.length;
    const entry = entries[state.index], generation = ++state.generation, kind = previewKind(entry.nome);
    release();
    title.textContent = entry.nome;
    info.textContent = [entries.length > 1 ? `${state.index + 1} de ${entries.length}` : null, formatBytes(entry.tamanho), entry.nota]
      .filter(Boolean).join(" · ");
    fill(body, h("p", { class: "vazio" }, "Carregando…"));
    try {
      const blob = await entry.load();
      if (generation !== state.generation) return;
      const mime = PREVIEW_MIME[attachmentExt(entry.nome)];
      state.blob = blob;
      state.url = mime ? URL.createObjectURL(new Blob([blob], { type: mime })) : null;
      fill(body, kind ? previewContent(kind, kind === "pdf" || kind === "imagem" ? null : await blob.arrayBuffer(), state.url, entry.nome)
        : h("div", { class: "visualizador-vazio" }, h("p", {}, "Este formato não tem visualização no navegador."),
          h("button", { type: "button", class: "botao pequeno", onclick: () => saveBlob(blob, entry.nome) }, "Baixar arquivo")));
    } catch (error) {
      if (generation === state.generation) fill(body, h("p", { class: "aviso erro" }, "Não foi possível abrir o anexo: " + error.message));
    }
  };
  prev.addEventListener("click", () => show(state.index - 1));
  next.addEventListener("click", () => show(state.index + 1));
  close.addEventListener("click", () => dialog.close());
  download.addEventListener("click", async () => {
    const entry = entries[state.index];
    try { saveBlob(state.blob || await entry.load(), entry.nome); } catch (error) { announce("Falha ao baixar anexo: " + error.message); }
  });
  dialog.addEventListener("click", event => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener("keydown", event => {
    if (entries.length < 2 || event.altKey || event.ctrlKey || event.metaKey) return;
    if (event.target instanceof Element && event.target.closest("input, textarea, select")) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") { event.preventDefault(); show(state.index + (event.key === "ArrowLeft" ? -1 : 1)); }
  });
  dialog.addEventListener("close", () => {
    state.generation++;
    release();
    dialog.remove();
    if (app.visualizador === state) app.visualizador = null;
  });
  document.body.append(dialog);
  dialog.showModal();
  show(index);
}

function closePreview() {
  if (app.visualizador?.dialog.open) app.visualizador.dialog.close();
}

function taskMaterials(detail, editable) {
  const data = detail.data, id = data.id;
  const notesPanel = h("section", { class: "comentario task-materials" });
  const filesPanel = h("section", { class: "comentario task-materials" });
  const pending = () => app.anexosRascunho[id];
  const label = (field, text) => h("label", { class: "campo" }, h("span", {}, text), field);

  function stageNote(op) {
    if (!app.editando || app.salvando) return;
    const entry = app.rascunho.tarefas[id];
    draftTask(id, {}, {
      revision: entry?.revision || detail.revision,
      anotacoes: [...(entry?.anotacoes || []), op],
    });
    renderNotes();
    renderToolbar();
    announce("Anotação atualizada no rascunho.");
  }

  function noteForm(note) {
    const title = h("input", { value: note?.titulo || "", required: true, maxlength: 160 });
    const text = h("textarea", { rows: 4, required: true, maxlength: 20000 }, note?.texto || "");
    return h("form", { class: "material-form", onsubmit: event => {
      event.preventDefault();
      if (!title.value.trim() || !text.value.trim()) {
        announce("Preencha o título e o conteúdo da anotação.");
        return;
      }
      stageNote({ acao: note ? "editar" : "criar", numero: note?.numero, titulo: title.value.trim(), texto: text.value.trim() });
    } }, label(title, "Título da anotação"), label(text, "Conteúdo em Markdown"),
    h("button", { type: "submit", class: "botao pequeno" }, "Aplicar anotação ao rascunho"));
  }

  function renderNotes() {
    const notes = draftAnnotations(data, editable ? app.rascunho.tarefas[id]?.anotacoes : []);
    fill(notesPanel, h("header", {}, h("h3", {}, "Anotações")),
      h("div", { class: "comentario-corpo material-lista" },
        notes.length ? notes.map(note => h("details", { class: "material-item" },
          h("summary", {}, "Nota " + String(note.numero).padStart(2, "0") + " · " + note.titulo),
          h("div", { class: "markdown" }, markdown(note.texto)),
          editable ? h("div", { class: "material-acoes" },
            h("details", {}, h("summary", {}, "Editar anotação"), noteForm(note)),
            h("button", { type: "button", class: "botao pequeno", onclick: () => stageNote({ acao: "excluir", numero: note.numero }) }, "Excluir anotação")) : null))
          : h("p", { class: "vazio" }, "Nenhuma anotação."),
        editable ? h("details", { class: "material-item" }, h("summary", {}, "Nova anotação"), noteForm()) : null));
  }

  function fileForm() {
    const file = h("input", { type: "file", required: true, accept: ATTACHMENT_ACCEPT });
    const name = h("input", { maxlength: 145 });
    const storage = h("select", { required: true }, h("option", { value: "" }, "Escolha onde guardar"),
      h("option", { value: "local", disabled: !app.estado.base_confidencial }, "Base confidencial local"),
      h("option", { value: "compartilhado" }, "Repositório privado de tarefas"));
    const error = h("p", { class: "vazio", role: "status" });
    return h("form", { class: "material-form", onsubmit: event => {
      event.preventDefault();
      const selected = file.files[0];
      if (!app.editando || app.salvando || !selected) return;
      if (!selected.size || selected.size > 1000000) {
        error.textContent = "Cada anexo deve ter entre 1 byte e 1 MB.";
        return;
      }
      const ext = selected.name.match(/\.[^.]+$/)?.[0] || "";
      const local = storage.value === "local";
      const nome = name.value.trim() ? name.value.trim() + ext
        : local ? "Documento confidencial" + ext : selected.name;
      const entry = pending() || { revision: detail.revision, items: [] };
      const bytes = Object.values(app.anexosRascunho).flatMap(entry => entry.items).reduce((sum, item) => sum + item.file.size, 0);
      if (bytes + selected.size > 1300000) {
        error.textContent = "Salve os anexos atuais antes de incluir mais arquivos.";
        return;
      }
      entry.items.push({ nome, local, file: selected });
      app.anexosRascunho[id] = entry;
      renderFiles();
      renderToolbar();
      announce("Anexo incluído no rascunho.");
    } }, label(file, "Arquivo"), label(name, "Nome genérico no card (opcional)"), label(storage, "Armazenamento"), error,
    h("button", { type: "submit", class: "botao pequeno" }, "Adicionar ao rascunho"));
  }

  function renderFiles() {
    const files = data.anexos || [];
    const staged = editable ? pending()?.items || [] : [];
    // Navegação do visualizador: anexos salvos e do rascunho que o navegador consegue exibir.
    const viewable = [
      ...files.map(item => ({ item, nome: item.nome, tamanho: item.tamanho, nota: item.local ? "só nesta máquina" : null,
        load: () => fetchAttachment(id, item) })),
      ...staged.map(item => ({ item, nome: item.nome, tamanho: item.file.size, nota: "no rascunho", load: async () => item.file })),
    ].filter(entry => previewKind(entry.nome));
    const viewButton = item => {
      const index = viewable.findIndex(entry => entry.item === item);
      return index < 0 ? null : h("button", { type: "button", class: "botao pequeno", onclick: () => openPreview(viewable, index) }, "Visualizar");
    };
    fill(filesPanel, h("header", {}, h("h3", {}, "Anexos")),
      h("div", { class: "comentario-corpo material-lista" },
        files.map(item => h("div", { class: "material-arquivo" },
          h("span", {}, item.nome, item.local ? " · só nesta máquina" : ""),
          viewButton(item),
          h("button", { type: "button", class: "botao pequeno", onclick: () => downloadAttachment(id, item) }, "Baixar"))),
        staged.map((item, index) => h("div", { class: "material-arquivo" },
          h("span", {}, item.nome + " · no rascunho"),
          viewButton(item),
          h("button", { type: "button", class: "botao pequeno", onclick: () => {
            if (!app.editando || app.salvando) return;
            pending().items.splice(index, 1);
            if (!pending().items.length) delete app.anexosRascunho[id];
            renderFiles();
            renderToolbar();
          } }, "Remover do rascunho"))),
        !files.length && !staged.length ? h("p", { class: "vazio" }, "Nenhum anexo.") : null,
        editable ? h("details", { class: "material-item" }, h("summary", {}, "Anexar arquivo"),
          h("p", { class: "vazio" }, "Até 1 MB por arquivo. Use a base local para material interno. Salve antes de recarregar."),
          fileForm()) : null));
  }
  renderNotes();
  renderFiles();
  return [notesPanel, filesPanel];
}

function fileBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",", 2)[1]);
    reader.onerror = () => reject(reader.error);
    reader.readAsDataURL(file);
  });
}

async function draftChanges(draft, files) {
  const ids = new Set([...Object.keys(draft.tarefas), ...Object.keys(files)]);
  return Promise.all([...ids].map(async id => {
    const entry = draft.tarefas[id] || {};
    const pending = files[id];
    // Envie a revisão de cada edição. Mesmo um anexo isolado pode ficar desatualizado.
    const revisions = [entry.revision, pending?.revision].filter(Boolean);
    const revision = new Set(revisions).size === 1 ? revisions[0] : null;
    const anexos = await Promise.all((pending?.items || []).map(async x =>
      ({ nome: x.nome, local: x.local, base64: await fileBase64(x.file) })));
    return { id, revision, campos: entry.campos, unset: entry.unset || [], registro: entry.registro,
      anotacoes: entry.anotacoes || [], anexos };
  }));
}

async function openTask(id, detail = null) {
  const panel = document.getElementById("painel");
  const request = beginPanel();
  if (!detail) {
    panel.setAttribute("aria-busy", "true");
    fill(panel, panelHeader("Carregando tarefa…"), h("div", { class: "painel-corpo" }, loadingState()));
    focusPanel();
  }
  try {
    detail ??= await api("/api/tarefa/" + encodeURIComponent(id));
    if (request !== app.painelRequest) return;
    const task = effectiveState().tarefas.find((t) => t.id === id) || detail.resumo;
    const data = { ...detail.data, ...task };
    const canEdit = !SNAPSHOT && !!TOKEN && data.tipo !== "pergunta";
    const editing = canEdit && app.editando;
    const draft = editing && app.rascunho.tarefas[id];
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
    let editAction = null;
    if (editing) {
      editAction = draftExitButton({ id: "painel-descartar", class: "botao pequeno", onclick: async () => {
        if (await discardDraft() && request === app.painelRequest) await openTask(id);
      } });
    } else if (canEdit) {
      editAction = h("button", { class: "botao pequeno", type: "button", onclick: () => {
        startEditing();
        openTask(id, detail);
      } }, icon("editar"), "Editar");
    }
    fill(panel,
      panelHeader([
        data.numero ? h("span", { class: "numero-issue" }, `@${data.numero} `) : null,
        data.titulo,
        ref ? [" ", h("span", { class: "numero-issue" }, `#${ref.number}`)] : null,
      ], editAction),
      h("div", { class: "faixa-estado" },
        stateLabel(task),
        // Status do fluxo e prazo ao lado do título; o painel lateral não repete o prazo.
        task.tipo !== "pergunta" ? h("span", { class: "selo neutro forte grande", title: "Status: etapa do fluxo" },
          h("span", { class: `status papel-${roleOf(data.coluna)}` }), columnName(data.coluna)) : null,
        data.prazo ? h("span", { class: "selo neutro forte grande" + (daysUntil(data.prazo) < 0 && !CLOSED.includes(task.papel) ? " vencido" : ""), title: "Prazo: " + fullDate(data.prazo) },
          icon("calendario"), cardDate(data.prazo)) : null,
        parent ? h("button", { class: "selo neutro forte grande", type: "button", onclick: () => openTask(parent.id) },
          stateIcon(parent), `Faz parte de: ${parent.titulo}${parentRef ? " #" + parentRef.number : ""}`) : null,
        task.codigo && (!ref || task.codigo !== ref.full) ? h("span", { class: "selo neutro forte grande" }, icon("repo"), task.codigo) : null,
        ref ? h("span", { class: "selo neutro forte grande" }, icon("repo"), ref.full.split("#")[0]) : null,
        task.size ? h("span", { class: "selo neutro forte grande" }, "Tamanho ", sizeNumber(task)) : null,
        task.pessoal ? h("span", { class: "selo cor-pink grande" }, "pessoal") : null),
      h("div", { class: "painel-colunas" },
        h("div", { class: "painel-principal" },
          h("div", { class: "comentario" },
            h("header", {}, h("strong", {}, label(data.tipo)),
              data.atualizada ? h("span", { class: "vazio" }, ` · atualizada ${when(data.atualizada)}`) : null,
              h("details", { class: "detalhes-tecnicos" }, h("summary", {}, "Detalhes técnicos"), h("code", {}, data.id))),
            h("div", { class: "comentario-corpo markdown" },
              data.descricao ? h("div", { class: "descricao-tarefa markdown" }, markdown(data.descricao)) : h("p", { class: "vazio" }, "Sem descrição."),
              data.proximo_passo ? h("div", { class: "proximo-destaque" }, h("h3", {}, icon("seta"), "Próximo passo"), h("p", {}, data.proximo_passo)) : null,
              detail.body ? h("details", { class: "historico-agente" }, h("summary", {}, icon("historico"), "Histórico do agente"), taskDocument(detail.body)) : null)),
          detail.filhos && detail.filhos.length ? h("div", { class: "caixa" },
            h("header", {}, h("h3", {}, data.nivel === "epico" ? "Histórias" : "Itens"),
              epic && data.nivel === "epico" ? h("span", { class: "direita" }, segments(epic.concluidas, epic.historias)) : null),
            detail.filhos.map((child) => h("div", { class: "linha-caixa" }, stateIcon(child), goTo(child),
              h("span", { class: "selo neutro" }, h("span", { class: `status papel-${roleOf(child.coluna)}` }), columnName(child.coluna))))) : null,
          !SNAPSHOT && task.tipo !== "pergunta" ? taskMaterials(detail, editing) : null,
          detail.complemento ? h("section", { class: "comentario documento-confidencial" }, h("header", {}, icon("cadeado"), h("strong", {}, "Complemento confidencial"), h("span", { class: "vazio" }, " · só nesta máquina")),
            h("div", { class: "comentario-corpo markdown" }, markdown(detail.complemento))) : null,
          Object.entries(detail.referencias || {}).map(([refName, text]) => h("section", { class: "comentario documento-confidencial" },
            h("header", {}, icon("cadeado"), h("strong", {}, "Referência confidencial"), h("span", { class: "vazio" }, "Só nesta máquina")),
            h("p", { class: "documento-origem" }, refName),
            h("div", { class: "comentario-corpo markdown" }, text ? markdown(text) : h("p", { class: "vazio" }, "Referência indisponível: arquivo não encontrado na base confidencial ou acesso fora da base.")))),
          detail.confidencial === "bloqueado" && !Object.keys(detail.referencias || {}).length
            ? h("p", { class: "vazio" }, "Complemento confidencial só na máquina que possui a base.") : null,
          editing ? h("div", { class: "comentario" }, h("div", { class: "comentario-corpo" }, editForm(id))) : null),
        h("aside", { class: "painel-lateral" },
          sideSection("Rótulos", h("div", { class: "rotulos" }, badges(task, { semPai: true, semCodigo: true, semData: true, semPrazo: true }))),
          sideSection("Campos",
            field("Status", h("span", { class: "selo neutro forte" }, h("span", { class: `status papel-${roleOf(data.coluna)}` }), columnName(data.coluna))),
            field("Tipo", label(data.tipo)),
            field("Máquina", data.maquina),
            field("Nível", data.nivel ? LEVEL[data.nivel][0] : null),
            field("Código", task.codigo),
            field("Rodada", data.rodada > 1 ? `${data.rodada} (${data.rodada - 1} retorno${data.rodada > 2 ? "s" : ""} da validação)` : null),
            field("Concluída", task.papel === "concluido" && data.atualizada ? fmtDate(data.atualizada) : null),
            field("Pessoal", task.pessoal ? (("pessoal_marcado" in task) ? "sim (marcado)" : "sim (calculado)") : (("pessoal_marcado" in task) ? "não (marcado)" : null))),
          sideSection("Relacionamentos",
            parent ? [h("span", { class: "vazio" }, "Faz parte de"), h("div", { class: "relacao" }, stateIcon(parent), goTo(parent),
              epic && data.nivel !== "epico" ? h("span", { class: "contador" }, `${epic.concluidas} / ${epic.historias}`) : null)] : null,
            (data.issue || []).length ? [h("span", { class: "vazio" }, "Issues"), (data.issue || []).map((i) => h("div", { class: "relacao" }, icon("aberto", "estado-aberto"), i))] : null,
            (() => {  // perguntas abertas desta tarefa, com acesso direto
              const asked = (effectiveState().tarefas || []).filter((t) => t.tipo === "pergunta" && t.sobre === data.id && !t.resposta);
              return asked.length ? [h("span", { class: "vazio" }, "Perguntas abertas"),
                asked.map((q) => h("div", { class: "relacao" }, icon("pergunta"), goTo(q)))] : null;
            })()))));
    panel.setAttribute("aria-busy", "false");
    focusPanel();
  } catch (error) {
    if (request !== app.painelRequest) return;
    showPanel(h("h2", {}, "Não foi possível abrir a tarefa"), h("p", { class: "aviso erro", role: "alert" }, error.message),
      h("button", { class: "botao", type: "button", onclick: () => openTask(id) }, "Tentar novamente"));
  }
}

function panelHeader(title, action = null) {
  const close = h("button", { class: "botao-icone discreto", type: "button", title: "Fechar", "aria-label": "Fechar painel", onclick: closePanel }, icon("fechar"));
  return h("div", { class: "painel-topo" }, h("h2", { id: "painel-titulo", tabindex: "-1" }, title),
    action ? h("div", { class: "painel-topo-acoes" }, action, close) : close);
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
  closePreview();
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

// Consolida só os itens presentes na visão, preservando o filho quando o pai
// estiver fechado ou fora do filtro. Sem prazo intermediário, compara com o
// ancestral mais próximo que tenha data; datas diferentes continuam separadas.
function deadlineTasks(tasks) {
  const index = new Map(tasks.map((task) => [task.id, task]));
  return tasks.filter((task) => {
    if (!task.prazo || CLOSED.includes(task.papel)) return false;
    const seen = new Set([task.id]);
    let parent = index.get(task.pai);
    while (parent && !seen.has(parent.id)) {
      if (CLOSED.includes(parent.papel)) return true;
      if (parent.prazo) return parent.prazo !== task.prazo;
      seen.add(parent.id);
      parent = index.get(parent.pai);
    }
    return true;
  }).sort((a, b) => a.prazo.localeCompare(b.prazo));
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

// Estimativa × tempo registrado: horas registradas das tarefas concluídas por size, para calibrar a escala.
async function estimateSection() {
  let data;
  try { data = await api("/api/estimativa"); } catch (e) { data = null; }
  if (!data || !Array.isArray(data.por_size)) return null;  // a Ficha segue mesmo sem a comparação
  const range = (f) => f[1] === null ? `mais de ${hours(f[0])}` : `até ${hours(f[1])}`;
  return h("section", { class: "estimativa" },
    h("h2", {}, "Estimativa × tempo registrado"),
    h("p", { class: "vazio" }, `${data.tarefas} tarefas concluídas com size e horas. As horas contam o trabalho registrado, não a espera por validação.`),
    h("table", {}, h("thead", {}, h("tr", {}, ["Size", "Faixa esperada", "Tarefas", "Mediana", "Menor", "Maior"].map((c, i) => h("th", { class: i > 1 ? "num" : null }, c)))),
      h("tbody", {}, data.por_size.map((g) => h("tr", {},
        h("td", {}, sizeNumber(g)), h("td", {}, range(g.faixa)), h("td", { class: "num" }, String(g.quantidade)),
        ...[g.mediana, g.minimo, g.maximo].map((v) => h("td", { class: "num" }, v === null ? "—" : hours(v))))))),
    data.fora_da_faixa.length ? [h("h3", {}, "Fora da faixa"),
      h("table", {}, h("tbody", {}, data.fora_da_faixa.map((r) => h("tr", {},
        h("td", {}, h("button", { class: "link", type: "button", onclick: () => openTask(r.id) }, (r.numero ? `@${r.numero} ` : "") + r.titulo)),
        h("td", {}, sizeNumber(r)), h("td", { class: "num" }, hours(r.horas)),
        h("td", {}, "pelas horas: ", sizeNumber({ size: r.size_pelas_horas }))))))]
      : h("p", { class: "vazio" }, "Nenhuma tarefa fora da faixa."));
}

// Colunas fechadas mostram só as 5 mais recentes até a pessoa pedir todas; a busca mostra tudo.
const CLOSED_PREVIEW = 5;
function closedPreview(column, cards) {
  if (!["concluido", "arquivado"].includes(column.papel) || (app.busca || "").trim() || (app.colunasAbertas || {})[column.id]
      || cards.length <= CLOSED_PREVIEW) return cards;
  const recent = new Set([...cards].sort((a, b) => String(b.atualizada || "").localeCompare(String(a.atualizada || "")))
    .slice(0, CLOSED_PREVIEW).map((t) => t.id));
  return cards.filter((t) => recent.has(t.id));
}

function boardMachines(estado) {
  return [...new Set(work(estado).map((task) => task.maquina).filter(Boolean))].sort();
}

function boardMachineFilter(machines) {
  const selected = pref("quadro.maquina", "");
  return machines.includes(selected) ? selected : "";
}

function filtered(tasks) {
  const text = (app.busca || "").trim().toLowerCase();
  if (!text) return tasks;
  return tasks.filter((t) => [t.numero ? "@" + t.numero : "", t.titulo, t.codigo, t.id, t.proximo_passo, (t.issue || []).join(" ")].join(" ").toLowerCase().includes(text));
}

function titleLink(task) {
  return h("button", { class: "link titulo", type: "button", title: task.titulo, onclick: () => openTask(task.id) }, task.titulo);
}

function sheetTask(row, tasks = []) {
  if (!row.codigo || !["demanda", "projeto", "especificacao"].includes(row.tipo)) return null;
  const matches = (task) => {
    const code = row.tipo === "especificacao" ? task.codigo ?? task.demanda ?? task.projeto : task[row.tipo];
    return task.tipo !== "pergunta" && (row.tipo !== "especificacao" || task.tipo === "especificacao")
      && String(code ?? "") === String(row.codigo);
  };
  const index = new Map(tasks.map((task) => [task.id, task]));
  const owners = new Map();
  for (const id of row.tarefas || []) {
    const seen = new Set();
    let task = index.get(id), owner = null;
    while (task && !seen.has(task.id)) {
      seen.add(task.id);
      if (matches(task)) owner = task;
      task = index.get(task.pai);
    }
    if (owner) owners.set(owner.id, owner);
  }
  // Linhas antigas podem não trazer as tarefas: só aceita um dono inequívoco.
  if (!owners.size) {
    const candidates = tasks.filter(matches);
    const typed = candidates.filter((task) => task.tipo === row.tipo);
    for (const task of typed.length ? typed : candidates) owners.set(task.id, task);
  }
  return owners.size === 1 ? owners.values().next().value : null;
}

// Durações padronizadas: "4h 45min", "1h 02min", "45min". O resumo arredonda ao minuto;
// o detalhe (recordedTime) mantém os segundos: "42min 30s", "1h 02min 30s".
function summaryTime(value) {
  if (value === undefined || value === null) return "—";
  const minutes = Math.round(value * 60), whole = Math.floor(minutes / 60), rest = minutes % 60;
  return whole ? `${whole}h ${String(rest).padStart(2, "0")}min` : `${rest}min`;
}

// Extras exibem o registrado: capturado nas janelas + informado à mão (task log), com recuo para respostas antigas.
function extraRecorded(extra) {
  return extra.registrado ?? (extra.capturado || 0) + (extra.informado || 0);
}

function extraDetail(extra) {
  return extra.informado ? `${recordedTime(extra.capturado || 0)} capturado + ${recordedTime(extra.informado)} informado` : null;
}

function recordedTime(value) {
  if (value === undefined || value === null) return "—";
  const seconds = Math.round(value * 3600), whole = Math.floor(seconds / 3600);
  const minutes = Math.floor(seconds % 3600 / 60), rest = seconds % 60;
  const parts = whole ? [whole + "h", String(minutes).padStart(2, "0") + "min"] : [minutes + "min"];
  if (rest) parts.push(String(rest).padStart(2, "0") + "s");
  return parts.join(" ");
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
    titulo: "Visão geral",
    descricao: "Seu trabalho em curso e o que precisa de atenção.",
    icone: "hoje",
    render(estado) {
      const tasks = filtered(work(estado));
      const waiting = tasks.filter((t) => t.aguardando && !CLOSED.includes(t.papel)).sort((a, b) => waitingDays(b) - waitingDays(a));
      const doing = tasks.filter((t) => t.papel === "ativo" && !t.aguardando).sort(byRecent);
      const testing = tasks.filter((t) => t.papel === "validacao" && !t.aguardando).sort(byRecent);
      app.contagem = doing.length + testing.length + waiting.length;
      const full = (task) => estado.tarefas.find((t) => t.id === task.id) || task;
      const deadlines = filtered(estado.prazos.map(full)), questions = filtered(estado.perguntas.map(full));
      const line = (task, detail = null) => h("div", { class: "resumo-linha" },
        h("div", { class: "resumo-linha-tarefa" }, stateIcon(task),
          h("span", { class: "resumo-codigo" }, task.codigo || (task.numero ? "@" + task.numero : "")), titleLink(task)),
        detail ? h("div", { class: "resumo-linha-detalhe" }, detail) : null);
      const section = (title, items, empty, renderItem = line) => h("section", { class: "caixa resumo-secao" },
        h("header", {}, h("h2", {}, title), h("span", { class: "contador" }, items.length)),
        items.length ? h("div", { class: "resumo-lista" }, items.map((task) => renderItem(task)))
          : h("p", { class: "resumo-vazio" }, empty));
      // Faixa de atenção: o que depende da pessoa aparece primeiro, também no celular.
      const next = deadlines.slice().sort((a, b) => (a.prazo || "").localeCompare(b.prazo || ""))[0];
      const jump = (id) => () => { const node = document.getElementById(id); if (node) node.scrollIntoView({ block: "start", behavior: "smooth" }); };
      const attention = [
        questions.length ? h("button", { type: "button", class: "atencao-item", onclick: jump("secao-perguntas") }, icon("pergunta"), `${questions.length} pergunta${questions.length > 1 ? "s" : ""}`) : null,
        waiting.length ? h("button", { type: "button", class: "atencao-item", onclick: jump("secao-aguardando") }, icon("ficha"), `${waiting.length} aguardando retorno`) : null,
        next ? h("button", { type: "button", class: "atencao-item" + (daysUntil(next.prazo) < 0 ? " vencido" : ""), onclick: jump("secao-prazos") }, icon("calendario"), `próximo prazo ${fmtDate(next.prazo)}`) : null,
      ].filter(Boolean);
      const withId = (id, node) => { if (node) node.id = id; return node; };
      return h("section", { class: "visao-hoje resumo-dia" },
        h("div", { class: "faixa-atencao", role: "navigation", "aria-label": "O que precisa de você" },
          attention.length ? attention : h("span", { class: "atencao-vazia" }, "Nada pendente com você.")),
        h("div", { class: "resumo-trabalho" },
          section("Em andamento", doing, "Nenhuma tarefa em andamento."),
          section("Em validação", testing, "Nenhuma tarefa em validação.")),
        h("aside", { class: "resumo-atencao", "aria-label": "Prazos, perguntas e retornos" },
          // Até três perguntas; o restante fica na página Perguntas.
          withId("secao-perguntas", (() => {
            const box = section("Perguntas para você", questions.slice(0, 3), "Nenhuma pergunta pendente.");
            if (questions.length > 3) {
              box.querySelector("header .contador").textContent = String(questions.length);
              box.append(h("a", { class: "link ver-todas", href: "#perguntas" }, `Ver todas (${questions.length})`));
            }
            return box;
          })()),
          waiting.length ? withId("secao-aguardando", section("Aguardando retorno", waiting, "", (task) => line(task, task.aguardando))) : null,
          withId("secao-prazos", section("Prazos: atrasados e próximos 2 dias", deadlines, "Nenhum prazo atrasado ou nos próximos 2 dias.", (task) => line(task,
            h("span", { class: "resumo-prazo" + (daysUntil(task.prazo) < 0 ? " vencido" : "") },
              icon("calendario"), fmtDate(task.prazo), daysUntil(task.prazo) < 0 ? " · Em atraso" : ""))))));
    },
  },
  quadro: {
    titulo: "Quadro de tarefas",
    descricao: "Organize o trabalho por etapa, do planejamento à conclusão.",
    icone: "quadro",
    opcoes(estado) {
      const epicFilter = pref("quadro.epico", "");
      const levelFilter = pref("quadro.nivel", "");
      const showArchived = pref("quadro.arquivadas", "0") === "1";
      const machines = boardMachines(estado);
      const machineFilter = boardMachineFilter(machines);
      return [
        h("select", { "aria-label": "Máquina", onchange: (e) => { setPref("quadro.maquina", e.target.value); render(); } },
          h("option", { value: "", selected: !machineFilter }, "Máquina: todas"),
          machines.map((machine) => h("option", { value: machine, selected: machine === machineFilter }, machine))),
        h("select", { title: "Épico", onchange: (e) => { setPref("quadro.epico", e.target.value); render(); } },
          h("option", { value: "" }, "Épico: todos"), h("option", { value: "-", selected: epicFilter === "-" }, "Sem épico"),
          estado.epicos.map((e) => h("option", { value: e.id, selected: e.id === epicFilter }, e.titulo))),
        h("select", { title: "Nível", onchange: (e) => { setPref("quadro.nivel", e.target.value); render(); } },
          [["", "Nível: todos"], ["epico", "Épicos"], ["historia", "Histórias"], ["tarefa", "Tarefas"], ["-", "Sem nível"]]
            .map(([v, n]) => h("option", { value: v, selected: v === levelFilter }, n))),
        switchInput("Arquivadas", showArchived, (e) => { setPref("quadro.arquivadas", e.target.checked ? "1" : "0"); render(); }),
        switchInput("Só aguardando", pref("quadro.aguardando", "0") === "1", (e) => { setPref("quadro.aguardando", e.target.checked ? "1" : "0"); render(); }),
        h("select", { "aria-label": "Apresentação", title: "Quadro ou lista agrupada por etapa",
          onchange: (e) => { setPref("quadro.modo", e.target.value); render(); } },
          [["quadro", "Quadro"], ["lista", "Lista"]].map(([value, text]) => h("option", { value, selected: boardMode() === value }, text))),
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
      const machineFilter = boardMachineFilter(boardMachines(estado));
      const visible = filtered(work(estado)).filter((t) => (!onlyWaiting || t.aguardando) &&
        (!machineFilter || t.maquina === machineFilter) &&
        (!epicFilter || (epicFilter === "-" ? !epicOf(t, map) : epicOf(t, map) === epicFilter)) &&
        (!levelFilter || (levelFilter === "-" ? !t.nivel : t.nivel === levelFilter)));
      const columns = estado.colunas.filter((c) => showArchived || c.papel !== "arquivado");
      // Épicos ficam numa coluna própria no fim (ativos primeiro), com o status do fluxo em cada card.
      const epics = visible.filter((t) => t.nivel === "epico" && columns.some((c) => c.id === t.coluna))
        .sort((a, b) => CLOSED.includes(a.papel) - CLOSED.includes(b.papel) || boardOrder(a, b));
      const items = visible.filter((t) => t.nivel !== "epico");
      app.contagem = items.filter((t) => columns.some((c) => c.id === t.coluna)).length + epics.length;
      const epicCards = () => epics.length ? epics.map((t) => card(t, { status: true, semNivel: true }))
        : h("p", { class: "vazio", style: "text-align:center;font-size:12px" }, "Nenhum épico");
      if (boardMode() === "lista") {
        return h("div", { class: "quadro-lista" }, [...columns.map((column) => {
          const cards = items.filter((t) => t.coluna === column.id).sort(boardOrder);
          const shown = closedPreview(column, cards);
          return h("details", { class: `lista-etapa papel-${column.papel}`, open: cards.length && !CLOSED.includes(column.papel) ? true : null },
            h("summary", {}, h("span", { class: `status papel-${column.papel}` }), h("span", { class: "nome" }, column.nome), h("span", { class: "contador" }, String(cards.length))),
            cards.length ? h("div", { class: "lista-itens" }, shown.map((t) => card(t))) : h("p", { class: "resumo-vazio" }, "Nenhum item."),
            shown.length < cards.length ? h("button", { class: "botao exibir-todas", type: "button",
              onclick: () => { app.colunasAbertas = { ...(app.colunasAbertas || {}), [column.id]: true }; render(); } }, `Exibir todas (${cards.length})`) : null);
        }), h("details", { class: "lista-etapa lista-epicos" },
          h("summary", {}, h("span", { class: "status" }), h("span", { class: "nome" }, "Épicos"), h("span", { class: "contador" }, String(epics.length))),
          h("div", { class: "lista-itens" }, epicCards()))]);
      }
      const epicColumn = h("div", { class: "coluna coluna-epicos", "data-coluna": "epicos" },
        h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, "Épicos"), h("span", { class: "contador" }, String(epics.length))),
        h("div", { class: "itens" }, epicCards()));
      return h("div", { class: "quadro" }, columns.map((column) => {
        const cards = items.filter((t) => t.coluna === column.id).sort(boardOrder);
        const shown = closedPreview(column, cards);
        if (!cards.length && !app.editando) {  // coluna vazia vira faixa estreita com nome e quantidade
          return h("div", { class: `coluna coluna-vazia papel-${column.papel}`, "data-coluna": column.id, title: `${column.nome}: nenhum item` },
            h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, column.nome), h("span", { class: "contador" }, "0")));
        }
        return h("div", { class: `coluna papel-${column.papel}`, "data-coluna": column.id,
          ondragover: app.editando ? indicateDrop : null,
          ondragleave: app.editando ? (e) => { if (!e.currentTarget.contains(e.relatedTarget)) clearDrop(); } : null,
          ondrop: app.editando ? (e) => { e.currentTarget.classList.remove("alvo"); dropCard(e, column.id, cards); } : null },
          h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, column.nome), h("span", { class: "contador" }, String(cards.length)),
            h("span", { class: "acoes" }, app.editando
              ? h("button", { class: "botao-icone discreto", type: "button", title: "Renomear coluna", "aria-label": "Renomear coluna " + column.nome, onclick: () => renameColumn(column) }, icon("editar"))
              : null)),
          h("div", { class: "itens" }, cards.length ? shown.map((t) => card(t)) : h("p", { class: "vazio", style: "text-align:center;font-size:12px" }, "Nenhum item"),
            shown.length < cards.length ? h("button", { class: "botao exibir-todas", type: "button",
              onclick: () => { app.colunasAbertas = { ...(app.colunasAbertas || {}), [column.id]: true }; render(); } },
              `Exibir todas (${cards.length})`) : null));
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
      const all = estado.epicos.filter((e) => matches(e) || children(e.id).some(matches));
      const finished = (e) => CLOSED.includes(roleOf(e.coluna));
      const epics = all.filter((e) => !finished(e));  // ativos primeiro; concluídos ficam recolhidos no fim
      const done = all.filter(finished);
      const loose = filtered(tasks.filter((t) => !t.pai && t.nivel !== "epico" && !CLOSED.includes(t.papel))).sort(byRecent);
      app.contagem = all.length;
      const storyRow = (story, sub) => h("div", { class: "linha-caixa" + (sub ? " sub" : "") }, stateIcon(story), titleLink(story),
        badges(story, { semNivel: true, semPai: true, semPessoal: true, semData: true }),
        h("span", { class: "selo neutro" }, h("span", { class: `status papel-${story.papel}` }), columnName(story.coluna)));
      const doneRow = (epic) => h("div", { class: "linha-caixa epico-concluido" }, stateIcon(tasks.find((t) => t.id === epic.id) || epic),
        h("button", { class: "link", type: "button", onclick: () => openTask(epic.id) }, epic.titulo), segments(epic.concluidas, epic.historias));
      return h("section", {},
        !epics.length && done.length && !app.busca ? h("p", { class: "resumo-vazio" }, "Nenhum épico ativo.") : null,
        epics.length || done.length ? epics.map((epic) => {
          const full = tasks.find((t) => t.id === epic.id) || epic;
          const stories = children(epic.id);
          const open = stories.filter((s) => !CLOSED.includes(s.papel));
          const closed = stories.filter((s) => CLOSED.includes(s.papel));
          const withTasks = (story) => [storyRow(story), children(story.id).map((sub) => storyRow(sub, true))];
          // Cada épico ativo é recolhível; o resumo mostra título, status, prazo e progresso.
          const collapsed = (app.epicosRecolhidos || {})[epic.id];
          return h("details", { class: "caixa epico-ativo", open: collapsed ? null : true,
            ontoggle: (e) => { app.epicosRecolhidos = { ...(app.epicosRecolhidos || {}), [epic.id]: !e.currentTarget.open }; } },
            h("summary", { class: "epico-resumo" }, stateIcon(full),
              h("button", { class: "link", type: "button", onclick: (e) => { e.preventDefault(); openTask(epic.id); } }, h("h3", {}, epic.titulo)),
              h("span", { class: "rotulos" }, badges(full, { semNivel: true })),
              h("span", { class: "direita" }, segments(epic.concluidas, epic.historias),
                h("span", { class: "selo neutro" }, h("span", { class: `status papel-${roleOf(epic.coluna)}` }), columnName(epic.coluna)))),
            epic.proximo_passo ? h("div", { class: "corpo" }, h("div", { class: "card-passo" }, epic.proximo_passo)) : null,
            open.map(withTasks),
            closed.length ? h("details", {}, h("summary", {}, `${closed.length} concluída(s) ou arquivada(s)`), closed.map(withTasks)) : null);
        }) : emptyState(app.busca ? "Nenhum épico com esse filtro" : "Nenhum épico", "Os épicos reúnem histórias e mostram o progresso da iniciativa."),
        done.length ? h("details", { class: "caixa epicos-concluidos", open: app.busca ? true : null },
          h("summary", {}, `Concluídos (${done.length})`), done.map(doneRow)) : null,
        loose.length ? [h("h2", {}, "Sem épico"), h("div", { class: "cards" }, loose.map(card))] : null);
    },
  },
  prazos: {
    titulo: "Calendário",
    descricao: "Calendário e agenda das tarefas com prazo.",
    icone: "prazos",
    opcoes() {
      return [h("select", { "aria-label": "Apresentação do calendário", onchange: (e) => { setPref("prazos.modo", e.target.value); render(); } },
        [["mes", "Mês"], ["agenda", "Agenda"]].map(([value, text]) => h("option", { value, selected: calendarMode() === value }, text)))];
    },
    render(estado) {
      const rows = deadlineTasks(filtered(work(estado)));
      app.contagem = rows.length;
      const agenda = app.prazoDia ? rows.filter((t) => t.prazo === app.prazoDia) : rows;
      const groups = [
        { title: "Atrasados", icon: "alerta", class: "atrasada", test: (days) => days < 0 },
        { title: "Próximos 2 dias", icon: "calendario", class: "proximo", test: (days) => days >= 0 && days <= 2 },
        { title: "Mais adiante", icon: "prazos", class: "", test: (days) => days > 2 },
      ];
      return h("section", { class: "prazos-visao" + (calendarMode() === "agenda" ? " so-agenda" : "") },
        calendarMode() === "agenda" ? null : deadlineCalendar(rows, estado.hoje),
        h("section", { class: "prazos-lista", "aria-label": "Agenda de prazos" },
          h("div", { class: "prazos-agenda-topo" },
            h("h2", { id: "prazos-agenda-titulo", tabindex: "-1" }, app.prazoDia ? "Prazos de " + fmtDate(app.prazoDia) : "Todos os prazos"),
            app.prazoDia ? h("button", { class: "botao pequeno", type: "button", onclick: () => { app.prazoDia = null; render(); } }, "Ver todos") : null),
          !agenda.length ? emptyState(app.prazoDia ? "Nenhum prazo neste dia" : app.busca ? "Nenhum prazo com esse filtro" : "Nenhuma tarefa aberta com prazo", "Os prazos aparecem aqui quando definidos nas tarefas.") : groups.map((group) => {
            const items = agenda.filter((task) => group.test(daysUntil(task.prazo)));
            if (!items.length) return null;
            return h("section", { class: "prazo-grupo " + group.class },
              h("header", {}, h("h3", {}, icon(group.icon), group.title), h("span", { class: "contador" }, items.length)),
              items.map((task, index) => {
                const days = daysUntil(task.prazo);
                const sameDay = index > 0 && items[index - 1].prazo === task.prazo;  // mesma data: um cabeçalho só
                const date = new Date(task.prazo + "T12:00:00");
                const month = date.toLocaleDateString("pt-BR", { month: "short" }).replace(".", "");
                const distance = days < 0 ? `${-days} dia${days === -1 ? "" : "s"} de atraso` : days === 0 ? "Hoje" : days === 1 ? "Amanhã" : `Em ${days} dias`;
                return h("article", { class: "prazo-item " + group.class + (sameDay ? " mesma-data" : "") },
                  h("time", { class: "prazo-data", datetime: task.prazo, "aria-label": fmtDate(task.prazo) },
                    h("strong", {}, task.prazo.slice(8, 10)), h("span", {}, month + (task.prazo.slice(0, 4) !== estado.hoje.slice(0, 4) ? " " + task.prazo.slice(0, 4) : ""))),
                  h("div", { class: "prazo-conteudo" }, h("div", { class: "prazo-titulo" }, stateIcon(task), titleLink(task)),
                    h("div", { class: "prazo-meta" },
                      pill((LEVEL[task.nivel] || LEVEL.tarefa)[0], (LEVEL[task.nivel] || LEVEL.tarefa)[1]),
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
          h("h3", {}, task.titulo), answered ? h("span", { class: "indicador-respondida" }, "Respondida") : null),
        answered ? about(task) : null,  // abertas já ficam agrupadas sob a tarefa
        answered ? h("details", { class: "pergunta-resposta" }, h("summary", {}, icon("seta"), h("span", { class: "resposta-resumo" }, task.resposta)), h("p", {}, task.resposta))
          : h("details", { class: "passo" }, h("summary", {}, "Como responder"),
            h("p", {}, `Responda ao agente mencionando esta pergunta${task.numero ? ` (@${task.numero})` : ""}.`),
            h("p", { class: "comando-secundario" }, "Ou pela linha de comando: ", h("code", {}, `task answer ${task.id} <resposta>`), " ",
              h("button", { class: "botao pequeno", type: "button", onclick: (e) => copy(`task answer ${task.id} `, e.currentTarget) }, icon("copiar"), "Copiar"))));
      // Abertas agrupadas pela tarefa relacionada; respondidas ficam recolhidas, em segundo plano.
      const byTask = open.reduce((groups, t) => {
        const key = t.sobre || "";
        (groups[key] = groups[key] || []).push(t);
        return groups;
      }, {});
      const taskTitle = (id) => (estado.tarefas.find((x) => x.id === id) || {}).titulo;
      return h("section", {},
        h("h2", {}, "Aguardando você", h("span", { class: "contador" }, open.length)),
        open.length ? Object.entries(byTask).map(([id, items]) => h("section", { class: "perguntas-grupo" },
          h("h3", { class: "perguntas-grupo-titulo" }, id && taskTitle(id)
            ? h("button", { class: "link", type: "button", onclick: () => openTask(id) }, icon("camadas"), taskTitle(id)) : "Sem tarefa relacionada",
            h("span", { class: "contador" }, items.length)),
          h("ul", { class: "perguntas" }, items.map((t) => questionCard(t, false)))))
          : emptyState(app.busca ? "Nenhuma pergunta com esse filtro" : "Tudo respondido por aqui", "As decisões pendentes aparecem aqui."),
        answered.length ? h("details", { class: "perguntas-respondidas" },
          h("summary", {}, `Respondidas recentes (${answered.length})`),
          h("ul", { class: "perguntas" }, answered.map((t) => questionCard(t, true)))) : null);
    },
  },
  semana: {
    titulo: "Atividade semanal",
    descricao: "Atividade por dia e totais da ficha. Abra um dia para ver os detalhes.",
    icone: "semana",
    async render(estado) {
      const ref = app.semana || estado.hoje;
      const [week, sheetWeek] = await Promise.all([api("/api/semana?data=" + ref), api("/api/ficha?semana=1&data=" + ref)]);
      const total = week.dias.reduce((sum, d) => sum + d.horas, 0);
      const accumulated = week.dias.reduce((sum, d) => sum + (d.acumulado ?? d.horas), 0);
      const peak = Math.max(1, ...week.dias.map((d) => d.horas));
      return h("section", {},
        dayNav("semana", ref, 7, `Semana de ${fmtDate(week.inicio)}`),
        // Resumo e rateio lado a lado, antes dos dias: o total e a divisão por código ficam juntos.
        h("div", { class: "semana-resumo" },
          h("div", { class: "semana-totais" },
            h("div", { class: "numero" }, h("b", { title: recordedTime(total) }, summaryTime(total)), h("span", { class: "numero-icone" }, icon("ficha")), h("span", { class: "numero-nome" }, "Capturado (estimativa)")),
            h("p", { class: "vazio" }, `Acumulado ${summaryTime(accumulated)}: soma as frentes simultâneas; capturado conta o tempo sobreposto uma vez.`)),
          h("section", { class: "totais-semana" }, h("h2", {}, "Rateio sugerido na semana"),
            !Array.isArray(sheetWeek.totais) ? h("p", { class: "vazio" }, "Totais semanais disponíveis no painel local.")
              : sheetWeek.totais.length ? h("table", {}, h("thead", {}, h("tr", {}, h("th", {}, "Tipo"), h("th", {}, "Código"), h("th", { class: "num" }, "Total"))),
              h("tbody", {}, sheetWeek.totais.map((r) => h("tr", {}, h("td", {}, label(r.tipo)), h("td", {}, r.codigo || "Sem código"), h("td", { class: "num" }, summaryTime(r.total))))))
              : h("p", { class: "vazio" }, "Sem horas que contam na ficha nesta semana."))),
        h("h2", {}, "Por dia", h("span", { class: "legenda-barra" }, "barra: atividade em relação ao dia mais ativo")),
        h("div", { class: "semana-grade" }, week.dias.map((day) => day.data > estado.hoje && !day.horas
          ? h("article", { class: "dia-card futuro" },  // dia futuro compacto
            h("div", { class: "dia-topo" }, h("span", {}, weekday(day.data)), h("strong", {}, day.data.slice(8, 10))),
            h("p", { class: "dia-vazio" }, "Ainda não chegou"))
          : h("article", {
          class: "dia-card" + (day.data === estado.hoje ? " hoje" : ""),
        },
          h("div", { class: "dia-topo" },
            h("button", { class: "link", type: "button", disabled: !!SNAPSHOT && day.data !== SNAPSHOT.ficha.data,
              title: SNAPSHOT && day.data !== SNAPSHOT.ficha.data ? "Ficha deste dia disponível no painel local" : "Abrir ficha de " + fmtDate(day.data),
              onclick: () => { app.ficha = day.data; location.hash = "ficha"; } },
              h("span", {}, weekday(day.data)), h("strong", {}, day.data.slice(8, 10)))),
          h("div", { class: "dia-horas" }, h("strong", { title: recordedTime(day.horas) }, summaryTime(day.horas)), h("span", {}, "capturadas")),
          h("p", { class: "vazio" }, `Acumulado: ${summaryTime(day.acumulado ?? day.horas)}`),
          day.informado ? h("p", { class: "vazio" }, `Informado: ${recordedTime(day.informado)}`) : null,
          h("div", { class: "dia-barra", "aria-hidden": "true", title: "Atividade em relação ao dia mais ativo da semana" }, h("i", { style: `width:${Math.round(day.horas / peak * 100)}%` })),
          day.tarefas.length ? h("ul", { class: "dia-tarefas" }, day.tarefas.slice(0, 3).map((task) =>
            h("li", {}, h("button", { class: "link", type: "button", title: task.titulo, onclick: () => openTask(task.tarefa) }, task.titulo), h("span", {}, recordedTime(task.horas)))))
            : h("p", { class: "dia-vazio" }, day.data > estado.hoje ? "Ainda não chegou" : "Sem atividade"),
          day.tarefas.length > 3 ? h("button", { class: "link dia-mais", type: "button", disabled: !!SNAPSHOT && day.data !== SNAPSHOT.ficha.data,
            onclick: () => { app.ficha = day.data; location.hash = "ficha"; } }, `+${day.tarefas.length - 3} tarefas na ficha`) : null))));
    },
  },
  ficha: {
    titulo: "Ficha de horas",
    descricao: "Compare os tempos do dia e revise seus lançamentos.",
    icone: "ficha",
    async render(estado) {
      const day = SNAPSHOT ? SNAPSHOT.ficha.data : app.ficha || estado.hoje;
      const sheet = await api("/api/ficha?data=" + day);
      const rows = sheet.linhas;
      const code = (row, task) => task ? h("button", { class: "link ficha-codigo", type: "button", title: "Abrir card: " + task.titulo,
        "aria-label": `Abrir card ${row.codigo}: ${task.titulo}`, onclick: () => openTask(task.id) }, row.codigo || "Sem código")
        : h("strong", { class: "ficha-codigo" }, row.codigo || "Sem código");
      const pendingWindows = (app.rascunho.correcoes || []).some((c) => c.data === day);
      const capturedSheet = rows.reduce((sum, row) => sum + (row.capturado || 0), 0);
      const capturedExtras = sheet.extras.reduce((sum, row) => sum + (row.capturado || 0), 0);
      const registeredExtras = sheet.extras.reduce((sum, row) => sum + extraRecorded(row), 0);
      const registeredSheet = rows.reduce((sum, row) => sum + (row.registrado ?? row.capturado ?? 0), 0);
      const difference = sheet.horas_dia - registeredSheet;
      const hasManual = !!sheet.informado_total;
      const balance = sheet.horas_dia - sheet.total;
      const metric = (name, value, detail, symbol) => h("div", { class: "ficha-metrica" },
        h("span", { class: "ficha-metrica-nome" }, icon(symbol), name),
        h("strong", { title: recordedTime(value) }, summaryTime(value)), h("span", { class: "ficha-metrica-detalhe" }, detail));
      const estimate = SNAPSHOT ? null : await estimateSection();
      return h("section", { class: "ficha-dia" },
        h("div", { class: "ficha-periodo" }, dayNav("ficha", day, 1, `${weekday(day)} ${fmtDate(day)}`),
          h("span", { class: "ficha-jornada" }, `Jornada de ${recordedTime(sheet.horas_dia)}`)),
        h("div", { class: "ficha-indicadores", "aria-label": "Resumo do dia" },
          // Composição com segundos: as parcelas somam exatamente o total, sem parecer divergência de arredondamento.
          metric("Capturado", sheet.capturado_total, `${recordedTime(capturedSheet)} na ficha + ${recordedTime(capturedExtras)} extras`, "ficha"),
          metric("Rateio sugerido", sheet.total, "Demandas e projetos", "camadas"),
          metric(balance >= 0 ? "Saldo após rateio" : "Acima da jornada", Math.abs(balance),
            balance >= 0 ? "Para completar a jornada" : "Revise os tempos do dia", "alvo")),
        pendingWindows ? h("p", { class: "aviso" }, "Salve as correções de janelas para atualizar os totais.") : null,
        h("section", { class: "ficha-lancamentos", "aria-labelledby": "ficha-lancamentos-titulo" },
          h("header", { class: "ficha-secao-topo" }, h("h2", { id: "ficha-lancamentos-titulo" }, "Demandas e projetos"),
            h("span", { class: "contador" }, rows.length)),
          rows.length ? h("div", { class: "ficha-tabela" + (hasManual ? " com-informado" : "") }, h("table", {},
            h("thead", {}, h("tr", {}, ["Item", "Capturado", ...(hasManual ? ["Informado"] : []), "Rateado", "Observação"].map((c) =>
              h("th", { scope: "col", class: ["Capturado", "Informado", "Rateado"].includes(c) ? "num" : null }, c)))),
            h("tbody", {}, rows.map((r) => {
              const task = sheetTask(r, estado.tarefas);
              return h("tr", {},
                h("td", { class: "ficha-item", "data-label": "Item" },
                  h("div", { class: "ficha-item-origem" }, task ? stateIcon(task) : icon("camadas"), code(r, task), h("span", {}, r.rotulo)),
                  task ? h("button", { class: "link ficha-item-titulo", type: "button", onclick: () => openTask(task.id) }, task.titulo) : null),
                h("td", { class: "num ficha-tempo", "data-label": "Capturado" }, r.capturado ? recordedTime(r.capturado)
                  : h("span", { class: "ficha-sem-captura", title: "Sem captura individual neste código" }, "Sem captura individual")),
                hasManual ? h("td", { class: "num ficha-tempo", "data-label": "Informado" }, recordedTime(r.informado)) : null,
                h("td", { class: "num ficha-tempo ficha-rateado", "data-label": "Rateado" }, r.total ? recordedTime(r.total) : "—"),
                h("td", { class: "ficha-observacao", "data-label": "Observação" },
                  (r.observacao || "").trim() ? h("div", { class: "ficha-observacao-texto" }, r.observacao)
                    : h("span", { class: "ficha-sem-observacao", title: "Demanda dispensa observação" }, "—"),
                  (r.observacao || "").trim() ? h("button", { class: "botao ficha-copiar", type: "button", onclick: (e) => copy(r.observacao, e.currentTarget) }, icon("copiar"), "Copiar observação") : null,
                  r.complemento ? h("details", { class: "ficha-complemento" }, h("summary", {}, "Complemento local"), h("div", { class: "markdown" }, markdown(r.complemento))) : null));
            })))) : h("div", { class: "estado-vazio" }, icon("ficha"), h("h3", {}, "Nenhuma hora que conta na ficha neste dia."),
              h("p", {}, "Escolha outro dia ou confira os detalhes de atividade abaixo."))),
        h("div", { class: "ficha-apoio" },
          h("details", { class: "ficha-detalhes" },
            h("summary", {}, icon("livro"), h("span", {}, "Como ler os tempos")),
            h("div", { class: "ficha-detalhes-corpo" },
              h("dl", { class: "ficha-definicoes" },
                h("div", {}, h("dt", {}, "Capturado"), h("dd", {}, "Estimativa por janelas de 30 minutos. Janelas antigas valem 15 minutos. Frentes simultâneas dividem o tempo sobreposto.")),
                h("div", {}, h("dt", {}, "Rateado"), h("dd", {}, "Sugestão com até 50% de margem, limitada a 1h por código e ao saldo da jornada. Você decide o que apontar.")),
                h("div", {}, h("dt", {}, "Acumulado"), h("dd", {}, `${recordedTime(sheet.acumulado_total)} somando frentes simultâneas e lançamentos existentes.`))),
              h("p", { class: "ficha-nota" }, `Capturado na ficha: ${recordedTime(capturedSheet)} · Extras: ${recordedTime(capturedExtras)}`),
              hasManual ? h("p", { class: "ficha-nota" }, `Informado: ${recordedTime(sheet.informado_total)} em lançamentos existentes.`) : null,
              h("p", { class: "ficha-nota" }, difference >= 0 ? `Saldo usando a base capturada/informada: ${recordedTime(difference)}` : `Base acima da jornada: ${recordedTime(-difference)}`))),
          h("details", { class: "ficha-detalhes" },
            h("summary", {}, icon("laptop"), h("span", {}, "Extras"), h("span", { class: "ficha-detalhes-meta" }, `${sheet.extras.length} · ${recordedTime(registeredExtras)}`)),
            h("div", { class: "ficha-detalhes-corpo" }, h("p", { class: "ficha-nota" }, "Atividades fora do total da ficha."),
              sheet.extras.length ? h("ul", { class: "ficha-lista-extras" }, sheet.extras.map((e) => h("li", {},
                h("button", { class: "link", type: "button", onclick: () => openTask(e.tarefa) }, e.titulo), h("strong", { title: extraDetail(e) }, recordedTime(extraRecorded(e))))))
                : h("p", { class: "vazio" }, "Nenhum extra."))),
          h("details", { class: "ficha-detalhes ficha-janelas", open: app.editando || pendingWindows },
            h("summary", {}, icon("historico"), h("span", {}, "Janelas de atividade"), h("span", { class: "ficha-detalhes-meta" }, (sheet.janelas || []).length)),
            h("div", { class: "ficha-detalhes-corpo" },
              h("p", { class: "ficha-nota" }, app.editando ? "Desconsidere as janelas que não representam trabalho e salve as alterações." : "Use Editar para revisar quais janelas entram nos tempos do dia."),
              sheet.janelas && sheet.janelas.length ? h("div", { class: "ficha-tabela-apoio" }, h("table", {},
                h("thead", {}, h("tr", {}, ["Horário", "Tarefa", "Estado", ...(app.editando ? ["Ação"] : [])].map((c) => h("th", { scope: "col" }, c)))),
                h("tbody", {}, sheet.janelas.map((j) => {
                  const pending = (app.rascunho.correcoes || []).find((c) => c.data === day && c.janela === j.janela && c.tarefa === j.tarefa);
                  const ignored = pending && "ignorar" in pending ? pending.ignorar : j.ignorar;
                  const target = pending && pending.para ? windowTargets().find((t) => t.id === pending.para) : null;
                  return h("tr", {}, h("td", {}, `${j.janela} · ${j.minutos ?? 15} min`), h("td", {}, target ? `${j.titulo} → ${target.titulo}` : j.titulo),
                    h("td", {}, h("span", { class: "selo neutro" }, ignored ? "Desconsiderada" : "Considerada")),
                    app.editando ? h("td", { class: "janela-acoes" },
                      h("button", { class: "botao", type: "button", onclick: () => toggleWindow(day, j, !ignored) }, ignored ? "Considerar" : "Desconsiderar"),
                      h("select", { "aria-label": "Mover janela para outra tarefa", onchange: (e) => moveWindow(day, j, e.target.value) },
                        h("option", { value: "" }, "Mover para…"),
                        windowTargets().filter((t) => t.id !== j.tarefa)
                          .map((t) => h("option", { value: t.id, selected: target && target.id === t.id }, (t.numero ? `@${t.numero} ` : "") + t.titulo)))) : null);
                })))) : h("p", { class: "vazio" }, "Nenhuma janela registrada neste dia."))),
          estimate ? h("details", { class: "ficha-detalhes" }, h("summary", {}, icon("alvo"), h("span", {}, "Calibração de estimativas")),
            h("div", { class: "ficha-detalhes-corpo ficha-tabela-apoio" }, estimate)) : null));
    },
  },
  historico: {
    titulo: "Registro de alterações",
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
          h("span", {}, icon("historico"), ` ${data.eventos.length} de ${data.total} ações carregadas · ${data.pendentes} não analisadas`),
          switchInput("Só não analisadas", onlyPending, (e) => { setPref("historico.pendentes", e.target.checked ? "1" : "0"); render(); }),
          h("label", {}, "Origem ", h("select", { onchange: (e) => { setPref("historico.origem", e.target.value); render(); } },
            [["", "Todas"], ["agente", "Agente"], ["quadro", "Quadro"]].map(([v, n]) => h("option", { value: v, selected: v === origin }, n))))),
        // Linhas compactas agrupadas por dia: ação, tarefa, origem e horário; o detalhe fica recolhido.
        rows.length ? Object.entries(rows.reduce((days, event) => {
          const day = when(event.ts).split(" ")[0] || "Sem data";
          (days[day] = days[day] || []).push(event);
          return days;
        }, {})).map(([day, events]) => h("section", { class: "historico-dia" },
          h("h2", {}, day, h("span", { class: "contador" }, events.length)),
          h("ol", { class: "historico-lista", "aria-label": "Ações de " + day }, (() => {
            const row = (event, extra) => {
              const action = actions[event.acao] || ["historico", event.acao];
              const detail = eventDetail(event, titles);
              const source = event.origem === "agente" ? "Agente" : event.origem === "quadro" ? "Quadro" : event.origem;
              const target = event.tarefa ? h("button", { class: "link titulo", type: "button", onclick: () => openTask(event.tarefa) }, titles[event.tarefa] || event.tarefa)
                : event.coluna ? h("span", { class: "titulo" }, columnName(event.coluna)) : h("span", { class: "titulo" });
              return h("li", { class: "evento-linha" + (event.pendente ? " pendente" : "") },
                h("span", { class: "evento-icone", title: action[1] }, icon(action[0])),
                h("span", { class: "evento-acao", title: event.acao }, action[1]), target,
                event.pendente ? h("span", { class: "indicador-pendente", title: "Não analisada" }, "não analisada") : null,
                h("span", { class: "evento-origem" }, source),
                h("time", { class: "evento-hora", datetime: event.ts, title: when(event.ts) }, when(event.ts).split(" ").slice(1).join(" ") || when(event.ts)),
                detail ? h("details", { class: "evento-detalhes" }, h("summary", {}, "Detalhes"), h("p", {}, detail)) : null,
                extra || null);
            };
            // Ações consecutivas da mesma tarefa viram um grupo: a mais recente aparece e as demais ficam em "+N ações".
            const groups = [];
            for (const event of events) {
              const last = groups[groups.length - 1];
              if (last && event.tarefa && last[0].tarefa === event.tarefa) last.push(event);
              else groups.push([event]);
            }
            return groups.map((group) => group.length === 1 ? row(group[0])
              : row(group[0], h("details", { class: "evento-grupo" }, h("summary", {}, `+${group.length - 1} ${group.length === 2 ? "ação" : "ações"} nesta tarefa`),
                h("ol", { class: "historico-lista" }, group.slice(1).map((event) => row(event))))));
          })())))
          : emptyState("Nenhuma ação com esses filtros", "Tente outra origem ou desmarque o filtro de ações não analisadas."),
        data.total > limit ? h("p", {}, h("button", { class: "botao", type: "button", onclick: () => { app.historicoLimite = limit + 200; render(); } }, "Carregar mais")) : null);
    },
  },
};
const NAV_GROUPS = [
  { titulo: "Trabalho", visoes: ["hoje", "quadro", "epicos"] },
  { titulo: "Planejamento", visoes: ["prazos", "perguntas"] },
  { titulo: "Horas e registros", visoes: ["semana", "ficha", "historico"] },
];
const ORDER = NAV_GROUPS.flatMap((group) => group.visoes);

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
          h("span", { class: "calendario-tarefas", "aria-hidden": "true" }, due.slice(0, 2).map((task) => h("span", {}, stateIcon(task), h("span", {}, task.titulo))), due.length > 2 ? h("small", {}, `+${due.length - 2}`) : null));
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

const FIELD_LABELS = { proximo_passo: "próximo passo", descricao: "descrição", coluna: "coluna", prazo: "prazo", titulo: "título",
  aguardando: "aguardando", aguardando_desde: "aguardando desde", ficha: "texto da ficha", size: "size", pai: "faz parte de",
  nivel: "nível", issue: "issue", demanda: "demanda", projeto: "projeto", pessoal: "pessoal", ordem: "ordem", resposta: "resposta" };

function eventDetail(e, titles) {
  if (e.acao === "analise") return `${(e.eventos || []).length} ação(ões): ${e.resultado || ""}`;
  if (e.de && e.para) return `${columnName(e.de)} → ${columnName(e.para)}`;
  if (e.campos) return "Campos alterados: " + e.campos.map((c) => FIELD_LABELS[c] || c).join(", ");
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
    fill(nav, NAV_GROUPS.map((group) => h("div", { class: "nav-grupo", role: "group", "aria-label": group.titulo },
      h("span", { class: "nav-grupo-titulo", "aria-hidden": "true" }, group.titulo),
      group.visoes.map((name) => {
        const index = ORDER.indexOf(name);
        return h("button", {
          type: "button", class: "nav-item", title: `${VIEWS[name].titulo} (Alt+${index + 1})`, "data-view": name, "aria-keyshortcuts": `Alt+${index + 1}`,
          onclick: () => { setMenuOpen(false); location.hash = name; document.getElementById("conteudo").focus({ preventScroll: true }); },
          onkeydown: (event) => {
            let target = index;
            if (event.key === "ArrowRight" || event.key === "ArrowDown") target = (index + 1) % ORDER.length;
            else if (event.key === "ArrowLeft" || event.key === "ArrowUp") target = (index - 1 + ORDER.length) % ORDER.length;
            else if (event.key === "Home") target = 0;
            else if (event.key === "End") target = ORDER.length - 1;
            else return;
            event.preventDefault();
            nav.querySelectorAll("button[data-view]")[target].focus();
            location.hash = ORDER[target];
          },
        }, icon(VIEWS[name].icone), h("span", { class: "nav-texto" }, VIEWS[name].titulo), h("span", { class: "contador", "data-count": name }));
      }))));
  }
  for (const button of nav.querySelectorAll("button[data-view]")) {
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
    // Coluna vazia recolhida não tem área de itens: guarda só as que rolam.
    columns: [...oldBoard.querySelectorAll(".coluna")].map((n) => [n.dataset.coluna, n.querySelector(".itens")?.scrollTop || 0]) } : null;
  app.view = name;
  main.classList.toggle("quadro-ativo", name === "quadro");
  main.setAttribute("aria-busy", "true");
  const filter = document.querySelector(".filtro");
  filter.hidden = name === "semana" || name === "ficha";
  document.getElementById("filtro").setAttribute("aria-label", name === "historico" ? "Filtrar histórico" : "Filtrar tarefas");
  document.getElementById("filtro").placeholder = name === "historico" ? "Buscar nas ações carregadas…" : `Buscar em ${VIEWS[name].titulo.toLocaleLowerCase("pt-BR")}…`;
  const estado = effectiveState();
  const options = VIEWS[name].opcoes ? VIEWS[name].opcoes(estado) : [];
  fill(document.getElementById("opcoes"), options);
  // No celular, filtros e ordenação ficam atrás de "Filtros"; a busca continua visível.
  const toggle = document.getElementById("alternar-filtros");
  if (toggle) {
    toggle.hidden = !options.length;
    toggle.onclick = () => {
      const open = document.querySelector(".barra-filtro").classList.toggle("filtros-abertos");
      toggle.setAttribute("aria-expanded", String(open));
    };
  }
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
          const list = column.querySelector(".itens");
          if (saved && list) list.scrollTop = saved[1];
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

function setMenuOpen(open, restoreFocus = false) {
  const button = document.getElementById("menu-visoes");
  app.menuOpen = open;
  document.querySelector(".navegacao").classList.toggle("menu-aberto", open);
  button.setAttribute("aria-expanded", String(open));
  button.setAttribute("aria-label", open ? "Fechar menu de navegação" : "Abrir menu de navegação");
  fill(button, icon(open ? "fechar" : "painel"), h("span", {}, "Menu"));
  if (open) document.querySelector('#abas [aria-current="page"]')?.focus({ preventScroll: true });
  if (restoreFocus) button.focus();
}

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
  if (!matchMedia("(max-width: 760px)").matches) setMenuOpen(false);
}

const PALETTES = [
  ["azul", "Azul", "#8bb5ff"],
  ["verde", "Verde", "#82db9c"],
  ["violeta", "Violeta", "#c2a3ff"],
  ["rosa", "Rosa", "#f59ac5"],
  ["vermelho", "Vermelho", "#db867a"],
  ["ambar", "Âmbar", "#e8bf71"],
  ["turquesa", "Turquesa", "#78d7cc"],
  ["preto", "Preto", "#111111"],
  ["neutro", "Grafite", "#5e6775"],
  ["ya-labs", "YA LABS", "#e8ac39"],
];

function renderPalettes() {
  const saved = pref("paleta", "azul");
  const current = PALETTES.some(([id]) => id === saved) ? saved : "azul";
  document.documentElement.dataset.palette = current;
  fill(document.getElementById("paletas-opcoes"), ...PALETTES.map(([id, label, color]) => h("button", {
    type: "button", "aria-pressed": String(id === current),
    onclick: () => {
      setPref("paleta", id);
      renderPalettes();
      document.getElementById("paletas").open = false;
      document.querySelector("#paletas summary").focus();
    }
  }, h("span", { class: "paleta-cor", style: `background:${color}`, "aria-hidden": "true" }), label)));
}

function renderTheme() {
  const current = pref("tema", "auto");
  const [, title, iconName] = THEMES.find((t) => t[0] === current) || THEMES[0];
  const button = document.getElementById("tema");
  button.title = title + " (clique para trocar)";
  button.setAttribute("aria-label", button.title);
  fill(button, icon(iconName), h("span", { class: "controle-rotulo" }, ({ auto: "Automático", light: "Claro", dark: "Escuro" })[current] || "Automático"));
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
      h("dt", {}, h("kbd", {}, "Alt"), " + ", h("kbd", {}, "1–8")), h("dd", {}, "Trocar de visão na ordem do menu"),
      h("dt", {}, h("kbd", {}, "←"), " / ", h("kbd", {}, "→"), " / ", h("kbd", {}, "↑"), " / ", h("kbd", {}, "↓")), h("dd", {}, "Trocar de visão com o foco na navegação"),
      h("dt", {}, h("kbd", {}, "Home"), " / ", h("kbd", {}, "End")), h("dd", {}, "Ir à primeira ou à última visão"),
      h("dt", {}, h("kbd", {}, "Enter"), " / ", h("kbd", {}, "Espaço")), h("dd", {}, "Abrir o card em foco"),
      h("dt", {}, h("kbd", {}, "Esc")), h("dd", {}, "Fechar o painel e voltar ao item de origem"),
      h("dt", {}, h("kbd", {}, "?")), h("dd", {}, "Mostrar esta ajuda")));
}

document.addEventListener("keydown", (event) => {
  if (event.defaultPrevented || event.isComposing) return;
  // Com o visualizador aberto, o próprio <dialog> trata Esc e as setas; o painel por trás fica intacto.
  if (app.visualizador) return;
  if (event.key === "Escape" && app.menuOpen) { event.preventDefault(); setMenuOpen(false, true); return; }
  if (event.key === "Escape" && !document.getElementById("painel").hidden) { event.preventDefault(); closePanel(); return; }
  const target = event.target instanceof Element ? event.target : null;
  if (target && target.closest("input, textarea, select, [contenteditable]:not([contenteditable=false])")) return;
  if (event.ctrlKey || event.metaKey) return;
  if (event.altKey) {
    if (!event.shiftKey && /^[1-8]$/.test(event.key)) {
      event.preventDefault(); setMenuOpen(false); closePanel(false); location.hash = ORDER[Number(event.key) - 1];
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
  if (app.visualizador || event.composedPath().some(node => node instanceof Element && node.matches("dialog.visualizador"))) return;
  if (!panel.hidden && !event.composedPath().includes(panel)) closePanel(false);
});
document.addEventListener("DOMContentLoaded", () => {
  renderTheme();
  renderPalettes();
  document.addEventListener("click", (event) => {
    const picker = document.getElementById("paletas");
    if (!picker.contains(event.target)) picker.open = false;
  });
  document.getElementById("paletas").addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      event.preventDefault(); event.stopPropagation();
      document.getElementById("paletas").open = false;
      document.querySelector("#paletas summary").focus();
    }
  });
  setMenuOpen(false);
  document.getElementById("menu-visoes").addEventListener("click", () => setMenuOpen(!app.menuOpen));
  renderNavigation();
  document.getElementById("compactar").addEventListener("click", () => {
    const next = document.documentElement.dataset.nav === "compacta" ? "expandida" : "compacta";
    app.navPreference = next;
    try { localStorage.setItem("yabook.navegacao", next); } catch (error) { /* sem armazenamento persistente */ }
    document.documentElement.dataset.nav = next;
    renderNavigation();
  });
  matchMedia("(max-width: 1190px)").addEventListener("change", renderNavigation);
  matchMedia("(max-width: 760px)").addEventListener("change", renderNavigation);
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
  window.addEventListener("beforeunload", event => {
    if (!Object.keys(app.anexosRascunho).length) return;
    event.preventDefault();
    event.returnValue = "";
  });
  app.editando = !SNAPSHOT && draftCount() > 0;
  setInterval(refreshChangeTimes, 60000);
  document.addEventListener("visibilitychange", refreshChangeTimes);
  refresh();
  listen();
  // Sem PWA: remove o service worker e o cache deixados pelas versões antigas.
  if (!SNAPSHOT && "serviceWorker" in navigator) {
    navigator.serviceWorker.getRegistrations().then((list) => list.forEach((r) => r.unregister())).catch(() => {});
    if ("caches" in window) caches.keys().then((keys) => keys.forEach((k) => caches.delete(k))).catch(() => {});
  }
});

// Edição -----------------------------------------------------------------------
// Rascunho local: {tarefas: {id: {revision, campos, unset, registro}}, colunas: {id: nome}, complementos: [], correcoes: []}.
function emptyDraft() {
  return { tarefas: {}, colunas: {}, complementos: [], correcoes: [] };
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
  return new Set([...Object.keys(d.tarefas), ...Object.keys(app.anexosRascunho)]).size
    + Object.keys(d.colunas).length + d.complementos.length + (d.correcoes || []).length;
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
    compare("descricao", values.descricao.trim(), original.descricao);
    compare("coluna", values.coluna, original.coluna);
    compare("prazo", values.prazo, original.prazo);
    compare("size", values.size, original.size ? String(original.size) : "");
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
    const anotacoes = entry?.anotacoes || [];
    if (!Object.keys(campos).length && !registro && !anotacoes.length) {
      if (entry) { delete app.rascunho.tarefas[id]; persistDraft(); }
    } else {
      const keep = entry && entry.campos.ordem !== undefined && !("coluna" in campos && campos.coluna !== entry.campos.coluna) ? { ordem: entry.campos.ordem } : {};
      app.rascunho.tarefas[id] = { revision: entry?.revision || original.revision, campos: { ...keep, ...campos }, unset: [], anotacoes, ...(registro ? { registro } : {}) };
      persistDraft();
    }
    closePanel();
    render();
    announce("Rascunho atualizado. Use Salvar para gravar as alterações.");
  } },
    h("h2", { style: "margin:0" }, "Editar tarefa"),
    h("p", { class: "vazio", style: "margin:0" }, "Aplique as mudanças ao rascunho e depois use Salvar na barra de filtros."),
    field("titulo", "Título", h("input", { name: "titulo", value: task.titulo, required: true })),
    field("descricao", "Descrição (objetivo e escopo em Markdown)", h("textarea", { name: "descricao", rows: 5 }, task.descricao || "")),
    field("coluna", "Coluna", h("select", { name: "coluna" }, effectiveState().colunas.map((c) => h("option", { value: c.id, selected: c.id === task.coluna }, c.nome)))),
    h("div", { class: "campos-linha" },
      field("prazo", "Prazo", h("input", { name: "prazo", type: "date", value: task.prazo || "" })),
      field("size", "Tamanho (entrega com agentes)", h("select", { name: "size" }, h("option", { value: "" }, "Sem tamanho"),
        [1, 2, 3, 4, 5].map((n) => h("option", { value: String(n), selected: task.size === n }, String(n)))))),
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

function toggleWindow(day, entry, ignored) {
  if (app.salvando) return;
  const corrections = app.rascunho.correcoes || [];
  app.rascunho.correcoes = corrections.filter((c) => !(c.data === day && c.janela === entry.janela && c.tarefa === entry.tarefa));
  if (ignored !== entry.ignorar) app.rascunho.correcoes.push({ data: day, janela: entry.janela, tarefa: entry.tarefa, ignorar: ignored });
  persistDraft();
  render();
}

// Tarefas abertas que podem receber uma janela; sem estado completo, nenhuma.
function windowTargets() {
  try { return (effectiveState().tarefas || []).filter((t) => t.tipo !== "pergunta" && !CLOSED.includes(t.papel)); } catch (e) { return []; }
}

// Mover janela: correção reversível que leva a janela capturada para a tarefa certa, sem duplicar tempo.
function moveWindow(day, entry, target) {
  if (app.salvando) return;
  app.rascunho.correcoes = (app.rascunho.correcoes || []).filter((c) => !(c.data === day && c.janela === entry.janela && c.tarefa === entry.tarefa));
  if (target) app.rascunho.correcoes.push({ data: day, janela: entry.janela, tarefa: entry.tarefa, para: target });
  persistDraft();
  render();
}

function startEditing() {
  app.editando = true;
  render();
}

function draftExitLabel(count) {
  return count ? "Descartar" : "Sair";
}

function draftExitButton(attrs, count = draftCount()) {
  return h("button", { class: "botao", type: "button", disabled: !!app.salvando, onclick: discardDraft, ...attrs },
    icon("desfazer"), h("span", {}, draftExitLabel(count)));
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
  const panelExit = document.getElementById("painel-descartar");
  if (panelExit) {
    panelExit.disabled = !!app.salvando;
    panelExit.lastElementChild.textContent = draftExitLabel(count);
  }
  const items = app.editando ? [
    app.pendente ? h("span", { class: "selo cor-orange", title: "Salve ou descarte para ver as mudanças" }, "repositório mudou") : null,
    h("span", { class: "selo cor-orange" }, count ? `${count} ${count === 1 ? "alteração" : "alterações"} no rascunho` : "Modo Editar"),
    draftExitButton({ id: "descartar" }, count),
    h("button", { id: "salvar", class: "botao primario", type: "button", disabled: !count || !!app.salvando, onclick: saveDraft }, icon("salvar"), app.salvando ? "Salvando…" : "Salvar"),
  ] : [h("button", { class: "botao", type: "button", onclick: startEditing }, icon("editar"), "Editar")];
  bar.replaceChildren(...items.filter(Boolean));
}

async function discardDraft() {
  if (app.salvando) return false;
  if (draftCount() && !window.confirm("Descartar as alterações não salvas?")) return false;
  app.rascunho = emptyDraft();
  app.anexosRascunho = {};
  persistDraft();
  app.editando = false;
  app.pendente = false;
  await refresh();
  return true;
}

async function saveDraft() {
  if (app.salvando || !draftCount()) return;
  app.salvando = true;
  renderToolbar();
  announce("Salvando alterações…");
  const d = app.rascunho;
  const body = {
    colunas: Object.entries(d.colunas).map(([id, nome]) => ({ id, nome })),
    complementos: d.complementos,
    correcoes: d.correcoes || [],
  };
  let response, result;
  try {
    body.tarefas = await draftChanges(d, app.anexosRascunho);
    const payload = JSON.stringify(body);
    if (new TextEncoder().encode(payload).length > 2000000) {
      app.salvando = false;
      renderToolbar();
      return showPanel(h("p", { class: "aviso erro" }, "O rascunho passa de 2 MB. Remova anexos do rascunho e salve em etapas."));
    }
    response = await fetch("/api/salvar", { method: "POST", headers: { "Content-Type": "application/json", "X-YABook-Token": TOKEN }, body: payload });
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
    app.anexosRascunho = {};
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
    const materials = lost.some(([id, e]) => e?.anotacoes?.length || app.anexosRascunho[id]);
    if (materials) {
      app.pendente = false;
      await refresh();
      return showPanel(h("h2", {}, "Tarefa alterada em outro lugar"),
        h("p", { class: "aviso erro" }, result.error),
        h("p", {}, "O rascunho foi mantido. Confira ou copie suas anotações no card antes de descartar e refazer sobre a versão atual."));
    }
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
