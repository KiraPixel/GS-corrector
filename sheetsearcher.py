import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

# настройки доступа к таблице
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)


class Placed:
    def __init__(self, placed_name):
        with open('config.json', 'r', encoding='utf-8') as file:
            config_data = json.load(file)
        data = config_data if isinstance(config_data, dict) else {}

        self.placed_data = data[placed_name]
        self.start_row = self.placed_data['start_row']
        self.column_value = self.placed_data['garage_num_row']
        self.column_date = self.placed_data['date_row']
        self.sheet_name = self.placed_data['sheet_name']
        self.sheet_url = self.placed_data['google_sheet_link']


def start_search(placed_name):
    placed_data = Placed(placed_name)
    # открываем таблицу по URL-адресу
    sheet = client.open_by_url(placed_data.sheet_url)
    worksheet = sheet.worksheet(placed_data.sheet_name)

    # получаем значения и номера ячеек столбца
    value_range = worksheet.range(placed_data.start_row, placed_data.column_value, worksheet.row_count, placed_data.column_value)
    date_range = worksheet.range(placed_data.start_row, placed_data.column_date, worksheet.row_count, placed_data.column_date)
    cells = [{'value': value_cell.value, 'row': value_cell.row, 'col': value_cell.col,
              'to_date': date_cell.value} for value_cell, date_cell in zip(value_range, date_range)]

    return cells


# корректор дат
def replace_on_correct(row, new_date, placed_name):
    placed_data = Placed(placed_name)
    sheet = client.open_by_url(placed_data.sheet_url)
    worksheet = sheet.worksheet(placed_data.sheet_name)
    worksheet.update_cell(row, placed_data.column_date, new_date)