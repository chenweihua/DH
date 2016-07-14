from django.shortcuts import render
from django.http import HttpResponse
from .models import News, KmeansData
from datetime import datetime, timedelta

now = datetime.now()  # 现在时刻,月日年时分秒
now_date = now.date()  # 现在时刻,月日年
yesterday = now + timedelta(days=-1)  # 昨天
the_day_before_yesterday = now + timedelta(days=-2)  # 前天
day_fixed_before_news = now + timedelta(days=-10)  # 10天前的消息自动从数据库中删除
day_fixed_before_kdata = now_date + timedelta(days=-90)  # 3个月前的k线图数据从数据库中删除
day_fixed_before_cdata = now_date + timedelta(days=-90)  # 3个月前的资金流数据从数据库中删除


# Create your views here.
def index(request):  # 处理主页的视图逻辑
    return render(request, 'choose_stock/index.html', {})


def news(request):  # 处理消息页面的视图逻辑
    news_dated = News.objects.filter(published_time__lte=day_fixed_before_news)  # 筛选出发布时间在特定天数前的过时消息
    news_dated.delete()  # 删除消息
    context_dict = {}  # 上下文字典
    news_today_pos = News.objects.filter(published_time__day=now.day, flag_pn=1).order_by(
            '-published_time')  # 提取出今日新闻利好列表,既查询,又排序,链接过滤器好
    context_dict['news_today_pos'] = news_today_pos
    news_today_neg = News.objects.filter(published_time__day=now.day, flag_pn=0).order_by(
            '-published_time')  # 提取今日利空新闻列表
    context_dict['news_today_neg'] = news_today_neg
    news_yes_pos = News.objects.filter(published_time__day=yesterday.day, flag_pn=1).order_by(
            '-published_time')  # 提取昨日利好新闻列表
    context_dict['news_yes_pos'] = news_yes_pos
    news_yes_neg = News.objects.filter(published_time__day=yesterday.day, flag_pn=0).order_by(
            '-published_time')  # 提取昨日利空新闻列表
    context_dict['news_yes_neg'] = news_yes_neg
    news_be_yes_pos = News.objects.filter(published_time__day=the_day_before_yesterday.day, flag_pn=1).order_by(
            '-published_time')  # 提取前日利好新闻列表
    context_dict['news_be_yes_pos'] = news_be_yes_pos
    news_be_yes_neg = News.objects.filter(published_time__day=the_day_before_yesterday.day, flag_pn=0).order_by(
            '-published_time')  # 提取前日利空新闻列表
    context_dict['news_be_yes_neg'] = news_be_yes_neg
    return render(request, 'choose_stock/news.html', context_dict)


def news_detail(request, pk):  # 显示具体新闻的视图逻辑, pk指新闻存储在mysql数据库中的id(用pk做传递参数是否存在安全隐患?)
    context_dict = {}  # 需要传递进模板中的上下文参数字典
    try:
        news = News.objects.get(pk=pk)
        context_dict['news'] = news
    except News.DoesNotExist:
        pass
    return render(request, 'choose_stock/news_detail.html', context_dict)


