# Лабораторная работа 1. Удалённый импорт

Механизм импорта Python-модулей и пакетов по HTTP через `sys.path_hooks`.

Елькин А.О. ИВТ-1.2

## Структура

```
.
├── activation_script.py   # регистрирует url_hook в sys.path_hooks
├── url_hook.py            # url_hook: читает листинг каталога по URL, создаёт URLFinder
├── url_finder.py          # URLFinder: находит модуль/пакет и создаёт для него spec
├── url_loader.py          # URLLoader: скачивает исходник и выполняет его
└── rootserver/            # «корень сервера»
    ├── myremotemodule.py
    └── mypackage/
        ├── __init__.py
        ├── mysubmodule.py
        └── subpackage/
            ├── __init__.py
            └── deep.py
```

## Установка

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

## 1. Локальный запуск

Запускаем HTTP-сервер в каталоге `rootserver`:

```sh
cd rootserver
python3 -m http.server
```

В другом терминале из корня проекта:

```sh
python3 -i activation_script.py
```

```python
>>> import myremotemodule
ModuleNotFoundError: No module named 'myremotemodule'
>>> sys.path.append("http://localhost:8000")
>>> import myremotemodule
>>> myremotemodule.myfoo()
Артемий Елькин's module is imported
```

![1.png](/screenshots/1.png)

![2.png](/screenshots/2.png)

Пока URL нет в `sys.path`, интерпретатор ничего о модуле не знает. После добавления пути
вызывается `url_hook`, который возвращает `URLFinder`, а модуль загружается через `URLLoader`.

## 2. Импорт с удалённого хоста (repl.it)

Модуль `myremotemodule.py` размещён на repl.it, где запущен `python3 -m http.server`.

```python
>>> sys.path.append("https://empty-limited-category--temaelkin.replit.app")
>>> import myremotemodule
>>> myremotemodule.myfoo()
Артемий Елькин's module is imported
```

![3.png](/screenshots/3.png)

![4.png](/screenshots/4.png)

## 3. Переход на `requests`

В `url_hook` и `URLLoader` вместо `urllib.request.urlopen` используется `requests.get()`.
`raise_for_status()` не даёт выполнить HTML страницы ошибки (404/500) как код модуля.
Исходник модуля передаётся в `compile()` байтами (`response.content`), чтобы кодировку
определил сам Python.

## 4. Обработка недоступного хоста (*)

Ошибки `requests` (`RequestException`: отказ соединения, таймаут, HTTP-ошибки)
перехватываются и превращаются в `ImportError`:

- в `url_hook`: если хост недоступен при добавлении пути, хук сообщает об этом в stderr,
  и Python переходит к следующим путям, поэтому получаем обычный `ModuleNotFoundError`;
- в `URLLoader`: если хост упал между поиском и загрузкой модуля, получаем `ImportError`
  с именем модуля и адресом.

Для всех запросов задан `timeout=5`.

![5.png](/screenshots/5.png)

Python кэширует неудачу хука в `sys.path_importer_cache`, поэтому после включения сервера
кэш нужно сбросить:

![6.png](/screenshots/6.png)

## 5. Загрузка пакетов (***)

`url_hook` находит в листинге каталога не только файлы `*.py`, но и подкаталоги, и считает их пакетами.
Для пакета `URLFinder` вызывает:

```python
spec = spec_from_loader(name, loader, origin=".../mypackage/__init__.py", is_package=True)
spec.submodule_search_locations.append(".../mypackage")
```

- `origin` указывает на `__init__.py`, то есть на код самого пакета;
- `is_package=True` создаёт `submodule_search_locations`, который становится `__path__` пакета.
  Подмодули ищутся по этому URL через тот же `url_hook`, поэтому работают вложенные пакеты
  и относительные импорты (`from . import mysubmodule`).

![7.png](/screenshots/7.png)
