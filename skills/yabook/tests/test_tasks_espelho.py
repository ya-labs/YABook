import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import mirror
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold

OPTIONS = [dict(id="o-" + n, name=n) for n in ("Backlog", "Pronto para dev", "Em andamento", "Bloqueado", "Validação interna",
                                               "Pronto para merge [QA]", "Validação QA", "Concluído", "Épicos")]
SIZES = [dict(id="s%d" % n, name=str(n)) for n in range(1, 6)]


class FakeGitHub:
    def __init__(self, status=None, size=None):
        self.status, self.size, self.calls = status, size, []

    def __call__(self, query, **variables):
        if query.startswith("mutation"):
            self.calls.append(variables["v"])
            return {}
        node = dict(id="item", project=dict(id="proj", status=dict(id="fs", options=OPTIONS), size=dict(id="fz", options=SIZES)),
                    statusValue=dict(name=self.status) if self.status else None, sizeValue=dict(name=self.size) if self.size else None)
        return dict(repository=dict(issue=dict(projectItems=dict(nodes=[node]))))


class MirrorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        (self.root / "quadro.yml").write_text((self.root / "quadro.yml").read_text().replace(
            "  - {id: testes, nome: Testes, papel: validacao}\n",
            "  - {id: testes, nome: Testes, papel: validacao}\n  - {id: qa, nome: Validação QA, papel: validacao}\n"))
        self.store = TaskStore(self.root)
        self.tasks = Tasks(self.store, dict(machine="trabalho"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_column_name_wins_and_size_is_published(self):
        self.tasks.add("issue", "A", issue=["dono/repo#1"], coluna="qa", size=3)
        gh = FakeGitHub(status="Em andamento", size="1")
        result = mirror.run(self.store, {}, graphql=gh)
        self.assertEqual(gh.calls, ["o-Validação QA", "s3"])
        self.assertEqual(result["publicadas"][0]["alteracoes"], ["Status: Validação QA", "Size: 3"])
        gh.calls.clear()
        self.assertEqual(mirror.run(self.store, {}, graphql=gh)["verificadas"], 0)  # sem mudança, nada a publicar

    def test_never_moves_back_nor_touches_team_states(self):
        self.tasks.add("issue", "Atrás", issue=["dono/repo#2"], coluna="andamento")
        self.tasks.add("issue", "Equipe", issue=["dono/repo#3"], coluna="concluido")
        gh = FakeGitHub(status="Validação QA")
        mirror.run(self.store, {}, graphql=gh)
        self.assertEqual(gh.calls, ["o-Concluído"])  # #3 avança; #2 não volta para andamento
        gh = FakeGitHub(status="Pronto para merge [QA]")
        self.tasks.edit("issue-atras", dict(coluna="concluido"))
        mirror.run(self.store, {}, graphql=gh)
        self.assertEqual(gh.calls, [])

    def test_column_mapping_advances_within_validation(self):
        self.tasks.add("issue", "Interna", issue=["dono/repo#7"], coluna="qa")
        gh = FakeGitHub(status="Validação interna")
        mirror.run(self.store, dict(espelho=dict(status={"*": dict(testes="Validação interna", qa="Validação QA")})), graphql=gh)
        self.assertEqual(gh.calls, ["o-Validação QA"])  # interna -> QA avança pela ordem das opções
        self.tasks.edit("issue-interna", dict(coluna="testes"))
        gh = FakeGitHub(status="Validação QA")
        mirror.run(self.store, dict(espelho=dict(status={"*": dict(testes="Validação interna", qa="Validação QA")})), graphql=gh)
        self.assertEqual(gh.calls, [])  # QA -> interna seria recuar

    def test_configured_mapping_epics_and_errors(self):
        self.tasks.add("issue", "Mapa", issue=["dono/repo#4"], coluna="testes")
        self.tasks.add("issue", "Épico", issue=["dono/repo#5"], coluna="andamento", nivel="epico", size=5)
        gh = FakeGitHub()
        mirror.run(self.store, dict(espelho=dict(status={"dono/repo": dict(validacao="Validação interna")})), graphql=gh)
        self.assertEqual(sorted(gh.calls), ["o-Validação interna", "s5"])  # épico só recebe Size

        def failing(query, **variables):
            raise RuntimeError("sem permissão")
        self.tasks.add("issue", "Falha", issue=["dono/repo#6"], coluna="andamento")
        result = mirror.run(self.store, {}, graphql=failing)
        self.assertEqual(result["erros"][0]["ref"], "dono/repo#6")
        state = json.loads((self.root / "local" / "espelho.json").read_text())
        self.assertNotIn("dono/repo#6", state)  # tenta de novo na próxima execução


if __name__ == "__main__":
    unittest.main()
