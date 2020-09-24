#!/usr/bin/env python3
import argparse

from binance.client import Client
import talib as ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class Trader:
    def __init__(self, file):
        self.connect(file)

    """ Creates Binance client """
    def connect(self,file):
        lines = [line.rstrip('\n') for line in open(file)]
        key = lines[0]
        secret = lines[1]
        self.client = Client(key, secret)

    """ Gets all account balances """
    def getBalances(self):
        prices = self.client.get_withdraw_history()
        return prices

class Strategy:

    def __init__(self, indicator_name, strategy_name, pair, interval, klines):
        #Name of indicator
        self.indicator = indicator_name
        #Name of strategy being used
        self.strategy = strategy_name
        #Trading pair
        self.pair = pair
        #Trading interval
        self.interval = interval
        #Kline data for the pair on given interval
        self.klines = klines
        #Calculates the indicator
        self.indicator_result = self.calculateIndicator()
        #Uses the indicator to run strategy
        self.strategy_result = self.calculateStrategy()


    '''
    Calculates the desired indicator given the init parameters
    '''
    def calculateIndicator(self):
        if self.indicator == 'MACD':
            close = [float(entry[4]) for entry in self.klines]
            close_array = np.asarray(close)

            macd, macdsignal, macdhist = ta.MACD(close_array, fastperiod=12, slowperiod=26, signalperiod=9)
            return [macd, macdsignal, macdhist]
        elif self.indicator == 'RSI':
            close = [float(entry[4]) for entry in self.klines]
            close_array = np.asarray(close)

            rsi = ta.RSI(close_array, timeperiod=14)
            return rsi

        else:
            return None


    '''
    Runs the desired strategy given the indicator results
    '''
    def calculateStrategy(self):
        if self.indicator == 'MACD':

            if self.strategy == 'CROSS':
                open_time = [int(entry[0]) for entry in self.klines]
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                self.time = new_time
                crosses = []
                macdabove = False
                #Runs through each timestamp in order
                for i in range(len(self.indicator_result[0])):
                    if np.isnan(self.indicator_result[0][i]) or np.isnan(self.indicator_result[1][i]):
                        pass
                    #If both the MACD and signal are well defined, we compare the 2 and decide if a cross has occured
                    else:
                        if self.indicator_result[0][i] > self.indicator_result[1][i]:
                            if macdabove == False:
                                macdabove = True
                                #Appends the timestamp, MACD value at the timestamp, color of dot, buy signal, and the buy price
                                cross = [new_time[i],self.indicator_result[0][i] , 'go', 'BUY', self.klines[i][4]]
                                crosses.append(cross)
                        else:
                            if macdabove == True:
                                macdabove = False
                                #Appends the timestamp, MACD value at the timestamp, color of dot, sell signal, and the sell price
                                cross = [new_time[i], self.indicator_result[0][i], 'ro', 'SELL', self.klines[i][4]]
                                crosses.append(cross)
                return crosses

            else:
                return None
        elif self.indicator == 'RSI':
            if self.strategy == '7030':
                open_time = [int(entry[0]) for entry in self.klines]
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                self.time = new_time
                result = []
                active_buy = False
                # Runs through each timestamp in order
                for i in range(len(self.indicator_result)):
                    if np.isnan(self.indicator_result[i]):
                        pass
                    # If the RSI is well defined, check if over 70 or under 30
                    else:
                        if float(self.indicator_result[i]) < 30 and active_buy == False:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                            entry = [new_time[i], self.indicator_result[i], 'go', 'BUY', self.klines[i][4]]
                            result.append(entry)
                            active_buy = True
                        elif float(self.indicator_result[i]) > 70 and active_buy == True:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                            entry = [new_time[i], self.indicator_result[i], 'ro', 'SELL', self.klines[i][4]]
                            result.append(entry)
                            active_buy = False
                return result
            elif self.strategy == '8020':
                open_time = [int(entry[0]) for entry in self.klines]
                new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
                self.time = new_time
                result = []
                active_buy = False
                # Runs through each timestamp in order
                for i in range(len(self.indicator_result)):
                    if np.isnan(self.indicator_result[i]):
                        pass
                    # If the RSI is well defined, check if over 80 or under 20
                    else:
                        if float(self.indicator_result[i]) < 20 and active_buy == False:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, buy signal, and the buy price
                            entry = [new_time[i], self.indicator_result[i], 'go', 'BUY', self.klines[i][4]]
                            result.append(entry)
                            active_buy = True
                        elif float(self.indicator_result[i]) > 80 and active_buy == True:
                            # Appends the timestamp, RSI value at the timestamp, color of dot, sell signal, and the sell price
                            entry = [new_time[i], self.indicator_result[i], 'ro', 'SELL', self.klines[i][4]]
                            result.append(entry)
                            active_buy = False
                return result

        else:
            return None

    '''
    Getter for the strategy result
    '''
    def getStrategyResult(self):
        return self.strategy_result

    '''
    Getter for the klines
    '''
    def getKlines(self):
        return self.klines

    '''
    Getter for the trading pair
    '''
    def getPair(self):
        return self.pair

    '''
    Getter for the trading interval
    '''
    def getInterval(self):
        return self.interval

    '''
    Getter for the time list
    '''
    def getTime(self):
        return self.time

    '''
    Plots the desired indicator with strategy buy and sell points
    '''
    def plotIndicator(self):
        open_time = [int(entry[0]) for entry in klines]
        new_time = [datetime.fromtimestamp(time / 1000) for time in open_time]
        plt.style.use('dark_background')
        for entry in self.strategy_result:
            plt.plot(entry[0], entry[1], entry[2])
        if self.indicator == 'MACD':
            plt.plot(new_time, self.indicator_result[0], label=f'{self.strategy}')
            plt.plot(new_time, self.indicator_result[1], label=f'{self.strategy} Signal')
            plt.plot(new_time, self.indicator_result[2], label=f'{self.strategy} Histogram')

        elif self.indicator == 'RSI':
            plt.plot(new_time, self.indicator_result, label='RSI')

        else:
            pass

        title = self.indicator + " Plot for " + self.pair + " on " + self.interval
        plt.title(title)
        plt.xlabel("Open Time")
        plt.ylabel("Value")
        plt.legend()
        plt.show()


