import re

from typing import Union, List

LIST_REGEX = re.compile(r'[\s,]+', re.UNICODE)


def strtobool(text: Union[str, bool]):
    if text is True or text is False:
        return text

    if text.lower() in ['y', 'yes', 'on', 'true', '1']:
        return True

    return False


def strtolist(text: str) -> List[str]:
    return LIST_REGEX.findall(text or "")
