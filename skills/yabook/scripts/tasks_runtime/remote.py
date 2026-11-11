"""Acesso ao GitHub pelo `gh`, isolado para os testes substituírem."""
import json
import subprocess


def run(*args, check=True, timeout=60, cwd=None):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    except subprocess.TimeoutExpired as exc:
        raise ValueError("Tempo esgotado em " + args[0] + "; verificar rede e repetir") from exc
    if check and result.returncode:
        detail = (result.stderr or result.stdout).strip().splitlines()[-1:] or [""]
        raise ValueError("Falha em %s %s: %s" % (args[0], args[1] if len(args) > 1 else "", detail[0]))
    return result


def git(root, *args, check=True, timeout=60):
    return run("git", "-C", str(root), *args, check=check, timeout=timeout)


def whoami():
    return json.loads(run("gh", "api", "user").stdout)["login"]


def info(repository):
    """None quando não existe; dicionário com `private` quando acessível."""
    result = run("gh", "api", "repos/" + repository, check=False)
    if result.returncode:
        if "404" in result.stderr or "Not Found" in result.stderr:
            return None
        raise ValueError("Falha ao consultar " + repository + "; verificar autenticação e rede")
    return dict(private=bool(json.loads(result.stdout).get("private")))


def create(repository):
    run("gh", "repo", "create", repository, "--private")


def clone(repository, destination):
    run("gh", "repo", "clone", repository, str(destination))


def url(repository):
    return "https://github.com/" + repository + ".git"


def accepted_urls(repository):
    return {url(repository), "git@github.com:" + repository + ".git", "https://github.com/" + repository}
