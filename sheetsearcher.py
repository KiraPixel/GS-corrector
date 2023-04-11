import gspread
from oauth2client.service_account import ServiceAccountCredentials

# настройки доступа к таблице
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('creds.json', scope)
client = gspread.authorize(creds)

# открываем таблицу по URL-адресу
sheet_url = 'https://docs.google.com/spreadsheets/d/1uhEHYOq5Xu66lznlwJ9yVs05nGN664yLGkAX-OHw5XY/edit#gid=0'
sheet = client.open_by_url(sheet_url)

# задаем необходимые столбы и колонки
start_row = 2
column_value = 3
column_date = 6


def start_search(sheet_name):
    worksheet = sheet.worksheet(sheet_name)

    # получаем значения и номера ячеек столбца
    value_range = worksheet.range(start_row, column_value, worksheet.row_count, column_value)
    date_range = worksheet.range(start_row, column_date, worksheet.row_count, column_date)
    cells = [{'value': value_cell.value, 'row': value_cell.row, 'col': value_cell.col,
              'to_date': date_cell.value} for value_cell, date_cell in zip(value_range, date_range)]

    return cells


# корректор дат
def replace_on_correct(row, new_date,sheet_name):
    worksheet = sheet.worksheet(sheet_name)
    worksheet.update_cell(row, column_date, new_date)