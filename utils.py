from typing import Union


def strtobool(text: Union[str, bool]):
    if text is True or text is False:
        return text

    if text.lower() in ['y', 'yes', 'on', 'true', '1']:
        return True

    return False
