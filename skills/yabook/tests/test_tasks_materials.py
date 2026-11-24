import base64
import contextlib
import io
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
        state = board.state()
        by_task = {item["id"]: item for item in state["tarefas"]}
        self.assertEqual(by_task[self.task]["anexos_total"], 2)
        self.assertEqual(by_task[self.other]["anexos_total"], 0)
        self.assertNotIn("anexos", by_task[self.task])
        self.assertNotIn("Lista confidencial", json.dumps(state))
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

    def test_viewable_formats_are_accepted_and_new_text_formats_are_checked(self):
        self.edit(anexos=[self.upload("dados.json", b'{"a": 1}'), self.upload("saida.log", b"ok"),
                          self.upload("tela.webp", b"RIFF"), self.upload("fluxo.gif", b"GIF89a")])
        self.assertEqual({f["nome"] for f in self.store.get(self.task)["data"]["anexos"]},
                         {"dados.json", "saida.log", "tela.webp", "fluxo.gif"})
        for name in ("erro.log", "erro.json"):
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, "termo confidencial"):
                self.edit(anexos=[self.upload(name, b"falha em ambiente-interno")])
        with self.assertRaisesRegex(ValueError, "UTF-8"):
            self.edit(anexos=[self.upload("latin.log", "ação".encode("latin-1"))])

    def attachments(self):
        return self.store.get(self.task)["data"].get("anexos", [])

    def blob(self, item):
        return materials.blob_path(self.store, self.cfg, self.task, item)

    def test_edit_renames_replaces_and_deletes_keeping_position_and_removing_old_files(self):
        self.edit(anexos=[self.upload("roteiro.md", b"# Passos"), self.upload("dados.csv", b"a;b"),
                          self.upload("tela.png", b"PNG")])
        first, csv, image = self.attachments()
        self.edit(anexos=[dict(acao="editar", id=first["id"], nome="Roteiro final.md"),
                          dict(acao="editar", id=csv["id"], base64=base64.b64encode(b"a;b\n1;2").decode()),
                          dict(acao="excluir", id=image["id"])])
        renamed, replaced = self.attachments()
        self.assertEqual((renamed["nome"], replaced["nome"]), ("Roteiro final.md", "dados.csv"))
        self.assertEqual(materials.read_attachment(self.store, self.cfg, self.task, renamed["id"])[1], b"# Passos")
        self.assertEqual(materials.read_attachment(self.store, self.cfg, self.task, replaced["id"])[1], b"a;b\n1;2")
        for old in (first, csv, image):
            self.assertFalse(self.blob(old).exists(), old["nome"])
        self.edit(anexos=[dict(acao="excluir", id=renamed["id"]), dict(acao="excluir", id=replaced["id"])])
        self.assertEqual(self.attachments(), [])
        self.assertFalse((self.store.root / "anexos-tasks" / self.task).exists())

    def test_invalid_edit_changes_nothing(self):
        self.edit(anexos=[self.upload("roteiro.md", b"# Passos"), self.upload("Lista.csv", b"x", local=True)])
        shared, local = self.attachments()
        current = self.store.get(self.task)
        encoded = lambda raw: base64.b64encode(raw).decode()
        cases = [dict(acao="editar", id=shared["id"], nome="roteiro.txt"),
                 dict(acao="editar", id=shared["id"], base64=encoded(b"cita ambiente-interno")),
                 dict(acao="editar", id=shared["id"], nome="ambiente-interno.md"),
                 dict(acao="editar", id=shared["id"]),
                 dict(acao="editar", id=shared["id"], base64=encoded(b"x" * (materials.MAX_FILE + 1))),
                 dict(acao="excluir", id="0" * 64),
                 dict(acao="mover", id=shared["id"])]
        for op in cases:
            with self.subTest(op=op.get("nome") or op["acao"]), self.assertRaises(ValueError):
                self.edit(anexos=[dict(acao="excluir", id=local["id"]), op])
            self.assertEqual(self.store.get(self.task), current)
            self.assertTrue(self.blob(shared).exists() and self.blob(local).exists())
        # Arquivo local de outra máquina não pode ser renomeado sem o conteúdo.
        self.blob(local).unlink()
        with self.assertRaisesRegex(ValueError, "indisponível nesta máquina"):
            self.edit(anexos=[dict(acao="editar", id=local["id"], nome="Outro nome.csv")])
        self.edit(anexos=[dict(acao="excluir", id=local["id"])])
        self.assertEqual([a["id"] for a in self.attachments()], [shared["id"]])

    def test_cli_edits_and_deletes_with_revision(self):
        config = self.private / "cfg.json"
        config.write_text(json.dumps({"tasks": dict(self.cfg, root=str(self.store.root))}), encoding="utf-8")
        parser = build_parser()
        cli = lambda *args: run(parser.parse_args(["--config", str(config), *args]))
        self.edit(anexos=[self.upload("roteiro.md", b"# Passos")])
        key = self.attachments()[0]["id"]
        with self.assertRaises(SystemExit), contextlib.redirect_stderr(io.StringIO()):
            parser.parse_args(["editar-anexo", self.task, key, "--excluir"])
        revision = self.store.get(self.task)["revision"]
        with self.assertRaisesRegex(ValueError, "--excluir sozinho"):
            cli("editar-anexo", self.task, key, "--excluir", "--nome", "x.md", "--revision", revision)
        source = self.private / "novo.md"
        source.write_bytes(b"# Novo")
        result = cli("editar-anexo", self.task, key, "--nome", "Roteiro.md", "--arquivo", str(source), "--revision", revision)
        self.assertEqual(result["anexos"][0]["nome"], "Roteiro.md")
        with self.assertRaises(Conflict):
            cli("editar-anexo", self.task, result["anexos"][0]["id"], "--excluir", "--revision", revision)
        cli("editar-anexo", self.task, result["anexos"][0]["id"], "--excluir", "--revision", self.store.get(self.task)["revision"])
        self.assertEqual(self.attachments(), [])

    def test_site_accept_list_matches_allowed_extensions(self):
        site = (Path(materials.__file__).parent / "site" / "app.js").read_text(encoding="utf-8")
        accept = site.split('const ATTACHMENT_ACCEPT = "', 1)[1].split('"', 1)[0]
        self.assertEqual(set(accept.split(",")), set(materials.EXTENSIONS))

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
