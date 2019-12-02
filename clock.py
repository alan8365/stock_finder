from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()


# TODO put scrapy in

@scheduler.scheduled_job('cron', day_of_week='mon-fri', hour=17)
def scheduled_job():
    print('This job is run every weekday at 5pm.')


scheduler.start()
