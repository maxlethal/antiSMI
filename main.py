import get_batch_into_pickle
import update_db
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import threading

agencies = [
	'vcnews',
	'addmeto',
	'thebell_io',
	'nplusone',
	'TJournal',
	'vedomosti',
	'VwordMedia',
	'meduzalive',
	'meduzapro',
	'rozetked',
	'now_ka',
	'rbc_sport',
	'ohmypain',
	'russianmacro']


def run():
	"""Собирает все свежие новости всех СМИ согласно заданного расписания"""
	scheduler_1 = AsyncIOScheduler(timezone='Europe/Moscow')
	scheduler_1.add_job(get_batch_into_pickle.join_all, 'cron', max_instances=10, misfire_grace_time=600, hour=7,
	                    kwargs={'agency_list': agencies})
	scheduler_1.add_job(get_batch_into_pickle.join_all, 'cron', max_instances=10, misfire_grace_time=600, hour=12,
	                    kwargs={'agency_list': agencies})
	scheduler_1.add_job(get_batch_into_pickle.join_all, 'cron', max_instances=10, misfire_grace_time=600, hour=17,
	                    kwargs={'agency_list': agencies})
	scheduler_1.add_job(get_batch_into_pickle.join_all, 'cron', max_instances=10, misfire_grace_time=600, hour=21,
	                    kwargs={'agency_list': agencies})
	scheduler_1.start()

	scheduler_2 = AsyncIOScheduler(timezone='Europe/Moscow')
	scheduler_2.add_job(update_db.update, 'cron', max_instances=10, misfire_grace_time=600, hour=7, minute=40)
	scheduler_2.add_job(update_db.update, 'cron', max_instances=10, misfire_grace_time=600, hour=12, minute=40)
	scheduler_2.add_job(update_db.update, 'cron', max_instances=10, misfire_grace_time=600, hour=17, minute=40)
	scheduler_2.add_job(update_db.update, 'cron', max_instances=10, misfire_grace_time=600, hour=21, minute=40)
	scheduler_2.start()

	asyncio.get_event_loop().run_forever()


thread = threading.Thread(target=run())
thread.start()
