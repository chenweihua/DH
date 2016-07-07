from django.shortcuts import render
from django.http import HttpResponse
from .models import News, KmeansData
from datetime import datetime, timedelta

now = datetime.now()  # 现在时刻
yesterday = now + timedelta(days=-1)  # 昨天
the_day_before_yesterday = now + timedelta(days=-2)  # 前天
day_5_before = now + timedelta(days=-5)  # 5天前的消息自动从数据库中删除


# Create your views here.
def index(request):  # 处理主页的视图逻辑
    return render(request, 'choose_stock/index.html', {})


def news(request):  # 处理消息页面的视图逻辑
    news_dated = News.objects.filter(published_time__lte=day_5_before)  # 筛选出发布时间在5天前的过时消息
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


def k_means(request):
    context_dict = {}  # 上下文字典
    stocks = KmeansData.objects.filter(stock_id__regex='600612|002060').order_by('stock_date')  # 利用老凤祥测试下

    stock_seen = list({(stock.stock_id, stock.stock_name) for stock in stocks})  # 去重用,获得不重名的stock_id
    # k = 0  # 用于计数,标度每一支股票
    stocks_new = []  # 添加每支重构后的股票
    for id_name in stock_seen:
        stock = {}  # 重构每支股票数据
        stock['stock_id'] = id_name[0]
        stock['name'] = id_name[1]

        data = [[str(s.stock_date), s.price_open, s.price_close, s.price_low, s.price_high]
                for s in stocks if s.stock_id == id_name[0]]  # 目前暂时只能用此种方式(注意列表内是列表),echarts要求

        # 获取涨跌幅数据,目前暂用最普通的方法
        sc = [s.price_close for s in stocks if s.stock_id == id_name[0]]  # 获取所有的收盘价格
        yy = []  # 储存涨跌数据
        for x in range(len(sc) - 1):
            y = (float(sc[x + 1]) - float(sc[x])) / float(sc[x])
            yy.append('{:.2%}'.format(y))
        zz = ['0.00%']
        zz.extend(yy)  # 完整的涨跌幅数据
        for x in range(len(zz)):
            data[x].append(zz[x])

        stock['data'] = data
        stock['volumn'] = [s.stock_volumn for s in stocks if s.stock_id == id_name[0]]
        # k += 1
        stocks_new.append(stock)
    context_dict['stocks'] = stocks_new

    return render(request, 'choose_stock/k_means.html', context_dict)


def capital(request):
    return render(request, 'choose_stock/capital.html', {})
