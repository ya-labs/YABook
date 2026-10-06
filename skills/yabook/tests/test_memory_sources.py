import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_runtime.core import Vault, write_json
from memory_runtime.sources import source_add, external_entries, sanitize, all_entries


class SourcesTest(unittest.TestCase):
    def test_scope_change_and_cross_links(self):
        with tempfile.TemporaryDirectory() as d:
            v=Vault(Path(d)/"vault");v.bootstrap("demo")
            source=dict(id="marco",remote="https://github.com/demo/YABook-memory-demo.git",includes=[["Org"]],excludes=[["Org","Pessoa"]])
            source_add(v,source)
            entries=[dict(id="R1",title="App",scope=["Org","App"],state="confirmed",relations=[dict(type="related",target="P1")]),
                     dict(id="P1",title="Pessoal",scope=["Org","Pessoa"],state="confirmed"),
                     dict(id="G1",title="Grupo",scope=["Org"],members=["R1","P1"],summary="Dado pessoal")]
            write_json(v.local/"sources/marco/receipt.json",dict(vault_id="external",revision="abc",entries=entries))
            result=list(external_entries(v))
            self.assertEqual({e['id'] for e in result},{"R1","G1"})
            self.assertEqual(result[0]['relations'],[])
            self.assertNotIn('summary',result[1])
            source['includes']=[["Outra"]];source_add(v,source)
            self.assertEqual(list(external_entries(v)),[])

    def test_origin_loop_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as d:
            v=Vault(Path(d)/"vault");v.bootstrap("demo")
            record=dict(id="R1",title="App",scope=["Org"],content="Pista",application="Investigar",state="hypothesis")
            a=dict(verdict="add",reason="Útil",utility="Contexto",application="Investigar",evidence_status="Hipótese")
            p=v.prepare([dict(collection="records",id="R1",value=record)],a,"test");v.apply(p['id'],p['approval_hash'])
            source_add(v,dict(id="marco",remote="https://github.com/demo/memory.git",includes=[["Org"]]))
            own=next(v.entries())
            write_json(v.local/"sources/marco/receipt.json",dict(vault_id="external",revision="abc",entries=[own]))
            self.assertEqual(len(all_entries(v)),1)


if __name__ == "__main__":unittest.main()
