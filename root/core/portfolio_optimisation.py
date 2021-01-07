import os # для работы с файловой системой
import pandas as pd # для создания датафреймов
import numpy as np # для математических преобразований
import datetime as dt # для работы с датами
import pandas_datareader.data as web # для загрузки данных из веба
from dateutil.relativedelta import relativedelta # для математических вычислений с датами
from scipy.optimize import minimize # для оптимизационной функции
import json # для работы с данными в представлении JSON

start = dt.datetime(2019, 1, 1) # самая ранняя дата периода, за который будем загружать информацию
today = dt.datetime.now() # самая поздняя дата периода, за который будем загружать информацию, т.е. сегодня

def stock_data(tickers):
    """
    Получение исторических данных о котировках ценных бумаг. Для получения данных применяется API Yahoo Finance. 
    Аргументом функции является список тикеров, передаваемый в виде строки, в которой тикеры перечислены через пробелы. 
    """
    tickers = tickers.split(" ")

    # Добавим курс доллара к рублю.
    tickers.append('USDRUB=X')

    # Создадим пустой датафрейм, в котором каждый столбец соответсвует каждому тикеру из списка.
    stock_data = pd.DataFrame(columns=tickers)

    for ticker in tickers:
        stock_data[ticker] = web.DataReader(ticker, 'yahoo', start, today)['Adj Close']

    moex_tickers = [ticker for ticker in tickers if '.ME' in ticker]

    # Курс российских акций в долларах = курс акций в рублях / курс доллара к рублю.
    for moex_ticker in moex_tickers:
        stock_data[moex_ticker] = stock_data.apply(lambda row: row[moex_ticker] / row['USDRUB=X'], axis=1)

    stock_data.drop(columns='USDRUB=X', inplace=True) # удалим курс доллара к рублю
    stock_data.columns = stock_data.columns.str.rstrip('.ME') # удалим окончание .ME для российских тикеров
    
    return stock_data

def cumulative_return(period, stock_data):
    """
    Определение функции для вычисления кумулятивного возврата на инвестиции. 
    Функция принимает один аргумент: строкое обозначение временного периода, за который нужно проанализировать возврат на инвестиции.
    """

    # дата отсчета вычисляется в зависимости от переданного функции аргумента 
    if period == "год":
        time_interval = today - relativedelta(years=1)
    elif period == "квартал":
        time_interval = today - relativedelta(months=3)
    else:
        raise Exception('Указан недопустимый период')

    # ограничим набор данных в соответствии с заданным периодом
    last_period_stock_data = stock_data[stock_data.index >= time_interval]
    cumulative_return = (last_period_stock_data.pct_change() + 1).cumprod() - 1

    return cumulative_return

def compare_returns(tickers, period):
    """Функция для вывода результатов сравнения доходности активов / портфелей в виде графика и в виде матрицы."""

    stocks = stock_data(tickers)
    returns = cumulative_return(period, stocks)
    
    # отображение возврата на инвестиции в виде матрицы
    total_returns = returns.tail(1).transpose()
    total_returns.sort_values(by=returns.columns[0], ascending=False, inplace=True)
    total_returns = returns.apply(lambda row:"{:.2%}".format(row[0]),  axis=1)
    stocks_comparison = {
        'tickers': ", ".join(tickers),
        'period': period,
        'stock_data': stocks,
        'returns': returns.to_string(),
    }
    return stocks_comparison