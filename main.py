import datetime

import pandas as pd
import matplotlib.pyplot as plt


def load_data(path, price_column, date_column):
    data = pd.read_csv(path, header=None)
    data = data.values.tolist()
    data.pop(0)  # removing unnecessary titles of columns
    dates = []
    prices = []
    rows_number = 0
    for line in data:
        prices.append(float(line[price_column]))  # here: 1-opening prices, 4-closing prices
        dates.append(datetime.datetime.strptime(line[date_column], "%Y-%m-%d"))
        rows_number += 1
    return prices, dates, rows_number


def EMA(samples, N, offset):
    alpha = 2/(N+1)
    nominator = 0
    denominator = 0
    for i in range(N+1):
        nominator += ((1-alpha)**i)*samples[offset-i]
        denominator += (1-alpha)**i
    return nominator / denominator


def create_MACD(prices, rows_number):
    MACD = []
    for i in range(rows_number):
        if i < 26:
            MACD.append(0)
        else:
            EMA12 = EMA(prices, 12, i)
            EMA26 = EMA(prices, 26, i)
            MACD.append(EMA12 - EMA26)
    return MACD


def create_SIGNAL(MACD, rows_number):
    SIGNAL = []
    for i in range(rows_number):
        if i < 26:
            SIGNAL.append(0)
        else:
            SIGNAL.append(EMA(MACD, 9, i))
    return SIGNAL


def MACD_simulation(prices, dates, MACD, SIGNAL, rows_number, starting_budget, starting_actions,
                    buying_multiplier=1.0, selling_multiplier=1.0, isDivisible=False):
    #buying_multiplier = 1.0 -> all in, 0.5 -> spend only 50% of budget to buy actions, 0.25 -> 25%, etc.
    #selling_multiplier -> as above but with selling
    #isDivisible = False -> actions are not divisible, cryptocurrencies are
    budget = starting_budget
    actions = starting_actions

    isOver = False  # is MACD over SIGNAL
    plt.figure(1)
    if MACD[26] > SIGNAL[26]:
        isOver = True
    for i in range(26, rows_number):
        if isOver and MACD[i] < SIGNAL[i]:  # selling
            if isDivisible:
                budget += round(selling_multiplier * actions * prices[i], 2)
                actions -= selling_multiplier * actions
            else:
                budget += round(round(selling_multiplier * actions) * prices[i], 2)
                actions -= round(selling_multiplier*actions)
            isOver = False
            plt.plot(dates[i], prices[i], "yo")
        elif not isOver and MACD[i] > SIGNAL[i]:  # buying
            if isDivisible:
                actions += buying_multiplier * budget / prices[i]
                budget -= round(buying_multiplier * budget, 2)
            else:
                new_actions = round(buying_multiplier * budget / prices[i])
                actions += new_actions
                budget -= round(new_actions * prices[i], 2)
            isOver = True
            plt.plot(dates[i], prices[i], "ro")
    budget += round(actions * prices[rows_number-1], 2)
    profit = round(budget - starting_budget, 2)
    print("In the end we have " + str(round(budget, 2)) + "j which gives us " + str(profit) + "j (" +
          str(round(profit/starting_budget * 100, 2)) + "%) of profit using MACD indicator.")
    return


def main():
    plt.rcParams['figure.figsize'] = [15, 5]
    prices, dates, rows_number = load_data("data2.csv", 1, 0)
    plt.plot(dates, prices)

    MACD = create_MACD(prices, rows_number)
    plt.figure(2)
    plt.plot(dates, MACD)

    SIGNAL = create_SIGNAL(MACD, rows_number)
    plt.plot(dates, SIGNAL)

    MACD_simulation(prices, dates, MACD, SIGNAL, rows_number, 10000, 0)

    plt.show()
    return


main()





