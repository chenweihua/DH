from django.contrib import admin
from .models import News


# Register your models here.
class NewsAdmin(admin.ModelAdmin):
    list_display = ('name', 'url', 'published_time', 'origin_from')


admin.site.register(News, NewsAdmin)
