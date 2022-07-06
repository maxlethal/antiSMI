import pandas as pd
from datetime import datetime


import requests
from bs4 import BeautifulSoup

import fasttext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import T5ForConditionalGeneration

model_class = fasttext.load_model("classification/ru_cat_v6.ftz")

tokenizer_resume = AutoTokenizer.from_pretrained("IlyaGusev/mbart_ru_sum_gazeta")
model_resume = AutoModelForSeq2SeqLM.from_pretrained("IlyaGusev/mbart_ru_sum_gazeta")

tokenizer_title = AutoTokenizer.from_pretrained("IlyaGusev/rut5_base_headline_gen_telegram")
model_title = T5ForConditionalGeneration.from_pretrained("IlyaGusev/rut5_base_headline_gen_telegram")

black_label = "ДАННОЕ СООБЩЕНИЕ (МАТЕРИАЛ) СОЗДАНО И (ИЛИ) РАСПРОСТРАНЕНО ИНОСТРАННЫМ СРЕДСТВОМ МАССОВОЙ ИНФОРМАЦИИ, " \
              "ВЫПОЛНЯЮЩИМ ФУНКЦИИ ИНОСТРАННОГО АГЕНТА, И (ИЛИ) РОССИЙСКИМ ЮРИДИЧЕСКИМ ЛИЦОМ, ВЫПОЛНЯЮЩИМ ФУНКЦИИ " \
              "ИНОСТРАННОГО АГЕНТА"


def article2summary(article_text: str) -> str:
	"""Делает краткое саммари из новости"""
	input_ids = tokenizer_resume(
		[article_text],
		max_length=600,
		truncation=True,
		return_tensors="pt")["input_ids"]

	output_ids = model_resume.generate(
		input_ids=input_ids,
		no_repeat_ngram_size=4)[0]

	summary = tokenizer_resume.decode(output_ids, skip_special_tokens=True)

	return summary


def summary2title(summary: str) -> str:
	"""Делает заголовок из краткой новости"""
	input_ids = tokenizer_title(
		[summary],
		max_length=600,
		add_special_tokens=True,
		padding="max_length",
		truncation=True,
		return_tensors="pt")["input_ids"]

	output_ids = model_title.generate(
		input_ids=input_ids)[0]

	title = tokenizer_title.decode(output_ids, skip_special_tokens=True)

	return title


def make_clean_text(article: str, date: int) -> dict:
	"""Обрабатывает полученную страницу новости, извлекает нужное и помещает в создаваемый словарь"""
	soup = BeautifulSoup(article, features="lxml")

	first_a = soup.find('a')
	try:
		first_link = first_a.get('href')
	except AttributeError:
		first_link = 'NaN'

	text = soup.get_text()
	text = text.replace("\xa0", ' ').replace("\n", ' ')
	text = text.replace(black_label, '\n')
	short_news = article2summary(text)
	title = summary2title(short_news)

	return {'date': date, 'title': title, 'short_news': short_news, 'first_link': first_link, 'raw_news': text}


def make_articles_dict(channel_name: str) -> dict:
	"""Получает страницу с новостью, отдаёт её на обработку, и завершает формирование словаря использовав полученное"""
	answer = requests.get('https://tg.i-c-a.su/json/' + channel_name)
	data = answer.json()
	messages = data['messages']

	# вытаскиваем из нашей базы статей id последней статьи текущего медиа, чтобы не обрабатывать уже отработанное
	temp_df = pd.read_pickle('table_news.pkl')
	try:
		start_id = temp_df.index[temp_df['agency'] == channel_name][0]
	except IndexError:
		start_id = 0  # если данное СМИ парсится впервые
	del temp_df

	# выбираем только те статьи, которые старше последней
	id_articles = [(el, messages[el]['id']) for el in range(len(messages)) if messages[el]['id'] > start_id]

	# получение двух предварительных словарей.

	# для этого словаря часть парсинга сообщения и даты передаётся на аутсорс в функцию make_clean_text
	draft_articles = [make_clean_text(messages[el[0]]['message'], messages[el[0]]['date']) for el in id_articles]
	# этот словарь окончательный, но он может содержать пустые статьи, если пост был не текстовым
	articles_dict = {el[1]: draft_articles[el[0]] for el in id_articles}

	# поэтому удаляем пустые статьи
	empty_keys = [k for k, v in articles_dict.items() if not v['raw_news']]
	for k in empty_keys:
		del articles_dict[k]

	return articles_dict


def agency2db(channel_name: str) -> None:
	"""Получает словарь текущего СМИ, и пишет его в нашу базу данных, предварительно обработав и отсортировав"""
	db = pd.read_pickle('table_news.pkl')
	channel_dict = make_articles_dict(channel_name)
	if channel_dict:
		df = pd.DataFrame(channel_dict).T
		df['category'] = df['short_news'].apply(
			lambda x: model_class.predict(x)[0][0].split('__')[-1])  # классифицируем fasttext-ом, достаём класс
		df = df.loc[df['category'] != 'not_news']  # удаляем новости, которые классификатор не признал новостями
		df['date'] = df['date'].apply(lambda x: datetime.fromtimestamp(x))  # преобразовываем timestamp-число в дату
		df['agency'] = channel_name
		ch_news = pd.concat([db, df]).sort_values('date', ascending=False)
		ch_news.to_pickle('table_news.pkl')


async def join_all(agency_list: list):
	"""Передаёт список СМИ на последовательную обработку для записи свежих новостей в pickle"""
	start_time = pd.to_datetime("today")
	print(f'Начинаю сбор текущих новостей в {start_time}')
	for agency in agency_list:
		print(f'Собираю {agency}...')
		agency2db(agency)
		print(f'................... complited')
	# читаем, что получилось
	news_db = pd.read_pickle('table_news.pkl')
	finish_time = pd.to_datetime("today")
	print(f'\nCбор этой порции новостей закончен за {str(pd.to_timedelta(finish_time - start_time))}\n')
	print('-------------------------------------------------------------------------------------------')
	print(f'-------------------------------------------------------------------------------------------\n')
	return news_db

# join_all(agencies)
