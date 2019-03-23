#!/usr/bin/env python
# -*- coding: utf-8 -*-
from itertools import chain
DBPLACE = '../Data/LANGUAGE5.sqlite3'
from peewee import *
import re
from datetime import datetime
from playhouse.sqlite_ext import SqliteExtDatabase
import utiltools
import numpy as np

twtrSQLPLACE = '/Users/xxxx'
twtrDB = SqliteExtDatabase(twtrSQLPLACE, autocommit=False, journal_mode='persist')
userDB = SqliteExtDatabase('/Users/xxxx')

class UserDBModel(Model):
    class Meta:
        database = userDB

class Srtrtemps(UserDBModel):
    kanasstream = CharField(db_column='kanasStream', null=True)
    lenrule = IntegerField(db_column='lenRule', null=True)
    losecnt = IntegerField(null=True)
    name = CharField(primary_key=True)
    totalcnt = IntegerField(null=True)
    wincnt = IntegerField(null=True)
    wordsstream = CharField(db_column='wordsStream', null=True)
    class Meta:
        db_table = 'srtrtemps'

class Users(UserDBModel):
	screen_name = CharField(primary_key=True)
	user_id = CharField(null=True)
	name = CharField(null=True)
	nickname = CharField(null=True)
	mode = CharField(null=True)
	cnt = IntegerField(null=True)
	reply_cnt = IntegerField(null=True)
	total_cnt = IntegerField(null=True)
	context = CharField(null=True)
	exp = IntegerField(null=True)
	reply_id = CharField(null=True)
	reply_name = CharField(null=True)
	status_id = CharField(null=True)
	time = DateTimeField(null=True, default = datetime.utcnow())
	tmp = CharField(null=True)
	tmpFile = CharField(null=True)
	tmpTime = DateTimeField(null=True)
	class Meta:
		db_table = 'users'

class Phrases(UserDBModel):
    phrase = CharField(primary_key=True)
    framework = CharField(null=True)
    s_type = CharField(null=True)
    status = CharField(null=True)
    ok_cnt = IntegerField(null=True)
    ng_cnt = IntegerField(null=True)
    class Meta:
        db_table = 'phrases'

class Words(UserDBModel):
    head = CharField()
    length = IntegerField()
    tail = CharField()
    word = CharField(primary_key=True)
    yomi = CharField()
    class Meta:
        db_table = 'words'

#####twtrDB#######
class twtrDBModel(Model):
  class Meta:
    database = twtrDB
class Tweets(twtrDBModel):
	status_id = IntegerField(null=True, primary_key=True)
	createdat = DateTimeField(db_column='createdAt')
	name = CharField(null=True)
	screen_name = CharField(null=True)
	text = CharField(null=True)
	updatedat = DateTimeField(db_column='updatedAt')
	user_id = CharField(null=True)
	bot_id = CharField(null=True)
	in_reply_to_status_id_str = CharField(null=True)
	class Meta:
		database = twtrDB

def saveTweet(status):
	try:
		twtrDB.create_tables([Tweets], True)
		with twtrDB.transaction():
			t = Tweets()
			t.status_id = int(status.id_str)
			t.text = status.text #本文
			# t.date = status.created_at #ツイートされた日時（確かdatetime型）
			t.name = status.author.name #投稿者id名(unicode型、sqlite3で都合が良いので.encode("utf-8")とはしませんでした
			t.screen_name = status.author.screen_name #投稿者の名前
			t.user_id = status.author.id_str; #メイン @_umiA
			t.bot_id = '2805015776'; #メイン @_umiA
			# now = datetime.utcnow()
			t.in_reply_to_status_id_str = status.in_reply_to_status_id_str
			t.createdat = status.created_at
			t.updatedat = datetime.utcnow()
			return t.save()
		print('SAVED]')
		twtrDB.commit()
	except Exception as e:
		print(e)
		twtrDB.rollback()
def getTweetList(n = 1000, UserList = ['sousaku_umi', 'umi0315_pokemon'], BlackList = ['hsw37', 'ry72321', 'MANI_CHO_8', 'HONO_HONOKA_1', 'MOEKYARA_SAIKOU', 'megmilk_0308'], contains = 'です'):
  try:
    twtrDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
    with twtrDB.transaction():
      if UserList == []:
        tweets = Tweets.select().where(Tweets.text.contains(contains), ~Tweets.text.contains('RT'), ~Tweets.screen_name << BlackList, ~Tweets.text.contains('【')).order_by(Tweets.createdat.desc()).limit(n)
      else:
        tweets = Tweets.select().where(Tweets.screen_name << UserList , ~Tweets.screen_name << BlackList, ~Tweets.text.contains('RT'), ~Tweets.text.contains('【')).order_by(Tweets.createdat.desc()).limit(n)
      tweetslist = [utiltools.cleanText(tweet.text) for tweet in tweets]
      return tweetslist
  except Exception as e:
    twtrDB.rollback()

def getPhrase(s_type = '公式文', n = 10):
	try:
		# UserDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			Ps = Phrases.select().where(Phrases.s_type == s_type).limit(n)
			cntArr = np.array([w.ok_cnt for w in Ps])
			P = np.random.choice([p.phrase for p in Ps], p = cntArr/np.sum(cntArr))
			return P
	except Exception as e:
		print(e)
		userDB.rollback()

def getUserInfo(screen_name):
	try:
		userDB.create_tables([Users], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			userinfo, iscreated = Users.get_or_create(screen_name = screen_name)
			if iscreated:
				userinfo.name = screen_name
				userinfo.nickname = screen_name
				userinfo.cnt = 0
				userinfo.total_cnt = 0
				userinfo.reply_cnt = 0
				userinfo.exp = 0
				userinfo.mode = 'dialog'
				userinfo.time = datetime.utcnow()
			# userinfo.time = datetime.utcnow()
			# userinfo.save()
			# userDB.commit()
			return userinfo.__dict__['_data'], iscreated
	except Exception as e:
		print(e)
		userDB.rollback()

def saveUserInfo(userstatus):
	try:
		# UserDB.create_tables([Tweets], True)# 第二引数がTrueの場合、存在している場合は、作成しない
		with userDB.transaction():
			try:
				# userinfo = Users.get_or_create(screen_name = userstatus['screen_name'])
				userinfo = Users(**userstatus)
				userinfo.save()
			except Exception as e:
				print(e)
				return False, userstatus
			userDB.commit()
			return True, userstatus
	except Exception as e:
	  userDB.rollback()
	  return False, userstatus

if __name__ == '__main__':
	import sys
	import io
	import os
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
	# umi = getTweetList(n = 10)
	# umi = saveUserInfo({'context': '', 'cnt': 3, 'status': '694057314039386113', 'mode': 'dialog', 'reply_name': '_umiA', 'usr': '2992260014', 'screen_name': 'pEEE', 'replycnt': 5, 'reply': '', 'exp': 0, 'totalcnt': 208, 'name': 'おてつだい実験用bot@フォロー非推奨'})

