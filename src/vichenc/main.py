#!/usr/bin/env python3
# coding: utf-8

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import chardet


@dataclass
class Entry:
    encoding: str | None
    path: str

    def as_str(self):
        encoding = self.encoding or ""
        return f"{encoding:<6}: {self.path}"

    @staticmethod
    def from_str(s: str) -> "Entry" | None:
        """
        >>> assert Entry.from_str("ascii: a.txt") == Entry(encoding="ascii", path="a.txt")
        """

        try:
            parts = s.split(": ", 1)
        except ValueError:
            return None
        encoding = parts[0].strip()
        path = parts[1].strip()
        return Entry(encoding=encoding, path=path)


def is_binary_file(file_path: str):
    with open(file_path, "rb") as file:
        chunk = file.read(8000)  # todo: peekにする？
        if b"\0" in chunk:
            return True
        return False


def detect_file_encoding(file_path: str):
    with open(file_path, "rb") as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        return result


def open_editor(content: str) -> str:
    """
    content の内容で$EDITORを開始し、編集後の内容を返す。
    """
    with tempfile.NamedTemporaryFile(delete=False, mode="w+", suffix=".vichec", prefix="tmp-") as tmp_file:
        tmp_file_path = tmp_file.name
        tmp_file.write(content)
        tmp_file.flush()

    editor = os.getenv("EDITOR", "vim")

    ret = subprocess.run([editor, tmp_file_path], stdin=None, stdout=None, stderr=None)
    if ret.returncode != 0:
        print(f"{editor} exited with {ret.returncode}")
        exit(1)

    with open(tmp_file_path, "r") as tmp_file:
        after_content = tmp_file.read()

    os.remove(tmp_file_path)

    return after_content


def change_encoding(
    file_path: str,
    from_encoding: str,
    to_encoding: str,
):
    with open(file_path, "r", encoding=from_encoding) as f:
        content = f.read()

    # todo errors='replace'
    with open(file_path, "w", encoding=to_encoding) as f:
        f.write(content)


def main():
    items = sys.argv[1:]
    if len(items) == 0:
        for dir_entry in os.scandir(os.getcwd()):
            items.append(dir_entry.path)

    before_entries: dict[str, Entry] = {}
    for item in map(Path, items):

        if not item.is_file():
            continue

        if is_binary_file(str(item)):
            continue

        result = detect_file_encoding(str(item))
        after = Entry(encoding=result["encoding"], path=str(item))

        assert after.path not in before_entries
        before_entries[after.path] = after

    before_content = "\n".join(e.as_str() for e in before_entries.values())
    after_content = open_editor(before_content)

    for l in after_content.splitlines():
        if len(l) == 0:
            continue

        after = Entry.from_str(l)
        if after is None:
            continue

        before = before_entries.get(after.path)
        if before is None:
            continue

        if before.encoding == after.encoding:
            continue

        if before.encoding is None:
            continue

        if after.encoding is None:
            continue

        if before.encoding == "ascii" and after.encoding.lower() == "utf-8":
            continue

        print(f"{before.encoding} -> {after.encoding}: {before.path}")
        change_encoding(before.path, before.encoding, after.encoding)


if __name__ == "__main__":
    main()
