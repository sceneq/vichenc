#! /usr/bin/env python3
# coding: utf-8

from __future__ import annotations

from typing import Generator, TypeGuard, TypeVar

T = TypeVar("T")


def chunks(l: list[T], n: int) -> Generator[list[T], None, None]:
    for i in range(0, len(l), n):
        yield l[i : i + n]


def chunks_gen(g: Generator[T, None, None], n: int) -> Generator[list[T], None, None]:
    buffer = []
    for item in g:
        buffer.append(item)
        if len(buffer) == n:
            yield buffer
            buffer.clear()
    if buffer:
        yield buffer


def must(v: T | None) -> T:
    assert v is not None
    return v


def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)


def is_int_list(val: list[object]) -> TypeGuard[list[int]]:
    return all(isinstance(x, int) for x in val)
