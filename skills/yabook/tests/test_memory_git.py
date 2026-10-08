import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault
from memory_runtime.gitstore import git, apply_and_publish, publish, inventory


class GitMemoryTest(unittest.TestCase):
    def test_local_remote_and_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); v=Vault(root / "vault"); v.bootstrap("demo")
            git(v.root,"init","-b","main"); git(v.root,"config","user.name","Demo"); git(v.root,"config","user.email","demo@example.invalid")
            git(v.root,"add","memory.json",".gitignore"); git(v.root,"commit","-m","docs: base")
            git(v.root,"remote","add","origin",str(root / "remote.git"))
            assessment=dict(verdict="add", reason="Contexto", utility="Investigar", application="Recebimento", evidence_status="Hipótese")
            entry=dict(id="R1",title="Retorno",scope=["Demo"],content="Pista",application="Investigar",state="hypothesis")
            p=v.prepare([dict(collection="records",id="R1",value=entry)],assessment,"test")
            result=apply_and_publish(v,p["id"],p["approval_hash"])
            self.assertEqual(result["publication"]["status"],"pending_push")
            commit=result["publication"]["commit"]
            git(root,"init","--bare",str(root / "remote.git"))
            self.assertEqual(publish(v)["status"],"published")
            self.assertEqual(git(v.root,"rev-parse","HEAD").stdout.strip(),commit)
            self.assertFalse(git(v.root,"status","--porcelain").stdout.strip())

    def test_inventory_reports_missing_and_sensitive(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(inventory("codex",Path(d)/"missing")["accessible"])
            (Path(d)/"memory.md").write_text("ghp_"+"a"*40)
            result=inventory("claude",d)
            self.assertEqual(result["files"][0]["status"],"sensitive")
            self.assertEqual(result["files"][0]["excerpt"],"")


if __name__ == "__main__": unittest.main()
