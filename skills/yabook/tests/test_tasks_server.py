import contextlib
import http.client
import io
import json
import re
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_tasks
from tasks_runtime import server
from tasks_runtime.commands import Tasks
from tasks_runtime.store import TaskStore, scaffold


class ServerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / "dados"
        scaffold(self.root)
        self.confidential = self.base / "confidencial"
        (self.confidential / "tarefas").mkdir(parents=True)
        (self.confidential / "paginas").mkdir()
        (self.confidential / "paginas" / "cliente.md").write_text("detalhe confidencial", encoding="utf-8")
        (self.base / "fora.md").write_text("fora da base", encoding="utf-8")
        self.store = TaskStore(self.root)
        self.cfg = dict(machine="trabalho", confidential=str(self.confidential))
        tasks = Tasks(self.store, self.cfg)
        tasks.add("projeto", "Melhorias do aplicativo", projeto="5723", nivel="epico", coluna="andamento")
        tasks.add("issue", "Agenda </script>", issue=["org/app#12"], pai="projeto-5723", refs=["confidencial:paginas/cliente"])
        tasks.add("issue", "V1 pessoal", issue=["org/yabook#156"], nivel="epico", refs=["confidencial:../fora"])
        tasks.ask("Qual layout?", about="issue-agenda-script")
        (self.confidential / "tarefas" / "projeto-5723.md").write_text("complemento local", encoding="utf-8")
        self.server = server.make_server(self.store, self.cfg, port=0, poll_seconds=0.1)
        self.port = self.server.server_address[1]
        server.start_background(self.server)

    def tearDown(self):
        self.server.stopping = True
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def request(self, method, path, body=None, headers=None, host=None):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        headers = dict(headers or {})
        conn.putrequest(method, path, skip_host=True)
        conn.putheader("Host", host or "127.0.0.1:%d" % self.port)
        data = json.dumps(body).encode() if body is not None else None
        if data:
            headers.setdefault("Content-Type", "application/json")
            headers["Content-Length"] = str(len(data))
        for key, value in headers.items():
            conn.putheader(key, value)
        conn.endheaders(data)
        response = conn.getresponse()
        payload = response.read()
        conn.close()
        return response.status, response.getheader("Content-Type"), payload

    def get_json(self, path):
        status, _, payload = self.request("GET", path)
        return status, json.loads(payload)

    def test_state_has_tree_codes_and_confidential_flags(self):
        status, state = self.get_json("/api/estado")
        self.assertEqual(status, 200)
        tasks = {t["id"]: t for t in state["tarefas"]}
        self.assertEqual(tasks["issue-agenda-script"]["codigo"], "5723")
        self.assertEqual(tasks["issue-agenda-script"]["perguntas_abertas"], 1)
        self.assertEqual(tasks["issue-agenda-script"]["confidencial"], "disponivel")
        self.assertEqual(tasks["projeto-5723"]["confidencial"], "disponivel")
        self.assertEqual(tasks["issue-v1-pessoal"]["confidencial"], "bloqueado")  # referência fora da base
        self.assertTrue(tasks["issue-v1-pessoal"]["pessoal"])
        self.assertEqual({e["id"] for e in state["epicos"]}, {"projeto-5723", "issue-v1-pessoal"})
        self.assertTrue(state["base_confidencial"])
        question = next(t for t in state["tarefas"] if t["tipo"] == "pergunta")
        self.assertEqual((question["sobre"], question["papel"]), ("issue-agenda-script", "entrada"))
        self.assertEqual(tasks["projeto-5723"]["papel"], "ativo")
        self.assertEqual([q["id"] for q in state["perguntas"]], [question["id"]])
        self.assertEqual({e["id"]: e["historias"] for e in state["epicos"]}["projeto-5723"], 1)

    def test_task_detail_resolves_refs_only_inside_the_base(self):
        status, detail = self.get_json("/api/tarefa/issue-agenda-script")
        self.assertEqual(detail["referencias"], {"confidencial:paginas/cliente": "detalhe confidencial"})
        status, detail = self.get_json("/api/tarefa/issue-v1-pessoal")
        self.assertEqual(detail["referencias"], {"confidencial:../fora": None})
        status, detail = self.get_json("/api/tarefa/projeto-5723")
        self.assertEqual(detail["complemento"], "complemento local")
        self.assertEqual([f["id"] for f in detail["filhos"]], ["issue-agenda-script"])
        self.assertEqual(self.get_json("/api/tarefa/inexistente")[0], 404)

    def test_without_base_confidential_is_locked(self):
        board = server.Board(self.store, dict(machine="casa", confidential=str(self.base / "ausente")))
        tasks = {t["id"]: t for t in board.state()["tarefas"]}
        self.assertEqual(tasks["issue-agenda-script"]["confidencial"], "bloqueado")
        self.assertNotIn("complemento", board.task("projeto-5723"))

    def test_reference_base_prefix_and_path_boundaries(self):
        board = server.Board(self.store, self.cfg)
        expected = self.confidential / "paginas" / "cliente.md"
        self.assertEqual(board._ref_path("confidencial/paginas/cliente.md"), expected)
        self.assertEqual(board._ref_path("confidencial/paginas/cliente"), expected)
        self.assertEqual(board._ref_path("paginas/cliente"), expected)
        self.assertIsNone(board._ref_path("confidencial/../../fora.md"))
        self.assertIsNone(board._ref_path(str(self.base / "fora.md")))
        (self.confidential / "atalho.md").symlink_to(self.base / "fora.md")
        self.assertIsNone(board._ref_path("atalho"))
        self.assertIsNone(board._ref_path("confidencial/atalho.md"))

    def test_read_routes(self):
        for path in ("/api/ficha", "/api/ficha?semana=1", "/api/semana", "/api/historico?limite=5"):
            with self.subTest(path=path):
                self.assertEqual(self.get_json(path)[0], 200)
        self.assertEqual(len(self.get_json("/api/semana?data=2026-11-11")[1]["dias"]), 7)

    def test_host_and_write_protection(self):
        self.assertEqual(self.request("GET", "/api/estado", host="evil.example:%d" % self.port)[0], 403)
        self.assertEqual(self.request("GET", "/api/estado", host="localhost:%d" % self.port)[0], 200)
        self.assertEqual(self.request("POST", "/api/salvar", body={})[0], 403)
        status, _, page = self.request("GET", "/")
        token = re.search(rb'name="yabook-token" content="([^"]+)"', page).group(1).decode()
        self.assertEqual(self.request("POST", "/api/salvar", body={}, headers={"X-YABook-Token": token,
                                                                               "Origin": "http://evil.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/salvar", body={}, headers={"X-YABook-Token": token})[0], 404)

    def test_static_shell(self):
        status, kind, _ = self.request("GET", "/manifest.webmanifest")
        self.assertEqual((status, kind.split(";")[0]), (200, "application/manifest+json"))
        self.assertEqual(self.request("GET", "/sw.js")[0], 200)
        self.assertEqual(self.request("GET", "/icon-192.png")[1], "image/png")
        self.assertEqual(self.request("GET", "/../store.py")[0], 404)
        self.assertEqual(self.request("GET", "/server.py")[0], 404)

    def test_stream_announces_changes(self):
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        conn.request("GET", "/api/stream")
        response = conn.getresponse()
        self.assertEqual(response.getheader("Content-Type").split(";")[0], "text/event-stream")
        self.assertIn(b"event: pronto", response.fp.readline() + response.fp.readline())
        time.sleep(0.15)
        Tasks(self.store, self.cfg).edit("projeto-5723", dict(proximo_passo="Novo passo"))
        deadline, seen = time.time() + 3, b""
        while time.time() < deadline and b"event: mudou" not in seen:
            seen += response.fp.readline()
        conn.close()
        self.assertIn(b"event: mudou", seen)

    def test_static_export_embeds_data_without_server(self):
        result = server.Board(self.store, self.cfg).export(self.base / "saida")
        html = Path(result["arquivo"]).read_text(encoding="utf-8")
        self.assertIn("window.YABOOK_SNAPSHOT", html)
        self.assertNotIn('rel="manifest"', html)
        self.assertNotIn("Agenda </script>", html)  # fechamento de script escapado no JSON
        self.assertIn("Agenda <\\/script>", html)
        self.assertEqual(result["tarefas"], 4)

    def test_cli_board_output(self):
        config = self.base / "cfg.json"
        config.write_text(json.dumps(dict(tasks=dict(root=str(self.root), machine="trabalho"))))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = yabook_tasks.main(["--config", str(config), "board", "--output", str(self.base / "copia.html")])
        self.assertEqual(code, 0)
        self.assertTrue((self.base / "copia.html").is_file())
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(yabook_tasks.main(["--config", str(config), "board"]), 1)


if __name__ == "__main__":
    unittest.main()
