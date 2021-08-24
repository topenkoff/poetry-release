import subprocess

from typing import Optional


class Git:

    def __init__(self) -> None:
        self.repo_exists = self._git_exists()

    def has_modified(self) -> bool:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-only", "--exit-code"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            universal_newlines=True,
        )
        if result.returncode == 0:
            return False
        else:
            return True

    def create_tag(
            self,
            tag_version: str,
            tag_message: str,
            sign: bool,
    ) -> None:
        command = ["git", "tag", "-a", f"{tag_version}"]
        if sign:
            command += ["-S"]
        command += ["-m", f"{tag_message}"]
        subprocess.run(command)

    def create_commit(self, commit_message: str, sign: bool) -> None:
        command = ["git", "commit", "-a", "-m"]
        if sign:
            command += ["-S"]
        command += [f"{commit_message}"]
        subprocess.run(command)

    def push_commit(self) -> None:
        subprocess.run(["git", "push"])

    def push_tag(self, tag_version: str) -> None:
        remote = self._get_remote()
        if remote is None:
            return
        subprocess.run(["git", "push", f"{remote}", f"{tag_version}"])

    def _git_exists(self) -> bool:
        result = subprocess.run(
            ["[", "-d", ".git", "]"],
            stdout=subprocess.PIPE
        )
        if result.returncode == 0:
            return True
        else:
            return False

    def _get_remote(self) -> Optional[str]:
        with subprocess.Popen(
            ["git", "branch", "--show-current"],
            stdout=subprocess.PIPE,
            universal_newlines=True
        ) as cur_process:
            current_branch, err = cur_process.communicate()
            if err is not None:
                return None
            current_branch = current_branch.replace("\n", "")
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
            for pair in data:
                branch, remote = pair.split(":")
                if branch == current_branch:
                    return remote
        return None
