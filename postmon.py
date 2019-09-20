import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

test_res = {}
with open('cods.txt', 'rU') as f:#читаем список из файла и превращаем его в список
    service_cods = f.read().split('\n')
urls = []
for s in service_cods:#теперь составляем список ссылок, которые будем тестить
    url = ('https://ckassa.ru/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(s)
    urls.append(url)


for url in urls:
    driver = webdriver.Chrome('/home/sanaev-va/chromedriver')
    driver.get(url)
    time.sleep(1.5)
    input_ls = driver.find_element_by_css_selector('input[type=text]')#нашел форму по css selector (скопировал из браузера)
    time.sleep(0.5)
    input_ls.send_keys('965557449')#ввел несуществующий л/с
    input_ls.send_keys(Keys.TAB)#переключился на следующее поле
    time.sleep(1)
    output_element = driver.find_element_by_xpath('//*[@id="payMasksBlock"]/div/div[1]/div')#ловим элемент с результатами теста
    output_text = output_element.text.split('\n')#парсим из него текст
    print(f'{url} - {output_text}')
    test_res[url] = output_text#записываем его в общий список ответов
    driver.close()

print(test_res)


#    def TearDown(self):
#        self.driver.close()

