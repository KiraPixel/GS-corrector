from datetime import datetime

import jirasearcher
import sheetsearcher
import time
import gspread
import os

# Список площадок, которые нужно проверить
placed = {
    "Силикат",
    "Фрезер"
}


# Функция для запуска поиска
def start_searcher(placed):
    for i in placed:
        print(f"Начинаю парсер площадки {i}")
        # Ищем данные в таблице Google Sheets
        cells = sheetsearcher.start_search(i)
        for cell in cells: 
            if cell['value'] != "":
                # Получаем дату ТО из таблицы и дату из Jira
                sheets_date = cell['to_date']
                jira_date_set = jirasearcher.start_search(cell['value'])
                jira_date_str = next(iter(jira_date_set))
                jira_date_obj = datetime.strptime(jira_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                formatted_jira_date = jira_date_obj.strftime('%d.%m.%Y')

                # Сравниваем даты и если они совпадают, то все хорошо
                if sheets_date == formatted_jira_date:
                    print(f"{cell['value']} имеет правильную дату ТО {cell['to_date']}")
                else:
                    try:
                        # Если даты не совпадают, то меняем дату в таблице на правильную из Jira
                        print(f"Меняю дату для {cell['value']}")
                        sheetsearcher.replace_on_correct(cell['row'], formatted_jira_date, i)
                    except gspread.exceptions.APIError as e:
                        # Если происходит ошибка из-за превышения лимита запросов в гугл, ждем 65 секунд и пробуем еще
                        print(f"Ошибка, слишком много запросов в гугл. Перезапуск через 65 секунд...")
                        time.sleep(65)


# Запускаем функцию поиска
start_searcher(placed)
print(f"Задача выполнена успешно")