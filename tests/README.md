# Проверка AiRogue

Тесты запускаются из корня репозитория после `poetry install --no-root`:

```bash
poetry run python -m pytest tests/ -v --ignore=tests/test_world_generator_e2e.py
poetry run python -m pytest tests/test_theme_generator.py -v
poetry run python -m pytest tests/test_cli.py -v
poetry run python -m llm.generators.cli --help
poetry run flake8 . --select=E9,F63,F7,F82 --exclude=.git,.venv,scratch.py,game/pipeline.py,game/slots.py,llm/models.py
```

Обычный набор запрещает socket-соединения до collection и не использует API-ключ. Он также не запускает реальный Codex App Server и не читает `CODEX_ACCESS_TOKEN`: JSON-RPC transport проверяется через fake `Popen`/stdio. Реальные API-проверки в `test_world_generator_e2e.py` помечены `requires_openai_api` и выполняются только при явном `--run-requires-openai-api`; это ручной, потенциально платный запуск, не часть CI.

Подписочный Codex backend проверяется вручную только на доверенной машине, где владелец уже завершил интерактивный `codex login`:

```bash
poetry run python -m llm.generators.cli --provider codex --output world_model.json
```

Не запускайте эту команду в CI: она может расходовать subscription quota. Backend `openai` использует Platform API billing; backend `codex` использует уже аутентифицированный локальный Codex client.

`test_game_startup.py` запускает настоящий `main.main()` с реальными `Registry`, `InGame` и offscreen `Console`. Он заменяет только загрузку неподготовленного мира, оконный context и очередь событий, затем проверяет кадр, Quit и cleanup. Это не интеграционный тест `new_world()` и сериализованного мира: этот путь по-прежнему требует локальный `world_model.json` и незавершённые signals/slots.

## Что есть в репозитории

| Файлы | Область проверки |
| --- | --- |
| `test_cli.py` | Импорт CLI, вызов генератора и разбор аргументов с моками |
| `test_codex_app_server.py` | Offline handshake, terminal output и isolation policy Codex App Server |
| `test_theme_generator.py` | Генерация тем с моками |
| `test_world_methods.py` | Методы обёртки `World` |
| `test_world_generation_isolation.py` | Модели, JSON и изолированная обёртка `World` |
| `test_import_debugging.py` | Импорты модулей |
| `test_openai_key_requirement.py` | Поведение без ключа |
| `test_game_startup.py` | Игровой цикл без дисплея и LLM |
| `test_world_generator_e2e.py` | Реальные API-вызовы и сохранение результата |
| `conftest.py` | Общие фикстуры и маркеры |

## Ограничения и безопасный запуск

- `test_world_generator_e2e.py` явно исключён из CI, чтобы не обращаться к API при наличии ключа. Для ручного запуска его требуется `--run-requires-openai-api`.
- Не используйте `-m "not llm"` как замену изоляции: доступ к сети в обычном наборе запрещён независимо от имени теста.
- Обёртка `World` проверяется через подмену `llm.world.WorldGenerator`: это проверяет делегирование без создания клиента. Для проверки отсутствующего ключа есть отдельный тест без подмены клиента.
- Полная цепочка «LLM JSON → игровые ECS-сущности» пока не поддерживается: `new_world()` ожидает `signals` и `slots`, которых нет в `ComponentModel`. Поэтому offline-набор не содержит заглушек, обещающих этот сценарий.
- CI запускает тесты с coverage XML/JUnit и отдельный узкий Flake8 lint. Порога покрытия, pre-commit и форматирования пока нет.

Для новых тестов подменяйте внешние вызовы, проверяйте наблюдаемое поведение и ошибки данных. Сверяйте доступные фикстуры с `conftest.py`. Не отключайте падающие тесты ради зелёного отчёта.

Результат первичной проверки окружения и приоритеты исправлений — в [ревью документации](../docs/INITIAL_REVIEW.md). Правила внесения изменений — в [AGENTS.md](../AGENTS.md).
