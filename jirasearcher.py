from jira import JIRA
import json

with open('jira.json', 'r') as f:
    config = json.load(f)


def start_search(gov_number, jira_project):
    # данные для входа
    jira_url = config['jira']['url']
    jira_username = config['jira']['username']
    jira_password = config['jira']['password']

    # Авторизуемся в Jira
    jira = JIRA(jira_url, basic_auth=(jira_username, jira_password))

    # Формируем запрос на поиск задачи
    jql = f'project = {jira_project} AND issuetype = "Запрос на обслуживание" AND status in (Закрыта, Выполнена) AND  ("Гаражный номер" ~ "{gov_number}" OR "Государственный номер" ~ "{gov_number}") ORDER BY created DESC'
    # Ищем задачи, соответствующие запросу
    issues = jira.search_issues(jql, maxResults=1)

    if issues:
        # Получаем первую найденную задачу
        issue = issues[0]
        # Выводим дату создания задачи
        return ({issue.fields.created})
    else:
        return None
