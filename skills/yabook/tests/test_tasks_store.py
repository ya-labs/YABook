import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import fmt
from tasks_runtime.store import Conflict, TaskStore, scaffold

GIT_ENV = dict(GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.com", GIT_COMMITTER_NAME="t",
               GIT_COMMITTER_EMAIL="t@example.com", GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


class FormatTest(unittest.TestCase):
    def test_roundtrip_frontmatter(self):
        data = dict(id="demanda-1001", tipo="demanda", titulo="Ajustar: limite, desconto", coluna="backlog",
                    demanda="1001", issue=["org/repo#10"], refs=["confidencial:pagina"], prazo="2026-11-14")
        text = fmt.join_frontmatter(data, "## Registro\n- nota", ("id",))
        parsed, body = fmt.split_frontmatter(text)
        self.assertEqual(parsed, data)
        self.assertEqual(body.strip(), "## Registro\n- nota")

    def test_rejects_unsupported_yaml(self):
        for text in ("a: &x 1", "a: [1, 2", "a: 1\na: 2", "a:\n\t- 1"):
            with self.assertRaises(fmt.FormatError, msg=text):
                fmt.loads(text)

    def test_default_quadro_parses(self):
        from tasks_runtime.store import DEFAULT_QUADRO, DEFAULT_CONFIG, validate_quadro
        columns = validate_quadro(fmt.loads(DEFAULT_QUADRO))
        self.assertEqual([c["papel"] for c in columns],
                         ["entrada", "pronto", "ativo", "validacao", "concluido", "arquivado"])
        self.assertEqual(fmt.loads(DEFAULT_CONFIG)["ficha"], dict(horas_dia=8, arredondamento=1))


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        scaffold(self.root)
        self.store = TaskStore(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def task(self, **extra):
        return dict(dict(id="demanda-1001", tipo="demanda", titulo="Ajustar limite", coluna="backlog"), **extra)

    def test_save_get_and_normalize(self):
        rev = self.store.save(self.task(demanda=1001, issue="org/repo#1"), "corpo")
        got = self.store.get("demanda-1001")
        self.assertEqual(got["revision"], rev)
        self.assertEqual(got["data"]["demanda"], "1001")
        self.assertEqual(got["data"]["issue"], ["org/repo#1"])
        self.assertIn("criada", got["data"])
        self.assertEqual(got["body"].strip(), "corpo")

    def test_stale_revision_is_refused_without_losing_data(self):
        first = self.store.save(self.task())
        second = self.store.save(dict(self.task(), titulo="Novo título"), "", first)
        with self.assertRaises(Conflict):
            self.store.save(dict(self.task(), titulo="Edição antiga"), "", first)
        self.assertEqual(self.store.get("demanda-1001")["data"]["titulo"], "Novo título")
        self.assertEqual(self.store.get("demanda-1001")["revision"], second)
        with self.assertRaises(Conflict):
            self.store.save(self.task())

    def test_creation_time_is_preserved(self):
        rev = self.store.save(self.task(criada="2026-01-01T00:00:00-03:00"))
        self.store.save(dict(self.task(), criada="outra"), "", rev)
        self.assertEqual(self.store.get("demanda-1001")["data"]["criada"], "2026-01-01T00:00:00-03:00")

    def test_validation(self):
        for extra in (dict(coluna="inexistente"), dict(prazo="14/11/2026"), dict(prazo="2026-02-30"),
                      dict(issue=["sem-numero"]), dict(refs=["outro:x"]), dict(tipo="bug"), dict(titulo=" "),
                      dict(id="Maiúsculo")):
            with self.assertRaises(ValueError, msg=extra):
                self.store.save(self.task(**extra))
        self.assertEqual(self.store.list(), [])

    def test_terms_block_writing(self):
        store = TaskStore(self.root, terms=["Cliente Exemplo"])
        with self.assertRaises(ValueError) as error:
            store.save(self.task(titulo="Ajuste do cliente exemplo"))
        self.assertIn("Cliente Exemplo", str(error.exception))
        self.assertFalse(store.exists("demanda-1001"))
        store.save(self.task(titulo="Ajuste de exemplos"))

    def test_new_id(self):
        self.assertEqual(self.store.new_id("demanda", 1001), "demanda-1001")
        self.store.save(self.task())
        self.assertEqual(self.store.new_id("demanda", "1001"), "demanda-1001-2")
        self.assertEqual(self.store.new_id("tarefa", title="Revisar fluxo de horas"), "tarefa-revisar-fluxo-de-horas")


class PrecommitTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / "dados"
        self.env = patch.dict(os.environ, GIT_ENV)
        self.env.start()
        scaffold(self.root)
        self.git("init", "-q", "-b", "main")
        self.git("config", "core.hooksPath", ".githooks")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def git(self, *args, check=True):
        return subprocess.run(["git", "-C", str(self.root), *args], capture_output=True, text=True, check=check)

    def commit(self, name, text):
        (self.root / "tarefas" / name).write_text(text, encoding="utf-8")
        self.git("add", "-A")
        return self.git("commit", "-q", "-m", "teste", check=False)

    def test_blocks_term_from_local_list(self):
        terms = Path(self.tmp.name) / "termos.txt"
        terms.write_text("# comentário\nCliente Exemplo\n", encoding="utf-8")
        self.git("config", "yabook.terms", str(terms))
        result = self.commit("a.md", "titulo: ajuste do CLIENTE EXEMPLO\n")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cliente Exemplo", result.stderr)
        self.git("reset", "-q")
        (self.root / "tarefas" / "a.md").unlink()
        self.assertEqual(self.commit("b.md", "titulo: exemplos de clientes\n").returncode, 0)

    def test_warns_without_list(self):
        result = self.commit("a.md", "titulo: qualquer\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("lista de termos proibidos ausente", result.stderr)


if __name__ == "__main__":
    unittest.main()
