#!/usr/bin/env python
# -*- coding: utf-8 -*-
# import subprocess
# PROJECT_PATH='/Users/xxxx'
# sys.path.append(PROJECT_PATH+'/modules')
# sys.path.append(PROJECT_PATH+'/Data')
# import datetime # datetimeモジュールのインポート
import random
# from pymongo import MongoClient, DESCENDING
# import numpy as np
# import scipy as sp
import NLP
import re

from itertools import chain
from collections import Counter

import sqlite3
from peewee import *

from playhouse.sqlite_ext import SqliteExtDatabase
db = SqliteExtDatabase('../twtrData.sqlite3', autocommit=False, journal_mode='persist')
db.connect()
class BaseModel(Model):
    class Meta:
        database = db
class Tweets(BaseModel):
    createdat = DateTimeField(db_column='createdAt')
    name = CharField(null=True)
    screen_name = CharField(null=True)
    text = CharField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    user = CharField(db_column='user_id', null=True)
    class Meta:
        db_table = 'tweets'


# tempdb = SqliteExtDatabase('../temp.sqlite3', autocommit=False, journal_mode='memory')
# tempdb.connect()


# MongoDBへの接続
# mongo_client = MongoClient('localhost:27017')
# データベースの選択
# db = mongo_client["Umi_IA"]
# wordsDB = db["words"]
# tweetsDB = db["tweets"]



def cleanText(text):
	text = re.sub(r'(@[^\s　]+)', '', text)
	text = re.sub(r'(#[^\s　]+)', '', text)
	text = re.sub(r'(http[^\s　]+)', '', text)
	text = re.sub(r'(^[\s　]+)', '', text)
	text = re.sub(r'([\s　]+$)', '', text)
	text = re.sub(r'(([\s　]+))', '', text)
	return text

def Kaomoji(s):
	text = '[0-9A-Za-zぁ-ヶ一-龠]';
	non_text = '[^0-9A-Za-zぁ-ヶ一-龠]';
	allow_text = '[ovっつ゜ニノ三二]';
	hw_kana = '[ｦ-ﾟ]';
	open_branket = '[\(∩꒰（]';
	close_branket = '[\)∩꒱）]';
	arround_face = '(?:' + non_text + '|' + allow_text + ')*';
	face = '(?!(?:' + text + '|' + hw_kana + '){3,}).{3,}';
	face_char = re.compile(arround_face + open_branket + face + close_branket + arround_face);
	facelist = face_char.findall(s)
	cleaned = re.sub(face_char, '' , s)
	return cleaned, facelist
	
def Daisuki(n = 400):
	try:
		db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():
			tweets = Tweets.select().where(Tweets.screen_name != '_umiA' and ~Tweets.text.contains('RT')).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [cleanText(tweet.text) for tweet in tweets  if 'RT' not in tweet.text ]
			tweetslist = [Kaomoji(tweet) for tweet in tweetslist]
			nouns = [NLP.MA.getMeCab(s[0], form='名詞', exception="数,接尾,非自立,接続助詞,格助詞,代名詞",returnstyle = 'list',Debug=0) for s in tweetslist]
			print(nouns)
			# nounslist = list(set(chain.from_iterable(nouns)))
			nounslist = list(chain.from_iterable(nouns))
			# print(nounslist)
			noun2list = [noun for noun in nounslist if len(noun) > 2]
			# # print(noun2list)
			randn = random.choice(noun2list)
			# counter = Counter(nounslist)
			# for word, cnt in counter.most_common(1):
			# 	print(word, cnt)
			ans = 'わぁい' + randn + ' うみみ' + randn + '大好き...です...//'
			print(ans)
	except IntegrityError as ex:
		print(ex)
		db.rollback()

def getBoomWords(username = '_umiA', n = 400):
	try:
		db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():
			tweets = Tweets.select().where((Tweets.screen_name == username) & (~Tweets.text.contains('RT'))).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [cleanText(tweet.text) for tweet in tweets]#  if 'RT' not in tweet.text]
			# print([tweet.text for tweet in tweets])
			tweetslist = [Kaomoji(tweet) for tweet in tweetslist]
			nouns = [NLP.MA.getMeCab(s[0], form='名詞', exception="数,接尾,非自立,接続助詞,格助詞,代名詞",returnstyle = 'list',Debug=0) for s in tweetslist]
			# nounslist = list(set(chain.from_iterable(nouns)))
			nounslist = list(chain.from_iterable(nouns))
			# print(nounslist)
			noun2list = [noun for noun in nounslist if len(noun) > 2]
			# # print(noun2list)
			# randn = random.choice(noun2list)
			if noun2list == []:
				print(user + 'さんのデータが足りません。もう少し経ってから再試行してみてください。')
			else:
				print(user + 'さんが最近よくつかう言葉は...')
				counter = Counter(noun2list)
				for word, cnt in counter.most_common(5):
					print('☆ ', word)
				print('です。')
			# ans = 'わぁい' + randn + ' うみみ' + randn + '大好き...です...//'
			# print(ans)
	except IntegrityError as ex:
		print(ex)
		db.rollback()

def createMarkovModel(username = 'xxxx', n = 10):
	try:
		# db.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with db.transaction():
			tweets = Tweets.select().where((Tweets.screen_name != username) & (~Tweets.text.contains('RT'))).order_by(Tweets.createdat.desc()).limit(n)
			tweetslist = [cleanText(tweet.text) for tweet in tweets]#  if 'RT' not in tweet.text]
			# print([tweet.text for tweet in tweets])
			tweetslist = [Kaomoji(tweet) for tweet in tweetslist]
			sentences = [NLP.MA.getMeCab(s[0], form = '', mode = "", exception = "", returnstyle = 'list',Debug=0) for s in tweetslist]
			for s in sentences:
				wordscnt = len(s)
				print(wordscnt,s)
				for i in range(wordscnt):
					if i > 1:
						print('SQL', s[i-2], s[i-1], s[i])
					else:
						print(s)

	except IntegrityError as ex:
		print(ex)
		db.rollback()



if __name__ == '__main__':
	import sys
	import io
	import os
	import re
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	try:
		argvs = sys.argv
		intext = argvs[1]
		user = argvs[2]
	except:
		user = 'xxxx'
		intext = "しりとり"
	cmdlist = intext.split(' ')
	text = cmdlist[0]
	if intext == 'Daisuki':
		Daisuki()
	else:
		getBoomWords(user)
		# createMarkovModel()

