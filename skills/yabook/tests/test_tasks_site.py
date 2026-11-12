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
