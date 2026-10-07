import re
import sys

import requests

from url_finder import URLFinder

def url_hook(some_str):

    if not some_str.startswith(("http", "https")):
        raise ImportError

    try:
        response = requests.get(some_str, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Хост {some_str} недоступен: {e}", file=sys.stderr)
        raise ImportError(f"Не удалось подключиться к {some_str}") from e

    data = response.text

    filenames = re.findall(
        r"[a-zA-Z_][a-zA-Z0-9_]*\.py",
        data
    )

    modnames = {name[:-3] for name in filenames}

    # Каталоги в листинге http.server выглядят как <a href="mypackage/">
    packages = set(re.findall(
        r'href="([a-zA-Z_][a-zA-Z0-9_]*)/"',
        data
    ))

    return URLFinder(some_str, modnames, packages)

print(sys.path_hooks)
