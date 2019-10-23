import os
import pickle
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


cd_dir_path = os.getcwd() + os.sep + 'chromedriver'#Chrome Driver directory
db4replay_path = os.getcwd() + os.sep + 'res' + os.sep + 'db4replay.data'
urls = []#список сгенерированных ссылок
db_first = 'first_db.data'
first_test_res = {}#результат первого тестового прогона
res_with_valid = {}#услуги без валидации
db_with_valid_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_with_valid.data'
res_4man_check = {}#неопознанные ошбки
db_4man_check_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_4man_check.data'
res_bad_url = {}#услуги, которые не открылись по ссылкам
db_bad_url_path = os.getcwd() + os.sep + 'res' + os.sep + 'db_bad_url.data'
res_ok = {}#услуги, по которым пройдена валидация
db_ok = os.getcwd() + os.sep + 'res' + os.sep + 'db_ok.data'
a = 'не сработала валидация'#вариант ошибок 1
b = 'услуга по ссылке не найдена'#вариант ошибок 2
word_ok_path = os.getcwd() + os.sep + 'words' + os.sep + 'ok.txt'
word_ok = {}


def create_urls_list():
    print("Составляю список ссылок для парсинга...", end="")
    with open('cods1.txt', 'rU') as f:#читаем содержимое
        service_cods = f.read().split('\n')#читаем пропуская перенос строки
    for s in service_cods:#теперь составляем список ссылок, которые будем тестить
        url = ('https://ckassa.ru/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(s)#превращаем код услуги в ссылку для теста
        urls.append(url)#запись в общий список ссылок
    print(" Ок")


def open_word(wordname, wordpath):#открыть словарь по принципу предыдущей функции
    with open(wordpath, 'rU') as f:
        wordname = f.read().split('\n')
    return wordname


def open_db(dbname, d_name):
    print(f'Загружаю данные из {dbname}...', end='')
    try:#подгружаем словарь
        f = open(dbname, 'rb')
        d_name = pickle.load(f)
        f.close()
        return d_name
    except EOFError:#если файл с данными пустой, то создаем новый словарь
        d_name = {}
        print(f'Хранилище {d_name} пустое, создаю новую переменную...')
    print('ok')


word = open_word(word_ok, word_ok_path)
word1 = open_db(db_first, first_test_res)
print(word1)
for key, value in word1.items():
    print(value)
    print(type(value))
print(type('fdg'))