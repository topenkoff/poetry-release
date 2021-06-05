import subprocess


class ReleaseGit:

    def has_modified(self) -> bool:
        result = subprocess.run(
            ["git", "diff", "HEAD", "--name-only", "--exit-code"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
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
        subprocess.run(["git", "push", f"{tag_version}"])

