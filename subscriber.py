#-*-coding:utf-8-*-
import futuquant
import const as ct
from log import getLogger
from futuquant.common.constant import SubType
logger = getLogger(__name__)
class Subscriber:
    def __init__(self):
        self.quote_ctx = futuquant.OpenQuoteContext(ct.FUTU_HOST, ct.FUTU_PORT)
        self.sub_dict = None
        self._status = False

    def __del__(self):
        self.quote_ctx.stop()
        self.quote_ctx.close()

    def start(self):
        self.quote_ctx.start()
        self.sub_dict = self.get_subscribed_list()
        logger.debug("self.sub_dict:%s" % self.sub_dict)
        self._status = True

    def stop(self):
        self.quote_ctx.stop()
        logger.debug("stop subscribe")
        self.sub_dict = None
        self._status = False

    def status(self):
        return self._status

    def subscribe_tick(self, code, callback):
        '''订阅一只股票的实时行情数据，接收推送 #设置监听-->订阅-->调用逐笔'''
        if code in self.sub_dict[SubType.TICKER]: return 0
        self.quote_ctx.set_handler(callback)
        ret, msg = self.quote_ctx.subscribe(code, SubType.TICKER)
        if 0 == ret:
            self.sub_dict[SubType.TICKER].append(code)
        else:
            logger.error(msg)
        return ret

    def subscribe_quote(self, code_list):
        if code in self.sub_dict[SubType.QUOTE]: return 0
        return self.quote_ctx.subscribe(code_list, SubType.QUOTE)

    def get_quote_data(self, code):
        ret_status, ret_data = self.quote_ctx.get_stock_quote(list(code))
        return ret_status, ret_data

    def unsubscribe_tick(self, code_list, subtype = SubType.TICKER):
        '''
        code_list – 取消订阅的股票代码列表
        subtype_list – 取消订阅的类型，参见SubType
        '''
        ret, msg = self.quote_ctx.unsubscribe(code_list, subtype)
        if 0 == ret: 
            self.sub_dict[SubType.TICKER].remove(code)
        else:
            logger.error(msg)
        return ret

    def get_subscribed_list(self):
        ret, data = self.quote_ctx.query_subscription()
        if 0 != ret: 
            logger.error(msg)
            return None
        return data['sub_dict']

    def get_tick_data(self, code):
        return self.quote_ctx.get_rt_ticker(code)

if __name__ == '__main__':
    s = Subscriber()
    x = s.get_subscribed_list()
