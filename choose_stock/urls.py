from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),  # 首页路径
    url(r'^news$', views.news, name='news'),  # 消息面路径
    url(r'^k_means$', views.k_means, name='k_means'),  # 技术面路径
    url(r'^capital$', views.capital, name='capital'),  # 资金面路径
    url(r'^news_detail/(?P<pk>\d+$)', views.news_detail, name='news_detail'),  # 具体消息
    url(r'^search$', views.search, name='search'),  # 个股讯息,以查询开始
    url(r'^stock_detail/(?P<stock_id>\d+$)', views.stock_detail, name='stock_detail'),

]