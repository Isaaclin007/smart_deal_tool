# -*- coding: utf-8 -*-
import os
import sys
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))
import pandas as pd
from zipfile import ZipFile
from struct import unpack, calcsize
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
from mpl_finance import candlestick_ohlc
from matplotlib.widgets import MultiCursor
from matplotlib.dates import DateFormatter
PROJECT_ROOT = '/Volumes/data/quant/stock/data/tdx/report'
class FinancialAnalysis():
    def __init__(self):
        self.base_color = '#e6daa6'
        self.fig = plt.figure(facecolor = self.base_color, figsize = (24, 24))
        self.ax = plt.subplot2grid((12,12), (0,0), rowspan = 12, colspan = 12, facecolor = self.base_color, fig = self.fig)

    def to_df(self, data):
        if len(data) == 0: return None
        total_lengh = len(data[0])
        col = ['code', 'date']
        length = total_lengh - 2
        for i in range(0, length):
            col.append("col" + str(i + 1))
        return pd.DataFrame(data = data, columns = col)

    def plot(self, df):
        for code in df.code.tolist():
            净资产收益率 = df.loc[df.code == code, 'col197']
            应收账款周转率 = df.loc[df.code == code, 'col213']
            self.ax.scatter(净资产收益率, 应收账款周转率, color = 'blue', s = 1)
            self.ax.set_title("map")
        plt.show()

    def parse(self, cdate):
        """
        获取指定日期的所有股票的财报信息
        :param cdate: yyyy-mm-dd
        :return:
        """
        item_all_list = []
        file_name = 'gpcw%s' % cdate.replace('-', '')
        file_path = "%s/%s.zip" % (PROJECT_ROOT, file_name)
        if not os.path.isfile(file_path): return None
        header_pack_format = "<1hI1H3L"
        with ZipFile(file_path) as myzip:
            with myzip.open('%s.dat' % file_name) as datfile:
                header_size = calcsize(header_pack_format)
                stock_item_size = calcsize("<6s1c1L")
                data_header = datfile.read(header_size)
                stock_header = unpack(header_pack_format, data_header)
                max_count = stock_header[2]
                report_date = stock_header[1]
                report_size = stock_header[4]
                report_fields_count = int(report_size / 4)
                report_pack_format = "<{}f".format(report_fields_count)
                for stock_idx in range(0, max_count):
                    datfile.seek(header_size + stock_idx * calcsize("<6s1c1L"))
                    si = datfile.read(stock_item_size)
                    stock_item = unpack("<6s1c1L", si)
                    code = stock_item[0].decode("utf-8")
                    foa = stock_item[2]
                    datfile.seek(foa)
                    info_data = datfile.read(calcsize(report_pack_format))
                    cw_info = unpack(report_pack_format, info_data)
                    one_record = (code, report_date) + cw_info
                    item_all_list.append(one_record)
        return item_all_list
    
    def report_list(self, cdate=None):
        """
        获取财报信息
        :param cdate: yyyy-mm-dd 指定日期
        :return:
        * 什么参数不指定返回所有股票的最后一季财报信息。
        * 仅指定cdate，返回该日期所有股票的财报信息
        :notice :
        引用专业财务数据.数据请用[专业财务数据]下载.
        数据编号如下:
        0--返回报告期(YYMMDD格式),150930表示为2015年第三季
        说明:
        1.所有指标没有标注单位的都是个位,如资金项单位都是元,股本单位都是股。
        2.所有的空值数据显示为0,以方便客户加减运算,非金融类指标在指标名称后有标注。
        -------------每股指标-----------------------------
        1--基本每股收益
        2--扣除非经常性损益每股收益
        3--每股未分配利润
        4--每股净资产
        5--每股资本公积金
        6--净资产收益率
        7--每股经营现金流量
        -------------资产负债表----------------------------
        8.--货币资金
        9.--交易性金融资产
        10.--应收票据
        11.--应收账款
        12.--预付款项
        13.--其他应收款
        14.--应收关联公司款
        15.--应收利息
        16.--应收股利
        17.--存货
        18.--其中：消耗性生物资产
        19.--一年内到期的非流动资产
        20.--其他流动资产
        21.--流动资产合计
        22.--可供出售金融资产
        23.--持有至到期投资
        24.--长期应收款
        25.--长期股权投资
        26.--投资性房地产
        27.--固定资产
        28.--在建工程
        29.--工程物资
        30.--固定资产清理
        31.--生产性生物资产
        32.--油气资产
        33.--无形资产
        34.--开发支出
        35.--商誉
        36.--长期待摊费用
        37.--递延所得税资产
        38.--其他非流动资产
        39.--非流动资产合计
        40.--资产总计
        41.--短期借款
        42.--交易性金融负债
        43.--应付票据
        44.--应付账款
        45.--预收款项
        46.--应付职工薪酬
        47.--应交税费
        48.--应付利息
        49.--应付股利
        50.--其他应付款
        51.--应付关联公司款
        52.--一年内到期的非流动负债
        53.--其他流动负债
        54.--流动负债合计
        55.--长期借款
        56.--应付债券
        57.--长期应付款
        58.--专项应付款
        59.--预计负债
        60.--递延所得税负债
        61.--其他非流动负债
        62.--非流动负债合计
        63.--负债合计
        64.--实收资本（或股本）
        65.--资本公积
        66.--盈余公积
        67.--减：库存股
        68.--未分配利润
        69.--少数股东权益
        70.--外币报表折算价差
        71.--非正常经营项目收益调整
        72.--所有者权益（或股东权益）合计
        73.--负债和所有者（或股东权益）合计
        -------------利润表-----------------------------
        74.--其中：营业收入
        75.--其中：营业成本
        76.--营业税金及附加
        77.--销售费用
        78.--管理费用
        79.--勘探费用
        80.--财务费用
        81.--资产减值损失
        82.--加：公允价值变动净收益
        83.--投资收益
        84.--其中：对联营企业和合营企业的投资收益
        85.--影响营业利润的其他科目
        86.--三、营业利润
        87.--加：补贴收入
        88.--营业外收入
        89.--减：营业外支出
        90.--其中：非流动资产处置净损失
        91.--加：影响利润总额的其他科目
        92.--四、利润总额
        93.--减：所得税
        94.--加：影响净利润的其他科目
        95.--五、净利润
        96.--归属于母公司所有者的净利润
        97.--少数股东损益
        ------------------现金流量表---------------------
        98.--销售商品、提供劳务收到的现金
        99.--收到的税费返还
        100.--收到其他与经营活动有关的现金
        101.--经营活动现金流入小计
        102.--购买商品、接受劳务支付的现金
        103.--支付给职工以及为职工支付的现金
        104.--支付的各项税费
        105.--支付其他与经营活动有关的现金
        106.--经营活动现金流出小计
        107.--经营活动产生的现金流量净额
        108.--收回投资收到的现金
        109.--取得投资收益收到的现金
        110.--处置固定资产、无形资产和其他长期资产收回的现金净额
        111.--处置子公司及其他营业单位收到的现金净额
        112.--收到其他与投资活动有关的现金
        113.--投资活动现金流入小计
        114.--购建固定资产、无形资产和其他长期资产支付的现金
        115.--投资支付的现金
        116.--取得子公司及其他营业单位支付的现金净额
        117.--支付其他与投资活动有关的现金
        118.--投资活动现金流出小计
        119.--投资活动产生的现金流量净额
        120.--吸收投资收到的现金
        121.--取得借款收到的现金
        122.--收到其他与筹资活动有关的现金
        123.--筹资活动现金流入小计
        124.--偿还债务支付的现金
        125.--分配股利、利润或偿付利息支付的现金
        126.--支付其他与筹资活动有关的现金
        127.--筹资活动现金流出小计
        128.--筹资活动产生的现金流量净额
        129.--四、汇率变动对现金的影响
        130.--四(2)、其他原因对现金的影响
        131.--五、现金及现金等价物净增加额
        132.--期初现金及现金等价物余额
        133.--期末现金及现金等价物余额
        134.--净利润
        135.--加：资产减值准备
        136.--固定资产折旧、油气资产折耗、生产性生物资产折旧
        137.--无形资产摊销
        138.--长期待摊费用摊销
        139.--处置固定资产、无形资产和其他长期资产的损失
        140.--固定资产报废损失
        141.--公允价值变动损失
        142.--财务费用
        143.--投资损失
        144.--递延所得税资产减少
        145.--递延所得税负债增加
        146.--存货的减少
        147.--经营性应收项目的减少
        148.--经营性应付项目的增加
        149.--其他
        150.--经营活动产生的现金流量净额2
        151.--债务转为资本
        152.--一年内到期的可转换公司债券
        153.--融资租入固定资产
        154.--现金的期末余额
        155.--减：现金的期初余额
        156.--加：现金等价物的期末余额
        157.--减：现金等价物的期初余额
        158.--现金及现金等价物净增加额
        ---------------------偿债能力分析------------------------
        159.--流动比率(非金融类指标)
        160.--速动比率(非金融类指标)
        161.--现金比率(%)(非金融类指标)
        162.--利息保障倍数(非金融类指标)
        163.--非流动负债比率(%)(非金融类指标)
        164.--流动负债比率(%)(非金融类指标)
        165.--现金到期债务比率(%)(非金融类指标)
        166.--有形资产净值债务率(%)
        167.--权益乘数(%)
        168.--股东的权益/负债合计(%)
        169.--有形资产/负债合计(%)
        170.--经营活动产生的现金流量净额/负债合计(%)(非金融类指标)
        171.--EBITDA/负债合计(%)(非金融类指标)
        ---------------------经营效率分析------------------------
        172.--应收帐款周转率(非金融类指标)
        173.--存货周转率(非金融类指标)
        174.--运营资金周转率(非金融类指标)
        175.--总资产周转率(非金融类指标)
        176.--固定资产周转率(非金融类指标)
        177.--应收帐款周转天数(非金融类指标)
        178.--存货周转天数(非金融类指标)
        179.--流动资产周转率(非金融类指标)
        180.--流动资产周转天数(非金融类指标)
        181.--总资产周转天数(非金融类指标)
        182.--股东权益周转率(非金融类指标)
        ---------------------发展能力分析------------------------
        183.--营业收入增长率(%)
        184.--净利润增长率(%)
        185.--净资产增长率(%)
        186.--固定资产增长率(%)
        187.--总资产增长率(%)
        188.--投资收益增长率(%)
        189.--营业利润增长率(%)
        190.--扣非每股收益同比(%)
        191.--扣非净利润同比(%)
        192.--暂无
        ---------------------获利能力分析------------------------
        193.--成本费用利润率(%)
        194.--营业利润率(非金融类指标)
        195.--营业税金率(非金融类指标)
        196.--营业成本率(非金融类指标)
        197.--净资产收益率
        198.--投资收益率
        199.--销售净利率(%)
        200.--总资产报酬率
        201.--净利润率(非金融类指标)
        202.--销售毛利率(%)(非金融类指标)
        203.--三费比重(非金融类指标)
        204.--管理费用率(非金融类指标)
        205.--财务费用率(非金融类指标)
        206.--扣除非经常性损益后的净利润
        207.--息税前利润(EBIT)
        208.--息税折旧摊销前利润(EBITDA)
        209.--EBITDA/营业总收入(%)(非金融类指标)
        ---------------------资本结构分析---------------------
        210.--资产负债率(%)
        211.--流动资产比率(非金融类指标)
        212.--货币资金比率(非金融类指标)
        213.--存货比率(非金融类指标)
        214.--固定资产比率
        215.--负债结构比(非金融类指标)
        216.--归属于母公司股东权益/全部投入资本(%)
        217.--股东的权益/带息债务(%)
        218.--有形资产/净债务(%)
        ---------------------现金流量分析---------------------
        219.--每股经营性现金流(元)
        220.--营业收入现金含量(%)(非金融类指标)
        221.--经营活动产生的现金流量净额/经营活动净收益(%)
        222.--销售商品提供劳务收到的现金/营业收入(%)
        223.--经营活动产生的现金流量净额/营业收入
        224.--资本支出/折旧和摊销
        225.--每股现金流量净额(元)
        226.--经营净现金比率（短期债务）(非金融类指标)
        227.--经营净现金比率（全部债务）
        228.--经营活动现金净流量与净利润比率
        229.--全部资产现金回收率
        ---------------------单季度财务指标---------------------
        230.--营业收入
        231.--营业利润
        232.--归属于母公司所有者的净利润
        233.--扣除非经常性损益后的净利润
        234.--经营活动产生的现金流量净额
        235.--投资活动产生的现金流量净额
        236.--筹资活动产生的现金流量净额
        237.--现金及现金等价物净增加额
        ---------------------股本股东---------------------
        238.--总股本
        239.--已上市流通A股
        240.--已上市流通B股
        241.--已上市流通H股
        242.--股东人数(户)
        243.--第一大股东的持股数量
        244.--十大流通股东持股数量合计(股)
        245.--十大股东持股数量合计(股)
        ---------------------机构持股---------------------
        246.--机构总量（家）
        247.--机构持股总量(股)
        248.--QFII机构数
        249.--QFII持股量
        250.--券商机构数
        251.--券商持股量
        252.--保险机构数
        253.--保险持股量
        254.--基金机构数
        255.--基金持股量
        256.--社保机构数
        257.--社保持股量
        258.--私募机构数
        259.--私募持股量
        260.--财务公司机构数
        261.--财务公司持股量
        262.--年金机构数
        263.--年金持股量
        ---------------------新增指标---------------------
        264.--十大流通股东中持有A股合计(股) [注：季度报告中，若股东同时持有非流通A股性质的股份(如同时持有流通A股和流通B股），指标264取的是包含同时持有非流通A股性质的流通股数]
        265.--第一大流通股东持股量(股)
        266.--自由流通股(股)[注：1.自由流通股=已流通A股-十大流通股东5%以上的A股；2.季度报告中，若股东同时持有非流通A股性质的股份(如同时持有流通A股和流通H股），5%以上的持股取的是不包含同时持有非流通A股性质的流通股数，结果可能偏大； 3.指标按报告期展示，新股在上市日的下个报告期才有数据]
        267.--受限流通A股(股)
        268.--一般风险准备(金融类)
        269.--其他综合收益(利润表)
        270.--综合收益总额(利润表)
        271.--归属于母公司股东权益(资产负债表)
        272.--银行机构数(家)(机构持股)
        273.--银行持股量(股)(机构持股)
        274.--一般法人机构数(家)(机构持股)
        275.--一般法人持股量(股)(机构持股)
        276.--近一年净利润(元)
        277.--信托机构数(家)(机构持股)
        278.--信托持股量(股)(机构持股)
        279.--特殊法人机构数(家)(机构持股)
        280.--特殊法人持股量(股)(机构持股)
        281.--加权净资产收益率(每股指标)
        282.--扣非每股收益(单季度财务指标)
        283.--最近一年营业收入（万元）
        284.--国家队持股数量（万股)[注：本指标统计包含汇金公司、证金公司、外汇管理局旗下投资平台、国家队基金、国开、养老金以及中科汇通等国家队机构持股数量]
        285.--业绩预告：本期净利润同比增幅下限%
        286.--业绩预告：本期净利润同比增幅上限%
        """
        all_date_list = []   # 所有财报日期
        file_list = os.listdir(PROJECT_ROOT)
        for file_name in file_list:
            if file_name.startswith("."): continue
            file_name = file_name.split('.')[0]
            ymd_str = file_name[4:]
            all_date_list.append("%d-%02d-%02d" % (int(ymd_str) / 10000, int(ymd_str) % 10000 / 100, int(ymd_str) % 100))
        return None if cdate not in all_date_list else self.parse(cdate)

