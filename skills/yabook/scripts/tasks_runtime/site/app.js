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
function label(tipo) {
  return (app.estado.rotulos || {})[tipo] || tipo;
}

function columnName(id) {
  const column = app.estado.colunas.find((c) => c.id === id);
  return column ? column.nome : id;
}

function badges(task, options = {}) {
  const items = [];
  if (task.nivel && !options.semNivel) items.push(h("span", { class: "selo nivel" }, task.nivel === "epico" ? "épico" : task.nivel === "historia" ? "história" : "tarefa"));
  if (task.codigo) items.push(h("span", { class: "selo", title: "Código" }, task.codigo));
  if (task.pessoal && !options.semPessoal) items.push(h("span", { class: "selo pessoal", title: "Sem numeração da empresa" }, "pessoal"));
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
  const editable = app.editando && task.tipo !== "pergunta";
  return h("button", { class: "card" + (task.editado ? " editado" : ""), type: "button", "data-id": task.id,
    draggable: editable ? "true" : null, ondragstart: editable ? (e) => { e.dataTransfer.setData("text/plain", task.id); e.dataTransfer.effectAllowed = "move"; } : null,
    onclick: () => openTask(task.id) },
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
    fill(panel,
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
      app.editando && data.tipo !== "pergunta" ? editForm(id) : null,
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

function section(title, nodes, empty) {
  return [h("h2", {}, title), nodes.length ? h("div", { class: "grade" }, nodes) : h("p", { class: "vazio" }, empty)];
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
    render(estado) {
      const tasks = work(estado);
      const active = estado.ativa ? tasks.find((t) => t.id === estado.ativa.id) : null;
      const doing = tasks.filter((t) => t.papel === "ativo" && (!active || t.id !== active.id)).sort(byOrder);
      const testing = tasks.filter((t) => t.papel === "validacao").sort(byOrder);
      const late = estado.prazos.filter((t) => daysUntil(t.prazo) < 0).length;
      return h("section", {},
        h("div", { class: "numeros" },
          [["Em andamento", tasks.filter((t) => t.papel === "ativo").length], ["Em validação", testing.length],
           ["Prazos próximos", estado.prazos.length], ["Atrasadas", late], ["Perguntas", estado.perguntas.length],
           ["Ações não analisadas", estado.eventos_pendentes]]
            .map(([name, total]) => h("div", { class: "numero" }, h("b", {}, total), h("span", {}, name)))),
        h("h2", {}, "Tarefa ativa"),
        active ? h("div", { class: "grade" }, card(active)) : h("p", { class: "vazio" }, "Nenhuma tarefa ativa nesta máquina."),
        section("Em andamento", doing.map(card), "Nada em andamento."),
        section("Prazos", estado.prazos.map((t) => card(estado.tarefas.find((x) => x.id === t.id) || t)), "Nenhum prazo atrasado ou nos próximos 2 dias."),
        section("Perguntas para você", estado.perguntas.map((t) => card(estado.tarefas.find((x) => x.id === t.id) || t)), "Nenhuma pergunta aberta."),
        section("Em validação", testing.map(card), "Nada em validação."),
      );
    },
  },
  quadro: {
    titulo: "Quadro",
    render(estado) {
      const map = Object.fromEntries(estado.tarefas.map((t) => [t.id, t]));
      const epicFilter = pref("quadro.epico", "");
      const levelFilter = pref("quadro.nivel", "");
      const showArchived = pref("quadro.arquivadas", "0") === "1";
      const text = (app.busca || "").toLowerCase();
      const visible = work(estado).filter((t) =>
        (!epicFilter || (epicFilter === "-" ? !epicOf(t, map) : epicOf(t, map) === epicFilter)) &&
        (!levelFilter || (levelFilter === "-" ? !t.nivel : t.nivel === levelFilter)) &&
        (!text || [t.titulo, t.codigo, t.id, t.proximo_passo].join(" ").toLowerCase().includes(text)));
      const columns = estado.colunas.filter((c) => showArchived || c.papel !== "arquivado");
      const filters = h("div", { class: "filtros" },
        h("label", {}, "Épico ", h("select", { onchange: (e) => { setPref("quadro.epico", e.target.value); render(); } },
          h("option", { value: "" }, "Todos"), h("option", { value: "-", selected: epicFilter === "-" }, "Sem épico"),
          estado.epicos.map((e) => h("option", { value: e.id, selected: e.id === epicFilter }, e.titulo)))),
        h("label", {}, "Nível ", h("select", { onchange: (e) => { setPref("quadro.nivel", e.target.value); render(); } },
          [["", "Todos"], ["epico", "Épicos"], ["historia", "Histórias"], ["tarefa", "Tarefas"], ["-", "Sem nível"]]
            .map(([v, n]) => h("option", { value: v, selected: v === levelFilter }, n)))),
        h("input", { type: "search", placeholder: "Buscar", value: app.busca || "", oninput: (e) => { app.busca = e.target.value; clearTimeout(app.buscaTimer); app.buscaTimer = setTimeout(render, 200); } }),
        h("label", {}, h("input", { type: "checkbox", checked: showArchived, onchange: (e) => { setPref("quadro.arquivadas", e.target.checked ? "1" : "0"); render(); } }), " Arquivadas"));
      return h("section", {}, filters,
        h("div", { class: "quadro" }, columns.map((column) => {
          const cards = visible.filter((t) => t.coluna === column.id).sort(byOrder);
          return h("div", { class: "coluna", "data-coluna": column.id,
            ondragover: app.editando ? (e) => { e.preventDefault(); e.dataTransfer.dropEffect = "move"; } : null,
            ondrop: app.editando ? (e) => dropCard(e, column.id, cards) : null },
            h("header", {}, h("span", {}, column.nome,
              app.editando ? h("button", { class: "link", type: "button", title: "Renomear coluna", onclick: () => renameColumn(column) }, " ✎") : null),
              h("span", {}, cards.length)), cards.map(card));
        })));
    },
  },
  epicos: {
    titulo: "Épicos",
    render(estado) {
      const tasks = work(estado);
      const children = (id) => tasks.filter((t) => t.pai === id)
        .sort((a, b) => ROLE_ORDER.indexOf(a.papel) - ROLE_ORDER.indexOf(b.papel) || byOrder(a, b));
      const loose = tasks.filter((t) => !t.pai && t.nivel !== "epico" && !CLOSED.includes(t.papel)).sort(byOrder);
      return h("section", {},
        estado.epicos.length ? estado.epicos.map((epic) => {
          const full = tasks.find((t) => t.id === epic.id) || epic;
          return h("article", { class: "bloco epico" },
            h("header", { class: "epico-topo" },
              h("button", { class: "link", type: "button", onclick: () => openTask(epic.id) }, h("strong", {}, epic.titulo)),
              h("span", { class: "linha" }, badges(full), h("span", { class: "selo" }, columnName(epic.coluna)))),
            progress(epic),
            epic.proximo_passo ? h("p", { class: "passo" }, "→ " + epic.proximo_passo) : null,
            h("ul", { class: "historias" }, children(epic.id).map((story) => h("li", {},
              h("button", { class: "link", type: "button", onclick: () => openTask(story.id) }, story.titulo),
              h("span", { class: "linha" }, h("span", { class: "selo" }, columnName(story.coluna)), badges(story, { semNivel: true, semPessoal: full.pessoal })),
              children(story.id).length ? h("ul", {}, children(story.id).map((sub) => h("li", {},
                h("button", { class: "link", type: "button", onclick: () => openTask(sub.id) }, sub.titulo),
                h("span", { class: "selo" }, columnName(sub.coluna))))) : null))));
        }) : h("p", { class: "vazio" }, "Nenhum épico. Use --nivel epico ou task capture."),
        loose.length ? [h("h2", {}, "Sem épico"), h("div", { class: "grade" }, loose.map(card))] : null);
    },
  },
  prazos: {
    titulo: "Prazos",
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
  nav.replaceChildren(...ORDER.map((name) =>
    h("button", { type: "button", "aria-current": name === current ? "page" : null, onclick: () => { location.hash = name; } }, VIEWS[name].titulo)));
}

async function render() {
  if (!app.estado) return;
  renderTabs();
  const main = document.getElementById("conteudo");
  try {
    renderToolbar();
    const node = await VIEWS[currentView()].render(effectiveState());
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
  source.addEventListener("mudou", () => { if (!app.editando) refresh(); else { app.pendente = true; renderToolbar(); } });
  source.onerror = () => { dot.className = "ponto offline"; dot.title = "Servidor indisponível; tentando reconectar"; };
}

window.addEventListener("hashchange", render);
document.addEventListener("keydown", (event) => { if (event.key === "Escape") closePanel(); });
document.addEventListener("DOMContentLoaded", () => {
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
    h("h2", {}, "Editar"),
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
  let bar = document.getElementById("edicao");
  if (!bar) {
    bar = h("div", { id: "edicao", class: "edicao" });
    document.querySelector(".situacao").prepend(bar);
  }
  if (SNAPSHOT || !TOKEN) { bar.replaceChildren(); return; }
  const count = draftCount();
  const items = app.editando ? [
    app.pendente ? h("span", { class: "selo prazo", title: "Salve ou descarte para ver as mudanças" }, "repositório mudou") : null,
    h("span", {}, count ? `${count} alteração(ões)` : "Modo edição"),
    h("button", { class: "botao primario", type: "button", disabled: !count, onclick: saveDraft }, "Salvar"),
    h("button", { class: "botao", type: "button", onclick: discardDraft }, count ? "Descartar" : "Sair"),
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
  fill(panel, h("button", { class: "botao fechar", type: "button", onclick: closePanel }, "Fechar"), ...children);
}
