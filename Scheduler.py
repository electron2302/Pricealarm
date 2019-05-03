from apscheduler.schedulers.blocking import BlockingScheduler
import json
from time import gmtime, strftime
from Run import main

with open('config.json', 'r') as f:
    config = json.load(f)

if config['debug']: print('it is {}'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))

main() # this is here on purpos so that it also runs once directly after startup

sched = BlockingScheduler()

@sched.scheduled_job('interval', hours=config['interval'])
def timed_job():
    if config['debug']: print('scheduled_job trigered at {}'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))
    main()
    if config['debug']: print('scheduled_job finished at {}'.format(strftime("%Y-%m-%d %H:%M:%S", gmtime())))

#sched.configure(options_from_ini_file)
sched.start()

#https://stackoverflow.com/questions/22715086/scheduling-python-script-to-run-every-hour-accurately