from django.db import models


# Create your models here.
class News(models.Model):
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