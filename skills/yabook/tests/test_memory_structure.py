import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault, read_json, write_json
from memory_runtime.map import map_data
from memory_runtime.retrieval import retrieve
from memory_runtime.search import search
from memory_runtime.sources import sanitize, source_add
from memory_runtime.views import session_context
import yabook_hook as hook


class StructureTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.v = Vault(Path(self.temp.name) / "vault")
        self.v.bootstrap("demo")
        self.assessment = dict(verdict="add", reason="Reutilizar descoberta", utility="Investigação",
                               application="Falhas de sincronização", evidence_status="Fixture confirmada")
        scope = ["Org", "demo-app"]
        self.items = {
            "P": ("groups", dict(title="Demo App", scope=scope, kind="project", members=[])),
            "T": ("groups", dict(title="Sincronização do supervisor", scope=scope + ["sync"], kind="topic",
                                  parent="P", project_id="P", members=["R", "E"], keywords=["checklist"],
                                  aliases=["não está chegando"], summary="Uma operação de exemplo recebe os dados.", summary_sources={"R": 1, "E": 1})),
            "R": ("records", dict(title="Responsabilidade do exemplo-sync.p", scope=scope + ["sync"],
                                   kind="knowledge", content="exemplo-sync.p trata o recebimento",
                                   application="Investigar falha", state="confirmed", evidence=[dict(type="code", ref="fixture:code", level="static")], episodes=["E"])),
            "E": ("episodes", dict(title="Investigação do checklist", scope=scope + ["sync"],
                                    objective="Localizar o recebimento", context="Checklist não apareceu",
                                    actions=["Rastrear transporte e fonte"], outcome="Operação identificada",
                                    validation=["Verificação de código; runtime pendente"], evidence=[dict(type="commit", ref="fixture:commit", level="static")],
                                    learnings=["R"], state="confirmed")),
            "U": ("groups", dict(title="Navegação", scope=scope + ["navigation"], kind="topic", parent="P", members=["N"])),
            "N": ("records", dict(title="Rota de outra funcionalidade", scope=scope + ["navigation"], content="Tela de relatórios", application="Navegar", state="hypothesis")),
            "PF": ("records", dict(title="Perfil", scope=["Pessoa"], kind="profile", content="Desenvolve em português", application="Colaborar", state="confirmed", evidence=[dict(type="conversation", ref="fixture:user", level="statement")])),
            "PR": ("records", dict(title="Preferência geral", scope=["Pessoa"], kind="preference", authority="explicit", activation="always", content="Explique validações pendentes", application="Relatórios", state="confirmed", evidence=[dict(type="conversation", ref="fixture:user", level="statement")])),
            "PC": ("records", dict(title="Preferência de investigação", scope=["Pessoa"], kind="preference", authority="explicit", activation="conditional", content="Comece rastreando o recebimento", application="Falha de checklist", triggers=["checklist"], state="confirmed", evidence=[dict(type="conversation", ref="fixture:user", level="statement")])),
        }
        self.save(self.items)

    def save(self, items):
        changes = [dict(collection=c, id=i, value=v) for i, (c, v) in items.items()]
        p = self.v.prepare(changes, self.assessment, "fixture")
        return self.v.apply(p["id"], p["approval_hash"])

    def test_bootstrap_context_includes_person_and_project_under_valid_json_budget(self):
        context = session_context(self.v, ["Org", "demo-app"], budget=4000)
        self.assertEqual([e["id"] for e in context["profile"]], ["PF"])
        self.assertEqual([e["id"] for e in context["preferences"]], ["PR"])
        self.assertIn("PC", [e["id"] for e in context["conditional"]])
        self.assertNotIn("content", next(e for e in context["conditional"] if e["id"] == "PC"))
        self.assertIn("T", [e["id"] for e in context["topics"]])
        small = session_context(self.v, ["Org", "demo-app"], budget=512)
        self.assertLessEqual(len(json.dumps(small, ensure_ascii=False)), 512)
        self.assertTrue(small["truncated"])

    def test_alias_routes_to_topic_and_knowledge_without_sibling_or_experience(self):
        result = retrieve(self.v, "não está chegando", [["Org", "demo-app"]])
        self.assertIn("R", [e["id"] for e in result["knowledge"]])
        self.assertNotIn("N", [e["id"] for e in result["knowledge"]])
        self.assertEqual(result["experiences"], [])
        self.assertNotIn("fixture:code", json.dumps(result))

    def test_experience_and_evidence_are_explicit_levels(self):
        result = retrieve(self.v, "checklist", [["Org"]], experiences=True, evidence=True)
        self.assertEqual([e["id"] for e in result["experiences"]], ["E"])
        self.assertIn("fixture:commit", json.dumps(result))
        self.assertLessEqual(len(json.dumps(result, ensure_ascii=False)), 6000)

    def test_exact_source_name_also_locates_its_topic(self):
        result = retrieve(self.v, "exemplo-sync.p", [["Org"]])
        self.assertIn("T", [e["id"] for e in result["topics"]])
        self.assertNotIn("N", [e["id"] for e in result["knowledge"]])

    def test_type_level_and_trigger_search_filters(self):
        result = search(self.v, "checklist", kinds=["preference"], level="knowledge")
        self.assertEqual([e["id"] for e in result["results"]], ["PC"])
        self.assertTrue(all(e["collection"] == "groups" for e in search(self.v, "checklist", level="index")["results"]))

    def test_views_invalidate_summaries_and_keep_unrelated_topic_unchanged(self):
        unrelated = self.v.root / "views/topics/U.md"
        before = (unrelated.read_bytes(), unrelated.stat().st_mtime_ns)
        value = dict(self.items["R"][1], content="Conhecimento corrigido")
        receipt = self.save({"R": ("records", value)})
        self.assertEqual((unrelated.read_bytes(), unrelated.stat().st_mtime_ns), before)
        self.assertNotIn("views/topics/U.md", receipt["paths"])
        self.assertIn("views/topics/T.md", receipt["paths"])
        self.assertIn("precisa ser revisto", (self.v.root / "views/topics/T.md").read_text())
        self.assertNotIn("Uma operação de exemplo", (self.v.root / "views/topics/T.md").read_text())

    def test_parent_cycles_and_cross_project_references_are_rejected(self):
        for value in (dict(self.items["P"][1], parent="T"), dict(self.items["R"][1], project_id="missing")):
            with self.assertRaises(ValueError):
                self.save({"P" if value.get("parent") else "R": ("groups" if value.get("parent") else "records", value)})

    def test_inferred_preference_cannot_become_permanent_rule(self):
        with self.assertRaises(ValueError):
            self.save({"PR": ("records", dict(self.items["PR"][1], authority="inferred"))})

    def test_legacy_read_does_not_migrate_metadata(self):
        metadata = read_json(self.v.root / "memory.json")
        metadata["schema_version"] = 1; write_json(self.v.root / "memory.json", metadata)
        before = (self.v.root / "memory.json").read_bytes()
        self.v.bootstrap("demo"); session_context(self.v); retrieve(self.v, "checklist")
        self.assertEqual((self.v.root / "memory.json").read_bytes(), before)
        value = dict(self.items["PR"][1], content="Preferência corrigida")
        p = self.v.prepare([dict(collection="records", id="PR", value=value)], self.assessment, "fixture")
        self.assertEqual(read_json(self.v.root / "memory.json")["schema_version"], 1)
        self.assertEqual(p["result"]["metadata"]["schema_version"], 2)

    def test_documented_template_produces_reviewable_proposal(self):
        template = Path(__file__).resolve().parents[1] / "templates/memory-proposal-v2.json"
        payload = read_json(template)
        vault = Vault(Path(self.temp.name) / "template-vault"); vault.bootstrap("demo")
        proposal = vault.prepare(payload["changes"], payload["assessment"], "fixture")
        self.assertIn("views/topics/T.md", proposal["derived_views"])
        self.assertEqual(list(vault.entries()), [])
        vault.apply(proposal["id"], proposal["approval_hash"])
        self.assertTrue((vault.root / "views/memory_summary.md").is_file())

    def test_derived_view_tampering_blocks_approval(self):
        value = dict(self.items["R"][1], content="Nova descoberta")
        proposal = self.v.prepare([dict(collection="records", id="R", value=value)], self.assessment, "fixture")
        proposal["derived_views"] = []
        write_json(self.v.local / "proposals" / (proposal["id"] + ".json"), proposal)
        with self.assertRaises(ValueError): self.v.apply(proposal["id"], proposal["approval_hash"])

    def test_filter_invalidates_ancestor_summary(self):
        entries = [dict(id="A", scope=["Org"], members=["B"], summary="Conteúdo pessoal", summary_sources={"B": 1}),
                   dict(id="B", scope=["Org"], members=["private"], summary="Conteúdo pessoal", summary_sources={"private": 1}),
                   dict(id="private", scope=["Pessoa"])]
        result = sanitize(entries, [["Org"]], [])
        self.assertTrue(all("summary" not in e for e in result))

    def test_external_personal_preferences_are_not_used(self):
        source_add(self.v, dict(id="colleague", remote="https://github.com/demo/memory.git", includes=[["Pessoa"], ["Org"]]))
        external = dict(self.items["PR"][1], id="FOREIGN", revision=1, collection="records")
        write_json(self.v.local / "sources/colleague/receipt.json", dict(vault_id="external", revision="abc", entries=[external]))
        result = session_context(self.v, ["Org"])
        self.assertNotIn("FOREIGN", json.dumps(result))

    def test_map_exposes_topics_types_and_experiences(self):
        data = map_data(self.v)
        nodes = {n["id"]: n for n in data["nodes"]}
        self.assertEqual(nodes["own:E"]["kind"], "episodes")
        self.assertEqual(nodes["own:PR"]["entry"]["kind"], "preference")
        self.assertIn(dict(source="own:P", target="own:T", type="contains"), data["links"])

    def test_hooks_inject_profile_and_find_topic_automatically(self):
        root = self.temp.name
        config = Path(root) / "config.json"
        write_json(config, dict(memory_root=str(self.v.root), projects={root: ["Org", "demo-app"]}))
        environment = dict(YABOOK_CONFIG=str(config), YABOOK_STATE=str(Path(root) / "sessions"))
        event = dict(session_id="demo-session", cwd=root)
        with patch.dict(os.environ, environment), patch.object(hook, "git", return_value=""):
            startup = hook.run(dict(event, hook_event_name="SessionStart", source="startup"))
            self.assertIn("Desenvolve em português", startup["hookSpecificOutput"]["additionalContext"])
            task = hook.run(dict(event, hook_event_name="UserPromptSubmit", prompt="checklist não está chegando"))
            self.assertIn("exemplo-sync.p", task["hookSpecificOutput"]["additionalContext"])
            self.assertNotIn("fixture:commit", task["hookSpecificOutput"]["additionalContext"])


if __name__ == "__main__": unittest.main()
