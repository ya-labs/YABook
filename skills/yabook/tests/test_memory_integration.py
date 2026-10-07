import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from memory_runtime.core import Vault, digest, write_json
from memory_runtime.gitstore import git, init_apply, publish
from memory_runtime.sources import refresh, all_entries


class IntegrationTest(unittest.TestCase):
    def fixture(self,d):
        v=Vault(Path(d)/"vault");v.bootstrap("demo")
        git(v.root,"init","-b","main");git(v.root,"config","user.name","Demo");git(v.root,"config","user.email","demo@example.invalid")
        git(v.root,"add","memory.json",".gitignore");git(v.root,"commit","-m","docs: base")
        remote=Path(d)/"remote.git";git(Path(d),"init","--bare",str(remote));git(v.root,"remote","add","origin",str(remote))
        a=dict(verdict="add",reason="Contexto",utility="Investigar",application="Investigar",evidence_status="Hipótese")
        changes=[dict(collection="records",id="R1",value=dict(title="Fonte",scope=["Org"],content="Pista",application="Investigar",state="hypothesis"))]
        p=v.prepare(changes,a,"test")
        return v,p,dict(changes=changes,assessment=a),remote

    def test_journal_blocks_readers_and_recovery_keeps_publication(self):
        with tempfile.TemporaryDirectory() as d:
            v,p,_,_=self.fixture(d)
            write_json(v.local/"transaction.json",p)
            with self.assertRaises(ValueError):v.snapshot()
            v.recover()
            self.assertTrue((v.local/"publication.json").exists())
            self.assertEqual(publish(v)["status"],"published")
            self.assertEqual(next(v.entries())["revision"],1)

    def test_changed_approved_file_cannot_be_committed_on_retry(self):
        with tempfile.TemporaryDirectory() as d:
            v,p,_,_=self.fixture(d);v.apply(p["id"],p["approval_hash"])
            path=v.path("records","R1");entry=json.loads(path.read_text());entry["content"]="Alterado";write_json(path,entry)
            with self.assertRaises(ValueError):publish(v)
            self.assertFalse(git(v.root,"diff","--cached","--name-only").stdout.strip())

    def test_reinitialization_does_not_duplicate_identical_knowledge(self):
        with tempfile.TemporaryDirectory() as d:
            v,p,curated,_=self.fixture(d);v.apply(p["id"],p["approval_hash"]);publish(v)
            plan=dict(owner="demo",repository="demo/YABook-memory-demo",root=str(v.root),existing=True,
                      inventory=dict(agent="codex",files=[]),curated_hash=digest(curated))
            plan["approval_hash"]=digest(plan)
            def remote_run(*args,**kwargs):
                body={"login":"demo"} if args[2]=="user" else {"private":True}
                return subprocess.CompletedProcess(args,0,json.dumps(body),"")
            actual_git=git
            def mapped_git(root,*args,**kwargs):
                if args==("remote","get-url","origin"):
                    return subprocess.CompletedProcess(args,0,"https://github.com/demo/YABook-memory-demo.git\n","")
                return actual_git(root,*args,**kwargs)
            with patch("memory_runtime.gitstore.run",side_effect=lambda *args,**kwargs: remote_run(*args,**kwargs) if args[0]=="gh" else subprocess.run(args,capture_output=True,text=True)),patch("memory_runtime.gitstore.git",side_effect=mapped_git):
                result=init_apply(plan,plan["approval_hash"],curated,Path(d)/"config.json")
            self.assertEqual(result["status"],"unchanged")
            self.assertEqual(next(v.entries())["revision"],1)

    def test_bare_source_refresh_reads_data_and_tracks_new_commit(self):
        with tempfile.TemporaryDirectory() as d:
            source,p,_,remote=self.fixture(d);source.apply(p["id"],p["approval_hash"]);publish(source)
            own=Vault(Path(d)/"own");own.bootstrap("other")
            write_json(own.local/"sources.json",{"colleague":dict(remote=str(remote),branch="main",includes=[["Org"]],refresh_seconds=60)})
            report=refresh(own,force=True)
            self.assertEqual(report[0]["added"],["R1"])
            self.assertEqual(all_entries(own)[0]["content"],"Pista")
            entry=dict(next(source.entries()),content="Pista nova",application="Verificar fonte atual")
            p=source.prepare([dict(collection="records",id="R1",value=entry)],dict(verdict="update",reason="Mudou",utility="Investigar",application="Consulta",evidence_status="Hipótese"),"test")
            source.apply(p["id"],p["approval_hash"]);publish(source)
            self.assertEqual(refresh(own,force=True)[0]["updated"],["R1"])
            self.assertEqual(all_entries(own)[0]["content"],"Pista nova")
