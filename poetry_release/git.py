import subprocess


class ReleaseGit:

    def __init__(self):
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


    def create_tag(self, tag_version, tag_message):
        subprocess.run(
            ["git", "tag", "-a", f"{tag_version}", "-m", f"{tag_message}"],
        )

    def create_commit(self, commit_message):
        subprocess.run(
            ["git", "commit", "-a", "-m", f"{commit_message}"]
        )

    def push_commit(self):
        subprocess.run(["git", "push"])

    def push_tag(self, tag_version):
        subprocess.run(["git", "push", "origin", f"{tag_version}"])


    def _git_exists(self) -> bool:
        result = subprocess.run(
            ["[", "-d" ,".git", "]"],
            stdout=subprocess.PIPE
        )
        if result.returncode == 0:
            return True
        else:
            return False

