from django.db import models


# Create your models here.
class News(models.Model):  # 股票消息面数据库
    name = models.CharField(max_length=128, unique=True)  # 新闻的标题,必须是唯一的
    url = models.URLField()  # 新闻的网络连接
    content = models.TextField()  # 新闻的内容
    published_time = models.DateTimeField()  # 新闻发表的时间
    origin_from = models.CharField(max_length=64)  # 新闻的来源
    flag_pn = models.IntegerField(default=1)  # 记录新闻的利好还是利空,1为利好,0为利空,-1为无价值

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'news'


class Name_Id(models.Model):  # 股票代码及名称
    stock_name = models.CharField(max_length=16, unique=True)  # 股票名称,唯一
    stock_id = models.CharField(max_length=8, unique=True)  # 股票代码, 唯一

    def __str__(self):
        return '{}-{}'.format(self.stock_name, self.stock_id)


class KmeansData(models.Model):
    stock_name = models.CharField(max_length=16)  # 股票名称
    stock_id = models.CharField(max_length=8)  # 股票代码
    stock_date = models.DateField()  # 交易日期
    price_open = models.CharField(max_length=10)  # 开盘价
    price_high = models.CharField(max_length=8)  # 最高价
    price_low = models.CharField(max_length=8)  # 最低价
    price_close = models.CharField(max_length=8)  # 收盘价
    stock_volumn = models.CharField(max_length=20)  # 成交量
    stock_id_date = models.CharField(max_length=20, unique=True)  # 重要,由股票代码及交易日期组成的字段,判断信息是否唯一的标识.
