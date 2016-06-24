from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime
import time
import os

def tick():
    #print('Tick! The time is: %s' % datetime.now()
    os.chdir('/Users/DQ/Desktop/Python/CHOOSE_STOCK/project/s_c_stock')
    print(os.getcwd())
    os.system('scrapy crawl choose_stock_news')  # doesn't work

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(tick, 'cron', minute='*/1', hour='*')
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


        
    
