from typing import List, Optional, Union


def as_bool(value: Union[str, bool]) -> bool:
    """
    Get the boolean value represented by the truthy `value`.

    :param value str: The value to check
    :rtype: bool
    """
    if not value:
        return False

    return str(value).lower() in ["y", "yes", "on", "t", "true", "1"]


def strtolist(text: Optional[str]) -> List[str]:
    return [item.strip() for item in (text or "").split(",") if item.strip()]
