import time
import requests
import threading

c1 = 'ETH'
c2 = 'BTC'

# Глобальный словарь, куда каждый поток складывает полученную информацию
stock_rates = {'exmo': 0, 'binance': 0, 'bittrex': 0}


# Получить последнюю цену с Эксмо
def get_exmo_rates(pair):
    while True:
        try:
            stock_rates['exmo'] = requests.get("https://api.exmo.com/v1/ticker/".format(pair=pair)).json()[pair][
                'last_trade']
        except Exception as e:
            print(e)
        time.sleep(0.5)


# Получить последнюю цену с Binance
def get_binance_rates(pair):
    while True:
        try:
            stock_rates['binance'] = \
            requests.get("https://api.binance.com/api/v3/ticker/price?symbol={pair}".format(pair=pair)).json()['price']
        except Exception as e:
            print(e)
        time.sleep(0.5)


# Получить последнюю цену с Bittrex
def get_bittrex_rates(pair):
    while True:
        try:
            stock_rates['bittrex'] = \
            requests.get("https://bittrex.com/api/v1.1/public/getticker?market={pair}".format(pair=pair)).json()[
                'result']['Last']
        except Exception as e:
            print(e)
        time.sleep(0.5)


def show_results():
    while True:
        print(stock_rates)
        time.sleep(1)


global_start_time = time.time()

threads = []

# Подготавливаем потоки, складываем их в массив
exmo_thread = threading.Thread(target=get_exmo_rates, args=(c1 + '_' + c2,))
binance_thread = threading.Thread(target=get_binance_rates, args=(c1 + c2,))
bittrex_thread = threading.Thread(target=get_bittrex_rates, args=(c2 + '-' + c1,))
show_results_thread = threading.Thread(target=show_results)

threads.append(exmo_thread)
threads.append(binance_thread)
threads.append(bittrex_thread)
threads.append(show_results_thread)

# Запускаем каждый поток
for thread in threads:
    thread.start()

# Ждем завершения каждого потока
for thread in threads:
    thread.join()