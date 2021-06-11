import re
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

from poetry_release.settings import Settings


class Template(Dict[Any, Any]):
    
    def __missing__(self, key: str) -> str:
        return "{}".format(key)


@dataclass
class Replacement:
    file: str
    pattern: str
    replace: str

    def update(self, template: Template) -> None:
        with open(self.file, "r") as read_changelog:
            content = read_changelog.read()
            replace = self.replace.format_map(template)
            content_new = re.sub(self.pattern, replace, content, flags=re.M)
        with open(self.file, "w") as write_changelog:
            write_changelog.write(content_new)



class Replacer:
    
    def __init__(
        self,
        template: Template,
        settings: Settings
    ) -> None:
        self.template = template
        self.__settings = settings
        self.replacements = [
            Replacement(**r)
            for r in settings.release_replacements
        ]

    def update_replacements(self) -> None:
        for replacement in self.replacements:
            replacement.update(self.template)

    def generate_messages(self) -> List[str]:
        if self.__settings.release_commit_message is None:
            commit_message = ""
        else:
            commit_message = self.__settings.release_commit_message

        if self.__settings.post_release_commit_message is None:
            next_commit_message = ""
        else:
            next_commit_message = self.__settings.post_release_commit_message

        if self.__settings.tag_name is None:
            tag_name = "" 
        else:
            tag_name = self.__settings.tag_name

        tag_message = ""

        return [
            tag_name,
            tag_message,
            commit_message,
            next_commit_message,
        ]