if __name__ == "__main__":
    filepath = "/Volumes/data/quant/stock/data/tdx/history/weeks/pledge/20190210_20190216.xls"
    index_list = [1, 2, 3, 4, 5, 6, 7, 8]
    name_list = ['date', 'code', 'name', 'counts', 'unlimited', 'limited', 'total', 'ratio'] 
    pledge_df = pd.read_excel(filepath, sheet_name = 0, skiprows = 2, header = 0, usecols = index_list, names = name_list)
    pledge_df.code = pledge_df.code.astype(str).str.zfill(6)

    fa = FinancialAnalysis()
    results = fa.report_list(cdate = '2018-09-30')
    df = fa.to_df(results)

    df = df[['code', 'col11', 'col13', 'col24', 'col74', 'col197', 'col210', 'col213']]
    df['应收账款率'] = 100 * (df['col11'] + df['col13']) / df['col74']
    df = df[(df['col197'] > 10) & (df['col213'] < 30) & (df['col213'] > 0) & (df['应收账款率'] < 30) & (df['col210'] < 30)]
    df = df.reset_index(drop = True)
    xdf_codelist = df.code.tolist()
    ydf = pledge_df[pledge_df['ratio'] < 15]
    ydf_codelist = ydf.code.tolist()
    code_list = list(set(xdf_codelist).intersection(set(ydf_codelist)))

    #净资产收益率 = df.loc[df.code == code, 'col197']
    #应收账款周转率 = df.loc[df.code == code, 'col172']
    #11.--应收账款
    #13.--其他应收款
    #24.--长期应收款
    #74.--其中：营业收入
    #197.--净资产收益率
    #210.--资产负债率(%)
    #213.--存货比率(非金融类指标)
    #fa.plot(df)
