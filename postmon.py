import os
import pickle
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

cd_dir = os.getcwd() + os.sep + 'chromedriver'
urls = []#список сгенерированных ссылок
test_res = {}#результат общего прогона


def create_urls_list():
    print("Составляю список ссылок для парсинга...", end="")
    with open('cods.txt', 'rU') as f:#читаем содержимое
        service_cods = f.read().split('\n')#читаем пропуская перенос строки
    for s in service_cods:#теперь составляем список ссылок, которые будем тестить
        url = ('https://ckassa.ru/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(s)#превращаем код услуги в ссылку для теста
        urls.append(url)#запись в общий список ссылок
    print(" Ок")


def check_urls():
    for url in urls:#запуск теста перебором всего списка ссылок
        driver = webdriver.Chrome(cd_dir)# указал где брать гугл хром драйвер
        driver.implicitly_wait(5)# неявное ожидание драйвера
        wait = WebDriverWait(driver, 5)  # Задал переменную, чтоб настроить явное ожидание элемента (сек)
        driver.get(url)
        try:
            input_ls = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="payMasksBlock"]/div/div[2]/input')))#нашел форму по XPATH
            input_ls.send_keys('9659659659')  # ввел несуществующий л/с
            input_ls.send_keys(Keys.TAB)  # переключился на следующее поле
        except TimeoutException:#если не удалось найти форму, генерим исключение и записываем его в общий результат
            try:#ищем лого сайта (чтоб отличить загруженнуб страницу без услуги от незагруженной страницы)
                driver.find_element_by_xpath('/html/body/div[2]/div[1]/div/table/tbody/tr/td[1]/div/img')
            except Exception:#если лого нет, то страница не прогрузилась
                print(f'{url} - не удалось загрузить страницу')
                test_res[url] = 'не удалось загрузить страницу'
                continue
            print(f'{url} - услуга по ссылке не выведена')#если лого есть, значит услуга не выведена
            test_res[url] = 'услуга по ссылке не выведена'  #и записываем его в общий список результатов
            driver.close()
            continue#все записал - прервал итерацию, перешел к следующей

        try:
            output_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="payMasksBlock"]/div/div[1]/div')))#ждем, пока элемент прогрузится
            output_text = output_element.text.split('\n')  # парсим из него текст
            print(f'{url} - {output_text}')  # выводим результат
            test_res[url] = output_text  # записываем его в общий список ответов
        except TimeoutException:#если по таймауту собрать не удалось, выводим исключение
            print(f'{url} - не сработала валидация')
            test_res[url] = 'не сработала валидация'  #и записываем его в общий список результатов
        driver.close()


#def save_to_bd():
#    f= open()



if __name__ == "__main__":
    try:
        create_urls_list()
        check_urls()
    except KeyboardInterrupt:
        print('Вы завершили работу программы. Закрываюсь.')


