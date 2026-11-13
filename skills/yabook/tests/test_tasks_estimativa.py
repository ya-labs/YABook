import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import estimate
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class EstimateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))

    def tearDown(self):
        self.tmp.cleanup()

    def windows(self, task, count, day="2026-11-10"):
        lines = [json.dumps(dict(tipo="janela", data=day, janela="%02d:%02d" % (8 + i // 4, 15 * (i % 4)), tarefa=task))
                 for i in range(count)]
        with (self.root / "horas" / "2026-11-trabalho.jsonl").open("a", encoding="utf-8") as handle:
            handle.write("\n".join(lines) + "\n")

    def test_groups_concluded_tasks_and_points_outliers(self):
        self.tasks.add("tarefa", "Rápida", coluna="concluido", size=1)
        self.tasks.add("tarefa", "Subestimada", coluna="concluido", size=1)
        self.tasks.add("tarefa", "Aberta", coluna="andamento", size=1)
        self.tasks.add("tarefa", "Épico", coluna="concluido", size=5, nivel="epico")
        self.windows("tarefa-rapida", 4)  # 1 h
        self.windows("tarefa-subestimada", 12, "2026-11-11")  # 3 h -> size 2
        self.windows("tarefa-aberta", 40)
        self.windows("tarefa-epico", 40)
        result = estimate.compare(self.store)
        self.assertEqual(result["tarefas"], 2)
        one = result["por_size"][0]
        self.assertEqual((one["quantidade"], one["minimo"], one["maximo"]), (2, 1.0, 3.0))
        self.assertEqual([(r["id"], r["size_pelas_horas"]) for r in result["fora_da_faixa"]], [("tarefa-subestimada", 2)])

    def test_story_sums_its_tasks(self):
        self.tasks.add("tarefa", "História", coluna="concluido", size=3, nivel="historia")
        self.tasks.add("tarefa", "Filha", coluna="concluido", pai="tarefa-historia")
        self.windows("tarefa-historia", 8)
        self.windows("tarefa-filha", 16, "2026-11-12")
        row = estimate.compare(self.store)["por_size"][2]
        self.assertEqual((row["quantidade"], row["mediana"]), (1, 6.0))
        self.assertEqual(estimate.size_for(30.5), 5)


if __name__ == "__main__":
    unittest.main()
