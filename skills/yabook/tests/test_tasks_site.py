"""Regressões do calendário e dos ícones compartilhados, executadas no JS real."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path


SITE = Path(__file__).resolve().parents[1] / "scripts/tasks_runtime/site/app.js"


@unittest.skipUnless(shutil.which("node"), "Node.js necessário para validar o site")
class TasksSiteTest(unittest.TestCase):
    def evaluate(self, expression, tasks):
        script = r'''
const fs = require("node:fs"), vm = require("node:vm");
const [site, expression, tasks] = process.argv.slice(1);
const context = vm.createContext({
  window: { addEventListener() {} },
  document: {
    querySelector() { return null; }, addEventListener() {},
    createElement() { return { style: {}, setAttribute(key, value) { this[key] = value; } }; },
  },
});
vm.runInContext(fs.readFileSync(site, "utf8"), context);
vm.runInContext(`app.estado = { colunas: [{id: "andamento", nome: "Em andamento"}] };`, context);
context.tasks = JSON.parse(tasks);
process.stdout.write(JSON.stringify(vm.runInContext(expression, context)));
'''
        result = subprocess.run(["node", "-e", script, str(SITE), expression, json.dumps(tasks)],
                                check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_recorded_time_preserves_fractional_minutes_from_concurrent_windows(self):
        self.assertEqual(self.evaluate("[.125, .375, 1.125, 0, null].map(recordedTime)", []),
                         ["7min 30s", "22min 30s", "1h 07min 30s", "0min", "—"])
        # Resumo arredonda ao minuto com minutos em dois dígitos: "4h 45min", "1h 02min", "45min".
        self.assertEqual(self.evaluate("[4.75, 1.0375, .75, 0].map(summaryTime)", []),
                         ["4h 45min", "1h 02min", "45min", "0min"])

    def test_grouped_navigation_keeps_legacy_routes_and_shortcut_order(self):
        self.assertEqual(self.evaluate("ORDER", []),
                         ["hoje", "quadro", "epicos", "prazos", "perguntas", "semana", "ficha", "historico"])
        for route, title in [("ficha", "Ficha de horas"), ("historico", "Registro de alterações"),
                             ("prazos", "Calendário"), ("rota-antiga-invalida", "Visão geral")]:
            with self.subTest(route=route):
                expression = 'globalThis.location = {hash: ' + json.dumps("#" + route) + '}; VIEWS[currentView()].titulo'
                self.assertEqual(self.evaluate(expression, []), title)

    def task(self, identifier, prazo=None, pai=None, **fields):
        return dict(id=identifier, titulo=identifier, tipo="issue", papel="ativo", coluna="andamento",
                    prazo=prazo, pai=pai, **fields)

    def deadlines(self, *tasks):
        return self.evaluate("deadlineTasks(tasks).map(t => t.id)", tasks)

    def test_card_demand_prefers_own_then_nearest_parent(self):
        tasks = [
            self.task("avo", demanda="320100"),
            self.task("pai", pai="avo", demanda="320200"),
            self.task("filho", pai="pai", demanda="320300"),
            self.task("herdada", pai="pai"),
            self.task("apenas-projeto", projeto="5723"),
            self.task("ciclo", pai="ciclo"),
        ]
        self.assertEqual(self.evaluate("tasks.map(task => cardDemand(task, tasks))", tasks),
                         ["320100", "320200", "320300", "320200", None, None])

    def test_sheet_code_opens_owner_instead_of_child_with_inherited_code(self):
        tasks = [dict(id="epico", tipo="projeto", projeto="1001"),
                 dict(id="historia", tipo="issue", pai="epico", projeto="1001", demanda="2001"),
                 dict(id="filho", tipo="tarefa", pai="historia", projeto="1001", demanda="2001")]
        for kind, code, owner in [("demanda", "2001", "historia"), ("projeto", "1001", "epico")]:
            with self.subTest(kind=kind):
                row = dict(tipo=kind, codigo=code, tarefas=["filho"])
                self.assertEqual(self.evaluate(f"sheetTask({json.dumps(row)}, tasks)?.id", tasks), owner)

    def test_sheet_project_groups_several_children_under_one_card(self):
        tasks = [dict(id="epico", tipo="projeto", projeto="1001"),
                 dict(id="a", tipo="issue", pai="epico", projeto="1001"),
                 dict(id="b", tipo="issue", pai="epico", projeto="1001")]
        self.assertEqual(self.evaluate('sheetTask({tipo:"projeto", codigo:"1001", tarefas:["a","b"]}, tasks)?.id', tasks), "epico")

    def test_sheet_matches_type_and_code_without_guessing_ambiguous_cards(self):
        tasks = [dict(id="projeto", tipo="projeto", projeto="1001"),
                 dict(id="demanda", tipo="demanda", demanda="1001")]
        self.assertEqual(self.evaluate('sheetTask({tipo:"demanda", codigo:"1001"}, tasks)?.id', tasks), "demanda")
        tasks.append(dict(id="outra", tipo="demanda", demanda="1001"))
        self.assertIsNone(self.evaluate('sheetTask({tipo:"demanda", codigo:"1001"}, tasks)', tasks))
        self.assertEqual(self.evaluate('sheetTask({tipo:"demanda", codigo:"1001", tarefas:["demanda"]}, tasks)?.id', tasks), "demanda")

    def test_sheet_without_code_or_available_card_stays_text(self):
        for row in [dict(tipo="trabalho", codigo=""), dict(tipo="demanda", codigo="9999", tarefas=["apagada"])]:
            with self.subTest(row=row):
                self.assertIsNone(self.evaluate(f"sheetTask({json.dumps(row)}, tasks)", []))

    def test_sheet_specification_opens_its_card_with_own_or_inherited_code(self):
        for field in ["demanda", "projeto", "codigo"]:
            with self.subTest(field=field):
                tasks = [dict(id="spec", tipo="especificacao", **{field: "3001"}),
                         dict(id="outro", tipo="demanda", demanda="3001")]
                self.assertEqual(self.evaluate('sheetTask({tipo:"especificacao",codigo:"3001",tarefas:["spec"]}, tasks)?.id', tasks), "spec")

    def test_sheet_only_copies_nonempty_observations(self):
        script = r'''
const fs = require("node:fs"), vm = require("node:vm");
class Element {
  constructor(tag, text = "") { this.tag = tag; this.text = text; this.childNodes = []; this.events = {}; this.style = {}; }
  setAttribute(k, v) { this[k] = v; }
  addEventListener(k, v) { this.events[k] = v; }
  append(n) { this.childNodes.push(n); }
  replaceChildren(...n) { this.childNodes = n.flat(); }
  get textContent() { return this.text + this.childNodes.map(n => n.textContent).join(""); }
}
const sheet = {data:"2026-11-11", total:8, horas_dia:8, extras:[], janelas:[], confirmada:{linhas:[]},
  linhas:[{tipo:"demanda", rotulo:"Demanda", codigo:"1001", total:8, estimado:.25, capturado:.25, informado:0, registrado:.25, observacao:""}]};
let copied = "";
const ctx = vm.createContext({Node:Element, window:{addEventListener(){}},
  document:{querySelector(){return null;}, addEventListener(){}, createElement(t){return new Element(t);},
    createTextNode(t){return new Element("text", t);}},
  fetch:async()=>({ok:true,json:async()=>sheet}), navigator:{clipboard:{writeText:async t=>{copied=t;}}},
  setTimeout(){}, console});
vm.runInContext(fs.readFileSync(process.argv[1],"utf8"),ctx);
vm.runInContext('app.estado={hoje:"2026-11-11"}; app.rascunho=emptyDraft(); app.editando=false;',ctx);
(async()=>{
  const view = vm.runInContext("VIEWS.ficha",ctx);
  const flatten = n => [n, ...n.childNodes.flatMap(flatten)];
  const full = flatten(await view.render({hoje:sheet.data}));
  const absent = full.filter(n=>n.tag==="button" && n.textContent.includes("Copiar"));
  sheet.linhas[0].observacao="   ";
  const whitespace = flatten(await view.render({hoje:sheet.data})).filter(n=>n.tag==="button" && n.textContent.includes("Copiar"));
  sheet.linhas[0].observacao="Desenvolvimento: ajustar relatório.";
  const observed = flatten(await view.render({hoje:sheet.data}));
  const button = observed.find(n=>n.tag==="button" && n.textContent==="Copiar observação");
  await button.events.click({currentTarget:button});
  sheet.janelas=[{janela:"08:00",tarefa:"demanda-1001",titulo:"Demanda",ignorar:false}];
  vm.runInContext('app.editando=true; render=()=>{};',ctx);
  const editing = flatten(await view.render({hoje:sheet.data}));
  const toggle = editing.find(n=>n.tag==="button" && n.textContent.includes("Desconsiderar"));
  toggle.events.click({currentTarget:toggle});
  const draft = vm.runInContext("app.rascunho.correcoes",ctx);
  sheet.linhas=[]; sheet.total=0;
  const empty = flatten(await view.render({hoje:sheet.data}));
  process.stdout.write(JSON.stringify({copied, absent:absent.length, whitespace:whitespace.length, fullCopy:full.some(n=>n.tag==="button" && /Copiar ficha|Copiar rateio/.test(n.textContent)), draft, confirmationShown:full.some(n=>n.textContent.includes("Confirmada:")), emptyCopy:empty.some(n=>n.tag==="button" && n.textContent.includes("Copiar ficha")),
    emptyText:empty.some(n=>n.textContent.includes("Nenhuma hora que conta"))}));
})().catch(e=>{console.error(e);process.exit(1)});
'''
        result = subprocess.run(["node", "-e", script, str(SITE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = json.loads(result.stdout)
        self.assertEqual(actual["copied"], "Desenvolvimento: ajustar relatório.")
        self.assertEqual(actual["absent"], 0)
        self.assertEqual(actual["whitespace"], 0)
        self.assertFalse(actual["fullCopy"])
        self.assertFalse(actual["confirmationShown"])
        self.assertEqual(actual["draft"], [dict(data="2026-11-11", janela="08:00", tarefa="demanda-1001", ignorar=True)])
        self.assertFalse(actual["emptyCopy"])
        self.assertTrue(actual["emptyText"])

    def test_card_shows_demand_among_badges_like_parent(self):
        script = r'''
const fs = require("node:fs"), vm = require("node:vm");
class Element {
  constructor(tag, text = "") { this.tag = tag; this.text = text; this.childNodes = []; this.events = {}; this.style = {}; }
  setAttribute(k, v) { this[k] = v; }
  addEventListener(k, v) { this.events[k] = v; }
  append(n) { this.childNodes.push(n); }
  get textContent() { return this.text + this.childNodes.map(n => n.textContent).join(""); }
}
const ctx = vm.createContext({Node:Element, window:{addEventListener(){}},
  document:{querySelector(){return null;}, querySelectorAll(){return [];}, addEventListener(){},
    createElement(t){return new Element(t);}, createTextNode(t){return new Element("text", t);}}});
vm.runInContext(fs.readFileSync(process.argv[1],"utf8"),ctx);
const tasks = JSON.parse(process.argv[2]);
ctx.tasks = tasks;
vm.runInContext('app.estado={hoje:"2026-11-19", colunas:[{id:"andamento", nome:"Em andamento"}], tarefas:tasks}; app.rascunho=emptyDraft(); app.editando=false;',ctx);
const find = (node, cls, out = []) => { if ((node.className || "").split(" ").includes(cls)) out.push(node); (node.childNodes || []).forEach(n => find(n, cls, out)); return out; };
const result = {};
for (const task of tasks) {
  const card = vm.runInContext(`card(tasks.find(t => t.id === ${JSON.stringify(task.id)}))`, ctx);
  const badges = find(card, "card-selos")[0];
  result[task.id] = {selo: badges ? find(badges, "card-demanda").map(n => [n.tag, n.textContent]) : [],
    rodape: find(find(card, "card-rodape")[0], "card-demanda").length};
}
process.stdout.write(JSON.stringify(result));
'''
        tasks = [
            dict(id="chamado", titulo="Chamado", tipo="demanda", papel="ativo", coluna="andamento", demanda="322628", codigo="322628", nivel="historia"),
            dict(id="issue", titulo="Issue", tipo="issue", papel="ativo", coluna="andamento", pai="chamado", issue=["dono/repo#7"]),
            dict(id="propria", titulo="Própria", tipo="issue", papel="ativo", coluna="andamento", demanda="1001", issue=["dono/repo#8"]),
            dict(id="solta", titulo="Solta", tipo="issue", papel="ativo", coluna="andamento", pai="neta", issue=["dono/repo#9"]),
            dict(id="neta", titulo="Neta", tipo="tarefa", papel="ativo", coluna="andamento", pai="chamado", numero=4),
        ]
        result = subprocess.run(["node", "-e", script, str(SITE), json.dumps(tasks)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = json.loads(result.stdout)
        # O selo do pai já mostra 322628: sem duplicar.
        self.assertEqual(actual["issue"]["selo"], [])
        self.assertEqual(actual["propria"]["selo"], [["span", "Demanda 1001"]])
        # Herdada do avô: selo clicável que abre a tarefa dona da demanda.
        self.assertEqual(actual["solta"]["selo"], [["button", "Demanda 322628"]])
        self.assertTrue(all(item["rodape"] == 0 for item in actual.values()))

    def test_attachment_preview_kinds_csv_and_text_decoding(self):
        script = r'''
const fs = require("node:fs"), vm = require("node:vm");
class Element {
  constructor(tag, text = "") { this.tag = tag; this.text = text; this.childNodes = []; this.events = {}; this.style = {}; this.classList = {toggle(){}}; }
  setAttribute(k, v) { this[k] = v; }
  addEventListener(k, v) { this.events[k] = v; }
  append(n) { this.childNodes.push(n); }
  get textContent() { return this.text + this.childNodes.map(n => n.textContent).join(""); }
}
const ctx = vm.createContext({Node:Element, TextDecoder, TextEncoder, window:{addEventListener(){}},
  document:{querySelector(){return null;}, addEventListener(){}, createElement(t){return new Element(t);}, createTextNode(t){return new Element("text", t);}}});
vm.runInContext(fs.readFileSync(process.argv[1],"utf8"),ctx);
const run = (code) => vm.runInContext(code, ctx);
const flat = (n) => [n, ...(n.childNodes || []).flatMap(flat)];
const nodes = (value) => [value].flat().filter(Boolean).flatMap(flat);
const csv = run('previewContent("csv", new TextEncoder().encode(\'nome;valor\\n"Silva; Ana";"1,5"\\n"linha\\nquebrada";2\\n\'), null, "a.csv")');
const markdown = run('previewContent("markdown", new TextEncoder().encode("# Título\\n\\n- item"), null, "a.md")');
const json = run('previewContent("json", new TextEncoder().encode(\'{"a":[1,2]}\'), null, "a.json")');
process.stdout.write(JSON.stringify({
  kinds: run('["a.PDF","b.jpeg","c.webp","d.md","e.txt","f.log","g.json","h.csv","i.docx","j"].map(previewKind)'),
  delimiters: run('[parseCsv("a,b\\n1,2").delimiter, parseCsv("a\\tb").delimiter, parseCsv("a;b").delimiter]'),
  cells: nodes(csv).filter(n => n.tag === "td" || n.tag === "th").map(n => n.textContent),
  utf8: run('decodeText(new Uint8Array([0xEF,0xBB,0xBF,0x61,0xC3,0xA7,0xC3,0xA3,0x6F]))'),
  latin: run('decodeText(new Uint8Array([0x61,0xE7,0xE3,0x6F]))'),
  markdown: nodes(markdown).map(n => n.tag).filter(t => ["button","h1","h2","h3","li","pre"].includes(t)),
  json: nodes(json).find(n => n.tag === "pre").textContent,
  bytes: run('[512, 2048, 1500000].map(formatBytes)'),
}));
'''
        result = subprocess.run(["node", "-e", script, str(SITE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = json.loads(result.stdout)
        self.assertEqual(actual["kinds"], ["pdf", "imagem", "imagem", "markdown", "texto", "texto", "json", "csv", None, None])
        self.assertEqual(actual["delimiters"], [",", "\t", ";"])
        self.assertEqual(actual["cells"], ["nome", "valor", "Silva; Ana", "1,5", "linha\nquebrada", "2"])
        self.assertEqual((actual["utf8"], actual["latin"]), ("ação", "ação"))
        self.assertEqual(actual["markdown"][0], "button")
        self.assertIn("li", actual["markdown"])
        self.assertIn("pre", actual["markdown"])
        self.assertEqual(actual["json"], '{\n  "a": [\n    1,\n    2\n  ]\n}')
        self.assertEqual(actual["bytes"], ["512 B", "2,0 KB", "1,4 MB"])

    def test_same_date_only_shows_parent(self):
        self.assertEqual(self.deadlines(self.task("epico", "2026-12-18"),
                                        self.task("historia", "2026-12-18", "epico")), ["epico"])

    def test_distinct_dates_and_unrelated_items_are_kept_and_sorted(self):
        self.assertEqual(self.deadlines(self.task("epico", "2026-12-18"),
                                        self.task("historia", "2026-12-10", "epico"),
                                        self.task("outro", "2026-12-18")), ["historia", "epico", "outro"])

    def test_child_without_date_does_not_duplicate_parent(self):
        self.assertEqual(self.deadlines(self.task("epico", "2026-12-18"),
                                        self.task("historia", pai="epico")), ["epico"])

    def test_three_levels_consolidate_and_keep_nearest_distinct_deadline(self):
        epic = self.task("epico", "2026-12-18")
        story = self.task("historia", "2026-12-18", "epico")
        task = self.task("tarefa", "2026-12-18", "historia")
        self.assertEqual(self.deadlines(epic, story, task), ["epico"])
        story["prazo"] = "2026-12-10"
        self.assertEqual(self.deadlines(epic, story, task), ["historia", "epico", "tarefa"])
        story["prazo"] = None
        self.assertEqual(self.deadlines(epic, story, task), ["epico"])

    def test_closed_or_missing_parent_does_not_hide_child(self):
        child = self.task("historia", "2026-12-18", "epico")
        for role in ("concluido", "arquivado"):
            with self.subTest(role=role):
                parent = self.task("epico", "2026-12-18")
                parent["papel"] = role
                self.assertEqual(self.deadlines(parent, child), ["historia"])
        self.assertEqual(self.deadlines(child), ["historia"])

    def test_filter_preserves_matching_child_when_parent_is_not_visible(self):
        tasks = [self.task("epico", "2026-12-18"), self.task("historia", "2026-12-18", "epico")]
        self.assertEqual(self.evaluate('app.busca = "historia"; deadlineTasks(filtered(tasks)).map(t => t.id)', tasks),
                         ["historia"])

    def test_levels_have_distinct_accessible_icons_even_when_closed(self):
        tasks = [self.task(level, nivel=level) for level in ("epico", "historia", "tarefa")]
        result = self.evaluate('tasks.map(t => { const n = stateIcon(t); return [n.innerHTML, n["aria-label"], n.role]; })', tasks)
        self.assertEqual(len({item[0] for item in result}), 3)
        self.assertEqual([item[1] for item in result], ["Épico · Em andamento", "História · Em andamento", "Tarefa · Em andamento"])
        self.assertTrue(all(item[2] == "img" for item in result))
        tasks[0]["papel"] = "concluido"
        self.assertEqual(self.evaluate('stateIcon(tasks[0]).innerHTML', tasks), result[0][0])
        self.assertIn("estado-fechado", self.evaluate('stateIcon(tasks[0]).className', tasks))

    def test_questions_keep_their_own_icon_and_legacy_tasks_get_a_task_icon(self):
        tasks = [dict(tipo="pergunta"), self.task("legada")]
        self.assertEqual(self.evaluate('stateIcon(tasks[0]).className', tasks), "icone estado-pergunta")
        self.assertEqual(self.evaluate('stateIcon(tasks[1])["aria-label"]', tasks), "Tarefa · Em andamento")


if __name__ == "__main__":
    unittest.main()
