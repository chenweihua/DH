from django.shortcuts import render
from django.http import HttpResponse
from .models import News
from datetime import datetime, timedelta


now = datetime.now()  # 现在时刻
yesterday = now + timedelta(days=-1)
the_day_before_yesterday = now + timedelta(days=-2)


# Create your views here.
def index(request):  # 处理主页的视图逻辑
    return render(request, 'choose_stock/index.html', {})


def news(request):  # 处理消息页面的视图逻辑
    context_dict = {}  # 上下文字典
    news_today_pos = News.objects.filter(published_time__day=now.day, flag_pn=1).order_by('-published_time')  # 提取出今日新闻利好列表,既查询,又排序,链接过滤器好
    context_dict['news_today_pos'] = news_today_pos
    news_today_neg = News.objects.filter(published_time__day=now.day, flag_pn=0).order_by('-published_time')  # 提取今日利空新闻列表
    context_dict['news_today_neg'] = news_today_neg
    news_yes_pos = News.objects.filter(published_time__day=yesterday.day, flag_pn=1).order_by('-published_time')  # 提取昨日利好新闻列表
    context_dict['news_yes_pos'] = news_yes_pos
    news_yes_neg = News.objects.filter(published_time__day=yesterday.day, flag_pn=0).order_by('-published_time')  # 提取昨日利空新闻列表
    context_dict['news_yes_neg'] = news_yes_neg
    news_be_yes_pos = News.objects.filter(published_time__day=the_day_before_yesterday.day, flag_pn=1).order_by('-published_time')  # 提取前日利好新闻列表
    context_dict['news_be_yes_pos'] = news_be_yes_pos
    news_be_yes_neg = News.objects.filter(published_time__day=the_day_before_yesterday.day, flag_pn=0).order_by('-published_time')  # 提取前日利空新闻列表
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
    return render(request, 'choose_stock/k_means.html', {})


def capital(request):
    return render(request, 'choose_stock/capital.html', {})
