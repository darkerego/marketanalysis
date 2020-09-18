#!/usr/bin/env python3
"""
TALIB Class
"""
import threading
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
import argparse
import talib as ta
import finplot as fplt
from binance.client import Client
import binance
import pandas as pd

from finplot import candlestick_ochl
from matplotlib.dates import date2num


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


class TaGenerator:

    def __init__(self, trading_pair, interval):
        self.rc_params = {
            "lines.color": "white",
            "patch.edgecolor": "white",
            "text.color": "white",
            "axes.facecolor": "black",
            "axes.edgecolor": "lightgray",
            "axes.labelcolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "grid.color": "grey",
            "figure.facecolor": "black",
            "figure.edgecolor": "black",
            "figure.figsize": "25, 12"}
        self.trading_pair = trading_pair
        self.interval = interval
        self.filename = 'credentials.txt'
        self.trader = Trader(self.filename)
        self.klines = self.trader.client.get_klines(symbol=trading_pair, interval=interval)
        self.open_time = [int(entry[0]) for entry in self.klines]
        self.low = [float(entry[1]) for entry in self.klines]
        self.mid = [float(entry[2]) for entry in self.klines]
        self.high = [float(entry[3]) for entry in self.klines]
        self.close = [float(entry[4]) for entry in self.klines]
        self.close_array = np.asarray(self.close)
        self.high_array = np.asarray(self.high)
        self.low_array = np.asarray(self.low)
        self.new_time = [datetime.fromtimestamp(time / 1000) for time in self.open_time]


    def generate_bbands(self, title='Boiler Bands'):
        upperband, middleband, lowerband = ta.BBANDS(self.close_array, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
        #plt.rcParams.update(self.rc_params)
        # plt.style.use('dark_background')
        plt.plot(self.new_time, upperband, label='UPPERBAND Signal')
        plt.plot(self.new_time, middleband, label='MIDDLEBAND Signal')
        plt.plot(self.new_time, lowerband, label='LOWERBAND Histogram')
        plt.title(f"{title} Plot for {self.trading_pair} Period: {self.interval}")
        plt.xlabel("Open Time")
        plt.ylabel("Price")
        return plt



    def generate_stoch(self, title='Stochastic'):
        slowk, slowd = ta.STOCH(self.low_array, self.high_array, self.close_array)
        plt.rcParams.update(self.rc_params)
        #plt.style.use('dark_background')
        plt.plot(self.new_time, slowk, label='STOCH Slowk', color='blue')
        plt.plot(self.new_time, slowd, label='STOCH Slowd', color='red')
        plt.title(f"{title} Plot for {self.trading_pair} Period: {self.interval}")
        plt.xlabel("Open Time")
        plt.ylabel("Price")
        return plt

    def generate_macd(self, title='MACD'):
        macd, macdsignal, macdhist = ta.MACD(self.close_array, fastperiod=12, slowperiod=26, signalperiod=9)

        crosses = []
        macdabove = False
        for i in range(len(macd)):
            if np.isnan(macd[i]) or np.isnan(macdsignal[i]):
                pass
            else:
                if macd[i] > macdsignal[i]:
                    if macdabove == False:
                        macdabove = True
                        cross = [self.new_time[i], macd[i], 'go']
                        crosses.append(cross)
                else:
                    if macdabove == True:
                        macdabove = False
                        cross = [self.new_time[i], macd[i], 'ro']
                        crosses.append(cross)

        plt.rcParams.update(self.rc_params)
        plt.plot(self.new_time, macd, label='MACD')
        plt.plot(self.new_time, macdsignal, label='MACD Signal')
        for cross in crosses:
            plt.plot(cross[0], cross[1], cross[2])
        # plt.plot(new_time, macdhist, label='MACD Histogram')
        plt.title(f"{title} Plot for {self.trading_pair} Period: {self.interval}")
        plt.xlabel("Open Time")
        plt.ylabel("Price")
        return plt

    def generate_sar(self, title='Parabolic SAR'):
        SAR = ta.SAR(self.high_array, self.low_array, acceleration=0.05, maximum=0.2)
        plt.rcParams.update(self.rc_params)
        plt.plot(self.new_time, SAR, label='Parabolic SAR', marker='.', linestyle='dotted', color='green')
        plt.title(f"{title} Plot for {self.trading_pair} Period: {self.interval}")
        plt.xlabel("Open Time")
        plt.ylabel("Price")
        return plt


    def generate_sma(self, title='Simple Moving Average'):
        SMA_200 = ta.SMA(self.close_array, timeperiod=200)
        SMA_14 = ta.SMA(self.close_array, timeperiod=14)
        plt.rcParams.update(self.rc_params)
        plt.title(f"{title} Plot for {self.trading_pair} Period: {self.interval}")
        plt.plot(self.new_time, SMA_200, label='SMA 200', color='red')
        plt.plot(self.new_time, SMA_14, label='SMA 14', color='blue')
        return plt

    def generate_rsi(self, title='Relative Strength Index'):
        rsi = ta.RSI(self.close_array, timeperiod=14)
        plt.rcParams.update(self.rc_params)
        plt.title(f"{title} Plot for {self.trading_pair} Period: {self.interval}")

        plt.plot(self.new_time, rsi, label='Relative Strength Index', color='red')
        return plt

    def generate_all(self):
        plt = self.generate_macd()
        plt = self.generate_stoch()
        plt = self.generate_sar()
        plt = self.generate_bbands()
        plt = self.generate_sma()
        plt = self.generate_rsi(title=f'Multi-Indicator Plot Period {self.interval} ')
        return plt




    def show(self, plt):
        plt.xlabel("Time")
        plt.ylabel("Price")
        plt.grid()
        plt.legend()
        plt.savefig(f'{self.trading_pair}_{self.interval}.png')
        if not args.no_plot:
            plt.show()


if __name__ == '__main__':  # TODO: change dest from 'pair' to symbol, and 'interval' to 'period'
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--symbol', dest='pair', default='BTCUSDT', type=str, help='Instrument to analyse')
    parser.add_argument('-i', '--indicator', default='MACD', type=str,
                        help='Plot this indicator (MACD, STOCH, SAR ,BBAND)')
    parser.add_argument('-p', '--period', dest='interval', default='1d', type=str, help='Interval. 1d means 1 day. 1h means 1 hour.')
    """parser.add_argument('-a', '--auto', action='store_true',
                        help="Run auto interval plot: '1d', '4h', '1h', '30m', '15m', '5m', '1m' ")"""
    parser.add_argument('-np', '--no_plot', action='store_true', default=False, help='Generate Only, do not show.')
    args = parser.parse_args()
    try:
        tagen = TaGenerator(trading_pair=args.pair, interval=args.interval)
    except Exception as fuck:
        print(f'Error: {fuck}')

    else:
        if args.interval:
            if args.indicator == 'MACD':
                p = tagen.generate_macd()
            elif args.indicator == 'STOCH':
                p = tagen.generate_stoch()
            elif args.indicator == 'SAR':
                p = tagen.generate_sar()
            elif args.indicator == 'BBANDS':
                p = tagen.generate_bbands()
            elif args.indicator == 'SMA':
                p = tagen.generate_sma()
            elif args.indicator == 'RSI':
                p = tagen.generate_rsi()
            elif args.indicator == 'ALL':
                p = tagen.generate_all()
            else:
                print('Invalid Interval Given!')
                exit(1)
            tagen.show(plt=p)
