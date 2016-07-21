from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import News, KmeansData, CashFlowData, Name_Id
from datetime import datetime, timedelta
from collections import defaultdict

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
def ChangeToEchartsData_kdata(stock_id_list=['000705', '300016', '002090']):  # 将特定代码的股票数据转换为符合echarts的数据
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


def KmeansStrategy2_1(index_day=3):  # KmeansStrategy2的改进版,希望可以提高运行效率,核心为只调用一次数据库筛选
    (*_, tradeday_0, tradeday_1, tradeday_2) = KmeansData.objects.filter(stock_id='601988').dates('stock_date', 'day',
                                                                                                  order='DESC')[
                                               :index_day]  # 提取中国银行的倒数第三个交易日,作为所有股票的倒数第三个交易日,本行第一个数字为控制变量,默认且最小为3.
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

    stock_id_list = KmeansStrategy2_1(4)  # 获取符合选股策略的股票代码, 见上面的函数,最小值为3(当天),4(前一天)
    context_dict['stocks'] = ChangeToEchartsData_kdata(stock_id_list)  # 将选择出的股票转换为符合echarts的数据结构,常规模式
    # context_dict['stocks'] = ChangeToEchartsData()  # 单独调试

    return render(request, 'choose_stock/k_means.html', context_dict)


# -----------------------------资金流相关函数---------------------------------
def ChangeToEchartsData_cdata(stock_id_list=['000705', '300016', '002090', '300110']):
    stocks = CashFlowData.objects.filter(stock_id__in=stock_id_list).order_by('stock_date')
    stock_seen = list({(stock.stock_id, stock.stock_name) for stock in stocks})
    stocks_new = []
    for sid in stock_seen:
        stock = {}  # 重构每支股票
        stock['stock_id'] = sid[0]
        stock['stock_name'] = sid[1]
        stock['stock_date'] = [str(s.stock_date) for s in stocks if s.stock_id == sid[0]]
        maincash_data = [s.maincash_in for s in stocks if s.stock_id == sid[0]]
        maincash_data_rise = []  # 资金净流入
        maincash_data_fall = []  # 资金净流出
        for eachdata in maincash_data:
            unit = eachdata[-1]  # 资金流数据单位,"亿"或者"万"
            try:
                number = float(eachdata[:-1])  # 数字,字符串形式
            except Exception as e:
                print('数据转换错误:', e, sid)
                continue
            if unit == '亿':
                number *= 10 ** 4
            if number > 0:
                maincash_data_rise.append(number)
                maincash_data_fall.append('-')
            else:
                maincash_data_rise.append('-')
                maincash_data_fall.append(number)
        stock['maincash_data_rise'] = maincash_data_rise
        rise_temp = [x for x in maincash_data_rise if isinstance(x, float)]
        stock['maincash_data_fall'] = maincash_data_fall
        fall_temp = [x for x in maincash_data_fall if isinstance(x, float)]
        try:
            stock['average_rise'] = sum(rise_temp) / len(rise_temp)  # 净流入平均值
            stock['average_fall'] = sum(fall_temp) / len(fall_temp)  # 净流出平均值
            # 主力净占比
            maincash_rate = [float(s.maincash_in_rate[:-1]) for s in stocks if s.stock_id == sid[0]]  # 单位为%, 比实际数大100倍
        except Exception as e:
            print('除法错误或数据转换错误:', e, sid)
            continue
        stock['maincash_rate'] = maincash_rate

        # 收盘价与主力成本
        stock['price_close'] = [float(s.price_close) for s in stocks if s.stock_id == sid[0]]
        main_cost = [s.main_cost for s in stocks if s.stock_id == sid[0]]
        stock['main_cost'] = [float(s) if s else '' for s in main_cost]  # 列表解析,带else的,要写前面

        stocks_new.append(stock)
    return stocks_new


def CashFlowStrategy1(index_day=1):  # 策略1: 最后一天净流入,大于平均值,(收盘价-成本价)从小到大排列10个
    (*_, tradeday_0) = CashFlowData.objects.filter(stock_id='601988').dates('stock_date', 'day', order='DESC')[
                       :index_day]  # 获取最近的交易日,"[]"中的数最小为1
    stocks = CashFlowData.objects.filter(stock_date__lte=tradeday_0).order_by('stock_date')
    id_maincash = stocks.values_list('stock_id', 'maincash_in')
    id_maincash2 = defaultdict(list)  # 初始化字典
    for k, v in id_maincash:
        id_maincash2[k].append(v)

    stock_id1 = []  # 储存最后一天主力资金净流入大于净流入平均值的股票代码
    for k in id_maincash2:
        k_maincash = id_maincash2[k]
        pos_maincash = [x for x in k_maincash if not x.startswith('-')]  # 去掉以'-'开头的maincash
        try:
            float_maincash = [float(x[:-1]) if x[-1] == '万' else float(x[:-1]) * 10 ** 4 for x in
                              pos_maincash]  # 转换为浮点数
            average_maincash = sum(float_maincash) / len(float_maincash)
            if k_maincash[-1][-1] == '万':
                last_maincash = float(k_maincash[-1][:-1])
            else:
                last_maincash = float(k_maincash[-1][:-1]) * 10 ** 4
            if last_maincash > average_maincash * 2:  # 净流入大于1.5倍的平均值
                stock_id1.append(k)
        except Exception as e:
            print('转换数据错误:', e, k)
            continue

    stocks1 = stocks.filter(stock_id__in=stock_id1, stock_date=tradeday_0)
    judge1 = stocks1.values_list('stock_id', 'price_close', 'main_cost')
    sorted_judge = sorted(judge1, key=lambda s: float(s[1]) - float(s[2]))  # 以(收盘价-开盘价)又小到大排序
    stocks_id2 = sorted_judge[:20]  # 前特定数量的股票,不足也行
    stocks_id2_1 = [s[0] for s in stocks_id2]  # 取出股票代码
    return stocks_id2_1


