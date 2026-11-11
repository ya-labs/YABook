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
    items.push(pill(task.codigo, "gray", { title: task.pessoal ? "Código" : "Código na ficha", icon: "repo" }));
  }
  if (task.pessoal && !options.semPessoal) items.push(pill("pessoal", "pink", { title: "Sem numeração da empresa" }));
  if (task.prazo && !CLOSED.includes(task.papel)) {
    const days = daysUntil(task.prazo);
    items.push(pill(fmtDate(task.prazo), days < 0 ? "red" : days <= 2 ? "orange" : "gray", { icon: "calendario", title: "Prazo" }));
  }
  if (task.perguntas_abertas) items.push(pill(`${task.perguntas_abertas} pergunta${task.perguntas_abertas > 1 ? "s" : ""}`, "blue", { icon: "pergunta" }));
  if (task.confidencial === "disponivel") items.push(pill("confidencial", "yellow", { icon: "cadeado", title: "Referência confidencial disponível nesta máquina" }));
  if (task.confidencial === "bloqueado") items.push(pill("confidencial", "gray", { icon: "cadeado", title: "Base confidencial ausente nesta máquina" }));
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

function card(task, options = {}) {
  const editable = app.editando && task.tipo !== "pergunta";
  return h("div", { class: "card" + (task.editado ? " editado" : ""), role: "button", tabindex: "0", "data-id": task.id,
    draggable: editable ? "true" : null,
    ondragstart: editable ? (e) => { e.dataTransfer.setData("text/plain", task.id); e.dataTransfer.effectAllowed = "move"; } : null,
    onclick: () => openTask(task.id), onkeydown: (e) => { if (e.key === "Enter") openTask(task.id); } },
    h("div", { class: "card-origem" }, stateIcon(task), h("span", {}, origin(task))),
    h("div", { class: "card-titulo" }, task.titulo),
    h("div", { class: "rotulos" }, badges(task, options)),
    task.nivel === "epico" ? epicProgress(task) : null,
    task.proximo_passo && !CLOSED.includes(task.papel) ? h("div", { class: "card-passo" }, task.proximo_passo) : null);
}

async function openTask(id) {
  const panel = document.getElementById("painel");
  panel.hidden = false;
  fill(panel, h("div", { class: "painel-corpo" }, h("p", { class: "vazio" }, "Carregando…")));
  try {
    const detail = await api("/api/tarefa/" + encodeURIComponent(id));
    const data = detail.data;
    const task = effectiveState().tarefas.find((t) => t.id === id) || detail.resumo;
    const parent = data.pai ? app.estado.tarefas.find((t) => t.id === data.pai) : null;
    const ref = issueRef(data);
    const field = (name, value) => value ? [h("dt", {}, name), h("dd", {}, value)] : null;
    fill(panel,
      h("div", { class: "painel-topo" },
        h("h2", {}, data.titulo, ref ? h("span", { class: "vazio" }, ` #${ref.number}`) : null),
        h("button", { class: "botao-icone discreto", type: "button", title: "Fechar", onclick: closePanel }, icon("fechar"))),
      h("div", { class: "painel-corpo" },
        h("div", { class: "card-origem" }, stateIcon(task), h("span", {}, `${origin(task)} · ${data.id}`)),
        h("div", { class: "rotulos" }, badges(task, { semPai: true })),
        task.nivel === "epico" ? epicProgress(task) : null,
        h("dl", { class: "campos-lista" },
          field("Status", h("span", { class: "selo neutro forte" }, h("span", { class: `status papel-${roleOf(data.coluna)}` }), columnName(data.coluna))),
          field("Tipo", label(data.tipo)),
          field("Faz parte de", parent ? h("button", { class: "link", type: "button", onclick: () => openTask(parent.id) }, parent.titulo) : null),
          field("Código", task.codigo),
          field("Prazo", data.prazo ? fmtDate(data.prazo) : null),
          field("Issues", (data.issue || []).join(", ")),
          field("Próximo passo", data.proximo_passo)),
        detail.filhos && detail.filhos.length ? [h("h2", {}, "Itens"), h("div", { class: "caixa" }, detail.filhos.map((child) =>
          h("div", { class: "linha-caixa" }, stateIcon(child), h("button", { class: "link titulo", type: "button", onclick: () => openTask(child.id) }, child.titulo),
            h("span", { class: "selo neutro" }, columnName(child.coluna)))))] : null,
        detail.body ? [h("h2", {}, "Registro"), h("pre", { class: "registro" }, detail.body.trim())] : null,
        detail.complemento ? [h("h2", {}, "Complemento confidencial (local)"), h("pre", { class: "registro" }, detail.complemento.trim())] : null,
        Object.entries(detail.referencias || {}).map(([refName, text]) =>
          [h("h2", {}, refName), text ? h("pre", { class: "registro" }, text.trim()) : h("p", { class: "vazio" }, "Bloqueado: base confidencial ausente nesta máquina.")]),
        detail.confidencial === "bloqueado" && !Object.keys(detail.referencias || {}).length
          ? h("p", { class: "vazio" }, "Complemento confidencial só na máquina que possui a base.") : null,
        app.editando && data.tipo !== "pergunta" ? editForm(id) : null));
  } catch (error) {
    showPanel(h("p", { class: "aviso erro" }, error.message));
  }
}

