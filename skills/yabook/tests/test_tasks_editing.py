import http.client
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from tasks_runtime import editing, events, fmt, server, sheet
from tasks_runtime.commands import Tasks
from tasks_runtime.store import Conflict, TaskStore, scaffold
from test_tasks_store import GIT_ENV

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "yabook_tasks.py"


class EditingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.env = patch.dict(os.environ, GIT_ENV)
        self.env.start()
        self.root = self.base / "dados"
        scaffold(self.root)
        subprocess.run(["git", "-C", str(self.root), "init", "-q", "-b", "main"], check=True)
        subprocess.run(["git", "-C", str(self.root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(self.root), "commit", "-q", "-m", "inicio"], check=True)
        self.terms = self.base / "termos.txt"
        self.terms.write_text("ClienteSecreto\n", encoding="utf-8")
        self.confidential = self.base / "confidencial"
        self.confidential.mkdir()
        self.cfg = dict(machine="trabalho", confidential=str(self.confidential))
        self.store = TaskStore(self.root, str(self.terms))
        tasks = Tasks(self.store, self.cfg)
        tasks.add("projeto", "Melhorias", projeto="5723", nivel="epico")
        tasks.add("issue", "Agenda", issue=["org/app#12"], pai="projeto-5723")
        tasks.add("tarefa", "Revisar layout")

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def rev(self, identifier):
        return self.store.get(identifier)["revision"]

    def log(self):
        return subprocess.run(["git", "-C", str(self.root), "log", "--format=%s"], capture_output=True, text=True).stdout.splitlines()

    def test_save_moves_edits_commits_and_leaves_board_events_pending(self):
        body = dict(tarefas=[
            dict(id="issue-agenda", revision=self.rev("issue-agenda"), campos=dict(coluna="andamento", proximo_passo="Publicar"),
                 registro="Layout aprovado"),
            dict(id="tarefa-revisar-layout", revision=self.rev("tarefa-revisar-layout"), campos=dict(ordem=5, pessoal=False)),
        ])
        result = editing.save(self.store, self.cfg, body)
        data = self.store.get("issue-agenda")
        self.assertEqual((data["data"]["coluna"], data["data"]["proximo_passo"]), ("andamento", "Publicar"))
        self.assertIn("Layout aprovado", data["body"])
        self.assertEqual(self.store.get("tarefa-revisar-layout")["data"]["pessoal"], False)
        self.assertEqual(self.log()[0], editing.COMMIT_MESSAGE)
        self.assertTrue(result["commit"])
        pending = {e["id"]: e["acao"] for e in events.pending(self.root)}
        self.assertEqual(set(result["eventos"]), set(pending))
        self.assertEqual(sorted(pending.values()), ["editar", "editar", "mover", "reordenar"])
        self.assertIn("Backlog → Em andamento", result["resumo"])
        self.assertIn("task review", result["resumo"])
        # Desmarcar volta ao cálculo
        editing.save(self.store, self.cfg, dict(tarefas=[dict(id="tarefa-revisar-layout", revision=self.rev("tarefa-revisar-layout"),
                                                               campos=dict(pessoal=None))]))
        self.assertNotIn("pessoal", self.store.get("tarefa-revisar-layout")["data"])

    def test_stale_revision_refuses_everything(self):
        stale = self.rev("issue-agenda")
        Tasks(self.store, self.cfg).edit("issue-agenda", dict(proximo_passo="Mudou no agente"))
        body = dict(tarefas=[dict(id="tarefa-revisar-layout", revision=self.rev("tarefa-revisar-layout"), campos=dict(coluna="testes")),
                             dict(id="issue-agenda", revision=stale, campos=dict(coluna="testes"))])
        with self.assertRaises(Conflict) as error:
            editing.save(self.store, self.cfg, body)
        self.assertEqual(error.exception.ids, ["issue-agenda"])
        self.assertEqual(self.store.get("tarefa-revisar-layout")["data"]["coluna"], "backlog")
        self.assertEqual(self.store.get("issue-agenda")["data"]["proximo_passo"], "Mudou no agente")

    def test_terms_refuse_and_complement_moves_text_locally(self):
        body = dict(tarefas=[dict(id="issue-agenda", revision=self.rev("issue-agenda"),
                                  campos=dict(proximo_passo="Validar na base do ClienteSecreto"), registro="ok")],
                    colunas=[dict(id="testes", nome="Validação")])
        with self.assertRaises(editing.TermsFound) as error:
            editing.save(self.store, self.cfg, body)
        self.assertEqual(error.exception.hits[0]["campo"], "proximo_passo")
        self.assertEqual(fmt.loads((self.root / "quadro.yml").read_text())["colunas"][3]["nome"], "Testes")
        body["tarefas"][0]["campos"]["proximo_passo"] = None
        body["complementos"] = [dict(id="issue-agenda", texto="proximo_passo: Validar na base do ClienteSecreto")]
        editing.save(self.store, self.cfg, body)
        self.assertIn("ClienteSecreto", (self.confidential / "tarefas" / "issue-agenda.md").read_text())
        self.assertNotIn("ClienteSecreto", self.store.get("issue-agenda")["body"])
        home = dict(machine="casa", confidential=str(self.base / "ausente"))
        with self.assertRaises(ValueError):
            editing.save(self.store, home, dict(complementos=[dict(id="issue-agenda", texto="x")]))

    def test_rename_column_keeps_role(self):
        result = editing.save(self.store, self.cfg, dict(colunas=[dict(id="testes", nome="Validação")]))
        columns = {c["id"]: c for c in self.store.columns()}
        self.assertEqual((columns["testes"]["nome"], columns["testes"]["papel"]), ("Validação", "validacao"))
        self.assertEqual(result["aplicadas"][0]["acao"], "coluna")
        self.assertEqual(events.pending(self.root)[0]["acao"], "renomear-coluna")
        for bad in (dict(colunas=[dict(id="nada", nome="X")]), dict(colunas=[dict(id="testes", nome=" ")]), dict()):
            with self.assertRaises(ValueError):
                editing.save(self.store, self.cfg, bad)

    def test_sheet_confirmation_from_the_site(self):
        editing.save(self.store, self.cfg, dict(ficha=dict(data="2026-11-11", linhas=[dict(tipo="projeto", codigo="5723", total=8)], extras=[])))
        self.assertEqual(sheet.confirmed_day(self.root, "2026-11-11")["linhas"][0]["total"], 8)
        self.assertEqual(events.pending(self.root)[0]["acao"], "confirmar-ficha")

    def test_tree_violation_is_refused_before_writing(self):
        body = dict(tarefas=[dict(id="tarefa-revisar-layout", revision=self.rev("tarefa-revisar-layout"), campos=dict(coluna="testes")),
                             dict(id="projeto-5723", revision=self.rev("projeto-5723"), campos=dict(nivel="historia"))])
        with self.assertRaises(ValueError):
            editing.save(self.store, self.cfg, body)
        self.assertEqual(self.store.get("tarefa-revisar-layout")["data"]["coluna"], "backlog")
        with self.assertRaises(ValueError):
            editing.save(self.store, self.cfg, dict(tarefas=[dict(id="issue-agenda", revision=self.rev("issue-agenda"), campos=dict(criada="x"))]))

    def test_http_save_flow(self):
        srv = server.make_server(self.store, self.cfg, port=0, poll_seconds=0.1, writer=editing.handle)
        server.start_background(srv)
        port = srv.server_address[1]
        try:
            def call(method, path, body=None, token=None):
                conn = http.client.HTTPConnection("127.0.0.1", port, timeout=5)
                headers = {"Content-Type": "application/json"}
                if token:
                    headers["X-YABook-Token"] = token
                conn.request(method, path, json.dumps(body) if body is not None else None, headers)
                response = conn.getresponse()
                payload = response.read()
                conn.close()
                return response.status, payload
            page = call("GET", "/")[1]
            token = re.search(rb'name="yabook-token" content="([^"]+)"', page).group(1).decode()
            ok = dict(tarefas=[dict(id="issue-agenda", revision=self.rev("issue-agenda"), campos=dict(coluna="testes"))])
            status, payload = call("POST", "/api/salvar", ok, token)
            self.assertEqual(status, 200, payload)
            self.assertIn("resumo", json.loads(payload))
            self.assertEqual(call("POST", "/api/salvar", ok, token)[0], 409)  # mesma revisão, agora antiga
            bad = dict(tarefas=[dict(id="issue-agenda", revision=self.rev("issue-agenda"), campos=dict(titulo="ClienteSecreto"))])
            status, payload = call("POST", "/api/salvar", bad, token)
            self.assertEqual(status, 422)
            self.assertTrue(json.loads(payload)["base_confidencial"])
            self.assertEqual(call("POST", "/api/outra", {}, token)[0], 404)
        finally:
            srv.stopping = True
            srv.shutdown()
            srv.server_close()


@unittest.skipUnless(Path("/proc/self/status").exists(), "medição de memória usa /proc")
class MemoryTest(unittest.TestCase):
    def test_server_memory_with_300_tasks(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "dados"
            scaffold(root)
            store = TaskStore(root)
            for index in range(300):
                store.save(dict(id="tarefa-%d" % index, tipo="tarefa", titulo="Tarefa %d com texto de exemplo" % index,
                                coluna="backlog", proximo_passo="Passo %d" % index), "## Registro\n\n- 2026-11-11 10:00 — feito\n")
            config = Path(tmp) / "cfg.json"
            with socket.socket() as probe:
                probe.bind(("127.0.0.1", 0))
                port = probe.getsockname()[1]
            config.write_text(json.dumps(dict(tasks=dict(root=str(root), machine="trabalho", port=port))))
            process = subprocess.Popen([sys.executable, str(SCRIPT), "--config", str(config), "board", "--serve"],
                                       stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
            try:
                process.stdout.readline()
                for _ in range(3):
                    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
                    conn.request("GET", "/api/estado")
                    state = json.loads(conn.getresponse().read())
                    conn.close()
                self.assertEqual(len(state["tarefas"]), 300)
                time.sleep(0.2)
                rss = next(int(line.split()[1]) for line in Path("/proc/%d/status" % process.pid).read_text().splitlines()
                           if line.startswith("VmRSS"))
                self.assertLess(rss, 40 * 1024, "servidor usa %d kB" % rss)
            finally:
                process.terminate()
                process.wait(5)
                process.stdout.close()


if __name__ == "__main__":
    unittest.main()
