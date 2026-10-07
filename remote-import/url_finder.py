from importlib.abc import PathEntryFinder
from importlib.util import spec_from_loader

from url_loader import URLLoader


class URLFinder(PathEntryFinder):
    def __init__(self, url, available, packages):
        self.url = url.rstrip("/")
        self.available = available
        self.packages = packages

    def find_spec(self, name, target=None):
        # Для подмодуля пакета приходит полное имя ("mypackage.mysubmodule"),
        # а на сервере лежит файл с последней частью имени
        shortname = name.rpartition(".")[2]

        if shortname in self.packages:
            package_url = "{}/{}".format(self.url, shortname)
            origin = "{}/__init__.py".format(package_url)
            loader = URLLoader()

            spec = spec_from_loader(
                name,
                loader,
                origin=origin,
                is_package=True
            )
            # is_package=True создаёт пустой submodule_search_locations;
            # он станет __path__ пакета, и подмодули будут искаться по этому URL
            # через тот же url_hook
            spec.submodule_search_locations.append(package_url)

            return spec

        if shortname in self.available:
            origin = "{}/{}.py".format(self.url, shortname)
            loader = URLLoader()

            return spec_from_loader(
                name,
                loader,
                origin=origin
            )

        return None