function closePanel() {
  document.getElementById("painel").hidden = true;
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
      const active = estado.ativa ? tasks.find((t) => t.id === estado.ativa.id) : null;
      const doing = tasks.filter((t) => t.papel === "ativo" && (!active || t.id !== active.id)).sort(byOrder);
      const testing = tasks.filter((t) => t.papel === "validacao").sort(byOrder);
      const late = estado.prazos.filter((t) => daysUntil(t.prazo) < 0).length;
      app.contagem = doing.length + testing.length + (active ? 1 : 0);
      const list = (title, items, empty, render = row) => h("div", { class: "caixa" },
        h("header", {}, h("h3", {}, title), h("span", { class: "contador" }, items.length || "")),
        items.length ? items.map(render) : h("div", { class: "corpo vazio" }, empty));
      const full = (t) => estado.tarefas.find((x) => x.id === t.id) || t;
      return h("section", {},
        h("div", { class: "numeros" },
          [["Em andamento", tasks.filter((t) => t.papel === "ativo").length], ["Em validação", testing.length],
           ["Prazos próximos", estado.prazos.length], ["Atrasadas", late], ["Perguntas", estado.perguntas.length],
           ["Ações não analisadas", estado.eventos_pendentes]]
            .map(([name, total]) => h("div", { class: "numero" }, h("b", {}, total), name))),
        h("div", { class: "painel-dia" },
          h("div", {},
            h("h2", {}, "Tarefa ativa"),
            active ? h("div", { class: "cards" }, card(active)) : h("p", { class: "vazio" }, "Nenhuma tarefa ativa nesta máquina."),
            h("h2", {}, "Em andamento"),
            doing.length ? h("div", { class: "cards" }, doing.map(card)) : h("p", { class: "vazio" }, "Nada em andamento.")),
          h("div", {},
            list("Prazos", estado.prazos.map(full), "Nenhum prazo atrasado ou nos próximos 2 dias.",
              (t) => h("div", { class: "linha-caixa" }, stateIcon(t), titleLink(t), badges(t, { semNivel: true, semPai: true, semCodigo: true }).filter((n) => n.title === "Prazo"))),
            list("Perguntas para você", estado.perguntas.map(full), "Nenhuma pergunta aberta."),
            list("Em validação", testing, "Nada em validação."))));
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
        h("label", {}, h("input", { type: "checkbox", checked: showArchived, onchange: (e) => { setPref("quadro.arquivadas", e.target.checked ? "1" : "0"); render(); } }), "Arquivadas"),
      ];
    },
    render(estado) {
      const map = Object.fromEntries(estado.tarefas.map((t) => [t.id, t]));
      const epicFilter = pref("quadro.epico", "");
      const levelFilter = pref("quadro.nivel", "");
      const showArchived = pref("quadro.arquivadas", "0") === "1";
      const visible = filtered(work(estado)).filter((t) =>
        (!epicFilter || (epicFilter === "-" ? !epicOf(t, map) : epicOf(t, map) === epicFilter)) &&
        (!levelFilter || (levelFilter === "-" ? !t.nivel : t.nivel === levelFilter)));
      const columns = estado.colunas.filter((c) => showArchived || c.papel !== "arquivado");
      const epics = visible.filter((t) => t.nivel === "epico" && columns.some((c) => c.id === t.coluna))
        .sort((a, b) => CLOSED.includes(a.papel) - CLOSED.includes(b.papel) || byOrder(a, b));
      const items = visible.filter((t) => t.nivel !== "epico");
      app.contagem = items.filter((t) => columns.some((c) => c.id === t.coluna)).length + epics.length;
      const epicColumn = h("div", { class: "coluna coluna-epicos", "data-coluna": "epicos" },
        h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, "Épicos"), h("span", { class: "contador" }, String(epics.length))),
        h("div", { class: "itens" }, epics.length ? epics.map((t) => card(t, { status: true, semNivel: true }))
          : h("p", { class: "vazio", style: "text-align:center;font-size:12px" }, "Nenhum épico")));
      return h("div", { class: "quadro" }, columns.map((column) => {
        const cards = items.filter((t) => t.coluna === column.id).sort(byOrder);
        return h("div", { class: `coluna papel-${column.papel}`, "data-coluna": column.id,
          ondragover: app.editando ? (e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; e.currentTarget.classList.add("alvo"); } : null,
          ondragleave: app.editando ? (e) => e.currentTarget.classList.remove("alvo") : null,
          ondrop: app.editando ? (e) => { e.currentTarget.classList.remove("alvo"); dropCard(e, column.id, cards); } : null },
          h("header", {}, h("span", { class: "status" }), h("span", { class: "nome" }, column.nome), h("span", { class: "contador" }, String(cards.length)),
            h("span", { class: "acoes" }, app.editando
              ? h("button", { class: "botao-icone discreto", type: "button", title: "Renomear coluna", onclick: () => renameColumn(column) }, icon("mais"))
              : null)),
          h("div", { class: "itens" }, cards.length ? cards.map((t) => card(t)) : h("p", { class: "vazio", style: "text-align:center;font-size:12px" }, "Nenhum item")));
      }), epicColumn);
    },
  },
  epicos: {
    titulo: "Épicos",
    icone: "epicos",
    render(estado) {
      const tasks = work(estado);
      const children = (id) => tasks.filter((t) => t.pai === id)
        .sort((a, b) => ROLE_ORDER.indexOf(a.papel) - ROLE_ORDER.indexOf(b.papel) || byOrder(a, b));
      const text = (app.busca || "").toLowerCase();
      const matches = (t) => !text || [t.titulo, t.codigo, t.id].join(" ").toLowerCase().includes(text);
      const epics = estado.epicos.filter((e) => matches(e) || children(e.id).some(matches));
      const loose = filtered(tasks.filter((t) => !t.pai && t.nivel !== "epico" && !CLOSED.includes(t.papel))).sort(byOrder);
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
        }) : h("p", { class: "vazio" }, "Nenhum épico. Use --nivel epico ou task capture."),
        loose.length ? [h("h2", {}, "Sem épico"), h("div", { class: "cards" }, loose.map(card))] : null);
    },
  },
  prazos: {
    titulo: "Prazos",
    icone: "prazos",
    render(estado) {
      const rows = work(estado).filter((t) => t.prazo && !CLOSED.includes(t.papel)).sort((a, b) => a.prazo.localeCompare(b.prazo));
      if (!rows.length) return h("p", { class: "vazio" }, "Nenhuma tarefa aberta com prazo.");
      return h("table", {},
        h("thead", {}, h("tr", {}, h("th", {}, "Prazo"), h("th", { class: "num" }, "Dias"), h("th", {}, "Tarefa"), h("th", {}, "Código"), h("th", {}, "Coluna"))),
        h("tbody", {}, rows.map((t) => {
          const days = daysUntil(t.prazo);
          return h("tr", { class: days < 0 ? "atrasada" : "" },
            h("td", {}, fmtDate(t.prazo)), h("td", { class: "num" }, days < 0 ? `${-days} atrasada` : days),
            h("td", {}, h("button", { class: "link", type: "button", onclick: () => openTask(t.id) }, t.titulo)),
            h("td", {}, t.codigo || ""), h("td", {}, columnName(t.coluna)));
        })));
    },
  },
  perguntas: {
    titulo: "Perguntas",
    icone: "pergunta",
    render(estado) {
      const questions = estado.tarefas.filter((t) => t.tipo === "pergunta");
      const open = questions.filter((t) => !t.resposta && !CLOSED.includes(t.papel));
      const answered = questions.filter((t) => t.resposta).sort((a, b) => (b.atualizada || "").localeCompare(a.atualizada || "")).slice(0, 10);
      const about = (t) => {
        const target = t.sobre && estado.tarefas.find((x) => x.id === t.sobre);
        return target ? h("button", { class: "link", type: "button", onclick: () => openTask(target.id) }, target.titulo) : null;
      };
      return h("section", {},
        h("h2", {}, "Abertas"),
        open.length ? h("ul", { class: "perguntas" }, open.map((t) => h("li", {}, h("strong", {}, t.titulo), " ", about(t),
          h("div", { class: "passo" }, `Responda com: task answer ${t.id} <resposta>`)))) : h("p", { class: "vazio" }, "Nenhuma pergunta aberta."),
        answered.length ? [h("h2", {}, "Respondidas recentes"), h("ul", { class: "perguntas" }, answered.map((t) =>
          h("li", {}, h("strong", {}, t.titulo), " ", about(t), h("div", { class: "passo" }, "↳ " + t.resposta))))] : null);
    },
  },
  semana: {
    titulo: "Semana",
    icone: "semana",
    async render(estado) {
      const ref = app.semana || estado.hoje;
      const [week, sheetWeek] = await Promise.all([api("/api/semana?data=" + ref), api("/api/ficha?semana=1&data=" + ref)]);
      const confirmed = Object.fromEntries((sheetWeek.dias || []).filter((d) => d.confirmada).map((d) => [d.data, true]));
      const total = week.dias.reduce((sum, d) => sum + d.horas, 0);
      return h("section", {},
        dayNav("semana", ref, 7, `Semana de ${fmtDate(week.inicio)}`),
        h("div", { class: "numeros" }, h("div", { class: "numero" }, h("b", {}, hours(total)), h("span", {}, "Atividade estimada")),
          h("div", { class: "numero" }, h("b", {}, Object.keys(confirmed).length), h("span", {}, "Dias confirmados"))),
        h("h2", {}, "Por dia"),
        h("table", {}, h("thead", {}, h("tr", {}, h("th", {}, "Dia"), h("th", { class: "num" }, "Horas"), h("th", {}, "Tarefas"))),
          h("tbody", {}, week.dias.map((d) => h("tr", {},
            h("td", {}, h("button", { class: "link", type: "button", onclick: () => { app.ficha = d.data; location.hash = "ficha"; } }, weekday(d.data) + " " + fmtDate(d.data)),
              confirmed[d.data] ? h("span", { class: "selo" }, "confirmada") : null),
            h("td", { class: "num" }, d.horas ? hours(d.horas) : "—"),
            h("td", {}, d.tarefas.slice(0, 6).map((t) => h("span", { class: "selo", title: t.tarefa }, `${t.titulo} · ${hours(t.horas)}`))))))),
        h("h2", {}, "Totais da ficha na semana"),
        sheetWeek.totais.length ? h("table", {}, h("thead", {}, h("tr", {}, h("th", {}, "Tipo"), h("th", {}, "Código"), h("th", { class: "num" }, "Total"))),
          h("tbody", {}, sheetWeek.totais.map((r) => h("tr", {}, h("td", {}, label(r.tipo)), h("td", {}, r.codigo || "Sem código"), h("td", { class: "num" }, hours(r.total))))))
          : h("p", { class: "vazio" }, "Sem horas que contam na ficha nesta semana."));
    },
  },
  ficha: {
    titulo: "Ficha",
    icone: "ficha",
    async render(estado) {
      const day = app.ficha || estado.hoje;
      const sheet = await api("/api/ficha?data=" + day);
      const confirmed = sheet.confirmada;
      const rows = sheet.linhas;
      const text = rows.map((r) => [r.rotulo, r.codigo || "", r.inicio || "", r.fim || "", hours(r.total), r.observacao].join("\t")).join("\n");
      return h("section", {},
        dayNav("ficha", day, 1, `${weekday(day)} ${fmtDate(day)}`),
        confirmed ? h("p", { class: "aviso" }, "Confirmada: ", confirmed.linhas.map((r) => `${label(r.tipo)} ${r.codigo || "sem código"} ${hours(r.total)}`).join(" · ")) : null,
        h("div", { class: "filtros" },
          h("span", {}, `Sugestão: ${hours(sheet.total)} de ${hours(sheet.horas_dia)}`),
          rows.length ? h("button", { class: "botao", type: "button", onclick: (e) => copy(text, e.target) }, "Copiar ficha") : null,
          app.editando && rows.length ? h("button", { class: "botao", type: "button", onclick: () => setSheetRow(sheet) },
            app.rascunho.ficha && app.rascunho.ficha.data === day ? "Confirmação no rascunho" : "Confirmar no salvamento") : null),
        rows.length ? h("table", {}, h("thead", {}, h("tr", {}, ["Tipo", "Código", "Início", "Fim", "Total", "Observação", ""].map((c, i) => h("th", { class: i === 4 ? "num" : null }, c)))),
          h("tbody", {}, rows.map((r) => h("tr", {},
            h("td", {}, r.rotulo), h("td", {}, r.codigo || "Sem código"), h("td", {}, r.inicio || ""), h("td", {}, r.fim || ""),
            h("td", { class: "num", title: `estimado ${hours(r.estimado)}` }, app.editando
              ? h("input", { class: "horas", type: "number", min: "0", max: "24", step: "0.25", value: sheetValue(day, r),
                  onchange: (e) => setSheetRow(sheet, r, e.target.value) }) : hours(r.total)),
            h("td", {}, r.observacao, r.complemento ? h("details", {}, h("summary", {}, "Complemento local"), h("pre", { class: "registro" }, r.complemento)) : null),
            h("td", {}, h("button", { class: "botao", type: "button", onclick: (e) => copy(r.observacao, e.target) }, "Copiar"))))))
          : h("p", { class: "vazio" }, "Nenhuma hora que conta na ficha neste dia."),
        h("h2", {}, "Extras (fora do total)"),
        sheet.extras.length ? h("table", {}, h("tbody", {}, sheet.extras.map((e) => h("tr", {},
          h("td", {}, h("button", { class: "link", type: "button", onclick: () => openTask(e.tarefa) }, e.titulo)), h("td", { class: "num" }, hours(e.horas))))))
          : h("p", { class: "vazio" }, "Nenhum extra."));
    },
  },
  historico: {
    titulo: "Histórico",
    icone: "historico",
    async render(estado) {
      const limit = app.historicoLimite || 200;
      const data = await api("/api/historico?limite=" + limit);
      const onlyPending = pref("historico.pendentes", "0") === "1";
      const origin = pref("historico.origem", "");
      const titles = Object.fromEntries(estado.tarefas.map((t) => [t.id, t.titulo]));
      const rows = data.eventos.filter((e) => (!onlyPending || e.pendente) && (!origin || e.origem === origin));
      return h("section", {},
        h("div", { class: "filtros" },
          h("span", {}, `${data.total} ações · ${data.pendentes} não analisadas`),
          h("label", {}, h("input", { type: "checkbox", checked: onlyPending, onchange: (e) => { setPref("historico.pendentes", e.target.checked ? "1" : "0"); render(); } }), " Só não analisadas"),
          h("label", {}, "Origem ", h("select", { onchange: (e) => { setPref("historico.origem", e.target.value); render(); } },
            [["", "Todas"], ["agente", "Agente"], ["quadro", "Quadro"]].map(([v, n]) => h("option", { value: v, selected: v === origin }, n))))),
        rows.length ? h("table", {}, h("thead", {}, h("tr", {}, ["Quando", "Origem", "Ação", "Tarefa", "Detalhe"].map((c) => h("th", {}, c)))),
          h("tbody", {}, rows.map((e) => h("tr", { class: e.pendente ? "pendente" : null },
            h("td", {}, when(e.ts)), h("td", {}, e.origem), h("td", {}, e.acao, e.pendente ? h("span", { class: "selo pergunta" }, "não analisada") : null),
            h("td", {}, e.tarefa ? h("button", { class: "link", type: "button", onclick: () => openTask(e.tarefa) }, titles[e.tarefa] || e.tarefa) : (e.coluna || "")),
            h("td", {}, eventDetail(e, titles))))))
          : h("p", { class: "vazio" }, "Nenhuma ação com esses filtros."),
        data.total > limit ? h("p", {}, h("button", { class: "botao", type: "button", onclick: () => { app.historicoLimite = limit + 200; render(); } }, "Carregar mais")) : null);
    },
  },
};
const ORDER = ["hoje", "quadro", "epicos", "prazos", "perguntas", "semana", "ficha", "historico"];

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
    h("button", { class: "botao", type: "button", disabled: !!SNAPSHOT, onclick: () => go(shiftDate(current, -step)) }, "←"),
    h("strong", {}, title),
    h("button", { class: "botao", type: "button", disabled: !!SNAPSHOT, onclick: () => go(shiftDate(current, step)) }, "→"),
    h("button", { class: "botao", type: "button", disabled: !!SNAPSHOT, onclick: () => go(app.estado.hoje) }, "Hoje"));
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
    const old = button.textContent;
    button.textContent = "Copiado";
    setTimeout(() => { button.textContent = old; }, 1500);
  } catch (error) {
    window.prompt("Copie o texto:", text);
  }
}

