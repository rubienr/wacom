from enum import Enum
from typing import Any, Callable, Tuple, Set, List


def get_public_class_members(obj: object) -> List[str]:
    """
    Retrieves names of public members.

    :param obj: the object to inspect
    :return: names of public members (vars and properties)
    """
    return [member for member in dir(obj) if not member.startswith("_") and type(getattr(obj, member, "")).__name__ not in ["method", "function"]]


def _get_public_class_member_values(obj: object) -> List[Tuple[str, object]]:
    return [(member, getattr(obj, member)) for member in get_public_class_members(obj)]


def _object_dump(obj: Any, prefix: str, indent: str, level: int) -> str:
    """
    Dumps object fields recursively.

    :param obj: the object to dump
    :param prefix: string to prepend to each line
    :param indent: indent string depending on object depth
    :param level: internal value for indentation
    :return: readable representation
    """
    expanded_indent: str = indent * level

    if obj is None:
        return "<none>\n"

    elif isinstance(obj, Callable):
        return "<callable>\n"

    elif isinstance(obj, Enum):
        return f"{obj}\n"

    elif isinstance(obj, (int, float)):
        return f"{obj}\n"

    elif isinstance(obj, (str)):
        return f"'{obj}'\n"

    elif isinstance(obj, (List, Set)):
        sep_start = "[" if isinstance(obj, List) else "{"
        sep_end = "]" if isinstance(obj, List) else "}"

        if len(obj) == 0:
            return f"{sep_start}{sep_end}\n"

        dump = f"\n{prefix}{expanded_indent}{sep_start}\n"
        for item in obj:
            dump += f"{prefix}{expanded_indent}{indent}{_object_dump(item, prefix, indent, level + 1)}"
        dump += f"{prefix}{expanded_indent}{sep_end}\n"
        return dump

    elif isinstance(obj, Tuple):
        if len(obj) == 0:
            return "()\n"
        dump = f"\n{prefix}{expanded_indent}(\n"
        for item in obj:
            dump += f"{prefix}{expanded_indent}{indent}{_object_dump(item, prefix, indent, level + 1)}"
        dump += f"{prefix}{expanded_indent})\n"
        return dump

    elif isinstance(obj, dict):
        if len(obj) == 0:
            return "{}\n"
        dump = f"\n{prefix}{expanded_indent}{{\n"
        for item_name, item_value in obj.items():
            dump += f"{prefix}{expanded_indent}{indent}{item_name}={_object_dump(item_value, prefix, indent, level + 2)}"
        dump += f"{prefix}{expanded_indent}}}\n"
        return dump

    else:
        dump = "\n"
        for member, value in _get_public_class_member_values(obj):
            dump += f"{prefix}{expanded_indent}{member}={_object_dump(value, prefix, indent, level + 1)}"
        return dump


def object_dump(obj: Any, prefix: str = "", indent: str = "  ", level: int = 0) -> str:
    """
    :param obj: see `_object_dump()`
    :param prefix: see `_object_dump()`
    :param indent: see `_object_dump()`
    :param level: see `_object_dump()`
    :return: see `_object_dump()`
    """
    return _object_dump(obj, prefix, indent, level).strip("\n")
