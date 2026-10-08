import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault
from memory_runtime.retrieval import retrieve
from memory_runtime.search import search
from memory_runtime.views import session_context

EVIDENCE = [dict(type="code", ref="fixture", level="static")]


class RelevanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.v = Vault(Path(self.tmp.name) / "v")
        self.v.bootstrap("demo")
        changes = [dict(collection="groups", id="P", value=dict(title="Projeto", scope=["Org", "App"], kind="project")),
                   dict(collection="groups", id="F", value=dict(title="Ferramentas", scope=["Pessoa"], kind="topic"))]
        members = []
        for i in range(12):
            identifier = "K%d" % i
            members.append(identifier)
            changes.append(dict(collection="records", id=identifier, value=dict(
                title="Checklist do supervisor %d" % i, scope=["Org", "App"], kind="knowledge", state="confirmed",
                content="Checklist do supervisor não chega quando o envio %d falha. " % i + "detalhe " * 40,
                application="Investigar envio", evidence=EVIDENCE, keywords=["checklist", "supervisor"] * 10)))
        changes.append(dict(collection="groups", id="T", value=dict(
            title="Checklist do supervisor", scope=["Org", "App"], kind="topic", parent="P", members=members,
            keywords=["checklist", "supervisor"] * 20, summary="Envio e pendência do checklist.",
            summary_sources={m: 1 for m in members})))
        assessment = dict(verdict="add", reason="teste", utility="teste", application="teste", evidence_status="teste")
        p = self.v.prepare(changes, assessment, "test")
        self.v.apply(p["id"], p["approval_hash"])

    def test_common_words_do_not_match(self):
        self.assertEqual(search(self.v, "não está pra isso")["results"], [])

    def test_knowledge_fills_budget_before_topics(self):
        result = retrieve(self.v, "checklist não está chegando pro supervisor", [["Org"]], budget=4500)
        self.assertGreaterEqual(len(result["knowledge"]), 3)
        self.assertLessEqual(len(json.dumps(result, ensure_ascii=False)), 4500)
        self.assertEqual(list(result).index("knowledge") < list(result).index("topics"), True)
        for topic in result["topics"]:
            self.assertNotIn("members", topic); self.assertNotIn("keywords", topic)

    def test_symptom_trigger_finds_technical_record(self):
        changes = [dict(collection="records", id="S1", value=dict(
            title="PRV_CODIGO_ERP divergente da visita local", scope=["Org", "App"], kind="knowledge",
            state="confirmed", content="Visita ERP 10 e local 12 não se vinculam.", application="Diagnóstico",
            evidence=EVIDENCE, triggers=["checklist sumiu da tela do gestor"]))]
        assessment = dict(verdict="add", reason="t", utility="t", application="t", evidence_status="t")
        p = self.v.prepare(changes, assessment, "test"); self.v.apply(p["id"], p["approval_hash"])
        ids = [r["id"] for r in search(self.v, "o checklist sumiu da tela do gestor", level="knowledge")["results"]]
        self.assertEqual(ids[0], "S1")

    def test_session_context_lists_project_topics_first(self):
        context = session_context(self.v, ["Org", "App"], budget=4200)
        order = [t["id"] for t in context["topics"]]
        self.assertLess(max(order.index("P"), order.index("T")), order.index("F"))
        self.assertTrue(all("references" not in t for t in context["topics"] + context["index"]))


if __name__ == "__main__":
    unittest.main()
