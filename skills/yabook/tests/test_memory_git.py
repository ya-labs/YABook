import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from memory_runtime.core import Vault
from memory_runtime.gitstore import git, apply_and_publish, publish, inventory
from memory_runtime.sources import sync


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

    def machines(self, root):
        """Duas máquinas com clones da mesma base e um remoto comum."""
        seed = Vault(root / "seed"); seed.bootstrap("demo")
        git(seed.root, "init", "-b", "main")
        git(seed.root, "add", "-A"); git(seed.root, "-c", "user.name=D", "-c", "user.email=d@x.invalid", "commit", "-m", "docs: base")
        git(root, "clone", "--bare", "-q", str(seed.root), str(root / "remote.git"))
        vaults = []
        for name in ("a", "b"):
            git(root, "clone", "-q", str(root / "remote.git"), str(root / name))
            git(root / name, "config", "user.name", name); git(root / name, "config", "user.email", name + "@x.invalid")
            vaults.append(Vault(root / name))
        return vaults

    def learn(self, vault, identifier, content):
        assessment = dict(verdict="add", reason="r", utility="u", application="a", evidence_status="e")
        entry = dict(id=identifier, title="Registro " + identifier, scope=["Demo"], content=content,
                     application="Investigar", state="hypothesis")
        p = vault.prepare([dict(collection="records", id=identifier, value=entry)], assessment, "test")
        return apply_and_publish(vault, p["id"], p["approval_hash"])["publication"]

    def test_sync_reapplies_local_commits_over_other_machine(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = self.machines(Path(d))
            self.assertEqual(self.learn(a, "RA", "da máquina A")["status"], "published")
            self.assertEqual(self.learn(b, "RB", "da máquina B")["status"], "pending_push")
            result = sync(b)
            publication = result["publication"]
            self.assertEqual((publication["reconcile"]["status"], publication["status"]), ("rebased", "published"))
            self.assertFalse((b.local / "publication.json").exists())
            index = (b.root / "views/MEMORY.md").read_text()
            self.assertIn("Registro RA", index); self.assertIn("Registro RB", index)
            self.assertEqual(sync(a)["own"]["status"], "updated")
            self.assertIn("Registro RB", (a.root / "views/MEMORY.md").read_text())

    def test_sync_keeps_local_base_on_record_conflict(self):
        with tempfile.TemporaryDirectory() as d:
            a, b = self.machines(Path(d))
            self.learn(a, "R1", "versão A")
            self.learn(b, "R1", "versão B")
            head = git(b.root, "rev-parse", "HEAD").stdout.strip()
            result = sync(b)
            self.assertEqual((result["own"]["status"], result["own"]["records"]), ("conflict", ["R1"]))
            self.assertEqual(git(b.root, "rev-parse", "HEAD").stdout.strip(), head)
            self.assertIn("versão B", (b.root / "records/R1.json").read_text())

    def test_inventory_reports_missing_and_sensitive(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(inventory("codex",Path(d)/"missing")["accessible"])
            (Path(d)/"memory.md").write_text("ghp_"+"a"*40)
            result=inventory("claude",d)
            self.assertEqual(result["files"][0]["status"],"sensitive")
            self.assertEqual(result["files"][0]["excerpt"],"")


if __name__ == "__main__": unittest.main()
