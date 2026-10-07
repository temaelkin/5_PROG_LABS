import sys

from url_hook import url_hook
from url_finder import URLFinder
from url_loader import URLLoader

sys.path_hooks.append(url_hook)

print(sys.path_hooks)
