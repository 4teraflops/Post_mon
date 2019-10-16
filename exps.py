import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

test_res = {}
urls = []


def create_urls_list():
    print("Составляю список ссылок для парсинга...", end="")
    with open('cods.txt', 'rU') as f:#читаем содержимое файла и превращаем его в список
        service_cods = f.read().split('\n')
    for s in service_cods:#теперь составляем список ссылок, которые будем тестить
        url = ('https://ckassa.ru/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(s)
        urls.append(url)
    print(" Ок")


def check_urls():
    driver = webdriver.Chrome('/home/sanaev-va/chromedriver')  # указал где брать гугл хром драйвер
    driver.implicitly_wait(10)# неявное ожидание драйвера
    driver.get(url)
    input_ls = driver.find_element_by_css_selector('input[type=text]')#нашел форму по css selector (скопировал из браузера)
    input_ls.send_keys('9659659659')#ввел несуществующий л/с
    input_ls.send_keys(Keys.TAB)#переключился на следующее поле
    wait = WebDriverWait(driver, 30)#Задал переменную, чтоб настроить явное ожидание элемента (сек)
    output_element = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="payMasksBlock"]/div/div[1]/div')))#ждем, пока элемент прогрузится
    output_text = output_element.text.split('\n')  # парсим из него текст
    print(f'{url} - {output_text}')#выводим
    test_res[url] = output_text#записываем его в общий список ответов
    driver.close()


if __name__ == "__main__":
    try:
        create_urls_list()
        for url in urls:#запуск перебора всех составленных ссылок
            check_urls()
        for key, value in test_res.items():
            print(key, value)
    except KeyboardInterrupt:
        print('Вы завершили работу программы. Закрываюсь.')