function currentView() {
  const name = location.hash.replace("#", "");
  return VIEWS[name] ? name : ORDER[0];
}

function renderTabs() {
  const nav = document.getElementById("abas");
  const current = currentView();
  const counts = { perguntas: app.estado.perguntas.length, prazos: app.estado.prazos.length, historico: app.estado.eventos_pendentes };
  fill(nav, ORDER.map((name) =>
    h("button", { type: "button", "aria-current": name === current ? "page" : null, onclick: () => { location.hash = name; } },
      icon(VIEWS[name].icone), VIEWS[name].titulo, counts[name] ? h("span", { class: "contador" }, counts[name]) : null)));
}

async function render() {
  if (!app.estado) return;
  renderTabs();
  const name = currentView();
  const main = document.getElementById("conteudo");
  main.classList.toggle("quadro-ativo", name === "quadro");
  const estado = effectiveState();
  fill(document.getElementById("opcoes"), VIEWS[name].opcoes ? VIEWS[name].opcoes(estado) : []);
  app.contagem = null;
  try {
    renderToolbar();
    const node = await VIEWS[name].render(estado);
    main.replaceChildren(node);
  } catch (error) {
    main.replaceChildren(h("p", { class: "aviso erro" }, error.message));
  }
  document.getElementById("contagem").textContent = app.contagem === null || app.contagem === undefined ? "" : String(app.contagem);
}

