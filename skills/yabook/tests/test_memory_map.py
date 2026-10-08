import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_runtime.core import Vault
from memory_runtime.map import map_data, html, hierarchy


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

    def test_tree_prefers_explicit_parent_and_topic_over_project(self):
        nodes = [
            dict(id="scope:org", kind="scope", scope=["Org"], title="Org"),
            dict(id="scope:app", kind="scope", scope=["Org", "App"], title="App"),
            dict(id="own:project", kind="groups", entry=dict(id="project", collection="groups", kind="project", scope=["Org", "App"])),
            dict(id="own:topic", kind="groups", entry=dict(id="topic", collection="groups", kind="topic", scope=["Org", "App"], parent="project")),
            dict(id="own:record", kind="records", entry=dict(id="record", collection="records", scope=["Org", "App"]))]
        pairs = [("scope:org", "scope:app"), ("scope:app", "own:project"), ("scope:app", "own:topic"),
                 ("scope:app", "own:record"), ("own:project", "own:topic"),
                 ("own:project", "own:record"), ("own:topic", "own:record")]
        links = [dict(source=a,target=b,type="contains") for a,b in pairs]
        hierarchy(nodes, links)
        parents = {n["id"]:n["tree_parent"] for n in nodes}
        self.assertEqual(parents["own:topic"], "own:project")
        self.assertEqual(parents["own:record"], "own:topic")
        self.assertEqual(parents["scope:app"], "scope:org")

    def test_tree_avoids_cycles_and_cross_location_memberships(self):
        nodes = [dict(id="s",kind="scope",scope=["Other"],title="Other"),
                 dict(id="a",kind="groups",entry=dict(id="a",collection="groups",scope=["Org"])),
                 dict(id="b",kind="groups",entry=dict(id="b",collection="groups",scope=["Org"])),
                 dict(id="r",kind="records",entry=dict(id="r",collection="records",scope=["Other"]))]
        links = [dict(source=a,target=b,type="contains") for a,b in [("a","b"),("b","a"),("a","r"),("s","r")]]
        hierarchy(nodes,links)
        parents = {n["id"]:n["tree_parent"] for n in nodes}
        self.assertEqual(parents["r"], "s")
        for n in nodes:
            seen=set();cursor=n["id"]
            while cursor is not None:
                self.assertNotIn(cursor,seen)
                seen.add(cursor);cursor=parents[cursor]


if __name__ == '__main__':unittest.main()
