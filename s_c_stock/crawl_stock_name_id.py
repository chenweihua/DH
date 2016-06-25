import urllib.request
import re


url = 'http://quote.eastmoney.com/stocklist.html' # target url
req = urllib.request.Request(url) # request
res = urllib.request.urlopen(req) # response
#content = res.read().decode('gb2312') # content of response
content = res.read(1000)

pattern = Now I will use scrapy instead


