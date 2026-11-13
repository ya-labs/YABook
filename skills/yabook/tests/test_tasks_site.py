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

    def task(self, identifier, prazo=None, pai=None, **fields):
        return dict(id=identifier, titulo=identifier, tipo="issue", papel="ativo", coluna="andamento",
                    prazo=prazo, pai=pai, **fields)

    def deadlines(self, *tasks):
        return self.evaluate("deadlineTasks(tasks).map(t => t.id)", tasks)

    def test_sheet_copies_only_current_suggestion_and_hides_copy_when_empty(self):
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
const sheet = {data:"2026-11-11", total:8, horas_dia:8, extras:[], janelas:[], confirmada:null,
  linhas:[{tipo:"demanda", rotulo:"Demanda", codigo:"1001", total:8, estimado:.25, observacao:""}]};
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
  const button = full.find(n=>n.tag==="button" && n.textContent.includes("Copiar ficha"));
  await button.events.click({currentTarget:button});
  sheet.janelas=[{janela:"08:00",tarefa:"demanda-1001",titulo:"Demanda",ignorar:false}];
  vm.runInContext('app.editando=true; render=()=>{};',ctx);
  const editing = flatten(await view.render({hoje:sheet.data}));
  const toggle = editing.find(n=>n.tag==="button" && n.textContent.includes("Desconsiderar"));
  toggle.events.click({currentTarget:toggle});
  const draft = vm.runInContext("app.rascunho.correcoes",ctx);
  sheet.linhas=[]; sheet.total=0;
  const empty = flatten(await view.render({hoje:sheet.data}));
  process.stdout.write(JSON.stringify({copied, draft, emptyCopy:empty.some(n=>n.tag==="button" && n.textContent.includes("Copiar ficha")),
    emptyText:empty.some(n=>n.textContent.includes("Nenhuma hora que conta"))}));
})().catch(e=>{console.error(e);process.exit(1)});
'''
        result = subprocess.run(["node", "-e", script, str(SITE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        actual = json.loads(result.stdout)
        self.assertIn("1001", actual["copied"])
        self.assertEqual(actual["draft"], [dict(data="2026-11-11", janela="08:00", tarefa="demanda-1001", ignorar=True)])
        self.assertFalse(actual["emptyCopy"])
        self.assertTrue(actual["emptyText"])

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
