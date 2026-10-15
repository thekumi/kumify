from dataclasses import dataclass


@dataclass
class VirtualCalendarDescriptor:
    key: str
    color: str = "#4A90D9"


@dataclass
class VirtualTaskListDescriptor:
    key: str
    color: str = "#4A90D9"


_calendar_descriptors: dict[str, VirtualCalendarDescriptor] = {}
_task_list_descriptors: dict[str, VirtualTaskListDescriptor] = {}


def register_virtual_calendar(key: str, color: str = "#4A90D9"):
    _calendar_descriptors[key] = VirtualCalendarDescriptor(key=key, color=color)


def register_virtual_task_list(key: str, color: str = "#4A90D9"):
    _task_list_descriptors[key] = VirtualTaskListDescriptor(key=key, color=color)


def get_virtual_calendars() -> list[VirtualCalendarDescriptor]:
    return list(_calendar_descriptors.values())


def get_virtual_task_lists() -> list[VirtualTaskListDescriptor]:
    return list(_task_list_descriptors.values())
