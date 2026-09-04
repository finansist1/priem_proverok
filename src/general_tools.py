import requests
import json
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, PROXY_TOKEN








def send_message_to_tg(text: str):
    """Функция отправляет данные о новой проверке в телеграм канал"""

    params = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text
    }

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

    requests.post(url=url, json=params)


def format_data_to_uat(data_from_user: dict) -> dict:
    """Функция формиурет структуру для отправки данных в 1с"""

    structrura_json = {
            'NameOfProject': data_from_user.get('name'),
            'AccountNum': data_from_user.get('account_num'),
            'Proverka': data_from_user.get('num_proverki'),
            'Income': data_from_user.get('income'),
            'Expense': data_from_user.get('expense'),
            'Fine': data_from_user.get('fine'),
            'Prepayment': data_from_user.get('prepayment'),
            'Fuel': data_from_user.get('fuel'),
            'StartDate': data_from_user.get('start_date'),
            'EndDate': data_from_user.get('end_date')        
    }

    return structrura_json


def send_request_to_1c(data=None, endpoint=None):
    """Функция отправляет запрос в 1с на указанный endpoint с указанным методом"""

    url_1c = f'http://82.146.63.191:8111/1c_proxy/{endpoint}'

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': PROXY_TOKEN
    }

    if data is None:
        response = requests.get(url=url_1c, headers=headers)
    else:
        response = requests.post(url=url_1c, headers=headers, json=data)

    return response


def get_business_lines():
    """Функция получает список наименований направлений деятельности из 1с"""

    endpoint = 'business-lines'

    response = send_request_to_1c(endpoint=endpoint).json()

    list_of_business_lines = [el.get('Наименование') for el in response]

    return list_of_business_lines


def get_num_inspections():
    """Функция получает список счетов проверок оплат из 1с"""

    endpoint = 'num_inspections'

    response = send_request_to_1c(endpoint=endpoint)

    data = response.content.decode("utf-8-sig")

    list_of_nums_inspections = [el["Наименование"] for el in json.loads(data)]

    return list_of_nums_inspections


def get_account_nums():
    """Функция получает список номеров счетов перевозчика из 1с"""

    endpoint = 'account_num'

    response = send_request_to_1c(endpoint=endpoint)

    data = response.content.decode("utf-8-sig")

    list_of_account_nums = [el["Наименование"] for el in json.loads(data)]

    return list_of_account_nums


def prepare_numbers_to_send(**kwargs):
    "Функция приводит числовые данные к корректному виду"

    for key, value in kwargs.items():

        if value is None or value == "" or str(value).isspace() == True:
            value = 0
            kwargs[key] = value
        else: 
            value = float(str(value).strip().replace(" ", "").replace(",", ".").replace("\xa0", ""))
            kwargs[key] = value

    return kwargs