import threading
import time
import gspread

from datetime import datetime

import jirasearcher
import sheetsearcher

# Создаем мьютекс для защиты функции jirasearcher.start_search()
jira_mutex = threading.Lock()

# Список площадок, которые нужно проверить
placed = {
    "Силикат",
    "Фрезер"
}


def start_searcher_multithreaded(placed):
    # Создаем список потоков
    threads = []

    # Для каждой площадки создаем новый поток
    for i in placed:
        t = threading.Thread(target=searcher_for_one_placed, args=(i,))
        threads.append(t)
        t.start()

    # Ждем завершения всех потоков
    for t in threads:
        t.join()


def searcher_for_one_placed(placed):
    print(f"Начинаю парсер площадки {placed}")
    # Ищем данные в таблице Google Sheets
    cells = sheetsearcher.start_search(placed)
    for cell in cells:
        if cell['value'] != "":
            # Получаем дату ТО из таблицы и дату из Jira
            sheets_date = cell['to_date']
            with jira_mutex:
                jira_date_set = jirasearcher.start_search(cell['value'])
            jira_date_str = next(iter(jira_date_set))
            jira_date_obj = datetime.strptime(jira_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
            formatted_jira_date = jira_date_obj.strftime('%d.%m.%Y')

            # Сравниваем даты и если они совпадают, то все хорошо
            if sheets_date == formatted_jira_date:
                print(f"{placed} | {cell['value']} имеет правильную дату ТО {cell['to_date']}")
            else:
                try:
                    # Если даты не совпадают, то меняем дату в таблице на правильную из Jira
                    print(f"{placed} | Меняю дату для {cell['value']}")
                    sheetsearcher.replace_on_correct(cell['row'], formatted_jira_date, placed)
                except gspread.exceptions.APIError as e:
                    # Если происходит ошибка из-за превышения лимита запросов в гугл, ждем 65 секунд и пробуем еще
                    print(f"Ошибка, слишком много запросов в гугл. Перезапуск через 65 секунд...")
                    time.sleep(65)


# Запускаем функцию поиска
start_searcher_multithreaded(placed)
print(f"Задача выполнена успешно")