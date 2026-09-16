# Проверка AiRogue

Тесты запускаются из корня репозитория после `poetry install --no-root`:

```bash
poetry run python -m pytest tests/ -v --ignore=tests/test_world_generator_e2e.py
poetry run python -m pytest tests/test_theme_generator.py -v
poetry run python -m pytest tests/test_cli.py -v
poetry run python -m llm.generators.cli --help
poetry run flake8 . --select=E9,F63,F7,F82 --exclude=.git,.venv,scratch.py,game/pipeline.py,game/slots.py,llm/models.py
```

Обычный набор запрещает socket-соединения до collection и не использует API-ключ. Реальные API-проверки в `test_world_generator_e2e.py` помечены `requires_openai_api` и выполняются только при явном `--run-requires-openai-api`; это ручной, потенциально платный запуск, не часть CI.

`test_game_startup.py` запускает настоящий `main.main()` с реальными `Registry`, `InGame` и offscreen `Console`. Он заменяет только загрузку неподготовленного мира, оконный context и очередь событий, затем проверяет кадр, Quit и cleanup. Это не интеграционный тест `new_world()` и сериализованного мира: этот путь по-прежнему требует локальный `world_model.json` и незавершённые signals/slots.

## Что есть в репозитории

| Файлы | Область проверки |
| --- | --- |
| `test_cli.py` | Импорт CLI, вызов генератора и разбор аргументов с моками |
| `test_theme_generator.py` | Генерация тем с моками |
| `test_world_methods.py` | Методы обёртки `World` |
| `test_world_generation_isolation.py`, `test_world_generation_stable.py` | Модели, JSON и загрузка мира |
| `test_import_debugging.py` | Импорты модулей |
| `test_openai_key_requirement.py` | Поведение без ключа |
| `test_integration.py` | Пропущенные сценарии и устаревшие контрактные заглушки |
| `test_game_startup.py` | Игровой цикл без дисплея и LLM |
| `test_world_generator_e2e.py` | Реальные API-вызовы и сохранение результата |
| `conftest.py` | Общие фикстуры и маркеры |

## Ограничения и безопасный запуск

- `test_world_generator_e2e.py` явно исключён из CI, чтобы не обращаться к API при наличии ключа. Для ручного запуска его требуется `--run-requires-openai-api`.
- Не используйте `-m "not llm"` как замену изоляции: доступ к сети в обычном наборе запрещён независимо от имени теста.
- Некоторые тесты патчат старый путь `llm.world.ChatOpenAI`, тогда как клиент используется в `llm.generators.base`. Фикстура `test_world` тоже обращается к старому интерфейсу. Перед расширением тестов проверьте фактическое место использования зависимости.
- Прохождение заглушек не доказывает соблюдение контрактов. Не используйте их число как критерий готовности.
- CI запускает тесты с coverage XML/JUnit и отдельный узкий Flake8 lint. Порога покрытия, pre-commit и форматирования пока нет.

Для новых тестов подменяйте внешние вызовы, проверяйте наблюдаемое поведение и ошибки данных. Сверяйте доступные фикстуры с `conftest.py`. Не отключайте падающие тесты ради зелёного отчёта.

Результат первичной проверки окружения и приоритеты исправлений — в [ревью документации](../docs/INITIAL_REVIEW.md). Правила внесения изменений — в [AGENTS.md](../AGENTS.md).
