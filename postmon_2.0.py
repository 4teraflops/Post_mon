import os
import pickle
import requests
import json
import time
from datetime import datetime

s = requests.Session()
urls = []
urlsA = []
start_time = datetime.now()

db_first = 'first_db.data'
first_test_res = {}

res_with_format = {}  # услуги с другим форматом ввода данных
db_with_format_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_with_format.data'
word_with_format = {}
word_with_format_path = os.getcwd() + os.sep + 'words' + os.sep + 'with_format.txt'
d = 'не попал в формат'

word_ok_path = os.getcwd() + os.sep + 'words' + os.sep + 'ok.txt'
word_ok = {}
res_ok = {}  # услуги, по которым пройдена валидация
db_ok_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_ok.data'

res_errors = {}  # переменные для маппинга технических ошибок
db_errors_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_errors.data'
word_errors_path = os.getcwd() + os.sep + 'words' + os.sep + 'errors.txt'
word_errors = {}

res_bad_url = {}  # услуги, которые не открылись по ссылкам
db_bad_url_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_bad_url.data'

res_4man_check = {}  # неопознанные ошбки
db_4man_check_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_4man_check.data'

res_A = {} #  Словарь для клиентов классаА


def create_urls_list():
    print("Составляю список ссылок для итераций...", end="")
    with open('cods.txt', 'rU') as f:  # читаем содержимое со всеми кодами услуг
        service_cods = f.read().split('\n')  # читаем, считая перенос строки за разделитель
    with open('stop_list_cods.txt',
              'rU') as f:  # читаем содержимое файла со стоп листом (те услуги, которые не надо чекать)
        stop_list_cods = f.read().split('\n')  # записываем все ненужные коды в переменную
    for s in service_cods:  # теперь составляем список ссылок, которые будем тестить
        if s not in stop_list_cods:
            # превращаем код услуги в ссылку для теста (отсекая коды из стоп листа)
            url = (
                    'https://uat.autopays.ru/api-shop/rs/shop/test?sec-key=96abc9ad-24dc-4125-9fc4-a8072f7b83c3&service-code=' + '{}').format(
                s)
            urls.append(url)  # запись в общий список ссылок
    print(" Ок")
    # если надо будет чекнуть сколько кодов услуг отсечено, выводим метрики и смотрим.
    # print(f'Service cods - {len(service_cods)}')
    # print(f'Stop list - {len(stop_list_cods)}')
    # print(f'Urls - {len(urls)}')
    # print(f'Отсечено - {(len(service_cods) - len(urls))}')


def update_db(dbname, dictname):
    f = open(dbname, 'wb')
    pickle.dump(dictname, f)
    f.close()


def open_db(dbname, d_name):
    print(f'\nЗагружаю данные из {dbname}...', end='')
    try:  # подгружаем словарь
        f = open(dbname, 'rb')
        d_name = pickle.load(f)
        f.close()
        return d_name
    except EOFError:  # если файл с данными пустой, то создаем новый словарь
        d_name = {}
        print(f'Хранилище {d_name} пустое, создаю новую переменную...')
    print('ok')


def open_word(wordname, wordpath):  # открыть словарь по принципу предыдущей функции
    with open(wordpath, 'rU') as f:
        wordname = f.read().split('\n')
    return wordname


def open_urls():
    for url in urls:
        r = s.get(url)
        # парсим текст, заменяя начало (оно у всех ошибок одинаковое, заменяем его на None)
        error_text = r.text.replace('--ERROR--\ncom.techinfocom.bisys.pay.utils.shared.exception.', '')
        # убираем из строки лишнее, оставляем только код услуги
        code = url.replace(
            'https://uat.autopays.ru/api-shop/rs/shop/test?sec-key=96abc9ad-24dc-4125-9fc4-a8072f7b83c3&service-code=',
            '')
        first_test_res[code] = [r.status_code, error_text]
        print(first_test_res[code])
        update_db(db_first, first_test_res)