const THEMES = [["auto", "Tema: automático", "auto"], ["light", "Tema: claro", "sol"], ["dark", "Tema: escuro", "lua"]];

function renderTheme() {
  const current = pref("tema", "auto");
  const [, title, iconName] = THEMES.find((t) => t[0] === current) || THEMES[0];
  const button = document.getElementById("tema");
  button.title = title + " (clique para trocar)";
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
  try {
    app.estado = await api("/api/estado");
    app.cache = {};
    document.getElementById("maquina").textContent = (app.estado.maquina || "local") + (SNAPSHOT ? " · cópia estática" : "");
    const open = app.estado.tarefas.filter((t) => t.tipo !== "pergunta" && !["concluido", "arquivado"].includes(t.papel)).length;
    document.getElementById("resumo").textContent = `${open} itens abertos · ${app.estado.epicos.length} épicos · atualizado ${new Date().toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`;
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
  source.addEventListener("mudou", () => { if (!app.editando) refresh(); else { app.pendente = true; renderToolbar(); } });
  source.onerror = () => { dot.className = "ponto offline"; dot.title = "Servidor indisponível; tentando reconectar"; };
}

window.addEventListener("hashchange", render);
document.addEventListener("keydown", (event) => { if (event.key === "Escape") closePanel(); });
document.addEventListener("DOMContentLoaded", () => {
  renderTheme();
  document.getElementById("tema").addEventListener("click", cycleTheme);
  const filter = document.getElementById("filtro");
  filter.addEventListener("input", () => { app.busca = filter.value; clearTimeout(app.buscaTimer); app.buscaTimer = setTimeout(render, 150); });
  app.rascunho = loadDraft();
  app.editando = !SNAPSHOT && draftCount() > 0;
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
  try { localStorage.setItem("yabook.rascunho", JSON.stringify(app.rascunho)); } catch (error) { /* sem armazenamento: rascunho só na memória */ }
}

function draftCount() {
  const d = app.rascunho || emptyDraft();
  return Object.keys(d.tarefas).length + Object.keys(d.colunas).length + d.complementos.length + (d.ficha ? 1 : 0);
}

function effectiveState() {
  const estado = app.estado;
  if (!app.editando || !draftCount()) return estado;
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
  return { ...estado, tarefas, colunas };
}

function draftTask(id, campos, extra = {}) {
  const original = app.estado.tarefas.find((t) => t.id === id);
  const entry = app.rascunho.tarefas[id] || { revision: original.revision, campos: {}, unset: [] };
  Object.assign(entry.campos, campos);
  Object.assign(entry, extra);
  app.rascunho.tarefas[id] = entry;
  persistDraft();
}

function dropCard(event, columnId, cards) {
  event.preventDefault();
  const id = event.dataTransfer.getData("text/plain");
  if (!id) return;
  const target = event.currentTarget;
  const others = cards.filter((t) => t.id !== id);
  let position = others.length;
  [...target.querySelectorAll(".card")].filter((n) => n.dataset.id !== id).forEach((node, index) => {
    const box = node.getBoundingClientRect();
    if (position === others.length && event.clientY < box.top + box.height / 2) position = index;
  });
  const ordered = [...others.slice(0, position), { id }, ...others.slice(position)];
  ordered.forEach((task, index) => {
    const current = effectiveState().tarefas.find((t) => t.id === task.id);
    const campos = {};
    if (current.coluna !== columnId) campos.coluna = columnId;
    if ((current.ordem || 0) !== index + 1) campos.ordem = index + 1;
    if (Object.keys(campos).length) draftTask(task.id, campos);
  });
  render();
}

function renameColumn(column) {
  const name = window.prompt("Novo nome da coluna (o papel não muda):", column.nome);
  if (!name || !name.trim() || name.trim() === column.nome) return;
  app.rascunho.colunas[column.id] = name.trim();
  persistDraft();
  render();
}

function editForm(id) {
  const task = effectiveState().tarefas.find((t) => t.id === id);
  const original = app.estado.tarefas.find((t) => t.id === id);
  const parents = app.estado.tarefas.filter((t) => t.id !== id && ["epico", "historia"].includes(t.nivel));
  const marked = "pessoal_marcado" in task ? (task.pessoal_marcado ? "sim" : "nao") : "auto";
  const field = (name, labelText, input) => h("label", { class: "campo" }, h("span", {}, labelText), input);
  const form = h("form", { class: "formulario", onsubmit: (e) => {
    e.preventDefault();
    const values = Object.fromEntries(new FormData(e.target).entries());
    const campos = {};
    const compare = (key, value, before) => { if ((value ?? "") !== (before ?? "")) campos[key] = value === "" ? null : value; };
    compare("titulo", values.titulo.trim(), original.titulo);
    compare("coluna", values.coluna, original.coluna);
    compare("prazo", values.prazo, original.prazo);
    compare("proximo_passo", values.proximo_passo.trim(), original.proximo_passo);
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
  } },
    h("h2", { style: "margin:0" }, "Editar"),
    field("titulo", "Título", h("input", { name: "titulo", value: task.titulo, required: true })),
    field("coluna", "Coluna", h("select", { name: "coluna" }, effectiveState().colunas.map((c) => h("option", { value: c.id, selected: c.id === task.coluna }, c.nome)))),
    field("prazo", "Prazo", h("input", { name: "prazo", type: "date", value: task.prazo || "" })),
    field("proximo_passo", "Próximo passo", h("textarea", { name: "proximo_passo", rows: 2 }, task.proximo_passo || "")),
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

function setSheetRow(sheet, row, value) {
  const draft = app.rascunho.ficha && app.rascunho.ficha.data === sheet.data ? app.rascunho.ficha : {
    data: sheet.data,
    linhas: sheet.linhas.map((r) => ({ tipo: r.tipo, codigo: r.codigo, total: r.total })),
    extras: sheet.extras.map((e) => ({ tarefa: e.tarefa, horas: e.horas })),
  };
  if (row) {
    const target = draft.linhas.find((r) => r.tipo === row.tipo && String(r.codigo) === String(row.codigo));
    target.total = Math.max(0, Math.min(24, Number(String(value).replace(",", ".")) || 0));
  }
  app.rascunho.ficha = draft;
  persistDraft();
  render();
}

function renderToolbar() {
  const bar = document.getElementById("edicao");
  if (SNAPSHOT || !TOKEN) { bar.replaceChildren(); return; }
  const count = draftCount();
  const items = app.editando ? [
    app.pendente ? h("span", { class: "selo prazo", title: "Salve ou descarte para ver as mudanças" }, "repositório mudou") : null,
    h("span", { class: "vazio", style: "font-size:12px" }, count ? `${count} alteração(ões)` : "Modo edição"),
    h("button", { class: "botao", type: "button", onclick: discardDraft }, count ? "Descartar" : "Sair"),
    h("button", { class: "botao primario", type: "button", disabled: !count, onclick: saveDraft }, "Salvar"),
  ] : [h("button", { class: "botao", type: "button", onclick: () => { app.editando = true; render(); } }, "Editar")];
  bar.replaceChildren(...items.filter(Boolean));
}

function discardDraft() {
  if (draftCount() && !window.confirm("Descartar as alterações não salvas?")) return;
  app.rascunho = emptyDraft();
  persistDraft();
  app.editando = false;
  app.pendente = false;
  refresh();
}

async function saveDraft() {
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
    return showPanel(h("p", { class: "aviso erro" }, "Servidor indisponível; o rascunho continua guardado. " + error.message));
  }
  if (response.ok) {
    app.rascunho = emptyDraft();
    persistDraft();
    app.editando = false;
    app.pendente = false;
    await refresh();
    return showPanel(
      h("h2", {}, "Salvo"),
      result.aviso ? h("p", { class: "aviso erro" }, result.aviso) : null,
      h("pre", { class: "registro" }, result.resumo),
      h("button", { class: "botao primario", type: "button", onclick: (e) => copy(result.resumo, e.target) }, "Copiar resumo"));
  }
  if (response.status === 409) {
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
  panel.hidden = false;
  const [first, ...rest] = children.flat(Infinity).filter(Boolean);
  const title = first && first.tagName === "H2" ? first.textContent : "YABook Tasks";
  fill(panel,
    h("div", { class: "painel-topo" }, h("h2", {}, title),
      h("button", { class: "botao-icone discreto", type: "button", title: "Fechar", onclick: closePanel }, icon("fechar"))),
    h("div", { class: "painel-corpo" }, first && first.tagName === "H2" ? rest : [first, ...rest]));
}