def CashFlowStrategy2(index_day=1):  # 策略2: 最后一天净流入,大于平均值,前三次净流入均小于平均值,(收盘价-成本价)从小到大排列10个
    (*_, tradeday_0) = CashFlowData.objects.filter(stock_id='601988').dates('stock_date', 'day', order='DESC')[
                       :index_day]  # 获取最近的交易日,"[]"中的数最小为1
    stocks = CashFlowData.objects.filter(stock_date__lte=tradeday_0).order_by('stock_date')
    id_maincash = stocks.values_list('stock_id', 'maincash_in')
    id_maincash2 = defaultdict(list)  # 初始化字典
    for k, v in id_maincash:
        id_maincash2[k].append(v)

    stock_id1 = []  # 储存最后一天主力资金净流入大于净流入平均值的股票代码
    for k in id_maincash2:
        k_maincash = id_maincash2[k]
        pos_maincash = [x for x in k_maincash if not x.startswith('-')]  # 去掉以'-'开头的maincash
        try:
            float_maincash = [float(x[:-1]) if x[-1] == '万' else float(x[:-1]) * 10 ** 4 for x in
                              pos_maincash]  # 转换为浮点数
            average_maincash = sum(float_maincash) / len(float_maincash)

            if float_maincash[-2] < average_maincash and float_maincash[-3] < average_maincash and float_maincash[
                -4] < average_maincash:
                ave3_less = True
            else:
                ave3_less = False

            if k_maincash[-1][-1] == '万':
                last_maincash = float(k_maincash[-1][:-1])
            else:
                last_maincash = float(k_maincash[-1][:-1]) * 10 ** 4

            if last_maincash > average_maincash * 2 and ave3_less and last_maincash > 1000:  # 净流入大于特定倍数的平均值, 大于1000(判定为热门股票)
                stock_id1.append(k)
        except Exception as e:
            print('转换数据错误:', e, k)
            continue

    stocks1 = stocks.filter(stock_id__in=stock_id1, stock_date=tradeday_0)
    judge1 = stocks1.values_list('stock_id', 'price_close', 'main_cost')
    judge2 = [s for s in judge1 if float(s[1]) - float(s[2]) <= 0.1]  # 收盘价-主力成本<=0.1
    sorted_judge = sorted(judge2, key=lambda s: float(s[1]) - float(s[2]))  # 以(收盘价-开盘价)又小到大排序
    stocks_id2 = sorted_judge[:20]  # 前特定数量的股票,不足也行
    stocks_id2_1 = [s[0] for s in stocks_id2]  # 取出股票代码
    return stocks_id2_1


def capital(request):
    context_dict = {}

    stock_id_list = CashFlowStrategy2(1)  # 最小为1(当前), 2(前一天)

    context_dict['stocks'] = ChangeToEchartsData_cdata(stock_id_list)

    return render(request, 'choose_stock/capital.html', context_dict)


# ---------------------------个股讯息--------------------------------------
def search(request):
    context = {}
    if request.method == 'POST':
        id_name = request.POST['id_name']  # 对应模板中input的name值
        stock_id_name = Name_Id.objects.all().values_list('stock_id', 'stock_name')  # 取得所有的股票代码及名称
        special_stock = [s for s in stock_id_name if id_name in s]
        if special_stock:
            return redirect('choose_stock.views.stock_detail', stock_id=special_stock[0][0])  # 必须加上return
        else:
            context['info'] = '无此股票讯息,请重新输入'
    return render(request, 'choose_stock/search.html', context)


def stock_detail(request, stock_id):
    context = {}
    stock_id1 = [stock_id]
    try:
        context['stock_c'] = ChangeToEchartsData_cdata(stock_id1)[0]
        context['stock_k'] = ChangeToEchartsData_kdata(stock_id1)[0]
        stock_name = Name_Id.objects.filter(stock_id=stock_id).values_list('stock_name', flat=True)[0]
        context['news'] = News.objects.filter(content__contains=stock_name).order_by('-published_time')
    except Exception as e:
        print('股票讯息读取错误:', e, stock_id)
    return render(request, 'choose_stock/stock_detail.html', context)
