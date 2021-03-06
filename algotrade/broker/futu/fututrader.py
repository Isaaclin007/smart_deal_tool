#-*-coding:utf-8-*-
import json
import threading
import const as ct
from base.clog import getLogger
from futu import OrderType, TrdSide, TrdEnv, OpenCNTradeContext, OpenUSTradeContext, OpenHKTradeContext
logger = getLogger(__name__)
class MDeal(object):
    def __init__(self, jsonDict):
        self.__jsonDict = jsonDict

    def getDict(self):
        return self.__jsonDict

    def getInstrument(self):
        return self.__jsonDict["code"]

    def getAction(self):
        return self.__jsonDict["trd_side"]

    def getCreateTime(self):
        return self.__jsonDict["create_time"]

    def getDealId(self):
        return self.__jsonDict["deal_id"]

    def getOrderId(self):
        return self.__jsonDict["order_id"]

    def getPrice(self):
        return float(self.__jsonDict["price"])

    def getQuantity(self):
        return self.__jsonDict["qty"]

class MOrder(object):
    def __init__(self, jsonDict):
        self.__jsonDict = jsonDict

    def getDict(self):
        return self.__jsonDict

    def getInstrument(self):
        return self.__jsonDict["code"]

    def getAction(self):
        return self.__jsonDict["trd_side"]

    def getType(self):
        return self.__jsonDict["order_type"]

    def getCreateTime(self):
        return self.__jsonDict["create_time"]

    def getLastUpdatedTime(self):
        return self.__jsonDict["updated_time"]

    def getStatus(self):
        return self.__jsonDict["order_status"]

    def getId(self):
        return self.__jsonDict["order_id"]

    def getPrice(self):
        return float(self.__jsonDict["price"])

    def getQuantity(self):
        return self.__jsonDict["qty"]

    def getDealtQuantity(self):
        return self.__jsonDict["dealt_qty"]

    def getDealtAvgPrice(self):
        return self.__jsonDict["dealt_avg_price"]

