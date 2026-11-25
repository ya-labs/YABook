import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import yabook_diff
from diff_runtime import explain, store


class DiffExplainTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        home = Path(self.tmp.name)
        self.root = home / "projeto"; self.root.mkdir()
        self.env = patch.dict(os.environ, YABOOK_CONFIG=str(home / "config.json"), YABOOK_DIFFS=str(home / "diffs"))
        self.env.start(); self.addCleanup(self.env.stop)
        self.session = store.Session(home / "diffs", self.root, "s1", "claude")
        source = self.root / "tela.p"
        source.write_bytes("\n".join(["a", "b", "c", "d", "e", "f", "g", "h"]).encode("latin-1") + b"\n")
        self.session.record(source, source)
        # b vira B, c some (blocos adjacentes se unem); g ganha linha nova depois (bloco separado).
        source.write_bytes("\n".join(["a", "B", "d", "e", "f", "g", "ação", "h"]).encode("latin-1") + b"\n")
        removed = self.root / "velho.txt"; removed.write_text("x\ny\n")
        self.session.record(removed, removed); removed.unlink()
        self.data = store.read_manifest(self.session.folder)

    def test_blocks_merge_neighbours_and_use_one_based_ranges(self):
        found = explain.blocks(self.session.folder, self.data)
        self.assertEqual([b["id"] for b in found], ["b1", "b2", "b3"])
        first, second, gone = found
        self.assertEqual((first["antes"], first["depois"], first["removidas"], first["adicionadas"]),
                         ([2, 2], [2, 1], ["b", "c"], ["B"]))
        self.assertEqual((second["antes"], second["depois"], second["adicionadas"]), ([8, 0], [7, 1], ["ação"]))
        self.assertEqual((gone["estado"], gone["depois"][1], gone["removidas"]), ("removido", 0, ["x", "y"]))
        self.assertEqual([b["id"] for b in explain.blocks(self.session.folder, self.data, "velho.txt")], ["b1"])

    def test_save_validates_ids_and_records_signature(self):
        with self.assertRaises(ValueError):
            explain.save(self.session.folder, self.data, {"b9": "não existe"})
        target, payload = explain.save(self.session.folder, self.data,
                                       explain.parse(json.dumps({"blocos": [{"id": "b1", "texto": "Troca o nome."}]})))
        saved = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(saved["blocos"][0]["texto"], "Troca o nome.")
        self.assertEqual(saved["blocos"][0]["assinatura"], explain.digest(self.root / "tela.p"))
        self.assertEqual(payload["pendentes"], ["b2", "b3"])
        self.assertEqual(explain.parse('{"b2": "Linha nova."}'), {"b2": "Linha nova."})
        for invalid in ('[]', '{"b1": ""}', '{"blocos": [{"id": "b1"}]}'):
            with self.assertRaises(ValueError):
                explain.parse(invalid)

    def test_long_blocks_are_clipped_for_the_model(self):
        self.assertEqual(len(explain._clip([str(i) for i in range(100)])), 29)
        self.assertTrue(explain._clip(["x" * 300])[0].endswith("…"))

    def test_cli_blocks_and_explain_from_stdin(self):
        out = io.StringIO()
        with patch.object(yabook_diff, "project_root", return_value=str(self.root)), contextlib.redirect_stdout(out):
            yabook_diff.main(["blocks"])
        self.assertEqual(len(json.loads(out.getvalue())["blocos"]), 3)
        out = io.StringIO()
        stdin = io.StringIO('{"b1": "Troca.", "b2": "Inclui.", "b3": "Remove."}')
        with patch.object(yabook_diff, "project_root", return_value=str(self.root)), patch.object(sys, "stdin", stdin), \
                contextlib.redirect_stdout(out):
            yabook_diff.main(["explain", "--sem-abrir"])
        result = json.loads(out.getvalue())
        self.assertEqual((result["blocos"], result["pendentes"]), (3, []))
        self.assertTrue((self.session.folder / "explain.json").exists())


if __name__ == "__main__":
    unittest.main()