# --------------------------------------------------------以下为与kmeans相关的函数
def ChangeToEchartsData(stock_id_list=['000705', '300016', '002090']):  # 将特定代码的股票数据转换为符合echarts的数据
    stocks = KmeansData.objects.filter(stock_id__in=stock_id_list).order_by('stock_date')
    # stocks = KmeansData.objects.filter(stock_id__in=['600612', '002060', '601988']).order_by('stock_date')  # 利用老凤祥测试下
    stock_seen = list({(stock.stock_id, stock.stock_name) for stock in stocks})  # 去重用,获得不重名的stock_id
    stocks_new = []  # 添加每支重构后的股票
    for id_name in stock_seen:
        stock = {}  # 重构每支股票数据
        stock['stock_id'] = id_name[0]
        stock['name'] = id_name[1]
        data = [[str(s.stock_date), float(s.price_open), float(s.price_close), float(s.price_low), float(s.price_high)]
                for s in stocks if s.stock_id == id_name[0]]  # 目前暂时只能用此种方式(注意列表内含列表),echarts要求,画K线图的4个数据一定为浮点数

        # 获取涨跌幅数据,目前暂用最普通的方法
        sc = [s.price_close for s in stocks if s.stock_id == id_name[0]]  # 获取所有的收盘价格
        yy = []  # 储存涨跌数据
        try:
            for x in range(len(sc) - 1):
                y = (float(sc[x + 1]) - float(sc[x])) / float(sc[x])
                yy.append('{:.2%}'.format(y))
        except Exception:
            continue
        zz = ['0.00%']
        zz.extend(yy)  # 完整的涨跌幅数据
        for x in range(len(zz)):
            data[x].append(zz[x])

        stock['data'] = data

        # 将涨跌的volumn分开
        volumn_data = [int(s.stock_volumn) for s in stocks if s.stock_id == id_name[0]]  # 获取该股票对应的成交量数据
        volumn_rise = []
        volumn_fall = []
        for x in range(len(data)):
            close_minus_open = data[x][2] - data[x][1]
            if close_minus_open > 0:  # 收盘价大于开盘价,此时volumn为涨,红色
                volumn_rise.append(volumn_data[x])
                volumn_fall.append('-')
            else:
                volumn_rise.append('-')
                volumn_fall.append(volumn_data[x])

        stock['volumn_rise'] = volumn_rise
        stock['volumn_fall'] = volumn_fall

        # stock['volumn'] = [int(s.stock_volumn) for s in stocks if s.stock_id == id_name[0]]
        # k += 1
        stocks_new.append(stock)
    return stocks_new


def KmeansStrategy1():  # 根据策略:跌-跌-涨-涨,最后一天下影线越短越好 选择符合要求的股票
    (*_, tradeday_0, tradeday_1, tradeday_2, tradeday_3) = KmeansData.objects.filter(stock_id='601988').dates(
            'stock_date', 'day', order='DESC')[:5]  # 提取中国银行的倒数第四个交易日,作为所有股票的倒数第四个交易日,本行第一个数字为控制变量,默认且最小为4.

    judge_3 = KmeansData.objects.filter(stock_date=tradeday_3).values_list('stock_id', 'price_open',
                                                                           'price_close')  # 获取倒数第四个交易日的股票代码,开盘价,收盘价
    stock_id_list3 = [s[0] for s in judge_3 if float(s[1]) > float(s[2])]  # 倒数第四日满足开盘价大于收盘价(绿)的股票代码,别忘了将字符串转换为浮点数
    # tradeday_2 = tradeday_3 + timedelta(days=1)  # 倒数第3日
    judge_2 = KmeansData.objects.filter(stock_id__in=stock_id_list3, stock_date=tradeday_2).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close')  # 获取倒数第三个交易日的股票代码,开盘价,收盘价
    stock_id_list2 = [s[0] for s in judge_2 if float(s[1]) > float(s[2])]  # 倒数第三日绿色股票代码
    # tradeday_1 = tradeday_2 + timedelta(days=1)  # 倒数第2日
    judge_1 = KmeansData.objects.filter(stock_id__in=stock_id_list2, stock_date=tradeday_1).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close',
                                                                                                        'stock_volumn')  # 倒数第二个交易日股票数据, 含成交量数据
    stock_id_list1 = [s[0] for s in judge_1 if float(s[1]) < float(s[2])]  # 倒数第2日红色股票代码
    # tradeday_0 = tradeday_1 + timedelta(days=1)  # 倒数第1日
    judge_0 = KmeansData.objects.filter(stock_id__in=stock_id_list1, stock_date=tradeday_0).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close',
                                                                                                        'stock_volumn')  # 倒数第一日交易日股票数据
    stock_id_list0 = [s[0] for s in judge_0 if float(s[1]) < float(s[2])]  # 倒数第1日红色股票代码

    # 找到倒数第1日红色股票代码中,成交量较倒数第二日成交量增加的股票代码
    sid_volumn = []  # 储存通过成交量增长判定得到的股票代码
    for s_id in stock_id_list0:
        volumn1 = [int(s[3]) for s in judge_1 if s[0] == s_id]  # judge_1中的volumn
        volumn0 = [int(s[3]) for s in judge_0 if s[0] == s_id]  # judge_0中的volumn
        if volumn0[0] > volumn1[0]:
            sid_volumn.append(s_id)

    return sid_volumn


