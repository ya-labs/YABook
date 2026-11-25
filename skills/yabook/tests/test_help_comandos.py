import re
import unittest
from pathlib import Path

REFERENCES = Path(__file__).resolve().parents[1] / "references"
PAGES = REFERENCES / "help" / "comandos"
HEADINGS = ["## Quando usar", "## Altera alguma coisa?", "## Sintaxe", "## Exemplos", "## Relacionados"]


def command_key(token):
    """Mesma regra da extensão do VS Code: primeiro termo sem `do`."""
    words = token.split()
    rest = words[1:] if words[0] == "do" and len(words) > 1 else words
    return re.sub(r"[^a-z0-9-]", "", rest[0].split("|")[0].lower())


def index_keys():
    text = (REFERENCES / "help.md").read_text(encoding="utf-8")
    section = re.search(r"## Índice geral\n(.*?)(?:\n## |\Z)", text, re.S).group(1)
    lines = section.lstrip("\n").splitlines()
    end = next((i for i, line in enumerate(lines) if not line.startswith("- ")), len(lines))
    tokens = [t for line in lines[:end] if re.match(r"- [^:]+:", line) for t in re.findall(r"`([^`]+)`", line)]
    return {command_key(token) for token in tokens}


class HelpPagesTest(unittest.TestCase):
    def test_every_command_in_help_index_has_a_page(self):
        missing = sorted(key for key in index_keys() if not (PAGES / f"{key}.md").exists())
        self.assertEqual(missing, [], "Comandos do índice sem página em help/comandos/")

    def test_no_page_without_command(self):
        orphans = sorted(p.stem for p in PAGES.glob("*.md") if p.stem not in index_keys())
        self.assertEqual(orphans, [], "Páginas sem comando no índice de help.md")

    def test_pages_follow_the_template(self):
        for page in sorted(PAGES.glob("*.md")):
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=page.name):
                self.assertTrue(text.startswith(f"# `$yabook {page.stem}"), "título fora do padrão")
                positions = [text.find(h) for h in HEADINGS]
                self.assertNotIn(-1, positions, "seção obrigatória ausente")
                self.assertEqual(positions, sorted(positions), "seções fora de ordem")
                self.assertNotRegex(text, r"- \[[ x]\]", "página com checklist")
                self.assertLessEqual(len(text), 4500 if "## Contrato" in text else 3400, "página longa demais")

    def test_contract_blocks_match_the_artifact_references(self):
        """O contrato mostrado à pessoa é cópia literal do contrato que o agente segue."""
        sources = "".join(p.read_text(encoding="utf-8") for p in (REFERENCES / "artefatos").glob("*.md"))
        pages = [p for p in sorted(PAGES.glob("*.md")) if "## Contrato" in p.read_text(encoding="utf-8")]
        self.assertEqual([p.stem for p in pages], ["branch", "commit", "issue", "pr", "release"])
        for page in pages:
            # Os modelos têm títulos `##` dentro dos blocos: a seção termina em Relacionados.
            section = page.read_text(encoding="utf-8").split("## Contrato", 1)[1].split("\n## Relacionados", 1)[0]
            blocks = re.findall(r"```\w*\n.*?```", section, re.S)
            with self.subTest(page=page.name):
                self.assertTrue(blocks, "contrato sem bloco")
                for block in blocks:
                    self.assertTrue(block in sources, "bloco diferente da referência em artefatos/:\n" + block)


if __name__ == "__main__":
    unittest.main()
