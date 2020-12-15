import re

from typing import List, Optional, Union

# List regex comma or white space, leading / trailing spaces are removed.
LIST_REGEX = re.compile(r"\s*[,\s+]\s*", re.UNICODE)


def strtobool(text: Union[str, bool]):
    if text is True or text is False:
        return text

    if text.lower() in ["y", "yes", "on", "true", "1"]:
        return True

    return False


def strtolist(text: Optional[str]) -> List[str]:
    return LIST_REGEX.split(text or "")
