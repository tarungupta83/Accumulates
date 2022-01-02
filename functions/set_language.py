import json
from pathlib import Path


def set_language():
    option_language = open(Path("assets", "language.set")).read()
    if option_language == "English":
        dict_language = json.loads(open(Path("assets", "language", "en.json")).read())
    elif option_language == "中文":
        dict_language = json.loads(open(Path("assets", "language", "zh.json")).read())
    return dict_language
