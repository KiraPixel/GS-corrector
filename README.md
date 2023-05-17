**GS-corrector** - это набор инструментов для обработки данных в форматах Google Sheets и JIRA.

![image](https://github.com/KiraPixel/GS-corrector/assets/90696175/8ff1d2ba-ad79-4210-8c6d-f64072c0a5e0) ![image](https://github.com/KiraPixel/GS-corrector/assets/90696175/8547e605-d2e9-4769-b9e1-7d281da743a6)

**Структура файлов:**
```
jirasearcher.py - скрипт для поиска задач в JIRA по ключевым словам и создания отчета в формате Google Sheets.
sheetsearcher.py - скрипт для поиска и фильтрации данных в Google Sheets.
starter.py - скрипт для запуска процесса обработки данных в Google Sheets и JIRA.
```


**Использование:**

Для использования проекта необходимо выполнить следующие шаги:

```
1. Загрузить все необходимые файлы из репозитория.
2. Установить необходимые зависимости, выполнив команду pip install -r requirements.txt.
3. Создать файл jira.json с данными для подключения к JIRA API.
4. Создать файл creds.json с учетными данными для подключения к Google API (генерируется автоматически).
5. Создать файл config.json с информацией о площадках.
6. Запустить скрипт starter.py.
```

**jira.json содержит следующую структуру:**
```
{
    "jira": {
        "username": "example",
        "password": "example",
        "url": "https://sm.example.ru/"
    }
}
```

**config.json содержит следующую структуру:**
```
{
    "Уникальное имя": {
      "google_sheet_link": "ссылка на таблицу",
      "sheet_name": "название листа",
      "start_row": начальная строка,
      "garage_num_row": колонка с номером,
      "date_row": колонка с датой
    },
    "Уникальное имя": {
      "google_sheet_link": "ссылка на таблицу",
      "sheet_name": "название листа",
      "start_row": начальная строка,
      "garage_num_row": колонка с номером,
      "date_row": колонка с датой
    }
}
```

