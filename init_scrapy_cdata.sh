#!/usr/bin/env bash

export PATH=/usr/local/bin:/usr/bin

export LANG=zh_CN.UTF-8

cd $HOME/Desktop/Python/CHOOSE_STOCK/project/CashFlowData

nohup scrapy crawl eachday_cdata &
