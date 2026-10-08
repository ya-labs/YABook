import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_runtime.core import Vault, write_json
from memory_runtime.map import map_data, html, hierarchy, query_map


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

    def test_map_dates_use_canonical_history_without_changing_records(self):
        with tempfile.TemporaryDirectory() as d:
            v=Vault(Path(d)/'vault');v.bootstrap('demo')
            record=dict(id='dated',title='Memória com histórico',scope=['Org'],content='Fato',state='hypothesis',application='Consulta',last_verified='2026-09-28')
            proposal=v.prepare([dict(collection='records',id='dated',value=record)],dict(verdict='add',reason='Contexto',utility='Consulta',application='Busca',evidence_status='Confirmado'),'test')
            v.apply(proposal['id'],proposal['approval_hash'])
            history=v.root/'history'
            for path in history.glob('*.json'):path.unlink()
            write_json(history/'creation.json',dict(created_at='2026-10-01T12:00:00Z',changes=[dict(collection='records',id='dated',before=None,after=record)]))
            write_json(history/'update.json',dict(created_at='2026-10-08T12:00:00Z',changes=[dict(collection='records',id='dated',before=record,after=record)]))
            before=v.snapshot()
            node=next(n for n in map_data(v)['nodes'] if n['id']=='own:dated')
            self.assertEqual(node['dates'],dict(created_at='2026-10-01T12:00:00Z',updated_at='2026-10-08T12:00:00Z',last_verified='2026-09-28'))
            self.assertEqual(v.snapshot(),before)
            for path in history.glob('*.json'):path.unlink()
            node=next(n for n in map_data(v)['nodes'] if n['id']=='own:dated')
            self.assertEqual(node['dates'],dict(last_verified='2026-09-28'))

    def test_manual_query_uses_runtime_scope_and_does_not_write_state(self):
        from test_memory_search import SearchTest
        fixture=SearchTest();fixture.setUp()
        try:
            vault=fixture.v
            before={str(p.relative_to(vault.root)):p.read_bytes() for p in vault.root.rglob('*') if p.is_file()}
            result=query_map(vault,'checklist supervisor',[['Org']])
            self.assertTrue(result['manual'])
            self.assertEqual([hit['id'] for hit in result['results']],['R1'])
            self.assertTrue(result['results'][0]['explanation']['lexical'])
            self.assertEqual(before,{str(p.relative_to(vault.root)):p.read_bytes() for p in vault.root.rglob('*') if p.is_file()})
            for query in ['', '   ', 'a'*1001]:
                with self.assertRaises(ValueError):query_map(vault,query)
        finally:fixture.doCleanups()

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
