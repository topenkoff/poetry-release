import subprocess

from typing import Optional


def has_modified() -> bool:
    result = subprocess.run(
        ["git", "diff", "HEAD", "--name-only", "--exit-code"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    return bool(result.returncode)

def create_tag(version: str, message: str, sign: bool) -> None:
    command = ["git", "tag"]
    if sign:
        command += ["-s"]
    command += ["-a", f"{version}", "-m", f"{message}"]
    subprocess.run(command)

def create_commit(message: str, sign: bool) -> None:
    command = ["git", "commit"]
    if sign:
        command += ["-S"]
    command += ["-a", "-m", f"{message}"]
    subprocess.run(command)

def push_commit() -> None:
    branch = __current_branch()
    remote = __get_remote()
    if remote is None:
        remote = "origin"
    subprocess.run(["git", "push", f"{remote}", f"{branch}"])

def push_tag(version: str) -> None:
    remote = __get_remote()
    if remote is None:
        remote = "origin"
    subprocess.run(["git", "push", f"{remote}", f"{version}"])

def repo_exists() -> bool:
    result = subprocess.run(
        ["[", "-d", ".git", "]"],
        stdout=subprocess.PIPE
    )
    return not result.returncode

def __current_branch() -> Optional[str]:
    args = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
    with subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        universal_newlines=True,
    ) as process:
        branch, err = process.communicate()
        if err is not None:
            return None
        branch = branch.replace("\n", "")
        return branch

def __get_remote() -> Optional[str]:
        args = [
            'git',
            'for-each-ref',
            "--format='%(refname:short):%(upstream:remotename)'",
            'refs/heads'
        ]
        with subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        ) as process:
            data, err = process.communicate()
            if err is not None:
                return None
            data = data.replace("'", "").split("\n")
            data = list(filter(None, data))
            current_branch = __current_branch()
            for pair in data:
                branch, remote = pair.split(":")
                if branch == current_branch and remote:
                    return remote
        return None