def p_res(item_name):  # печать словаря
    for key, value in item_name.items():
        print(f'{key} - {value}')


def route_answers():
    first_res = open_db(db_first, first_test_res)  # подгружаем собранные данные из проверки ссылок
    word_ok_res = open_word(word_ok, word_ok_path)  # подгружаем словарь с норм результатами проверки
    word_format = open_word(word_with_format, word_with_format_path)  # подгружаем словарь с ошибками по формату
    word_errors_res = open_word(word_errors, word_errors_path)  # подгружаем словарь с тех. ошибками
    # структурируем полученную инфу
    for key, value in first_res.items():
        if value[0] == 200 or value[1] in word_ok_res:
            res_ok[key] = 'ok'
        elif value[0] == 400 and value[1] == 'provider == null':
            res_bad_url[key] = 'услуга не найдена'
        elif value[1] in word_errors_res:
            res_errors[key] = value[1]
        elif value[1] in word_format:
            res_with_format[key] = value[1]
        else:
            res_4man_check[key] = value[1]
    # Апдейтим данные в файл
    update_db(db_ok_path, res_ok)
    update_db(db_bad_url_path, res_bad_url)
    update_db(db_errors_path, res_errors)
    update_db(db_with_format_path, res_with_format)

    # выводим на печать услуги, прошедшие проверку
    print(f'\n \n Услуги ОК ({len(res_ok)}): \n')
    p_res(res_ok)
    # выводим на печать услуги, которые не найдены
    print(f'\nУслуги, которые не были найдены ({len(res_bad_url)}): \n')
    p_res(res_bad_url)
    # выводим на печать технические ошибки
    print(f'\nУслуги с техническими ошибками ({len(res_errors)}): \n')
    p_res(res_errors)
    # выводим на печать неразобранные ошибки
    print(f'\n Неопознанные ошибки ({len(res_4man_check)}): \n')
    p_res(res_4man_check)

    # выводим итоговые цифры
    print('\nИтого: \n')
    print(f'Услуги ОК: {len(res_ok)}')
    print(f'Услуги, которые не выведены: {len(res_bad_url)}')
    print(f'Услуги с техническими ошибками: {len(res_errors)}')
    print(f'Неопознанные ошибки на услугах: {len(res_4man_check)}')
    print(f'Услуги, по которым не попал в формат: {len(res_with_format)}')

    #  Теперь чекнем есть ли в ошибках клиенты класса А
    with open('codsA.txt', 'rU') as f:
        codsA = f.read().split('\n')

    #  вытаскиваем все ключи из списков тех. ошибок и неопознанных ошибок и складываем в отдельный словарь

    for key in res_errors.keys():
        if key in codsA:
            res_A[key] = res_errors[key]

    for key in res_4man_check:
        if key in codsA:
            res_A[key] = res_4man_check[key]

    #  выводим на печать результат, если есть что печатать
    if len(codsA) >= 0:
        print('\n Ошибки по клиентам класса А: ')
        for key, value in res_A.items():
            alarmtext = f'{key} - {value}'
            print(alarmtext)
            do_alarm(alarmtext)
            print('Сообщения отправлены в Slack')


def do_alarm(alarmtext):  # отправка сообщения в канал slack
    headers = {"Content-type": "application/json"}
    url = "https://hooks.slack.com/services/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"
    payload = {"text": f"{alarmtext}"}
    r = requests.post(url, headers=headers, data=json.dumps(payload))


if __name__ == '__main__':

    try:
        while True:
            # create_urls_list()
            # open_urls()
            route_answers()
            end_time = datetime.now()  # для рассчета времени выполнения скрипта
            work_time = end_time - start_time  # рассчет времени вполнения скрипта
            print(f'Время исполнения: {work_time}')
            time.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        print('\nВы завершили работу программы. Закрываюсь.')