class Backtest:
    def __init__(self, starting_amount, start_datetime, end_datetime, strategy):
        #Starting amount
        self.start = starting_amount
        #Number of trades
        self.num_trades = 0
        #Number of profitable trades
        self.profitable_trades = 0
        #Running amount
        self.amount = self.start
        #Start of desired interval
        self.startTime = start_datetime
        #End of desired interval
        self.endTime = end_datetime
        #Strategy object
        self.strategy = strategy
        #Trading pair
        self.pair = self.strategy.getPair()
        #Trading interval
        self.interval = self.strategy.getInterval()
        #Outputs the trades exectued
        self.trades = []
        #Runs the backtest
        self.results = self.runBacktest()
        #Prints the results
        self.printResults()


    def runBacktest(self):
        amount = self.start
        klines = self.strategy.getKlines()
        time = self.strategy.getTime()
        point_finder = 0
        strategy_result = self.strategy.getStrategyResult()
        #Finds the first cross point within the desired backtest interval
        while strategy_result[point_finder][0] < self.startTime:
            point_finder += 1
        #Initialize to not buy
        active_buy = False
        buy_price = 0
        #Runs through each kline
        for i in range(len(klines)):
            if point_finder > len(strategy_result)-1:
                break
            #If timestamp is in the interval, check if strategy has triggered a buy or sell
            if time[i] > self.startTime and time[i] < self.endTime:
                if(time[i] == strategy_result[point_finder][0]):
                    if strategy_result[point_finder][3] == 'BUY':
                        active_buy = True
                        buy_price = float(strategy_result[point_finder][4])
                        self.trades.append(['BUY', buy_price])
                    if strategy_result[point_finder][3] == 'SELL' and active_buy == True:
                        active_buy = False
                        bought_amount = amount / buy_price
                        self.num_trades += 1
                        if(float(strategy_result[point_finder][4]) > buy_price):
                            self.profitable_trades += 1
                        amount = bought_amount * float(strategy_result[point_finder][4])
                        self.trades.append(['SELL', float(strategy_result[point_finder][4])])
                    point_finder += 1
        self.amount = amount

    '''
    Prints the results of the backtest
    '''
    def printResults(self):
        print("Trading Pair: " + self.pair)
        print("Interval: " + self.interval)
        print("Ending amount: " + str(self.amount))
        print("Number of Trades: " + str(self.num_trades))
        profitable = self.profitable_trades / self.num_trades * 100
        print("Percentage of Profitable Trades: " + str(profitable) + "%")
        percent = self.amount / self.start * 100
        print(str(percent) + "% of starting amount")
        for entry in self.trades:
            print(entry[0] + " at " + str(entry[1]))


def main():
    global klines
    filename = 'credentials.txt'
    trader = Trader(filename)
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pair', default='BTCUSDT', type=str, help='Instrument to analyse')
    parser.add_argument('-i', '--interval', default='1d', type=str, help='Interval. 1d means 1 day. 1h means 1 hour.')
    parser.add_argument('-I', '--indicator', default='MACD', choices=['RSI', 'MACD'], type=str, help='Indictator to use')
    parser.add_argument('-s', '--strategy', default='CROSS', type=str, choices=['7030', '8020', 'CROSS'])
    args = parser.parse_args()
    trading_pair = args.pair
    interval = args.interval
    strat = args.strategy
    klines = trader.client.get_klines(symbol=trading_pair, interval=interval)
    if args.indicator == 'RSI':
        if args.strategy == 'CROSS':
            strat = '8020'
        else:
            strat = args.strategy
        rsi_strategy = Strategy('RSI', strat, trading_pair, interval, klines)
        rsi_strategy.plotIndicator()
        time = rsi_strategy.getTime()
        Backtest(100000, time[0], time[len(time) - 1], rsi_strategy)
    elif args.indicator == 'MACD':
        strat = 'CROSS'
        macd_strategy = Strategy('MACD', strat, trading_pair, interval, klines)
        macd_strategy.plotIndicator()
        time = macd_strategy.getTime()
        Backtest(100000, time[0], time[len(time) - 1], macd_strategy)
    else:

        print(f'Unknown strategy {args.strategy}')
        return False
main()