class FutuTrader:
    ORDER_SCHEMA = ['order_id', 'order_type', 'order_status', 'code', 'stock_name', 'trd_side', 'qty', 'price', 'create_time', 'dealt_qty', 'dealt_avg_price', 'updated_time', 'last_err_msg']
    DEAL_SCHEMA = ['trd_side', 'deal_id', 'order_id', 'code', 'stock_name', 'qty', 'price', 'create_time', 'dealt_qty', 'counter_broker_id', 'counter_broker_name']
    def __init__(self, host, port, trd_env, market, unlock_path = ct.FUTU_PATH):
        if market != ct.CN_MARKET_SYMBOL and market != ct.US_MARKET_SYMBOL and market != ct.HK_MARKET_SYMBOL: raise Exception("not supported market:%s" % market)
        if ct.CN_MARKET_SYMBOL == market:
            self.trd_ctx = OpenCNTradeContext(host, port)
        elif ct.US_MARKET_SYMBOL == market:
            self.trd_ctx = OpenUSTradeContext(host, port)
        else:
            self.trd_ctx = OpenHKTradeContext(host, port)
        self.trd_env = trd_env
        self.acc_id = self.get_acc_id()
        self.unlock_pwd = self.get_unlock_pwd(fpath = unlock_path)
        if self.trd_env == TrdEnv.REAL:
            self.trd_ctx.unlock_trade(password_md5 = self.unlock_pwd)
        self._status = True
        self._lock   = threading.Lock()

    def __del__(self):
        if self.trd_ctx is not None:
            self.trd_ctx.close()

    def start(self):
        if self.trd_ctx is not None:
            self.trd_ctx.start()

    def get_acc_id(self):
        ret, data = self.trd_ctx.get_acc_list()
        if ret != 0: raise Exception("get accid failed")
        return data.loc[data.trd_env == self.trd_env, 'acc_id'].values[0]

    def get_unlock_pwd(self, fpath = ct.FUTU_PATH):
        with open(fpath) as f: infos = json.load(f)
        return infos['unlock_pwd']

    def get_cash(self):
        ret, data = self.trd_ctx.accinfo_query(trd_env = self.trd_env)
        if ret != 0: raise Exception("get cash failed")
        return data['cash'].values[0]

    def set_handler(self, mclass):
        with self._lock:
            self.trd_ctx.set_handler(mclass)

    def get_shares(self):
        mshares = dict()
        ret, data = self.trd_ctx.position_list_query(trd_env = self.trd_env)
        if ret != 0: raise Exception("get shares failed")
        for index, code in data.code.iteritems():
            mshares[code] = data.loc[index, 'qty']
        return mshares
           
    def get_order(self, id_ = "", filter_list = list()):
        orders = list()
        ret, data = self.trd_ctx.order_list_query(trd_env = TrdEnv.SIMULATE, order_id = id_, status_filter_list = filter_list)
        if ret != 0: raise Exception("get opend order failed. order_id:%s, filter_list:%s" % (id_, filter_list))
        if data.empty: return orders
        data = data[self.ORDER_SCHEMA]
        for mdict in data.to_dict("records"):
            orders.append(MOrder(mdict))
        return orders if id_ != "" else orders[0]

    def trade(self, order):
        code      = order.getInstrument()
        price     = order.getLimitPrice()
        quantity  = order.getQuantity()
        type_     = OrderType.NORMAL
        direction = TrdSide.BUY if order.isBuy() else TrdSide.SELL
        ret, data = self.trd_ctx.place_order(price, quantity, code, trd_side = direction, order_type = type_, adjust_limit = 0, trd_env = self.trd_env, acc_id = self.acc_id)
        if  ret  != 0: logger.error("trade failed, ret:%s, data:%s" % (ret, data))
        #logger.info("trade %s success, ret:%s, data:%s" % (code, ret, data))
        return ret, data

    def get_history_orders(self, code = "", start = "", end = "", status_filter_list = ["FILLED_ALL"]):
        orders = list()
        ret, data = self.trd_ctx.history_order_list_query(status_filter_list, code, start, end, trd_env = self.trd_env, acc_id = self.acc_id)
        if ret != 0: raise Exception("get history orders failed.code:%s, start:%s, end:%s, ret:%s, msg:%s" % (code, start, end, ret, data))
        if data.empty: return orders
        return data
        #data = data[self.ORDER_SCHEMA]
        #for mdict in data.to_dict("records"):
        #    orders.append(MOrder(mdict))
        #return orders

    def get_history_deals(self, code = "", start = "", end = ""):
        deals = list()
        ret, data = self.trd_ctx.history_deal_list_query(code, start, end, trd_env = self.trd_env, acc_id = self.acc_id)
        if ret != 0: raise Exception("get history deals failed.code:%s, start:%s, end:%s" % (code, start, end))
        if data.empty: return deals
        return data
        #data = data[self.DEAL_SCHEMA]
        #for mdict in data.to_dict("records"):
        #    deals.append(MDeal(mdict))
        #return deals

    def buy(self, code, price, quantity):
        ret, data = self.trd_ctx.place_order(code = code, price = price, qty = quantity, trd_side = TrdSide.BUY, order_type = OrderType.NORMAL, trd_env = self.trd_env)
        return ret, data

    def modify(self, order, operation):
        id_       = order.getId()
        price     = order.getLimitPrice()
        quantity  = order.getQuantity()
        type_     = order.getOrderType()
        side      = order.getOrderDirection()
        ret, data = self.trd_ctx.modify_order(operation, id_, quantity, price, adjust_limit = 0, trd_env = self.trd_env, acc_id = self.acc_id)
        return ret, data

    def close(self):
        with self._lock:
            self.trd_ctx.close()
            self._status = False

    def status(self):
        with self._lock:
            return self._status
