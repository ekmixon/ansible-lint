from typing import TYPE_CHECKING, Any, Dict, List, Union

from ansiblelint.rules import AnsibleLintRule

if TYPE_CHECKING:
    from typing import Optional

    from ansiblelint.constants import odict
    from ansiblelint.errors import MatchError
    from ansiblelint.file_utils import Lintable


class NoFormattingInWhenRule(AnsibleLintRule):
    id = 'no-jinja-when'
    shortdesc = 'No Jinja2 in when'
    description = (
        '``when`` is a raw Jinja2 expression, remove redundant {{ }} from variable(s).'
    )
    severity = 'HIGH'
    tags = ['deprecations']
    version_added = 'historic'

    def _is_valid(self, when: str) -> bool:
        return '{{' not in when and '}}' not in when if isinstance(when, str) else True

    def matchplay(
        self, file: "Lintable", data: "odict[str, Any]"
    ) -> List["MatchError"]:
        errors: List["MatchError"] = []
        if isinstance(data, dict):
            if 'roles' not in data or data['roles'] is None:
                return errors
            errors.extend(
                self.create_matcherror(details=str({'when': role}))
                for role in data['roles']
                if self.matchtask(role, file=file)
            )

        if isinstance(data, list):
            for play_item in data:
                if sub_errors := self.matchplay(file, play_item):
                    errors = errors + sub_errors
        return errors

    def matchtask(
        self, task: Dict[str, Any], file: 'Optional[Lintable]' = None
    ) -> Union[bool, str]:
        return 'when' in task and not self._is_valid(task['when'])
