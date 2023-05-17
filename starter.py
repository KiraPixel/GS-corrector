import json
import threading
import time

import gspread
import tkinter as tk
from datetime import datetime

from ttkbootstrap import Style, ttk
from ttkbootstrap.widgets import Button

import jirasearcher
import sheetsearcher


class ParserGUI:
    def __init__(self):
        # Инициализация GUI
        self.style = Style(theme='darkly')
        self.window = self.style.master
        self.window.title("Парсер данных")
        self.window.iconbitmap('icon.ico')
        self.window.geometry("400x450")
        self.window.resizable(True, False)

        # Создание меню
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)

        # Создание текстового поля для лога
        self.log_text = tk.Text(self.window, height=20)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Создание скроллбара и привязка его к текстовому полю
        scrollbar = ttk.Scrollbar(self.log_text, style='darkly.Vertical.TScrollbar')
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)

        # Чтение данных о площадках из config.json
        with open('config.json', 'r', encoding='utf-8') as file:
            config_data = json.load(file)
        placed_data = config_data if isinstance(config_data, dict) else {}
        # Создание кнопок для каждой площадки и кнопка "Стоп"
        self.placed_buttons = []
        for placed_name in placed_data:
            button_text = placed_name
            button = Button(
                self.window,
                text=button_text,
                command=lambda placed=placed_name: self.start_search(placed),
                style='primary.TButton'
            )
            button.pack(side='left', padx=5, pady=5)
            self.placed_buttons.append(button)

        self.stop_button = Button(
            self.window,
            text="Остановить",
            command=self.stop_search,
            style='danger.TButton'
        )
        self.stop_button.pack(side='left', padx=5, pady=5)
        self.stop_button.configure(state=tk.DISABLED)

        # Инициализация переменных состояния
        self.is_searching = False
        self.stop_event = threading.Event()

    def start_search(self, placed_info):
        # Метод для начала поиска данных для конкретной площадки
        self.is_searching = True
        self.clear_log()

        for button in self.placed_buttons:
            button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)

        t = threading.Thread(target=self.search, args=(placed_info,))
        t.start()

    def stop_search(self):
        # Метод для остановки поиска данных
        self.is_searching = False
        for button in self.placed_buttons:
            button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
        self.log('Закончил работу')
        self.stop_event.set()
    def clear_log(self):
        # Метод для очистки текстового поля с логом
        self.log_text.delete("1.0", tk.END)

    def log(self, message):
        # Метод для записи сообщения в текстовое поле с логом
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def search(self, placed_name):
        # Метод для выполнения поиска данных для конкретной площадки
        self.log(f"Начинаю парсер площадки {placed_name}")
        cells = sheetsearcher.start_search(placed_name)

        for cell in cells:
            if self.stop_event.is_set():
                break

            if cell['value'] != "":
                sheets_date = cell['to_date']

                jira_date_set = jirasearcher.start_search(cell['value'])  # Поиск даты в Jira

                jira_date_str = next(iter(jira_date_set))
                jira_date_obj = datetime.strptime(jira_date_str, '%Y-%m-%dT%H:%M:%S.%f%z')
                formatted_jira_date = jira_date_obj.strftime('%d.%m.%Y')

                if sheets_date == formatted_jira_date:
                    # Если дата в Google Sheets совпадает с датой в Jira, записать соответствующее сообщение в лог
                    self.log(f"{placed_name} | {cell['value']} имеет правильную дату ТО {cell['to_date']}")
                else:
                    try:
                        # Иначе, если даты не совпадают, заменить дату в Google Sheets на дату из Jira
                        self.log(f"{placed_name} | Меняю дату для {cell['value']}")
                        sheetsearcher.replace_on_correct(cell['row'], formatted_jira_date, placed_name)
                    except gspread.exceptions.APIError as e:
                        # Обработка ошибки API при слишком большом количестве запросов к Google Sheets
                        self.log(f"Ошибка, слишком много запросов в гугл. Перезапуск через 65 секунд...")
                        time.sleep(65)

        self.stop_search()
        self.stop_event.clear()

    def run(self):
        # Метод для запуска GUI
        self.window.mainloop()


# Создаем экземпляр класса ParserGUI и запускаем приложение
parser_gui = ParserGUI()
parser_gui.run()
