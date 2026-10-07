import requests


class URLLoader:
    def create_module(self, target):
        return None

    def exec_module(self, module):
        origin = module.__spec__.origin

        try:
            response = requests.get(origin, timeout=5)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ImportError(
                f"Не удалось загрузить модуль {module.__name__} с {origin}: {e}",
                name=module.__name__
            ) from e

        source = response.content

        code = compile(
            source,
            origin,
            mode="exec"
        )

        exec(code, module.__dict__)
