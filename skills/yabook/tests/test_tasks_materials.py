import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from yabook_tasks import build_parser, run
from tasks_runtime import editing, materials
from tasks_runtime.commands import Tasks
from tasks_runtime.server import Board
from tasks_runtime.store import Conflict, TaskStore, scaffold


class TaskMaterialsTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        data = root / "tasks"
        self.private = root / "confidential"
        self.private.mkdir()
        scaffold(data)
        self.cfg = dict(confidential=str(self.private), machine="teste")
        self.store = TaskStore(data, terms=["ambiente-interno"])
        self.tasks = Tasks(self.store, self.cfg)
        self.task = self.tasks.add("tarefa", "Organizar fontes", size=1)["id"]
        self.other = self.tasks.add("tarefa", "Outra demanda", size=1)["id"]

    def edit(self, **changes):
        current = self.store.get(self.task)
        return editing.save(self.store, self.cfg, {"tarefas": [
            dict(id=self.task, revision=current["revision"], **changes),
        ]})

    def upload(self, name, content, local=False):
        return dict(nome=name, base64=base64.b64encode(content).decode(), local=local)

    def test_markdown_and_notes_survive_file_read_and_number_is_never_reused(self):
        description = 'Resumo.\n\n## Escopo\n- Manter "A": #3\n- Caminho \\rede e d\'água'
        note = 'Decisão "A", teste B\n\n- Confirmado #4\n- Revisar seção C'
        self.edit(campos=dict(descricao=description),
                  anotacoes=[dict(acao="criar", titulo='Análise d\'água ("A")', texto=note),
                             dict(acao="criar", titulo="Validação", texto="Preparar lote")])
        detail = Board(self.store, self.cfg).task(self.task)
        self.assertEqual(detail["data"]["descricao"], description)
        self.assertEqual(detail["data"]["anotacoes"][0]["texto"], note)
        self.tasks.update_materials(self.task, [dict(acao="editar", numero=2, titulo="Validação", texto="Validar por lote")],
                                    expected_revision=detail["revision"])
        with self.assertRaises(Conflict):
            self.tasks.update_materials(self.task, [dict(acao="excluir", numero=2)], expected_revision=detail["revision"])
        self.edit(anotacoes=[dict(acao="excluir", numero=1), dict(acao="excluir", numero=2)])
        self.edit(anotacoes=[dict(acao="criar", titulo="Escopo vigente", texto="Confirmado")])
        data = self.store.get(self.task)["data"]
        self.assertEqual(data["anotacoes_seq"], 3)
        self.assertEqual([n["numero"] for n in data["anotacoes"]], [3])

    def test_attachments_have_correct_contents_and_storage_and_are_task_scoped(self):
        public = self.upload("fontes.md", b"# Inventario")
        private = self.upload("Lista confidencial.csv", b"ambiente-interno", local=True)
        self.edit(anexos=[public, private])
        items = {f["nome"]: f for f in self.store.get(self.task)["data"]["anexos"]}
        for upload in (public, private):
            item = items[upload["nome"]]
            key = item["id"]
            meta, raw = materials.read_attachment(self.store, self.cfg, self.task, key)
            self.assertEqual((meta["nome"], raw), (upload["nome"], base64.b64decode(upload["base64"])))
            with self.assertRaises(KeyError):
                materials.read_attachment(self.store, self.cfg, self.other, key)
        key = items[private["nome"]]["id"]
        self.assertFalse((self.store.root / "anexos-tasks" / self.task / key).exists())
        self.assertEqual((self.private / "anexos-tasks" / self.task / key).read_bytes(), b"ambiente-interno")
        board = Board(self.store, self.cfg)
        self.assertNotIn("Lista confidencial", json.dumps(board.state()))
        output = self.private / "copia.html"
        board.export(output)
        page = output.read_text(encoding="utf-8")
        self.assertNotIn("Lista confidencial.csv", page)
        self.assertNotIn(private["base64"], page)
        with self.assertRaisesRegex(ValueError, "Base confidencial"):
            materials.read_attachment(self.store, {}, self.task, key)

    def test_invalid_upload_prevents_all_writes_for_the_batch(self):
        current = self.store.get(self.task)
        note = dict(acao="criar", titulo="Verificação", texto="Testar novamente")
        cases = [self.upload("../fontes.md", b"x"),
                 self.upload("fontes.html", b"x"), self.upload("fontes.md", b"ambiente-interno"),
                 dict(nome="fontes.md", local=False, base64="***")]
        for upload in cases:
            with self.subTest(upload=upload["nome"]), self.assertRaises(ValueError):
                self.edit(anotacoes=[note], anexos=[self.upload("valido.md", b"ok"), upload])
            self.assertEqual(self.store.get(self.task), current)
            self.assertFalse((self.store.root / "anexos-tasks").exists())

    def test_agent_commands_preserve_the_other_notes_and_download_to_a_new_file(self):
        config = self.private / "cfg.json"
        config.write_text(json.dumps({"tasks": dict(self.cfg, root=str(self.store.root))}), encoding="utf-8")
        parser = build_parser()

        def cli(*args):
            return run(parser.parse_args(["--config", str(config), *args]))

        number = self.store.get(self.task)["data"]["numero"]
        ref = f"@{number}"
        note = cli("anotacao", ref, "criar", "--titulo", "Plano", "--texto", "Validar por lote")
        self.assertEqual(note["anotacoes"][0]["numero"], 1)
        cli("anotacao", ref, "criar", "--titulo", "Origem", "--texto", "Revisão da análise")
        revision = self.store.get(self.task)["revision"]
        cli("anotacao", ref, "editar", "--numero", "1", "--titulo", "Plano", "--texto", "Validar todos",
            "--revision", revision)
        self.assertEqual([n["texto"] for n in self.store.get(self.task)["data"]["anotacoes"]],
                         ["Validar todos", "Revisão da análise"])
        path = self.private / "fontes.txt"
        path.write_bytes(b"lista de teste")
        upload = cli("anexar", ref, str(path), "--local")
        key = upload["anexos"][0]["id"]
        output = self.private / "saida.txt"
        cli("baixar-anexo", ref, key, "--output", str(output))
        self.assertEqual(output.read_bytes(), path.read_bytes())
        with self.assertRaisesRegex(ValueError, "já existe"):
            cli("baixar-anexo", ref, key, "--output", str(output))

    def test_multiline_task_text_respects_confidential_terms(self):
        with self.assertRaisesRegex(ValueError, "ambiente-interno"):
            self.tasks.edit(self.task, {"descricao": "Descrição\nambiente-interno"})
        with self.assertRaisesRegex(ValueError, "confidencial"):
            self.edit(anotacoes=[dict(acao="criar", titulo="Contexto", texto="Linha\nambiente-interno")])
        self.assertNotIn("descricao", self.store.get(self.task)["data"])
