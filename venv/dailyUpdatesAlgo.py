import numpy as np
import pandas as pd
from numpy.random import randn
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pandas_datareader.data as web
import pandas_datareader
import datetime
from pandas_datareader.yahoo.options import Options as YahooOptions
import quandl
from pandas.plotting import scatter_matrix
from matplotlib.dates import DateFormatter, date2num, WeekdayLocator, DayLocator, MONDAY
from mpl_finance import candlestick_ohlc
from pandas_datareader import data
from yahoofinancials import YahooFinancials
from dateutil.relativedelta import relativedelta
import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from dateutil import relativedelta
import time
import talib

#Written by Nishant Jain
class DailyUpdate:
    def run(self):
        tickers = ['ATVI', 'GOOGL', 'AMED', 'CHWY', 'C', 'CRWD', 'FB', 'FTHM', 'VEEV']
        today = date.today()
        writeToday = str(today)
        writeToday = writeToday + ".txt"
        outF = open(writeToday, "w")
        for i in tickers:
            ticker = "$" + i + ":"
            addedDate = getBuyDate(ticker)
            #get market cap + stock price
            yearold = today.year - 1
            yago = datetime.date(yearold, today.month, today.day)
            stock = web.DataReader(i, 'yahoo', yago, today)
            outF.write("\n\nDISPLAYING DATA FOR " + ticker)
            outF.write("\n\tAdded to the portfolio on: " + addedDate.strftime('%m/%d/%Y'))
            outF.write("\n\tShare price as of "+ today.strftime('%m/%d/%Y') + " for "+ ticker + " ${0:.2f}".format(stock['Close'][-1])+ " per share")
            market_cap = int(data.get_quote_yahoo(i)['marketCap'])
            outF.write("\n\tMarket cap is: ${:,}".format(market_cap))
            yahoo_financials = YahooFinancials([i])

            #get dividend yield
            dividend_yield = str(yahoo_financials.get_dividend_yield())
            dividend_yield = dividend_yield[(len(i) + 5):len(dividend_yield) - 1]
            if (dividend_yield == "None"):
                dividend_yield = 0.00
            dividend_yield = float(dividend_yield) * 100
            outF.write("\n\tDividend yield: "+"{0:.4g}".format(dividend_yield)+ "%")

            #Get daily return
            stock['Daily Return'] = stock['Close'].pct_change(1)
            daily_return = float(stock['Daily Return'][-1]) * 100
            outF.write("\n\tDaily return as of " + today.strftime('%m/%d/%Y') + "is: " + "{0:.3f}".format(daily_return) + "%")

            #Get week to date return
            lastMonday = today - datetime.timedelta(days=today.weekday())
            weekToDate = web.DataReader(i, 'yahoo', lastMonday, today)
            firstPrice = float(weekToDate['Open'][0])
            lastPrice = float(weekToDate['Close'][-1])
            weekToDateReturn = (lastPrice/firstPrice - 1) * 100
            #weekToDate['Daily Return'] = weekToDate['Close'].pct_change(1)
            #weekToDate['Cumulative Return'] = ((1 + weekToDate['Daily Return']).cumprod() - 1) * 100
            #returnWeekly =  float(weekToDate['Cumulative Return'][1])
            outF.write("\n\tWeek-to-date return: "+"{0:.4g}".format(weekToDateReturn)+ "%")

            #get month to date return
            first_day_of_month = today.replace(day=1)
            monthToDate = web.DataReader(i, 'yahoo', first_day_of_month, today)
            firstPrice = float(monthToDate['Open'][0])
            lastPrice = float(monthToDate['Close'][-1])
            monthToDateReturn = (lastPrice/firstPrice - 1) * 100
            outF.write("\n\tMonth-to-date return: " + "{0:.4g}".format(monthToDateReturn)+ "%")

            #get trailing month change
            if today.month == 3 and today.day > 28:
                day = 28
            else:
                day = today.day
            if today.month == 1:
                year = today.year - 1
                month = 12
            else:
                year = today.year
                month = today.month - 1
            lastMonth = datetime.date(year, month, day)
            trailingMonth = web.DataReader(i, 'yahoo', lastMonth, today)
            firstPrice = float(trailingMonth['Open'][0])
            lastPrice = float(monthToDate['Close'][-1])
            trailingMonthReturn = (lastPrice/firstPrice - 1) * 100
            outF.write("\n\tTrailing month return: "+"{0:.5g}".format(trailingMonthReturn)+ "%")

            #get YTD return
            firstDay = datetime.date(today.year, 1, 4)
            yearToDate = web.DataReader(i, 'yahoo', firstDay, today)
            firstPrice = float(yearToDate['Open'][0])
            lastPrice = float(yearToDate['Close'][-1])
            yearToDateReturn = (lastPrice/firstPrice - 1) * 100
            outF.write("\n\tYear-to-date return: {0:.3g}".format(yearToDateReturn)+ "%")

            #get percent down from 52 week high
            yearAgo = datetime.date(today.year - 1, 1, 1)
            oneYear = web.DataReader(i, 'yahoo', yearAgo, today)
            high = float(oneYear['High'][0])
            count = int(oneYear['High'].count())
            for j in range (1,count):
                if float(oneYear['High'][j]) > high:
                    high = float(oneYear['High'][j])
            priceToday = float(oneYear['Close'][-1])
            down52wk = (high/priceToday - 1) * 100
            outF.write("\n\tPercent down from 52-week-high is: {0:.5g}".format(down52wk) + "%")

            # get percent down from peak since buy
            buyDate = getBuyDate(ticker)
            holdingPeriod = web.DataReader(i, 'yahoo', buyDate, today)
            peakHigh = float(holdingPeriod['High'][0])
            count = int(holdingPeriod['High'].count())
            for j in range(1, count):
                 if float(holdingPeriod['High'][j]) > peakHigh:
                     peakHigh = float(holdingPeriod['High'][j])
            priceToday = float(holdingPeriod['Close'][-1])
            downPeak = (peakHigh / priceToday - 1) * 100
            outF.write("\n\tPercent down from peak since purchase is: {0:.5g}".format(downPeak) + "%")

            #get 50 day SMA
            stock['SMA10'] = talib.MA(stock['Close'].values, timeperiod=10, matype=0)
            SMA10 = float(stock['SMA10'][-1])
            stock['SMA50'] = talib.MA(stock['Close'].values, timeperiod=50, matype=0)
            SMA50 = float(stock['SMA50'][-1])
            if SMA10 > SMA50:
                outF.write("\n\tThe SMA10 is: " + "${0:.5g}, ".format(SMA10) + " which is above the SMA50 of: ${0:.5g}".format(SMA50))
            elif SMA10 == SMA50:
                outF.write("\n\tThe SMA10 is:" + "${0:.5g}".format(SMA10) + "which is equal the SMA50 of: ${0:.5g}".format(SMA50))
            else:
                outF.write("\n\tThe SMA10 is:"+ "${0:.5g}".format(SMA10)+ "which is below the SMA50 of: ${0:.5g}".format(SMA50))

            #get the RSI
            stock['RSI'] = talib.RSI(stock['Close'].values)
            rsiVal = float(stock['RSI'][-1])
            outF.write("\n\tThe RSI is "+ "{0:.5g}".format(rsiVal))

            #get the MACD
            stock['MACD'], stock['MACDsignal'], stock['MACDhist'] = talib.MACD(stock["Close"], fastperiod=12, slowperiod=26, signalperiod=9)
            fig, axes = plt.subplots(2, 1)
            stock[['MACD', 'MACDsignal', 'MACDhist']].plot(ax=axes[1], grid=True)
            plt.legend(loc='best', shadow=True)
            symbol = ticker + " MACD graph"
            plt.title(symbol)
            plt.show()
            print("\tDone with", i)
            time.sleep(8)

def getBuyDate(i):
    date = datetime.date(2021, 1, 1)
    if (i == "$CRWD:"):
        date = datetime.date(2021, 1, 4)
        return date
    elif (i == "$C:"):
        date = datetime.date(2020, 9, 29)
        return date
    elif (i == "$AMED:"):
        date = datetime.date(2020, 7, 7)
        return date
    elif (i == "$GOOGL:"):
        date = datetime.date(2020, 4, 22)
        return date
    elif (i == "$FTHM:"):
        date = datetime.date(2021, 1, 11)
        return date
    elif (i == "$CHWY:"):
        date = datetime.date(2020, 12, 7)
        return date
    elif (i == "$VEEV:"):
        date = datetime.date(2020, 6, 8)
        return date
    elif (i == "$FB:"):
        date = datetime.date(2020, 7, 7)
        return date
    elif (i == "$ATVI:"):
        date = datetime.date(2020, 4, 22)
        return date
    return date

def main():
    obj = DailyUpdate()
    obj.run()
if __name__ == "__main__":
    main()


