import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta, date


class Portfolio:
    def __init__(self):
        # считываем данные
        self.currencies = pd.read_csv('files/currencies.csv', index_col='id', sep=',')
        self.prices = pd.read_csv('files/prices.csv', index_col='date', parse_dates=True, sep=',')
        self.weights = pd.read_csv('files/weights.csv', index_col='date', parse_dates=True, sep=',')
        self.exchanges = pd.read_csv('files/exchanges.csv', index_col='date', parse_dates=True, sep=',')
        # создаем массив с id интересующих нас активов
        self.ids = self.currencies.index

    # извлечение из таблицы ближайших к указанной дате данных (от прошедших дней)
    def get_last_valid_data(self, dataframe, date):
        if date in dataframe.index:
            return dataframe.loc[date]
        else:
            # ищем последние актуальные данные
            while True:
                date -= timedelta(days=1)
                # если находим в таблице дату, выходим
                if date in dataframe.index:
                    return dataframe.loc[date]

    def calculate_asset_performance(self, start_date, end_date):
        # ограничиваем начальную и конечную даты граничными данными таблиц
        # можно было, конечно, взять максимин и минимакс по датам из всех таблиц
        if start_date < date(2014, 1, 14) or end_date > date(2018, 3, 5):
            raise Exception('Not enough initial data in tables.')
        # берем из таблиц столбцы по интересующим нас id активов
        prices = self.prices[self.ids]
        weights = self.weights[self.ids]
        # структура для ответа
        asset_performance = pd.Series([])
        # диапазон пробега по датам
        dates = pd.date_range(start_date, end_date)
        # первый день
        asset_performance[dates[0]] = 1
        # цена в рассматриваемый день
        curr_price = self.get_last_valid_data(prices, dates[0])
        for i in range(1, len(dates)):
            # цена в предыдущий день
            prev_price = curr_price
            curr_price = self.get_last_valid_data(prices, dates[i])
            # веса в рассматриваемый день
            curr_weight = self.get_last_valid_data(weights, dates[i])
            # считаем элемент искомого массива за текущую дату
            asset_performance[dates[i]] = asset_performance[dates[i-1]] \
                    * (1 + ((curr_price - prev_price) / prev_price * curr_weight).sum())
        return asset_performance

    def calculate_currency_performance(self, start_date, end_date):
        # ограничиваем начальную и конечную даты граничными данными таблиц
        if start_date < date(2014, 1, 14) or end_date > date(2018, 3, 5):
            raise Exception('Not enough initial data in tables.')
        # берем из таблицы столбцы по интересующим нас id активов
        weights = self.weights[self.ids]
        # выделяем валюты, отличные от USD
        currencies = self.currencies[self.currencies.currency != 'USD']['currency'].drop_duplicates()
        # структура для ответа
        currency_performance = pd.Series([])
        # диапазон пробега по датам
        dates = pd.date_range(start_date, end_date)
        # первый день
        currency_performance[dates[0]] = 1
        # структура с валютами и курсами обмена для всех активов в рассматриваемый день
        # для USD курс = 1
        curr_exchange = pd.DataFrame({
            'currency': self.currencies.currency,
            'rate': [1] * len(self.currencies)
        })
        # обновляем курсы для отличных от USD валют
        for currency in currencies:
            curr_exchange.loc[curr_exchange.currency == currency, 'rate'] = self.get_last_valid_data(
                    self.exchanges, dates[0])[currency]
        for i in range(1, len(dates)):
            # структура с валютами и курсами обмена для всех активов в предыдущий день
            prev_exchange = curr_exchange
            curr_exchange = pd.DataFrame({
                'currency': self.currencies.currency,
                'rate': [1] * len(self.currencies)
            })
            for currency in currencies:
                curr_exchange.loc[curr_exchange.currency == currency, 'rate'] = self.get_last_valid_data(
                    self.exchanges, dates[i])[currency]
            # веса в рассматриваемый день
            curr_weight = self.get_last_valid_data(weights, dates[i])
            # считаем элемент искомого массива за текущую дату
            currency_performance[dates[i]] = currency_performance[dates[i - 1]] \
                    * (1 + ((curr_exchange.rate - prev_exchange.rate) / prev_exchange.rate * curr_weight).sum())
        return currency_performance

    def calculate_total_performance(self, start_date, end_date):
        # ограничиваем начальную и конечную даты граничными данными таблиц
        if start_date < date(2014, 1, 14) or end_date > date(2018, 3, 5):
            raise Exception('Not enough initial data in tables.')
        # берем из таблиц столбцы по интересующим нас id активов
        weights = self.weights[self.ids]
        prices = self.prices[self.ids]
        # выделяем валюты, отличные от USD
        currencies = self.currencies[self.currencies.currency != 'USD']['currency'].drop_duplicates()
        # структура для ответа
        total_performance = pd.Series([])
        # диапазон пробега по датам
        dates = pd.date_range(start_date, end_date)
        # первый день
        total_performance[dates[0]] = 1
        # цена в рассматриваемый день
        curr_price = self.get_last_valid_data(prices, dates[0])
        # структура с валютами и курсами обмена для всех активов в рассматриваемый день
        # для USD курс = 1
        curr_exchange = pd.DataFrame({
            'currency': self.currencies.currency,
            'rate': [1] * len(self.currencies)
        })
        # обновляем курсы для отличных от USD валют
        for currency in currencies:
            curr_exchange.loc[curr_exchange.currency == currency, 'rate'] = self.get_last_valid_data(
                    self.exchanges, dates[0])[currency]
        for i in range(1, len(dates)):
            # цена в предыдущий день
            prev_price = curr_price
            # структура с валютами и курсами обмена для всех активов в предыдущий день
            prev_exchange = curr_exchange
            curr_price = self.get_last_valid_data(prices, dates[i])
            curr_exchange = pd.DataFrame({
                'currency': self.currencies.currency,
                'rate': [1] * len(self.currencies)
            })
            for currency in currencies:
                curr_exchange.loc[curr_exchange.currency == currency, 'rate'] = self.get_last_valid_data(
                    self.exchanges, dates[i])[currency]
            # веса в рассматриваемый день
            curr_weight = self.get_last_valid_data(weights, dates[i])
            # считаем элемент искомого массива за текущую дату
            total_performance[dates[i]] = total_performance[dates[i - 1]] \
                    * (1 + ((curr_exchange.rate * curr_price - prev_exchange.rate * prev_price)
                    / (prev_exchange.rate * prev_price) * curr_weight).sum())
        return total_performance


if __name__ == '__main__':
    port1 = Portfolio()
    res = port1.calculate_total_performance(date(2015, 1, 29), date(2016, 1, 31))
    res.plot()
    plt.show()