def KmeansStrategy2():  # 根据策略:跌-跌-涨,要求最后一天无下影线, 且成交量最好上升
    (*_, tradeday_0, tradeday_1, tradeday_2) = KmeansData.objects.filter(stock_id='601988').dates('stock_date', 'day',
                                                                                                  order='DESC')[
                                               :3]  # 提取中国银行的倒数第三个交易日,作为所有股票的倒数第三个交易日,本行第一个数字为控制变量,默认且最小为3.
    judge_2 = KmeansData.objects.filter(stock_date=tradeday_2).values_list('stock_id', 'price_open',
                                                                           'price_close')  # 获取倒数第三个交易日的股票代码,开盘价,收盘价
    stock_id_list2 = [s[0] for s in judge_2 if float(s[1]) > float(s[2])]  # 倒数第三日满足开盘价大于收盘价(绿)的股票代码,别忘了将字符串转换为浮点数
    # tradeday_1 = tradeday_2 + timedelta(days=1)  # 倒数第2日----此种方法是错误的,有可能包含了周六或日
    judge_1 = KmeansData.objects.filter(stock_id__in=stock_id_list2, stock_date=tradeday_1).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close',
                                                                                                        'stock_volumn')  # 倒数第2个交易日的股票代码,开盘价,收盘价
    stock_id_list1 = [s[0] for s in judge_1 if float(s[1]) > float(s[2])]  # 倒数第2日绿色股票代码
    # tradeday_0 = tradeday_1 + timedelta(days=1)  # 倒数第1日
    judge_0 = KmeansData.objects.filter(stock_id__in=stock_id_list1, stock_date=tradeday_0).values_list('stock_id',
                                                                                                        'price_open',
                                                                                                        'price_close',
                                                                                                        'price_low',
                                                                                                        'price_high',
                                                                                                        'stock_volumn')  # 倒数第一日交易日股票数据
    stock_id_list0 = [s[0] for s in judge_0 if float(s[1]) < float(s[2])]  # 倒数第1日红色股票代码

    # 找寻stock_id_list0中下影线特别短的股票
    sid_stock = []
    for sid in stock_id_list0:
        prices = [(float(s[1]), float(s[2]), float(s[3]), float(s[4]), int(s[5])) for s in judge_0 if
                  s[0] == sid]  # 获取开盘价, 收盘价,最低价,最高价
        price_open = prices[0][0]
        price_close = prices[0][1]
        price_low = prices[0][2]
        price_high = prices[0][3]
        volumn0 = prices[0][4]
        volumn1 = [int(s[3]) for s in judge_1 if s[0] == sid][0]  # 倒数第二天的成交量
        try:
            if ((price_open - price_low) / price_low < 0.001) and (
                            (price_close - price_open) / (
                                    price_high - price_low) > 0.2) and volumn0 > volumn1:  # 下影线短,开收盘价与最高低价比例的判定
                sid_stock.append(sid)
        except Exception:
            continue

    return sid_stock


