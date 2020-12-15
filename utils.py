from typing import List, Optional, Union


def strtobool(text: Union[str, bool]):
    if text is True or text is False:
        return text

    if text.lower() in ["y", "yes", "on", "true", "1"]:
        return True

    return False


def strtolist(text: Optional[str]) -> List[str]:
    return [item.strip() for item in (text or "").split(",")]
