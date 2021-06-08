import re
from dataclasses import dataclass
from datetime import datetime


class Templates(dict):

    def __missing__(self, key):
        return "{}".format(key)


@dataclass
class Replacement:
    file: str
    pattern: str
    replace: str

    def update(self, template) -> None:
        with open(self.file, "r") as read_changelog:
            content = read_changelog.read()
            replace = self.replace.format_map(template)
            content_new = re.sub(self.pattern, replace, content, flags=re.M)
        with open(self.file, "w") as write_changelog:
            write_changelog.write(content_new)

