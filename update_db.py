import pandas as pd
import sqlite3
import shutil


def make_file_backup(filename: str):
	"""Делает копию задаваемого файла в директорию backups"""
	file_source = filename
	file_destination = 'backups/'
	shutil.copy(file_source, file_destination)


async def update():
	"""Определяет dataframe свежих новостей (есть в pickle, но нет в базе), и добавляет его в базу данных"""
	with sqlite3.connect('db.db') as db:
		cursor = db.cursor()
		query = """SELECT max (date), agency, title FROM news """
		cursor.execute(query)
		for res in cursor:
			last_date = res[0]

	df = pd.read_pickle('table_news.pkl')
	fresh_df = df[df.date > last_date]

	fresh_df.to_sql(name='news', con=db, if_exists='append', index=True)
	print('Записал свежую порцию в БД')
	make_file_backup('table_news.pkl')  # делаем backup pickle df
	print('Сделал backup pkl')
	make_file_backup('db.db')  # делаем backup базы
	print('Сделал backup БД\n')
	print(f'Новостей было записано {fresh_df.shape[0]}, на текущий момент их общее количество {df.shape[0]}')

	return fresh_df

# update()
