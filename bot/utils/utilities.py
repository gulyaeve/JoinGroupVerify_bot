import os
import re

from aiogram import types


def make_text(input_text):
    return re.sub(r"<.*?>", "", input_text)


def make_bytes(file_content: str, file_label: str) -> bytes:
    with open(f"temp/{file_label}", "w") as f:
        f.write(file_content)
    with open(f"temp/{file_label}", "rb") as f:
        file = f.read()
        b = bytearray(file)
    os.remove(f"temp/{file_label}")
    return b


def format_info(info_from_telegram: types.Chat) -> str:
    formatted_info = dict(info_from_telegram)
    if formatted_info['photo'] is not None:
        del formatted_info["photo"]
    result = ""
    for key, value in formatted_info.items():
        if value:
            result += "{0}: {1}\n".format(key, value)
    return result


