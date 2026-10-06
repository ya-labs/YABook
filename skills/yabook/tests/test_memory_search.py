import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_runtime.core import Vault, read_json
from memory_runtime.search import search, import_vectors


class SearchTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.v=Vault(Path(self.tmp.name)/"vault");self.v.bootstrap("demo")
        a=dict(verdict="add",reason="Útil",utility="Investigar",application="Investigar",evidence_status="Hipótese")
        records=[dict(id="R1",title="Checklist supervisor",scope=["Org","App"],content="lnws-pv200c2 recebe checklist",application="Investigar recebimento",state="hypothesis"),
                 dict(id="R2",title="Checklist pessoal",scope=["Pessoa"],content="checklist pessoal",application="Organização pessoal",state="hypothesis")]
        p=self.v.prepare([dict(collection="records",id=r['id'],value=r) for r in records],a,"test");self.v.apply(p['id'],p['approval_hash'])

    def test_exact_name_and_scope(self):
        result=search(self.v,"lnws-pv200c2",[["Org"]])
        self.assertEqual(result['results'][0]['id'],"R1")
        self.assertNotIn("R2",[e['id'] for e in result['results']])

    def test_optional_vectors_and_invalidated_cache(self):
        with patch('memory_runtime.search.embed',side_effect=lambda texts,*args:[[1.,0.] for t in texts]):
            result=search(self.v,"recebimento",[["Org"]],model="demo")
            self.assertEqual(result['mode'],"hybrid")
        package=dict(schema_version=1,pipeline="yabook-text-v1",vectors=read_json(self.v.local/'vectors.json'))
        p=self.v.prepare([dict(collection="records",id="R1",value=dict(next(self.v.entries()),content="Outro conhecimento"))],dict(verdict="update",reason="Correção",utility="Atualizar",application="Investigar",evidence_status="Hipótese"),"test")
        self.v.apply(p['id'],p['approval_hash'])
        self.assertEqual(import_vectors(self.v,package)['accepted'],0)

    def test_provider_unavailable_falls_back(self):
        with patch('memory_runtime.search.embed',side_effect=OSError("offline")):
            result=search(self.v,"checklist",model="demo")
        self.assertEqual(result['mode'],"textual");self.assertTrue(result['degraded'])

    def test_budget(self):
        result=search(self.v,"checklist",budget=512)
        self.assertLessEqual(result['characters'],512)


if __name__ == '__main__': unittest.main()
