import os
import sys
import itertools
from datetime import datetime
import time
import pickle
from selenium import webdriver
from threading import Thread
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

startTime = datetime.now()  # для замера времени исполнения скрипта

cd_dir_path = os.getcwd() + os.sep + 'chromedriver'  # Chrome Driver directory
db4replay_path = os.getcwd() + os.sep + 'res' + os.sep + 'db4replay.data'
urls = []  # общий список сгенерированных ссылок

db_first = 'first_db.data'
first_test_res = {}  # результат первого тестового прогона

res_4man_check = {}  # неопознанные ошбки
db_4man_check_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_4man_check.data'

res_with_valid = {}  # услуги без валидации
db_with_valid_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_with_valid.data'
a = 'не сработала валидация'  # вариант ошибок 1

res_bad_url = {}  # услуги, которые не открылись по ссылкам
db_bad_url_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_bad_url.data'
b = 'услуга по ссылке не найдена'  # вариант ошибок 2

res4_replay = {}
res4_replay_path = os.getcwd() + os.sep + 'res' + os.sep + 'db4replay.data'
c = 'не удалось загрузить страницу'  # вариант ошибок 3

res_with_format = {}  # услуги с другим форматом ввода данных
db_with_format_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_with_format.data'
word_with_format = {}
word_with_format_path = os.getcwd() + os.sep + 'words' + os.sep + 'with_format.txt'

word_ok_path = os.getcwd() + os.sep + 'words' + os.sep + 'ok.txt'
word_ok = {}
res_ok = {}  # услуги, по которым пройдена валидация
db_ok_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_ok.data'

res_errors = {}  # переменные для маппинга технических ошибок
db_errors_path = os.getcwd() + os.sep + 'words' + os.sep + 'db_errors.data'
word_errors_path = os.getcwd() + os.sep + 'words' + os.sep + 'errors.txt'
word_errors = {}


def create_urls_list():
    print("Составляю список ссылок для итераций...", end="")
    with open('cods.txt', 'rU') as f:  # читаем содержимое
        service_cods = f.read().split('\n')  # читаем пропуская перенос строки
    for s in service_cods:  # теперь составляем список ссылок, которые будем тестить
        url = ('http://10.10.137.23:8080/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(
            s)  # превращаем код услуги в ссылку для теста
        urls.append(url)  # запись в общий список ссылок
    print(" Ок")


def open_word(wordname, wordpath):  # открыть словарь по принципу предыдущей функции
    with open(wordpath, 'rU') as f:
        wordname = f.read().split('\n')
    return wordname


def check_urls(urls_list):
    for url in urls_list:  # запуск теста перебором всего списка ссылок
        chrome_options = Options()  # задаем параметры запуска драйвера, чтоб не крашился (когда работает во много потоков)
        chrome_options.add_argument('--headless')  # скрывать окна хрома
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(cd_dir_path, chrome_options=chrome_options)  # указал где брать гугл хром драйвер
        driver.implicitly_wait(3)  # неявное ожидание драйвера
        wait = WebDriverWait(driver, 3)  # Задал переменную, чтоб настроить явное ожидание элемента (сек)
        driver.get(url)
        try:
            input_ls = wait.until(EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="payMasksBlock"]/div/div[2]/input')))  # нашел форму по XPATH
            input_ls.send_keys('9659659659')  # ввел несуществующий л/с
            input_ls.send_keys(Keys.TAB)  # переключился на следующее поле
        except TimeoutException:  # если не удалось найти форму, генерим исключение и записываем его в общий результат
            try:  # ищем лого сайта (чтоб отличить загруженнуб страницу без услуги от незагруженной страницы)
                driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/table/tbody/tr/td[1]/div/img')
            except Exception:  # если лого нет, значит страница не прогрузилась
                print(f'{url} - {c}')
                first_test_res[url] = c
                driver.close()
                continue
            print(f'{url} - {b}')  # если лого есть, значит услуга не выведена
            first_test_res[url] = b  # и записываем его в общий список результатов
            driver.close()
            continue  # все записал - прервал итерацию, перешел к следующей
        try:
            output_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="payMasksBlock"]/div/div[1]/div')))  # ждем, пока элемент прогрузится
            output_text = output_element.get_attribute('innerHTML')  # парсим из него текст
            print(f'{url} - {output_text}')  # выводим результат
            first_test_res[url] = output_text  # записываем его в общий список ответов
        except TimeoutException:  # если по таймауту собрать не удалось, выводим исключение
            print(f'{url} - {a}')
            first_test_res[url] = a  # и записываем его в общий список результатов
        driver.quit()
    update_db(db_first, first_test_res)


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


