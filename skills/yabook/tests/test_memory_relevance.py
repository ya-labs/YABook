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

    def test_single_shared_term_is_not_relevant(self):
        self.assertEqual(search(self.v, "exportação de relatórios em excel do supervisor")["results"], [])
        self.assertTrue(search(self.v, "envio do checklist do supervisor")["results"])

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

    def test_session_start_keeps_every_permanent_preference_and_filters_machine(self):
        statement = [dict(type="conversation", ref="fixture", level="statement")]
        personal = dict(scope=["Pessoa"], state="confirmed", evidence=statement)
        changes = [dict(collection="records", id="PW", value=dict(personal, title="Ambiente Windows", kind="profile",
                        platform="windows", content="C:\\Users\\x " * 200, application="Comandos"))]
        changes.append(dict(collection="records", id="PD", value=dict(personal, title="Perfil", kind="profile",
                            content="Desenvolvedor " * 200, application="Contexto")))
        for i in range(7):
            changes.append(dict(collection="records", id="PR%d" % i, value=dict(personal, title="Preferência %d" % i,
                                kind="preference", authority="explicit", activation="always",
                                content="Regra permanente %d " % i * 30, application="Sempre")))
        assessment = dict(verdict="add", reason="t", utility="t", application="t", evidence_status="t")
        p = self.v.prepare(changes, assessment, "test"); self.v.apply(p["id"], p["approval_hash"])
        context = session_context(self.v, ["Org", "App"], budget=4200, platform="linux")
        self.assertEqual(len(context["preferences"]), 7)
        self.assertEqual([e["id"] for e in context["profile"]], ["PD"])
        self.assertLessEqual(len(context["profile"][0]["content"]), 361)
        self.assertIn("PW", [e["id"] for e in session_context(self.v, ["Org", "App"], platform="windows")["profile"]])

    def test_retrieve_delivers_matches_without_alphabetical_filler(self):
        changes = [dict(collection="entities", id="ENT", value=dict(title="exemplo-envio.p", scope=["Org", "App"],
                        kind="fonte", aliases=["exemplo-envio.p"], evidence=EVIDENCE))]
        base = dict(scope=["Org", "App"], kind="knowledge", state="confirmed", evidence=EVIDENCE, application="Investigar")
        changes.append(dict(collection="records", id="CITA", value=dict(base, title="Fila do envio",
                            content="Fila grava antes do envio.", entities=["ENT"], triggers=["fila do envio"],
                            relations=[dict(target="VIZ", type="related")])))
        changes.append(dict(collection="records", id="VIZ", value=dict(base, title="Reenvio manual",
                            content="Reenvio depende da fila.", triggers=["reenvio manual"])))
        changes.append(dict(collection="records", id="AAA", value=dict(base, title="Agro modal sem relação",
                            content="Modal de busca.", triggers=["modal de busca"])))
        assessment = dict(verdict="add", reason="t", utility="t", application="t", evidence_status="t")
        p = self.v.prepare(changes, assessment, "test"); self.v.apply(p["id"], p["approval_hash"])
        ids = [k["id"] for k in retrieve(self.v, "exemplo-envio.p", [["Org"]], budget=3500, excerpt=300)["knowledge"]]
        self.assertEqual(ids[:2], ["CITA", "VIZ"])  # registro que cita a entidade e seu vizinho direto
        self.assertNotIn("ENT", ids); self.assertNotIn("AAA", ids)

    def test_session_context_lists_project_topics_first(self):
        context = session_context(self.v, ["Org", "App"], budget=4200)
        order = [t["id"] for t in context["topics"]]
        self.assertLess(max(order.index("P"), order.index("T")), order.index("F"))
        self.assertTrue(all("references" not in t for t in context["topics"] + context["index"]))


if __name__ == "__main__":
    unittest.main()
