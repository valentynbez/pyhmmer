# coding: utf-8
import typing


statuscode: typing.Dict[int, str]


class UnexpectedError(RuntimeError):
    def __init__(self, code: int, function: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class AllocationError(MemoryError):
    def __init__(self, ctype: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...


class EaselException(RuntimeError):
    pass
