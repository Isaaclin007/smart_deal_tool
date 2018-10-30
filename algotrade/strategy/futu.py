# -*- coding: utf-8 -*-
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
import const as ct
from cstock import CStock
from futuquant import TrdEnv, TrdSide
from pyalgotrade import broker, strategy
from algotrade.feed import dataFramefeed
from algotrade.feed.futufeed import FutuFeed
from algotrade.broker.futu.futubroker import FutuBroker
from common import add_prifix, get_real_trading_stocks
class LiveTradingStrategy(strategy.BaseStrategy):
    def __init__(self, feed, brk, instruments):
        super(LiveTradingStrategy, self).__init__(feed, brk)
        self.__instruments = instruments
        self.__feed = feed
        self.__position = None

    def onEnterCanceled(self, position):
        self.__position = None

    def onEnterOK(self):
        pass

    def onExitOk(self, position):
        self.__position = None

    def onExitCanceled(self, position):
        self.__position.exitMarket()

    def onBars(self, bars):
        instrument  = self.__instruments[0]
        bar         = bars[instrument]
        #price       = bar.getOpen()
        price       = 5.8
        cash        = self.getBroker().getCash()
        shares      = self.getBroker().getPositions()
        action      = broker.Order.Action.BUY
        quantity    = 100
        order       = self.getBroker().createLimitOrder(action, instrument, price, quantity)
        self.getBroker().submitOrder(order)
        print("price:%s, cash:%s, shares:%s" % (price, cash, shares))

def main():
    fpath = "/Users/hellobiek/Documents/workspace/python/quant/smart_deal_tool/configure/trading.json"
    trading_info = get_real_trading_stocks(fpath)
    stocks  = trading_info['buy']
    stocks.extend(trading_info['sell'])
    #dataFeed   = dataFramefeed.Feed()
    #start_date = '2018-03-01'
    #end_date   = '2018-10-28'
    #for code in stocks:
    #    obj  = CStock(code, should_create_influxdb = False, should_create_mysqldb = True, redis_host = "127.0.0.1")
    #    data = obj.get_k_data_in_range(start_date, end_date)
    #    data = data.set_index('date')
    #    dataFeed.addBarsFromDataFrame(code, data)
    stocks = [add_prifix(code) for code in stocks]
    market_   = ct.CN_MARKET_SYMBOL
    timezone_ = ct.TIMEZONE_DICT[market_]
    apath       = "/Users/hellobiek/Documents/workspace/python/quant/smart_deal_tool/configure/futu.json"
    dataFeed    = FutuFeed(stocks, end_time = "15:00:00", timezone = timezone_)
    futuBroker  = FutuBroker(host = ct.FUTU_HOST_LOCAL, port = ct.FUTU_PORT, trd_env = TrdEnv.SIMULATE, market = market_, unlock_path = apath)
    strat       = LiveTradingStrategy(dataFeed, futuBroker, stocks)
    strat.run()

if __name__ == "__main__": 
    main()
