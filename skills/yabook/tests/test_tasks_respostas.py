import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import capture
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class AnswerCandidatesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))
        self.open = self.tasks.add("pergunta", "Onde se cadastra o limite por filial na tabela facliuni?")["id"]
        answered = self.tasks.add("pergunta", "Qual coluna usar para o limite por filial?")["id"]
        self.tasks.answer(answered, "Validação QA")
        self.number = self.store.get(self.open)["data"]["numero"]

    def tearDown(self):
        self.tmp.cleanup()

    def test_mentioned_number_or_shared_terms_point_to_open_question(self):
        by_number = capture.answer_candidates(self.store, "sobre a @%s: vale a filial principal" % self.number)
        self.assertEqual(len(by_number), 1)
        self.assertIn(self.open, by_number[0])
        by_terms = capture.answer_candidates(self.store, "o limite por filial fica na facliuni, uma linha por unidade")
        self.assertEqual(len(by_terms), 1)
        self.assertIn(self.open, by_terms[0])

    def test_unrelated_or_administrative_message_has_no_candidate(self):
        self.assertEqual(capture.answer_candidates(self.store, "pode commitar e abrir o PR"), [])
        self.assertEqual(capture.answer_candidates(self.store, "task review"), [])
        self.assertEqual(capture.answer_candidates(self.store, ""), [])


if __name__ == "__main__":
    unittest.main()
