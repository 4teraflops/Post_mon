

#url = ('https://ckassa.ru/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(service_code)


with open('cods.txt', 'rU') as f:#читаем список из файла и превращаем его в список
    service_cods = f.read().split('\n')
urls = []
for s in service_cods:#теперь составляем список ссылок, которые будем тестить
    url = ('https://ckassa.ru/payment/#!search_provider/pt_search/' + '{}' + '/pay').format(s)
    urls.append(url)






