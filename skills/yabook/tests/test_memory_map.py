import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_runtime.core import Vault
from memory_runtime.map import map_data, html


class MapTest(unittest.TestCase):
    def test_same_ids_and_script_escape(self):
        with tempfile.TemporaryDirectory() as d:
            v=Vault(Path(d)/'vault');v.bootstrap('demo')
            record=dict(id='R1',title='Fonte <script>',scope=['Org','App'],content='</script><script>alert(1)</script>',state='hypothesis',application='Investigar')
            p=v.prepare([dict(collection='records',id='R1',value=record)],dict(verdict='add',reason='Contexto',utility='Investigar',application='Busca',evidence_status='Hipótese'),'test');v.apply(p['id'],p['approval_hash'])
            data=map_data(v)
            self.assertTrue(any(n['id']=='own:R1' for n in data['nodes']))
            self.assertTrue(any(l['target']=='own:R1' for l in data['links']))
            output=html(data)
            self.assertNotIn('</script><script>alert(1)',output)
            self.assertIn('\\u003c',output)


if __name__ == '__main__':unittest.main()
