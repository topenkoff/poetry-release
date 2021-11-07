import subprocess

from typing import Optional

from poetry_release.settings import Settings


class Git:

    def __init__(self, settings: Settings) -> None:
        self.sign_tag = settings.sign_tag
        self.sign_commit = settings.sign_commit

    def has_modified(self) -> bool:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-only", "--exit-code"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        return bool(result.returncode)

    def create_tag(self, tag_version: str, tag_message: str) -> None:
        command = ["git", "tag"]
        if self.sign_tag:
            command += ["-s"]
        command += ["-a", f"{tag_version}", "-m", f"{tag_message}"]
        subprocess.run(command)

    def create_commit(self, commit_message: str) -> None:
        command = ["git", "commit"]
        if self.sign_commit:
            command += ["-S"]
        command += ["-a", "-m", f"{commit_message}"]
        subprocess.run(command)

    def push_commit(self) -> None:
        subprocess.run(["git", "push"])

    def push_tag(self, tag_version: str) -> None:
        remote = self.__get_remote()
        if not remote:
            return
        subprocess.run(["git", "push", f"{remote}", f"{tag_version}"])

    def repo_exists(self) -> bool:
        result = subprocess.run(
            ["[", "-d", ".git", "]"],
            stdout=subprocess.PIPE
        )
        return not result.returncode

    def __get_current_branch(self) -> Optional[str]:
        with subprocess.Popen(
            ["git", "branch", "--show-current"],
            stdout=subprocess.PIPE,
            universal_newlines=True
        ) as cur_process:
            current_branch, err = cur_process.communicate()
            if err is not None:
                return None
            current_branch = current_branch.replace("\n", "")
            return current_branch

    def __get_remote(self) -> Optional[str]:
        args = [
            'git',
            'for-each-ref',
            "--format='%(refname:short):%(upstream:remotename)'",
            'refs/heads'
        ]
        with subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            universal_newlines=True
        ) as rem_process:
            data, err = rem_process.communicate()
            if err is not None:
                return None
            data = data.replace("'", "").split("\n")
            data = list(filter(None, data))
            current_branch = self.__get_current_branch()
            for pair in data:
                branch, remote = pair.split(":")
                if branch == current_branch:
                    return remote
        return None
