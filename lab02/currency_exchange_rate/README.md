# Currency Exchange Rate CLI

Утилита командной строки для получения валютных курсов через лабораторный сервис и сохранения ответов в JSON-файлах.

## Требования
- Python 3.12 или новее
- Доступ к API обменных курсов (например, `http://localhost:8080/api`)

## Установка и запуск в виртуальной среде
1. Создайте и активируйте виртуальную среду Python:
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
   Для bash/zsh:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Установите зависимости пакета (editable-режим добавит CLI-скрипт `currency-rate` в PATH):
   ```bash
   pip install -e .
   ```

## Примеры запуска
### Один день
```bash
currency-rate --api-url http://localhost:8080/api --api-key TEST_KEY USD EUR 2025-01-01
```

### Диапазон дат (включительно)
```bash
currency-rate --api-url http://localhost:8080/api --api-key TEST_KEY USD EUR --range 2025-01-01 2025-01-07
```

### Дополнительные замечания
- Допустимые валюты: USD, EUR, RUB, RON, UAH.
- Результаты сохраняются в папку `data/` в корне проекта, имя файла содержит выбранные валюты и дату/диапазон.
- Логи пишутся в консоль и в файл `currency_exchange_rate.log`.
- Для справки используйте `currency-rate --help`.

## Структура пакета
- `currency_exchange_rate/cli.py` — парсит аргументы, проверяет корректность дат и валют, вызывает API и сохраняет результат.
- `currency_exchange_rate/api.py` — отправляет POST-запрос через `requests`, проверяет статус ответа и наличие поля `data`.
- `currency_exchange_rate/utils.py` — создает каталог `data/` и сохраняет одиночные/множественные ответы в JSON с читаемыми именами.
- `currency_exchange_rate/logger_setup.py` — настраивает консольный и файловый логгеры для приложения.
