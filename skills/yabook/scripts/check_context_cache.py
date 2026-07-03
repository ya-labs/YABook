#!/usr/bin/env python3

import argparse
import hashlib
import subprocess
from pathlib import Path


MAX_CACHE_CHARS = 3000
REQUIRED = {
    "version",
    "branch",
    "remote",
    "reference",
    "rules_sources",
    "rules_fingerprint",
    "planning_sources",
    "planning_fingerprint",
}


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def parse_metadata(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("frontmatter ausente")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("frontmatter não finalizado") from error

    metadata = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        key, separator, value = line.partition(":")
        if not separator or not key.strip() or not value.strip():
            raise ValueError(f"metadado inválido: {line}")
        metadata[key.strip()] = value.strip()
    return metadata


def source_files(repo: Path, value: str) -> list[Path]:
    if value == "-":
        return []

    files = []
    root = repo.resolve()
    for raw_path in value.split(";"):
        candidate = (root / raw_path.strip()).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"fonte fora do repositório: {raw_path}")
        if not candidate.exists():
            raise ValueError(f"fonte ausente: {raw_path}")
        if candidate.is_dir():
            files.extend(path for path in candidate.rglob("*") if path.is_file())
        else:
            files.append(candidate)
    return sorted(set(files), key=lambda path: path.relative_to(root).as_posix())


def fingerprint(repo: Path, value: str) -> str:
    digest = hashlib.sha256()
    for path in source_files(repo, value):
        relative = path.relative_to(repo.resolve()).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def repository_state(repo: Path, reference: str) -> dict[str, object]:
    ancestor = subprocess.run(
        ["git", "-C", str(repo), "merge-base", "--is-ancestor", reference, "HEAD"],
        capture_output=True,
    )
    return {
        "branch": git(repo, "branch", "--show-current"),
        "remote": git(repo, "remote", "get-url", "origin"),
        "reference_is_ancestor": ancestor.returncode == 0,
    }


def validate_text(
    repo: Path,
    text: str,
    state: dict[str, object] | None = None,
) -> list[str]:
    errors = []
    if len(text) > MAX_CACHE_CHARS:
        errors.append(f"cache possui {len(text)} caracteres; máximo {MAX_CACHE_CHARS}")

    try:
        metadata = parse_metadata(text)
    except ValueError as error:
        return errors + [str(error)]

    missing = sorted(REQUIRED - metadata.keys())
    if missing:
        errors.append("metadados ausentes: " + ", ".join(missing))
        return errors
    if metadata["version"] != "1":
        errors.append("version deve ser 1")

    try:
        current = state or repository_state(repo, metadata["reference"])
        if metadata["branch"] != current["branch"]:
            errors.append("branch divergente")
        if metadata["remote"] != current["remote"]:
            errors.append("remote divergente")
        if not current["reference_is_ancestor"]:
            errors.append("reference não é ancestral do HEAD")
        for group in ("rules", "planning"):
            current = fingerprint(repo, metadata[f"{group}_sources"])
            if current != metadata[f"{group}_fingerprint"]:
                errors.append(f"{group}_fingerprint divergente")
    except (subprocess.CalledProcessError, ValueError) as error:
        errors.append(str(error))
    return errors


def validate(
    repo: Path,
    cache: Path,
    state: dict[str, object] | None = None,
) -> list[str]:
    if not cache.exists():
        return []
    return validate_text(repo, cache.read_text(encoding="utf-8"), state)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--cache", default=".yabook/context-cache.md")
    parser.add_argument("--fingerprints", action="store_true")
    args = parser.parse_args()

    repo = args.repo.resolve()
    cache = (repo / args.cache).resolve()
    if not cache.exists():
        print("AUSENTE: cache opcional não encontrado")
        return

    metadata = parse_metadata(cache.read_text(encoding="utf-8"))
    if args.fingerprints:
        for group in ("rules", "planning"):
            print(f"{group}_fingerprint: {fingerprint(repo, metadata[f'{group}_sources'])}")
        return

    errors = validate(repo, cache)
    if errors:
        raise SystemExit("INVÁLIDO: " + "; ".join(errors))
    print("VÁLIDO: cache compacto pode ser usado")


if __name__ == "__main__":
    main()
