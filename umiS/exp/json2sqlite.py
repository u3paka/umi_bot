#!/usr/bin/env python
# -*- coding:utf-8 -*-
import json
import sqlite3

JSON_FILE = "../Data/mongobkup/temp.json"
DB_FILE = "temp.db"
null = 0
traffic =[
]
# userinfos = traffic

# datalist = []

# for info in userinfos:
# 	user = {}
# 	user['screen_name'] =  info['screen_name']
# 	try:
# 		user['totalcnt'] = info['totalcnt']
# 	except:
# 		user['totalcnt'] = 0
# 	try:
# 		user['exp'] = info['exp']
# 	except:
# 		user['exp'] = 0
# 	datalist.append(user)

# conn = sqlite3.connect('../umiA.sqlite3')

# screen_name = traffic[0]["screen_name"]
# exp = traffic[0]["exp"]

# data = [screen_name, exp]

# c = conn.cursor()
# # c.execute('create table userinfos (screen_name, exp)')
# # c.execute('insert into userinfos values (?,?)', data)
# a = c.execute('select * from userinfos')
# print(a)
# conn.commit()
# c.close()

# print(datalist)

from peewee import *
from datetime import date
database = SqliteDatabase('/Users/xxxx', **{})

class UnknownField(object):
    pass

class BaseModel(Model):
    class Meta:
        database = database

# class SqliteSequence(BaseModel):
#     name = UnknownField(null=True)
#     seq = UnknownField(null=True)
#     class Meta:
#         db_table = 'sqlite_sequence'

class Tweets(BaseModel):
    createdat = DateTimeField(db_column='createdAt')
    name = CharField(null=True)
    screen_name = CharField(null=True)
    text = CharField(null=True)
    updatedat = DateTimeField(db_column='updatedAt')
    user = CharField(db_column='user_id', null=True)

    class Meta:
        db_table = 'tweets'

class Word(Model):
	word = CharField(primary_key=True)
	yomi = CharField()
	head = CharField()
	tail = CharField()
	length = IntegerField()
	class Meta:
		database =  database

database.connect()
try:
	# 第二引数がTrueの場合、存在している場合は、作成しない
	database.create_tables([Tweets], True)
	with database.transaction():
# 		# # createでINSERTする
		# grandma = Word.create(word = 'Test', yomi = 'テスト', head = 'テ', tail = 'ト', length = 3)
		for tweet in Tweets.select():
			print (tweet.screen_name, tweet.text)
		# db.commit()
except IntegrityError as ex:
    print (ex)
    db.rollback()

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')