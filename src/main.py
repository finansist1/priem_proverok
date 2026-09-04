from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from src.general_tools import (
    send_message_to_tg,
    send_request_to_1c,
    format_data_to_uat,
    get_business_lines,
    get_num_inspections,
    get_account_nums,
    prepare_numbers_to_send
)
from datetime import datetime


app = FastAPI()

templates = Jinja2Templates(directory="template")


@app.get('/proverka')
def render_template(request: Request):
    """Отпраляет на клиент форму для сдачи проверки"""

    list_of_business_lines = get_business_lines()    # Получение списка направлений деятельности
    list_of_nums_inspections = get_num_inspections()    # Получение списка счетов проверок оплат
    list_of_account_nums = get_account_nums()    # получение списка счетов перевозчиков

    return templates.TemplateResponse(
        request,
        'forma.html',
        {
            "business_lines": list_of_business_lines,
            "nums_inspections": list_of_nums_inspections,
            "account_nums": list_of_account_nums
        },
    )



@app.post('/senddata')
def get_data_from_front(data: dict):
    """Получение данных от пользователя с формы, приведение числовых згначений к корректному виду и отпарвка их в телеграмм, и в 1с"""

    data_to_send = dict()

    prepared_data = prepare_numbers_to_send(income=data.get('income'),
                             expense=data.get('expense'),
                             fine=data.get('fine'),
                             prepayment=data.get('prepayment'),
                             fuel=data.get('fuel')
                            )

    data_to_send['name'] = data.get('name')
    data_to_send['num_proverki'] = data.get('num_proverki')
    data_to_send['income'] = prepared_data.get('income')
    data_to_send['expense'] = prepared_data.get('expense')
    data_to_send['fine'] = prepared_data.get('fine')
    data_to_send['fuel'] = prepared_data.get('fuel')
    data_to_send['prepayment'] = prepared_data.get('prepayment')
    data_to_send['start_date'] = data.get('start_date')
    data_to_send['end_date'] = data.get('end_date')
    data_to_send['account_num'] = data.get('account_num')
    data_to_send['comment'] = data.get('comment')      


    start_date_obj = datetime.strptime(data_to_send.get('start_date'), '%Y-%m-%d').strftime('%d.%m.%Y')
    end_date_obj = datetime.strptime(data_to_send.get('end_date'), '%Y-%m-%d').strftime('%d.%m.%Y')


    message = (
        f'{data_to_send.get('name')}\n'
        f'{start_date_obj} - {end_date_obj}\n'
        f'--------------------------------\n'
        f'Счет проверки: {data_to_send.get('num_proverki')}\n'
        f'Счет перевозчика: {data_to_send.get('account_num')}\n'
        f'Сумма дохода: {data_to_send.get('income')}\n'
        f'Сумма расхода: {data_to_send.get('expense')}\n'
        f'Сумма топлива: {data_to_send.get('fuel')}\n'
        f'Штраф: {data_to_send.get('fine')}\n'
        f'Аванс: {data_to_send.get('prepayment')}\n'
        f'--------------------------------\n'
        f'Комментарий: {data_to_send.get('comment')}'
    )

    send_message_to_tg(text=message)
    response_1c = send_request_to_1c(data=format_data_to_uat(data_from_user=data_to_send),endpoint='accept_inspections')

    report_text = response_1c.content.decode("utf-8-sig")

    print(report_text)