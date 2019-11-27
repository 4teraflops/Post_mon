import os
import pickle
import requests
from datetime import datetime

s = requests.Session()
urls = []
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
db_errors_path = os.getcwd() + os.sep + 'words' + os.sep + 'db_errors.data'
word_errors_path = os.getcwd() + os.sep + 'words' + os.sep + 'errors.txt'
word_errors = {}

res_bad_url = {}  # услуги, которые не открылись по ссылкам
db_bad_url_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_bad_url.data'


def create_urls_list():
    print("Составляю список ссылок для итераций...", end="")
    with open('cods1.txt', 'rU') as f:  # читаем содержимое со всеми кодами услуг
        service_cods = f.read().split('\n')  # читаем пропуская перенос строки
    with open('stop_list_cods.txt', 'rU') as f:  # читаем содержимое файла со стоп листом (те услуги, которые не надо чекать)
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
#    print(f'Service cods - {len(service_cods)}')
#    print(f'Stop list - {len(stop_list_cods)}')
#    print(f'Urls - {len(urls)}')
#    print(f'Отсечено - {(len(service_cods) - len(urls))}')


def update_db(dbname, dictname):
    f = open(dbname, 'wb')
    pickle.dump(dictname, f)
    f.close()


def open_db(dbname, d_name):
    print(f'Загружаю данные из {dbname}...', end='')
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
        # убираем из строки лишнее, оставляем только код услуги
        code = url.replace(
            'https://uat.autopays.ru/api-shop/rs/shop/test?sec-key=96abc9ad-24dc-4125-9fc4-a8072f7b83c3&service-code=',
            '')
        first_test_res[code] = [r.status_code, r.text]
        print(first_test_res[code])
        update_db(db_first, first_test_res)


def route_answers():
    first_res = open_db(db_first, first_test_res)  # подгружаем собранные данные из чека ссылок
    word_ok_res = open_word(word_ok, word_ok_path)  # подгружаем словарь с норм результатами проверки
    word_format = open_word(word_with_format, word_with_format_path)  # подгружаем словарь с ошибками по формату
    word_errors_res = open_word(word_errors, word_errors_path)
    for key, value in first_res.items():
        if value[0] == 200:
            res_ok[key] = 'ok'
        elif value[0] == 400 and value[1] == 'provider == null':
            res_bad_url[key] = 'услуга не найдена'



if __name__ == '__main__':

    try:
        create_urls_list()
        open_urls()
        route_answers()
        end_time = datetime.now()  # для рассчета времени выполнения скрипта
        work_time = end_time - start_time  # рассчет времени вполнения скрипта
        print(f'Время исполнения: {work_time}')
    except (KeyboardInterrupt, SystemExit):
        print('\nВы завершили работу программы. Закрываюсь.')