def animate():  # анимация загрузки
    for cc in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rloading... This make take some time... ' + cc)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rDone!     ')


def route_answers():  # функция структурирования данных из первого словаря
    first_res = open_db(db_first, first_test_res)  # подгружаем собранные данные из чека ссылок
    word_ok_res = open_word(word_ok, word_ok_path)  # подгружаем словарь с норм результатами проверки
    word_format = open_word(word_with_format, word_with_format_path)  # подгружаем словарь с ошибками по формату
    word_errors_res = open_word(word_errors, word_errors_path)
    for key, value in first_res.items():
        if a == value:  # если сработало условие
            res_with_valid[key] = value  # записываем ключ и значение в отдельный словарь и файл
            update_db(db_with_valid_path, res_with_valid)
        elif b == value:
            res_bad_url[key] = value
            update_db(db_bad_url_path, res_bad_url)
        elif value in word_ok_res:
            res_ok[key] = 'ОК'  # заменяем значение ключа на ОК
            update_db(db_ok_path, res_ok)
        elif value == c:
            res4_replay[key] = value
            update_db(db4replay_path, res4_replay)
        elif value in word_errors_res:
            res_errors[key] = value
            update_db(db_with_format_path, res_errors)
        elif value in word_format:
            res_with_format[key] = value
            update_db(db_with_format_path, res_with_format)
        else:  # все, что не попало под условия записываем в неопознанные ошибки
            res_4man_check[key] = value
            update_db(db_4man_check_path, res_4man_check)

    print(
        f'\n \n Ссылки на услуги без валидации ({len(res_with_valid)}): \n')  # выводим итоговый список. Ссылки без валидации
    for key, value in res_with_valid.items():
        print(key, ' - ', value)
    print(f'\n Ссылки, по которым услуга не открылась ({len(res_bad_url)}):\n')
    for key, value in res_bad_url.items():
        print(key, ' - ', value)
    print(f'\n Ссылки, которые прошли проверку ({len(res_ok)}):\n')
    for key, value in res_ok.items():
        print(key, ' - ', value)
    print(f'\n Ссылки, которые не прогрузились и отложены на следующий тест ({len(res4_replay)}):\n')
    for key, value in res4_replay.items():
        print(key, ' - ', value)
    print(f'\n Ссылки, по которым скрипт не попал в формат ({len(res_with_format)}):\n')
    for key, value in res_with_format.items():
        print(key, ' - ', value)
    print(f'\nУслуги с техническими ошибками {len(res_errors)}:\n')
    for key, value in res_errors.items():
        print(key, ' - ', value)
    print(
        f'\n Ссылки на услуги с неопознанными ошибками ({len(res_4man_check)}): \n')  # список c неопознанными ошибками
    for key, value in res_4man_check.items():
        print(key, ' - ', value)

    print('\nИтого: \n')
    print(f'Услуги без валидации - {len(res_with_valid)}')
    print(f'Услуга не открылась - {len(res_bad_url)}')
    print(f'Услуги, которые OK - {len(res_ok)}')
    print(f'Сайт не прогрузил страницу - {len(res4_replay)}')
    print(f'Не попал в формат - {len(res_with_format)}')
    print(f'Технические ошибки на услуге - {len(res_errors)}')
    print(f'Неопознанный ответ - {len(res_4man_check)}')


if __name__ == "__main__":

    try:
        create_urls_list()
        urls1 = urls[0:500]  # разбиваем список на подсписки для потоков
        urls2 = urls[500:1000]
        urls3 = urls[1000:1500]
        urls4 = urls[1500:2000]
        urls5 = urls[2000:2500]
        urls6 = urls[2500:3000]
        threads = [Thread(target=check_urls, args=(urls1,)),
                   Thread(target=check_urls, args=(urls2,)),
                   Thread(target=check_urls, args=(urls3,)),
                   Thread(target=check_urls, args=(urls4,)),
                   Thread(target=check_urls, args=(urls5,)),
                   Thread(target=check_urls, args=(urls6,)),
                   ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        #        done = False#для анимации
        #        anim = threading.Thread(target=animate)#для запуска анимации
        #        anim.start()#start анимации
        #        done = True#стоп анимации
        route_answers()
        endtime = datetime.now()  # для замера времени исполнения скрипта
        print(f'Время выполнения:  {endtime - startTime}')
    except (KeyboardInterrupt, SystemExit):
        print('\nВы завершили работу программы. Закрываюсь.')
        done = True
