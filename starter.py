import time
from datetime import datetime
import threading
import gspread
import tkinter as tk
from ttkbootstrap import Style
from ttkbootstrap.widgets import Button
from ttkbootstrap import ttk


import jirasearcher
import sheetsearcher


class ParserGUI:
    def __init__(self):

        # Инициализация GUI
        self.style = Style(theme='darkly')  # Выбор темы darkly (можно выбрать другую тему)
        self.window = self.style.master
        self.window.title("Парсер данных")
        self.window.iconbitmap('icon.ico')

        # Настройка размеров и масштабирования окна
        self.window.geometry("400x450")  # Задайте начальные размеры окна по своему усмотрению
        self.window.resizable(True, False)  # Разрешить изменение размера окна по обоим осям

        # Создание меню
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        # Создание текстового поля для лога
        self.log_text = tk.Text(self.window, height=20)  # Увеличение высоты текстового поля на 400 пикселей
        self.log_text.pack(fill=tk.BOTH, expand=True)  # Используем fill и expand для масштабирования


        # Создание скроллбара и привязка его к текстовому полю
        scrollbar = ttk.Scrollbar(self.log_text, style='darkly.Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # Создание кнопки "Начать" и привязка ее к методу toggle_search()
        self.start_button = Button(
            self.window,
            text="Начать",
            command=self.toggle_search,
            style='success.TButton'  # Стиль кнопки успеха (можно выбрать другой стиль)
        )
        self.start_button.pack(pady=10)  # Используем pady для отступа

        # Инициализация переменных состояния
        self.is_searching = False  # Флаг поиска данных
        self.stop_event = threading.Event()  # Событие для остановки поиска

    def toggle_search(self):
        # Метод для переключения между началом и остановкой поиска
        if self.is_searching:
            self.stop_search()  # Если поиск уже выполняется, остановить его
        else:
            self.start_search()  # Если поиск не выполняется, начать его

    def start_search(self):
        # Метод для начала поиска данных
        self.is_searching = True
        self.start_button.config(text="Стоп")  # Изменение надписи кнопки на "Стоп"
        self.clear_log()  # Очистка лога

        # Запуск нового потока для выполнения поиска данных
        t = threading.Thread(target=self.search)
        t.start()

    def stop_search(self):
        # Метод для остановки поиска данных
        self.is_searching = False
        self.log('Закончил работу')
        self.stop_event.set()  # Установка события для остановки поиска
        self.start_button.config(text="Начать")  # Изменение надписи кнопки на "Начать"

    def clear_log(self):
        # Метод для очистки текстового поля с логом
        self.log_text.delete("1.0", tk.END)

    def log(self, message):
        # Метод для записи сообщения в текстовое поле с логом
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def search(self):
        # Метод для выполнения поиска данных
        placed = {"Силикат", "Фрезер"}  # Площадки для парсинга

        for i in placed:
            if not self.is_searching:
                break  # Если поиск был остановлен, выйти из цикла

            self.log(f"Начинаю парсер площадки {i}")
            cells = sheetsearcher.start_search(i)  # Получение ячеек данных

            for cell in cells:
                if self.stop_event.is_set():
                    break  # Если поиск был остановлен, выйти из цикла

                if cell['value'] != "":
                    sheets_date = cell['to_date']

                    jira_date_set = jirasearcher.start_search(cell['value'])  # Поиск даты в Jira

                    jira_date_str = next(iter(jira_date_set))
                    jira_date_obj = datetime.strptime(jira_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                    formatted_jira_date = jira_date_obj.strftime('%d.%m.%Y')

                    if sheets_date == formatted_jira_date:
                        # Если дата в Google Sheets совпадает с датой в Jira, записать соответствующее сообщение в лог
                        self.log(f"{i} | {cell['value']} имеет правильную дату ТО {cell['to_date']}")
                    else:
                        try:
                            # Иначе, если даты не совпадают, заменить дату в Google Sheets на дату из Jira
                            self.log(f"{i} | Меняю дату для {cell['value']}")
                            sheetsearcher.replace_on_correct(cell['row'], formatted_jira_date, i)
                        except gspread.exceptions.APIError as e:
                            # Обработка ошибки API при слишком большом количестве запросов к Google Sheets
                            self.log(f"Ошибка, слишком много запросов в гугл. Перезапуск через 65 секунд...")
                            time.sleep(65)

        self.is_searching = False
        self.start_button.config(text="Начать")
        self.stop_event.clear()

    def run(self):
        # Метод для запуска GUI
        self.window.mainloop()



# Создаем экземпляр класса ParserGUI и запускаем при
parser_gui = ParserGUI()
parser_gui.window.mainloop()