def KmeansStrategy2_1():  # KmeansStrategy2的改进版,希望可以提高运行效率,核心为只调用一次数据库筛选
    (*_, tradeday_0, tradeday_1, tradeday_2) = KmeansData.objects.filter(stock_id='601988').dates('stock_date', 'day',
                                                                                                  order='DESC')[
                                               :3]  # 提取中国银行的倒数第三个交易日,作为所有股票的倒数第三个交易日,本行第一个数字为控制变量,默认且最小为3.
    stocks_2 = KmeansData.objects.filter(stock_date__range=(tradeday_2, tradeday_0))  # 获取特定三个交易日的所有股票
    judge_2 = stocks_2.filter(stock_date=tradeday_2).values_list('stock_id', 'price_open',
                                                                 'price_close')  # 获取倒数第三个交易日的股票代码,开盘价,收盘价
    stock_id_list2 = [s[0] for s in judge_2 if float(s[1]) > float(s[2])]  # 倒数第三日满足开盘价大于收盘价(绿)的股票代码,别忘了将字符串转换为浮点数
    judge_1 = stocks_2.filter(stock_id__in=stock_id_list2, stock_date=tradeday_1).values_list('stock_id',
                                                                                              'price_open',
                                                                                              'price_close',
                                                                                              'stock_volumn')  # 倒数第2个交易日的股票代码,开盘价,收盘价
    stock_id_list1 = [s[0] for s in judge_1 if float(s[1]) > float(s[2])]  # 倒数第2日绿色股票代码
    judge_0 = stocks_2.filter(stock_id__in=stock_id_list1, stock_date=tradeday_0).values_list('stock_id',
                                                                                              'price_open',
                                                                                              'price_close',
                                                                                              'price_low',
                                                                                              'price_high',
                                                                                              'stock_volumn')  # 倒数第一日交易日股票数据
    stock_id_list0 = [s[0] for s in judge_0 if float(s[1]) < float(s[2])]  # 倒数第1日红色股票代码

    # 找寻stock_id_list0中下影线特别短,成交量上涨,圆柱实体具有一定长度的股票
    sid_stock = []
    for sid in stock_id_list0:
        prices = [(float(s[1]), float(s[2]), float(s[3]), float(s[4]), int(s[5])) for s in judge_0 if
                  s[0] == sid]  # 获取开盘价, 收盘价,最低价,最高价
        price_open = prices[0][0]
        price_close = prices[0][1]
        price_low = prices[0][2]
        price_high = prices[0][3]
        volumn0 = prices[0][4]
        volumn1 = [int(s[3]) for s in judge_1 if s[0] == sid][0]  # 倒数第二天的成交量
        try:
            if ((price_open - price_low) / price_low < 0.001) and (
                            (price_close - price_open) / (
                                    price_high - price_low) > 0.2) and volumn0 > volumn1:  # 下影线短,开收盘价与最高低价比例的判定
                sid_stock.append(sid)
        except Exception:
            continue

    return sid_stock


def k_means(request):
    kdata_dated = KmeansData.objects.filter(stock_date__lte=day_fixed_before_kdata)  # 筛选出过时数据
    kdata_dated.delete()  # 删除

    context_dict = {}  # 上下文字典

    (*_, tradeday_0, tradeday_1) = KmeansData.objects.filter(stock_id='601988').dates('stock_date', 'day',
                                                                                      order='DESC')[
                                   :2]  # 股票最新交易日与前一交易日,本行第一个数字最小为2
    sc_0 = KmeansData.objects.filter(stock_date=tradeday_0).values_list('stock_id', 'price_close')
    sc_1 = KmeansData.objects.filter(stock_date=tradeday_1).values_list('stock_id', 'price_close')
    count_rise = 0  # 计算上涨的股票数量
    for sc in sc_0:
        try:
            close_price0 = float(sc[1])
            close_price1 = float([s[1] for s in sc_1 if s[0] == sc[0]][0])
            if close_price0 > close_price1:
                count_rise += 1
        except Exception:
            continue
    print('上涨股票数量为:', count_rise)
    print('全部股票数量为:', len(sc_0))
    print('上涨比例为:', count_rise / len(sc_0))

    stock_id_list = KmeansStrategy2_1()  # 获取符合选股策略的股票代码, 见上面的函数
    context_dict['stocks'] = ChangeToEchartsData(stock_id_list)  # 将选择出的股票转换为符合echarts的数据结构,常规模式
    # context_dict['stocks'] = ChangeToEchartsData()  # 单独调试

    return render(request, 'choose_stock/k_means.html', context_dict)


def capital(request):
    return render(request, 'choose_stock/capital.html', {})
